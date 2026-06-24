import { EVENT_ICONS, eventLabel } from "@/lib/utils";

interface Props {
  type: string;
}

export default function EventTypeBadge({ type }: Props) {
  return (
    <span className="inline-flex items-center gap-1.5 text-sm font-medium">
      <span>{EVENT_ICONS[type] ?? "•"}</span>
      {eventLabel(type)}
    </span>
  );
}
