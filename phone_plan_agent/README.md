# International Student Phone Plan Advisor

A Claude agent that compares US cell phone plans for international students. It
asks for your monthly budget and situation, looks up today's prices on carrier
websites, and returns a table with each plan's
monthly cost, predicted annual cost, total for your stay, and whether it fits
your budget, plus a recommendation.

Built on Claude Managed Agents (beta): Anthropic runs the agent loop and the web
tools. The cost math runs on your machine in `plan_tools.py`.

## Setup

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...      # or sign in with `ant auth login`
python setup_agent.py                   # once; re-run after editing agent_config.py
```

## Use

```bash
python chat.py --budget 30
```

While chatting: `/save` writes the last answer to `comparison.md`, `/quit` exits.

## Files

| File | What it does |
|---|---|
| `agent_config.py` | System prompt, model, allowed carrier websites, tools |
| `plan_tools.py` | `calculate_plan_cost` tool: monthly, annual, stay total, budget check |
| `setup_agent.py` | Creates or updates the agent and environment, saves IDs to `.agent_ids.json` |
| `chat.py` | Terminal chat; runs the local tool and streams the agent's replies |
| `test_plan_tools.py` | Tests for the cost math (`python -m pytest`) |

## Notes

- The agent can only search and read the sites in `CARRIER_DOMAINS`. Add one there
  and re-run `setup_agent.py` to cover another carrier.
- It never asks for an SSN, passport or payment details. It only asks whether you have an SSN.
- Each chat is a billed session (tokens plus session runtime), and session history
  is kept by Anthropic until deleted.
- Prices come from carrier pages on the day you run it. Confirm at checkout.
