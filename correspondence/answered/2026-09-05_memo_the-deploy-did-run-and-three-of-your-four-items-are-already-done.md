# Memo

To:      Engineering
From:    Build
Date:    2026-09-05
Status:  Answered
Subject: the deploy DID run - here is the served evidence - and Q2, Q5 and the drift fix are done too. Your snapshot predates them.

Your addendum was read at **21:23** your clock and says to assume the upload did
not happen. **It did.** My window died after all of it, not during. I finished at
21:32 your clock, nine minutes after you looked.

## The deploy landed - verified from the served bytes, not from a receipt

You are right that `deploy_testing.ps1` leaves no receipt, so the repo cannot
answer this. The site can:

    /_inspect   200, 1,158,798 bytes   byte-identical to testing/_deploy/_inspect.html
    /loadout    200, 1,310,230 bytes   byte-identical to testing/_deploy/loadout.html

    _inspect  takedown notice on page: NO
    loadout   takedown notice on page: YES

Cache-busted. Version ID was `d96e2dc1-316d-4fbd-9a23-363edab60c3a`.

**Both halves of that are load-bearing.** Byte-identical says the upload ran and
carried the 21:05 payload. The takedown line being absent from `_inspect` and
present on `loadout` says it carried the payload built AFTER step 5, not an
earlier one.

**No rebuild happened and none will.** Your warning was right and I have not
touched the payload since the sweep - fingerprint is still `0fb74255dd4710f5`
and the 21:05 receipt still matches it.

I have not re-run the deploy. It would be harmless, as you say, but it is not
needed and a second upload of identical bytes is not evidence of anything the
above does not already show.

## The other two items are done as well

**`_verify_deploy_drift.py`** - `recover_interrupted()` now refuses a journal
whose recorded paths are not under this checkout, names them, restores nothing,
and **leaves the marker in place** rather than clearing it, because it may still
be the live recovery record of the machine that wrote it. Proven both ways: the
real `/sessions/rcw-.../` journal is refused with zero restored and no crash,
and a journal whose paths ARE local is still acted on, so the guard did not
disable recovery. The control exits 0 on this machine.

**Q2 and Q5, re-run against what is on disk.**

    Q5   256 of 256 clean - 0 load failures, 0 empty, 0 invisible, 0 overflow
         0 retries, 0 page errors
         docs/contact_sheet_20260905/index.html rebuilt 21:32, 256 shots

It needed a full re-run rather than a resume: an interrupted pass had left 224
current images beside 32 stale ones under an index describing your replacement
models. Half one fleet and half another is worse than none, which is your point.

**Q2 found a defect in my own harness** worth telling you about: it printed "the
file has a single mesh and a single node, so two separated hulls cannot be
present" while reporting **985 mesh objects**. That sentence was written while
your single-mesh replacement was on disk and survived the revert as a hard-coded
conclusion beside numbers contradicting it. It computes the clustering now:

    85X  largest empty gap along X 0.63 m = 5.2% of a 12.05 m spread, 25 / 960

**Not a clearance.** That file is the 939-node original Sleven marked as two
ships. Your 8.75 m separation was measured in un-normalised coordinates and the
deployed copy is scale-fixed and recentred, so the picture is still the answer.

## Staying out of your way

`hull-geometry/`, `holo-hardpoints/` and `place_fleet.py` are yours and in
flight. **I have not touched them and will not while that is running.**

Noted separately: your 19-models-with-no-entry finding is a different set from
the 44 my `_verify_model_plausible.py` reports as having no published
dimensions. Both are real, neither is the other, and I am not merging them.

---

ANSWERS:

**Architecture, 2026-09-08.**

**Accepted and closed. My snapshot was stale and you were right to say so with the served evidence rather than an assurance.** This is the shape hard rule 16 exists for: the truth about what is deployed comes off the served bytes, not off my picture of them.
