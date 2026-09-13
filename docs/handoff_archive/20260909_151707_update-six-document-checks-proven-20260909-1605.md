# Update — the six document checks are proven able to fail. 31 cases, both directions

**2026-09-09 16:05 CDT.** Build tray item 2 is closed. Rule 12 is satisfied and
the numbers the order asked for are below.

## THE PROOF

`checks/_verify_document_checks.py` — 31 cases, **all green**, `--self-test`
exits 1 as the convention requires.

    state_document_agreement    5/5      finding_resolution_marker   5/5
    derived_number_freshness    5/5      published_patch_currency    4/4
    sweep_runtime_drift         5/5      named_thing_exists          7/7

Every one of the six has now been **seen to go red** on planted input: a document
naming a path that was never written, a FINDING with its status line removed, a
state file made older than its sibling, a page stating 4.9 against a 4.10
manifest, a sweep that took ten times as long, and a derived artifact whose
inputs moved underneath it.

**And seen to stay silent on the near-misses**, which is the half that decides
whether anybody keeps it: a bare filename, prose containing a slash
(`Freelancer_DUR/MAX/MIS`), a glob, an exempt namespace, an archived document, a
5% sweep wobble, a 10s→20s move that is 100% and still says nothing, and a
pre-cutoff FINDING that must never be a DEFECT.

Nothing is planted in the real repository. Each case builds a throwaway tree
under `tempfile` and hands that to the checker as `repo_root`.

## THE PROOF FOUND A REAL DEFECT IN MY OWN CODE, WHICH IS THE POINT

Two of the six keep a small sidecar so they have something to compare against.
Both wrote it with `Path.write_text` **without creating the parent directory**.
On this machine `checks/` exists, so it worked here and would have worked
forever — and on any tree where it did not, the baseline would have silently
failed to persist and **every run would have reported "first run, nothing to
compare" indefinitely.** A check that can never reach its second run is a check
that can never fail. Caught by the harness, fixed, re-proven.

## THE COST, MEASURED, BECAUSE THE ORDER ASKED

    the six, in the auditor layer      0.618s total
      state_document_agreement          0.249s
      derived_number_freshness          0.253s
      named_thing_exists                0.067s
      finding_resolution_marker         0.036s
      published_patch_currency          0.013s
      sweep_runtime_drift               0.001s

    added to the DEPLOY SWEEP            0.0s   nothing in the sweep calls them
    _verify_document_checks.py in sweep  0.4s   the rule 12 proof, discovered
                                                as _verify_*.py and swept

**The first version of `state_document_agreement` took 19.4 seconds.** It used
`Path.rglob` over the whole tree, and this repository holds ~29,000 files cloned
from third-party sources — a bare rglob walks every one. Pruned to the
directories that could actually hold a state document: **19.4s → 0.25s, same
finding.** Measured before and after, not assumed.

## RUN FOR REAL THROUGH THE LAYER THAT WILL RUN THEM

`python run_checks.py --group file` — the same entry point
`run_checks_scheduled.ps1` uses. All six executed and wrote where that layer
already writes: 11 rows into
`logs/pipeline_check_results_fallback.jsonl` (no DB reachable from here, so they
queue as every other checker's findings do).

`checks/_verify_rule16_labels.py` is green: **127 checks labelled, 0 unlabelled,
0 malformed.** The new control declares `RULE16: UNPROVEN` and says why — it asks
the checkers about repositories it planted, so a checker whose idea of "a path
that exists" is wrong is wrong on both sides. Rule 12 and rule 16 are different
axes and the header says so.

## TWO NEW GITIGNORE ENTRIES

`checks/.derived_freshness.json` and `checks/.sweep_runtime_history.json` — the
memories those two checks need. Both are machine state about THIS working copy,
filed beside `checks/.last_sweep.json` for the same stated reason: a committed
baseline would describe somebody else's tree and report drift that never
happened.

## WHAT THEY FOUND, WHICH IS NOT MINE TO FIX

**Number 6 is GREEN on `CLAUDE.md`.** It has not found a second one there — the
answer Architecture asked for explicitly.

Five other documents name 21 repo-relative paths that are not on disk, and one
ownership register still points at a state file that moved. **The auditor layer
flags; it never edits.** Those belong to the desks that own those documents and
are named in the memo answer.

**Nothing committed.**
