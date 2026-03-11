"use client";

import { usePathname } from "next/navigation";
import Link from "next/link";
import { ChevronRight, Clock3, Moon, Radar, Sun } from "lucide-react";
import { useEffect, useState } from "react";
import { format } from "date-fns";

interface Crumb {
  label: string;
  href?: string;
}

export function TopBar({ crumbs }: { crumbs?: Crumb[] }) {
  const pathname = usePathname();
  const [time, setTime] = useState("");
  const [theme, setTheme] = useState<"light" | "dark">("dark");

  useEffect(() => {
    const update = () => setTime(format(new Date(), "HH:mm:ss"));
    update();
    const id = setInterval(update, 1000);
    return () => clearInterval(id);
  }, []);

  useEffect(() => {
    const root = document.documentElement;
    const isDark = root.classList.contains("dark");
    setTheme(isDark ? "dark" : "light");
  }, []);

  function toggleTheme() {
    const next = theme === "dark" ? "light" : "dark";
    setTheme(next);
    document.documentElement.classList.toggle("dark", next === "dark");
    localStorage.setItem("grabon-theme", next);
  }

  const displayCrumbs = crumbs ?? generateCrumbs(pathname);

  return (
    <header className="sticky top-0 z-30 border-b border-ink-100 bg-surface-card px-6 py-3">
      <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
        <nav className="flex min-h-[24px] flex-wrap items-center gap-1.5 text-sm">
          {displayCrumbs.map((crumb, i) => (
            <span key={`${crumb.label}-${i}`} className="flex items-center gap-1.5">
              {i > 0 ? <ChevronRight className="h-3.5 w-3.5 text-ink-300" /> : null}
              {crumb.href && i < displayCrumbs.length - 1 ? (
                <Link
                  href={crumb.href}
                  className="font-medium text-ink-400 transition-colors hover:text-go-700"
                >
                  {crumb.label}
                </Link>
              ) : (
                <span className="font-semibold text-ink-700">{crumb.label}</span>
              )}
            </span>
          ))}
        </nav>

        <div className="flex flex-wrap items-center gap-3">
          <div className="status-pill border-go-200 bg-go-50 text-go-700">
            <Radar className="h-3.5 w-3.5" />
            Live
          </div>
          <button onClick={toggleTheme} className="btn-outline px-3 py-1.5 text-xs">
            {theme === "dark" ? <Sun className="h-3.5 w-3.5" /> : <Moon className="h-3.5 w-3.5" />}
            {theme === "dark" ? "Light" : "Dark"}
          </button>
          <div className="status-pill border-ink-100 bg-surface-card text-ink-500">
            <Clock3 className="h-3.5 w-3.5" />
            <span className="font-mono tabular-nums">{time}</span>
          </div>
        </div>
      </div>
    </header>
  );
}

function generateCrumbs(pathname: string): Crumb[] {
  const parts = pathname.split("/").filter(Boolean);
  const crumbs: Crumb[] = [{ label: "Merchant Console", href: "/" }];

  if (parts[0] === "merchants" && parts[1]) {
    crumbs.push({ label: "Merchant Detail" });
  } else if (parts[0] === "runs") {
    crumbs.push({ label: "Run Ledger", href: "/runs" });
    if (parts[1]) {
      crumbs.push({ label: `Run #${parts[1]}`, href: `/runs/${parts[1]}` });
      if (parts[2] === "communicate") crumbs.push({ label: "Communications" });
      if (parts[2] === "accept") crumbs.push({ label: "Offer Acceptance" });
      if (parts[2] === "mandate") crumbs.push({ label: "Mandate Flow" });
    }
  } else if (parts[0] === "settings") {
    crumbs.push({ label: "Settings" });
  }
  return crumbs;
}
