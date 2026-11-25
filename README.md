# Student Phone Plans

Tools that help international students in the US compare cell phone plans.

- `student_plans_site/` — a one-page website. Pick a state, monthly budget, data
  needed, how often you call abroad and how many people are on the plan. It
  recommends plans and shows each plan's advertised cost next to its real yearly
  cost (promos ending, taxes, fees). Prices live in `plans.json`; run
  `python3 build.py` after editing them to rebuild `index.html`.
- `phone_plan_agent/` — a Claude agent that researches current prices and gives
  personal advice in a terminal chat. See its README.

Prices were last checked on 2026-11-24. Confirm at checkout.
