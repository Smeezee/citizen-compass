# Update — Sleven: *"run it with the corrected filter"*. Running it, and writing down the authority before I do.

**2026-08-27 22:06 local · Code (background session)**

## Why I am running a rule 1 action

Hard rule 1 says **"Sleven deletes it himself"**, and at 22:02 I reported rather
than ran, on exactly that basis.

**He has now told me to run it, in this session, in this message, for this
specific action, with the corrected filter I proposed.** That is the same
standard rule 2 sets for a commit — *"Sleven saying so, in that message, for that
change"* — and it is met. The rule exists so that Code does not decide what goes;
Sleven has decided.

## The guard I am adding on top of the order's

The order's own stop condition is a count and a size. Mine is stricter: the
script **recomputes the selection and refuses to touch anything** unless it
matches what I measured and reported at 22:02 —

    160 items, 2.89 GB, holding 20260827T030607Z_source1_git by name

If the disk has moved since (a control writing a new attic, C1 moving something
aside), the numbers change and it stops without recycling a single item. **The
cutoff is not widened and is not a parameter.**

## Rule 4, and why there is no backup step

*"Take a verified backup before anything destructive or irreversible."* This is
neither. Every item goes to the Recycle Bin, `NukeOnDelete = 0` on every volume,
bin capacity 13–192 GB against a largest item of 1.55 GB, 495 GB free — all
measured at 22:00. **The Recycle Bin IS the backup**, and backing up the attic
would be backing up a backup.

## Rule 5, and the list

Bulk work gets a report-only pass first, and it had one — the 22:02 note carried
the count and the size and Sleven has seen it. The run below prints **every item
by name, size and date before it touches anything**, so the record of what went
is itemised rather than a total.
