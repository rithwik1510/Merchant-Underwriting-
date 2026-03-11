import { notFound } from "next/navigation";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { getUnderwritingRun } from "@/lib/api/underwriting";
import { getCommunications } from "@/lib/api/communications";
import { CommunicationWorkspace } from "@/components/communications/CommunicationWorkspace";
import { PageHero } from "@/components/ui/PageHero";
import { ApiError } from "@/lib/api/client";

export const dynamic = "force-dynamic";

interface Params {
  params: { id: string };
}

export default async function CommunicatePage({ params }: Params) {
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
        eyebrow="Communication layer"
        title={`Explain and communicate ${run.merchant.merchant_name}`}
        description="Generate the grounded AI explanation, review outbound WhatsApp copy, and inspect persisted communication history for this underwriting run."
        meta={
          <>
            <span className="status-pill border-ink-200 bg-white text-ink-500">
              Run #{run.run_id}
            </span>
            <span className="status-pill border-go-200 bg-go-100 text-go-700">
              {run.decision?.replace(/_/g, " ") ?? "pending"}
            </span>
          </>
        }
      />

      <CommunicationWorkspace
        runId={run.run_id}
        defaultRecipientPhone={run.merchant.registered_whatsapp_number}
        initialExplanation={comms?.latest_explanation ?? null}
        initialDraft={comms?.latest_whatsapp_draft ?? null}
        initialMessages={comms?.whatsapp_messages ?? []}
      />
    </div>
  );
}
