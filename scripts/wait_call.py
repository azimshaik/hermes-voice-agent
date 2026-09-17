#!/usr/bin/env python3
"""Wait for a call to finish, then print transcript + summary and download the recording.

Usage:
    python3 scripts/wait_call.py <call_id> [max_seconds]

Saves the recording to samples/<call_id>.wav (and .m4a copy for easy sharing).
"""
import json
import os
import sys
import time
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


def get_call(call_id):
    key = load_env()["RETELL_API_KEY"]
    req = urllib.request.Request(
        BASE + "/v2/get-call/" + call_id,
        headers={"Authorization": f"Bearer {key}"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    samples = os.path.join(here, "..", "samples")
    call_id = sys.argv[1]
    max_wait = int(sys.argv[2]) if len(sys.argv) > 2 else 600

    deadline = time.time() + max_wait
    while time.time() < deadline:
        call = get_call(call_id)
        status = call.get("call_status")
        if status == "ended":
            break
        time.sleep(10)
    else:
        print("TIMEOUT: call still", call.get("call_status"))

    print("call_status:", call.get("call_status"))
    print("--- transcript ---")
    trans = call.get("transcript")
    if isinstance(trans, str):
        print(trans)
    else:
        print(json.dumps(trans, indent=1) if trans else "(none)")
    print("--- summary ---")
    print(call.get("call_summary") or "(none)")
    print("--- cost (dollars) ---")
    cost = call.get("call_cost") or {}
    if cost.get("combined_cost") is not None:
        print(f"${cost['combined_cost']/100:.4f} for {cost.get('total_duration_seconds', 0)}s")
    rec = call.get("recording_url")
    if rec:
        wav = os.path.join(samples, f"{call_id}.wav")
        urllib.request.urlretrieve(rec, wav)
        print("recording saved:", wav)
        m4a = os.path.join(samples, f"{call_id}.m4a")
        os.system(f'afconvert -f m4af -d aac "{wav}" "{m4a}" 2>/dev/null')
        if os.path.exists(m4a):
            print("shareable copy saved:", m4a)


if __name__ == "__main__":
    main()
