"""Shared CLI output helpers."""

from pipeline.kafka.schemas import FusedEvent


def format_ms(ms: int) -> str:
    minutes = ms // 60000
    seconds = (ms % 60000) // 1000
    return f"{minutes:02d}:{seconds:02d}"


def print_event(event: FusedEvent) -> None:
    status = (
        "AUTO-CONFIRMED"
        if event.auto_confirmed
        else "NEEDS REVIEW" if event.requires_review else "DISCARDED"
    )
    print(
        f"[{format_ms(event.timestamp_ms)}] "
        f"{event.event_type.upper():12} | "
        f"Confidence: {event.composite_confidence:.0%} | "
        f"Signals: {event.signals_agreed}/3 | "
        f"{status}"
    )
    if event.commentary:
        print(f"  >> {event.commentary}")
    if event.highlight_clip_path:
        print(f"  Clip: {event.highlight_clip_path}")
    print()
