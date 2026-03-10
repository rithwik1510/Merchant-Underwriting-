import { cn } from "@/lib/utils";

interface LoadingPulseProps {
  className?: string;
  lines?: number;
}

export function LoadingPulse({ className, lines = 1 }: LoadingPulseProps) {
  return (
    <div className={cn("space-y-2", className)}>
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className="h-4 rounded shimmer"
          style={{ width: `${85 - i * 12}%` }}
        />
      ))}
    </div>
  );
}

export function LoadingCard({ className }: { className?: string }) {
  return (
    <div className={cn("rounded-xl border border-navy-700 bg-navy-800 p-5 space-y-3", className)}>
      <div className="h-3 w-20 rounded shimmer" />
      <div className="h-7 w-32 rounded shimmer" />
      <div className="h-3 w-full rounded shimmer" />
      <div className="h-3 w-3/4 rounded shimmer" />
    </div>
  );
}
