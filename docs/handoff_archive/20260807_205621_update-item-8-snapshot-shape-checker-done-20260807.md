# Update — item 8 done: `snapshot_shape` checker, and the count was wrong (2026-08-07)

## The correction that matters: there is no code to fix

C2's `URGENT_path-join-bug-is-live-fired-tonight.md` treats this as a
path-construction bug in the pipeline. **It is not, and I could not find any
committed code carrying it.**

`uex_corp.py` does not write `_pull_summary.json` or `_pull_stderr.log` at all.
It documents `python uex_corp.py <output-dir>`, prints the summary to **stdout**
and diagnostics to **stderr**. The redirect into those filenames is done by the
**caller** — and there is no runner script anywhere in this repo. Searched for
one across `.py`, `.ps1`, `.sh`, `.bat`, `.cmd`, `.go`: the only references to
`uex_corp.py` are its own docstring, its verifier, and a manifest builder
recording which script produced a snapshot.

So the malformed names came from a hand-typed shell redirect. **There is no
patch that prevents a recurrence**, which is exactly why this needed a check
rather than a fix. I did not invent a runner script to have something to correct
— per rule 11, an honest gap beats a fabricated cause.

## Five occurrences across three sources, not four across one

The checker found one C2's sweep never reached:

    uexcorp/snapshots/
      20260806T033217Z.pullstderr.log          98 bytes   loose
      20260806T033217Z.pullsummary.json         0 bytes   loose AND empty
    api.star-citizen.wiki/snapshots/
      20260731T031754Z.partial/_fetch_metadata.json       0 bytes   correct path
      20260801T015346Z.partial.aborted__pagesize50/
                              _pull_summary.json          0 bytes   correct path
    scunpacked-data/snapshots/
      20260731T041451Z.partial.fsck_output.log  0 bytes   loose AND empty   <- NEW

The new one is the worst of the set. `20260731T041451Z.partial.fsck_output.log`
should have been `20260731T041451Z.partial/fsck_output.log` — same shape, the
separator replaced by a `.`. And it is **an fsck output log that is zero bytes**.
An integrity check whose output is empty is indistinguishable from an integrity
check that found nothing wrong.

The shape is consistent across all three sources: the path separator became a
literal `.`.

## What was built

`snapshot_shape_check` in `checks/source_checks.py`, registered in `CHECKERS` so
`run_checks.py` picks it up with the rest of the source group. Findings-only —
it never moves or deletes anything, so the cleanup of the five files above stays
Sleven's call under rule 1.

It reports **two deliberately separate defects**, because fixing one leaves the
other standing:

1. **Loose files directly inside `snapshots/`** — that directory holds sealed
   snapshot *directories* only. C2's point stands: a snapshot directory that can
   contain loose files is one bad glob away from a gate enumerating a file where
   it expected a snapshot.
2. **Zero-byte files anywhere in the tree** — two of the five sit at entirely
   *correct* paths. Fixing the path join would leave them exactly as they are,
   just filed more tidily.

## Proven before trusted — `checks/_verify_snapshot_shape.py`, 14 checks

Both directions, on synthetic trees, per hard rule 12:

- a clean tree produces **no** DEFECT (no false positive)
- the real 2026-08-06 malformed filename planted → caught, and the finding
  **names** the file
- a zero-byte file at a **correct** path → still caught, proving the two defects
  are independently detectable
- a non-empty loose file does **not** trip the zero-byte check, and vice versa
- absent root / no `*/snapshots` → **LIMITATION**, never PASS
- the file cap degrades to a LIMITATION naming partial coverage, never to a
  silent pass

Nothing committed. Nothing moved or deleted. Next: item 9.
