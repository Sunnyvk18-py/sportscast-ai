import { NavLink } from "react-router-dom";
import { Activity, BarChart3, Film, LayoutDashboard, List, ShieldCheck } from "lucide-react";
import { cn } from "@/lib/utils";

const links = [
  { to: "/", label: "Live", icon: LayoutDashboard },
  { to: "/events", label: "Events", icon: List },
  { to: "/review", label: "Review", icon: ShieldCheck },
  { to: "/highlights", label: "Highlights", icon: Film },
  { to: "/metrics", label: "Metrics", icon: BarChart3 },
];

export default function Sidebar() {
  return (
    <aside className="w-56 shrink-0 border-r border-border bg-card min-h-screen p-4">
      <div className="flex items-center gap-2 mb-8 px-2">
        <Activity className="text-vision w-6 h-6" />
        <span className="font-bold text-lg">SportsCast AI</span>
      </div>
      <nav className="space-y-1">
        {links.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors",
                isActive ? "bg-border text-foreground" : "text-foreground/60 hover:text-foreground hover:bg-border/50"
              )
            }
          >
            <Icon className="w-4 h-4" />
            {label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
