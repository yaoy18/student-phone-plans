import pytest
from plan_tools import PlanInputError, calculate_plan_cost

MINT_12 = {"name": "Mint 12-mo", "billing": "prepaid_bundle", "bundle_price": 180, "bundle_months": 12}
BIG = {"name": "Big carrier", "billing": "monthly", "monthly_price": 40, "promo_months": 3,
       "promo_monthly_price": 25, "one_time_fees": 35, "monthly_extras": 5, "refundable_deposit": 100}

def test_ranking_budget_and_annual():
    out = calculate_plan_cost({"stay_months": 9, "monthly_budget_usd": 30, "plans": [BIG, MINT_12]})
    mint, big = out["ranked_cheapest_first"]
    assert mint["name"] == "Mint 12-mo" and mint["total_usd"] == 180 and mint["prepaid_months_unused"] == 3
    assert mint["predicted_annual_usd"] == 180 and mint["monthly_cost_usd"] == 15
    # 3*25 + 6*40 + 35 + 9*5 = 395
    assert big["total_usd"] == 395 and big["refundable_deposit_usd"] == 100
    # 12-month: 3*25 + 9*40 + 35 + 60 = 530
    assert big["predicted_annual_usd"] == 530
    assert out["plans_within_budget"] == ["Mint 12-mo"] and big["within_budget"] is False

def test_default_stay_is_12():
    assert calculate_plan_cost({"plans": [MINT_12]})["stay_months"] == 12

@pytest.mark.parametrize("bad", [
    {"plans": []},
    {"stay_months": 0, "plans": [MINT_12]},
    {"plans": [{"name": "x", "billing": "monthly"}]},
    {"plans": [{"name": "x", "billing": "weekly", "monthly_price": 1}]},
    {"plans": [{"name": "x", "billing": "monthly", "monthly_price": -5}]},
    {"monthly_budget_usd": "cheap", "plans": [MINT_12]},
])
def test_rejects_bad_input(bad):
    with pytest.raises(PlanInputError):
        calculate_plan_cost(bad)
