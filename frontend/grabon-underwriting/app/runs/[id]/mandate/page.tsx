import { notFound } from "next/navigation";
import Link from "next/link";
import { AlertTriangle, ArrowLeft, Landmark } from "lucide-react";
import { getUnderwritingRun } from "@/lib/api/underwriting";
import { getAcceptance } from "@/lib/api/offers";
import { MandateWizard } from "@/components/mandate/MandateWizard";
import { PageHero } from "@/components/ui/PageHero";
import { PanelCard } from "@/components/ui/PanelCard";
import { ApiError } from "@/lib/api/client";

export const dynamic = "force-dynamic";

interface Params {
  params: { id: string };
}

export default async function MandatePage({ params }: Params) {
  let run;
  try {
    run = await getUnderwritingRun(params.id);
  } catch {
    notFound();
  }

  let acceptance = null;
  try {
    acceptance = await getAcceptance(run.run_id);
  } catch (err) {
    if (!(err instanceof ApiError) || err.status !== 404) {
      acceptance = null;
    }
  }

  const canStart = acceptance?.mandate_can_start ?? false;

  return (
    <div className="space-y-5 px-6 py-6">
      <Link
        href={`/runs/${run.run_id}`}
        className="inline-flex items-center gap-1.5 text-sm text-ink-400 transition-colors hover:text-go-600"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to run #{run.run_id}
      </Link>

      <PageHero
        eyebrow="Mock NACH workflow"
        title={`Mandate flow for ${run.merchant.merchant_name}`}
        description="Move the accepted merchant through a realistic bank, OTP, and UMRN journey without changing the deterministic underwriting decision."
        meta={
          <>
            <span className="status-pill border-ink-200 bg-white text-ink-500">
              Run #{run.run_id}
            </span>
            <span className="status-pill border-go-200 bg-go-100 text-go-700">
              {acceptance ? "Acceptance found" : "Acceptance required"}
            </span>
          </>
        }
      />

      {!acceptance ? (
        <div className="rounded-[24px] border border-risk-200 bg-risk-50 px-5 py-4 text-sm text-risk-700">
          <div className="flex items-start gap-3">
            <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
            <div>
              An offer must be accepted before the mandate can begin. Use the acceptance page first.
            </div>
          </div>
        </div>
      ) : null}

      {acceptance && !canStart ? (
        <div className="rounded-[24px] border border-risk-200 bg-risk-50 px-5 py-4 text-sm text-risk-700">
          <div className="flex items-start gap-3">
            <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
            <div>The current acceptance record does not allow a mandate to start.</div>
          </div>
        </div>
      ) : null}

      <PanelCard className="p-5">
        <div className="mb-4 flex items-center gap-2 text-sm font-semibold text-ink-900">
          <Landmark className="h-4 w-4 text-go-600" />
          Mandate wizard
        </div>
        <MandateWizard runId={run.run_id} />
      </PanelCard>
    </div>
  );
}
