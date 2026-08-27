# AMENDS — the roadmap watcher's endpoint is wrong, and the watcher is now needed

**2026-08-27 · C1 · amends `docs/WORKORDER_roadmap-watcher-2026-08-14.md`**
**Where this disagrees with that work order, this wins.**

---

## Why this is being raised now

**Sleven had to tell C1 what CIG announced.** He mentioned a roadmap change
about the Nyx planets in 4.11 and C1 could not confirm it: every source it can
reach is from **13-14 August** and says **Nyx I only**, with Nyx II and III
"hinted for subsequent updates".

**There was a Roadmap Roundup posted 26 August** — the Comm-Link and the
Spectrum thread both exist and **both return only page metadata to a fetch, not
the body text.** The same wall the 4.10 release notes hit earlier the same day.

So the position is: the roadmap moved, the aggregators had not caught up, the
articles are unreadable to a fetch, and **the only person in the loop who knew
was Sleven.** That is exactly the job this watcher was approved to do on
2026-08-14 and it has never been built.

---

## The defect — and it would have shipped silently

The work order names the Release View endpoint as:

    GET /api/roadmap/v1/boards/1

**Board 1 is not the current release view. It returns 2018.** Fetched
2026-08-27, it answers with releases **3.1 through 3.3.5**, all marked released:
Hurston, Lorville, Object Container Streaming, Aberdeen, Arial. No 4.x
anything. No Nyx.

**Built to spec, the watcher would have polled a museum exhibit every four
hours and correctly reported that nothing ever changed.** No error, no empty
response, no crash — a green watcher watching history. This project has a name
for that shape and it is the reason Rule 12 exists.

### R0 — find the real board before writing anything that polls one

**First task, before any of the work order's build steps.** Enumerate the
boards, identify which one carries the live release view, and **prove it by
finding a 4.x release and a card that is not yet released.** Record the board
id and the evidence in the manifest.

**And write the check that could fail:** assert the polled board contains at
least one unreleased card and at least one release numbered 4.x or higher. A
board that answers only with released history must fail the control, loudly, at
startup — not after months of silence.

---

## What stands unchanged from the work order

- **Both endpoints approved, staged.** Release View on a timer now; the
  Progress Tracker GraphQL endpoint built now, scheduled when Sleven says.
- **Every 4 hours, in config.** Plus an on-demand "check now" that **must run
  the same code path as the timer** — a second path is a second thing to be
  wrong.
- **Key on card presence plus a payload hash. Never on `updateDate`** — the API
  returns Aug 2024 for a card the UI renders as Aug 2021.
- It supersedes `WORKORDER_rework-tripwire-build-spec-2026-08-14.md` and both
  copies of the tripwire amendment, which now redirect.

## What this amendment adds

**R1 — a change is only useful if somebody reads it.** A detected change writes
a dated finding into the project the same way every other durable output does,
naming the cards added, removed and altered, with the board id and fetch time.
**Silent success is the failure mode here**: a watcher that detects a change and
files it nowhere is indistinguishable from one that detected nothing.

**R2 — the Comm-Link roundups are a second source and are NOT a substitute.**
They are human-readable and they are also unreadable to a fetch, returning
metadata only. Do not build the watcher against article text. **The API is the
route.** Record the roundup URL alongside a detected change if one can be
matched by date, as a pointer for a person — never as the evidence.

**R3 — this is the first live use of `last_verified_patch`'s sibling problem.**
The site knows which patch its data was verified against. It does not know what
CIG has announced since. Those are different questions and the watcher answers
the second one.

---

## What is NOT in scope

Nothing about acting on a roadmap change automatically. **The watcher reports.**
Whether a Nyx planet or a new ship changes what this site does is Sleven's call,
as it has always been.

Do not deploy the live site. Testing only.
