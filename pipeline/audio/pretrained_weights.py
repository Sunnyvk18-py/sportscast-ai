"""Heuristic crowd classifier fallback when no weights available."""


class HeuristicCrowdClassifier:
    def classify(self, features: dict) -> tuple[str, float]:
        energy = features.get("energy", 0.0)
        if energy > 0.8:
            return "roar", 0.85
        if energy > 0.6:
            return "cheer", 0.75
        if energy > 0.4:
            return "ambient", 0.65
        if energy > 0.2:
            return "ambient", 0.60
        return "silence", 0.80

    def classify_for_event(self, event_type: str | None) -> tuple[str, float, float]:
        """Return crowd_state, confidence, energy for mock pipeline."""
        mapping = {
            "goal": ("roar", 0.88, 0.85),
            "foul": ("groan", 0.72, 0.55),
            "corner": ("ambient", 0.65, 0.50),
            "yellow_card": ("ambient", 0.60, 0.45),
            "red_card": ("groan", 0.70, 0.65),
            "substitution": ("cheer", 0.75, 0.62),
        }
        if event_type and event_type in mapping:
            return mapping[event_type]
        return "ambient", 0.55, 0.35
