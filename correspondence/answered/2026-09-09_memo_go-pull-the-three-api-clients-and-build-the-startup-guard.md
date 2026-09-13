# Memo

To:      Build
From:    Owner
Date:    2026-09-09
Subject: GO — pull the three API clients out of the venv, and build the startup guard you offered
Status:  Answered

**Both approved. Your supplement was the right call and the second search is why
you get asked.**

Context you did not have: those packages are mine, left over from my first attempt
at the AI Historian. I thought I was running something local and free. **I was
running clients for paid services and nobody told me the difference.** Nothing on
this project uses them and nothing is going to.

## 1. CHECK BEFORE YOU REMOVE — ONE GAP IN YOUR OWN REPORT

You confirmed nothing imports `aider` or `litellm`. **You did not say the same
about `openai`, and it is the most likely of the three to be imported by something
I have forgotten.**

Search the whole tree — including everything git ignores, the way your second pass
did, not your first. `import openai`, `from openai`, and any indirect use.

**If anything imports it, STOP and tell me.** Do not remove it and do not work
around it. The other two still come out.

## 2. REMOVE THEM

    aider-chat 0.86.2, litellm 1.81.10, openai 2.20.0

Out of the project venv. **Record the exact version strings in your reply** so they
can be put back with one command if I ever want aider again.

**Only those three.** Do not touch anything they dragged in — a shared dependency
removed to tidy up is how a build breaks a week later with no obvious cause.

Run whatever the project uses to prove itself afterwards and say what you ran.
**"It should still work" is not the answer I am asking for.**

## 3. BUILD THE GUARD

The thing you offered and correctly did not build unasked: **every unattended entry
point asserts at startup that `ANTHROPIC_API_KEY` is unset, and refuses to run if
it finds it. Presence or absence, never the value — not in a log, not in an error
message, not anywhere.**

**Name every entry point you put it on**, and name any you deliberately left off
and why. `run_checks_scheduled.ps1` is the obvious one; you know the rest better
than I do.

**Make it loud.** The whole point is that the silent path becomes a stopped one.
A refusal nobody sees is the same failure in a different coat.

## WHY BOTH, RATHER THAN EITHER

Removing the clients means there is nothing on the machine that knows what to do
with that variable. The guard means it stops even if something new arrives. **The
second one is the one that survives me forgetting this conversation.**

ANSWERS:

**All three parts done 2026-09-09 20:59 CDT.**

## 1. CHECKED BEFORE REMOVING — AND YOU WERE RIGHT ABOUT THE GAP

You spotted that I had cleared `aider` and `litellm` and **had not said the same
about `openai`**. Fixed properly: **746,566 files scanned**, the whole tree,
including everything git ignores.

    IMPORTS OUTSIDE venv/Lib/site-packages   NONE
    IMPORTS INSIDE                           4,023 sites across 4 packages

**Nothing in this project imports openai, aider or litellm.** The 4,023 are the
packages importing each other — litellm's entire job is wrapping openai — which
is why the count is split by location rather than given as one number.

**Every mention outside site-packages is a document about this question**, except
one worth naming: `checks/_verify_no_agent_traces.py:61` has "openai" inside a
regex of words that must never appear in published output. A blocklist entry,
not an import.

**A fourth package imports openai and is NOT one of the three: `posthog`.** You
said not to touch what they dragged in, so it stays — but I had to know whether
removing openai would break it. **It does not.** posthog's openai code is an
opt-in integration under `posthog/ai/openai/`; its top level never mentions
openai and `posthog/ai/__init__.py` imports one thing, `Prompts`. Confirmed
after the removal: `import posthog` still works, 7.8.6. Nothing outside
site-packages imports posthog either.

## 2. REMOVED — AND EXACTLY THREE THINGS CHANGED

    aider-chat==0.86.2
    litellm==1.81.10
    openai==2.20.0

    pip list before   117 packages
    pip list after    114 packages
    the diff          three lines, nothing else

**Put back with one command:**

    venv\Scripts\python.exe -m pip install aider-chat==0.86.2 litellm==1.81.10 openai==2.20.0

Nothing they dragged in was touched. `pip uninstall` removes only what it is
named and the 114-line diff is the proof rather than the promise.

## 3. WHAT I RAN TO PROVE IT

**An import smoke test first**, so a broken venv would not cost forty minutes to
find: dotenv, psycopg2, sqlalchemy, fastapi, alembic, requests, PIL, bs4 all
import, and `build_find_data` imports clean.

**Then the project's own proof of itself — a FULL SWEEP.**

    128 ok, 0 failed, 3 skipped, 0 NOT RUN, in 2534s (42.2 min)

**128 of 128 green with the three packages gone.** That is the answer to "run
whatever the project uses to prove itself", and it is a run rather than an
opinion.

**One thing I found and did not cause:** `pytest` is not installed in this venv,
though `requirements-dev.txt` line 5 declares `pytest==9.1.1`. **Absent in both
snapshots**, before the uninstall and after, so it is a pre-existing gap. Said
only because "it was already like that" is worth nothing unless the before
picture was actually taken, and it was.

## 4. THE GUARD

**One behaviour, two languages**, because this project has both:

    pkg/apikeyguard/apikeyguard.go     the Go entry points
    scripts/Assert-NoApiKey.ps1        the PowerShell ones

Both refuse if the variable is **present at all**, both exit **78 (EX_CONFIG)** so
a refusal is distinguishable in a scheduler's history from an ordinary failure,
and **neither ever reads, logs, prints or returns the value.**

**Presence, not non-emptiness.** You said "refuses to run if it finds it". An
empty value is still something configuring that name; the message says which of
the two it found so nobody hunts for a value that is not there.

**ON THESE, and every one placed after the logger exists and before any work:**

    run_checks_scheduled.ps1   the daily task that runs with nobody watching
    watcher-go/main.go         inbox_watcher.exe, unattended and never stops
    roadmap-watcher/main.go    including -check and -status, because a guard you
                               can walk around with a flag is not a guard

**DELIBERATELY NOT ON THESE**, and the distinction is *unattended*, not
*important* — a refusal a person is standing in front of does not need a log line
to be loud:

    deploy_testing.ps1, deploy_live.ps1, push_main.ps1   operator-run
    setup_*.ps1                                          operator-run installers
    Backup-CitizenCompass.ps1                            operator-run, unscheduled
    checks/run_all_controls.py                           operator-run; the
                                                         scheduled path is
                                                         run_checks.py, whose
                                                         parent IS guarded
    citizen-collector, collector2                        yours, closed to this desk

**LOUD, and proven loud.** The refusal goes to the process's own log file, not
just stderr — a Task Scheduler process's stderr goes nowhere anybody looks. The
control's run put it in `logs/checks_scheduled.log`, and that log does **not**
contain the planted marker.

**It can fail on demand.** `go test ./pkg/apikeyguard` — 5 green, including one
that plants a marker value and fails if even a 12-character fragment reaches the
message. `checks/_verify_api_key_guard.py` — 15 assertions, 2.3s in the sweep,
`--self-test` exits 1. It runs the REAL scheduled script with a planted
environment and requires exit 78, the refusal text, the program named, no marker
in the output, and that it stopped before running any check group. **Two more
things a unit test cannot see:** that every entry point still CALLS the guard —
a guard nobody calls passes its own unit tests forever — and that the Go and
PowerShell twins still agree on the exit code and the variable name.

**One case I could not test, stated rather than claimed:** PowerShell cannot
create an empty-but-present environment variable — `$env:X = ''` deletes it — so
that branch of the PowerShell guard is written and reviewed but has never
executed. Only the Go one has. Reported as NOT PERFORMED.

## ONE THING STILL OUTSTANDING

**`inbox_watcher.exe` is still running the OLD binary.** The guard compiles and
its tests pass, but swapping the exe means stopping the sole writer of
`LATEST_HANDOFF.md`. **Say the word and I will stop the task, rebuild, and start
it** — about a minute, and the handoff pipeline is deaf for that minute. I have
not done it unasked.
