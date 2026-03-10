"use client";

import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { ChevronDown, ChevronRight, Minus, TrendingDown, TrendingUp } from "lucide-react";
import { DecisionReason } from "@/lib/types/underwriting";

interface ScorecardPanelProps {
  reasons: DecisionReason[];
  adjustments?: DecisionReason[];
}

function ImpactIcon({ direction }: { direction: string | null }) {
  if (direction === "positive") return <TrendingUp className="h-4 w-4 text-go-600" />;
  if (direction === "negative") return <TrendingDown className="h-4 w-4 text-risk-600" />;
  return <Minus className="h-4 w-4 text-ink-400" />;
}

function ScoreRow({ reason, index }: { reason: DecisionReason; index: number }) {
  const normalized = Math.min(Math.abs(reason.metric_value ?? 0), 100);
  const width = reason.weight ? Math.min((normalized / Math.max(reason.weight * 2, 1)) * 100, 100) : 42;
  const tone =
    reason.impact_direction === "positive"
      ? "bg-go-500"
      : reason.impact_direction === "negative"
      ? "bg-risk-500"
      : "bg-violet-500";

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.24, delay: index * 0.03 }}
      className="rounded-2xl border border-ink-100 bg-surface-50 p-4"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex gap-3">
          <div className="mt-0.5">
            <ImpactIcon direction={reason.impact_direction} />
          </div>
          <div className="min-w-0">
            <div className="text-sm font-semibold text-ink-900">{reason.reason_label}</div>
            <div className="mt-1 text-sm leading-6 text-ink-500">{reason.reason_detail}</div>
          </div>
        </div>
        {reason.weight !== null ? (
          <div className="font-mono text-xs text-ink-500">w:{reason.weight.toFixed(0)}</div>
        ) : null}
      </div>

      <div className="mt-4">
        <div className="mb-2 flex justify-between text-[11px] font-mono text-ink-500">
          <span>{reason.metric_value !== null ? `metric ${reason.metric_value.toFixed(2)}` : "qualitative"}</span>
          <span>
            {reason.benchmark_value !== null ? `benchmark ${reason.benchmark_value.toFixed(2)}` : "no benchmark"}
          </span>
        </div>
        <div className="h-2 rounded-full bg-ink-100">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${width}%` }}
            transition={{ duration: 0.45, delay: index * 0.03 }}
            className={`h-2 rounded-full ${tone}`}
          />
        </div>
      </div>
    </motion.div>
  );
}

function CollapsibleSection({
  title,
  subtitle,
  defaultOpen = true,
  children,
}: {
  title: string;
  subtitle: string;
  defaultOpen?: boolean;
  children: React.ReactNode;
}) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <div className="rounded-[24px] border border-ink-100 bg-white">
      <button
        onClick={() => setOpen((prev) => !prev)}
        className="flex w-full items-center justify-between px-5 py-4 text-left"
      >
        <div>
          <div className="text-sm font-semibold text-ink-900">{title}</div>
          <div className="mt-1 text-sm text-ink-500">{subtitle}</div>
        </div>
        {open ? <ChevronDown className="h-4 w-4 text-ink-400" /> : <ChevronRight className="h-4 w-4 text-ink-400" />}
      </button>

      <AnimatePresence initial={false}>
        {open ? (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden"
          >
            <div className="space-y-3 border-t border-ink-100 px-5 py-5">{children}</div>
          </motion.div>
        ) : null}
      </AnimatePresence>
    </div>
  );
}

export function ScorecardPanel({ reasons, adjustments }: ScorecardPanelProps) {
  if (!reasons.length && !adjustments?.length) return null;

  return (
    <div className="space-y-4">
      {reasons.length ? (
        <CollapsibleSection
          title="Scorecard breakdown"
          subtitle="Weighted factors that produced the final tier and decision."
        >
          {reasons.map((reason, index) => (
            <ScoreRow key={reason.reason_code} reason={reason} index={index} />
          ))}
        </CollapsibleSection>
      ) : null}

      {adjustments && adjustments.length ? (
        <CollapsibleSection
          title="Offer adjustments"
          subtitle="Post-score adjustments that changed pricing, limit, or review posture."
          defaultOpen={false}
        >
          {adjustments.map((reason, index) => (
            <ScoreRow key={reason.reason_code} reason={reason} index={index} />
          ))}
        </CollapsibleSection>
      ) : null}
    </div>
  );
}
