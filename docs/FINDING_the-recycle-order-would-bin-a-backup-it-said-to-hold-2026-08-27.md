# FINDING — the recycle order's own stop condition fires, and the command would bin a backup the order says to hold

**2026-08-27 22:00 local · Code (background session)**
Verifying `ORDER-send-the-old-attic-to-the-recycle-bin-2026-08-27.md` before
anyone runs it. **Nothing has been moved, recycled or deleted.**

---

## The order's numbers do not match the disk

    ORDER says                       MEASURED just now
    SEND   157 items   3.10 GB       161 items   4.20 GB
    HOLD    32 items   5.07 GB        30 items   3.41 GB
    TOTAL  189 items   8.17 GB       191 items   7.61 GB

The order's own instruction is what settles this:

> **Report the count and the freed space back.** If it does not move roughly 157
> items and ~3.1 GB, **stop and say so** rather than re-running it with a wider
> date.

It does not. **1.1 GB more would go than the order sanctions**, so it stops here.

## And I can name the gigabyte

    20260827T030607Z_source1_git    1.31 GB    LastWriteTime 2026-08-26

**The order lists that folder in its HOLD set**, at 1.40 GB, under the heading
"dated TODAY". Its LastWriteTime is **yesterday**.

The order judged it by the timestamp in its NAME — `20260827T030607Z`, the
snapshot run id — and the command filters on `LastWriteTime`. Those disagree,
and where they disagree the command wins, silently.

**So the command as written bins one of the five same-day backups the order
deliberately held back**, for the exact reason the order gives for holding them:

> Binning a same-day backup to reclaim space is the trade this project should
> never make.

That is not a criticism of the split. The split is sound; the FILTER does not
implement it.

## The other claim in the order needs a correction, though the conclusion survives

The order states: **"Nothing in the repo READS from `_to_delete`."** Measured,
that is not so — three controls read it:

    checks/_verify_model_scale.mjs      reads _to_delete/pre_scale_fix_* and
                                        prints NOT PERFORMED without one
    checks/_verify_marker_positions.mjs uses _to_delete/control_no_overlay
    checks/_verify_takedown.py          enumerates _to_delete/takedown_*

**Every one of them is safe under this sweep, and I checked rather than assumed:**

- all three `pre_scale_fix_*` are dated today and are HELD — so the control that
  would go NOT PERFORMED keeps its input
- `control_no_overlay` is dated today and is HELD
- `_verify_takedown` asserts only that *some* `takedown_*` exists, and it
  performs a real takedown during its own run, so it creates one; three more
  from today are held anyway
- `a2_mark_fixtures` and `a4_takedown_fixture` (2026-08-22) are scratch
  directories those controls recreate each run

**The conclusion holds. The reasoning did not.** Worth fixing in the record
because "nothing reads it" is the kind of premise that gets reused next month
against a different sweep, when one of those three inputs is on the wrong side
of a cutoff.

## One hazard I suspected and can now rule out

A large item that will not fit in the Recycle Bin is **permanently** deleted, and
`OnlyErrorDialogs` would suppress the prompt. Checked:

    NukeOnDelete = 0 on every volume        (nothing bypasses the bin)
    bin capacity  13 GB / 97 GB / 192 GB depending on volume
    free on C:    495 GB

The largest single item is 1.55 GB. **There is no silent-permanent-delete risk
here.** Saying so plainly rather than leaving the worry standing.

---

## HARD RULE 1, and why this is being reported rather than run

> Never delete. Move aside instead. … **Sleven deletes it himself.**

The rule names `rm`, `del`, `Remove-Item`, `rmdir` and `shutil.rmtree`. The
order uses the VisualBasic `FileSystem::DeleteDirectory` API with
`SendToRecycleBin`, which is not on that list by name — and the rule's answer to
exactly that is *"if you are ever unsure whether an action falls under one of
these, it does."*

Removing 3–4 GB from the repo directory is what rule 1 exists to stop, whatever
the API is called. The quoted go-ahead in the order is also **Sleven speaking to
C1**, not in the session that would run it.

## What to run, when Sleven wants it run

The date is the safeguard and must not be widened. Holding the one mis-sorted
folder by name makes the command match the order's own split:

    Add-Type -AssemblyName Microsoft.VisualBasic
    $repo = "C:\Users\david\citizen-compass\_to_delete"
    $cut  = Get-Date "2026-08-27 00:00"
    $hold = @("20260827T030607Z_source1_git")   # named TODAY, stamped yesterday
    Get-ChildItem -LiteralPath $repo -Force |
      Where-Object { $_.LastWriteTime -lt $cut -and $hold -notcontains $_.Name } |
      ForEach-Object {
        if ($_.PSIsContainer) {
            [Microsoft.VisualBasic.FileIO.FileSystem]::DeleteDirectory($_.FullName,'OnlyErrorDialogs','SendToRecycleBin')
        } else {
            [Microsoft.VisualBasic.FileIO.FileSystem]::DeleteFile($_.FullName,'OnlyErrorDialogs','SendToRecycleBin')
        }
        Write-Host "recycled $($_.Name)"
      }

That moves **160 items / 2.89 GB** and leaves every same-day backup where it is.

**Sleven runs it.** In this session, prefixing it with `!` puts it in his hands
with the output landing here.
