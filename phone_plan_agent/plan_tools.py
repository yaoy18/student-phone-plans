"""Local (client-side) tool the agent calls to total up plan costs.

Prices come from the agent's web research; this module only does the math so
totals are deterministic instead of being estimated by the model.
"""

from __future__ import annotations

import math
from typing import Any

CALCULATE_PLAN_COST_TOOL = {
    "type": "custom",
    "name": "calculate_plan_cost",
    "description": (
        "Compute each plan's monthly cost, predicted annual (12-month) cost, total "
        "over the student's stay, and whether it fits the student's monthly budget. "
        "Call this after researching prices, with every "
        "plan you intend to show the student, so the comparison table uses exact "
        "numbers. Handles monthly plans, prepaid multi-month bundles (e.g. 3/6/12 "
        "month packages), intro/promo pricing, one-time fees, monthly add-ons such "
        "as taxes or international calling packs, and refundable deposits."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "stay_months": {
                "type": "integer",
                "minimum": 1,
                "maximum": 120,
                "description": "How many months the student needs service. Defaults to 12.",
            },
            "monthly_budget_usd": {
                "type": "number",
                "minimum": 0,
                "description": "The student's monthly budget in USD. Each plan is checked against it.",
            },
            "plans": {
                "type": "array",
                "minItems": 1,
                "maxItems": 15,
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Carrier and plan name."},
                        "billing": {
                            "type": "string",
                            "enum": ["monthly", "prepaid_bundle"],
                            "description": "monthly = billed each month; prepaid_bundle = pay up front for bundle_months.",
                        },
                        "monthly_price": {
                            "type": "number",
                            "minimum": 0,
                            "description": "Regular monthly price in USD (billing=monthly).",
                        },
                        "bundle_price": {
                            "type": "number",
                            "minimum": 0,
                            "description": "Price of one bundle in USD (billing=prepaid_bundle).",
                        },
                        "bundle_months": {
                            "type": "integer",
                            "minimum": 1,
                            "description": "Months covered by one bundle (billing=prepaid_bundle).",
                        },
                        "promo_months": {
                            "type": "integer",
                            "minimum": 0,
                            "description": "Months at the promo price before the regular monthly price applies (billing=monthly).",
                        },
                        "promo_monthly_price": {
                            "type": "number",
                            "minimum": 0,
                            "description": "Monthly price during the promo period (billing=monthly).",
                        },
                        "one_time_fees": {
                            "type": "number",
                            "minimum": 0,
                            "description": "Activation, SIM/eSIM, shipping, or similar one-time costs in USD.",
                        },
                        "monthly_extras": {
                            "type": "number",
                            "minimum": 0,
                            "description": "Recurring extras per month in USD: taxes/fees estimate, international calling add-on, etc.",
                        },
                        "refundable_deposit": {
                            "type": "number",
                            "minimum": 0,
                            "description": "Security deposit (e.g. postpaid without SSN/credit history). Reported separately, not added to total.",
                        },
                    },
                    "required": ["name", "billing"],
                },
            },
        },
        "required": ["plans"],
    },
}


class PlanInputError(ValueError):
    pass


def _num(plan: dict[str, Any], key: str, default: float = 0.0) -> float:
    value = plan.get(key, default)
    if value is None:
        return default
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise PlanInputError(f"{plan.get('name', '?')}: '{key}' must be a number")
    if value < 0:
        raise PlanInputError(f"{plan.get('name', '?')}: '{key}' cannot be negative")
    return float(value)


def cost_for_plan(plan: dict[str, Any], stay_months: int) -> dict[str, Any]:
    name = plan.get("name")
    if not isinstance(name, str) or not name.strip():
        raise PlanInputError("every plan needs a non-empty 'name'")
    billing = plan.get("billing")
    one_time = _num(plan, "one_time_fees")
    extras = _num(plan, "monthly_extras")
    deposit = _num(plan, "refundable_deposit")
    unused_months = 0

    if billing == "monthly":
        if "monthly_price" not in plan:
            raise PlanInputError(f"{name}: monthly plans need 'monthly_price'")
        regular = _num(plan, "monthly_price")
        promo_months = int(_num(plan, "promo_months"))
        promo_price = _num(plan, "promo_monthly_price", regular)
        promo_used = min(promo_months, stay_months)
        service = promo_used * promo_price + (stay_months - promo_used) * regular
    elif billing == "prepaid_bundle":
        if "bundle_price" not in plan or "bundle_months" not in plan:
            raise PlanInputError(f"{name}: prepaid bundles need 'bundle_price' and 'bundle_months'")
        bundle_price = _num(plan, "bundle_price")
        bundle_months = int(_num(plan, "bundle_months"))
        if bundle_months < 1:
            raise PlanInputError(f"{name}: 'bundle_months' must be at least 1")
        bundles = math.ceil(stay_months / bundle_months)
        service = bundles * bundle_price
        unused_months = bundles * bundle_months - stay_months
    else:
        raise PlanInputError(f"{name}: 'billing' must be 'monthly' or 'prepaid_bundle'")

    total = service + one_time + extras * stay_months
    return {
        "name": name,
        "total_usd": round(total, 2),
        "effective_monthly_usd": round(total / stay_months, 2),
        "service_usd": round(service, 2),
        "one_time_fees_usd": round(one_time, 2),
        "extras_usd": round(extras * stay_months, 2),
        "refundable_deposit_usd": round(deposit, 2),
        "prepaid_months_unused": unused_months,
    }


def calculate_plan_cost(tool_input: dict[str, Any]) -> dict[str, Any]:
    stay = tool_input.get("stay_months", 12)
    if isinstance(stay, bool) or not isinstance(stay, int) or not 1 <= stay <= 120:
        raise PlanInputError("'stay_months' must be an integer from 1 to 120")
    budget = tool_input.get("monthly_budget_usd")
    if budget is not None and (isinstance(budget, bool) or not isinstance(budget, (int, float)) or budget < 0):
        raise PlanInputError("'monthly_budget_usd' must be a non-negative number")
    plans = tool_input.get("plans")
    if not isinstance(plans, list) or not plans:
        raise PlanInputError("'plans' must be a non-empty list")
    if len(plans) > 15:
        raise PlanInputError("at most 15 plans per call")

    results = []
    for plan in plans:
        r = cost_for_plan(plan, stay)
        annual = cost_for_plan(plan, 12)
        r["predicted_annual_usd"] = annual["total_usd"]
        # Average monthly cost in a typical year, after one-time fees are spread out.
        r["monthly_cost_usd"] = annual["effective_monthly_usd"]
        if budget is not None:
            r["within_budget"] = r["effective_monthly_usd"] <= budget
            r["monthly_headroom_usd"] = round(budget - r["effective_monthly_usd"], 2)
        results.append(r)

    results.sort(key=lambda r: r["total_usd"])
    cheapest = results[0]["total_usd"]
    for r in results:
        r["more_than_cheapest_usd"] = round(r["total_usd"] - cheapest, 2)

    out: dict[str, Any] = {"stay_months": stay, "ranked_cheapest_first": results}
    if budget is not None:
        out["monthly_budget_usd"] = budget
        out["plans_within_budget"] = [r["name"] for r in results if r["within_budget"]]
    return out
