import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";

export function useReview() {
  const qc = useQueryClient();
  const query = useQuery({ queryKey: ["review"], queryFn: api.getReview });
  const stats = useQuery({ queryKey: ["review-stats"], queryFn: api.getReviewStats });

  const refresh = () => {
    qc.invalidateQueries({ queryKey: ["review"] });
    qc.invalidateQueries({ queryKey: ["review-stats"] });
  };

  return { ...query, stats: stats.data, refresh };
}
