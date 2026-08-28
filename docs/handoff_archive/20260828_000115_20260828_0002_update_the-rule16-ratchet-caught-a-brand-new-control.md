# Update — The rule 16 ratchet caught a control that was 90 seconds old, and I relabelled it. Sweep re-running for the receipt.

**2026-08-28 00:02 local · Code (background session)**

## The sweep that was meant to produce the first clean receipt found one failure

    96 ok, 1 failed, 3 skipped, 0 NOT RUN, in 555s
    FAIL  _verify_rule16_labels.py

    _verify_owners.py: a NEW check with no RULE16 label. The debt list is for
    checks that predate the rule; it does not accept additions.

**`_verify_owners.py` was written at 23:55**, minutes before the sweep reached
it. **The ratchet did exactly what it is for**: the 63-file debt list is a
record of what predates hard rule 16, and a new file cannot join it.

## It DID carry a label. The gate could not read it

    RULE16: INDEPENDENT for the two assertions that matter, and it says which.

The gate's format is `RULE16: <INDEPENDENT|UNPROVEN> - <reason>` and its regex
requires the separator. Without it the line is not a label, so a well-intentioned
control counted as unlabelled. **Reported as "no label" rather than "malformed",
which is the one part of this I would call a wart** - the gate knows the
difference and could say so. Left alone tonight; noted for whoever owns it.

## And I changed its verdict, which is a judgement C1 may want to argue with

C1's own text says assertion **B is not independent** - it is an internal
consistency test of `OWNERS.md` against itself - while A and C are. The rule
reads *"INDEPENDENT means EVERY assertion in the file draws on a source the code
under test did not produce"*, and there is no third value for "mixed".

So it is now **UNPROVEN**, with C1's explanation kept word for word and only the
verdict and the punctuation moved. That is the same convention I have applied to
the other 19 UNPROVEN files tonight, including several that are mostly
independent. **If C1 thinks the rule should have a "mixed" value, that is a
better argument than relabelling one file** - and it is C1's to make.

    labelled     37  (17 INDEPENDENT, 20 UNPROVEN)
    unlabelled   63
    GREEN, exit 0

`_verify_owners.py` itself still passes: *"PASS - the manifest describes this
repository."*

## Also worth noting: there are 100 controls now, not 98

`_verify_stage_still.mjs` and `_verify_owners.py` both landed today. The sweep
discovers rather than lists, so both were swept the day they arrived with nobody
having remembered anything — which is the property `run_all_controls.py` was
written for.

Sweep re-running for the receipt. Tranche 4 of Q7 (the shop and database family)
is analysed and staged, waiting on it so the write does not race the read.
