# BUILD AND DEPLOY NOW. My last note said "no urgency" and that was wrong.

**2026-08-27 19:25 local · C1** — read from `date`, not estimated.

## Correcting myself first

`update-one-more-rebuild-the-frame-fix-landed-after-your-deploy` ended with
**"one more build and deploy, no urgency."** You read it at 19:03, finished the
subject-gate item you were already on, filed it at 19:06, and stopped. **That is
exactly right and my wording caused it.**

Sleven's standing instruction has not changed since this morning: everything
done that day reaches the test page that day. **"No urgency" was mine to invent
and it was not mine to invent.** Ignore it.

## Do this now

    python testing/_src/build_deploy.py
    powershell -ExecutionPolicy Bypass -File .\scripts\deploy_testing.ps1

**Read these before the upload:**

    client marker records added for 30 hull(s) the dataset had none for
    client hardpoint overlay: 955 port(s) moved onto CIG positions
    disclosure CSS: shared from _disc.css into index.html, keybinds.html,
                    loadout.html, find.html

**30 and 955.** Your last deploy carried 29 and 952 — correct at the time, half
an hour before my frame fix landed.

## The one thing that can stop you, and what it means

The placement script now reconciles its own output directory and **exits fatally
if it cannot delete a stale file**. I already moved 93 stale files into
`_to_delete/hardpoint-placement-stale-2026-08-27/` from this side, so the
directory is clean: 146 files against a manifest of 146.

You should not need to run `build_hardpoint_placement.py` at all — its output is
already current on disk. If you do run it, expect
`removed N output(s) from an earlier run`. If it stops you instead, that is the
guard firing correctly and the message names the files.

## What to check after the deploy

**The M2 Hercules.** It had no marker record at all and should now show 12 dots.
It is the ship the whole frame fix came out of, and it is the one that proves
this build did something the last one did not.

The Mantis already had its 6 on your last deploy — no need to re-check it.

Nothing commits or pushes to the live site without Sleven's explicit go-ahead.
Testing only.

— C1
