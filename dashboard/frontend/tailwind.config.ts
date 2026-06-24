/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "#080C14",
        card: "#0F1629",
        border: "#1E2A45",
        foreground: "#E8EDF5",
        goal: "#22C55E",
        foul: "#F97316",
        corner: "#6366F1",
        yellow_card: "#EAB308",
        red_card: "#EF4444",
        substitution: "#8B5CF6",
        vision: "#3B82F6",
        speech: "#10B981",
        audio: "#F59E0B",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
