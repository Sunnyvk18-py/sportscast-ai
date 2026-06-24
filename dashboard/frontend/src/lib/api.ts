const API_BASE = import.meta.env.VITE_API_URL || "";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export const api = {
  getEvents: (params?: Record<string, string>) => {
    const qs = params ? "?" + new URLSearchParams(params).toString() : "";
    return request<import("./types").DetectedEvent[]>(`/api/events${qs}`);
  },
  getEvent: (id: string) => request<import("./types").DetectedEvent>(`/api/events/${id}`),
  getMatches: () => request<import("./types").MatchSession[]>("/api/matches"),
  createMatch: (name: string, source_url: string) =>
    request<import("./types").MatchSession>("/api/matches", {
      method: "POST",
      body: JSON.stringify({ name, source_url }),
    }),
  getReview: () => request<import("./types").DetectedEvent[]>("/api/review"),
  approveReview: (id: string, notes = "") =>
    request(`/api/review/${id}/approve`, { method: "POST", body: JSON.stringify({ notes }) }),
  rejectReview: (id: string, notes = "") =>
    request(`/api/review/${id}/reject`, { method: "POST", body: JSON.stringify({ notes }) }),
  getReviewStats: () =>
    request<{ total: number; approved: number; rejected: number; pending: number }>(
      "/api/review/stats"
    ),
  getHighlights: () => request<import("./types").DetectedEvent[]>("/api/highlights"),
  getLiveMetrics: () => request<import("./types").LiveMetrics>("/api/metrics/live"),
  getMetricsHistory: () => request<import("./types").LiveMetrics[]>("/api/metrics/history"),
  runBenchmark: () =>
    request<import("./types").BenchmarkResult>("/api/metrics/benchmark", { method: "POST" }),
};
