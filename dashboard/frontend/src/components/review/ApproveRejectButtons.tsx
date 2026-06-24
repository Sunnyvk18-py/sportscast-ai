import { useState } from "react";
import { api } from "@/lib/api";

interface Props {
  eventId: string;
  onComplete: () => void;
}

export default function ApproveRejectButtons({ eventId, onComplete }: Props) {
  const [notes, setNotes] = useState("");
  const [loading, setLoading] = useState(false);

  const handle = async (action: "approve" | "reject") => {
    setLoading(true);
    try {
      if (action === "approve") await api.approveReview(eventId, notes);
      else await api.rejectReview(eventId, notes);
      onComplete();
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-3">
      <textarea
        className="w-full rounded-lg border border-border bg-background p-2 text-sm"
        placeholder="Reviewer notes (optional)"
        value={notes}
        onChange={(e) => setNotes(e.target.value)}
        rows={2}
      />
      <div className="flex gap-3">
        <button
          disabled={loading}
          onClick={() => handle("approve")}
          className="flex-1 py-2 rounded-lg bg-goal text-white font-medium hover:bg-goal/90 disabled:opacity-50"
        >
          Approve
        </button>
        <button
          disabled={loading}
          onClick={() => handle("reject")}
          className="flex-1 py-2 rounded-lg bg-red_card text-white font-medium hover:bg-red_card/90 disabled:opacity-50"
        >
          Reject
        </button>
      </div>
    </div>
  );
}
