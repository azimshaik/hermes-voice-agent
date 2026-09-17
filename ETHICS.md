# Ethics, disclosure, and the law

This repo makes it trivial to put an AI voice on a phone line. That power has
rules. They're not optional, and they're not complicated.

## The one rule

**The agent introduces itself as your assistant. It never claims to be you,
and it never pretends to be human when asked.**

It can *sound* like you — that's the point of voice cloning. It must not *lie*
for you. The default prompt in this repo enforces this:

> "Hi, this is <name>'s personal assistant — he asked me to call."

That single sentence is the difference between a legitimate personal assistant
and an impersonation scheme.

## Why this matters legally

**AI disclosure laws.** Multiple US states now require disclosure when an AI
system interacts with a person (California's bot-disclosure statute, and
similar rules in other states), and disclosure requirements tighten every year.

**FCC + AI voices.** The FCC's 2024 declaratory ruling treats AI-generated
voices in calls as "artificial" under the TCPA. If a call is marketing or
telemarketing, consent rules apply hard. Personal, non-marketing inquiry calls
to businesses are a different category, but the direction of regulation is
one-way: assume you must disclose.

**Impersonation.** Presenting yourself as a specific human being to obtain
something — information, money, access — is fraud in most jurisdictions. An
agent that says "yes, it's really me" when asked is creating liability for
*you*, the accountable party.

**Recording consent.** Phone calls are recorded by the platform (that's how you
get transcripts). Some states are two-party-consent for call recording. The
agent's disclosure opener plus the assistant framing is what keeps you on the
right side of "informed."

## Why you cannot use your personal mobile number as caller ID

The single most common question. The answer is physics of the phone network,
not a vendor policy:

1. **Caller ID is an attestation, not a label.** Calls from a VoIP platform
   enter the phone network over SIP, and the originating carrier must *sign*
   them under **STIR/SHAKEN** — the FCC-mandated anti-spoofing framework. A
   carrier can only fully attest numbers it assigned to you.
2. **Your mobile number belongs to your mobile carrier.** Only they can sign
   calls presenting it. A VoIP platform presenting your mobile number would be
   spoofing — illegal under the Truth in Caller ID Act.
3. **It would backfire anyway.** Unauthenticated calls claiming to be your
   number get labeled "Spam Likely" or blocked outright by the receiving
   carrier. Your agent would be screened by exactly the businesses you want to
   reach.

Buy a dedicated number (~$2/mo). The caller-ID *name* (CNAM) can sometimes be
set to your name — that's a registry entry, not spoofing.

## Do

- Only call numbers you have a legitimate reason to call
- Only use **your own** voice for cloning (or one you have written consent to use)
- Keep the assistant disclosure in the prompt
- Honour do-not-call requests; if someone says "don't call again", end and record it
- Review transcripts of calls your agent makes — you are responsible for its conduct

## Don't

- Don't remove the disclosure to "make it sound more natural"
- Don't use the agent to impersonate a human for gain
- Don't use it for robocalling, mass outreach, or anything marketing without
  checking TCPA consent requirements with a lawyer
- Don't clone someone else's voice
- Don't call emergency services, or any number where an AI voice could cause harm

## A note on the "human" framing

The prompt in this repo lets the agent say *"I'm <name>'s personal assistant"*
without volunteering the word "AI" — the same way a human assistant answers a
business phone. The moment someone asks *"is this a robot / are you real?"*, the
prompt requires an honest answer and offers a callback instead. If you disagree
with that line, don't use this repo.
