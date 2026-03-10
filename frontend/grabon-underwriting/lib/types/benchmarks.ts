export interface CategoryBenchmark {
  category: string;
  avg_refund_rate: number;
  avg_customer_return_rate: number;
  avg_order_value_low: number;
  avg_order_value_high: number;
  typical_seasonality_low: number;
  typical_seasonality_high: number;
  risk_adjustment_factor: number;
}
