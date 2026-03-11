import { MerchantSummary } from "./merchant";

export type UnderwritingRunStatus =
  | "pending"
  | "processing"
  | "completed"
  | "failed"
  | "rejected"
  | "manual_review";

export type Decision = "approved" | "rejected" | "manual_review";

export type RiskTier = "tier_1" | "tier_2" | "tier_3" | "rejected" | null;

export type ImpactDirection = "positive" | "negative" | "neutral";

export interface DecisionReason {
  reason_code: string;
  reason_label: string;
  reason_detail: string;
  metric_name: string | null;
  metric_value: number | null;
  benchmark_value: number | null;
  weight: number | null;
  impact_direction: ImpactDirection | null;
}

export interface FeatureSnapshot {
  avg_monthly_gmv_3m: number | null;
  annual_gmv_12m: number;
  gmv_growth_3m_pct: number | null;
  gmv_growth_12m_pct: number | null;
  gmv_volatility_cv: number;
  avg_orders_3m: number | null;
  avg_unique_customers_3m: number | null;
  customer_efficiency_ratio: number | null;
  refund_delta_vs_category: number;
  return_rate_delta_vs_category: number;
  aov_position_vs_category_midpoint: number;
  seasonality_pressure_score: number;
  recent_gmv_drop_pct: number;
  merchant_health_score: number;
  raw_feature_json: Record<string, unknown>;
}

export interface CreditOffer {
  base_limit: number | null;
  final_limit: number | null;
  interest_rate_min: number | null;
  interest_rate_max: number | null;
  tenure_options: number[];
  offer_status: string;
}

export interface InsuranceOffer {
  coverage_base: number | null;
  coverage_amount: number | null;
  premium_rate: number | null;
  premium_amount: number | null;
  policy_type: string | null;
  offer_status: string;
}

export interface AISanityCheck {
  provider_name: string;
  model_name: string;
  status: "passed" | "warning" | "unavailable" | "skipped";
  issue_codes: string[];
  notes: string[];
  suggested_explanation_focus: string[];
  suggested_message_focus: string[];
  validation_errors_json: string[] | null;
  created_at: string;
}

export interface UnderwritingRun {
  run_id: number;
  merchant: MerchantSummary;
  policy_version: string;
  status: UnderwritingRunStatus;
  decision: Decision | null;
  risk_tier: RiskTier;
  numeric_score: number | null;
  usable_history_months: number;
  hard_stop_triggered: boolean;
  manual_review_triggered: boolean;
  features: FeatureSnapshot;
  hard_stop_reasons: DecisionReason[];
  manual_review_reasons: DecisionReason[];
  score_reasons: DecisionReason[];
  offer_adjustments: DecisionReason[];
  credit_offer: CreditOffer | null;
  insurance_offer: InsuranceOffer | null;
  ai_sanity_check: AISanityCheck | null;
  created_at: string;
}

export interface UnderwritingRunListItem {
  run_id: number;
  merchant_id: string;
  merchant_name: string;
  status: UnderwritingRunStatus;
  decision: Decision | null;
  risk_tier: RiskTier;
  numeric_score: number | null;
  created_at: string;
}
