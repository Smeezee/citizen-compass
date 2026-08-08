# Update — item 9 done: unreleased-content filter and guard (2026-08-07)

## The correction: this is NOT a live leak

C2's list says *"Contract-derived pages may be advertising unreleased missions
right now."* **They are not, and I checked before building anything.**

Nothing published reads the contract tables. The only file in the repo that
touches contract fields is `scripts/split_craft_pages.py`, which uses
`mission_type` and writes to `data-layer/processed/` — never to `releases/`,
`static/` or `testing/_deploy/`. The flagged records sit in `data-layer/derived/`,
which is not served.

So the exposure is **prospective, not live**. Saying otherwise would have been
easy and wrong. What is true is that this is the cheap moment to fix it — before
the first contract page ships rather than after.

## The size of it, measured

    contracts_full.json        5,107 records   958 not_for_release   22 work_in_progress
    contracts_by_system.json   5,108 records   959 not_for_release   22 work_in_progress

**959 of 5,107 — 18.8%, nearly one in five.** Both flags are real Python bools
in the current data, sampled across 2,000 records.

Note the derived tables are **correct** to carry these flags. They are a
faithful record of what is in the game files, and stripping them at derivation
time would destroy the evidence that a record is unreleased. The filtering
belongs at publication time, which is where it now is.

## What was built

**`scripts/publication_filter.py`** — the single definition of "may this be
published", per rule 14. `is_publishable`, `unreleased_reasons`, and
`filter_publishable`, which returns **both** halves on purpose: "we withheld 959
records" is a number a publisher should log and a reviewer should be able to
check. A filter that silently drops rows is indistinguishable from a filter that
never ran.

**`unreleased_content_check`** in `checks/file_checks.py`, registered in
`CHECKERS`. Scans `releases/`, `static/` and `testing/_deploy/` for any record
carrying the flags, walking nested structures rather than assuming a flat array.

**The important design decision:** when it finds no contract corpus, it reports
**LIMITATION, not PASS.** A checker that scans published output, finds no
contract records because none are published, and calls that a pass is reporting
clean for a corpus it never had — the same shape as `integrity_scan` globbing
`*.json` and passing over files it never opened. Run against the repo right now
it says, correctly:

> scanned 0 published .json file(s) … but also no contract-shaped corpus to
> examine at all. This is reported as NOT PERFORMED rather than PASS.

## Proven before trusted — `checks/_verify_unreleased_content.py`, 19 checks

Highlights of the negative controls:

- **The truthiness trap.** `bool("false")` is `True` in Python. The test first
  proves the trap is real, then proves the filter does not fall for it — a plain
  truthiness check would have withheld a publishable record, or with the flags
  inverted, published a withheld one.
- A flagged record in a published file → **DEFECT**, and the finding **names**
  the record.
- The same corpus run through the filter → no DEFECT.
- A flagged record nested three levels deep → still caught.
- An unparseable file mentioning the flags → **WARNING**, never a pass.
- No corpus → **LIMITATION**, and never PASS.

## Verification

- Both new checkers registered: 19 checkers across the file and source groups.
- Existing suite unaffected — `_verify_missing_encoding.py` still passes 19/19.
- Rule 15: `missing_encoding_check` reports **zero** violations in any file I
  added.

Nothing committed, nothing pushed, nothing moved or deleted.
