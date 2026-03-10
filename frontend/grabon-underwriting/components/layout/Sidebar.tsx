"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutGrid,
  ListOrdered,
  ChevronRight,
  Activity,
  ShieldCheck,
} from "lucide-react";

const navItems = [
  { label: "Merchant Console", href: "/", icon: LayoutGrid, exact: true },
  { label: "Run Ledger", href: "/runs", icon: ListOrdered, exact: false },
];

export function Sidebar() {
  const pathname = usePathname();

  function isActive(href: string, exact: boolean) {
    return exact ? pathname === href : pathname.startsWith(href);
  }

  return (
    <aside className="nav-surface fixed left-0 top-0 z-40 flex h-screen w-72 flex-col">
      <div className="border-b border-ink-100 px-6 pb-5 pt-6">
        <div className="flex items-start gap-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-go-600 text-white shadow-brand">
            <ShieldCheck className="h-6 w-6" />
          </div>
          <div className="space-y-1.5">
            <div>
              <div className="text-[11px] font-semibold uppercase tracking-[0.24em] text-go-600">
                Fintech Control
              </div>
              <div className="font-display text-xl font-bold tracking-tight text-ink-900">
                GrabOn Underwriting
              </div>
            </div>
            <p className="text-sm text-ink-500">Underwriting ops.</p>
          </div>
        </div>

        <div className="mt-5 inline-flex items-center gap-2 rounded-2xl border border-go-200 bg-go-50 px-3 py-2 text-xs font-semibold text-go-700">
          <Activity className="h-3.5 w-3.5" />
          System online
        </div>
      </div>

      <div className="flex-1 px-4 py-5">
        <div className="px-3 text-[10px] font-semibold uppercase tracking-[0.22em] text-ink-400">
          Workspace
        </div>
        <nav className="mt-3 space-y-1.5">
          {navItems.map(({ label, href, icon: Icon, exact }) => {
            const active = isActive(href, exact);
            return (
              <Link
                key={href}
                href={href}
                className={cn(
                  "group flex items-center gap-3 rounded-2xl border px-3.5 py-3 text-sm font-semibold transition-all duration-200",
                  active
                    ? "border-go-200 bg-go-50 text-go-700 shadow-card"
                    : "border-transparent text-ink-500 hover:border-ink-100 hover:bg-white hover:text-ink-800"
                )}
              >
                <div
                  className={cn(
                    "flex h-9 w-9 items-center justify-center rounded-xl border transition-colors",
                    active
                      ? "border-go-200 bg-white text-go-700"
                      : "border-ink-100 bg-ink-50 text-ink-400 group-hover:border-go-100 group-hover:bg-go-50 group-hover:text-go-600"
                  )}
                >
                  <Icon className="h-4.5 w-4.5" />
                </div>
                <div className="flex-1">
                  <div>{label}</div>
                </div>
                <ChevronRight
                  className={cn(
                    "h-4 w-4 transition-transform",
                    active ? "text-go-500" : "text-ink-300 group-hover:translate-x-0.5 group-hover:text-go-500"
                  )}
                />
              </Link>
            );
          })}
        </nav>
      </div>

      <div className="border-t border-ink-100 bg-surface-muted px-6 py-4">
        <div className="text-[10px] font-semibold uppercase tracking-[0.2em] text-ink-400">
          Delivery
        </div>
        <div className="mt-1 text-sm font-semibold text-ink-800">Live</div>
      </div>
    </aside>
  );
}
