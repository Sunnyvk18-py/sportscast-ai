import { formatPercent, formatTimestamp } from "@/lib/utils";
import type { FusedEvent } from "@/lib/types";
import EventTypeBadge from "../events/EventTypeBadge";
import SignalAgreementBar from "../events/SignalAgreementBar";
import ConfidenceMeter from "./ConfidenceMeter";
import CommentaryBox from "./CommentaryBox";

interface Props {
  events: FusedEvent[];
}

export default function EventFeed({ events }: Props) {
  if (events.length === 0) {
    return (
      <div className="rounded-xl border border-border bg-card p-8 text-center text-foreground/50">
        Waiting for live events… Connect the pipeline or run the mock demo.
      </div>
    );
  }

  return (
    <div className="space-y-3 max-h-[70vh] overflow-y-auto pr-2">
      {events.map((event) => (
        <div key={event.event_id} className="rounded-xl border border-border bg-card p-4">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-center gap-3">
              <EventTypeBadge type={event.event_type} />
              <span className="tabular-nums text-sm text-foreground/60">
                {formatTimestamp(event.timestamp_ms)}
              </span>
            </div>
            <ConfidenceMeter value={event.composite_confidence} />
          </div>
          <div className="mt-3">
            <SignalAgreementBar event={event} />
          </div>
          {event.commentary && (
            <div className="mt-3">
              <CommentaryBox text={event.commentary} />
            </div>
          )}
          <div className="mt-2 flex gap-2">
            {event.auto_confirmed && (
              <span className="text-xs px-2 py-0.5 rounded bg-goal/20 text-goal">Confirmed</span>
            )}
            {event.requires_review && (
              <span className="text-xs px-2 py-0.5 rounded bg-yellow_card/20 text-yellow_card">
                Review
              </span>
            )}
            <span className="text-xs text-foreground/40 tabular-nums ml-auto">
              {formatPercent(event.composite_confidence)} · {event.signals_agreed}/3 signals
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}
