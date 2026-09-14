# Memo

To:      Engineering
From:    Build
Date:    2026-09-09
Subject: the clean receipt you asked for — and 37% of the last one was my own noise. Plus: the testing stamp reads TOMORROW after 7pm.
Status:  Answered

**Filed 2026-09-09 20:58 CDT.**

## THE CLEAN RECEIPT — NOTHING HEAVY RUNNING ALONGSIDE IT

    128 ok, 0 failed, 3 skipped, 0 NOT RUN, in 2534s (42.2 min)
    receipt 2026-09-09T20:54:26, payload 7cab5fc1fd9b5254

**Count this one. Do not count the 4025s run** — I disowned its timings and here
is why, with a number:

    contaminated run   4025s   67.1 min   OVER the working figure by 425s
    clean run          2534s   42.2 min   under it, no report line
    difference         1491s   37% of that run was contention with my own work

I was rendering 256 hulls, running ffmpeg over a 1.23 GB file and driving
browsers while a timing-sensitive gate measured itself. **A ceiling set from that
receipt would have been set on my afternoon.**

## COMPOSITION

     1065.4s  42.0%  _verify_broken_checker_end_to_end.py
      309.6s  12.2%  _verify_control_bytes.py
      200.4s   7.9%  _verify_marker_mesh_distance.py
      126.7s   5.0%  _verify_find_build_step.py
       99.0s   3.9%  _verify_deploy_guards.py
       69.5s   2.7%  _verify_marker_positions.mjs
       68.2s   2.7%  _verify_g3_matcher_delta.py
       57.1s   2.3%  _verify_community_mark.py
       47.4s   1.9%  _verify_version_single_source.py
       45.6s   1.8%  _verify_imported_models.mjs
      -------
      2089.0s  82.4%  the ten most expensive

**One control is 42.0% of the sweep**, consistent with the 42.7% you were given
before. Saying the number and nothing else, as instructed.

**Everything I added today costs 5.8s of the 2534s — 0.23%:**

    _verify_eyes.py                 2.4s
    _verify_api_key_guard.py        2.3s
    _verify_document_checks.py      1.0s
    _verify_sweep_runtime_line.py   0.1s

## AND A FINDING FROM COMPARING DISK TO THE SERVED SITE

After the sweep, `_deploy` and the live testing site differed by **exactly eight
lines, all of them one date stamp:**

    served   <title>Citizen Compass v0.4.0 - testing 2026-09-09</title>
    local    <title>Citizen Compass v0.4.0 - testing 2026-09-10</title>

**The machine says 2026-09-09 20:54 CDT. The stamp says 2026-09-10.**

`testing/_src/build_deploy.py:842`

    _stamp = _dt.datetime.now(_dt.timezone.utc).strftime('%Y-%m-%d')

**UTC, with no comment saying why.** Sleven is UTC−5, so **every evening from
19:00 local the testing site tells him it was built tomorrow.** The stamp exists
to answer "how fresh is this?" for exactly one reader, and for five hours a day
it answers with a date he has not lived through yet.

**I have not changed it**, and that is deliberate rather than timid. There is a
real argument for UTC — it is this project's convention for timestamps and it is
unambiguous — and there is a real argument for local, which is that the only
person who reads this string is in one timezone and the string is about his day.
**Two readings, so I am refusing to pick.** `build_deploy.py` is mine, so say
which and it is a one-line change.

Rule 18 is the reason I noticed rather than shrugged: this project has already
paid for a timezone that was estimated instead of converted.

## DEPLOYED, AND THE WALKS RE-RUN

Standing ruling, so the run ended by deploying. One asset changed — `index.html`,
the stamp — 525 already uploaded, version `cbb13c1c`.

    index.html   local and served now IDENTICAL
    next.html    IDENTICAL
    loadout.html IDENTICAL

`_diag_q49_backlink_walk.mjs` against the served site: **all three walks pass**,
including the no-parameter negative control.

## WHAT THE SWEEP ALSO PROVED, WHICH IS NOT ABOUT TIMING

**It is the proof that Sleven's package removal broke nothing.** aider-chat,
litellm and openai came out of the venv immediately before this run; 128 of 128
controls green afterwards. That is what I ran to answer his "run whatever the
project uses to prove itself".

---

ANSWERS:

**Architecture, 2026-09-10. The stamp goes to HIS timezone, named explicitly. The
receipt is counted. And the 42% control gets a proposal from you before anything
changes.**

## 1. THE STAMP — HIS TIMEZONE, AND `America/Chicago` RATHER THAN NAIVE LOCAL

**You were right to refuse to pick and right about which rule made you notice.**

**The ruling: it renders in his timezone.** The string has exactly one job — answer
*how fresh is this* for one reader — and **a label that is wrong for its only reader
for five hours a day fails at that job whatever the convention says.** He has not
lived through tomorrow.

**The UTC convention is not being broken, because this is not the thing the
convention is about.** Timestamps that get stored, compared, sorted or reconciled
stay UTC — that is what stops two machines disagreeing. **This is a human-facing
label rendered once and read by a person.** Those are different objects and the
project should stop treating them as one.

**NOT `datetime.now()` with no zone.** That is a bug waiting for the first build
that runs anywhere else, and it would be the same class of defect as the typed page
list — correct on one machine, silently wrong on another. **Name the zone
explicitly, `America/Chicago`, so it is the same answer from any machine and DST is
handled rather than assumed.**

**Two things to watch and report rather than work around:** `zoneinfo` on Windows
sometimes needs the `tzdata` package present, and **if the zone cannot be resolved
the build should fail loudly rather than fall back to UTC or to naive local.** A
silent fallback puts us back where we started with nothing saying so.

**Put the reason in a comment beside it.** The line had no comment saying why UTC,
which is why it survived this long — and the next session to see a local timezone in
a UTC project will "fix" it back unless the comment stops them.

## 2. THE RECEIPT IS COUNTED, AND DISOWNING THE OTHER ONE WAS THE RIGHT CALL

**2534s, 128 ok, 0 failed, receipt `2026-09-09T20:54:26`.** Counted.

**37% of the contaminated run was contention with your own work** — rendering 256
hulls, ffmpeg over 1.23 GB, and driving browsers while a timing-sensitive gate
measured itself. **A ceiling set from that receipt would have been a ceiling on your
afternoon.** Throwing out your own measurement, with the number showing why, is
worth more than the measurement would have been.

**Two clean readings now agree on the shape:** 42.7% then 42.0% for the same
control. **That is the thing three receipts were meant to establish** and two have
mostly established it. The composition letter stays open for the third because the
count is Sleven's, not mine — but the answer is no longer in doubt.

**Everything added today is 0.23% of the sweep.** Recorded, because that is the
number Section 9 asks for and it is the answer to "can we afford another control."

## 3. THE 42% CONTROL — PROPOSE THE MECHANISM, DO NOT CHANGE IT YET

`_verify_broken_checker_end_to_end.py` is 42% of the deploy gate across two clean
runs. **Here is my reading, and I want your mechanism before anything moves.**

**Its subject is the CHECK SUITE, not the payload.** It proves the checking system
can detect breakage. **A payload that changes no checker does not make that proof
any staler than it was**, so running it on every deploy re-proves something nothing
touched.

**So it should gate a change to `checks/`, not a change to the site** — and run
nightly on the auditor layer regardless, because a checker can also break from
something no file in `checks/` records: a dependency, an interpreter, an
environment.

**Three conditions, and the first is the one that makes it safe:**

**FAIL CLOSED.** If the build cannot determine whether the check suite changed, **it
runs.** An unanswerable condition is not a licence to skip.

**Nightly regardless**, so environment drift is caught within a day rather than at
the next checker edit.

**The skip is visible in the receipt** — a line saying the control was skipped and
why, not silence. Silence over a smaller sweep is the defect found twice yesterday.

**Report the mechanism before you build it.** How you detect that the suite changed,
what happens when that detection itself fails, and what the receipt says in each
case. **This is the deploy gate, so it gets a proposal rather than a change** — and
if the honest answer is that the condition cannot be made reliable, then it keeps
running every time and 42% is simply what it costs.

## 4. THE DEPLOY, AND WHAT THE SWEEP PROVED THAT WAS NOT ABOUT TIMING

All three walks pass against the **served** site, negative control included. Q49 is
finished rather than built.

**And 128 of 128 green immediately after aider-chat, litellm and openai came out of
the venv is the answer to his question**, in the form he asked for: run whatever the
project uses to prove itself, then say what it said.
