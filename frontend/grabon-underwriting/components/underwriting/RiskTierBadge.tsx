import { cn } from "@/lib/utils";
import { getTierConfig, decisionToTierKey } from "@/lib/constants/tiers";

interface RiskTierBadgeProps {
  riskTier: string | null;
  decision: string | null;
  size?: "sm" | "lg";
  className?: string;
}

export function RiskTierBadge({ riskTier, decision, size = "lg", className }: RiskTierBadgeProps) {
  const key = decisionToTierKey(decision, riskTier);
  const config = getTierConfig(key);

  return (
    <div
      className={cn(
        "inline-flex flex-col items-center justify-center rounded-2xl border font-display font-800",
        size === "lg" ? "px-7 py-4 gap-0.5" : "px-3 py-1.5",
        className
      )}
      style={{
        color: config.hexColor,
        background: `${config.hexColor}0D`,
        borderColor: `${config.hexColor}35`,
        boxShadow: `0 4px 20px ${config.hexColor}18`,
      }}
    >
      <span className={size === "lg" ? "text-2xl tracking-tight" : "text-sm"}>
        {config.label}
      </span>
      {size === "lg" && (
        <span className="text-[11px] font-sans font-medium opacity-60 tracking-widest uppercase">
          {config.sublabel}
        </span>
      )}
    </div>
  );
}
