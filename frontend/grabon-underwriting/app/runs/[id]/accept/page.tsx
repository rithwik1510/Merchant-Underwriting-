import { notFound } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, ClipboardCheck } from "lucide-react";
import { getUnderwritingRun } from "@/lib/api/underwriting";
import { getAcceptance } from "@/lib/api/offers";
import { AcceptanceForm } from "@/components/acceptance/AcceptanceForm";
import { CreditOfferCard, InsuranceOfferCard } from "@/components/underwriting/OfferCards";
import { PageHero } from "@/components/ui/PageHero";
import { PanelCard } from "@/components/ui/PanelCard";
import { ApiError } from "@/lib/api/client";

export const dynamic = "force-dynamic";

interface Params {
  params: { id: string };
}

export default async function AcceptancePage({ params }: Params) {
  let run;
  try {
    run = await getUnderwritingRun(params.id);
  } catch {
    notFound();
  }

  let existing = null;
  try {
    existing = await getAcceptance(run.run_id);
  } catch (err) {
    if (!(err instanceof ApiError) || err.status !== 404) {
      existing = null;
    }
  }

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
        eyebrow="Offer conversion"
        title={`Record acceptance for ${run.merchant.merchant_name}`}
        description="Review the offers produced by the underwriting engine, then capture the merchant acceptance record that unlocks the mandate workflow."
        meta={
          <>
            <span className="status-pill border-ink-200 bg-white text-ink-500">
              Run #{run.run_id}
            </span>
            <span className="status-pill border-go-200 bg-go-100 text-go-700">
              {existing ? "Acceptance recorded" : "Waiting for acceptance"}
            </span>
          </>
        }
      />

      <div className="grid gap-5 xl:grid-cols-[1fr_1fr]">
        <div className="space-y-4">
          <PanelCard className="p-5">
            <div className="mb-1 flex items-center gap-2 text-sm font-semibold text-ink-900">
              <ClipboardCheck className="h-4 w-4 text-go-600" />
              Available offers
            </div>
            <div className="text-sm text-ink-500">
              The acceptance record can only choose from offer objects already produced by the deterministic engine.
            </div>
          </PanelCard>
          <CreditOfferCard offer={run.credit_offer} />
          <InsuranceOfferCard offer={run.insurance_offer} />
        </div>

        <PanelCard className="p-5">
          <div className="mb-4 text-sm font-semibold text-ink-900">
            {existing ? "Acceptance record" : "Record acceptance"}
          </div>
          <AcceptanceForm run={run} existing={existing} />
        </PanelCard>
      </div>
    </div>
  );
}
