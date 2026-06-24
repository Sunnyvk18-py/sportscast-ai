import type { DetectedEvent } from "@/lib/types";
import { formatPercent, formatTimestamp } from "@/lib/utils";
import EventTypeBadge from "../events/EventTypeBadge";
import ClipPlayer from "./ClipPlayer";

interface Props {
  event: DetectedEvent;
}

export default function HighlightCard({ event }: Props) {
  return (
    <div className="rounded-xl border border-border bg-card overflow-hidden">
      <div className="p-4 flex items-center justify-between">
        <EventTypeBadge type={event.event_type} />
        <span className="text-xs tabular-nums text-foreground/60">
          {formatTimestamp(event.timestamp_ms)}
        </span>
      </div>
      {event.highlight_clip_path && <ClipPlayer eventId={event.id} />}
      <div className="p-4">
        <span className="text-xs px-2 py-0.5 rounded bg-border">
          {formatPercent(event.composite_confidence)}
        </span>
        {event.commentary && (
          <p className="mt-2 text-sm text-foreground/70 italic">{event.commentary}</p>
        )}
        <a
          href={`/api/highlights/${event.id}/download`}
          className="inline-block mt-3 text-sm text-vision hover:underline"
        >
          Download clip
        </a>
      </div>
    </div>
  );
}
