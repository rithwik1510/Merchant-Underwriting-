import { ListOrdered } from "lucide-react";
import { getUnderwritingRuns } from "@/lib/api/underwriting";
import { RunsTable } from "@/components/runs/RunsTable";
import { EmptyState } from "@/components/ui/EmptyState";
import { PageHero } from "@/components/ui/PageHero";

export const dynamic = "force-dynamic";

export default async function RunHistoryPage() {
  let runs: Awaited<ReturnType<typeof getUnderwritingRuns>> = [];
  let error: string | null = null;

  try {
    runs = await getUnderwritingRuns();
  } catch {
    error = "Could not load run history.";
  }

  const sorted = [...runs].sort(
    (left, right) => new Date(right.created_at).getTime() - new Date(left.created_at).getTime()
  );

  return (
    <div className="space-y-6 px-6 py-6">
      <PageHero
        eyebrow="Run ledger"
        title="Underwriting run history"
        description="Track every underwriting packet created across the merchant portfolio, including decision outcome, tier, score, and downstream status."
        meta={
          <span className="status-pill border-ink-200 bg-white text-ink-500">
            {sorted.length} persisted runs
          </span>
        }
      />

      {error ? (
        <div className="rounded-2xl border border-risk-200 bg-risk-50 px-5 py-4 text-sm text-risk-700">
          {error}
        </div>
      ) : null}

      {sorted.length === 0 && !error ? (
        <EmptyState
          icon={ListOrdered}
          title="No runs yet"
          description="Go to a merchant page and trigger underwriting to create the first decision packet."
        />
      ) : (
        <RunsTable runs={sorted} />
      )}
    </div>
  );
}
