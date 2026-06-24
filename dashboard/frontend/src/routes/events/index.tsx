import Header from "@/components/layout/Header";
import EventsTable from "@/components/events/EventsTable";
import { useEvents } from "@/hooks/useEvents";

export default function EventsPage() {
  const { data = [], isLoading } = useEvents();

  return (
    <div>
      <Header title="All Events" />
      {isLoading ? (
        <p className="text-foreground/50">Loading…</p>
      ) : (
        <div className="rounded-xl border border-border bg-card p-4">
          <EventsTable data={data} />
        </div>
      )}
    </div>
  );
}
