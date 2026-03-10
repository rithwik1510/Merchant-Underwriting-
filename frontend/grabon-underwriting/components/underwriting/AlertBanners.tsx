"use client";

import { motion } from "framer-motion";
import { AlertTriangle, Info, OctagonAlert } from "lucide-react";
import { DecisionReason } from "@/lib/types/underwriting";

interface AlertBannerProps {
  reasons: DecisionReason[];
  type: "hard_stop" | "manual_review";
}

export function AlertBanner({ reasons, type }: AlertBannerProps) {
  if (!reasons.length) return null;

  const isHardStop = type === "hard_stop";

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.28 }}
      className={`overflow-hidden rounded-[24px] border ${
        isHardStop ? "border-risk-200 bg-risk-50" : "border-rose-200 bg-rose-50"
      }`}
    >
      <div
        className={`flex items-center gap-2 border-b px-5 py-3 ${
          isHardStop
            ? "border-risk-200 bg-risk-100 text-risk-800"
            : "border-rose-200 bg-rose-100 text-rose-800"
        }`}
      >
        {isHardStop ? <OctagonAlert className="h-4 w-4" /> : <AlertTriangle className="h-4 w-4" />}
        <div className="text-sm font-semibold">
          {isHardStop ? "Hard stop triggered" : "Manual review required"}
        </div>
      </div>

      <div className="space-y-0 divide-y divide-white/70">
        {reasons.map((reason) => (
          <div key={reason.reason_code} className="flex gap-3 px-5 py-4">
            <Info className="mt-0.5 h-4 w-4 shrink-0 text-ink-400" />
            <div className="min-w-0">
              <div className="text-sm font-semibold text-ink-900">{reason.reason_label}</div>
              <div className="mt-1 text-sm text-ink-600">{reason.reason_detail}</div>
              {reason.metric_value !== null ? (
                <div className="mt-2 font-mono text-xs text-ink-500">
                  value {reason.metric_value.toFixed(2)}
                  {reason.benchmark_value !== null ? ` | benchmark ${reason.benchmark_value.toFixed(2)}` : ""}
                </div>
              ) : null}
            </div>
          </div>
        ))}
      </div>
    </motion.div>
  );
}
