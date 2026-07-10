"""
Significance + forecasting for Hookflash A/B Results Analysis.

Pure standard-library (math only) so it runs anywhere. Feed it the raw counts
parsed from the Tapa workbook; it returns conversion rates, uplift, a
two-proportion z-test verdict, and a predicted end date.

Usage:
    from stats import compare_variations, predicted_end_date
    res = compare_variations(control={"users":5162,"conversions":1859},
                             variation={"users":5105,"conversions":1831})
    # res -> dict with rates, uplift, z, p_value, confidence, significant
"""
from __future__ import annotations
import math
from dataclasses import dataclass, asdict


def _norm_cdf(x: float) -> float:
    """Standard normal CDF via erf (no scipy dependency)."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _norm_ppf(p: float) -> float:
    """Inverse normal CDF (Acklam's rational approximation). 0<p<1."""
    if not 0.0 < p < 1.0:
        raise ValueError("p must be in (0,1)")
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00]
    plow, phigh = 0.02425, 1 - 0.02425
    if p < plow:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    if p > phigh:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    q = p - 0.5
    r = q * q
    return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)


@dataclass
class VariationResult:
    name: str
    users: int
    conversions: int
    rate: float          # conversion rate (0..1)
    uplift: float | None # vs control; None for control itself


def rate(users: int, conversions: int) -> float:
    return conversions / users if users else 0.0


def two_proportion_z(control: dict, variation: dict) -> dict:
    """Two-proportion z-test on conversion rate. Returns z, p_value (two-tailed),
    confidence (1 - p), and the pooled standard error."""
    n1, x1 = control["users"], control["conversions"]
    n2, x2 = variation["users"], variation["conversions"]
    p1, p2 = rate(n1, x1), rate(n2, x2)
    if n1 == 0 or n2 == 0:
        return {"z": 0.0, "p_value": 1.0, "confidence": 0.0, "se": 0.0}
    p_pool = (x1 + x2) / (n1 + n2)
    se = math.sqrt(p_pool * (1 - p_pool) * (1 / n1 + 1 / n2))
    z = (p2 - p1) / se if se else 0.0
    p_value = 2 * (1 - _norm_cdf(abs(z)))
    return {"z": z, "p_value": p_value, "confidence": 1 - p_value, "se": se}


def compare_variations(control: dict, variation: dict, threshold: float = 0.95,
                        min_conversions: int = 25) -> dict:
    """Compare one variation against control for a single KPI."""
    test = two_proportion_z(control, variation)
    p1, p2 = rate(**{"users": control["users"], "conversions": control["conversions"]}), \
             rate(**{"users": variation["users"], "conversions": variation["conversions"]})
    uplift = (p2 / p1 - 1) if p1 else None
    underpowered = (control["conversions"] < min_conversions or
                    variation["conversions"] < min_conversions)
    return {
        "control_rate": p1,
        "variation_rate": p2,
        "uplift": uplift,
        **test,
        "significant": (test["confidence"] >= threshold) and not underpowered,
        "underpowered": underpowered,
        "threshold": threshold,
    }


def required_sample_size(baseline_rate: float, mde: float,
                         power: float = 0.80, alpha: float = 0.05) -> int:
    """Users per arm to detect a relative `mde` change at `power`/`alpha`
    (two-sided). Returns per-arm sample size."""
    p1 = baseline_rate
    p2 = baseline_rate * (1 + mde)
    if not 0 < p1 < 1 or not 0 < p2 < 1:
        return 0
    z_alpha = _norm_ppf(1 - alpha / 2)
    z_beta = _norm_ppf(power)
    pbar = (p1 + p2) / 2
    num = (z_alpha * math.sqrt(2 * pbar * (1 - pbar)) +
           z_beta * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
    return math.ceil(num / ((p2 - p1) ** 2))


def predicted_end_date(baseline_rate: float, users_so_far: int, days_elapsed: int,
                       mde: float, power: float = 0.80, alpha: float = 0.05) -> dict:
    """Days remaining until each arm reaches the required sample size, at the
    current daily user rate. Returns per-arm target, users_so_far, days_remaining."""
    need_per_arm = required_sample_size(baseline_rate, mde, power, alpha)
    daily = (users_so_far / days_elapsed) if days_elapsed else 0
    remaining_users = max(0, need_per_arm - users_so_far)
    days_remaining = math.ceil(remaining_users / daily) if daily else None
    return {
        "required_per_arm": need_per_arm,
        "users_so_far": users_so_far,
        "daily_users": round(daily, 1),
        "days_remaining": days_remaining,
        "viable": need_per_arm > 0 and daily > 0,
    }


if __name__ == "__main__":
    # Smoke test with the numbers from the example panel.
    demo = compare_variations(
        {"users": 5162, "conversions": 1859},   # Original search reach
        {"users": 5105, "conversions": 1831},   # Variation 1
    )
    for k, v in demo.items():
        print(f"{k:16} {v}")
