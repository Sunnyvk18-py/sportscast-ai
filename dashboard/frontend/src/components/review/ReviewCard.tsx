import type { DetectedEvent } from "@/lib/types";
import { formatPercent, formatTimestamp } from "@/lib/utils";
import EventTypeBadge from "../events/EventTypeBadge";
import ApproveRejectButtons from "./ApproveRejectButtons";

interface Props {
  event: DetectedEvent;
  onAction: () => void;
}

export default function ReviewCard({ event, onAction }: Props) {
  return (
    <div className="rounded-xl border border-border bg-card p-5">
      <div className="flex items-center justify-between mb-3">
        <EventTypeBadge type={event.event_type} />
        <span className="tabular-nums text-sm text-foreground/60">
          {formatTimestamp(event.timestamp_ms)}
        </span>
      </div>
      <p className="text-sm text-foreground/60 mb-2">
        Confidence {formatPercent(event.composite_confidence)} — below auto-confirm threshold
      </p>
      <p className="text-sm mb-4">{event.commentary ?? "No commentary"}</p>
      <ApproveRejectButtons eventId={event.id} onComplete={onAction} />
    </div>
  );
}
