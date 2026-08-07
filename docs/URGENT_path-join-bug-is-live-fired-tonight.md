# The path-join bug is LIVE — it fired again tonight, 03:32

    from   C2, 2026-08-06
    for    C1 -> Claude Code
    refs   docs/REPORT_full-data-layer-dig-and-two-corrections.md §8
           docs/REPORT_full-dig-part2-images-raw-dismantle.md §9

**I reported three malformed directories as historical evidence of a
path-construction bug. They are not historical. It happened again during
tonight's UEX commodity pull.**

## The new evidence

    data-layer/external-sources/uexcorp/snapshots/
      20260801T235530Z/                          (dir, correct)
      20260806T033315Z/                          (dir, correct)
      20260806T033217Z.pullstderr.log      98 bytes    <- WRONG
      20260806T033217Z.pullsummary.json     0 bytes    <- WRONG

**Both were written at 03:32, from the aborted `033217Z` run**, as *siblings* of
the snapshot directories rather than inside one. The correct names are
`20260806T033217Z/_pull_stderr.log` and `.../_pull_summary.json` — note that the
separator AND the leading underscore are both gone.

**That is the same failure as the three malformed top-level directories:**

    data-layerexports
    data-layerprocessedhardpoints_by_type
    data-layerrawhardpoints/ship_specs.json

**Same shape — path segments concatenated with the separator stripped. Four
occurrences now, and one of them is twenty minutes old.**

## Why this matters more than tidiness

**The `.pullsummary.json` is zero bytes.** So the aborted run produced an empty
artifact at a path nothing reads back from. **A run that fails partway leaves no
recoverable record of what it did** — which is exactly the class of defect this
project closed for the checker lifecycle ("a checker that stopped running must
never look like a problem that went away").

**And it lands inside `snapshots/`.** Anything that enumerates that directory
expecting snapshot folders now has to defend against files. **A sealed-snapshot
model whose snapshot directory can contain loose files is one bad glob away from
a gating check reading the wrong thing.**

## What to do

1. **Find the join.** Likely a `+` or an f-string where `os.path.join` or
   `pathlib` belongs, in the pull path that writes `_pull_stderr.log` and
   `_pull_summary.json`. The `.partial` / rename flow is the place to look —
   the good runs land correctly, so it is the abort path that is wrong.
2. **Fix it with a construct that cannot produce a wrong path**, not with a
   corrected string. **Rule 12 applies: the fix is one that cannot fail, not one
   that happens to be right today.**
3. **Then clean up.** Move the two orphans into `_to_delete/`, along with
   `data-layerexports` and `data-layerprocessedhardpoints_by_type` (both empty).
   **Do NOT bin `data-layerrawhardpoints/ship_specs.json`** — it is real ship
   spec data (`uuid`, `game_name`, `slug`, `class_name`, `port_tags`,
   `sizes{length,beam,height}`). Check it against `data-layer/raw/` first.
4. **Add a gate:** `snapshots/` contains directories only. **That check can
   fail, which is the point.**

## Not verified

- **Which script writes it.** I have not read the pull code — C2 does not write
  to the repo and did not want to guess at a line number without reading it.
- **Whether the `033217Z` run's failure is itself worth investigating.** It
  aborted, then `033315Z` succeeded a minute later. **The stderr log is 98 bytes
  and nobody has read it.**
