"""Per-event confidence computation."""

from pipeline.kafka.schemas import AudioEvent, SpeechEvent, VisionEvent


class ConfidenceScorer:
    def score(
        self,
        vision: VisionEvent | None,
        speech: SpeechEvent | None,
        audio: AudioEvent | None,
        event_type: str,
    ) -> tuple[float, int]:
        base_confidence = 0.0
        signals_agreed = 0

        if vision and vision.detected_event_type == event_type:
            base_confidence += 0.45 * vision.confidence
            signals_agreed += 1

        if speech and speech.detected_event_type == event_type:
            base_confidence += 0.35 * speech.commentary_confidence
            signals_agreed += 1

        if audio:
            audio_boost = self.energy_to_confidence(audio.energy_level, event_type)
            base_confidence += 0.20 * audio_boost
            if audio_boost > 0.6:
                signals_agreed += 1

        composite = min(1.0, base_confidence)
        signals_agreed = min(3, signals_agreed)
        return composite, signals_agreed

    def energy_to_confidence(self, energy: float, event_type: str) -> float:
        if event_type in ("goal", "foul") and energy > 0.7:
            return 0.9
        if event_type in ("corner", "substitution") and 0.4 <= energy <= 0.7:
            return 0.6
        if energy < 0.4:
            return 0.3
        if energy > 0.7:
            return 0.85
        return 0.5
