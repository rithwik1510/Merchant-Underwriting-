import { notFound } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, ChartNoAxesCombined, DatabaseZap, ShieldCheck } from "lucide-react";
import { getMerchantDetail } from "@/lib/api/merchants";
import { getBenchmark } from "@/lib/api/benchmarks";
import { GmvAreaChart } from "@/components/merchants/GmvAreaChart";
import { MetricsGrid } from "@/components/merchants/MetricsGrid";
import { RunUnderwritingButton } from "@/components/merchants/RunUnderwritingButton";
import { OutcomeBadge } from "@/components/merchants/OutcomeBadge";
import { PageHero } from "@/components/ui/PageHero";
import { PanelCard } from "@/components/ui/PanelCard";
import { SectionTabs } from "@/components/ui/SectionTabs";
import { Tabs, TabsContent } from "@/components/ui/tabs";
import { getCategoryConfig } from "@/lib/constants/categories";
import { formatCurrency, formatDate } from "@/lib/utils/formatters";

export const dynamic = "force-dynamic";

interface Params {
  params: { id: string };
}

export default async function MerchantDetailPage({ params }: Params) {
  let merchant;
  try {
    merchant = await getMerchantDetail(params.id);
  } catch {
    notFound();
  }

  let benchmark = null;
  try {
    benchmark = await getBenchmark(merchant.category);
  } catch {
    benchmark = null;
  }

  const category = getCategoryConfig(merchant.category);
  const annualGmv = merchant.monthly_metrics.reduce((sum, item) => sum + item.gmv, 0);
  const avgGmv = merchant.monthly_metrics.length ? annualGmv / merchant.monthly_metrics.length : 0;

  return (
    <div className="space-y-6 px-6 py-6">
      <Link
        href="/"
        className="inline-flex items-center gap-1.5 text-sm text-ink-400 transition-colors hover:text-go-600"
      >
        <ArrowLeft className="h-4 w-4" />
        All Merchants
      </Link>

      <PageHero
        eyebrow={`${category.label} merchant`}
        title={merchant.merchant_name}
        meta={
          <>
            <span className="status-pill border-ink-200 bg-white font-mono text-ink-500">
              {merchant.merchant_id}
            </span>
            <OutcomeBadge outcome={merchant.seed_intended_outcome} size="md" />
            <span className="status-pill border-ink-200 bg-white text-ink-500">
              Updated {formatDate(merchant.updated_at)}
            </span>
          </>
        }
      />

      <div className="grid gap-4 md:grid-cols-3">
        <PanelCard className="p-5">
          <div className="text-xs font-semibold uppercase tracking-[0.18em] text-ink-400">
            Annual GMV
          </div>
          <div className="mt-2 text-3xl font-bold tracking-tight text-ink-900">
            {formatCurrency(annualGmv)}
          </div>
          <div className="mt-2 text-sm text-ink-500">
            Based on {merchant.monthly_metrics.length} months of available history.
          </div>
        </PanelCard>

        <PanelCard className="p-5">
          <div className="text-xs font-semibold uppercase tracking-[0.18em] text-ink-400">
            Average monthly GMV
          </div>
          <div className="mt-2 text-3xl font-bold tracking-tight text-ink-900">
            {formatCurrency(avgGmv)}
          </div>
          <div className="mt-2 text-sm text-ink-500">
            Baseline volume used for working-capital sizing logic.
          </div>
        </PanelCard>

        <PanelCard className="p-5">
          <div className="text-xs font-semibold uppercase tracking-[0.18em] text-ink-400">
            Benchmark posture
          </div>
          <div className="mt-2 text-3xl font-bold tracking-tight text-ink-900">
            {benchmark ? "Loaded" : "Pending"}
          </div>
          <div className="mt-2 text-sm text-ink-500">
            {benchmark
              ? `${category.label} category benchmark is available for comparison.`
              : "Benchmark data is unavailable, so underwriting will lean more heavily on the merchant ledger."}
          </div>
        </PanelCard>
      </div>

      <Tabs defaultValue="overview" className="space-y-4">
        <SectionTabs
          items={[
            { value: "overview", label: "Overview" },
            { value: "benchmarks", label: "Benchmarks" },
            { value: "history", label: "History", count: `${merchant.monthly_metrics.length}m` },
          ]}
        />

        <TabsContent value="overview" className="space-y-6">
          <PanelCard className="p-5">
            <div className="mb-4 flex items-center justify-between gap-3">
              <div className="text-sm font-semibold text-ink-900">GMV trend</div>
              <div className="flex items-center gap-1.5 text-[11px] text-ink-400">
                <span className="h-2 w-6 rounded-full bg-go-500" />
                Monthly GMV
              </div>
            </div>
            <GmvAreaChart metrics={merchant.monthly_metrics} />
          </PanelCard>

          <div className="space-y-3">
            <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-ink-400">
              <DatabaseZap className="h-3.5 w-3.5" />
              Merchant operating metrics
            </div>
            <MetricsGrid merchant={merchant} />
          </div>
        </TabsContent>

        <TabsContent value="benchmarks">
          <div className="grid gap-4 lg:grid-cols-[1.1fr_0.9fr]">
            <PanelCard className="p-5">
              <div className="mb-4 flex items-center gap-2 text-sm font-semibold text-ink-900">
                <ShieldCheck className="h-4 w-4 text-go-600" />
                Category benchmark comparison
              </div>
              {benchmark ? (
                <div className="grid gap-3 md:grid-cols-2">
                  {[
                    {
                      label: "Refund average",
                      merchantValue: `${merchant.return_and_refund_rate.toFixed(1)}%`,
                      benchmarkValue: `${benchmark.avg_refund_rate.toFixed(1)}%`,
                    },
                    {
                      label: "Return rate average",
                      merchantValue: `${merchant.customer_return_rate.toFixed(1)}%`,
                      benchmarkValue: `${benchmark.avg_customer_return_rate.toFixed(1)}%`,
                    },
                    {
                      label: "AOV band",
                      merchantValue: formatCurrency(merchant.avg_order_value),
                      benchmarkValue: `${formatCurrency(benchmark.avg_order_value_low)} - ${formatCurrency(
                        benchmark.avg_order_value_high
                      )}`,
                    },
                    {
                      label: "Seasonality band",
                      merchantValue: merchant.seasonality_index.toFixed(2),
                      benchmarkValue: `${benchmark.typical_seasonality_low.toFixed(2)} - ${benchmark.typical_seasonality_high.toFixed(2)}`,
                    },
                  ].map((item) => (
                    <div key={item.label} className="rounded-2xl border border-ink-100 bg-surface-50 p-4">
                      <div className="text-xs font-semibold uppercase tracking-[0.16em] text-ink-400">
                        {item.label}
                      </div>
                      <div className="mt-3 text-sm text-ink-500">Merchant</div>
                      <div className="text-lg font-semibold text-ink-900">{item.merchantValue}</div>
                      <div className="mt-3 text-sm text-ink-500">Benchmark</div>
                      <div className="text-lg font-semibold text-go-700">{item.benchmarkValue}</div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="rounded-2xl border border-ink-100 bg-surface-50 p-5 text-sm text-ink-500">
                  Benchmark data could not be loaded for this category. The underwriting engine can still use merchant history, but benchmark-aware explanations will be limited.
                </div>
              )}
            </PanelCard>

            <PanelCard className="p-5">
              <div className="mb-4 flex items-center gap-2 text-sm font-semibold text-ink-900">
                <ChartNoAxesCombined className="h-4 w-4 text-risk-600" />
                Underwriting preview
              </div>
              <div className="space-y-4 text-sm text-ink-500">
                <p>
                  This profile is pre-tagged as{" "}
                  <span className="font-semibold text-ink-900">
                    {merchant.seed_intended_outcome.replace(/_/g, " ")}
                  </span>{" "}
                  so we can validate the scoring engine against known scenarios.
                </p>
                <p>
                  The run will compute features from this history, compare benchmark deltas, apply hard stops, and then map those signals into tier, decision, and offer outputs.
                </p>
                <div className="rounded-2xl border border-go-200 bg-go-50 p-4">
                  <div className="text-xs font-semibold uppercase tracking-[0.18em] text-go-700">
                    Ready for underwriting
                  </div>
                  <div className="mt-2 text-sm text-ink-800">
                    Launch the deterministic engine when you are ready to generate a decision packet.
                  </div>
                </div>
                <RunUnderwritingButton merchantId={merchant.merchant_id} />
              </div>
            </PanelCard>
          </div>
        </TabsContent>

        <TabsContent value="history">
          <PanelCard className="p-0">
            <div className="border-b border-ink-100 px-5 py-4">
              <div className="text-sm font-semibold text-ink-900">History ledger</div>
              <div className="mt-1 text-sm text-ink-500">
                Month-level GMV, order, and customer counts used for deterministic feature engineering.
              </div>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full min-w-[680px]">
                <thead className="bg-surface-100">
                  <tr>
                    {["Month", "GMV", "Orders", "Customers", "Refund rate"].map((heading) => (
                      <th
                        key={heading}
                        className="px-5 py-3 text-left text-[11px] font-semibold uppercase tracking-[0.18em] text-ink-400"
                      >
                        {heading}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {merchant.monthly_metrics.map((row) => (
                    <tr key={row.metric_month} className="border-t border-ink-100">
                      <td className="px-5 py-3 text-sm font-medium text-ink-800">
                        {row.metric_month}
                      </td>
                      <td className="px-5 py-3 font-mono text-sm text-ink-700">
                        {formatCurrency(row.gmv)}
                      </td>
                      <td className="px-5 py-3 font-mono text-sm text-ink-700">
                        {row.orders_count.toLocaleString("en-IN")}
                      </td>
                      <td className="px-5 py-3 font-mono text-sm text-ink-700">
                        {row.unique_customers.toLocaleString("en-IN")}
                      </td>
                      <td className="px-5 py-3 font-mono text-sm text-ink-700">
                        {row.refund_rate.toFixed(1)}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </PanelCard>
        </TabsContent>
      </Tabs>
    </div>
  );
}
