# Update — received four new jobs (window matcher, UEX commodities, unreleased filter, FixedReward census)

**When:** 2026-08-05

Logging on arrival per hard rule 13, before starting. Ordered as given.

1. **The window matcher** (rev 5 §3 defect). Match on **process** —
   `StarCitizen.exe` — and refuse any other process outright. Title becomes a
   hint for choosing between that process's windows, never authority to capture.
   Bench testing moves behind `--allow-any-window`, which **must not compile
   into the crew build**. Then prove the refusal against a browser titled to
   match.
2. **Call the UEX commodity endpoints.** Six endpoints with the existing Bearer
   token from `.env`. Gate exactly like source 6 — five checks, hashes,
   manifest, sealed snapshot, `data_tier C` with UEX's ±20% commodity
   tolerance. **Promote nothing to the database.** Report row counts per
   endpoint and whether prices carry a timestamp or a game_version — coverage is
   not freshness, and that distinction decides whether the collector's price
   role survives.
3. **Filter unreleased content** (rev 5 §5). `NotForRelease`, `WorkInProgress`,
   `HiddenInMobiglas` across 5,108 contracts. Count each, then check whether any
   contract-derived output already shipped — blueprint source lists, crafting
   pages, anything in `processed/`. If unreleased content is reachable from a
   live page that is a defect to fix now.
4. **The FixedReward census, locally.** Full scan of all 5,108 contract files —
   C2's 50.4%/46.4% split was a 25% sample that timed out through the Cowork
   mount. Publish `FixedReward.Amount` as **"listed reward"**, never "what you
   get".

## Noted, and acted on

**The token is not going into chat, a log, or any file I write.** It goes from
`.env` to the request header and nowhere else — the same handling
`deploy_testing.ps1` already uses for the Cloudflare token.

**Separately flagged by Sleven and worth repeating here: that UEX token was
exposed in a screenshot and has never been rotated.** That is a live credential
exposure independent of this job. I am not able to rotate it — it needs doing at
UEX — but it should not wait on this work order.

## One correction to the defect report, which does not change the fix

Capture 0006 was produced by an explicit `--window "DuckDuckGo"` on my side
while bench-testing the three capture backends, not by title auto-detection. The
underlying defect is real and was found the same evening: auto-detection *was* a
title-substring test, and it selected **this session's own terminal**, titled
"Build Star Citizen data pipeline with three jobs". I tightened it to an
exact-title test plus a denylist and logged that.

**The new instruction is stricter and better, and supersedes my fix.** An
exact-title match is still title-as-authority, and a denylist is a blocklist —
it fails open for anything not on it. Process-only is a whitelist and fails
closed. I am replacing my fix rather than keeping it.

**Next:** job 1 now.
