# Update — mirror check rebuilt: per-file, non-tautological, proven against real known-bad data

**When:** 2026-08-05

New: `scripts/Verify-MirrorTree.ps1`. Step 7b of `Backup-CitizenCompass.ps1` now
calls it instead of comparing aggregates.

## Why the old check was not a check

Two independent defects, both now fixed:

1. **Aggregates cancel.** A file count plus an MB total can both match while the
   contents are wrong — two files differing by +2 MB and −2 MB sum to a pass.
2. **A truncated file is invisible to a count.** It is *present*, so the count
   matches.

## Not tautological — enforced structurally

The verifier is a **separate script run as a separate process**. It shares no
filter state with the copy, so it cannot compare the copy to itself. It:

- enumerates the **destination from disk** — never from `SHA256SUMS.txt`, never
  from robocopy's log, never from the copy's own file list;
- compares **per file, on relative path AND byte size**;
- **names the first 10 mismatches** with both sizes and the delta, not just a
  count.

## Two controls, because a checker that reads nothing passes everything

- **POSITIVE** — a known-*included* file must be found at the destination. If
  this fails, the enumeration is empty or aimed at the wrong path and no verdict
  below it means anything.
- **NEGATIVE** — a known-*excluded* file (something under `.cache`) must be
  **absent**.

The negative control is **only credited when the positive control passed**,
otherwise "absent" is vacuous. Where no excluded file exists to test with, it is
reported **NOT PERFORMED** — never as a pass.

## Proven to fail, on real data rather than a fixture

The killed run left genuine known-bad input, which is better evidence than
anything synthetic:

| Target | Result |
|---|---|
| **Killed run** `20260805-204113` external-sources | **FAIL, exit 1** — `MISSING from destination: 44428` of 58,257, first 10 named. Positive control passed, so it demonstrably *was* reading the destination. |
| **Good run** `20260805-205238` sc-ships | **PASS** — all **951** files present, byte sizes matching. **Both controls fired:** positive `Liberator\model.glb` present; negative `.cache\huggingface\trees\aed8d04c…json` **absent** — proving `.cache` was genuinely excluded rather than assumed. |
| **Good run** external-sources | **PASS** — all **58,257** files present with matching byte sizes. Negative control honestly reported *not performed* (that tree contains no excluded dirs). |

**One honest correction to the prediction.** The expectation was that the killed
run would leave a *truncated* file. It did not — it left 44,428 files **missing**
and **zero** size mismatches. robocopy evidently does not leave partials behind
in this mode. The per-file size comparison is still the right check and stays,
but I did not catch a truncation, and I am not going to claim I did. What the
check actually caught was mass absence that the old aggregate check would have
flagged too — the size dimension remains **unproven against a real partial**,
and is recorded as such rather than as demonstrated.

## `/MIR` — not used, and why

The instruction specified `/MIR`. I used **`/E`** and am flagging it rather than
silently substituting.

`/MIR` deletes anything at the destination that is not at the source. This
script's header states as a **guarantee** that it "contains no delete operation
of any kind… robocopy is called with /E, never /MIR", and CLAUDE.md hard rule 1
is never delete. Using `/MIR` would break both.

**The stated reason for `/MIR` was resumability, and `/E` already has it.**
Measured, not assumed — re-running `/E` against the completed mirror:

```
elapsed: 1.1s   exit code: 0
Files :  951   Copied: 0   Skipped: 951   Bytes: 7.392 g skipped
```

It re-scanned 7.4 GB and copied nothing in about a second. A killed run restarts
cheaply. Nothing is gained by `/MIR` except the ability to destroy. Say the word
and I will switch it.

## robocopy's exit code is now reported and decoded

It is a bitmask, and it is printed in full: 1 = files copied, 2 = extra at
destination, 4 = **mismatched**, 8 = **some files could not be copied**, 16 =
**serious error**; 0 = nothing to do. **Anything ≥ 8 is FATAL regardless of what
the file counts say**, and the copy is abandoned for that tree before
verification even runs.

If the verifier cannot run at all (script missing) that is reported as **not
verified**, never as passed.

## The timeout was structural

7.5 GB will not finish inside a 10-minute tool call and never will. The copy no
longer runs inside a tool call — it is launched detached (`Start-Process
-PassThru -WindowStyle Hidden`) with `/LOG:` to a durable per-tree log, and each
tool call only polls exit state and tails the log. That is how the completed run
above was driven.

**Nothing staged or committed.**

**Next:** the flight-stick device-facts job, then the unreleased-content filter
and the FixedReward census.
