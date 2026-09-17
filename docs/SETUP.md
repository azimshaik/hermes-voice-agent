# Setup — from zero to a working phone agent

Everything below was done for real on a live account; every quirk listed here
was hit and solved. Budget ~30 minutes.

## 0. What you're building

A dedicated phone number that answers/dials for you, speaks in your cloned
voice, follows per-call instructions from your assistant, and gives you the
transcript + recording afterwards.

## 1. Accounts

| Service | Why | Notes |
|---|---|---|
| **Retell AI** | The voice-agent platform (telephony + LLM + call control) | retellai.com — $10 free credit, no subscription |
| **ElevenLabs** *(optional)* | Voice cloning you control + offline script→audio | Free tier **cannot** clone via API — Starter (~$5/mo) required |
| **Hermes Agent** *(optional)* | Telegram control loop so you can trigger calls from your phone | see the [harness architecture repo](https://github.com/azimshaik/harness-architecture) |

Get your Retell **secret** API key (Settings → API Keys). There's also a
*publishable* key — that one is for browser clients. Use the secret one.

## 2. Record your voice sample

- 60–120 seconds of continuous, natural speech; single speaker; quiet room
- Phone Voice Memos is fine; avoid compressed chat-app audio (Opus) and
  recordings with music/background noise
- Speak in the tone and pace you want on calls — the clone copies delivery
- Save as `samples/my_voice.m4a` (any of m4a/mp3/wav)

## 3. Clone the voice

**Path A — Retell native (simplest, one API call):**

```bash
python3 scripts/clone_voice.py samples/my_voice.m4a
# → voice_id: custom_voice_xxxxxxxx
```

Retell supports cloning with several providers (`elevenlabs`, `cartesia`,
`minimax`, `fish_audio`, `platform`, `inworld`). ElevenLabs accepts up to 25
files; others take 1 (Inworld up to 3).

**Path B — ElevenLabs (more control; also enables offline TTS):**

```bash
python3 scripts/el_clone.py samples/my_voice.m4a     # needs ELEVENLABS_API_KEY
python3 scripts/tts.py "Any script you want read aloud" out.mp3
```

> **Quirk (hit live):** ElevenLabs free tier returns
> `payment_required / paid_plan_required` on `POST /v1/voices/add`.
> Cloning through their API needs the Starter plan.

## 4. Create the agent (LLM + agent in one step)

Edit `prompts/assistant-agent.md` first — at minimum set your name in the
disclosure line.

```bash
python3 scripts/create_prompt_agent.py
# creates an LLM resource (model from the script), then the agent bound to
# your cloned voice, then writes AGENT_ID into .env
```

**Choosing the brain (the only real cost dial):**

| Model family | Approx $/min | Use |
|---|---|---|
| `gemini-3.1-flash-lite`, `gemini-3.5-flash-lite` | ~$0.014–0.023 | Simple bookings/inquiries — **start here** |
| `gpt-4.1` | ~$0.045 | More robust on messy conversations |
| `gpt-4.1-nano`…`gpt-5.x-nano` | ~$0.003–0.01 | Cheapest; test carefully |
| `claude-4.5-haiku`, `claude-4.5/4.6/5-sonnet` | ~$0.025–0.08 | Stronger reasoning |

Available names (Retell): `gpt-4.1`, `gpt-4.1-mini`, `gpt-4.1-nano`, `gpt-5`,
`gpt-5-mini`, `gpt-5-nano`, `gpt-5.1`…`gpt-5.5`/`5.6-*`,
`claude-4.5-haiku`, `claude-4.5/4.6/5-sonnet`, `gemini-3.0-flash`,
`gemini-3.1-flash-lite`, `gemini-3.5-flash`, `gemini-3.5-flash-lite`,
`gemini-3.6-flash`. **Fast Tier costs 1.5× — leave it off** for personal use.

Change it later:

```bash
curl -X PATCH -H "Authorization: Bearer $RETELL_API_KEY" -H "Content-Type: application/json" \
  -d '{"model":"gemini-3.5-flash-lite"}' \
  https://api.retellai.com/update-retell-llm/<llm_id>
```

## 5. Get a phone number

**Do this in the dashboard, not the API.** The API's `POST /create-phone-number`
returns `403 No valid KYC` until you've completed identity verification, and
that flow is only triggerable by purchasing a number in the UI:

1. retellai.com → **Phone Numbers → Buy number** (area code of your choice)
2. Complete the KYC form (legal name, address, ID check — FCC requirement)
3. Put the assigned number in `.env` as `FROM_NUMBER=+1XXXXXXXXXX`

> Retell-provided numbers can only **dial US destinations**. For international
> calling, import a SIP trunk from Twilio/Telnyx (also possible KYC on their side).

## 6. First test call

```bash
python3 scripts/make_call.py "+1YOUR_MOBILE"      # generic: agent asks how it can help
```

**If your phone doesn't ring:** two usual suspects, both on the receiving side:

1. **"Silence Unknown Callers"** (iPhone: Settings → Phone) sends unrecognised
   numbers straight to voicemail with no ring. **Save the agent's number to
   contacts.**
2. Carrier spam analytics: brand-new numbers with no reputation sometimes get
   labelled "Spam Likely". Adding the contact + a few answered calls fixes it.

If calls show `ongoing` forever with no ring, check voicemail — the agent will
have left a message (that's working as designed).

## 7. Calls with instructions (the actual magic)

```bash
python3 scripts/make_call.py "+12135551234" "ask if they have a table for four on Saturday around 7"
```

The task text is injected as a dynamic variable (`retell_llm_dynamic_variables`)
into the agent's prompt, so the agent **opens the call stating that purpose**
instead of vaguely asking how it can help.

Then:

```bash
python3 scripts/wait_call.py <call_id>   # blocks until the call ends
```

You get the full transcript, the recording (`samples/<call_id>.m4a`), and the
cost of that call.

## 8. Wire it to Telegram (Hermes)

With Hermes connected to Telegram, you say *"call the salon, ask about
Saturday"* and Hermes runs the scripts for you — including waiting for the call
to finish and summarising the result back to you. The agent harness choices and
setup patterns are documented in the
[harness architecture repo](https://github.com/azimshaik/harness-architecture).

Keep the calls themselves in the same repository directory as `.env` so the
scripts pick up the keys.

## Troubleshooting the API paths (they're inconsistent)

Retell's API mixes versioned and unversioned routes. Verified working (spec
revision 2026-09):

| Action | Method + path |
|---|---|
| Clone voice | `POST /clone-voice` |
| List/create agents | `GET /list-agents`, `POST /create-agent` |
| Create LLM | `POST /create-retell-llm` |
| Update LLM | `PATCH /update-retell-llm/{llm_id}` |
| Place call | `POST /v2/create-phone-call` |
| Get call | `GET /v2/get-call/{call_id}` |
| List numbers | `GET /list-phone-numbers` |
| Buy number | `POST /create-phone-number` *(KYC-gated; use the dashboard)* |

If you get `Cannot POST /something`, check the noun — some routes are `/v2/`,
some aren't.

## Cost control checklist

- Use a Flash-Lite-class brain (~2¢/min instead of 7–8¢/min)
- Leave Fast Tier off (it's 1.5×)
- Keep the prompt tight — long prompts = more tokens per turn
- The $0.04/min cloned voice and ~$0.07–0.09/min platform+telephony are fixed;
  the LLM is the only meaningful dial
- `wait_call.py` prints per-call cost so you can see drift immediately
