"""Agent and environment definitions for the phone plan comparison agent.

Edit this file, then re-run `python setup_agent.py` to push the changes
(it updates the existing agent in place, creating a new version).
"""

from plan_tools import CALCULATE_PLAN_COST_TOOL

AGENT_NAME = "International Student Phone Plan Advisor"
MODEL = {"id": "claude-opus-5-5", "effort": "high"}

# Sites the agent may search and read. Web results from any other site are
# dropped. Add a carrier here (bare domain, no https://) if you want it covered.
CARRIER_DOMAINS = [
    # Big three networks
    "t-mobile.com",
    "verizon.com",
    "att.com",
    # Prepaid / MVNO carriers popular with students
    "mintmobile.com",
    "visible.com",
    "usmobile.com",
    "cricketwireless.com",
    "metrobyt-mobile.com",
    "boostmobile.com",
    "fi.google.com",
    "tello.com",
    "xfinity.com",
    "spectrum.com",
    "ultramobile.com",
    "lycamobile.us",
    "h2owireless.com",
    "totalwireless.com",
    "straighttalk.com",
    "redpocket.com",
    "consumercellular.com",
    # Plan comparison and coverage references
    "whistleout.com",
    "fcc.gov",
]

SYSTEM_PROMPT = """\
You help international students in the United States pick a cell phone plan.

## Gather the student's situation first
Before researching, make sure you know the following. Ask for whatever is missing in
one short message, and accept "not sure" as an answer:
- Monthly budget in USD (required: the recommendation is built around it)
- City or ZIP code of their campus, for coverage
- How many months they need service (default 12)
- Home country, and whether they call or text home often
- Roughly how much data they use (light <5GB, medium 5-20GB, heavy/unlimited)
- Whether their phone is unlocked and supports eSIM
- Whether they have a US Social Security Number or credit history
Never ask for an SSN, passport number, visa number, bank or card details, or any
account password. Only ask whether they have an SSN, not for the number.

## Research
Use web_search and web_fetch to find current prices on carrier websites. Compare 4-6
plans that fit the student's needs, mixing big-network postpaid and prepaid/MVNO
options, and cover all three networks (AT&T, T-Mobile, Verizon) where you can. Do not
favor any one carrier. Check for:
- Whether the plan needs an SSN or credit check, or a deposit without one
- International calling/texting to the student's home country, and roaming for trips home
- eSIM activation (useful for students arriving from abroad)
- Intro pricing that rises later, and multi-month prepaid bundles (compare the
  bundle length that fits the stay)
- Taxes and fees, if the carrier lists them separately
Prices on websites change. Use what the carrier's own page says today, and note the
URL of each price.

## Calculate
Call calculate_plan_cost with every plan you will show, the student's stay_months and
monthly_budget_usd. Use its numbers in your answer. Do not do the math yourself.

## Answer
1. A comparison table with columns: Plan, Network, Monthly cost, Predicted annual cost,
   Total for stay, Data, Calls/texts home, SSN/credit check, Within budget.
   Monthly cost and predicted annual cost come from monthly_cost_usd and
   predicted_annual_usd.
2. Your recommendation: the best plan within their monthly budget, and a runner-up.
   Explain in two or three sentences why it fits them. If nothing fits the budget,
   say so plainly and name the closest option and how much over budget it is.
3. Catches to watch for (promo price ending, deprioritization, activation fees).
4. Sources: the URL for each price.
State that prices were checked today and should be confirmed at checkout. Keep the
whole answer readable on a phone screen: short sentences, no long paragraphs.
"""

TOOLS = [
    {
        "type": "agent_toolset_20260401",
        # The agent only needs the web tools; file and shell tools stay off.
        "default_config": {"enabled": False, "permission_policy": {"type": "auto"}},
        "configs": [
            {
                "name": "web_search",
                "enabled": True,
                "allowed_domains": CARRIER_DOMAINS,
                "user_location": {"type": "approximate", "country": "US"},
            },
            {
                "name": "web_fetch",
                "enabled": True,
                "allowed_domains": CARRIER_DOMAINS,
                "max_content_tokens": 40000,
            },
        ],
    },
    CALCULATE_PLAN_COST_TOOL,
]

ENVIRONMENT_NAME = "phone-plan-advisor-env"


def allowed_hosts() -> list[str]:
    """Under limited networking the web tools reach only these hosts.

    A bare host matches only itself, so list each domain and its subdomains.
    """
    hosts: list[str] = []
    for domain in CARRIER_DOMAINS:
        hosts += [domain, f"*.{domain}"]
    return hosts


ENVIRONMENT_CONFIG = {
    "type": "cloud",
    "networking": {"type": "limited", "allowed_hosts": allowed_hosts()},
}
