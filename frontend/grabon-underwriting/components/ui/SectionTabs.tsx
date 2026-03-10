"use client";

import { TabsList, TabsTrigger } from "@/components/ui/tabs";
import { cn } from "@/lib/utils";

export interface SectionTabItem {
  value: string;
  label: string;
  count?: string;
}

export function SectionTabs({
  items,
  className,
}: {
  items: SectionTabItem[];
  className?: string;
}) {
  return (
    <TabsList
      variant="line"
      className={cn(
        "sticky top-0 z-10 w-full justify-start gap-1 overflow-x-auto rounded-2xl border border-ink-100 bg-white px-2 py-2 shadow-card",
        className
      )}
    >
      {items.map((item) => (
        <TabsTrigger
          key={item.value}
          value={item.value}
          className="rounded-md px-3 py-2 text-sm font-semibold text-ink-500 transition-colors hover:text-ink-800 data-active:text-go-700 [&::after]:!bg-go-600"
        >
          <span>{item.label}</span>
          {item.count ? (
            <span className="rounded-full bg-white px-1.5 py-0.5 text-[10px] font-mono text-ink-400 ring-1 ring-ink-100">
              {item.count}
            </span>
          ) : null}
        </TabsTrigger>
      ))}
    </TabsList>
  );
}
