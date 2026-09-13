    state        WORKING
    blocked_on
    clears_by

Filed at 13:48 CDT / 18:48 UTC, read from the machine.

# STEP 1 IS DONE. THE GUARD CHECK NOW COVERS THE LAUNCHER, AND IT WAS PROVEN BY
# BREAKING THE LAUNCHER THREE WAYS ON PURPOSE.

## WHAT AGREEING ACTUALLY MEANS HERE, BECAUSE IT IS NOT "THE SAME RULE"

The order said assert that the two enforcement points agree. **They enforce
different rules, and a check that flattened them into one would have been the
false part.**

    Assert-DeclaredBilling.ps1 / apikeyguard.go   refuse a MISMATCH between a
        declared intent and what is set. A key is LEGITIMATE under them -
        `claude --bare` requires one and ignores the subscription login.

    scripts/wake_desk.py:assert_no_api_key        refuses on PRESENCE, always.
        In print mode a key takes precedence over the subscription with no
        approval step and no fallback. No intent makes that acceptable, so
        there is nothing to declare.

**So section 4 asserts the three things a divergence would actually cost**, and
its comment says in the file why the stricter rule is deliberate, so nobody
later "fixes" the difference into a hole:

    the variable        both watch ANTHROPIC_API_KEY - proven by PLANTING that
                        name and requiring the refusal, not by reading a
                        literal. A launcher watching a different name passes a
                        source read and fails this.
    EMPTY IS SET        both treat a variable set to "" as present. That is the
                        exact defect found in the PowerShell guard on
                        2026-09-09 and it cannot now move house unnoticed.
    the value           never read, never printed, never in a message.

## AND ONE THING ONLY THE LAUNCHER COULD GET WRONG

**`--dry-run` must not skip the gate.** Rule 12's second half - a safety flag
that can be lost on the way to the code it guards reports a safety it does not
provide. **The planted key is therefore planted WITH `--dry-run` set**, and the
allowed run has to leave `logs/wake_log.jsonl` byte-identical, checked from
outside rather than believed from the script's own "nothing was launched" line.

## THE RESULT

    36 passed, 0 failed          was 30; six of them are new
    --self-test                  0 passed, 36 failed, exit 1
    about 16 seconds             it was 2.3 in the last sweep

The six new ones run the REAL launcher three times with a planted environment:
a marker key, an EMPTY key, and no key at all.

## THE PART THAT MATTERS - IT WAS FED THINGS THAT MUST FAIL

`checks/_prove_launcher_gate.py`, new, and **deliberately not named `_verify_*`
so the sweep does not pick it up** - it plants a file inside `scripts/` and it
is a proof of a control rather than a control. Four launchers, one honest and
three broken:

    UNTOUCHED - the real launcher, copied                  0 findings   OK
    THE GATE NEVER FIRES (still prints its reassuring line) 2 findings  OK
    AN EMPTY KEY READS AS ABSENT - the 09-09 defect rehoused 1 finding  OK
    THE GATE RUNS AFTER THE FLAG PROBE                     2 findings   OK

**The second one is the interesting one.** With the gate neutered it still
printed `billing  ANTHROPIC_API_KEY is not in this environment` and still exited
0 on the ordinary path - a launcher that looks exactly like a working one from
its own output. **The refusal states caught it; the reassuring line did not.**

The planted copy is moved to `_to_delete/planted_wake_desk_<timestamp>/` by the
harness itself (rule 1). Nothing was left in `scripts/`.

## ONE DIVERGENCE I FOUND AND DID NOT CLOSE

**The two guards refuse with exit 78. The launcher refuses with exit 1**, which
is what every other refusal in it exits with - so an unattended caller cannot
tell "refused for billing" from "crashed on something else". **I have not
changed it.** It is a decision about the launcher's exit contract and the brakes
are about to give it more callers, so it belongs with Architecture rather than
in a change I make while passing. Named here, not fixed.

## NEXT

**The usage block into `logs/wake_log.jsonl`** - your 13:19 item 1. The record
is currently thinner than the memo thought: `wake_end` carries
`label/seconds/exit/timed_out` and **no usage at all, not even
`usage_parsed`**. Going in at `parse_usage`, so no caller can forget it.

**Then the brakes**, in the specified order, each tripped on purpose before the
next is started.

**Nothing wakes until the brakes exist and have been tripped.** Nothing
committed.
