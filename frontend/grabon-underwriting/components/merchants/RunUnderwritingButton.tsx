"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { AnimatePresence, motion } from "framer-motion";
import { AlertCircle, ArrowRight, CheckCircle2, Loader2, Radar } from "lucide-react";
import { runUnderwriting } from "@/lib/api/underwriting";
import { ApiError } from "@/lib/api/client";

const STAGES = [
  "Collecting merchant signals...",
  "Computing benchmark deltas...",
  "Scoring policy fit...",
  "Structuring offer outputs...",
];

export function RunUnderwritingButton({
  merchantId,
  compact = false,
}: {
  merchantId: string;
  compact?: boolean;
}) {
  const router = useRouter();
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
  const [stageIdx, setStageIdx] = useState(0);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (status !== "loading") return;
    const id = setInterval(() => setStageIdx((prev) => (prev + 1) % STAGES.length), 700);
    return () => clearInterval(id);
  }, [status]);

  async function handleClick() {
    if (status === "loading") return;
    setStatus("loading");
    setStageIdx(0);
    setError(null);
    try {
      const run = await runUnderwriting(merchantId);
      setStatus("success");
      setTimeout(() => router.push(`/runs/${run.run_id}`), 420);
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Failed to run underwriting");
      setStatus("error");
    }
  }

  const canAnimate = status === "idle" || status === "error";

  return (
    <div className="space-y-2">
      <motion.button
        onClick={handleClick}
        disabled={status === "loading" || status === "success"}
        whileHover={canAnimate ? { scale: 1.01, y: -1 } : undefined}
        whileTap={canAnimate ? { scale: 0.995 } : undefined}
        className={
          compact
            ? "relative min-w-[220px] overflow-hidden rounded-2xl border border-go-300 bg-[linear-gradient(135deg,#0f4ae6,#1d63ff)] px-5 py-3 text-left text-white shadow-glow transition-all duration-200 disabled:cursor-not-allowed disabled:opacity-95"
            : "relative w-full overflow-hidden rounded-[22px] border border-go-300 bg-[linear-gradient(135deg,#0f4ae6,#1d63ff)] px-6 py-4 text-left text-white shadow-glow transition-all duration-200 disabled:cursor-not-allowed disabled:opacity-95"
        }
      >
        <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(255,255,255,0.26),transparent_38%)]" />
        <div className="pointer-events-none absolute inset-0 bg-[linear-gradient(180deg,transparent,rgba(2,6,23,0.08))]" />

        <AnimatePresence mode="wait">
          {status === "idle" ? (
            <motion.div
              key="idle"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="relative flex items-center justify-between gap-4"
            >
              <div className="flex items-center gap-3">
                <div
                  className={
                    compact
                      ? "flex h-9 w-9 items-center justify-center rounded-xl border border-white/20 bg-white/10"
                      : "flex h-11 w-11 items-center justify-center rounded-2xl border border-white/20 bg-white/10"
                  }
                >
                  <Radar className="h-4 w-4" />
                </div>
                <div>
                  <div className="text-sm font-semibold">Run underwriting engine</div>
                  {!compact ? (
                    <div className="mt-1 text-xs text-white/78">
                      Produce decision tier, score, reasons, and offer outputs
                    </div>
                  ) : null}
                </div>
              </div>
              <ArrowRight className="h-4 w-4 shrink-0" />
            </motion.div>
          ) : null}

          {status === "loading" ? (
            <motion.div
              key="loading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="relative flex items-center gap-3"
            >
              <Loader2 className="h-4 w-4 animate-spin" />
              <AnimatePresence mode="wait">
                <motion.span
                  key={stageIdx}
                  initial={{ opacity: 0, y: 5 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -5 }}
                  transition={{ duration: 0.18 }}
                  className="text-sm font-medium"
                >
                  {STAGES[stageIdx]}
                </motion.span>
              </AnimatePresence>
            </motion.div>
          ) : null}

          {status === "success" ? (
            <motion.div
              key="success"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="relative flex items-center gap-2"
            >
              <CheckCircle2 className="h-4 w-4" />
              Decision complete - opening results
            </motion.div>
          ) : null}

          {status === "error" ? (
            <motion.div
              key="error"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="relative flex items-center gap-2"
            >
              <AlertCircle className="h-4 w-4" />
              Retry underwriting
            </motion.div>
          ) : null}
        </AnimatePresence>
      </motion.button>

      {error ? (
        <p className={compact ? "text-left text-xs text-risk-600" : "text-center text-xs text-risk-600"}>
          {error}
        </p>
      ) : null}
    </div>
  );
}
