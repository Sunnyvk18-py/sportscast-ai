import Header from "@/components/layout/Header";
import LatencyChart from "@/components/metrics/LatencyChart";
import FPRChart from "@/components/metrics/FPRChart";
import AgreementRateChart from "@/components/metrics/AgreementRateChart";
import { useMetrics } from "@/hooks/useMetrics";
import { formatPercent } from "@/lib/utils";

export default function MetricsPage() {
  const { live, history, benchmark } = useMetrics();
  const m = live.data;

  const chartData =
    history.data?.map((h, i) => ({
      timestamp: h.timestamp?.slice(11, 19) ?? `${i}`,
      value: h.avg_confidence * 1000,
      fpr: h.false_positive_rate_estimate,
      one: 0.2,
      two: 0.5,
      three: h.signal_agreement_rate,
    })) ?? [];

  const result = benchmark.data;

  return (
    <div>
      <Header title="Pipeline Metrics" />

      <div className="grid grid-cols-4 gap-4 mb-6">
        {[
          { label: "Events/min", value: m?.events_per_minute?.toFixed(1) ?? "—" },
          { label: "Avg Confidence", value: m ? formatPercent(m.avg_confidence) : "—" },
          { label: "Signal Agreement", value: m ? formatPercent(m.signal_agreement_rate) : "—" },
          { label: "Queue Depth", value: String(m?.review_queue_depth ?? "—") },
        ].map((stat) => (
          <div key={stat.label} className="rounded-xl border border-border bg-card p-4">
            <div className="text-xs text-foreground/50">{stat.label}</div>
            <div className="text-2xl font-semibold tabular-nums mt-1">{stat.value}</div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-8">
        <ChartCard title="Detection Latency">
          <LatencyChart data={chartData.map((d) => ({ timestamp: d.timestamp, value: d.value }))} />
        </ChartCard>
        <ChartCard title="False Positive Rate">
          <FPRChart data={chartData.map((d) => ({ timestamp: d.timestamp, value: d.fpr }))} />
        </ChartCard>
        <ChartCard title="Signal Agreement">
          <AgreementRateChart
            data={chartData.map((d) => ({
              timestamp: d.timestamp,
              one: d.one,
              two: d.two,
              three: d.three,
            }))}
          />
        </ChartCard>
      </div>

      <div className="rounded-xl border border-border bg-card p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-medium">Offline Benchmark</h3>
          <button
            onClick={() => benchmark.mutate()}
            disabled={benchmark.isPending}
            className="px-4 py-2 rounded-lg bg-vision text-white text-sm hover:bg-vision/90 disabled:opacity-50"
          >
            {benchmark.isPending ? "Running…" : "Run Offline Benchmark"}
          </button>
        </div>
        {result && (
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div>Precision: {formatPercent(result.precision)}</div>
            <div>Recall: {formatPercent(result.recall)}</div>
            <div>F1: {formatPercent(result.f1_score)}</div>
            <div>Latency: {result.detection_latency_ms.toFixed(0)}ms</div>
            <div>FPR: {formatPercent(result.false_positive_rate)}</div>
            <div>Agreement: {formatPercent(result.signal_agreement_rate)}</div>
          </div>
        )}
      </div>
    </div>
  );
}

function ChartCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="rounded-xl border border-border bg-card p-4">
      <h3 className="text-sm font-medium mb-3 text-foreground/70">{title}</h3>
      {children}
    </div>
  );
}
