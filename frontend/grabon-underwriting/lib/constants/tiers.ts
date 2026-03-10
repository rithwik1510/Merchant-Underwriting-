export const TIER_CONFIG = {
  tier_1: {
    label: "Tier 1",
    sublabel: "Prime Approved",
    hexColor: "#2563EB",
    badgeBg: "rgba(37,99,235,0.10)",
    badgeBorder: "rgba(37,99,235,0.18)",
  },
  tier_2: {
    label: "Tier 2",
    sublabel: "Standard Approved",
    hexColor: "#1D4ED8",
    badgeBg: "rgba(29,78,216,0.10)",
    badgeBorder: "rgba(29,78,216,0.18)",
  },
  tier_3: {
    label: "Tier 3",
    sublabel: "Conditional Review",
    hexColor: "#7C3AED",
    badgeBg: "rgba(124,58,237,0.10)",
    badgeBorder: "rgba(124,58,237,0.18)",
  },
  rejected: {
    label: "Rejected",
    sublabel: "Not Eligible",
    hexColor: "#DC2626",
    badgeBg: "rgba(220,38,38,0.08)",
    badgeBorder: "rgba(220,38,38,0.18)",
  },
  manual_review: {
    label: "Manual Review",
    sublabel: "Ops Confirmation",
    hexColor: "#BE123C",
    badgeBg: "rgba(190,18,60,0.08)",
    badgeBorder: "rgba(190,18,60,0.18)",
  },
} as const;

export type TierKey = keyof typeof TIER_CONFIG;

export function getTierConfig(tier: string | null) {
  if (!tier) return TIER_CONFIG.manual_review;
  return TIER_CONFIG[tier as TierKey] ?? TIER_CONFIG.manual_review;
}

export function decisionToTierKey(
  decision: string | null,
  riskTier: string | null
): TierKey {
  if (riskTier && riskTier in TIER_CONFIG) return riskTier as TierKey;
  if (decision === "rejected") return "rejected";
  if (decision === "manual_review") return "manual_review";
  return "manual_review";
}
