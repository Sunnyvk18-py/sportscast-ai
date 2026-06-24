import { formatPercent } from "@/lib/utils";
import type { FusedEvent } from "@/lib/types";

interface SignalMonitorProps {
  lastVision?: FusedEvent["vision_signal"];
  lastSpeech?: FusedEvent["speech_signal"];
  lastAudio?: FusedEvent["audio_signal"];
}

export function SignalMonitorCards({ lastVision, lastSpeech, lastAudio }: SignalMonitorProps) {
  return (
    <div className="space-y-3">
      <SignalCard
        label="Vision"
        color="text-vision"
        content={
          lastVision
            ? `${lastVision.detected_event_type ?? "none"} · ${formatPercent(lastVision.confidence)} · ${lastVision.processing_ms}ms`
            : "No data"
        }
      />
      <SignalCard
        label="Speech"
        color="text-speech"
        content={
          lastSpeech
            ? `"${lastSpeech.transcript.slice(0, 60)}${lastSpeech.transcript.length > 60 ? "…" : ""}"`
            : "No data"
        }
      />
      <SignalCard
        label="Audio"
        color="text-audio"
        content={
          lastAudio
            ? `${lastAudio.crowd_state} · energy ${formatPercent(lastAudio.energy_level)}`
            : "No data"
        }
      />
    </div>
  );
}

function SignalCard({ label, color, content }: { label: string; color: string; content: string }) {
  return (
    <div className="rounded-xl border border-border bg-card p-4">
      <div className={`text-xs font-medium mb-1 ${color}`}>{label}</div>
      <div className="text-sm text-foreground/80">{content}</div>
    </div>
  );
}
