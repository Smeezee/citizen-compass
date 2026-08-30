# Update — Q30 done. A subset run can no longer erase a sweep, and the message that hid it for a day now names the path it actually wrote.

**2026-08-30 04:30 UTC / 2026-08-29 23:30 local · Code (background session)**

My call, made and built rather than restated: **fail-closed was not sufficient.**

    a full sweep   -> checks/.last_sweep.json          unchanged
    --only         -> checks/.last_sweep_partial.json
    --self-test    -> checks/.last_sweep_partial.json

**Self-test goes with it** because it inverts every expectation, so it is not a
sweep of the payload either - and until today a self-test run also took a good
receipt down with it.

## PROVEN, NOT ASSERTED

    routing        partial=F self_test=F  -> .last_sweep.json
                   the other three combinations -> .last_sweep_partial.json

    a 3-control --only run
      before  at 2026-08-29T22:26:57  partial=False  passed=106
      after   at 2026-08-29T22:26:57  partial=False  passed=106
      FULL RECEIPT BYTE-IDENTICAL - untouched
      partial went to .last_sweep_partial.json, 3 passed

    with the full receipt moved aside (rule 1: moved, not deleted)
      GATE EXIT 1, and it NAMES the partial while refusing to read it:
      "a subset is not a sweep - and it is kept separately so it cannot
       overwrite the real one."
      full receipt put back, byte-identical to before the test

**The gate did not change its mind about anything.** It reads the full receipt
and nothing else, so a partial still cannot masquerade as a sweep.

## THE MESSAGE THAT HID IT

`run_all_controls.py` printed `sweep_gate.RECEIPT` unconditionally, so a
`--only` run **announced the full receipt's path while writing over it.** The
message and the act disagreed, which is why the clobber went unnoticed until C1
happened to check. It now names the path it actually wrote, and says outright
when it did not touch the real one.

## ONE THING BROKE ON THE WAY AND THE EXISTING GUARD CAUGHT IT

My first patch aborted on an assertion **after** making its edit in memory, so
nothing reached disk - and the two later patches landed referring to a helper
that did not exist. The subset run then reported:

    SWEEP RECEIPT NOT WRITTEN: NameError: name 'receipt_path' is not defined
    The deploy gate refuses on a missing receipt, so this fails closed
    rather than quietly.

**Exactly as designed.** A receipt that cannot be written is reported and does
not silently look unreceipted-but-fine. I had not written that guard today and
it caught my own mistake within a minute.

## ALSO

`checks/.last_sweep_partial.json` added to `.gitignore` beside its sibling -
both are machine state and neither belongs in history. `.gitignore` has no
declared owner in `OWNERS.md`; the edit is one line adjacent to the existing
entry and is recorded here rather than done quietly.

## STANDING

    Q29, Q30   done
    Q3, Q5     the two still open, and both are older than today
    Q28        C1's
    draco3d    still not installed, still asked rather than assumed

Uncommitted: `checks/sweep_gate.py`, `checks/run_all_controls.py`, `.gitignore`.
