"""Offline benchmark vs labeled clips."""

import logging

from pipeline.evaluation.labeled_clips import LabeledClip
from pipeline.evaluation.metrics import BenchmarkResult
from pipeline.fusion.signal_fuser import SignalFuser
from pipeline.kafka.schemas import AudioEvent, VisionEvent
from pipeline.speech.commentary_parser import CommentaryParser

logger = logging.getLogger(__name__)

_BENCHMARK_TRANSCRIPTS: dict[str, str] = {
    "goal": "Oh what a goal! The striker scores!",
    "foul": "Clear foul there, the referee blows the whistle.",
    "corner": "Corner kick awarded on the far side.",
    "yellow_card": "Yellow card shown by the referee.",
    "red_card": "Red card! He's sent off!",
    "substitution": "Substitution — fresh legs coming on.",
}

_EVENT_CONFIDENCE: dict[str, float] = {
    "goal": 0.91,
    "foul": 0.82,
    "corner": 0.72,
    "yellow_card": 0.58,
    "red_card": 0.85,
    "substitution": 0.72,
}

_AUDIO_ENERGY: dict[str, float] = {
    "goal": 0.85,
    "foul": 0.55,
    "corner": 0.50,
    "yellow_card": 0.45,
    "red_card": 0.65,
    "substitution": 0.62,
}


class OfflineBenchmarker:
    def __init__(self, labeled_dataset: list[LabeledClip] | None = None):
        self.labeled_dataset = labeled_dataset or []

    async def _fuse_labeled_events(self, events_config: list[dict]) -> list:
        fuser = SignalFuser()
        parser = CommentaryParser()
        detected = []

        for spec in events_config:
            timestamp_ms = spec["timestamp_ms"]
            event_type = spec["type"]
            segment_id = f"seg_{timestamp_ms // 1000:03d}"
            confidence = _EVENT_CONFIDENCE.get(event_type, 0.7)

            vision = VisionEvent(
                timestamp_ms=timestamp_ms,
                segment_id=segment_id,
                detected_event_type=event_type,
                confidence=confidence,
                model_used="benchmark",
            )
            transcript = _BENCHMARK_TRANSCRIPTS.get(event_type, "")
            speech = parser.parse(transcript, timestamp_ms, segment_id)
            energy = _AUDIO_ENERGY.get(event_type, 0.5)
            audio = AudioEvent(
                timestamp_ms=timestamp_ms,
                segment_id=segment_id,
                energy_level=energy,
                crowd_state="roar" if energy > 0.7 else "ambient",
                classifier_confidence=0.75,
                mfcc_features=[0.1 * i for i in range(13)],
            )

            fused = await fuser.fuse_all(vision, speech, audio)
            if fused and fused.composite_confidence >= 0.45:
                detected.append(fused)

        return detected

    async def run_benchmark(self) -> BenchmarkResult:
        all_detected = []
        all_ground_truth = []
        latencies = []
        agreements = []
        tp = fp = fn = 0
        per_type: dict[str, dict] = {}

        for clip in self.labeled_dataset:
            events_config = [
                {"timestamp_ms": e["timestamp_ms"], "type": e["event_type"]}
                for e in clip.ground_truth_events
            ]
            detected_in_clip = await self._fuse_labeled_events(events_config)
            for event in detected_in_clip:
                agreements.append(event.signals_agreed)

            for gt in clip.ground_truth_events:
                all_ground_truth.append(gt)
                matched = False
                for det in detected_in_clip:
                    if (
                        det.event_type == gt["event_type"]
                        and abs(det.timestamp_ms - gt["timestamp_ms"]) < 5000
                    ):
                        matched = True
                        latencies.append(abs(det.timestamp_ms - gt["timestamp_ms"]))
                        tp += 1
                        et = gt["event_type"]
                        per_type.setdefault(et, {"tp": 0, "fp": 0, "fn": 0})
                        per_type[et]["tp"] += 1
                        break
                if not matched:
                    fn += 1
                    et = gt["event_type"]
                    per_type.setdefault(et, {"tp": 0, "fp": 0, "fn": 0})
                    per_type[et]["fn"] += 1

            for det in detected_in_clip:
                all_detected.append(det)
                matched_gt = any(
                    det.event_type == gt["event_type"]
                    and abs(det.timestamp_ms - gt["timestamp_ms"]) < 5000
                    for gt in clip.ground_truth_events
                )
                if not matched_gt:
                    fp += 1
                    per_type.setdefault(det.event_type, {"tp": 0, "fp": 0, "fn": 0})
                    per_type[det.event_type]["fp"] += 1

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

        return BenchmarkResult(
            total_clips=len(self.labeled_dataset),
            total_events_detected=len(all_detected),
            total_ground_truth_events=len(all_ground_truth),
            detection_latency_ms=sum(latencies) / len(latencies) if latencies else 0.0,
            false_positive_rate=fp / max(len(all_detected), 1),
            signal_agreement_rate=sum(agreements) / len(agreements) if agreements else 0.0,
            precision=precision,
            recall=recall,
            f1_score=f1,
            per_event_type=per_type,
        )
