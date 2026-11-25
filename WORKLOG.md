# Work log

Newest entries first. Each price update adds an entry here.

## 2026-11-24

### Prices now come from each carrier's own site
- Three agents read plan prices, fees and multi-line prices in Chrome from
  mintmobile.com, ultramobile.com, tello.com, t-mobile.com, prepaid.t-mobile.com,
  visible.com, verizon.com, usmobile.com, cricketwireless.com, att.com and
  fi.google.com. No sign-in, no checkout, nothing typed into forms.
- `plans.json` rebuilt: 33 plans, up from 20. The US Mobile blog and WhistleOut are
  no longer sources.
- Corrections found on the carrier sites:
  - US Mobile's monthly Unlimited Starter does not include international calls
    (it is a $3/mo add-on) and has 70GB at full speed, not unlimited.
  - T-Mobile no longer lists Essentials; its cheapest postpaid plan is T-Mix Saver
    ($45 with AutoPay, at most 2 lines).
  - Cricket and T-Mobile Prepaid charge $5 more in the first month.
  - Google Fi is half price for 12 months with your own phone (offer ends Dec 1).
  - Mint, Ultra, Tello, AT&T Prepaid and T-Mobile list monthly carrier fees
    separately; these are now counted.
  - AT&T, T-Mobile and Verizon postpaid charge $35 to $40 per line to activate.
- Not read, and why:
  - Verizon's postpaid monthly fees need a street address. They are not counted,
    and the plan says so.
  - AT&T's two plan pages disagree on the 4-line price ($25 or $30 a line). The
    higher regular price is used.
  - No carrier page states its SSN or credit-check rule. Prepaid plans are marked
    "No SSN needed"; postpaid plans and Google Fi are marked "May need an SSN".
  - Verizon's new Simplicity Plan is left out: its price without the switch
    discount is not printed.

### Site changes
- Compare: two to four plans, each with its own colour and letter badge; time span
  from 1 to 100 years; month read-out stays on screen after a tap.
- Find: "Do you have a US SSN?" input; a plan must fit the budget in year 2 as
  well; plans limited to one or two people, or with no price read for that number
  of people, are tagged and not recommended; only the six cheapest fits show until
  you open the rest.
- Costs: one-time fees (activation, connection) count toward year 1 and the amount
  due at the start; taxes use each state's average state and local wireless rate
  (Tax Foundation, July 2026).
- Added `student_plans_site/check.mjs`, which checks the data and the cost math.
- Compare chart draws smooth curves instead of stepped lines. The read-out under
  the chart still gives the exact total for the month you pick.
- A weekly price check is scheduled in the Claude desktop app (Mondays, 9 AM). It
  re-reads each carrier page in Chrome, updates `plans.json`, republishes and
  pushes. It had not yet run when this entry was written.

### Review panel
Three simulated reviewers (AI personas, not real users) scored the site twice.

| Reviewer | Round 1 | Round 2 |
|---|---|---|
| New international student, $30 budget | 5 | 7 |
| Mobile UX and accessibility | 6 | 7 |
| Consumer-advice editor | 5 | 6 |

Round 2 complaints, all addressed after scoring: the chart read-out vanished on
tap; plans were told apart by colour only; small links; fit was judged on the
promo year alone; some multi-line prices were guessed. The version with those
fixes has not been scored.

### Earlier the same day
- `2764f66` First version: terminal advisor agent (Claude Managed Agents) and a
  one-page site with budget and people inputs, recommendations, and advertised vs
  real yearly cost.
- `2883102` Compare page for two plans.
- `82a64d1` State tax selector, AT&T and Verizon plans, data and calling inputs,
  charts, carrier-neutral recommendations, phone-size plan list.
- `90b54ef` Up to four plans in Compare, SSN filter, second-round review fixes.
- Repository made public.

### Known limits
- Tax is a state average. City and county rates differ, and the federal surcharge
  is not included.
- Prices change only when `plans.json` is updated. The page shows the date they
  were last checked.
- The dark theme and desktop layout of the latest version were not looked at.
