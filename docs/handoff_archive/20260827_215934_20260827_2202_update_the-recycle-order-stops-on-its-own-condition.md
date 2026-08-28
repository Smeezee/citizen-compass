# Update — Verified the recycle order. It fails its OWN stop condition, and the command would bin a backup the order says to hold.

**2026-08-27 22:02 local · Code (background session)** — follow-on to 21:58.
**Nothing has been moved, recycled or deleted.**

`docs/FINDING_the-recycle-order-would-bin-a-backup-it-said-to-hold-2026-08-27.md`

## The measurement

    ORDER says                       MEASURED
    SEND   157 items   3.10 GB       161 items   4.20 GB
    HOLD    32 items   5.07 GB        30 items   3.41 GB

The order says: *"If it does not move roughly 157 items and ~3.1 GB, stop and
say so rather than re-running it with a wider date."* **It does not. Stopping.**

## The gigabyte has a name

    20260827T030607Z_source1_git   1.31 GB   LastWriteTime 2026-08-26

**The order HOLDS that folder** — it is one of the five same-day backups, listed
at 1.40 GB as "dated TODAY". Its LastWriteTime is yesterday. The order judged it
by the run id in its NAME; the command filters on `LastWriteTime`. Where those
disagree the command wins, silently, and it bins a same-day backup — the one
trade the order itself says this project should never make.

**The split is sound. The filter does not implement it.**

## A correction to the order, conclusion unchanged

*"Nothing in the repo READS from `_to_delete`"* is not so — `_verify_model_scale.mjs`,
`_verify_marker_positions.mjs` and `_verify_takedown.py` all read it. **All three
are safe under this sweep** and I checked each rather than assuming: their inputs
are either dated today and held, or scratch directories the controls recreate.

Worth correcting anyway, because "nothing reads it" is a premise that gets reused
next month against a different cutoff.

## And one worry I can retire

A too-large item would be permanently deleted rather than binned, with
`OnlyErrorDialogs` hiding the prompt. Checked: `NukeOnDelete = 0` on every
volume, bin capacity 13–192 GB, 495 GB free, largest item 1.55 GB. **No
silent-permanent-delete risk.**

## Rule 1

I am not running it. *"Sleven deletes it himself."* The order uses the VisualBasic
Recycle Bin API rather than `Remove-Item`, which is not on rule 1's list by
name — and the rule's answer to that is *"if you are ever unsure, it is."* The
go-ahead quoted in the order is also Sleven speaking to C1, not here.

The finding carries the corrected command, holding the one mis-sorted folder by
name: **160 items / 2.89 GB**, every same-day backup untouched. Sleven runs it.

## Also unactioned, and neither needs me tonight

- `PROPOSAL_the-marker-pipeline-is-four-layers-deep...` (21:00) — a proposal,
  wants a decision rather than work.
- `FINDING_the-economy-data-we-never-opened...` (21:50) — C1's, informational.
