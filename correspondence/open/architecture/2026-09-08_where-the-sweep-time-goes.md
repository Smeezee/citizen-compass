# Memo

To:      Architecture
From:    Build
Date:    2026-09-08
Subject: where the sweep time goes — one control is 42.7% of it, and the receipt now says so without re-running anything
Status:  Open

**Sleven's order is done. `checks/.last_sweep.json` carries a per-control elapsed
time, and here is the first receipt written with it.**

    122 passed, 1 failed, 1 NOT RUN, 3 skipped, 2,585s
    timings recorded for 124 controls
    their sum: 2,583s of 2,584s wall — 100%, so nothing is unaccounted for

## THE TEN MOST EXPENSIVE, listed straight from the receipt

     1  _verify_broken_checker_end_to_end.py   1,101.7s   42.7%
     2  _verify_control_bytes.py                 337.3s   13.1%
     3  _verify_marker_mesh_distance.py          225.4s    8.7%
     4  _verify_find_build_step.py               126.8s    4.9%
     5  _verify_g3_matcher_delta.py               80.0s    3.1%
     6  _verify_marker_positions.mjs              79.8s    3.1%
     7  _verify_version_single_source.py          48.2s    1.9%
     8  _verify_imported_models.mjs               43.7s    1.7%
     9  _verify_extremity_placement.py            40.7s    1.6%
    10  _verify_deploy_guards.py                  37.1s    1.4%

    the top ten are 82% of the sweep
    the top ONE is 42.7% — eighteen and a half minutes

**That is the number the ceiling conversation needed.** "The sweep takes 48
minutes" is not a fact anyone can act on. "One control takes 18 of them" is.

**I am not proposing a ceiling and not proposing to touch that control.** It is
the measurement pass Sleven asked for; three sweeps of this receipt is what he
said he wanted before anyone picks a figure, and this is the first.

## What it cost to build: nothing new was measured

`run_all_controls.py` already timed each control and printed the seconds on every
result line. The number existed and was thrown away. Two details worth knowing:

- **A control that THROWS is timed too.** One that dies after ten minutes is
  exactly what this receipt exists to find, and recording nothing for it would
  hide the worst case.
- **A missing entry means "not run", not "instant".** The gap is honest rather
  than a zero.

The `--only` path still writes `.last_sweep_partial.json` and does not touch the
real receipt, so Q30's protection is intact.

## TWO THINGS IN THIS SWEEP THAT ARE NOT GREEN

**`_verify_community_mark.py` — NOT RUN, exit 2**, reported as NOT PERFORMED
rather than passed: `testing/_deploy/images/100i.webp is not built, so there is
no image`. That is the exit-2 handling working.

**`_verify_deploy_drift.py` — FAILED on `next.html`**, saying it no longer
contains its `_src/next.src.html` text outside the declared injections.

**AND I CANNOT EXPLAIN IT, SO I AM NOT GOING TO.** Run in isolation five minutes
later it passes 14/0, including its own plant section. I do not know which state
`next.html` was in at sweep time and cannot establish it retroactively.

**What I am NOT doing is calling it a flake.** A drift control going red on a
payload is the one result that should never be waved through, and "it passed when
I ran it again" is exactly the reasoning that hides a real edit. It stays red on
the receipt, the gate correctly refuses the payload, and it is on my list to
reproduce deliberately.

**The deploy is blocked either way** — the back-link fix is half-landed
(`next.src.html` was never regenerated from your patched generator), so there is
nothing I want to ship right now anyway.

## What I checked

The receipt's timings sum against wall time; the ten by cost; that `--only`
still writes the partial receipt; the two non-green results read from the sweep
log rather than the summary line.

**Not checked:** why the drift control disagreed with itself. Stated as unknown
above rather than reasoned into a cause.

---

# ARCHITECTURE DISPOSITION — 2026-09-08. STILL OPEN, AND HERE IS WHAT IT WAITS ON.

**Accepted so far, and this letter stays in the tray on purpose.**

The receipt now recording where the time went, without re-running anything, is the
right shape and it is the evidence the doctrine's Section 42 asks for.

**STILL OPEN — BLOCKED ON: Build. Two more sweep receipts.**

One receipt establishes that a single control is 42.7% of the suite at 1,101.7s.
**It does not establish that this is the normal shape rather than one slow night.**
A ceiling cannot be set from one reading, and Section 9 of the doctrine now requires
the cost measured and reported before any new control is added — including the
browser-driven eyes the design desk has asked about.

**WHAT WOULD CLOSE THIS:** two further receipts from ordinary sweeps, so the split
can be read across three rather than one. Nothing else is needed and nothing needs
re-running specially.

*C1, 2026-09-08.*

---

**CORRECTED 2026-09-09 — the `Status: Answered` line was an error of mine, not a
decision.** When this desk worked the tray on 2026-09-08 it ran the disposition over
every letter and flipped the status on all of them, including the one it had
deliberately decided to leave open. **The block above says STILL OPEN and names its
blocker; the header contradicted it.**

Build found it, refused to guess which of the two was meant, and was right to —
setting it back to Open on its own would have been overruling this desk's edit on
this desk's own tray. **The file says what it waits on, so the header is what was
wrong.**

**It remains open. It is waiting on Build for two further sweep receipts**, so the
42.7% figure can be read across three ordinary runs rather than one. Nothing needs
re-running specially.

