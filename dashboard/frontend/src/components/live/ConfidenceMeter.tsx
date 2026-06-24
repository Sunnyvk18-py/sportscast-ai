interface Props {
  value: number;
}

export default function ConfidenceMeter({ value }: Props) {
  const pct = Math.round(value * 100);
  const color = value >= 0.75 ? "#22C55E" : value >= 0.45 ? "#EAB308" : "#EF4444";

  return (
    <div className="flex flex-col items-center">
      <div
        className="w-12 h-12 rounded-full border-4 flex items-center justify-center tabular-nums text-xs font-semibold"
        style={{ borderColor: color }}
      >
        {pct}%
      </div>
    </div>
  );
}
