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
        "w-full justify-start gap-2 overflow-x-auto border-b border-ink-100 bg-transparent px-0 py-0",
        className
      )}
    >
      {items.map((item) => (
        <TabsTrigger
          key={item.value}
          value={item.value}
          className="rounded-none border-b-2 border-transparent px-2 py-2 text-sm font-semibold text-ink-500 transition-colors hover:text-ink-800 data-active:border-go-600 data-active:text-go-700 [&::after]:hidden"
        >
          <span>{item.label}</span>
          {item.count ? (
            <span className="rounded-full bg-surface-50 px-1.5 py-0.5 text-[10px] font-mono text-ink-400 ring-1 ring-ink-100">
              {item.count}
            </span>
          ) : null}
        </TabsTrigger>
      ))}
    </TabsList>
  );
}
