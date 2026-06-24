import Header from "@/components/layout/Header";
import ReviewCard from "@/components/review/ReviewCard";
import { useReview } from "@/hooks/useReview";

export default function ReviewPage() {
  const { data = [], stats, refresh, isLoading } = useReview();

  return (
    <div>
      <Header title="Review Queue">
        <span className="text-sm px-3 py-1 rounded-full bg-yellow_card/20 text-yellow_card">
          {stats?.pending ?? data.length} items pending review
        </span>
      </Header>

      {isLoading ? (
        <p className="text-foreground/50">Loading…</p>
      ) : data.length === 0 ? (
        <div className="rounded-xl border border-border bg-card p-12 text-center text-foreground/50">
          All caught up! No items in review.
        </div>
      ) : (
        <div className="grid gap-4 max-w-2xl">
          {data.map((event) => (
            <ReviewCard key={event.id} event={event} onAction={refresh} />
          ))}
        </div>
      )}
    </div>
  );
}
