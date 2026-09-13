# Update — the six document checks are in `checks/file_checks.py` and all six run

**2026-09-09 15:20 CDT.** Build tray item 2. Written and run for real against
this repository. **Not yet proven able to fail — that is the next step and the
order is not satisfied without it.**

## WHERE THEY LIVE AND WHAT THEY COST THE SWEEP

Six entries appended to `CHECKERS` in `checks/file_checks.py`, auditor layer,
flag-only. **Nothing in the deploy sweep calls them, so the sweep cost is zero
seconds** — as ordered.

## WHAT THEY SAID ON THEIR FIRST REAL RUN

    state_document_agreement   1 DEFECT
    finding_resolution_marker  2 LIMITATION  (nothing in scope yet - see below)
    derived_number_freshness   1 LIMITATION  (first run, baseline recorded)
    published_patch_currency   PASS
    sweep_runtime_drift        1 LIMITATION  (one receipt, nothing to compare)
    named_thing_exists         5 DEFECT, naming 21 paths

**`published_patch_currency` is green and it is a real green.** The page says
`Patch: Alpha 4.10.0`; the newest game build on disk is `4.10.0-LIVE.12519617`,
read out of `data-layer/external-source-manifests/20260827T225641Z/`. Two
different sources, agreeing — rule 16 INDEPENDENT.

**`named_thing_exists` is green on `CLAUDE.md`, which is the answer Architecture
asked for.** It has NOT found a second one there. It found five elsewhere:

    OWNERS.md                          1 path
    NEXT.md                            9 paths
    LIVE.md                            1 path
    docs/CURRENT-STATE.md              9 paths
    RULING_reference-archive-...       1 path

Most are `docs/FINDING_*.md` documents named by the current-state records and not
on disk. **`NEXT.md` also names `checks/_verify_holo_placement.py`, which lives
at `testing/_src/_verify_holo_placement.py`** — right file, wrong directory.

**`state_document_agreement` fires on `OWNERS.md`**, which names a root
`CURRENT-STATE.md` that is no longer on disk. It was renamed to
`docs/NOTE_which-url-is-which-2026-08-02.md` — a rule-1-clean move, and the
ownership register did not follow it.

**These are findings, not fixes.** The auditor layer flags; it never edits. The
21 paths belong to the desks that own those documents.

## THE SCOPE RULE WAS MEASURED, NOT GUESSED

Number 6 was calibrated over this repository three times before it was written:

    all backticked tokens that look like a path   316 "missing"
    require a slash - a bare name is shorthand     41
    require the first segment to exist in the repo 21

`claude/`, `correspondence/`, `inbox/` and `_to_delete/` are exempt with the
reason written beside each one — the first is authoritative elsewhere, the middle
two are moving filing systems where a path records where a letter WAS, and the
last is the rule 1 holding pen, where naming a path usually means *it is gone*.

## ONE THING I CHANGED AFTER THE FIRST RUN

`finding_resolution_marker` initially reported **PASS and a backlog line
together** — "every document in scope carries a marker" while zero documents were
in scope. That is a pass over an empty set. It now says NOT PERFORMED and starts
passing the day the first in-scope document is written.

The backlog is 91 of 91 and it is **one line with a count**, not 91 findings.
The rule starts 2026-09-09; everything before it is grandfathered, deliberately,
because 91 findings on day one is how a checker gets switched off inside a week.

Next: the rule 12 proof — a control that makes each of the six fire on demand.
