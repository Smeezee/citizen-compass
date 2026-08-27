# FINDING — Netlify is not the blocker. Nobody has run the button that already exists.

**C1, 2026-08-27 13:32 local.** Answers `NEXT.md` Q1 and corrects the reason
given in `LIVE.md` an hour ago.

## What I said an hour ago, and it was wrong

`LIVE.md` records the public site as 28 days stale and attributes part of that
to a **Netlify credit block** nobody had re-checked in three weeks — reading
`CURRENT-STATE.md`, which says the live site would sit on v0.3.9 "until that
clears".

**That is stale and I repeated it without checking the deploy path.** Same
failure the critique describes, committed while writing the response to the
critique.

## What is actually true

`scripts/deploy_live.ps1`, committed **2026-08-21** (`0a4d5ed`), 381 lines. Its
own header, verbatim:

> **NOTHING HERE TOUCHES NETLIFY.** citizencompass.netlify.app is where the live
> site is TODAY, hand-deployed.

**The live deploy targets Cloudflare Workers, exactly like the testing site.**
The Netlify credit block was engineered around six days ago. It blocks nothing.
Cloudflare's free tier does not meter bandwidth, which is why testing moved
there and why the same reasoning applies to live.

The script is a mirror of `deploy_testing.ps1` — same unknown-file guard on the
same bytes, same fail-closed handling when the guard cannot run, same `-WhatIf`.
`wrangler.live.toml` exists. The API token is in `.env`.

**And it refuses to publish the wrong thing, in ways worth naming:**

- **It refuses a payload carrying the password gate.** Its own words: publishing
  it "would lock every visitor out behind a password they were never given, and
  from the outside that looks like an outage rather than like a mistake — so
  nobody would report it as one."
- **It refuses a payload carrying the `testing <date>` stamp.**
- **It refuses to publish under the testing worker's name**, because a wrong
  name does not fail — it succeeds, at a second URL. This project has already
  done that once.

## So what IS the blocker

Three things, and none of them is billing:

1. **`citizencompass.citizencompass-contact.workers.dev` returns 404.**
   Verified 2026-08-27 13:30 local. The worker does not exist yet.
2. **The script has never been run for real.** Only with `-WhatIf`. Its header
   says so: *"Do not be the one who runs it for real without being asked to."*
3. **Nobody has asked.** That is the whole of it.

**Whether `wrangler deploy` creates the worker on first publish is UNTESTED
HERE and is not being guessed at.** It normally does, with a scoped token. The
`-WhatIf` path will say, and that costs nothing to run.

## The sequence, which already exists

    python testing\_src\build_deploy.py --live        # no gate, no testing stamp
    powershell -File .\scripts\deploy_live.ps1 -WhatIf   # says what it WOULD do
    powershell -File .\scripts\deploy_live.ps1           # publishes. SLEVEN ONLY.
    python testing\_src\build_deploy.py                # back to testing, or the
                                                       # next testing deploy refuses

**The first two are information and are safe. The third is publication and is
Sleven's alone.**

## What this does to the critique's Finding 5

`CRITIQUE_senior-analyst-review-2026-08-27` says almost every front is at 70-90%
and none has crossed to live, and recommends freezing new work until one does.
**The recommendation stands. The premise that it is far away does not.**

The testing payload right now carries the holo viewer on 258 models, 754
hardpoints on CIG's own coordinates proven in a real browser, 19 rescaled
models, the picker, and the settings fix. **The distance between that and a
public site is one command and one person's go-ahead** — and it has been since
2026-08-21, through six days in which the reason given for not shipping was a
billing state that had already been designed around.

---

*C1, 2026-08-27.*
