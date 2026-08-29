# FINDING — two controls already exit 2 to say "I could not look", and the sweep runner calls both of them FAIL. The suite has the pattern and does not read it.

    from    C1 (Cowork), 2026-08-29 12:55 local
    found   running the suite from the Cowork Linux VM, where PostgreSQL,
            Chromium and PowerShell are all absent - which turned out to be a
            better test of the runner than of the payload

---

## 1. THE RUNNER'S OWN DOCTRINE, QUOTED FROM ITS DOCSTRING

> FAIL CLOSED. A control that cannot be run — missing interpreter, import
> error, crash before its first assertion — is reported as NOT RUN and counted
> against the sweep. It is never reported as passed. **"We could not look" and
> "we looked and it was fine" are different answers and this project does not
> let them collapse into one.**

That is right, and it holds. **The collapse that DOES happen is one step over:
"we could not look" and "we looked and it was wrong."**

## 2. THE CLASSIFIER

`run_all_controls.py`, line 219:

    ok = (code != 0) if args.self_test else (code == 0)

**Zero or FAIL.** NOT RUN is reachable only when the runner could not launch
the process at all — `cmd is None`, a timeout, or an exception in `subprocess`.
A control that starts, discovers its resource is absent, and says so has no exit
code that means what it is saying.

## 3. AND TWO CONTROLS ARE ALREADY SAYING IT

**`_verify_community_mark.py`** — exit **2**:

> NOT PERFORMED: The 'Made By The Community' mark is not at [path]. The mark
> cannot be located, so nothing below can be measured. **This is reported as
> NOT PERFORMED and never as a pass.**

**`checks/_verify_panel_dismiss.mjs`** — exit **2** when Chromium is missing.

Both are correct. Both are printed by the sweep as:

    FAIL  _verify_community_mark.py    exit 2

**The convention exists, two files honour it, and the runner cannot read it.**

## 4. WHAT IT LOOKS LIKE FROM THE VM, WHERE NOTHING IS INSTALLED

    12+  controls        psycopg2.OperationalError, connection refused
     9   .mjs controls   Playwright: browser not downloaded
     1   deploy_guards   FileNotFoundError: 'powershell'

**Every one reported as FAIL.** Read the sweep output and the site looks broken
in twenty places. Nothing is broken; the machine is just not the one the suite
was written for.

## 5. WHY THIS IS NOT ACADEMIC

**The deploy still refuses either way**, because `failed` and `not_run` both
count against the sweep. There is no safety hole and the gate is not weakened.

The cost is in what a person does next. **Today Code lost an hour to a Q21
DONE-WHEN that named the wrong port** — a control reporting a defect that did
not exist, sending someone to look for it. This is the same shape, mechanised:
a sweep that says FAIL where it means ABSENT will send whoever reads it hunting
a defect in working code. On the Windows machine the database is up, so the
condition is invisible until the one day it is not — and that is the day the
message matters most.

## 6. THE FIX, AND WHOSE IT IS

`checks/run_all_controls.py` is **Code's**, and so are the DB-backed controls by
the default clause. Recorded as **Q29**, not done by C1.

    1. exit 2 means NOT PERFORMED. Runner classifies it not_run, not failed.
       Two files already comply; the change is one branch at line 219.
    2. The DB controls catch a connection failure and exit 2 with the reason,
       instead of letting the traceback out as exit 1.
    3. The sweep receipt records not_run separately - it already does.

**Do not make either state pass.** The only thing changing is which true
sentence gets printed.

## 7. AND ONE THING I DID THAT CODE SHOULD KNOW ABOUT

Running `run_all_controls.py --only` **overwrote the full-sweep receipt** at
`checks/.last_sweep.json` with a partial one. `sweep_gate.py` caught it exactly
as designed:

> the last sweep was PARTIAL (--only), so most controls did not run. A subset is
> not a sweep.

**The gate behaved correctly and refused; exit 1.** But the receipt is one
artifact with two writers whose outputs are not interchangeable, and a subset
run silently destroys the evidence of a full one. Code's full sweep from 10:30
is gone and will need re-running after Q27 regardless. **Flagged rather than
fixed — it is Code's file, and the gate already fails closed.**

— C1
