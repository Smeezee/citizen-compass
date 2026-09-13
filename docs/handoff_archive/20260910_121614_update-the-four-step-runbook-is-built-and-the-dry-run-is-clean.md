    state        BLOCKED
    blocked_on   the go to spend on step 1 + step 2 of scripts/wake_desk.py
    clears_by    OWNER

Filed at the time in this file's archive name. **Nothing spent since the wake.**

**The three lines above are new, on your instruction, and they lead every report
from here.** Prose unchanged below them.

## THE RUNBOOK IS BUILT. ALL FOUR STEPS. DRY RUN CLEAN.

    STEP 0  pre-flight, costs nothing            RUNS CLEAN
    STEP 1  containment probe                    built, not run
    STEP 2  the letter                           built, not run
    STEP 3  scored from the filesystem           built
    STEP 4  close it out                         built

Step 0 output, in full:

    executable   C:\Users\david\.local\bin\claude.exe      a real .exe, no shim
    billing      ANTHROPIC_API_KEY is not in this environment
    9 flags      all accepted; the method control proves the probe can say no
    prompt file  logs/wake_prompt_audit.md, 33,601 bytes: charter + CLAUDE.md
    the answer   .py 91  .mjs 79   counted by me, top level of checks/ only
                 7 subdirectories NOT counted, named in the output
    watcher      alive, last line present
    snapshot     304 files across inbox/, correspondence/, logs/ with sha256
    git          HEAD c8ab1d0f3d8f, 418 dirty paths
    mode         unattended -> tools 'Read,Glob,Grep,Write'

Detector self-test: **6 passed, 0 failed**, and every case has been seen to fire
under a deliberately blinded run.

## 0.1 CAUGHT ME BUILDING A CHECK THAT LIED

**Your step 0.1 says run `claude --help` and refuse if a flag is absent. Doing
exactly that would have refused this run over two flags that work.**

    --append-system-prompt-file   ABSENT from --help on 2.1.266   AND ACCEPTED
    --system-prompt-file          ABSENT from --help              AND ACCEPTED

So I used your own acceptance method instead - offer the flag beside a
deliberately bogus one and see which the parser names. **And the first version of
that probe was itself wrong:**

    --output-format        reported *** ABSENT ***
    --permission-prompts   reported *** ABSENT ***
    --max-budget-usd       reported *** ABSENT ***

**All three exist, and `--output-format json` was in the wake that already ran.**
The probe passed `x` as the value; the parser rejected the VALUE before it ever
reached the bogus flag. **A probe that says ABSENT about a flag standing in front
of it is worse than no probe, because it fails closed on a lie** - and it would
have refused every run from here with a confident, specific, wrong reason.

Each flag now carries a value the parser accepts. **Nine accepted, and the method
control still names a genuinely bogus flag**, so the probe can still say no.

**Two checks in two days that reported the wrong answer because of what they were
looking at rather than what they were looking for.** Same shape as `Test-Path`.

## EVERYTHING ELSE FROM SECTION 5 IS IN

    .env denied                 --disallowedTools "Read(.env)"
    display quoting             subprocess.list2cmdline, and it SAYS which it is
    stdout forced to UTF-8      a cp1252 console would throw after the spend
    no settings file            every rule on the command line, where a typo errors
    600s timeout                process killed and reported if it hits it
    Edit(inbox/**) not Write()  a Write(path) rule is never matched
    tool set is a LOOKUP        per desk, per mode, not a literal in the builder

**Mode selection is not wired to anything.** The table has an `unattended` row
without a shell and a `present` row with one, and nothing chooses between them -
Architecture is specifying how presence is established and I have not invented it.

## WHAT I HAVE NOT DONE, AND WHY EACH ONE IS NOT DONE

**Not run step 1 or step 2.** Your word covers the run that happened; you said the
go for steps 1 and 2 comes once the runbook is built and the dry run is clean.
**Both are now true. This letter is the ask.**

**Not built the brakes.** Architecture specifies, Build builds. Nothing here has a
counter, a ceiling or a lock, and nothing calls it.

**Not extended `checks/_verify_api_key_guard.py` to assert the two enforcement
points agree.** That is in your 0.3 and it is real work, not a line. It is next
after the run, unless you want it first.

**Not touched the sixth-document check, the card mark, B2, the desk-list
derivation or the timezone stamp.** All queued behind this.

## THE ONE THING I WANT ON THE RECORD BEFORE THE PROBE RUNS

**If the outside write succeeds, that is the finding and I stop.** I will not
loosen the permission to make it pass, and I will not run step 2. Your words, and
I am repeating them so there is no doubt about what I will do at that moment.

Nothing committed.
