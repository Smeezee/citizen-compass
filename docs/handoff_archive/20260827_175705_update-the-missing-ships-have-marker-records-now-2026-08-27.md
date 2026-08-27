# Update — The 19 new ships had no marker records at all. They do now. Please build and deploy.

**C1, 2026-08-27 19:04 local.** Sleven: *"whatever it takes to get everything
updated and done on the test page now."*

## The thing nobody had noticed

`hardpoints_fleet.json` decides which hulls get hull markers. It holds **178
records**. The nineteen ships imported today are **not in it** — Mantis,
Tiburon, M80, 85X, Basher, Fury, Pitbull, Tyilui, Starlite and the rest.

**That is why those ships show no dots.** Not a marker bug. A missing record.

**And it cannot be regenerated. `place_fleet.py`, its single writer, IS NOT IN
THIS REPOSITORY.** I looked for it before proposing anything. So "re-run the
generator" was never available to either of us, and I had been telling Sleven it
was your lane. It was nobody's — the tool is gone.

## What I did instead

`build_hardpoint_overlay.py` now emits a SECOND, ADDITIVE file:

    data-layer/derived/holo-hardpoints-align/fleet_records_client.json
    29 hulls, 2,486 ports

Built from **CIG's own transforms**, not from a name-derived guess — so these
arrive *better* placed than the records they are joining, not worse.

**It does not write `hardpoints_fleet.json`.** One writer per artifact, and a
second file is reversible by deleting it. Same pattern the alignment overlay
already uses, for the same reason.

## One block added to `build_deploy.py`, and it refuses rather than merges

Right beside the client-overlay block I added at 12:47. It merges the new
records **and exits the build outright if one would overwrite a hull the
dataset already has:**

    client fleet record would overwrite an existing hull (X) - refusing.
    This file is additive only.

**Additive-only is the whole safety property**, so it is enforced rather than
intended. Move or rewrite the block as you see fit — it is your file and I am
handing it straight back.

## What I need — this is the ask

**Build and deploy.** Everything from today is sitting in source and none of it
is on the testing site:

    the 29 new marker records          Mantis, Tiburon, M80, Fury, Basher...
    93 hulls of real CIG hardpoints    952 ports, unchanged and already proven
    the swap loop's Undo and ledger    M2
    compare-on-what-the-part-is-for    M2b
    the camera no longer zooming out   the defect Sleven reported directly
    the see-through picker panel       the other thing he asked for

**Check the build's own line first:** `client marker records added for 29
hull(s)`. If that prints 0, the file is not being read and the ships will still
be empty — and that is worth catching before the deploy rather than after.

**Then check the Mantis on the served page.** It is one of the two ships Sleven
opened at random this morning and found completely empty. If it has dots, today
worked.

*C1*
