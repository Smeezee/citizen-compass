# Update — the startup guard is built, wired into three entry points, and proven

**Filed 2026-09-09 18:30 CDT.** Sleven's GO order, part 3. Parts 1 and 2 are still running.

## WHAT IT IS

**One behaviour, two languages, because this project has both.**

    pkg/apikeyguard/apikeyguard.go     for the Go entry points
    scripts/Assert-NoApiKey.ps1        for the PowerShell ones

Both refuse if `ANTHROPIC_API_KEY` is **present at all**, both exit **78
(EX_CONFIG)** so a refusal is distinguishable in a scheduler's history from an
ordinary failure, and **neither ever reads, logs, prints or returns the value.**

**Presence, not non-emptiness, and that is deliberate.** The order says "asserts
that it is unset and refuses to run if it finds it". An empty value is still
something configuring that name; the message says which of the two it found so
nobody hunts for a value that is not there.

## WIRED INTO THREE ENTRY POINTS

    run_checks_scheduled.ps1   the daily auditor task - the one that runs with
                               nobody watching, so the one where a metered call
                               would go unnoticed longest
    watcher-go/main.go         inbox_watcher.exe, unattended and never stops
    roadmap-watcher/main.go    scheduled poller; -check and -status go through
                               it too, because a guard somebody can walk around
                               with a flag is not a guard

**Every one is placed AFTER the logger exists and BEFORE any work.** That is the
whole of "make it loud": a refusal on stderr from a Task Scheduler process goes
nowhere anybody looks. **Proven** — the control's run put the refusal in
`logs/checks_scheduled.log`, which is a file people here read.

## DELIBERATELY NOT GUARDED, AND WHY

    scripts/deploy_testing.ps1, deploy_live.ps1   operator-run, in front of a
    scripts/push_main.ps1                         person who would see it
    setup_*.ps1                                   operator-run installers
    Backup-CitizenCompass.ps1                     operator-run, not scheduled
    checks/run_all_controls.py                    operator-run; the scheduled
                                                  path is run_checks.py, whose
                                                  parent IS guarded
    citizen-collector, collector2                 Sleven's own, closed to this
                                                  desk

The distinction is **unattended**, not important. A refusal a person is standing
in front of does not need a log line to be loud.

## RULE 12 — PROVEN IN BOTH DIRECTIONS

**`go test ./pkg/apikeyguard` — 5 tests, all green.** Unset is allowed; set is
refused; empty is refused and says EMPTY; **the value never appears in the
message**, checked against a planted marker and against a 12-character fragment
of it; and the `Result` struct is asserted to carry no field that could hold one.

**`checks/_verify_api_key_guard.py` — 15 assertions, all green, 2.4s**,
`--self-test` exits 1. It runs the REAL `run_checks_scheduled.ps1` as a
subprocess with a planted marker in its environment and requires:

    exit 78, not 0 and not 1
    it says REFUSING TO START
    it names the variable and names itself
    THE PLANTED MARKER DOES NOT APPEAR IN THE OUTPUT
    it refused BEFORE running any check group

**And two things the unit tests cannot see.** Section 2 asserts every entry
point still CALLS the guard — *a guard nobody calls passes its own unit tests
forever*, and deleting one line is invisible in a diff nobody reads. Section 3
reads the exit code and variable name out of both source files, in two
languages, and requires them to agree, so the twins cannot drift.

Confirmed afterwards: **the refusal reached the log, and the log does not
contain the marker.**

## ONE THING I COULD NOT TEST, STATED RATHER THAN CLAIMED

**PowerShell cannot create an empty-but-present environment variable** —
`$env:X = ''` removes it. So the PowerShell guard's empty branch is written and
reviewed but has never been executed; only the Go one has, where `os.Setenv`
does create that state. Reported as NOT PERFORMED rather than counted as a pass.

## AND ONE THING NOT YET DONE

**`inbox_watcher.exe` is running the OLD binary.** The guard is compiled and
tested but the live watcher started before it existed, and rebuilding the exe
needs the running process stopped — it is the sole writer of
`LATEST_HANDOFF.md`. Both Go modules build and their test suites pass; the
deployment of that binary is an operational step I have not taken unasked.

`_verify_rule16_labels.py` green. Nothing committed.
