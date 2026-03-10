import { apiFetch } from "./client";
import { MerchantSummary, MerchantDetail } from "../types/merchant";

function toNumber(value: number | string | null | undefined): number {
  if (typeof value === "number") return value;
  if (typeof value === "string") return Number(value);
  return 0;
}

function normalizeMerchantSummary(raw: MerchantSummary): MerchantSummary {
  return {
    ...raw,
    unique_customer_count: toNumber(raw.unique_customer_count),
    customer_return_rate: toNumber(raw.customer_return_rate),
    return_and_refund_rate: toNumber(raw.return_and_refund_rate),
  };
}

function normalizeMerchantDetail(raw: MerchantDetail): MerchantDetail {
  return {
    ...raw,
    unique_customer_count: toNumber(raw.unique_customer_count),
    customer_return_rate: toNumber(raw.customer_return_rate),
    return_and_refund_rate: toNumber(raw.return_and_refund_rate),
    coupon_redemption_rate: toNumber(raw.coupon_redemption_rate),
    avg_order_value: toNumber(raw.avg_order_value),
    seasonality_index: toNumber(raw.seasonality_index),
    deal_exclusivity_rate: toNumber(raw.deal_exclusivity_rate),
    monthly_metrics: raw.monthly_metrics.map((metric) => ({
      ...metric,
      gmv: toNumber(metric.gmv),
      orders_count: toNumber(metric.orders_count),
      unique_customers: toNumber(metric.unique_customers),
      refund_rate: toNumber(metric.refund_rate),
    })),
  };
}

export const getMerchants = async () => {
  const merchants = await apiFetch<MerchantSummary[]>("/merchants");
  return merchants.map(normalizeMerchantSummary);
};

export const getMerchantDetail = async (id: string) => {
  const merchant = await apiFetch<MerchantDetail>(`/merchants/${id}`);
  return normalizeMerchantDetail(merchant);
};
