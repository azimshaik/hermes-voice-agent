#!/usr/bin/env python3
"""Fetch a finished call's transcript + summary from Retell.

Usage:
    python3 scripts/get_call.py <call_id>
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
    if not key:
        sys.exit("RETELL_API_KEY missing in .env")
    if len(sys.argv) < 2:
        sys.exit("Usage: get_call.py <call_id>")

    req = urllib.request.Request(
        BASE + "/v2/get-call/" + sys.argv[1],
        headers={"Authorization": f"Bearer {key}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            resp = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code}: {e.read().decode()[:500]}")

    # Print the useful bits, then raw JSON for the rest
    for k in ("call_id", "call_status", "agent_id", "to_number", "from_number",
              "call_summary", "call_cost", "disconnect_reason", "started_at",
              "ended_at", "recording_url", "transcript"):
        if k in resp:
            v = resp[k]
            if k == "transcript":
                v = json.dumps(v, indent=1)[:6000]
            print(f"--- {k} ---\n{v}\n")


if __name__ == "__main__":
    main()
