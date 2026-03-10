"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ArrowRight, CheckCircle2, MessageSquareText, ShieldCheck, WalletCards } from "lucide-react";
import { getCommunications } from "@/lib/api/communications";
import { getAcceptance } from "@/lib/api/offers";
import { getMandateStatus } from "@/lib/api/mandates";
import { formatRelativeTime } from "@/lib/utils/formatters";

interface StatusSummaryBarProps {
  runId: number;
}

interface StatusState {
  loaded: boolean;
  explanation: { done: boolean; at?: string } | null;
  acceptance: { done: boolean; product?: string; at?: string } | null;
  mandate: { done: boolean; status?: string; umrn?: string } | null;
}

function StatusCard({
  title,
  detail,
  href,
  done,
  icon: Icon,
}: {
  title: string;
  detail: string;
  href: string;
  done: boolean;
  icon: React.ComponentType<{ className?: string }>;
}) {
  return (
    <Link
      href={href}
      className="panel-card group flex items-center justify-between gap-3 p-4 transition-all hover:-translate-y-0.5"
    >
      <div className="flex items-center gap-3">
        <div
          className={`flex h-10 w-10 items-center justify-center rounded-2xl border ${
            done ? "border-go-200 bg-go-50 text-go-600" : "border-ink-200 bg-surface-100 text-ink-500"
          }`}
        >
          {done ? <CheckCircle2 className="h-4 w-4" /> : <Icon className="h-4 w-4" />}
        </div>
        <div>
          <div className="text-sm font-semibold text-ink-900">{title}</div>
          <div className="text-sm text-ink-500">{detail}</div>
        </div>
      </div>
      <ArrowRight className="h-4 w-4 text-ink-300 transition-colors group-hover:text-go-600" />
    </Link>
  );
}

export function StatusSummaryBar({ runId }: StatusSummaryBarProps) {
  const [state, setState] = useState<StatusState>({
    loaded: false,
    explanation: null,
    acceptance: null,
    mandate: null,
  });

  useEffect(() => {
    let cancelled = false;

    async function load() {
      const [communications, acceptance, mandate] = await Promise.allSettled([
        getCommunications(runId),
        getAcceptance(runId),
        getMandateStatus(runId),
      ]);

      if (cancelled) return;

      setState({
        loaded: true,
        explanation:
          communications.status === "fulfilled"
            ? {
                done: !!communications.value.latest_explanation,
                at: communications.value.latest_explanation?.created_at,
              }
            : { done: false },
        acceptance:
          acceptance.status === "fulfilled"
            ? {
                done: true,
                product: acceptance.value.accepted_product_type,
                at: acceptance.value.accepted_at,
              }
            : { done: false },
        mandate:
          mandate.status === "fulfilled"
            ? {
                done:
                  mandate.value.mandate_status === "completed" ||
                  mandate.value.mandate_status === "umrn_generated",
                status: mandate.value.mandate_status,
                umrn: mandate.value.umrn ?? undefined,
              }
            : { done: false },
      });
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [runId]);

  if (!state.loaded) return null;

  return (
    <div className="grid gap-4 lg:grid-cols-3">
      <StatusCard
        title="Explanation and comms"
        detail={
          state.explanation?.done && state.explanation.at
            ? `Generated ${formatRelativeTime(state.explanation.at)}`
            : "No generated explanation yet"
        }
        href={`/runs/${runId}/communicate`}
        done={state.explanation?.done ?? false}
        icon={MessageSquareText}
      />
      <StatusCard
        title="Offer acceptance"
        detail={
          state.acceptance?.done
            ? `${state.acceptance.product?.replace(/_/g, " ")} accepted`
            : "Offer not accepted yet"
        }
        href={`/runs/${runId}/accept`}
        done={state.acceptance?.done ?? false}
        icon={WalletCards}
      />
      <StatusCard
        title="NACH mandate"
        detail={
          state.mandate?.umrn
            ? `UMRN ${state.mandate.umrn.slice(0, 12)}...`
            : state.mandate?.status
            ? state.mandate.status.replace(/_/g, " ")
            : "Mandate not started"
        }
        href={`/runs/${runId}/mandate`}
        done={state.mandate?.done ?? false}
        icon={ShieldCheck}
      />
    </div>
  );
}
