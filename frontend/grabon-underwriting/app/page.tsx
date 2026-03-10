import { getMerchants } from "@/lib/api/merchants";
import { MerchantGrid } from "@/components/merchants/MerchantGrid";
import { EmptyState } from "@/components/ui/EmptyState";
import { LayoutGrid } from "lucide-react";

export const dynamic = "force-dynamic";

export default async function MerchantsPage() {
  let merchants: Awaited<ReturnType<typeof getMerchants>> = [];
  let error: string | null = null;

  try {
    merchants = await getMerchants();
  } catch {
    error = "Could not reach the backend. Make sure the API is running at localhost:8000.";
  }

  const total = merchants.length;
  const approved = merchants.filter((m) =>
    ["tier_1", "tier_2"].includes(m.seed_intended_outcome)
  ).length;
  const manualReview = merchants.filter((m) =>
    m.seed_intended_outcome.includes("manual")
  ).length;
  const rejected = merchants.filter((m) =>
    m.seed_intended_outcome.includes("rejected")
  ).length;

  const stats = [
    { label: "Total", value: total, color: "text-ink-700" },
    { label: "Approved", value: approved, color: "text-go-600" },
    { label: "Review", value: manualReview, color: "text-violet-600" },
    { label: "Rejected", value: rejected, color: "text-risk-600" },
  ];

  return (
    <div className="px-6 py-6">
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="mb-1 text-[11px] font-semibold uppercase tracking-[0.22em] text-go-600">
            Fintech Control
          </p>
          <h1 className="text-2xl font-bold tracking-tight text-ink-900">Merchant Console</h1>
          {!error && merchants.length > 0 ? (
            <p className="mt-1 text-sm text-ink-500">Choose a merchant to inspect and run underwriting.</p>
          ) : null}
        </div>

        {!error && merchants.length > 0 ? (
          <div className="flex items-stretch divide-x divide-ink-100 overflow-hidden rounded-2xl border border-ink-100 bg-white shadow-card">
            {stats.map((stat) => (
              <div key={stat.label} className="flex flex-col items-center px-5 py-3">
                <div className={`font-mono text-2xl font-bold tabular-nums ${stat.color}`}>
                  {stat.value}
                </div>
                <div className="mt-0.5 text-[10px] font-semibold uppercase tracking-[0.16em] text-ink-400">
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        ) : null}
      </div>

      {error ? (
        <div className="rounded-2xl border border-risk-200 bg-risk-50 px-5 py-4 text-sm text-risk-700">
          <strong>Backend unavailable:</strong> {error}
        </div>
      ) : merchants.length === 0 ? (
        <EmptyState
          icon={LayoutGrid}
          title="No merchants found"
          description="Seed the database by calling POST /api/seed/init on the backend."
        />
      ) : (
        <MerchantGrid merchants={merchants} />
      )}
    </div>
  );
}
