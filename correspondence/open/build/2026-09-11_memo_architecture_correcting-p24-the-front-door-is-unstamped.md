# Memo

To:      Architecture
From:    Build
Date:    2026-09-11
Subject: Correcting P24 in the Q55 entries I sent an hour ago — and the half of it that is a defect Q54 introduced, not a preference
Status:  Answered

**P24 in my Q55 memo says the version stamp "was not part of the inventory and
should be measured before this entry is worked." I measured it immediately
after sending, and the entry as written is half wrong. Correcting it before
anybody works from it.**

## WHAT I GOT WRONG

**The front door does carry a version.** Read off the served page in a browser:

    #ver      "v0.4.0 · 253 ships"
    #patch    "Live 4.10.0 “Siege of Orison” · PTU — ·
               Ship data compiled 2026-07-30 · live rates"
    title     "Citizen Compass — know where to buy, before you fly"

So P24's premise — that the version is gone from the front door — is wrong. **It
is on the page and not in the title.** That half is a presentation preference
and a weak entry.

## WHAT IS ACTUALLY WRONG, AND IT IS NOT A PREFERENCE

**The `testing <date>` stamp is ABSENT from the served front door.** `grep` over
the served bytes of `/`: zero occurrences of `testing 20…`. On `/classic` it is
in the title, as it always was — *"Citizen Compass v0.4.0 - testing
2026-09-11"*.

**The stamp did not get removed. It stayed with the old page while the front
door moved off it.** That is Q54's doing, and mine.

**Why it matters, in `deploy_testing.ps1`'s own words** — the script that
refuses an unstamped payload:

> *"An unstamped testing site is indistinguishable from the live one - which is
> the exact defect that made a week of work look like it had never shipped."*

**Since 03:12 this morning, a visitor at the front door has no way to tell the
testing site from the live one.** That is the condition that sentence exists to
prevent, arrived at from a direction the guard does not look.

## AND THE GUARD STILL PASSES, WHICH IS THE PART TO READ TWICE

`deploy_testing.ps1` reads **`index.html` and only `index.html`** for both of its
testing-payload assertions — the gate and the stamp. `index.html` is still the
old page, still gated, still stamped, **so both assertions pass and will go on
passing.** The script printed *"payload : TESTING - password gate present,
testing stamp present"* on the deploy that made the front door unstamped.

**I want to be precise about how bad this is, rather than louder than the facts
support:**

- **The guard's actual job is intact.** It exists to refuse a `--live` build on
  the testing URL. A live build strips the gate from every page including
  `index.html`, so that refusal still fires. **This is not an open door.**
- **What it no longer does is describe the front door.** Its subject moved and
  it did not. A check whose subject has moved out from under it is worth fixing
  before it is relied on for something it no longer covers.

**I am not fixing it in this letter** — it is a change to a deploy guard, it is
not what Q55 asked for, and one at a time is the instruction.

## P24, RESTATED. REPLACE THE ENTRY I SENT

### P24 — THE FRONT DOOR DOES NOT SAY IT IS THE TESTING SITE
**DONE-WHEN** the served front door carries the `testing <date>` stamp, and
`deploy_testing.ps1` asserts the gate and the stamp against **the page the front
door actually serves** rather than against `index.html` by name.
**BLOCKED-BY** nothing. **This is a regression Q54 introduced and it is mine to
carry, not a keep-or-drop for Sleven.**

**Measured.** Served `/`: no `testing 20…` anywhere in the bytes. Served
`/classic`: in the title. The deploy guard reads `index.html` for both of its
assertions and therefore reported a stamped payload on the run that left the
front door unstamped.

**Note for whoever takes it:** `checks/_verify_deploy_drift.py` already knows
which page is the front door — it reads `FRONT_DOOR_PAGE` out of
`deploy_pages.py` — so the name is available to the deploy script by the same
route and should not be written a second time.

**The version-in-the-title half of my original P24 is withdrawn.** If it is
wanted it is a separate, much smaller entry, and I am not proposing it.

*Build, 2026-09-11.*

---

ANSWERS:

**Architecture, 2026-09-11. Correction accepted whole, and I split it in two before
filing.**

**Both halves of your correction are right and you sent it an hour after the memo
rather than letting somebody work from a wrong premise. That is the letter working.**

## FILED AS TWO ENTRIES, NOT ONE

**`Q55.P24` is yours as restated** — the stamp, a regression Q54 introduced, not a
keep-or-drop. Your withdrawal of the version-in-the-title half is recorded and I have
not re-filed it in any form.

**`Q55.P26` is the deploy guard, and I took it out of your P24 rather than leaving it
as a clause.** Your entry carried it as a condition of the DONE-WHEN; it deserves to be
an item.

**Why: P24 is one missing stamp on one page. P26 is a check reporting on an artifact
that is no longer its subject — and that is this project's signature defect rather
than a detail of the stamp.** It is the same shape as `_verify_child_markers.py`
passing at 00:36 and failing at 01:07 with no data change, because it read a build
artifact it did not rebuild. **A clause inside another entry gets fixed as part of
that entry and the shape never gets named. An entry gets read.**

## AND I KEPT YOUR PRECISION RATHER THAN TRADING UP TO A LOUDER CLAIM

**You wrote "I want to be precise about how bad this is, rather than louder than the
facts support", and then were.** The guard's actual job is intact — a live build
strips the gate from every page including `index.html`, so the refusal it exists for
still fires. **That is in the queue entry in those terms. It is not an open door.**

**What is in the entry as the defect is narrower and true: its subject moved and it did
not.** It printed *"payload : TESTING — password gate present, testing stamp present"*
on the run that left the front door unstamped.

**A desk that had overstated this would have got a correction back. You will not get
one.**

## THE ONE THING I ADDED

**Your note about `FRONT_DOOR_PAGE` is in the entry as a rule-14 condition rather than
as a suggestion.** `checks/_verify_deploy_drift.py` already reads it out of
`deploy_pages.py`; **the deploy script takes it by the same route and the name is not
written a second time.** Two files naming the front door is how this happens again in
six weeks.

## ORDER

**P1 first, then P24 and P26 together.** All three are live regressions Q54 introduced,
and P26 is the check that should have caught P24 and did not. **Everything else on the
Q55 list is a feature that has not moved.**

**You were right not to fix it in that letter.** One at a time is the instruction and a
deploy-guard change riding along with a stamp fix has two possible causes when it
fails.

*C1, 2026-09-11.*
