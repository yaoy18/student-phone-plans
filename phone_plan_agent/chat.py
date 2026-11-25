"""Chat with the phone plan advisor in your terminal.

    python chat.py                 # asks for your monthly budget first
    python chat.py --budget 30     # start with a $30/month budget

Commands while chatting: /save (write the last answer to comparison.md), /quit
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import anthropic

from plan_tools import PlanInputError, calculate_plan_cost

IDS_FILE = Path(__file__).with_name(".agent_ids.json")
SAVE_FILE = Path(__file__).with_name("comparison.md")

LOCAL_TOOLS = {"calculate_plan_cost": calculate_plan_cost}


def run_local_tool(name: str, tool_input: dict) -> tuple[str, bool]:
    """Returns (result text, is_error)."""
    fn = LOCAL_TOOLS.get(name)
    if fn is None:
        return f"Unknown tool: {name}", True
    try:
        return json.dumps(fn(tool_input), indent=2), False
    except PlanInputError as exc:
        return f"Invalid input: {exc}. Fix the input and call the tool again.", True


def describe_tool_call(name: str, tool_input: dict) -> str:
    if name == "web_search":
        return f"searching: {tool_input.get('query', '')}"
    if name == "web_fetch":
        return f"reading: {tool_input.get('url', '')}"
    if name == "calculate_plan_cost":
        return f"calculating costs for {len(tool_input.get('plans', []))} plans"
    return name


def ask_yes_no(question: str) -> bool:
    try:
        return input(f"{question} [y/N] ").strip().lower() in {"y", "yes"}
    except EOFError:
        return False


def run_turn(client: anthropic.Anthropic, session_id: str, text: str) -> str:
    """Send one message and stream the agent's work until it is done. Returns its reply."""
    reply_parts: list[str] = []
    # Open the stream before sending so no early events are missed.
    with client.beta.sessions.events.stream(session_id=session_id) as stream:
        client.beta.sessions.events.send(
            session_id=session_id,
            events=[{"type": "user.message", "content": [{"type": "text", "text": text}]}],
        )
        for event in stream:
            if event.type == "agent.message":
                for block in event.content:
                    if block.type == "text":
                        print(block.text, end="", flush=True)
                        reply_parts.append(block.text)

            elif event.type == "agent.tool_use":
                print(f"\n  · {describe_tool_call(event.name, event.input)}", flush=True)
                if event.evaluated_permission == "ask":
                    allowed = ask_yes_no(f"  Allow {event.name} with {json.dumps(event.input)}?")
                    client.beta.sessions.events.send(
                        session_id=session_id,
                        events=[{
                            "type": "user.tool_confirmation",
                            "tool_use_id": event.id,
                            "result": "allow" if allowed else "deny",
                        }],
                    )

            elif event.type == "agent.custom_tool_use":
                print(f"\n  · {describe_tool_call(event.name, event.input)}", flush=True)
                result, is_error = run_local_tool(event.name, event.input)
                client.beta.sessions.events.send(
                    session_id=session_id,
                    events=[{
                        "type": "user.custom_tool_result",
                        "custom_tool_use_id": event.id,
                        "content": [{"type": "text", "text": result}],
                        "is_error": is_error,
                    }],
                )

            elif event.type == "session.error":
                print(f"\n[session error] {event.error}", file=sys.stderr)

            elif event.type == "session.status_idle":
                # requires_action means it is waiting on a tool result or confirmation
                # we are sending; keep streaming until it is really done.
                if event.stop_reason.type != "requires_action":
                    break

            elif event.type == "session.status_terminated":
                print("\n[session ended]")
                break
    print()
    return "".join(reply_parts)


def read_budget(cli_budget: float | None) -> float:
    if cli_budget is not None:
        return cli_budget
    while True:
        raw = input("What's your monthly budget for a phone plan, in USD? $").strip().lstrip("$")
        try:
            value = float(raw)
            if value > 0:
                return value
        except ValueError:
            pass
        print("Please enter a number, like 25.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare US phone plans for international students.")
    parser.add_argument("--budget", type=float, help="Monthly budget in USD")
    args = parser.parse_args()

    if not IDS_FILE.exists():
        sys.exit("No agent yet. Run `python setup_agent.py` first.")
    ids = json.loads(IDS_FILE.read_text())

    client = anthropic.Anthropic()
    print("International Student Phone Plan Advisor (type /quit to exit, /save to save the last answer)\n")
    budget = read_budget(args.budget)

    session = client.beta.sessions.create(
        agent=ids["agent_id"],
        environment_id=ids["environment_id"],
        title="Phone plan comparison",
    )

    print("\nTell me a bit about yourself: campus city, how long you'll be here, home country,")
    print("data use, and whether your phone is unlocked. Or just press Enter and I'll ask.\n")
    intro = input("You: ").strip()
    first_message = f"My monthly budget is ${budget:.2f}. " + (
        intro or "Please ask me what you need to know."
    )

    print("\nAdvisor: ", end="")
    last_reply = run_turn(client, session.id, first_message)

    while True:
        try:
            text = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not text:
            continue
        if text == "/quit":
            break
        if text == "/save":
            SAVE_FILE.write_text(last_reply + "\n")
            print(f"Saved to {SAVE_FILE.name}")
            continue
        print("\nAdvisor: ", end="")
        last_reply = run_turn(client, session.id, text) or last_reply

    print("Good luck with the move!")


if __name__ == "__main__":
    main()
