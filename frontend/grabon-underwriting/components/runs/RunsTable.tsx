"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowUpRight, Search } from "lucide-react";
import { UnderwritingRunListItem } from "@/lib/types/underwriting";
import { decisionToTierKey, getTierConfig } from "@/lib/constants/tiers";
import { formatRelativeTime, scoreToColor } from "@/lib/utils/formatters";

interface RunsTableProps {
  runs: UnderwritingRunListItem[];
}

const DECISION_FILTERS = ["all", "approved", "rejected", "manual_review"] as const;

export function RunsTable({ runs }: RunsTableProps) {
  const [search, setSearch] = useState("");
  const [decisionFilter, setDecisionFilter] =
    useState<(typeof DECISION_FILTERS)[number]>("all");

  const filtered = useMemo(() => {
    return runs.filter((run) => {
      const matchesSearch =
        !search ||
        run.merchant_name.toLowerCase().includes(search.toLowerCase()) ||
        String(run.run_id).includes(search);
      const matchesDecision = decisionFilter === "all" || run.decision === decisionFilter;
      return matchesSearch && matchesDecision;
    });
  }, [runs, search, decisionFilter]);

  return (
    <div className="space-y-4">
      <div className="panel-card flex flex-col gap-3 p-4 lg:flex-row lg:items-center lg:justify-between">
        <div className="relative w-full max-w-md">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-400" />
          <input
            type="text"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search merchant or run ID"
            className="w-full rounded-xl border border-ink-200 bg-white py-2.5 pl-10 pr-3 text-sm text-ink-900 placeholder:text-ink-300 focus:border-go-500 focus:outline-none"
          />
        </div>

        <div className="flex flex-wrap gap-2">
          {DECISION_FILTERS.map((filter) => {
            const active = decisionFilter === filter;
            return (
              <button
                key={filter}
                onClick={() => setDecisionFilter(filter)}
                className={`rounded-xl border px-3 py-2 text-xs font-semibold uppercase tracking-[0.12em] transition-all ${
                  active
                    ? "border-go-300 bg-go-50 text-go-700"
                    : "border-ink-200 bg-white text-ink-500"
                }`}
              >
                {filter === "all" ? "All" : filter.replace(/_/g, " ")}
              </button>
            );
          })}
        </div>
      </div>

      <div className="panel-card overflow-hidden p-0">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[760px]">
            <thead className="bg-surface-100">
              <tr>
                {["Run ID", "Merchant", "Decision", "Tier", "Score", "Created", ""].map((heading) => (
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
              {filtered.map((run, index) => {
                const tierKey = decisionToTierKey(run.decision, run.risk_tier);
                const tier = getTierConfig(tierKey);

                return (
                  <motion.tr
                    key={run.run_id}
                    initial={{ opacity: 0, y: 6 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.2, delay: index * 0.02 }}
                    className="border-t border-ink-100 bg-white transition-colors hover:bg-surface-50"
                  >
                    <td className="px-5 py-4 font-mono text-sm text-ink-600">#{run.run_id}</td>
                    <td className="px-5 py-4 text-sm font-semibold text-ink-900">{run.merchant_name}</td>
                    <td className="px-5 py-4">
                      <span
                        className="status-pill"
                        style={{
                          color: tier.hexColor,
                          background: tier.badgeBg,
                          border: `1px solid ${tier.badgeBorder}`,
                        }}
                      >
                        {run.decision?.replace(/_/g, " ") ?? "pending"}
                      </span>
                    </td>
                    <td className="px-5 py-4 font-mono text-sm" style={{ color: tier.hexColor }}>
                      {run.risk_tier?.replace(/_/g, " ") ?? "-"}
                    </td>
                    <td
                      className="px-5 py-4 font-mono text-sm font-semibold"
                      style={{ color: scoreToColor(run.numeric_score) }}
                    >
                      {run.numeric_score?.toFixed(1) ?? "-"}
                    </td>
                    <td className="px-5 py-4 text-sm text-ink-500">
                      {formatRelativeTime(run.created_at)}
                    </td>
                    <td className="px-5 py-4">
                      <Link
                        href={`/runs/${run.run_id}`}
                        className="inline-flex items-center gap-1 text-sm font-medium text-go-700 transition-colors hover:text-go-800"
                      >
                        View
                        <ArrowUpRight className="h-4 w-4" />
                      </Link>
                    </td>
                  </motion.tr>
                );
              })}
            </tbody>
          </table>

          {!filtered.length ? (
            <div className="px-5 py-12 text-center text-sm text-ink-500">
              No runs match the current filters.
            </div>
          ) : null}
        </div>
      </div>

      <div className="text-xs font-mono text-ink-500">
        {filtered.length} of {runs.length} runs shown
      </div>
    </div>
  );
}
