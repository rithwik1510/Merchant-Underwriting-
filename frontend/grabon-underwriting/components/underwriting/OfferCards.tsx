"use client";

import { motion } from "framer-motion";
import { CheckCircle2, CircleOff, Clock3, CreditCard, Shield } from "lucide-react";
import { CreditOffer, InsuranceOffer } from "@/lib/types/underwriting";
import { AnimatedNumber } from "@/components/ui/AnimatedNumber";
import { formatCurrency } from "@/lib/utils/formatters";

function StatusIcon({ status }: { status: string }) {
  if (status === "eligible") return <CheckCircle2 className="h-4 w-4 text-go-600" />;
  if (status === "manual_review") return <Clock3 className="h-4 w-4 text-violet-600" />;
  return <CircleOff className="h-4 w-4 text-risk-600" />;
}

export function CreditOfferCard({ offer }: { offer: CreditOffer | null }) {
  const eligible = offer?.offer_status === "eligible";
  const review = offer?.offer_status === "manual_review";

  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="panel-card p-5">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl border border-go-200 bg-go-50">
            <CreditCard className="h-5 w-5 text-go-600" />
          </div>
          <div>
            <div className="text-sm font-semibold text-ink-900">GrabCredit</div>
            <div className="text-sm text-ink-500">Working capital line</div>
          </div>
        </div>
        {offer ? <StatusIcon status={offer.offer_status} /> : null}
      </div>

      {eligible && offer?.final_limit ? (
        <div className="mt-6">
          <div className="text-xs font-semibold uppercase tracking-[0.18em] text-ink-400">
            Final limit
          </div>
          <div className="mt-2 font-mono text-3xl font-bold tracking-tight text-ink-900">
            <AnimatedNumber value={offer.final_limit} formatter={formatCurrency} duration={900} />
          </div>
          {offer.base_limit && offer.base_limit !== offer.final_limit ? (
            <div className="mt-1 font-mono text-sm text-ink-400 line-through">
              {formatCurrency(offer.base_limit)}
            </div>
          ) : null}

          <div className="mt-5 grid gap-4 md:grid-cols-2">
            <div className="rounded-2xl border border-ink-100 bg-surface-50 p-4">
              <div className="text-xs font-semibold uppercase tracking-[0.18em] text-ink-400">
                Rate band
              </div>
              <div className="mt-2 font-mono text-lg font-semibold text-go-700">
                {offer.interest_rate_min}% - {offer.interest_rate_max}%
              </div>
            </div>
            <div className="rounded-2xl border border-ink-100 bg-surface-50 p-4">
              <div className="text-xs font-semibold uppercase tracking-[0.18em] text-ink-400">
                Tenure options
              </div>
              <div className="mt-2 flex flex-wrap gap-2">
                {offer.tenure_options.map((term) => (
                  <span
                    key={term}
                    className="status-pill border-go-200 bg-go-100 font-mono text-go-700"
                  >
                    {term}mo
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="mt-6 rounded-2xl border border-ink-100 bg-surface-50 p-4 text-sm text-ink-500">
          {review
            ? "Credit is available subject to final ops review and pricing confirmation."
            : "Credit is not available for this run."}
        </div>
      )}
    </motion.div>
  );
}

export function InsuranceOfferCard({ offer }: { offer: InsuranceOffer | null }) {
  const eligible = offer?.offer_status === "eligible";
  const review = offer?.offer_status === "manual_review";

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.05 }}
      className="panel-card p-5"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl border border-risk-200 bg-risk-50">
            <Shield className="h-5 w-5 text-risk-600" />
          </div>
          <div>
            <div className="text-sm font-semibold text-ink-900">GrabInsurance</div>
            <div className="text-sm text-ink-500">Revenue protection cover</div>
          </div>
        </div>
        {offer ? <StatusIcon status={offer.offer_status} /> : null}
      </div>

      {eligible && offer?.coverage_amount ? (
        <div className="mt-6">
          <div className="text-xs font-semibold uppercase tracking-[0.18em] text-ink-400">
            Coverage amount
          </div>
          <div className="mt-2 font-mono text-3xl font-bold tracking-tight text-ink-900">
            <AnimatedNumber value={offer.coverage_amount} formatter={formatCurrency} duration={950} />
          </div>

          <div className="mt-5 grid gap-4 md:grid-cols-2">
            <div className="rounded-2xl border border-ink-100 bg-surface-50 p-4">
              <div className="text-xs font-semibold uppercase tracking-[0.18em] text-ink-400">
                Premium
              </div>
              <div className="mt-2 font-mono text-lg font-semibold text-risk-700">
                {offer.premium_amount ? `${formatCurrency(offer.premium_amount)}/mo` : "-"}
              </div>
            </div>
            <div className="rounded-2xl border border-ink-100 bg-surface-50 p-4">
              <div className="text-xs font-semibold uppercase tracking-[0.18em] text-ink-400">
                Policy structure
              </div>
              <div className="mt-2 text-sm font-semibold text-ink-900">
                {offer.policy_type?.replace(/_/g, " ") ?? "Not defined"}
              </div>
              <div className="mt-1 text-sm text-ink-500">
                Rate {offer.premium_rate != null ? `${(offer.premium_rate * 100).toFixed(2)}%` : "-"}
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="mt-6 rounded-2xl border border-ink-100 bg-surface-50 p-4 text-sm text-ink-500">
          {review
            ? "Insurance can proceed only after review confirms premium and coverage posture."
            : "Insurance is not available for this run."}
        </div>
      )}
    </motion.div>
  );
}
