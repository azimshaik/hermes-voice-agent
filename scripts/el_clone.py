#!/usr/bin/env python3
"""Clone your voice on ElevenLabs (your own account) from a local sample.

Usage:
    python3 scripts/el_clone.py [sample_file]
Writes EL_VOICE_ID into .env when done.
"""
import json
import mimetypes
import os
import sys
import uuid
import urllib.request

BASE = "https://api.elevenlabs.io"


def load_env(path=".env"):
    env = {}
    if os.path.exists(path):
        for line in open(path):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip()
    return env


def multipart(fields, files):
    boundary = "----hermes" + uuid.uuid4().hex
    parts = []
    for k, v in fields.items():
        parts.append(
            f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
        )
    for path in files:
        fname = os.path.basename(path)
        ctype = mimetypes.guess_type(path)[0] or "audio/mpeg"
        data = open(path, "rb").read()
        parts.append(
            f'--{boundary}\r\nContent-Disposition: form-data; name="files"; filename="{fname}"\r\nContent-Type: {ctype}\r\n\r\n'.encode()
            + data
            + b"\r\n"
        )
    parts.append(f"--{boundary}--\r\n".encode())
    return b"".join(parts), boundary


def main():
    env = load_env()
    key = env.get("ELEVENLABS_API_KEY", "")
    if not key:
        sys.exit("ELEVENLABS_API_KEY missing in .env")
    here = os.path.dirname(os.path.abspath(__file__))
    sample = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "..", "samples", "my_voice.m4a")
    if not os.path.exists(sample):
        sys.exit(f"sample not found: {sample}")

    body, boundary = multipart({"name": os.environ.get("EL_CLONE_NAME", "My Clone")}, [sample])
    req = urllib.request.Request(
        BASE + "/v1/voices/add",
        data=body,
        headers={
            "xi-api-key": key,
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            resp = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code}: {e.read().decode()[:500]}")

    voice_id = resp.get("voice_id")
    print("voice_id:", voice_id)

    env_path = os.path.join(here, "..", ".env")
    lines = []
    added = False
    for line in open(env_path):
        if line.startswith("EL_VOICE_ID="):
            lines.append(f"EL_VOICE_ID={voice_id}\n")
            added = True
        else:
            lines.append(line)
    if not added:
        lines.append(f"EL_VOICE_ID={voice_id}\n")
    open(env_path, "w").writelines(lines)
    print("EL_VOICE_ID saved to .env")


if __name__ == "__main__":
    main()
