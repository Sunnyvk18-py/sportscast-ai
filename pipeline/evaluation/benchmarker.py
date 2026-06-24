"""Offline benchmark vs labeled clips."""

import logging

from pipeline.evaluation.labeled_clips import LabeledClip
from pipeline.evaluation.metrics import BenchmarkResult
from pipeline.testing.mock_pipeline import MockPipeline

logger = logging.getLogger(__name__)


class OfflineBenchmarker:
    def __init__(self, labeled_dataset: list[LabeledClip] | None = None):
        self.labeled_dataset = labeled_dataset or []

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
            max_ts = max((e["timestamp_ms"] for e in clip.ground_truth_events), default=60000)
            pipeline = MockPipeline(
                duration_seconds=max(max_ts // 1000 + 5, 10),
                events_to_simulate=events_config,
                commentary_enabled=False,
            )

            detected_in_clip = []
            async for event in pipeline.run():
                if event.composite_confidence >= 0.45:
                    detected_in_clip.append(event)
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
