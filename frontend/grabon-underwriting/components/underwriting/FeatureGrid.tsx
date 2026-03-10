"use client";

import { FeatureSnapshot } from "@/lib/types/underwriting";
import { formatCurrency } from "@/lib/utils/formatters";

function formatFeatureValue(key: string, value: unknown) {
  if (value === null || value === undefined) return "-";
  if (typeof value !== "number") return String(value);

  if (key.includes("gmv") && !key.includes("pct") && !key.includes("cv")) {
    return formatCurrency(value);
  }
  if (key.includes("pct")) return `${value.toFixed(2)}%`;
  return value.toFixed(2);
}

const FEATURE_GROUPS: Array<{
  title: string;
  keys: Array<[keyof FeatureSnapshot, string]>;
}> = [
  {
    title: "Volume and growth",
    keys: [
      ["avg_monthly_gmv_3m", "Average GMV (3m)"],
      ["annual_gmv_12m", "Annual GMV"],
      ["gmv_growth_3m_pct", "GMV growth (3m)"],
      ["gmv_growth_12m_pct", "GMV growth (12m)"],
    ],
  },
  {
    title: "Stability and quality",
    keys: [
      ["gmv_volatility_cv", "Volatility CV"],
      ["customer_efficiency_ratio", "Customer efficiency"],
      ["refund_delta_vs_category", "Refund delta vs category"],
      ["return_rate_delta_vs_category", "Return delta vs category"],
    ],
  },
  {
    title: "Risk posture",
    keys: [
      ["aov_position_vs_category_midpoint", "AOV position"],
      ["seasonality_pressure_score", "Seasonality pressure"],
      ["recent_gmv_drop_pct", "Recent GMV drop"],
      ["merchant_health_score", "Merchant health score"],
    ],
  },
];

export function FeatureGrid({ features }: { features: FeatureSnapshot }) {
  return (
    <div className="grid gap-4 xl:grid-cols-3">
      {FEATURE_GROUPS.map((group) => (
        <div key={group.title} className="panel-card p-5">
          <div className="text-sm font-semibold text-ink-900">{group.title}</div>
          <div className="mt-1 text-sm text-ink-500">
            Structured signals persisted from the underwriting feature engine.
          </div>

          <div className="mt-5 space-y-3">
            {group.keys.map(([key, label]) => (
              <div key={String(key)} className="rounded-2xl border border-ink-100 bg-surface-50 p-4">
                <div className="text-xs font-semibold uppercase tracking-[0.16em] text-ink-400">
                  {label}
                </div>
                <div className="mt-2 font-mono text-lg font-semibold text-ink-900">
                  {formatFeatureValue(String(key), features[key])}
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
