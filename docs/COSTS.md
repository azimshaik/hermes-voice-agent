# Costs — verified, not guessed

All platform rates below were read off the vendors' live pricing pages
(September 2026), and the "measured" rows are real calls placed with the
scripts in this repo.

## Per-minute, all-in

| Component | Rate | Notes |
|---|---|---|
| Retell platform | **$0/mo** | pure pay-as-you-go; $10 free credit on signup |
| Retell voice engine | ~$0.055–0.09/min | infrastructure + speech pipeline |
| Telephony (US, in/out) | ~$0.015–0.025/min | US destinations on Retell numbers |
| Cloned voice (ElevenLabs engine) | **$0.04/min** | this is the "sounds like you" cost |
| Retell's own voices | $0.015/min | if you don't need your own voice |
| LLM brain | $0.003–0.08/min | the only real dial — see below |
| Phone number | ~$2/mo | + one-time KYC; custom/imported numbers differ |

**Realistic total: ~$0.13–0.25 per minute.**

## Measured on real calls (this repo's scripts)

| Call | Duration | Cost |
|---|---|---|
| Test call, generic greeting | 40 s | $0.12 (~$0.18/min) |
| Voicemail + screening service | 71 s | $0.17 (~$0.15/min) |
| Voicemail then live conversation (gpt-4.1) | 83 s | $0.20 (~$0.14/min) |
| Personal-check call, Flash-Lite brain | 69 s | $0.15 (~$0.13/min) |

Real-world example: **a 4-minute appointment-booking call ≈ $0.55–0.75**
with a cheap brain, ≈$0.30 more with a GPT-class brain.

## The LLM dial (where 80% of the variance is)

| Class | Models | $/min |
|---|---|---|
| Nano / Lite | `gpt-4.1-nano`, `gpt-5-nano`, `gemini-3.1-flash-lite`, `gemini-3.5-flash-lite` | ~$0.003–0.023 |
| Mid | `gpt-4.1`, `gemini-3.6-flash`, `claude-4.5-haiku` | ~$0.025–0.069 |
| Strong | `gpt-5.x`, `claude-4.5/4.6-sonnet` | ~$0.08+ |

- Fast Tier = **1.5×** the model's rate. Leave it off.
- Voice quality ≠ brain cost. The cloned voice is $0.04/min regardless.

## ElevenLabs (only if you clone/tts there)

| Plan | Price | Credits | Notes |
|---|---|---|---|
| Free | $0 | 10,000 | **cannot clone via API** (paid_plan_required) |
| Starter | ~$5–6/mo | 30,000 | instant voice cloning + API access |
| Creator | $22/mo | 121,000 | pro cloning, more credits |

Offline script→audio (no phone call) runs on those credits: cheap for a few
minutes of narration per month.

## Monthly reality check

| Usage | Est. monthly |
|---|---|
| Light (10 calls × 3 min) | $4–6 |
| Normal (30 calls × 4 min) | $15–23 |
| Heavy (100 calls × 4 min) | $70–100 |
| + ElevenLabs Starter (optional) | +$5 |
| + phone number | +$2 |

No subscription on the calling platform means the off-switch is free: stop
calling, stop paying.

## Things that aren't costs but feel like them

- **Numbers you can't use**: KYC rejections waste time, not money
- **Retries**: a call the receiving carrier silently screens still bills
  (you're paying for connection attempts and any voicemail the agent leaves) —
  which is why `wait_call.py` prints per-call cost
- **Prompt bloat**: every extra paragraph in the system prompt is billed tokens
  on every turn
