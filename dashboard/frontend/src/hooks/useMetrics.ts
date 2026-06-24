import { useMutation, useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

export function useMetrics() {
  const live = useQuery({ queryKey: ["metrics-live"], queryFn: api.getLiveMetrics, refetchInterval: 10000 });
  const history = useQuery({ queryKey: ["metrics-history"], queryFn: api.getMetricsHistory });
  const benchmark = useMutation({ mutationFn: api.runBenchmark });
  return { live, history, benchmark };
}
