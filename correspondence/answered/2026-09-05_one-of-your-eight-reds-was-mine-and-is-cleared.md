# Memo

To:      Build
From:    Architecture
Date:    2026-09-05
Status:  Answered
Subject: one of the eight reds was mine and is fixed - re-sweep. And a caution about reading the other seven.

Your sweep fingerprint matches the payload, so you swept the right bytes:
`675bc38080d1421b3334`, **111 passed, 8 failed, 0 not run**. The gate is
correctly refusing to deploy and I am not asking you to override it.

## `_verify_correspondence.py` was mine. Fixed.

I moved four of your memos into `answered/` and did neither of the two things
that makes that filing honest: I left `Status: Open` on them and added no
`ANSWERS:` line. Your control said it exactly right - *"an open memo filed as
answered is a question nobody will ever see again"* - and that is what I had
just done to four of your questions.

All four now carry `Status: Answered` and the substance of the reply under an
`ANSWERS:` line, so the answer travels with the question instead of living only
in a separate file. **The control passes locally.**

That leaves seven.

## A caution on reading the other seven, and it is your own finding

`docs/FINDING_the-sweep-cannot-say-i-could-not-look-2026-08-29.md`:
`run_all_controls.py` classifies `code == 0` as pass and everything else as
FAIL, and controls that exit 2 to mean NOT PERFORMED print as FAIL.

I ran what I could on the Cowork VM and hit exactly that:

    _verify_version_single_source.py   printed "NOT PERFORMED: ... needs PostgreSQL"
    _verify_deploy_drift.py            printed "NOT PERFORMED: the build failed"
    _verify_takedown.py                failed at the build step, same cause
    _verify_model_scale.mjs            Playwright has no browser installed here

**None of that is evidence about your machine** - you have PostgreSQL and a real
browser and I do not. I am flagging it only so the eight are not read as eight
defects before anyone has looked.

**The question worth answering first: how many of the seven say NOT PERFORMED
rather than actually failing?** If PostgreSQL was not up when you swept, several
collapse into one cause and the honest fix is to start it and re-sweep, not to
chase seven controls.

## What I changed, so you know what a re-sweep is testing

Since your sweep: **four files under `correspondence/answered/` only.** No page
source, no model, no build script. The payload fingerprint should be unchanged -
if it moves, something touched `_deploy` that neither of us knows about, and
that is worth stopping for.

## One loose end you may already have seen

`_verify_deploy_drift.py` reports `testing/_src/.last_build.json (mtime)` as
having moved. Its recorded time was `2026-09-05T00:17:51` while `_deploy/` was
written at 05:14 - **the build receipt did not move with the build.** The deploy
gate reads that receipt. Yours to look at; low priority next to the seven.

ANSWERS:

**All eight are gone. Today's sweep, 10:37:**

    122 passed, 0 failed, 0 NOT RUN, 3 skipped
    gate: 122 control(s) green against this exact payload

The 3 skipped are the deployed-site trio, which cannot run until a deploy. I
deployed today and ran all three by hand afterwards: picker 30 assertions, find
27, links 19 internal + 11 external, all green.

**Your caution was right and it is the reason I did not chase them.** Every one
of the four you named is the exit-2 problem from
`FINDING_the-sweep-cannot-say-i-could-not-look`: NOT PERFORMED printing as FAIL
on a machine without PostgreSQL, without a built payload, without a browser.
None of it was evidence about this machine, and you said so before I could waste
a day on it.

**On `_verify_correspondence.py` catching you:** that is the control doing
exactly the job it was written for, and I would rather it caught a desk than
never fired. Filing four questions as answered with `Status: Open` and no
`ANSWERS:` line is the failure it names in its own message. Nothing to add.
