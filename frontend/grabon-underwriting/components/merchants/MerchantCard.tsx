"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowUpRight, AlertCircle, Users } from "lucide-react";
import { MerchantSummary } from "@/lib/types/merchant";
import { getCategoryConfig } from "@/lib/constants/categories";
import { OutcomeBadge } from "./OutcomeBadge";
import { formatCurrency, formatNumber, formatPercentRaw } from "@/lib/utils/formatters";
import { CategoryGlyph } from "@/components/ui/CategoryGlyph";

interface MerchantCardProps {
  merchant: MerchantSummary;
  index: number;
}

export function MerchantCard({ merchant, index }: MerchantCardProps) {
  const cat = getCategoryConfig(merchant.category);
  const snapshotTone =
    merchant.latest_decision === "rejected" || merchant.seed_intended_outcome === "rejected"
      ? "text-risk-700"
      : merchant.latest_decision === "manual_review" || merchant.seed_intended_outcome === "manual_review"
        ? "text-violet-700"
        : "text-ink-800";
  const latestStatus =
    merchant.latest_decision && merchant.latest_risk_tier
      ? `${merchant.latest_decision.replace(/_/g, " ")} | ${merchant.latest_risk_tier.replace(/_/g, " ")}`
      : "Not underwritten yet";

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, delay: index * 0.05, ease: [0.22, 1, 0.36, 1] }}
      whileHover={{ y: -4, transition: { duration: 0.18, ease: "easeOut" } }}
    >
      <Link href={`/merchants/${merchant.merchant_id}`} className="group block">
        <div
          className="rounded-3xl border border-ink-100 bg-white p-5 shadow-card transition-all duration-200 group-hover:border-ink-200 group-hover:shadow-card-hover"
        >
          <div className="mb-4 flex items-start gap-3">
            <div
              className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl border"
              style={{ background: cat.bg, borderColor: cat.border, color: cat.color }}
            >
              <CategoryGlyph glyph={cat.glyph} className="h-4.5 w-4.5" stroke={cat.color} />
            </div>
            <div className="min-w-0 flex-1">
              <div className="text-xs font-medium text-ink-400">{cat.label}</div>
              <h3 className="truncate text-base font-bold leading-tight text-ink-900">
                {merchant.merchant_name}
              </h3>
            </div>
            <div className="flex-shrink-0">
              <OutcomeBadge outcome={merchant.seed_intended_outcome} />
            </div>
          </div>

          <div className="flex items-center gap-3 rounded-2xl border border-ink-100 bg-surface-50 px-3.5 py-3">
            <div className="flex min-w-0 flex-1 items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-white text-go-600 ring-1 ring-ink-100">
                <Users className="h-3.5 w-3.5" />
              </div>
              <div className="min-w-0">
                <div className="text-[11px] font-medium text-ink-400">Customers</div>
                <div className="font-mono text-sm font-semibold text-ink-800">
                  {formatNumber(merchant.unique_customer_count)}
                </div>
              </div>
            </div>
            <div className="h-8 w-px bg-ink-100" />
            <div className="flex min-w-0 flex-1 items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-white text-risk-600 ring-1 ring-ink-100">
                <AlertCircle className="h-3.5 w-3.5" />
              </div>
              <div className="min-w-0">
                <div className="text-[11px] font-medium text-ink-400">Refund</div>
                <div className="font-mono text-sm font-semibold text-ink-800">
                  {formatPercentRaw(merchant.return_and_refund_rate)}
                </div>
              </div>
            </div>
          </div>

          <div className="mt-3 rounded-2xl border border-ink-100 bg-white px-3.5 py-3">
            <div className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink-400">Latest snapshot</div>
            <div className={`mt-1 text-sm font-semibold ${snapshotTone}`}>{latestStatus}</div>
            {merchant.latest_run_id ? (
              <div className="mt-2 grid grid-cols-2 gap-2 text-xs text-ink-500">
                <span>Credit {formatCurrency(merchant.latest_credit_limit)}</span>
                <span>Cover {formatCurrency(merchant.latest_insurance_coverage)}</span>
              </div>
            ) : (
              <div className="mt-1 text-xs text-ink-500">Run underwriting to generate offers.</div>
            )}
          </div>

          <div className="mt-3 flex items-center justify-between">
            <span className="text-xs font-medium text-ink-500">Open merchant profile</span>
            <div className="flex h-7 w-7 items-center justify-center rounded-full border border-ink-100 bg-white text-ink-400 transition-all duration-200 group-hover:border-go-200 group-hover:bg-go-50 group-hover:text-go-600">
              <ArrowUpRight className="h-3.5 w-3.5" />
            </div>
          </div>
        </div>
      </Link>
    </motion.div>
  );
}
