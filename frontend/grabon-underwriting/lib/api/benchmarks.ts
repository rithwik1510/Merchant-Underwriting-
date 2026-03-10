import { apiFetch } from "./client";
import { CategoryBenchmark } from "../types/benchmarks";

interface RawCategoryBenchmark {
  category: string;
  avg_refund_rate: number | string;
  avg_customer_return_rate: number | string;
  avg_order_value_low: number | string;
  avg_order_value_high: number | string;
  typical_seasonality_low: number | string;
  typical_seasonality_high: number | string;
  risk_adjustment_factor: number | string;
}

function toNumber(value: number | string | null | undefined): number {
  if (typeof value === "number") return value;
  if (typeof value === "string") return Number(value);
  return 0;
}

function normalizeBenchmark(raw: RawCategoryBenchmark): CategoryBenchmark {
  return {
    ...raw,
    avg_refund_rate: toNumber(raw.avg_refund_rate),
    avg_customer_return_rate: toNumber(raw.avg_customer_return_rate),
    avg_order_value_low: toNumber(raw.avg_order_value_low),
    avg_order_value_high: toNumber(raw.avg_order_value_high),
    typical_seasonality_low: toNumber(raw.typical_seasonality_low),
    typical_seasonality_high: toNumber(raw.typical_seasonality_high),
    risk_adjustment_factor: toNumber(raw.risk_adjustment_factor),
  };
}

export const getBenchmark = async (category: string) => {
  const benchmark = await apiFetch<RawCategoryBenchmark>(`/benchmarks/${category}`);
  return normalizeBenchmark(benchmark);
};
