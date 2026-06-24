import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

export function useHighlights() {
  return useQuery({ queryKey: ["highlights"], queryFn: api.getHighlights });
}
