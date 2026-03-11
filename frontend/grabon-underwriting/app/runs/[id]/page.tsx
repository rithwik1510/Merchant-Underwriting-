import { notFound } from "next/navigation";
import Link from "next/link";
import type { ComponentType } from "react";
import { ArrowLeft, ChevronDown, Landmark, MessageSquareText, ShieldCheck, Sparkles } from "lucide-react";
import { getUnderwritingRun } from "@/lib/api/underwriting";
import { getCommunications } from "@/lib/api/communications";
import { getAcceptance } from "@/lib/api/offers";
import { DecisionHeader } from "@/components/underwriting/DecisionHeader";
import { AlertBanner } from "@/components/underwriting/AlertBanners";
import { CreditOfferCard, InsuranceOfferCard } from "@/components/underwriting/OfferCards";
import { FeatureGrid } from "@/components/underwriting/FeatureGrid";
import { CommunicationWorkspace } from "@/components/communications/CommunicationWorkspace";
import { AcceptanceForm } from "@/components/acceptance/AcceptanceForm";
import { MandateWizard } from "@/components/mandate/MandateWizard";
import { PanelCard } from "@/components/ui/PanelCard";
import { ApiError } from "@/lib/api/client";

export const dynamic = "force-dynamic";

interface Params {
  params: { id: string };
}

export default async function RunDetailPage({ params }: Params) {
  let run;
  try {
    run = await getUnderwritingRun(params.id);
  } catch {
    notFound();
  }

  let comms = null;
  try {
    comms = await getCommunications(run.run_id);
  } catch (err) {
    if (!(err instanceof ApiError) || err.status !== 404) {
      comms = null;
    }
  }

  let acceptance = null;
  try {
    acceptance = await getAcceptance(run.run_id);
  } catch (err) {
    if (!(err instanceof ApiError) || err.status !== 404) {
      acceptance = null;
    }
  }

  const headlineReasons = run.score_reasons.slice(0, 4);
  const totalReasons = run.score_reasons.length;
  const canStartMandate = acceptance?.mandate_can_start ?? false;

  return (
    <div className="space-y-6 px-6 py-6">
      <Link
        href="/runs"
        className="inline-flex items-center gap-1.5 text-sm text-ink-400 transition-colors hover:text-go-600"
      >
        <ArrowLeft className="h-4 w-4" />
        Run history
      </Link>

      <DecisionHeader run={run} />

      {(run.hard_stop_triggered && run.hard_stop_reasons.length) || (run.manual_review_triggered && run.manual_review_reasons.length) ? (
        <div className="space-y-3">
          {run.hard_stop_triggered && run.hard_stop_reasons.length ? (
            <AlertBanner reasons={run.hard_stop_reasons} type="hard_stop" />
          ) : null}
          {run.manual_review_triggered && run.manual_review_reasons.length ? (
            <AlertBanner reasons={run.manual_review_reasons} type="manual_review" />
          ) : null}
        </div>
      ) : null}

      <section className="space-y-3">
        <SectionLabel
          icon={MessageSquareText}
          title="Communicate"
          subtitle="Summary, draft, send."
          tone="go"
        />
        <CommunicationWorkspace
          runId={run.run_id}
          sanityCheck={run.ai_sanity_check}
          initialExplanation={comms?.latest_explanation ?? null}
          initialDraft={comms?.latest_whatsapp_draft ?? null}
          initialMessages={comms?.whatsapp_messages ?? []}
        />
      </section>

      <section className="space-y-3">
        <SectionLabel
          icon={Sparkles}
          title="Decision"
          subtitle="Top signals and full detail."
          tone="risk"
        />
        <PanelCard className="p-4 md:p-5">
          <div className="space-y-4">
            <div className="grid gap-3 md:grid-cols-2">
              {headlineReasons.map((reason) => (
                <div
                  key={reason.reason_code}
                  className="rounded-2xl border border-ink-100 bg-surface-50 px-4 py-3"
                >
                  <div className="flex items-center justify-between gap-3">
                    <div className="min-w-0 text-sm font-semibold text-ink-900">{reason.reason_label}</div>
                    {reason.weight ? (
                      <span className="status-pill shrink-0 border-ink-200 bg-white font-mono text-ink-500">
                        {reason.weight} pts
                      </span>
                    ) : null}
                  </div>
                  <p className="mt-1 truncate text-sm text-ink-500">{reason.reason_detail}</p>
                </div>
              ))}
            </div>

            <details className="group overflow-hidden rounded-[22px] border border-ink-100 bg-white">
              <summary className="flex cursor-pointer list-none items-center justify-between gap-3 px-4 py-3">
                <div>
                  <div className="text-sm font-semibold text-ink-900">Full detail</div>
                  <div className="mt-1 text-sm text-ink-500">
                    {totalReasons} reasons, offers, features.
                  </div>
                </div>
                <ChevronDown className="h-4 w-4 text-ink-400 transition-transform group-open:rotate-180" />
              </summary>
              <div className="space-y-4 border-t border-ink-100 px-4 py-4">
                <div className="space-y-2">
                  {run.score_reasons.map((reason) => (
                    <div key={reason.reason_code} className="rounded-2xl border border-ink-100 bg-surface-50 px-4 py-3">
                      <div className="flex items-start justify-between gap-3">
                        <div className="min-w-0">
                          <div className="text-sm font-semibold text-ink-900">{reason.reason_label}</div>
                          <div className="mt-1 text-sm text-ink-500">{reason.reason_detail}</div>
                        </div>
                        {reason.weight ? (
                          <span className="status-pill shrink-0 border-ink-200 bg-white font-mono text-ink-500">
                            {reason.weight} pts
                          </span>
                        ) : null}
                      </div>
                    </div>
                  ))}
                </div>

                <div className="grid gap-4 xl:grid-cols-2">
                  <div className="rounded-[22px] border border-ink-100 bg-surface-50 p-4">
                    <div className="mb-3 text-sm font-semibold text-ink-900">Offers</div>
                    <div className="space-y-4">
                      <CreditOfferCard offer={run.credit_offer} />
                      <InsuranceOfferCard offer={run.insurance_offer} />
                    </div>
                  </div>

                  <div className="space-y-4">
                    <PanelCard className="p-4">
                      <div className="mb-3 text-sm font-semibold text-ink-900">Adjustments</div>
                      <div className="space-y-3">
                        {run.offer_adjustments.length ? (
                          run.offer_adjustments.map((reason) => (
                            <div key={reason.reason_code} className="rounded-2xl border border-ink-100 bg-surface-50 p-4 text-sm text-ink-600">
                              <div className="font-semibold text-ink-900">{reason.reason_label}</div>
                              <div className="mt-1">{reason.reason_detail}</div>
                            </div>
                          ))
                        ) : (
                          <div className="rounded-2xl border border-ink-100 bg-surface-50 p-4 text-sm text-ink-500">
                            No additional adjustments.
                          </div>
                        )}
                      </div>
                    </PanelCard>

                    <PanelCard className="p-4">
                      <div className="mb-3 text-sm font-semibold text-ink-900">Features</div>
                      <FeatureGrid features={run.features} />
                    </PanelCard>
                  </div>
                </div>
              </div>
            </details>
          </div>
        </PanelCard>
      </section>

      <section className="space-y-3">
        <SectionLabel
          icon={ShieldCheck}
          title="Accept offer"
          subtitle="Record acceptance."
          tone="go"
        />
        <PanelCard className="p-5">
          <AcceptanceForm run={run} existing={acceptance} inline />
        </PanelCard>
      </section>

      <section id="mandate-section" className="space-y-3">
        <SectionLabel
          icon={Landmark}
          title="Mandate"
          subtitle="Unlocks after acceptance."
          tone="risk"
        />
        {!acceptance ? (
          <PanelCard className="p-5 text-sm text-ink-500">
            Record acceptance first. The mandate section unlocks automatically after that.
          </PanelCard>
        ) : !canStartMandate ? (
          <PanelCard className="p-5 text-sm text-risk-700">
            The current acceptance record does not allow a mandate to start yet.
          </PanelCard>
        ) : (
          <PanelCard className="p-5">
            <MandateWizard runId={run.run_id} />
          </PanelCard>
        )}
      </section>
    </div>
  );
}

function SectionLabel({
  icon: Icon,
  title,
  subtitle,
  tone = "go",
}: {
  icon: ComponentType<{ className?: string }>;
  title: string;
  subtitle: string;
  tone?: "go" | "risk";
}) {
  return (
    <div className="flex items-start gap-3">
      <div
        className={
          tone === "risk"
            ? "mt-0.5 flex h-9 w-9 items-center justify-center rounded-2xl border border-risk-200 bg-risk-50"
            : "mt-0.5 flex h-9 w-9 items-center justify-center rounded-2xl border border-go-200 bg-go-50"
        }
      >
        <Icon className={tone === "risk" ? "h-4 w-4 text-risk-700" : "h-4 w-4 text-go-700"} />
      </div>
      <div>
        <div className="text-sm font-semibold text-ink-900">{title}</div>
        <div className="mt-1 text-sm text-ink-500">{subtitle}</div>
      </div>
    </div>
  );
}
