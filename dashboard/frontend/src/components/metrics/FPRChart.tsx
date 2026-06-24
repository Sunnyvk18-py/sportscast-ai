import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

interface Props {
  data: { timestamp: string; value: number }[];
}

export default function FPRChart({ data }: Props) {
  return (
    <ResponsiveContainer width="100%" height={220}>
      <LineChart data={data}>
        <CartesianGrid stroke="#1E2A45" />
        <XAxis dataKey="timestamp" tick={{ fill: "#E8EDF5", fontSize: 11 }} />
        <YAxis tick={{ fill: "#E8EDF5", fontSize: 11 }} />
        <Tooltip contentStyle={{ background: "#0F1629", border: "1px solid #1E2A45" }} />
        <Line type="monotone" dataKey="value" stroke="#EF4444" dot={false} name="FPR" />
      </LineChart>
    </ResponsiveContainer>
  );
}
