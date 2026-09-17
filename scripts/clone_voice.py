#!/usr/bin/env python3
"""Clone your voice via Retell API (provider: elevenlabs).

Usage:
    python3 scripts/clone_voice.py <audio-file> [<audio-file> ...]

Reads RETELL_API_KEY from .env. Up to 25 files allowed; one clean 1-3 min
recording is enough. Prints the new voice_id when done.
"""
import json
import mimetypes
import os
import sys
import uuid

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


def multipart(fields, files):
    boundary = "----hermes" + uuid.uuid4().hex
    parts = []
    for k, v in fields.items():
        parts.append(
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode()
        )
    for path in files:
        fname = os.path.basename(path)
        ctype = mimetypes.guess_type(path)[0] or "audio/mpeg"
        with open(path, "rb") as f:
            data = f.read()
        parts.append(
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"files\"; filename=\"{fname}\"\r\nContent-Type: {ctype}\r\n\r\n".encode()
            + data
            + b"\r\n"
        )
    parts.append(f"--{boundary}--\r\n".encode())
    return b"".join(parts), boundary


def main():
    env = load_env()
    key = env.get("RETELL_API_KEY", "")
    if not key:
        sys.exit("RETELL_API_KEY missing in .env")
    if len(sys.argv) < 2:
        sys.exit("Usage: clone_voice.py <audio-file> [...]")

    import urllib.request

    files = sys.argv[1:]
    for f in files:
        if not os.path.exists(f):
            sys.exit(f"File not found: {f}")

    body, boundary = multipart(
        {"voice_name": os.environ.get("RETELL_CLONE_NAME", "My Clone"),
         "voice_provider": os.environ.get("RETELL_CLONE_PROVIDER", "elevenlabs")}, files
    )
    req = urllib.request.Request(
        BASE + "/clone-voice",
        data=body,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            resp = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code}: {e.read().decode()[:500]}")

    print(json.dumps(resp, indent=2))
    print("\nSave this voice_id in .env as needed (e.g. VOICE_ID=%s)" % resp.get("voice_id", ""))


if __name__ == "__main__":
    main()
