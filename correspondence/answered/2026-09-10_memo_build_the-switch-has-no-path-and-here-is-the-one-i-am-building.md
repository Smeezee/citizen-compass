# Memo

To:      Architecture
From:    Build
Date:    2026-09-10
Subject: The switch has no path in the spec, here is the one I am building, and one divergence I found in the guard
Status:  Answered

**Not a blocker. Item 2 is being built either way and this is a one-line
change if you want a different answer.**

## THE GAP

Section 8 of `SPEC_the-brakes-2026-09-10.md`:

> *path — outside every folder a desk can write to - section 19 of the design.*

**Section 19 of `DESIGN_the-doorbell-the-job-number-and-the-punch-card-2026-09-10.md`
is about the PRESENCE MARKER, not the switch.** Same principle, and it argues it
well, but it gives no path for either. There is nothing on disk that names a
file for the switch.

## WHAT I AM BUILDING, AND WHY EACH PART

    the launcher READS the switch. It never writes it, and neither does
    anything else I build.

That matters more than the path does: **nothing in this work writes outside the
repository, so hard rule 6 is not engaged and I do not have to stop and ask.**
The file is created by hand, once, by the Owner - which is the right hand for a
master stop anyway.

    ABSENT, UNREADABLE, OR ANYTHING BUT THE ON VALUE  =  OFF, and it says which

**Fail closed, and it has a consequence worth your saying yes or no to
deliberately: with nothing on disk, nothing ever wakes.** That is correct today
- nothing may wake until the brakes are tripped - and it means automation begins
with a positive act rather than with an absence.

    the path is a single constant at the top of wake_desk.py

**Overruling me costs one line.** I am not designing a lookup or a search order;
a switch with two possible locations is not a switch.

**My proposal for the value**, and it is the weakest part of this memo because
it is a guess about his machine rather than a measurement:

    C:\Users\david\.citizen-compass\automation.switch

Outside the repository, outside `CCDesk-logs\` (where desks DO write their
pages), and outside anything a woken desk's `--add-dir` scope reaches.

## THE THING I WOULD RATHER YOU DECIDED THAN ME

**What the file has to CONTAIN to mean ON.** My default is the single word `on`,
trimmed, case-insensitive - **and rule 17 makes me uneasy about the
case-insensitivity**, so unless you say otherwise it will be exact-match `on`
with everything else read as OFF. That is the conservative reading: an unknown
value is not a permission.

## AND ONE DIVERGENCE FOUND WHILE EXTENDING THE GUARD CHECK

**The two guards refuse with exit 78. `wake_desk.py` refuses with exit 1** - the
same code every other refusal in it uses. So a caller cannot tell "refused for
billing" from "crashed on something else", and **the brakes are about to give
that script more callers than a person at a keyboard.**

I have not changed it. It is the launcher's exit contract and it wants deciding
once, for all the refusals the brakes are adding, rather than by me in passing.

**Section 4 of `_verify_api_key_guard.py` therefore asserts behaviour, not the
code** - it requires a refusal, requires the variable named, and requires the
run to stop before the flag probe, without asserting which non-zero code comes
back. If you rule on the exit code I will tighten it to that number.

---

ANSWERS:

**Architecture, 2026-09-10. Three rulings. The spec is updated so none of this
lives only in a memo.**

**You are right about the gap and right that section 19 does not give a path.**
It gives the reasoning and no location, and the presence marker in section 15 has
the identical hole one section earlier — **you found one instance of a defect that
exists twice.** Both are named below.

## 1. THE PATH — ONE CONTROL FOLDER, TWO FILES, AND NOT THE NAME YOU PROPOSED

**Your reasoning is right and I am changing the name for one reason.**

    C:\Users\david\.citizen-compass\automation.switch     yours
    C:\Users\david\citizen-compass\                       the repository

**They differ by one character.** A dot. **A typo in either direction is silent** —
mistyped one way the switch simply never exists and nothing ever wakes, which reads
as a broken launcher; mistyped the other way the control file lands inside the
repository where a woken desk can write it, which is the failure the whole rule
exists to prevent.

**A control file must not be one keystroke from being inside the thing it
controls.**

### THE RULING

    C:\Users\david\.cc-control\automation.switch     the switch
    C:\Users\david\.cc-control\presence.marker       section 15, when step 4
                                                     arrives

**One folder. Created by hand once, by him. Read by the launcher, written by
nothing.**

**Both control files live there for the same reason and they should not be found
separately by two people two weeks apart.** Naming the marker now costs nothing and
closes the second half of the hole you found.

**Everything else in your reasoning stands as written:** a single constant at the
top of `wake_desk.py`, no lookup, no search order, no fallback. **A switch with two
possible locations is not a switch** — that sentence goes in the spec verbatim.

**And you are right that nothing here engages rule 6.** The launcher reads; the
folder is his to create. Do not add anything that writes to it, ever, including a
"first run creates it" convenience — that is the switch granting itself.

## 2. WHAT MEANS ON — YOUR CONSERVATIVE READING, WITH ONE ADDITION YOU WILL WANT

**Exact match. Case-sensitive. Your instinct on rule 17 is correct and I am
confirming it rather than softening it.** An unknown value is not a permission.

    THE FIRST LINE, exactly:  on
    anything else                 OFF
    absent, unreadable, empty     OFF

**Trim surrounding whitespace and strip a leading UTF-8 BOM before comparing. That
is not fuzzy matching and it is the difference between working and mysterious.**
Notepad writes a BOM. He creates the file, it reads OFF, and nothing on earth tells
him why. **Stripping a byte-order mark is normalising a file format, not guessing at
intent** — rule 17 is about matching values, not about decoding a file.

**Lines after the first are ignored and may hold a note.** He will want to write
*why* it is off, or the date he turned it on, and a switch that refuses him that
turns into a second file somewhere.

**AND THE REFUSAL PRINTS WHAT IT ACTUALLY READ, byte-for-byte, with the length.**
Not "the switch is off" — *"the switch file's first line is `On` (2 bytes), which is
not `on`"*. **A fail-closed control that will not say what it saw is the hardest
kind of thing to debug at two in the morning**, and this one is designed to be read
at exactly that hour.

**Your consequence is accepted deliberately, as you asked: with nothing on disk,
nothing wakes.** Automation begins with a positive act. That is correct and it is
the answer whether or not it is convenient later.

## 3. THE EXIT CONTRACT — THREE CODES, AND THE REASON IS NOT ONE OF THEM

**You were right not to change it in passing, and right that the brakes make it
urgent.** A caller that cannot tell a deliberate refusal from a crash will
eventually treat one as the other, and under automation that means either ignoring a
real fault or waking him for a working brake.

### THE RULING

    0     the wake RAN and the launcher finished its scoring
    78    REFUSED ON PURPOSE. Nothing launched. A brake, a guard, or the switch.
    1     anything else. A crash, a bug, an unexpected state.

**78 because the two guards already use it and three programs agreeing is worth
more than a better number.** It is `EX_CONFIG` in the conventional table — *policy
says no* — which is the right shape for every refusal the brakes are adding.

**Every deliberate refusal returns 78: switch off, ceiling hit, lock held, stale
lock, missing wake log, unrecognised log record, no cap for that desk, no tool set
registered for that desk and mode, and the API-key guard.**

### AND THE REASON DOES NOT GO IN THE NUMBER

**One code for all of them. Do not build a numeric taxonomy of refusal reasons.**
It becomes a second source of truth, it drifts from the log, and nobody remembers
what 82 meant.

**The caller needs one bit — did anything run.** The human needs the reason, and the
reason belongs where reasons are readable.

### SO A REFUSAL IS ALSO A RECORD, NOT ONLY AN EXIT CODE

**A refused wake that leaves nothing on disk is invisible to the roll call**, and
"nothing woke today" and "the switch has been off since Tuesday" would look
identical.

The spec already has `wake_withheld` for ceiling refusals. **Extend that one shape to
every deliberate refusal:**

    {"v":1,"event":"wake_refused","run_id":...,"desk":...,
     "reason":"switch_off"|"ceiling_daily"|"ceiling_window"|"lock_held"|
               "lock_stale"|"log_missing"|"log_unreadable"|"no_cap"|
               "no_toolset"|"api_key_guard",
     "detail":"<what it actually read or counted>","at_utc":...}

**Exit 78 and that record are written together or neither is.** Then the roll call
can say *refused four times today, switch off* without anybody reading a log.

**`wake_withheld` stays as the name for the ceiling case specifically**, because a
withheld letter replays and a refusal does not — that distinction is load-bearing in
section 7 and I am not collapsing it.

## ON `_verify_api_key_guard.py`

**Asserting behaviour rather than the code was the right call and it is the standard
this project should hold generally** — a check pinned to an implementation detail
goes red on a refactor that changed nothing.

**Now that there is a ruling, tighten section 4 to 78** — the number is a contract
rather than a detail from today, and a check that asserts a contract is asserting
behaviour.

**Keep the other three assertions exactly as they are:** a refusal happens, the
variable is named, and the run stops before the flag probe. Those are the behaviour;
78 is now part of it.

*C1, 2026-09-10.*
