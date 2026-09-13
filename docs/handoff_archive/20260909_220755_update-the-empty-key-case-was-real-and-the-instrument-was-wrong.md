# Update — the red case was real: Test-Path was lying, not PowerShell refusing

**Filed 2026-09-09 22:10 CDT.** Job 2 of the boot memo, closed. The control is
**30 passed, 0 failed**, and it is green because the guard was fixed, not because
the case was retired.

## THE ANSWER TO THE QUESTION HE ACTUALLY ASKED

**The empty-but-present state EXISTS on this platform.** The diagnosis it was
handed — *"PowerShell cannot hold one"* — was about SETTING one from inside
PowerShell, which is true and is not what the control does. The control plants it
from the PARENT process, and that works:

    Go binary, launched by Git Bash `env VAR=`     present, empty
    Go binary, launched by Python subprocess       present, empty
    PowerShell -Command, planted by Python         Test-Path True, Length 0
    PowerShell -File,    planted by Python         Test-Path True, Length 0

Two independent launchers, two languages. **It was never impossible, so NOT
PERFORMED would have been the wrong answer and would have retired a live case.**

## WHY IT FAILED ANYWAY — AND THIS IS THE PART WORTH KEEPING

`Test-Path Env:X` **disagrees with itself inside one process** when the variable
is present and empty. Three identical readings, back to back, **nothing between
them but the calls themselves**:

    PROBE[1] TestPath=True   ChildItem=1
    PROBE[2] TestPath=False  ChildItem=1
    PROBE[3] TestPath=False  ChildItem=1

`Get-ChildItem Env:` said present on every reading. The variable never changed.
In the unpatched entry point the guard's own single call read **False**, which is
why the refusal said *"is not set at all"* about a variable that was set.

The guard's presence test was:

    $keyPresent = Test-Path "Env:$script:BillingGuardKeyName"

It now reads the environment block instead, for the key and the declaration both:

    $keyItem    = @(Get-ChildItem Env: | Where-Object { $_.Name -eq $KeyName })
    $keyPresent = ($keyItem.Count -gt 0)

The measurements are in the file above the code, so the next person does not
re-derive them. Name comparison is `-eq` and case-insensitive **on purpose and
stated**: Windows environment names ARE case-insensitive, so `PATH` and `Path`
are one variable. That is not a fuzzy match (rule 17).

## HOW BAD IT WAS — HONESTLY, AND IT IS NOT THE WORST READING

**No verdict was ever wrong.** An empty key cannot bill, so every state still
refused or allowed correctly. What was wrong:

    the refusal MISDESCRIBED what it found   "is not set at all" when it was set
    the "present but EMPTY" NOTICE never
    fired at all                             a signal that something on this
                                             machine sets that name, lost silently

The second is the one that matters, and **nothing in the suite covered it**,
because every existing case was a refusal. A notice that silently stops appearing
is the same defect as a refusal that silently stops refusing.

## SO THE CONTROL GREW ONE CASE, AND IT IS PROVEN THE ONLY WAY THAT COUNTS

    ("an EMPTY key with nothing declared - allowed, and it must still SAY it
      found one",  "", None, False, "present but EMPTY")

The phrase assertion used to run on refusals only; it now runs on allowed states
too, when the verdict itself was right.

**Driven with known-bad input, not read (rule 12).** The pre-fix guard was copied
back over the fixed one and the suite re-run:

    fixed guard      30 passed, 0 failed
    OLD guard back   28 passed, 2 FAILED  <- both new assertions, and only those
    fixed guard      30 passed, 0 failed   (sha 8719e71a..., confirmed identical)
    --self-test      inverted run FAILS, as it must

**Both new checks have been seen to fail.** They are not decorations.

## WHAT WAS TOUCHED, AND THE ONE THING THAT SHOULD WORRY SOMEBODY

    scripts/Assert-DeclaredBilling.ps1   presence test replaced
    checks/_verify_api_key_guard.py      one case added, phrase check widened
    originals copied to                  _to_delete/2026-09-09_billing_guard_before_presence_fix/

**Both files are UNTRACKED, and so is `pkg/apikeyguard/`.** The entire billing
guard — Go package, PowerShell twin, and the control that holds them together —
exists only in the working tree. `git status` shows `??` against all three. That
is one careless `git clean` from gone, and it is the newest safety control in the
project. **I have not committed anything** (rule 2). It needs your go-ahead.

## THREE THINGS FOUND, NONE FIXED, NONE ASKED FOR

**1. The roadmap watcher has no scheduled task at all.** Correcting what I wrote
at 22:00: I said it might be a third live half of the disagreement. **It is not
live.** Both its binaries (`roadmap-watcher.exe` Aug 30, `roadmapwatcher.exe`
Sep 9 18:26) predate the amendment, but nothing on this machine runs them — the
only two Citizen Compass tasks registered are the auditor checks and the inbox
watcher. Commit `835413a` says *"the roadmap watcher gets a scheduled task"*.
**On this machine, today, it does not have one.**

**2. Section 3 compares the two guards' CONSTANTS, not their BEHAVIOUR.** It
checks that both spell `ANTHROPIC_API_KEY` and `78` the same way. This whole
defect was a behavioural disagreement — the Go guard read the empty key correctly
the entire time — and section 3 passed throughout. **A behavioural comparison is
buildable: drive both guards through the same state table and require the same
verdict.** Not started, not asked for.

**3. The guard's header still overstates its own contract** — reported at 22:00,
unchanged, one sentence, waiting on your word.

## NEXT

Tray item 2: the six old letters — DONE / SUPERSEDED / NEVER STARTED for each,
having first read the authorisation memo you pointed me at.

Nothing committed.
