#!/usr/bin/env python3
"""Create (or refresh) the prompt-based assistant agent with your cloned voice.

Reads: .env (RETELL_API_KEY, RETELL_VOICE_ID), prompts/assistant-agent.md
Writes: new agent_id back into .env AGENT_ID
"""
import json
import os
import sys
import urllib.request

BASE = "https://api.retellai.com"
MODEL = os.environ.get("RETELL_MODEL", "gemini-3.5-flash-lite")  # ~$0.023/min


def load_env(path=".env"):
    env = {}
    if os.path.exists(path):
        for line in open(path):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip()
    return env


def api(path, payload=None, method="POST"):
    key = load_env()["RETELL_API_KEY"]
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        BASE + path,
        data=data,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code} on {path}: {e.read().decode()[:400]}")


def main():
    env = load_env()
    here = os.path.dirname(os.path.abspath(__file__))
    prompt = open(os.path.join(here, "..", "prompts", "assistant-agent.md")).read().split("---", 1)[-1].strip()

    voice_id = env.get("RETELL_VOICE_ID", "")
    if not voice_id:
        sys.exit("RETELL_VOICE_ID missing in .env — run scripts/clone_voice.py first "
                 "and add its voice_id as RETELL_VOICE_ID")
    agent_name = env.get("RETELL_AGENT_NAME", "My Assistant")

    print(f"1) Creating LLM resource ({MODEL})...")
    llm = api("/create-retell-llm", {"model": MODEL, "general_prompt": prompt})
    llm_id = llm.get("llm_id")
    print("   llm_id:", llm_id)

    print(f"2) Creating agent '{agent_name}' with cloned voice...")
    agent = api(
        "/create-agent",
        {
            "agent_name": agent_name,
            "response_engine": {"type": "retell-llm", "llm_id": llm_id},
            "voice_id": voice_id,
            "language": "en-US",
            "end_call_after_silence_ms": 15000,
        },
    )
    agent_id = agent.get("agent_id")
    print("   agent_id:", agent_id)

    print("3) Updating .env AGENT_ID...")
    env_path = os.path.join(here, "..", ".env")
    lines = []
    for line in open(env_path):
        if line.startswith("AGENT_ID="):
            lines.append(f"AGENT_ID={agent_id}\n")
        else:
            lines.append(line)
    open(env_path, "w").writelines(lines)
    print("Done. New agent id saved to .env:", agent_id)


if __name__ == "__main__":
    main()
