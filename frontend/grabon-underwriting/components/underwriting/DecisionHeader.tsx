"use client";

import { motion } from "framer-motion";
import { Calendar, Hash, Layers } from "lucide-react";
import { UnderwritingRun } from "@/lib/types/underwriting";
import { RiskTierBadge } from "./RiskTierBadge";
import { ScoreGauge } from "./ScoreGauge";
import { CategoryGlyph } from "@/components/ui/CategoryGlyph";
import { getCategoryConfig } from "@/lib/constants/categories";
import { formatDate } from "@/lib/utils/formatters";

export function DecisionHeader({ run }: { run: UnderwritingRun }) {
  const category = getCategoryConfig(run.merchant.category);

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
      className="hero-surface p-6 md:p-7"
    >
      <div className="flex flex-col gap-5 xl:flex-row xl:items-center">
        <div className="rounded-[28px] border border-go-200 bg-white p-4 shadow-card">
          <ScoreGauge score={run.numeric_score} size={190} />
        </div>

        <div className="min-w-0 flex-1">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div className="min-w-0">
              <div className="mb-3 flex items-center gap-3">
                <div
                  className="flex h-12 w-12 items-center justify-center rounded-2xl border"
                  style={{ background: category.bg, borderColor: category.border }}
                >
                  <CategoryGlyph glyph={category.glyph} stroke={category.color} />
                </div>
                <div>
                  <div className="text-xs font-semibold uppercase tracking-[0.18em] text-go-700">
                    Deterministic decision packet
                  </div>
                  <h2 className="text-3xl font-bold tracking-tight text-ink-900">
                    {run.merchant.merchant_name}
                  </h2>
                </div>
              </div>

              <div className="mt-3 flex flex-wrap gap-2">
                <span className="status-pill border-ink-200 bg-white text-ink-500">
                  {category.label}
                </span>
                <span className="status-pill border-go-200 bg-go-100 text-go-700">
                  {run.status.replace(/_/g, " ")}
                </span>
                <span className="status-pill border-ink-200 bg-white text-ink-500">
                  {run.usable_history_months}m usable history
                </span>
              </div>
            </div>

            <RiskTierBadge riskTier={run.risk_tier} decision={run.decision} size="lg" />
          </div>

          <div className="mt-5 grid gap-3 md:grid-cols-3">
            {[
              { icon: Hash, label: "Run ID", value: `#${run.run_id}` },
              { icon: Layers, label: "Policy version", value: run.policy_version },
              { icon: Calendar, label: "Generated", value: formatDate(run.created_at) },
            ].map((item) => {
              const Icon = item.icon;
              return (
                <div key={item.label} className="rounded-2xl border border-ink-100 bg-white p-4">
                  <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-ink-400">
                    <Icon className="h-3.5 w-3.5" />
                    {item.label}
                  </div>
                  <div className="mt-2 font-mono text-sm font-semibold text-ink-800">
                    {item.value}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </motion.div>
  );
}
