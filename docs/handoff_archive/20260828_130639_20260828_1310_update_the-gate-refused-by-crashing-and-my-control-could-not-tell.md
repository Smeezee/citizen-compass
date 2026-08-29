# Update — The deploy was correctly refused, the gate refused by CRASHING, and the control I wrote to prove that gate could not tell the difference. Three of mine, all found in ten minutes.

**2026-08-28 13:10 local · Code (background session)** — Sleven ran
`deploy_testing.ps1` while `run_all_controls.py --include-deployed` was in
flight.

---

# 1. THE GATE WAS RIGHT TO REFUSE

    sweep : THE PAYLOAD CHANGED SINCE THE LAST SWEEP.
            swept   c40e02e7a49809e1544a9bc0f0d1d42b
            current 366af81b0ab7583b429c5556258ae52b
    DEPLOY ABORTED

**The running sweep's `_verify_deploy_drift.py` rebuilds `testing/_deploy` as
part of its own work**, and it did so between Sleven's two commands. The payload
about to be uploaded was not the payload anything had swept.

**That is Q10 doing exactly what it was built for**, on a real collision nobody
staged: two things driving the same directory, and the upload stopped.

---

# 2. BUT IT REFUSED BY CRASHING

    print("          swept at %s. Re-run the sweep ...")      <- the %s is here
    print("          about to be uploaded." % rec.get("at"))  <- the % is here
    TypeError: not all arguments converted during string formatting

**Failed closed, which is the safe direction - but by exception rather than by
decision.** It printed `swept at %s.` literally and then died.

**This branch had never executed.** The stale-payload path is the one case that
needs two things happening at once, and nothing had ever produced that until
Sleven ran a deploy during a sweep.

---

# 3. AND MY CONTROL PASSED ON THE CRASH

`_verify_deploy_guards.py` section 11 asserted:

    check("  REFUSES when the payload changed since the sweep", code != 0)

**A traceback also gives a non-zero exit.** Measured, both ways:

    WITH the bug back: exit=1  traceback in output=True
    WITH the fix     : exit=1  traceback in output=False

**The exit code cannot tell a considered refusal from a Python traceback**, and
the assertion was reading only the exit code. That is rule 12's silent success
in the control I wrote *to prove a gate could not silently succeed*.

Every run's output is now kept and one assertion covers all 42 of them:

    no deploy-script run in this control refused by CRASHING - a traceback is
    not a decision

Proven by putting the bug back into a fixture's copy of the gate: the assertion
fires. **A gate that crashes on its refusal path would crash on its success path
the day the same mistake lands there**, and then nothing would deploy at all.

---

# 4. THE FIX HAD A BUG OF ITS OWN, AND IT WAS INVERTED

I wrote:

    check("no deploy-script run ... CRASHING", not crashed,
          "; ".join(...))                       <- third positional

**The third positional is `want`, not `detail`.** With nothing crashed the join
is `""`, so `want=""`, so the assertion **failed exactly when it should have
passed** - and would have PASSED on a real crash. Inverted, in the assertion
whose whole job is to catch an inversion.

Caught within the hour, and only because of the fifth thing:

# 5. `check()` NEVER PRINTED ITS DETAIL

It printed `FAIL <label>` and threw the evidence away. The crash assertion
reported *"a traceback is not a decision"* and named neither the script nor the
traceback; finding out which run it meant took a separate probe.

**It prints the detail on failure now** - and the detail printing as EMPTY on a
failure that named no run is what exposed the inverted argument.

    116 passed, 0 failed

---

# ONE CONSEQUENCE TO FLAG

**The sweep still running is unreliable.** I edited `checks/` while it was
executing those files - `sweep_gate.py`, `_verify_deploy_guards.py` and
`run_all_controls.py` all changed mid-run. Some controls in it ran against the
old code and some against the new.

I did it anyway because the alternative was leaving a crashing gate in place for
another ten minutes while a deploy was being attempted against it. **That is a
judgement call and it is the reason I have been holding every Q7 tranche until a
sweep finishes.** Its numbers should be read as indicative and the sweep re-run
before anything trusts a receipt from it.

Nothing committed since `1a1b4b7`.
