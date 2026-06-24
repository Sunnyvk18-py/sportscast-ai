import Header from "@/components/layout/Header";
import HighlightCard from "@/components/highlights/HighlightCard";
import { useHighlights } from "@/hooks/useHighlights";

export default function HighlightsPage() {
  const { data = [], isLoading } = useHighlights();

  return (
    <div>
      <Header title="Highlights" />
      {isLoading ? (
        <p className="text-foreground/50">Loading…</p>
      ) : data.length === 0 ? (
        <div className="rounded-xl border border-border bg-card p-12 text-center text-foreground/50">
          No highlight clips generated yet. Run the pipeline to generate clips automatically.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {data.map((event) => (
            <HighlightCard key={event.id} event={event} />
          ))}
        </div>
      )}
    </div>
  );
}
