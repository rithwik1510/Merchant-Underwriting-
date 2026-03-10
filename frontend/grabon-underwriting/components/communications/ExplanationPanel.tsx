"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { BrainCircuit, Loader2, RefreshCw } from "lucide-react";
import { ExplanationContent } from "@/lib/types/communications";
import { generateExplanation } from "@/lib/api/communications";
import { ApiError } from "@/lib/api/client";
import { formatDate } from "@/lib/utils/formatters";

interface ExplanationPanelProps {
  runId: number;
  initial?: ExplanationContent | null;
}

function useTextReveal(text: string, speed = 8) {
  const [revealed, setRevealed] = useState("");

  useEffect(() => {
    if (!text) return;
    setRevealed("");
    let index = 0;
    const id = setInterval(() => {
      index += speed;
      setRevealed(text.slice(0, index));
      if (index >= text.length) {
        setRevealed(text);
        clearInterval(id);
      }
    }, 16);
    return () => clearInterval(id);
  }, [text, speed]);

  return revealed;
}

function extractText(content: ExplanationContent) {
  const payload = content.output_payload_json;
  if (typeof payload === "string") return payload;
  if (payload?.summary) return String(payload.summary);
  if (payload?.explanation) return String(payload.explanation);
  if (payload?.text) return String(payload.text);
  return JSON.stringify(payload, null, 2);
}

export function ExplanationPanel({ runId, initial }: ExplanationPanelProps) {
  const [content, setContent] = useState<ExplanationContent | null>(initial ?? null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fullText = content ? extractText(content) : "";
  const revealed = useTextReveal(fullText);

  async function generate() {
    setLoading(true);
    setError(null);
    try {
      const result = await generateExplanation(runId);
      setContent(result);
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Explanation generation failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="panel-card overflow-hidden">
      <div className="flex items-center justify-between border-b border-ink-100 px-5 py-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-2xl border border-go-200 bg-go-50">
            <BrainCircuit className="h-4 w-4 text-go-600" />
          </div>
          <div>
            <div className="text-sm font-semibold text-ink-900">AI explanation</div>
            <div className="text-sm text-ink-500">
              {content ? `${content.provider_name} | ${content.model_name}` : "Generate a grounded decision narrative"}
            </div>
          </div>
        </div>

        <button onClick={generate} disabled={loading} className="btn-outline">
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
          {content ? "Regenerate" : "Generate"}
        </button>
      </div>

      <div className="space-y-4 p-5">
        {content ? (
          <div className="flex flex-wrap gap-2">
            <span className="status-pill border-go-200 bg-go-100 text-go-700">
              {content.status.replace(/_/g, " ")}
            </span>
            <span className="status-pill border-ink-200 bg-surface-100 text-ink-500">
              {formatDate(content.created_at)}
            </span>
          </div>
        ) : null}

        {loading ? (
          <div className="rounded-2xl border border-go-200 bg-go-50 px-4 py-4 text-sm text-go-700">
            <div className="flex items-center gap-2">
              <Loader2 className="h-4 w-4 animate-spin" />
              Generating explanation from persisted underwriting facts...
            </div>
          </div>
        ) : null}

        {error ? (
          <div className="rounded-2xl border border-risk-200 bg-risk-50 px-4 py-4 text-sm text-risk-700">
            {error}
          </div>
        ) : null}

        {!loading && !error && !content ? (
          <div className="rounded-2xl border border-ink-100 bg-surface-50 px-4 py-5 text-sm text-ink-500">
            Use the model layer to narrate the decision using only approved scorecard facts and stored benchmark comparisons.
          </div>
        ) : null}

        {!loading && content ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="rounded-[24px] border border-ink-100 bg-white p-5 text-sm leading-7 text-ink-700"
          >
            {revealed}
            {revealed.length < fullText.length ? (
              <span className="ml-0.5 inline-block h-4 w-0.5 animate-pulse bg-go-500" />
            ) : null}
          </motion.div>
        ) : null}
      </div>
    </div>
  );
}
