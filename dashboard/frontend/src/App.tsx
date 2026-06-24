import { BrowserRouter, Route, Routes } from "react-router-dom";
import Layout from "./components/layout/Layout";
import LiveDashboard from "./routes/index";
import EventsPage from "./routes/events/index";
import EventDetailPage from "./routes/events/[id]";
import ReviewPage from "./routes/review/index";
import HighlightsPage from "./routes/highlights/index";
import MetricsPage from "./routes/metrics/index";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<LiveDashboard />} />
          <Route path="/events" element={<EventsPage />} />
          <Route path="/events/:id" element={<EventDetailPage />} />
          <Route path="/review" element={<ReviewPage />} />
          <Route path="/highlights" element={<HighlightsPage />} />
          <Route path="/metrics" element={<MetricsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
