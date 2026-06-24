import { useState } from "react";
import Header from "@/components/layout/Header";
import EventFeed from "@/components/live/EventFeed";
import { SignalMonitorCards } from "@/components/live/SignalMonitor";
import { useLiveEvents } from "@/hooks/useLiveEvents";
import { useMetrics } from "@/hooks/useMetrics";
import { formatPercent } from "@/lib/utils";
import { api } from "@/lib/api";

export default function LiveDashboard() {
  const { events, connected } = useLiveEvents();
  const { live } = useMetrics();
  const [creating, setCreating] = useState(false);

  const last = events[0];
  const metrics = live.data;

  const startMatch = async () => {
    setCreating(true);
    try {
      await api.createMatch("Live Match", "stream://pending");
    } finally {
      setCreating(false);
    }
  };

  return (
    <div>
      <Header title="Live Match">
        <button
          onClick={startMatch}
          disabled={creating}
          className="px-4 py-2 rounded-lg bg-vision text-white text-sm font-medium hover:bg-vision/90"
        >
          Start New Match
        </button>
        <span
          className={`flex items-center gap-2 text-sm ${connected ? "text-goal" : "text-foreground/40"}`}
        >
          <span className={`w-2 h-2 rounded-full ${connected ? "bg-goal animate-pulse" : "bg-foreground/30"}`} />
          {connected ? "Live" : "Disconnected"}
        </span>
      </Header>

      <div className="flex gap-6">
        <div className="w-[60%]">
          <EventFeed events={events} />
        </div>
        <div className="w-[40%] space-y-4">
          <SignalMonitorCards
            lastVision={last?.vision_signal}
            lastSpeech={last?.speech_signal}
            lastAudio={last?.audio_signal}
          />
          <div className="rounded-xl border border-border bg-card p-4 grid grid-cols-3 gap-2 text-center text-xs">
            <div>
              <div className="text-foreground/50">Events/min</div>
              <div className="tabular-nums font-semibold mt-1">
                {metrics?.events_per_minute?.toFixed(1) ?? "—"}
              </div>
            </div>
            <div>
              <div className="text-foreground/50">Avg Confidence</div>
              <div className="tabular-nums font-semibold mt-1">
                {metrics ? formatPercent(metrics.avg_confidence) : "—"}
              </div>
            </div>
            <div>
              <div className="text-foreground/50">Queue Depth</div>
              <div className="tabular-nums font-semibold mt-1">
                {metrics?.review_queue_depth ?? "—"}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
