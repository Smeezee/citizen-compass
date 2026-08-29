# Update — Q25 done. The separator was never one character, the en dash is a worse trap than the comma, and a lowercase label is invisible to the gate.

**2026-08-29 11:10 local · Code (background session)**

`docs/DECISION_the-rule16-label-format-2026-08-29.md`, 149 lines. C1's
instruction was *"write what the gate does, not what it should do — if they
differ, that difference is the finding."* They differ in three places.

## 1. THE SEPARATOR IS THREE CHARACTERS

    LABEL = re.compile(r"RULE16:\s*(INDEPENDENT|UNPROVEN)\s*[-—:]\s*(.+)")

**Hyphen, em dash AND colon all pass.** `RULE16: UNPROVEN: reason` is a valid
label and always has been. Every error message the gate prints says *"with the
separator"* and shows only the hyphen, so **the rule as communicated has been
narrower than the rule as enforced since adoption.** Not a defect — a
documentation gap, and the document is the fix.

## 2. THE EN DASH IS WORSE THAN THE COMMA EVER WAS

    ACCEPTED   RULE16: UNPROVEN — reason      em dash  U+2014
    MALFORMED  RULE16: UNPROVEN – reason      en dash  U+2013

**One pixel apart, treated oppositely.** The comma cost two people an hour and a
comma is at least visible. The gate prints the offending line back in its error —
where an en dash looks correct. Anyone who hits this should suspect the character
before the code.

## 3. THE ONE ACTUAL HOLE, AND I FOUND IT BY TESTING RATHER THAN READING

**A lowercase label is not seen as a label at all.**

    checks/_verify_zz_probe_lowercase.py
      -> "a NEW check with no RULE16 label"

The regex is case-sensitive and **so is the fallback that detects a MALFORMED
label** — it greps for the literal `RULE16`. So `rule16: unproven - ...` produces
neither a match nor a malformed report. It is classified **unlabelled**.

**And `rule16_baseline.txt` excuses unlabelled files.** The baseline is matched
on the reason string `"no RULE16: line"` (`_verify_rule16_labels.py:167`), which
is precisely what a lowercase label produces. A baselined file carrying a
lowercase label would be **silently excused while appearing to have declared
itself.**

It fails today only because the debt list is closed and a NEW unlabelled check is
refused outright — **a second guard catching it, not the label logic working.**

**Not fixed.** Q25 was to record behaviour, and changing the gate would make the
document stale the day it was written. The fix is one word — case-insensitive
loose detection so a lowercase label reports MALFORMED rather than absent — and
it is mine when it is wanted.

## HOW EACH ROW WAS ESTABLISHED

Every acceptance row was run through the gate rather than reasoned about, and the
three interesting ones — colon, en dash, lowercase — were run **end to end as
real files in `checks/`**, so the gate discovered and classified them the way it
would any control. All three are parked in `_to_delete/probes-20260829/`, and the
suite is back to 105 of 105, 0 unlabelled, 0 malformed, GREEN.

## STANDING

    Q22  verified myself, 105 of 105
    Q24  done - the comment, plus a second stale premise (numpy IS installed)
    Q25  done - this
    Q21  2 of 3. MISC_Hull_C port 2 still in the payload.
    Q26  blocked by Q21
    Q23  blocked by Q21

**The deploy is still gated** on `_verify_child_markers.py` and
`_verify_marker_census.py`, and both baselines are C1's to clear. Nothing I own
is in the way of it.
