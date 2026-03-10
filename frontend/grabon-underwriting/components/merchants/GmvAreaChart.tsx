"use client";

import {
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ComposedChart,
} from "recharts";
import { MonthlyMetric } from "@/lib/types/merchant";
import { formatCurrency, formatMonthLabel } from "@/lib/utils/formatters";

function CustomTooltip({
  active,
  payload,
  label,
}: {
  active?: boolean;
  payload?: { name: string; value: number; color: string }[];
  label?: string;
}) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-2xl border border-ink-100 bg-white px-4 py-3 text-xs shadow-card">
      <div className="mb-2 font-semibold text-ink-600">{label}</div>
      {payload.map((p) => (
        <div key={p.name} className="mb-1 flex items-center gap-2 last:mb-0">
          <div className="h-2 w-2 rounded-full" style={{ background: p.color }} />
          <span className="text-ink-500">{p.name}:</span>
          <span className="font-semibold text-ink-900">
            {p.name === "GMV" ? formatCurrency(p.value) : p.value.toLocaleString("en-IN")}
          </span>
        </div>
      ))}
    </div>
  );
}

export function GmvAreaChart({ metrics }: { metrics: MonthlyMetric[] }) {
  const data = [...metrics]
    .sort((a, b) => a.metric_month.localeCompare(b.metric_month))
    .map((m) => ({
      month: formatMonthLabel(m.metric_month),
      GMV: Number(m.gmv),
      Orders: m.orders_count,
    }));

  const maxGmv = Math.max(...data.map((d) => d.GMV));

  return (
    <ResponsiveContainer width="100%" height={280}>
      <ComposedChart data={data} margin={{ top: 8, right: 20, bottom: 12, left: 0 }}>
        <defs>
          <linearGradient id="gmvGradControl" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#2563EB" stopOpacity={0.18} />
            <stop offset="100%" stopColor="#2563EB" stopOpacity={0.01} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="4 4" stroke="#E2E8F0" vertical={false} />
        <XAxis
          dataKey="month"
          tick={{ fill: "#64748B", fontSize: 11 }}
          tickLine={false}
          axisLine={false}
        />
        <YAxis
          tickFormatter={(v) => formatCurrency(v)}
          tick={{ fill: "#64748B", fontSize: 10 }}
          tickLine={false}
          axisLine={false}
          domain={[0, maxGmv * 1.1]}
          width={64}
        />
        <Tooltip content={<CustomTooltip />} />
        <Area
          type="monotone"
          dataKey="GMV"
          stroke="#2563EB"
          strokeWidth={2.5}
          fill="url(#gmvGradControl)"
          dot={false}
          activeDot={{ r: 5, fill: "#2563EB", stroke: "#ffffff", strokeWidth: 2 }}
        />
      </ComposedChart>
    </ResponsiveContainer>
  );
}
