export type MerchantCategory =
  | "food"
  | "fashion"
  | "electronics"
  | "travel"
  | "health_beauty"
  | "home_lifestyle";

export type IntendedOutcome =
  | "tier_1"
  | "tier_2"
  | "tier_3"
  | "rejected"
  | "manual_review"
  | "reduced_offers"
  | string;

export interface MerchantSummary {
  merchant_id: string;
  merchant_name: string;
  category: MerchantCategory;
  seed_intended_outcome: IntendedOutcome;
  unique_customer_count: number;
  customer_return_rate: number;
  return_and_refund_rate: number;
  registered_whatsapp_number: string;
  latest_run_id: number | null;
  latest_decision: string | null;
  latest_risk_tier: string | null;
  latest_credit_limit: number | null;
  latest_insurance_coverage: number | null;
  latest_run_at: string | null;
}

export interface MonthlyMetric {
  metric_month: string;
  gmv: number;
  orders_count: number;
  unique_customers: number;
  refund_rate: number;
}

export interface MerchantDetail extends MerchantSummary {
  coupon_redemption_rate: number;
  avg_order_value: number;
  seasonality_index: number;
  deal_exclusivity_rate: number;
  created_at: string;
  updated_at: string;
  monthly_metrics: MonthlyMetric[];
}
