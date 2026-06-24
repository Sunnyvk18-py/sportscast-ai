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
