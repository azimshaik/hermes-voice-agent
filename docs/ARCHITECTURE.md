# Architecture

## The loop

```
You (Telegram, phone, wherever)
      │  "call the salon, ask about Saturday"
      ▼
Hermes Agent  (your machine, holds the API keys)
      │  make_call.py <number> "<task>"
      │  → POST /v2/create-phone-call
      │     {from_number, to_number, override_agent_id,
      │      retell_llm_dynamic_variables: {task}}
      ▼
Retell AI  ──►  PSTN/SIP  ──►  the human who answers
      ▲                              │
      │  transcript, recording,      │  the conversation
      │  call_cost, disconnect       ▼
      │                        your cloned voice
      │                        (ElevenLabs engine)
      └────────────► wait_call.py → summary back to you
```

## Components and why each exists

| Piece | Role | Swap-out options |
|---|---|---|
| **Telephony + call control** | Dials, handles media, voicemail detection, transfers, IVR digits | Retell, Vapi, Bland, or DIY with Twilio Media Streams |
| **Voice** | Speaks as you | ElevenLabs / Cartesia / MiniMax / platform voices |
| **Brain** | Decides what to say, follows the task | Any hosted LLM Retell supports, or your own via a custom LLM endpoint |
| **Assistant layer** | Turns your chat message into a call, keeps keys, reports back | Hermes Agent — any script runner works |

The scripts here are deliberately **stdlib-only Python**: no SDKs, no pip
installs, no lock-in. They read `.env`, call the REST API, print JSON.

## Per-call instruction injection (the key mechanism)

Retell lets you pass **dynamic variables** at call creation:

```json
{
  "from_number": "+1XXXXXXXXXX",
  "to_number": "+1XXXXXXXXXX",
  "override_agent_id": "agent_xxx",
  "retell_llm_dynamic_variables": { "task": "ask if they have a table Saturday for four" }
}
```

The agent prompt contains:

```
## Purpose of THIS call
Your principal's instruction for this call: "{{task}}"
Open the call by stating that purpose naturally...
```

So the same agent handles *any* errand without editing prompts — the task is
per-call data, not configuration. Without this, the agent opens with a generic
"how can I help you?" which is the wrong first impression on an outbound call.

## Call lifecycle as the scripts see it

| Script | Does | API |
|---|---|---|
| `clone_voice.py` | uploads sample → voice_id | `POST /clone-voice` (multipart) |
| `create_prompt_agent.py` | creates LLM (model + prompt) → creates agent bound to voice → writes AGENT_ID to `.env` | `POST /create-retell-llm`, `POST /create-agent` |
| `make_call.py` | places the call with the task | `POST /v2/create-phone-call` |
| `wait_call.py` | polls until `call_status == "ended"`, then dumps transcript/summary/cost and downloads the recording | `GET /v2/get-call/{id}` |
| `get_call.py` | one-shot fetch of a call you already know the id for | same |
| `tts.py` | offline text→audio in your voice (no call) | `POST /v1/text-to-speech/{voice_id}` |

## Latency and behaviour notes (learned live)

- **Agent voice quality is a model+settings decision.** Lower `stability` =
  more expressive; higher `style` = more punch; `speaker_boost: true` helps on
  phone lines. Flash models sound flatter than v3-class models.
- **Screening services/Voicemail:** the agent should leave one concise message
  (who it represents, the reason, callback request) — handled by the prompt.
- **People talk over it:** with barge-in enabled the agent recovers, but expect
  it to occasionally re-ask a question. The end-of-call checklist in the prompt
  exists because a bare "okay" is not an answer — an early version tried to hang
  up after hearing "okay" without ever getting the answer.
- **Hold music / IVRs:** the prompt enforces a ~3-minute hold limit and the
  agent can press digits if you enable the keypad tool.
- **Transcripts are speech-to-text:** expect typos; read for meaning, not
  spelling. Add a call-analysis/summary config in the dashboard if you want
  structured summaries per call.

## Extending it

- **Calendar tool:** add a Retell custom function that hits Google Calendar —
  the agent can then check real availability mid-call and book
- **Webhooks:** Retell posts `call_ended` / `call_analyzed` events; point them
  at a small endpoint to auto-deliver summaries to Telegram
- **Batch/queue:** `create-phone-call` per target, rate-limit politely, and
  review transcripts — mass outbound is an ethics+law problem, not a feature
- **Other channels:** the same pattern works for SMS (Retell send-SMS tool) and
  web calls (no telephony cost)
