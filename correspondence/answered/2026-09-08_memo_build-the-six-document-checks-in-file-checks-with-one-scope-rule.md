# Memo

To:      Build
From:    Engineering
Date:    2026-09-08
Status:  Answered
Subject: six document checks into `checks/file_checks.py` — Sleven asked for them, the audit desk designed them, and the sixth needs a scope rule

**Sleven's ruling: he asked for a repeatable way to fact-check the project's own
files, was offered automatic checks or a standing manual pass, and answered
BOTH.** The proposal is
`claude/PROPOSAL_check-the-documents-2026-09-08.md` in the claude.ai project and
it is worth reading — it ties every check to an incident that already happened.

**They go in the auditor layer, NOT the sweep.** Entries appended to `CHECKERS`
in `checks/file_checks.py`, on the existing schedule, flag-only, writing where
that layer already writes. **Zero seconds added to the deploy sweep.**

## THE SIX

    1  state_document_agreement    the files claiming to be current state
                                   disagree, or onboarding points at the older
    2  finding_resolution_marker   a FINDING_*.md with no OPEN / CLOSED /
                                   WITHDRAWN line and a date
    3  derived_number_freshness    a number meant to be regenerated has stopped
                                   moving
    4  published_patch_currency    the patch the public page states is behind
                                   the newest patch we know of
    5  sweep_runtime_drift         a full sweep's time moves materially against
                                   the previous receipt
    6  named_thing_exists          a document names a file, folder or tool that
                                   is not there

**Number 5 is no longer held.** It waited on the receipt recording per-control
times; that landed today.

## THE SCOPE RULE ON NUMBER 6 — IT IS NOT OPTIONAL

**History is allowed to name dead paths. Current documents are not.**

`docs/handoff_archive/` holds 773 documents that correctly describe a repository
that no longer exists. **A check firing on those produces hundreds of correct,
useless findings and gets switched off inside a week.**

**Scope it to documents asserting a PRESENT state:** `CLAUDE.md`, the doctrine,
`docs/CURRENT-STATE.md`, `OWNERS.md`, `NEXT.md`, `LIVE.md`, and the
`DECISION_*` / `RULING_*` set. **Repo-relative paths only** — no URLs, no
external tools, nothing outside the tree.

## ONE INSTANCE IS ALREADY FIXED, SO NUMBER 6 SHOULD BE GREEN ON IT

`CLAUDE.md` said the retired Python files were moved to
`_to_delete/python_handoff_path_retired_20260801/`. **That folder does not exist
and the files are nowhere on disk.** They are in git at `5081be4`. I corrected
the paragraph to name the commit.

**If number 6 still fires on `CLAUDE.md` after that, it has found a second one
and I want to know.**

## EVERY ONE MUST BE PROVEN ABLE TO FAIL

Rule 12. **Each checker gets a case that makes it fire** — a document naming a
path you delete, a FINDING with its status line removed, a state file made older
than its sibling. **A checker nobody has seen go red is a checker nobody will
believe when it does.**

## AND THE LIMIT, FROM THE PROPOSAL, WHICH I AM MAKING PART OF THE ORDER

**A check that flags constantly becomes wallpaper.** Each of these must be quiet
when things are fine. **A noisy checker is removed rather than tolerated** —
that is the instruction, not a preference, and it is Section 42's ceremony trap
in a different coat.

ANSWERS:

**Built, run, and proven able to fail. 2026-09-09.**

Six entries appended to `CHECKERS` in `checks/file_checks.py`, auditor layer,
flag-only, writing where that layer already writes. **Zero seconds added to the
deploy sweep** - nothing in the sweep calls them. Measured, not assumed.

## THE SIX, AND WHAT EACH DECIDES ON

    1  state_document_agreement   three arms: two state documents with no
                                  pointer between them; onboarding naming a
                                  state document that is NOT ON DISK; onboarding
                                  naming the OLDER of two. Arm three is your
                                  2026-09-07 incident exactly.
    2  finding_resolution_marker  Status:/Resolution: reading OPEN, CLOSED,
                                  WITHDRAWN or SUPERSEDED, AND an ISO date.
                                  Both, because a status with no date does not
                                  say when it became true.
    3  derived_number_freshness   content hashes, not modification times - a git
                                  checkout stamps every file and an mtime check
                                  could never fail on demand. Inputs moved and
                                  the output did not is the DEFECT.
    4  published_patch_currency   the page's 'Patch: Alpha X.Y.Z' against the
                                  upstream commit subject in the newest source
                                  manifest. Two sources, neither derived from
                                  the other.
    5  sweep_runtime_drift        it keeps its own rolling history of the last
                                  20 receipts, because .last_sweep.json is a
                                  SINGLE receipt with nothing to compare
                                  against. It never writes the receipt - rule
                                  14, the sweep owns that file.
    6  named_thing_exists         the scope rule, below.

## NUMBER 6 IS GREEN ON `CLAUDE.md`. IT HAS NOT FOUND A SECOND ONE

You asked to be told. It has not. Your correction holds.

## THE SCOPE RULE, MEASURED THREE TIMES BEFORE IT WAS WRITTEN

    every backticked token that looks like a path      316 "missing"
    require a slash - a bare name is shorthand          41
    require the first segment to exist in the repo      21

`build_deploy.py` and `.glb` are shorthand and file extensions.
`Freelancer_DUR/MAX/MIS` and `wheelFL/FR/BL/BR` are prose that happens to
contain slashes - both are real strings out of this project's own documents.

Four namespaces are exempt with the reason written beside each: `claude/`
(authoritative elsewhere), `correspondence/` and `inbox/` (MOVING filing systems
- a path records where a letter WAS), and `_to_delete/` (the rule 1 holding pen,
where naming a path usually means IT IS GONE, the opposite of what this tests).

Present-state documents only, exactly as you scoped it. The 773 archived
handoffs are untouched.

## WHAT IT FOUND - 21 PATHS ACROSS FIVE DOCUMENTS, PLUS ONE STALE POINTER

    NEXT.md                  9   incl. `checks/_verify_holo_placement.py`,
                                 which is real but lives at
                                 `testing/_src/_verify_holo_placement.py`
    docs/CURRENT-STATE.md    9   mostly docs/FINDING_*.md that are not on disk
    OWNERS.md                1   docs/PROPOSAL_the-marker-pipeline-is-four-
                                 layers-deep-2026-08-27.md
    LIVE.md                  1   docs/FINDING_the-live-site-was-a-month-wrong-
                                 about-the-patch-...-2026-08-30.md
    RULING_reference-archive 1   models/100i.glb

**`state_document_agreement` fires once, on `OWNERS.md`**, which still names a
root `CURRENT-STATE.md`. That file was renamed to
`docs/NOTE_which-url-is-which-2026-08-02.md` - a clean rule 1 move - and the
ownership register did not follow it.

**These are flags, not fixes.** The auditor layer never edits. They belong to the
desks that own those documents.

## RULE 12 - EVERY ONE HAS BEEN SEEN TO GO RED

`checks/_verify_document_checks.py`, 31 cases, all green, `--self-test` exits 1.
Each of the six fires on planted input and stays silent on the near-misses its
scope rules exist to exclude. Nothing is planted in the real repo - every case
builds a throwaway tree under `tempfile`.

**The harness caught a real defect in my own code.** Two of the six keep a
sidecar baseline and both wrote it without creating the parent directory. Here
`checks/` exists so it worked; anywhere it did not, the baseline would silently
fail to persist and every run would report "first run, nothing to compare"
FOREVER. A check that can never reach its second run can never fail. Fixed and
re-proven.

## THE NOISE LIMIT, TAKEN AS THE ORDER RATHER THAN ADVICE

**91 of 91 FINDING documents carry no resolution marker.** Firing 91 times on day
one is exactly how a checker gets switched off inside a week, so the rule starts
2026-09-09 and everything before it is **one LIMITATION line carrying a count
that should only ever go down.**

Number 2 also refuses to report PASS while nothing is in scope. Its first draft
said "every document in scope carries a marker" over a scope of zero - a pass
over an empty set, and the same shape as a glob that matched nothing. It says NOT
PERFORMED and starts passing the day the first in-scope document is written.

## COST

    the six, auditor layer     0.618s total   (worst: 0.249s)
    added to the deploy sweep  0.0s
    the rule 12 proof, swept   0.4s

The first `state_document_agreement` took **19.4 seconds** - `Path.rglob` over a
tree holding ~29,000 third-party files. Pruned to directories that could hold a
state document: 19.4s -> 0.25s, same finding.

Two gitignore entries added for the sidecars, filed beside
`checks/.last_sweep.json` with the same reasoning.

Nothing committed.
