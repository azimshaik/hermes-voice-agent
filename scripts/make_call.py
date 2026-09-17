#!/usr/bin/env python3
"""Make an outbound phone call with the voice agent.

Usage:
    python3 scripts/make_call.py +12135551234                       # generic call
    python3 scripts/make_call.py +12135551234 "ask about Saturday table for 4"
    python3 scripts/make_call.py +12135551234 "TASK" AGENTID        # override agent

The task text is injected into the agent prompt so it opens the call
stating that purpose. Prints the call_id.
"""
import json
import os
import sys
import urllib.request

BASE = "https://api.retellai.com"


def load_env(path=".env"):
    env = {}
    if os.path.exists(path):
        for line in open(path):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip()
    return env


def main():
    env = load_env()
    key = env.get("RETELL_API_KEY", "")
    agent_id = env.get("AGENT_ID", "")
    from_number = env.get("FROM_NUMBER", "")
    if not key:
        sys.exit("RETELL_API_KEY missing in .env")
    if len(sys.argv) < 2:
        sys.exit("Usage: make_call.py +1XXXXXXXXXX [\"task text\"] [AGENT_ID]")

    to_number = sys.argv[1]
    task = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("agent_") else ""
    agent = sys.argv[3] if len(sys.argv) > 3 else agent_id
    if not from_number:
        sys.exit("FROM_NUMBER missing in .env (buy a number in the Retell dashboard first)")
    if not agent:
        sys.exit("AGENT_ID missing in .env")

    payload = {
        "from_number": from_number,
        "to_number": to_number,
        "override_agent_id": agent,
    }
    if task:
        payload["retell_llm_dynamic_variables"] = {"task": task}

    req = urllib.request.Request(
        BASE + "/v2/create-phone-call",
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            resp = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code}: {e.read().decode()[:500]}")

    print(json.dumps(resp, indent=2))
    print("\nWatch it live: https://dashboard.retellai.com (calls tab)")


if __name__ == "__main__":
    main()
