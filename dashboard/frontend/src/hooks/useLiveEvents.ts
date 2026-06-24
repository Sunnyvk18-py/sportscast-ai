import { useCallback, useEffect, useRef, useState } from "react";
import type { FusedEvent } from "@/lib/types";

const WS_URL = import.meta.env.VITE_WS_URL || `${window.location.protocol === "https:" ? "wss" : "ws"}://${window.location.host}/ws/events`;

export function useLiveEvents() {
  const [events, setEvents] = useState<FusedEvent[]>([]);
  const [connected, setConnected] = useState(false);
  const retryRef = useRef(1000);

  const connect = useCallback(() => {
    const ws = new WebSocket(WS_URL);

    ws.onopen = () => {
      setConnected(true);
      retryRef.current = 1000;
    };

    ws.onmessage = (msg) => {
      try {
        const data = JSON.parse(msg.data);
        if (data.type === "new_event") {
          setEvents((prev) => [data.data as FusedEvent, ...prev].slice(0, 100));
        } else if (data.type === "ping") {
          ws.send(JSON.stringify({ type: "pong" }));
        }
      } catch {
        /* ignore */
      }
    };

    ws.onclose = () => {
      setConnected(false);
      const delay = Math.min(retryRef.current, 30000);
      retryRef.current = Math.min(retryRef.current * 2, 30000);
      setTimeout(connect, delay);
    };

    ws.onerror = () => ws.close();

    return ws;
  }, []);

  useEffect(() => {
    const ws = connect();
    return () => ws.close();
  }, [connect]);

  return { events, connected };
}
