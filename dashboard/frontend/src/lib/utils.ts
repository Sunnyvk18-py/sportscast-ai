import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatTimestamp(ms: number): string {
  const minutes = Math.floor(ms / 60000);
  const seconds = Math.floor((ms % 60000) / 1000);
  return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
}

export function formatPercent(value: number): string {
  return `${Math.round(value * 100)}%`;
}

export const EVENT_COLORS: Record<string, string> = {
  goal: "text-goal",
  foul: "text-foul",
  corner: "text-corner",
  yellow_card: "text-yellow_card",
  red_card: "text-red_card",
  substitution: "text-substitution",
};

export const EVENT_ICONS: Record<string, string> = {
  goal: "⚽",
  foul: "⚠️",
  corner: "📐",
  yellow_card: "🟡",
  red_card: "🔴",
  substitution: "🔄",
};

export function eventLabel(type: string): string {
  return type.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}
