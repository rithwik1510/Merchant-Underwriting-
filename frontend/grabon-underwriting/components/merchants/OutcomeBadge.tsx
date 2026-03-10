import { cn } from "@/lib/utils";

const OUTCOME_MAP: Record<
  string,
  { label: string; color: string; bg: string; border: string }
> = {
  tier_1: {
    label: "Tier 1",
    color: "#2563EB",
    bg: "rgba(37,99,235,0.10)",
    border: "rgba(37,99,235,0.18)",
  },
  tier_2: {
    label: "Tier 2",
    color: "#1D4ED8",
    bg: "rgba(29,78,216,0.10)",
    border: "rgba(29,78,216,0.18)",
  },
  tier_3: {
    label: "Tier 3",
    color: "#7C3AED",
    bg: "rgba(124,58,237,0.10)",
    border: "rgba(124,58,237,0.18)",
  },
  rejected: {
    label: "Rejected",
    color: "#DC2626",
    bg: "rgba(220,38,38,0.08)",
    border: "rgba(220,38,38,0.18)",
  },
  manual_review: {
    label: "Manual Review",
    color: "#BE123C",
    bg: "rgba(190,18,60,0.08)",
    border: "rgba(190,18,60,0.18)",
  },
  manual_review_volatility: {
    label: "Manual Review",
    color: "#BE123C",
    bg: "rgba(190,18,60,0.08)",
    border: "rgba(190,18,60,0.18)",
  },
  tier_3_manual_review: {
    label: "Tier 3 Review",
    color: "#7C3AED",
    bg: "rgba(124,58,237,0.10)",
    border: "rgba(124,58,237,0.18)",
  },
  rejected_refund_rate: {
    label: "Rejected",
    color: "#DC2626",
    bg: "rgba(220,38,38,0.08)",
    border: "rgba(220,38,38,0.18)",
  },
  rejected_insufficient_history: {
    label: "Rejected",
    color: "#DC2626",
    bg: "rgba(220,38,38,0.08)",
    border: "rgba(220,38,38,0.18)",
  },
  reduced_credit_high_premium: {
    label: "Reduced Terms",
    color: "#1D4ED8",
    bg: "rgba(29,78,216,0.08)",
    border: "rgba(29,78,216,0.18)",
  },
};

interface OutcomeBadgeProps {
  outcome: string;
  className?: string;
  size?: "sm" | "md";
}

export function OutcomeBadge({
  outcome,
  className,
  size = "sm",
}: OutcomeBadgeProps) {
  const c = OUTCOME_MAP[outcome] ?? {
    label: outcome.replace(/_/g, " "),
    color: "#475569",
    bg: "rgba(71,85,105,0.08)",
    border: "rgba(71,85,105,0.16)",
  };

  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border font-semibold uppercase tracking-[0.12em]",
        size === "sm" ? "px-2.5 py-1 text-[10px]" : "px-3 py-1.5 text-[11px]",
        className
      )}
      style={{ color: c.color, backgroundColor: c.bg, borderColor: c.border }}
    >
      {c.label}
    </span>
  );
}
