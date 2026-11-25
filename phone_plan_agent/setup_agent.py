"""One-time setup: create (or update) the agent and its environment.

Run once before chat.py, and again whenever you edit agent_config.py.
The IDs are saved to .agent_ids.json so chat sessions reuse the same agent.
"""

import json
from pathlib import Path

import anthropic

import agent_config as cfg

IDS_FILE = Path(__file__).with_name(".agent_ids.json")


def main() -> None:
    client = anthropic.Anthropic()
    ids = json.loads(IDS_FILE.read_text()) if IDS_FILE.exists() else {}

    if "environment_id" not in ids:
        env = client.beta.environments.create(
            name=cfg.ENVIRONMENT_NAME, config=cfg.ENVIRONMENT_CONFIG
        )
        ids["environment_id"] = env.id
        print(f"Created environment {env.id}")
    else:
        client.beta.environments.update(
            ids["environment_id"], config=cfg.ENVIRONMENT_CONFIG
        )
        print(f"Updated environment {ids['environment_id']}")

    agent_fields = dict(
        name=cfg.AGENT_NAME,
        model=cfg.MODEL,
        system=cfg.SYSTEM_PROMPT,
        tools=cfg.TOOLS,
    )
    if "agent_id" not in ids:
        agent = client.beta.agents.create(**agent_fields)
        print(f"Created agent {agent.id} (version {agent.version})")
    else:
        current = client.beta.agents.retrieve(ids["agent_id"])
        agent = client.beta.agents.update(
            ids["agent_id"], version=current.version, **agent_fields
        )
        print(f"Updated agent {agent.id} (now version {agent.version})")
    ids["agent_id"] = agent.id

    IDS_FILE.write_text(json.dumps(ids, indent=2) + "\n")
    print(f"Saved IDs to {IDS_FILE.name}. Next: python chat.py")


if __name__ == "__main__":
    main()
