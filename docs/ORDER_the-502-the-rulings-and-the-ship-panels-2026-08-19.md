# ORDER — the 502, four rulings Sleven delegated, and the ship detail panels. RUN CONTINUOUSLY.

    from    C1, 2026-08-19 evening
    for     Code
    status  GO. No stop points. Same run rules as the 08-19 shop order:
              docs/ORDER_shop-and-price-layer-RUN-CONTINUOUSLY-2026-08-19.md §1.
              Read that section again and obey it. It worked - 25 items,
              68 minutes, no gates. Nothing here changes it.
    ledger  APPEND to docs/LEDGER_shop-price-layer-2026-08-19.md. Same file.
              The run continues; it is not a new project.

---

## 0. First, credit where it is owed

Phase A through F was good work. Three things in particular:

- **You overrode my §3.2 uuid ruling and you were right.** I ruled "join on UUID,
  never on display name". The data says uuid is the worst key available: 120
  shared by up to 10 items, 2,162 items carrying none, zero commodities carrying
  one. Display-name collision - the thing I predicted - was 7 of 7,721. The
  measurement beat the ruling and you followed the measurement. Do that again.
- **The D2 409 on an ambiguous uuid** is the right call and for the right stated
  reason: returning the first match is the silent version of the upstream bug.
- **You refused to remove the mockup banner.** That is the single most valuable
  thing in the whole run.

One correction, and it is mine to make: my §3.3 said the thruster question would
be answered by the coverage table. It was not answerable at all - UEX has no
thruster category. **"The source cannot answer this" is a better result than a
number, and you reported it as such rather than returning a plausible zero.**

## 1. SLEVEN'S RULINGS - he delegated these four to C1. They are settled.

### R1. Category 36 "Commodities" vs the commodity import

**The site shows the COMMODITY IMPORT.** 204 commodities, 147 priced, 72%.
Category 36's 158 items carry zero prices, and a price site showing a commodity
with no price is worse than not showing it.

**Both stay stored. Nothing is deleted** - standing preservation rule. The
category-36 rows become a **cross-reference**, not a tombstone: where an item-side
row and a commodity-side row describe the same thing, record the link so the site
can follow it later. **Do not merge them.** They are two UEX representations and
collapsing them would destroy the evidence that they differ.

Reverses as a display filter, one line, if he disagrees later.

### R2. The FIND home-page explainer rewording — ACCEPTED

You were right and for the reason you gave. "Seventeen invented items across nine
invented shops" described the DATA, the data is now real, and leaving it would
have been false in the other direction. **The banner staying and the explainer
changing are not in tension** - one describes whether the deployed path is proven,
the other described the data. Keep it as you wrote it.

### R3. The Stims conflict — default ACCEPTED, but it does not stay in the ledger

First-occurrence-wins is correct as *storage* behaviour and nothing is
overwritten, so it reverses freely. **But a one-off note in a ledger is not a
check.** You said yourself it should probably be a C-phase finding. It should.
See G4 - it becomes an auditor, because if the source did this once it will do it
again and nobody will be reading the ledger that day.

### R4. A missing database URL must never present as a total outage

Ruled below in G1, because it is also the leading hypothesis for the 502.

## 2. THE 502 — what I found, so you do not re-derive it

**Your push is exonerated, and I checked rather than took your word for it:**
`app/database.py` is unchanged since 2026-08-08 and the DATABASE_URL line since
f8d612d on 2026-07-24. `Procfile` unchanged since 07-24. Every third-party import
under `app/` (fastapi, pydantic, sqlalchemy, dotenv) is already in
`requirements.txt` - **your new router added no dependency**, which was the
failure mode most likely to break only in deploy. The whole-file `M` markers in
git status are whitespace; `git diff --ignore-all-space` is empty.

**The one import-time crash that produces exactly this symptom:**

    app/database.py:
    DATABASE_URL = os.environ.get("DATABASE_URL") or os.environ["RAILWAY_DATABASE_URL"]

If `DATABASE_URL` is absent, that raises `KeyError` **at import**, uvicorn never
binds, and every route 502s including `/health`. That matches what you observed
exactly: /health, /docs and /api/v1/shop/categories all failing after ~15s.

**And note the gap in your own check:** you tested "imports cleanly with an
unreachable DATABASE_URL (simulated)". **Unreachable is not absent.** An
unreachable URL is lazy and boots fine. An absent one is a KeyError. Your test
could not have caught this and it is worth knowing why.

**The other candidate I cannot rule out from here: the Railway service is simply
not running** - stopped, crashed, or out of credit. Uniform 502 with ~15s
timeouts fits that just as well. **I have no Railway access and neither do you.
Do not try to get any.** G1 makes the difference visible from outside, which is
the part that is ours to fix.

## 3. THE WORK

**G1. A missing database URL must not take the whole app down.**
Read the URL from `DATABASE_URL`, then `RAILWAY_DATABASE_URL`. If neither is set:
**do not raise at import.** The app boots, `/health` answers
`{"status": "degraded", "database": "unconfigured"}` naming BOTH variables it
looked for, and every database-backed route returns **503 with that same reason**.
*Why not leave it loud:* it is already loud, in the worst possible way - a uniform
502 with no signal, which is why we are guessing tonight instead of reading.
*Why not exit cleanly at startup:* Railway restarts it in a loop and you still get
502. **Degraded-but-answering is the only shape that can be diagnosed from
outside.**
*Acceptance:* with the variable unset, the app boots and `/health` says degraded.
*Control, and it is the load-bearing one:* with the variable SET, `/health` says
`ok` and a real query still works. A degraded mode that never leaves degraded is
worse than the crash.
**Do not make a wrong URL silent** - unreachable is a different fault from absent
and must read differently.

**G2. Say which fault it is, in the log, once.**
One line at startup naming which variable supplied the URL, or that none did.
Not a heartbeat. Not per request.

**G3. The Ares matcher — 2 ships, one rule, and the trap in fixing it.**
The word-match is directional: it requires every word of the mount KEY to appear
in the MODEL name, so "Ares Star Fighter Inferno" refuses `Ares_Inferno`. Fix the
direction.
**THE TRAP:** loosening a matcher to catch 2 is exactly how you silently join the
wrong 25. *Control, mandatory:* after the change, **the 25 ships F1 identified as
genuinely having no mount data must STILL not match** - Crucible, Endeavor,
Galaxy, Kraken, Liberator, Orion, Pioneer, the Rangers, Hull_D, Hull_E,
Zeus_Mk_II_MR, E1_Spirit and the rest. Assert that list by name. If any of them
starts matching, the fix is wrong and you revert it rather than accept 27.
*Acceptance:* placed goes 29 -> 31. Skipped goes 39 -> 37. Not 12.

**G4. C7 — a source-duplicate auditor, per R3.**
Flag (commodity, terminal) and (item, terminal) pairs appearing more than once in
one source file **with differing prices**. Byte-identical repeats are noise and
are not findings. Stims at HUR-L5 (5,800 vs 4,900) is the known case and must
appear. **Flag only. Never resolve.** Standing rule.
*Control:* both halves, like C6 - a planted conflict fires it, a planted
byte-identical repeat does not.

**G5. R1 — the commodity cross-reference.**
Link, do not merge, do not delete. Record how many of the 158 category-36 items
found a commodity counterpart and how many did not. **The ones that did not are
the interesting number** and belong in the ledger.

**G6. E2 — try again, and stay honest.**
Fetch `/api/v1/shop/search?q=omnisky` off the deployed URL. **Real rows back ->
the banner comes off and nothing else changes.** Still 502 -> it stays BLOCKED,
you say so in one line, and you move on. **Do not remove the banner on a build, a
deploy, a local server, or a good feeling.** This is the third time that rule has
saved this project; do not be the run that breaks it.

**G7. The self-install build has never been verified.**
9271f6d added 1,073 lines of Win32 registry and shortcut code this morning and
nobody has built it. Build it. **Read the PE subsystem byte back off the exe and
confirm it is 2, not 3.** That defect shipped to two of Sleven's testers once
already because a comment claimed a build flag no script ever passed.
Run `-selftest`. **Do not cut a release. Do not install it anywhere.** Report
whether it builds and what the byte says.

**G8. The two `cc-pending` panels on the ship detail page.**
F3 already worked out what they need and there is now an API to give it to them.
Wire them. Component and hardpoint data reaches the panel from
`/api/v1/shop/...` and the ship endpoints.
*Control:* a ship with no component data shows an honest empty state - **not a
spinner, not invented values.** That panel's own text promises "no invented
values" and it must stay true.

**G9. Sweep.** Re-run every control in `checks/`, including the ones from A-F.
G1 touches `app/database.py`, which every check that opens a session depends on.
**A change at the engine is exactly the change that breaks things far away.**

## 4. WHAT MUST NOT HAPPEN

- **Do not remove the mockup banner without the live fetch.** G6.
- **Do not accept 27 recovered ships.** G3. Two is the right answer.
- **Do not merge or delete the category-36 rows.** R1.
- **Do not auto-resolve a price conflict.** G4. Auditors flag.
- **Do not cut a release or install the collector.** G7.
- **Do not go looking for Railway credentials.** §2.
- **Do not `git add -A`. Push at the end.**

## 5. REPORT

- The ledger, appended.
- Whether the deployed API came back, and what `/health` says now.
- Whether the collector builds and what its PE subsystem byte is.
- Placed / skipped after G3, and confirmation the 25 still do not match.
- How many of the 158 category-36 items found no commodity counterpart.
- Anything here you think is wrong. **G1's degraded mode is the part most worth
  arguing with** - it trades a loud failure for a diagnosable one, and if you
  think that trade is wrong, say so with the failure you have in mind.
