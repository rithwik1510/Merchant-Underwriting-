from __future__ import annotations

from decimal import Decimal

from app.models import CategoryBenchmark, Merchant
from app.services.underwriting_math import average, clamp_decimal, quantize_2, quantize_4, safe_div, stddev
from app.services.underwriting_types import FeatureResult


def compute_features(merchant: Merchant, benchmark: CategoryBenchmark | None, policy_rules: dict) -> FeatureResult:
    metrics = merchant.monthly_metrics
    gmv_values = [Decimal(metric.gmv) for metric in metrics]
    order_values = [Decimal(metric.orders_count) for metric in metrics]
    unique_customer_values = [Decimal(metric.unique_customers) for metric in metrics]

    usable_history_months = len(metrics)
    last_3_gmv = gmv_values[-3:]
    prev_3_gmv = gmv_values[-6:-3]
    last_3_orders = order_values[-3:]
    last_3_unique_customers = unique_customer_values[-3:]

    avg_monthly_gmv_3m = average(last_3_gmv) if last_3_gmv else None
    annual_gmv_12m = sum(gmv_values, Decimal("0"))

    gmv_growth_3m_pct = None
    recent_gmv_drop_pct = Decimal("0")
    if len(last_3_gmv) == 3 and len(prev_3_gmv) == 3:
        prev_avg = average(prev_3_gmv)
        curr_avg = average(last_3_gmv)
        if prev_avg != 0:
            gmv_growth_3m_pct = quantize_2(safe_div(curr_avg - prev_avg, prev_avg) * Decimal("100"))
            recent_gmv_drop_pct = quantize_2(max(Decimal("0"), safe_div(prev_avg - curr_avg, prev_avg) * Decimal("100")))

    gmv_growth_12m_pct = None
    if len(gmv_values) >= 2 and gmv_values[0] != 0:
        gmv_growth_12m_pct = quantize_2(safe_div(gmv_values[-1] - gmv_values[0], gmv_values[0]) * Decimal("100"))

    gmv_volatility_cv = Decimal("0")
    if gmv_values:
        gmv_volatility_cv = quantize_4(safe_div(stddev(gmv_values), average(gmv_values)))

    avg_orders_3m = quantize_2(average(last_3_orders)) if last_3_orders else None
    avg_unique_customers_3m = quantize_2(average(last_3_unique_customers)) if last_3_unique_customers else None
    customer_efficiency_ratio = None
    if avg_monthly_gmv_3m is not None and avg_unique_customers_3m is not None:
        customer_efficiency_ratio = quantize_2(safe_div(avg_monthly_gmv_3m, avg_unique_customers_3m))

    if benchmark:
        category_refund = Decimal(benchmark.avg_refund_rate)
        category_return = Decimal(benchmark.avg_customer_return_rate)
        category_mid_aov = (Decimal(benchmark.avg_order_value_low) + Decimal(benchmark.avg_order_value_high)) / Decimal("2")
        benchmark_high_seasonality = Decimal(benchmark.typical_seasonality_high)
    else:
        category_refund = Decimal("0")
        category_return = Decimal("0")
        category_mid_aov = Decimal("0")
        benchmark_high_seasonality = Decimal("0")

    refund_delta_vs_category = quantize_2(Decimal(merchant.return_and_refund_rate) - category_refund)
    return_rate_delta_vs_category = quantize_2(Decimal(merchant.customer_return_rate) - category_return)
    aov_position_vs_category_midpoint = quantize_2(Decimal(merchant.avg_order_value) - category_mid_aov)

    seasonality_pressure_score = Decimal("0")
    if benchmark and Decimal(merchant.seasonality_index) > benchmark_high_seasonality:
        overshoot_ratio = safe_div(Decimal(merchant.seasonality_index) - benchmark_high_seasonality, benchmark_high_seasonality)
        seasonality_pressure_score = Decimal("0.5") if overshoot_ratio <= Decimal("0.2") else Decimal("1.0")

    refund_health = clamp_decimal(Decimal("1") - safe_div(max(refund_delta_vs_category, Decimal("0")), Decimal("12")), Decimal("0"), Decimal("1"))
    return_health = clamp_decimal(safe_div(Decimal(merchant.customer_return_rate), Decimal("100")), Decimal("0"), Decimal("1"))
    growth_health = clamp_decimal(
        safe_div((gmv_growth_12m_pct or Decimal("0")) + Decimal("20"), Decimal("60")),
        Decimal("0"),
        Decimal("1"),
    )
    merchant_health_score = quantize_2((refund_health * Decimal("40") + return_health * Decimal("30") + growth_health * Decimal("30")))

    raw_feature_json = {
        "usable_history_months": usable_history_months,
        "last_3_gmv_count": len(last_3_gmv),
        "previous_3_gmv_count": len(prev_3_gmv),
        "benchmark_present": benchmark is not None,
    }

    return FeatureResult(
        usable_history_months=usable_history_months,
        avg_monthly_gmv_3m=quantize_2(avg_monthly_gmv_3m) if avg_monthly_gmv_3m is not None else None,
        annual_gmv_12m=quantize_2(annual_gmv_12m),
        gmv_growth_3m_pct=gmv_growth_3m_pct,
        gmv_growth_12m_pct=gmv_growth_12m_pct,
        gmv_volatility_cv=gmv_volatility_cv,
        avg_orders_3m=avg_orders_3m,
        avg_unique_customers_3m=avg_unique_customers_3m,
        customer_efficiency_ratio=customer_efficiency_ratio,
        refund_delta_vs_category=refund_delta_vs_category,
        return_rate_delta_vs_category=return_rate_delta_vs_category,
        aov_position_vs_category_midpoint=aov_position_vs_category_midpoint,
        seasonality_pressure_score=seasonality_pressure_score,
        recent_gmv_drop_pct=recent_gmv_drop_pct,
        merchant_health_score=merchant_health_score,
        raw_feature_json=raw_feature_json,
    )
