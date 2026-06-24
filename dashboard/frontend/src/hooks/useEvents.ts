import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

export function useEvents(params?: Record<string, string>) {
  return useQuery({
    queryKey: ["events", params],
    queryFn: () => api.getEvents(params),
  });
}

export function useEvent(id: string) {
  return useQuery({
    queryKey: ["event", id],
    queryFn: () => api.getEvent(id),
    enabled: !!id,
  });
}
