# Student Phone Plans

Tools that help international students in the US compare cell phone plans.

- `student_plans_site/` — a one-page website with two views.
  - **Find a plan:** pick a state, monthly budget, data needed, how often you call
    abroad, whether you have an SSN, and how many people are on the plan. It
    recommends plans and shows each plan's advertised cost next to its real
    first-year cost (price changes, one-time fees, carrier fees, tax).
  - **Compare plans:** two to four plans side by side over 1 to 100 years.
- `phone_plan_agent/` — a Claude agent that researches current prices and gives
  personal advice in a terminal chat. See its README.
- `WORKLOG.md` — what changed and when, including every price update.

## Updating prices

Prices live in `student_plans_site/plans.json`, read from each carrier's own
website. Its `notes` field explains every field. After editing it:

```bash
cd student_plans_site
python3 build.py     # rebuilds index.html from template.html + plans.json
node check.mjs       # checks the data and the cost math
```

`index.html` is the built page; edit `template.html`, not `index.html`.

Prices were last checked on the date in `plans.json` (`checked`). Confirm at checkout.
