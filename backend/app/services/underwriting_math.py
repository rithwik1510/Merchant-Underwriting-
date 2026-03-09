from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from math import sqrt


TWO_PLACES = Decimal("0.01")
FOUR_PLACES = Decimal("0.0001")


def to_decimal(value: int | float | str | Decimal) -> Decimal:
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def quantize_2(value: Decimal) -> Decimal:
    return value.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)


def quantize_4(value: Decimal) -> Decimal:
    return value.quantize(FOUR_PLACES, rounding=ROUND_HALF_UP)


def safe_div(numerator: Decimal, denominator: Decimal) -> Decimal:
    if denominator == 0:
        return Decimal("0")
    return numerator / denominator


def average(values: list[Decimal]) -> Decimal:
    if not values:
        return Decimal("0")
    return sum(values) / Decimal(len(values))


def stddev(values: list[Decimal]) -> Decimal:
    if len(values) < 2:
        return Decimal("0")
    mean = average(values)
    variance = sum((value - mean) ** 2 for value in values) / Decimal(len(values))
    return Decimal(str(sqrt(float(variance))))


def clamp_decimal(value: Decimal, min_value: Decimal, max_value: Decimal) -> Decimal:
    return max(min_value, min(max_value, value))


def round_to_nearest(value: Decimal, step: Decimal) -> Decimal:
    if step == 0:
        return value
    multiplier = (value / step).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return multiplier * step
