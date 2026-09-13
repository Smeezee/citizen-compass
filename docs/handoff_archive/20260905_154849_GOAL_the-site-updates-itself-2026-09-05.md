# GOAL — Citizen Compass keeps itself current, without anyone driving it

Stated by Sleven, 2026-09-05. **Direction, not scope.** Nothing is to be
designed or built against this yet, and no current work is to be justified by it.

## The goal in his words

The system updates itself every time the game patches, and every time new
information appears that can be tracked.

## What it means when the time comes

- A game patch lands, the pipeline notices, pulls what changed, and refreshes
  the site with nobody starting it.
- New trackable information appears and is picked up on its own, not on someone
  remembering to look.
- No manual step in the normal path. A person rules on what is ambiguous; they
  do not run the machinery.

## Why it is filed and not started

The pieces it would stand on are unfinished. The model pipeline does not work,
the deploy is driven by hand, and the verification layer that would have to gate
an unattended refresh - `last_verified_patch`, the auditor and its results
table, the claim register - is only partly built. **Automation on top of a
pipeline that is not correct produces wrong data faster.**

## Also recorded in

The claude.ai project (`claude/GOAL_the-site-updates-itself-2026-09-05.md`) and
in memory under `citizen-compass-automation`, so it survives this repo, this
chat and this session.

**Do not open this as a work item until Sleven says so.**
