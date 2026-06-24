"""Detection latency, FPR, agreement metrics."""

from pydantic import BaseModel, Field


class BenchmarkResult(BaseModel):
    total_clips: int = 0
    total_events_detected: int = 0
    total_ground_truth_events: int = 0
    detection_latency_ms: float = 0.0
    false_positive_rate: float = 0.0
    signal_agreement_rate: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    per_event_type: dict[str, dict] = Field(default_factory=dict)
