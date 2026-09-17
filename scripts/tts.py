#!/usr/bin/env python3
"""Text-to-speech in your cloned voice (ElevenLabs).

Usage:
    python3 scripts/tts.py "text to speak" [output.mp3]
    python3 scripts/tts.py --file script.txt [output.mp3]

Model: eleven_flash_v2_5 (fast/cheap). For Telugu or other languages later,
switch to eleven_multilingual_v2_5. Output default: samples/tts_output.mp3
"""
import json
import os
import sys
import urllib.request

BASE = "https://api.elevenlabs.io"
MODEL = os.environ.get("EL_TTS_MODEL", "eleven_flash_v2_5")


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
    key = env.get("ELEVENLABS_API_KEY", "")
    voice_id = env.get("EL_VOICE_ID", "")
    if not key:
        sys.exit("ELEVENLABS_API_KEY missing in .env")
    if not voice_id:
        sys.exit("EL_VOICE_ID missing in .env — run scripts/el_clone.py first")
    if len(sys.argv) < 2:
        sys.exit('Usage: tts.py "text" [output.mp3]  |  tts.py --file script.txt')

    here = os.path.dirname(os.path.abspath(__file__))
    out_default = os.path.join(here, "..", "samples", "tts_output.mp3")

    if sys.argv[1] == "--file":
        text = open(sys.argv[2]).read()
        out = sys.argv[3] if len(sys.argv) > 3 else out_default
    else:
        text = sys.argv[1]
        out = sys.argv[2] if len(sys.argv) > 2 else out_default

    payload = json.dumps(
        {
            "text": text,
            "model_id": MODEL,
            "voice_settings": {
                "stability": float(os.environ.get("EL_STABILITY", "0.45")),
                "similarity_boost": float(os.environ.get("EL_SIMILARITY", "0.8")),
                "style": float(os.environ.get("EL_STYLE", "0.2")),
                "speaker_boost": True,
            },
        }
    ).encode()
    req = urllib.request.Request(
        BASE + f"/v1/text-to-speech/{voice_id}",
        data=payload,
        headers={
            "xi-api-key": key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            audio = r.read()
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code}: {e.read().decode()[:500]}")

    open(out, "wb").write(audio)
    print(f"Saved {len(audio)/1024:.0f} KB → {out}")


if __name__ == "__main__":
    main()
