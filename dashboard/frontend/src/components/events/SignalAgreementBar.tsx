import type { FusedEvent } from "@/lib/types";

interface Props {
  event: FusedEvent;
}

export default function SignalAgreementBar({ event }: Props) {
  const visionAgreed =
    event.vision_signal?.detected_event_type === event.event_type &&
    (event.vision_signal?.confidence ?? 0) > 0.3;
  const speechAgreed =
    event.speech_signal?.detected_event_type === event.event_type &&
    (event.speech_signal?.commentary_confidence ?? 0) > 0.3;
  const audioAgreed = (event.audio_signal?.energy_level ?? 0) > 0.5;

  const segments = [
    { label: "👁 Vision", active: visionAgreed, color: "bg-vision" },
    { label: "🎤 Speech", active: speechAgreed, color: "bg-speech" },
    { label: "🔊 Audio", active: audioAgreed, color: "bg-audio" },
  ];

  return (
    <div className="flex gap-1">
      {segments.map((seg) => (
        <div
          key={seg.label}
          className={`flex-1 rounded px-2 py-1 text-xs text-center ${
            seg.active ? seg.color + " text-white" : "bg-border text-foreground/40"
          }`}
        >
          {seg.label}
        </div>
      ))}
    </div>
  );
}
