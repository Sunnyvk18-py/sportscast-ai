import { useParams, Link } from "react-router-dom";
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer } from "recharts";
import Header from "@/components/layout/Header";
import EventTypeBadge from "@/components/events/EventTypeBadge";
import { useEvent } from "@/hooks/useEvents";
import { formatPercent, formatTimestamp } from "@/lib/utils";

export default function EventDetailPage() {
  const { id = "" } = useParams();
  const { data: event, isLoading } = useEvent(id);

  if (isLoading) return <p className="text-foreground/50">Loading…</p>;
  if (!event) return <p>Event not found. <Link to="/events" className="text-vision">Back</Link></p>;

  const mfccData = Array.from({ length: 13 }, (_, i) => ({
    coeff: `M${i + 1}`,
    value: (event.audio_energy ?? 0.1) * (i + 1) * 0.08,
  }));

  return (
    <div>
      <Header title="Event Detail">
        <Link to="/events" className="text-sm text-vision hover:underline">← Back</Link>
      </Header>

      <div className="rounded-xl border border-border bg-card p-6 mb-6">
        <div className="flex items-center gap-4">
          <EventTypeBadge type={event.event_type} />
          <span className="tabular-nums">{formatTimestamp(event.timestamp_ms)}</span>
          <span className="text-sm">{formatPercent(event.composite_confidence)} confidence</span>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-6">
        <SignalCard title="Vision" color="text-vision">
          <p>Type: {event.event_type}</p>
          <p>Confidence: {event.vision_confidence != null ? formatPercent(event.vision_confidence) : "—"}</p>
        </SignalCard>
        <SignalCard title="Speech" color="text-speech">
          <p>Confidence: {event.speech_confidence != null ? formatPercent(event.speech_confidence) : "—"}</p>
          <p className="text-sm mt-2 italic">{event.commentary ?? "No transcript stored"}</p>
        </SignalCard>
        <SignalCard title="Audio" color="text-audio">
          <p>Energy: {event.audio_energy != null ? formatPercent(event.audio_energy) : "—"}</p>
          <div className="h-24 mt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={mfccData}>
                <XAxis dataKey="coeff" tick={{ fill: "#E8EDF5", fontSize: 9 }} />
                <YAxis hide />
                <Bar dataKey="value" fill="#F59E0B" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </SignalCard>
      </div>

      <div className="rounded-xl border border-border bg-card p-6 mb-6">
        <h3 className="font-medium mb-2">Fusion Decision</h3>
        <p className="text-sm text-foreground/70">
          Vision (45%) + Speech (35%) + Audio (20%) = {formatPercent(event.composite_confidence)}.
          Signals agreed: {event.signals_agreed}/3.
        </p>
      </div>

      {event.commentary && (
        <div className="rounded-xl border border-border bg-card p-6 mb-6">
          <h3 className="font-medium mb-2">Commentary</h3>
          <p className="italic">{event.commentary}</p>
        </div>
      )}

      {event.highlight_clip_path && (
        <div className="rounded-xl border border-border bg-card p-6">
          <h3 className="font-medium mb-2">Highlight Clip</h3>
          <video controls className="w-full max-w-lg rounded" src={`/api/highlights/${event.id}/download`} />
        </div>
      )}
    </div>
  );
}

function SignalCard({ title, color, children }: { title: string; color: string; children: React.ReactNode }) {
  return (
    <div className="rounded-xl border border-border bg-card p-4">
      <h3 className={`text-sm font-medium mb-3 ${color}`}>{title}</h3>
      <div className="text-sm space-y-1">{children}</div>
    </div>
  );
}
