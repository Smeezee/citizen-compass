    state        WORKING
    blocked_on
    clears_by

Filed at 13:51 CDT / 18:51 UTC, read from the machine.

# THE TOKEN COUNTS REACH `logs/wake_log.jsonl`. PROVEN ON A REPLICA, NOTHING
# SPENT, THE REAL EVIDENCE FILE UNTOUCHED.

## THE RECORD WAS THINNER THAN THE MEMO THOUGHT

Your memo quoted `{"event":"wake_end",...,"usage_parsed":true}`. **That field is
gone from the current code.** What `wake_end` actually carried was
`label / seconds / exit / timed_out` and **no usage of any kind** - the counts
did not even reach a boolean.

## WHERE IT WENT, AND WHY NOT AT THE CALL SITES

**In `parse_usage`, which is the one place both callers go through** - the
containment probe and the letter. Logging at the two call sites is how the
second one is wrong six weeks from now.

    {"event":"wake_usage","label":"letter","at_utc":"...",
     "usage_parsed":true,"payload_file":"logs/wake_payload_letter_....json",
     "input_tokens":12,"output_tokens":3456,
     "cache_creation_input_tokens":9935,"cache_read_input_tokens":304083,
     "num_turns":6,"total_cost_usd":0.3615,"session_id":"abc-123"}

**`session_id` is one I added beyond your list.** The 304,000 was only
answerable because the CLI had persisted a transcript under the user profile,
and the id is what names it. It costs a field and it makes that measurement
repeatable instead of lucky.

**`total_cost_usd` is in the record and in no report**, per your ruling.

## THE TWO BEHAVIOURS YOU SAID TO KEEP ARE KEPT, AND THEY ARE WHAT I TESTED

    a block that did not parse   `usage_parsed: false` and NOTHING ELSE. A zero
                                 there would be a measurement nobody took.
    a missing field              ABSENT from the record, never zero.

## HOW IT WAS PROVEN - THREE SYNTHETIC PAYLOADS, ON A COPY

`ROOT` and `WAKE_LOG` pointed at a temp directory, per the brakes spec's own
rule: **seeding the real `wake_log.jsonl` with synthetic records corrupts the
evidence file.** `logs/wake_log.jsonl` is still 6,649 bytes, mtime 12:36.

    one record per call, parsed or not                          PASS
    the four token counts are in the record, unaltered          PASS
    num_turns is recorded                                       PASS
    total_cost_usd stays in the record                          PASS
    a field the payload does not carry is ABSENT, not zero      PASS
    the fields it does carry are still there                    PASS
    an unparsed block says so                                   PASS
    an unparsed block records NO count rather than a guessed one PASS
    and it still returns None to the caller                     PASS

**The middle two are the ones worth having.** A record that reported
`cache_creation_input_tokens: 0` for the probe would have been a lie about a
cache that was created; the payload simply did not carry the field.

## RE-CHECKED AFTER THE CHANGE

    checks/_verify_api_key_guard.py     36 passed, 0 failed
    checks/_prove_launcher_gate.py      all four planted launchers behave
    scripts/wake_desk.py --self-test    6 passed, 0 failed

## NOT DONE, AND SAID RATHER THAN QUIETLY ADDED

**There is no control over the shape of the wake record.** The proof above is a
harness in the scratchpad, not a `_verify_*`, so nothing will notice if a future
edit starts writing zeros. **The brakes are about to make these records load
bearing** - the ceilings count them - so it is probably wanted, and it is the
kind of thing I have been told twice this week not to build unasked. **Say the
word and it is fifteen minutes.**

## NEXT

**The brakes**, in your order: `run_id` and `v:1` on every record, then the
switch, then the per-desk lock, then the two ceilings with the withheld list,
then the spend cap as an empty lookup that refuses to wake. **I read
`claude/SPEC_the-brakes-2026-09-10.md` at the point of building, now.** Each one
tripped on purpose before the next is started.

**Nothing wakes until the brakes exist and have been tripped.** Nothing
committed.
