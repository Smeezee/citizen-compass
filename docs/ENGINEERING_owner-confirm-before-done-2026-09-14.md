# HARD RULE — Owner confirm before DONE (2026-09-14)

**Trigger:** Engineering reported webhook deep links “WORKED” when Owner still had no copyable URL. That class of error is **not acceptable**.

## Rule
For any step that **only Owner can see or complete** (host-panel fields, webhook URL/key, logins, payments, GUI-only copy, “paste into settings”):

1. **Never** mark DONE / WORKED / COMPLETE from a guess, half-signal, or “should have worked.”
2. Status stays **WAITING ON OWNER** until Owner says it in chat (e.g. “saved”, “got the URL”, “it opened”).
3. If unsure, say **UNKNOWN** + what you checked — not success.
4. Just Talk / Owner report beats any agent status. Correct the board immediately when they contradict you.

## Applies to
Engineering first. Same bar for Research and every desk on Owner-gated steps.

## Why
False success destroys trust and ships broken pipes. Confidence without proof is a defect.
