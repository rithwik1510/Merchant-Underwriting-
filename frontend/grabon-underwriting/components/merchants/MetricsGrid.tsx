"use client";

import { motion } from "framer-motion";
import {
  BadgePercent,
  CalendarRange,
  RotateCcw,
  ShoppingBag,
  Users,
  Wallet,
} from "lucide-react";
import { MerchantDetail } from "@/lib/types/merchant";
import { AnimatedNumber } from "@/components/ui/AnimatedNumber";
import { formatCurrency } from "@/lib/utils/formatters";

interface MetricItem {
  label: string;
  value: number;
  formatter: (value: number) => string;
  note?: string;
  warnIf?: (value: number) => boolean;
  icon: React.ComponentType<{ className?: string }>;
}

export function MetricsGrid({ merchant }: { merchant: MerchantDetail }) {
  const metrics: MetricItem[] = [
    {
      label: "Unique customers",
      value: merchant.unique_customer_count,
      formatter: (value) => Math.round(value).toLocaleString("en-IN"),
      icon: Users,
    },
    {
      label: "Return rate",
      value: merchant.customer_return_rate,
      formatter: (value) => `${value.toFixed(1)}%`,
      warnIf: (value) => value < 18,
      icon: RotateCcw,
    },
    {
      label: "Refund rate",
      value: merchant.return_and_refund_rate,
      formatter: (value) => `${value.toFixed(1)}%`,
      warnIf: (value) => value > 12,
      icon: ShoppingBag,
    },
    {
      label: "Avg order value",
      value: merchant.avg_order_value,
      formatter: formatCurrency,
      icon: Wallet,
    },
    {
      label: "Coupon redemption",
      value: merchant.coupon_redemption_rate,
      formatter: (value) => `${value.toFixed(1)}%`,
      icon: BadgePercent,
    },
    {
      label: "Seasonality index",
      value: merchant.seasonality_index,
      formatter: (value) => value.toFixed(2),
      note: ">3.0 generally triggers review",
      warnIf: (value) => value > 3,
      icon: CalendarRange,
    },
  ];

  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-3">
      {metrics.map((metric, index) => {
        const isWarn = metric.warnIf?.(metric.value) ?? false;
        const Icon = metric.icon;

        return (
          <motion.div
            key={metric.label}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.08 + index * 0.05 }}
            className="metric-card"
          >
            <div className="mb-4 flex items-start justify-between gap-3">
              <div
                className={`flex h-10 w-10 items-center justify-center rounded-2xl border ${
                  isWarn
                    ? "border-risk-200 bg-risk-50 text-risk-600"
                    : "border-go-200 bg-go-50 text-go-600"
                }`}
              >
                <Icon className="h-4 w-4" />
              </div>
              {isWarn ? (
                <span className="status-pill border-risk-200 bg-risk-50 text-risk-600">
                  Watch
                </span>
              ) : null}
            </div>

            <div
              className={`mb-1 font-mono text-2xl font-bold tabular-nums leading-none ${
                isWarn ? "text-risk-700" : "text-ink-900"
              }`}
            >
              <AnimatedNumber value={metric.value} formatter={metric.formatter} />
            </div>
            <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-ink-400">
              {metric.label}
            </div>
            {metric.note ? <div className="mt-1 text-[11px] text-ink-400">{metric.note}</div> : null}
          </motion.div>
        );
      })}
    </div>
  );
}
