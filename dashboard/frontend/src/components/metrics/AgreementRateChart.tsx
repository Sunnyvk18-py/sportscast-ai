import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

interface Props {
  data: { timestamp: string; one: number; two: number; three: number }[];
}

export default function AgreementRateChart({ data }: Props) {
  return (
    <ResponsiveContainer width="100%" height={220}>
      <AreaChart data={data}>
        <CartesianGrid stroke="#1E2A45" />
        <XAxis dataKey="timestamp" tick={{ fill: "#E8EDF5", fontSize: 11 }} />
        <YAxis tick={{ fill: "#E8EDF5", fontSize: 11 }} />
        <Tooltip contentStyle={{ background: "#0F1629", border: "1px solid #1E2A45" }} />
        <Area type="monotone" dataKey="one" stackId="1" stroke="#EF4444" fill="#EF4444" name="1 signal" />
        <Area type="monotone" dataKey="two" stackId="1" stroke="#EAB308" fill="#EAB308" name="2 signals" />
        <Area type="monotone" dataKey="three" stackId="1" stroke="#22C55E" fill="#22C55E" name="3 signals" />
      </AreaChart>
    </ResponsiveContainer>
  );
}
