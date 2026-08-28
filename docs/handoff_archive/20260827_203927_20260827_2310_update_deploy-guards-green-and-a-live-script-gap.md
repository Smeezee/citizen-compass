# Update — `_verify_deploy_guards.py`: 40/3 failed -> 56/0. And the live deploy script has neither gate.

**2026-08-27 23:08 local · Code (background session)** — one of the 22:15
sweep's 14 failures, closed.

## The three failures were the fixture, not the guards

    DEPLOY ABORTED: browser check missing: checks\_verify_panel_dismiss.mjs
    - refusing to deploy unverified content. A check that is not there has
      not passed.

The control builds a throwaway project with no `checks/` directory. The
browser-check gate went into `deploy_testing.ps1` **this morning** (C1's ruling
11:57), so the clean payload in section 1 was refused before the dry run — for a
reason section 1 was not testing. **The script was right and the control was one
day stale.**

## So the gate got assertions of its own, not just a fixture patch

New **section 8, thirteen assertions**, because this gate is the last thing
between a red page and an upload and nothing had ever watched it work:

    every check this fixture stubs is one the script actually asks for (4/4)
    and the script asks for no MORE than this fixture stubs
    REFUSES a payload when a browser check FILE is missing / names it / never reached its dry run
    REFUSES when a browser check is RED / names which one / quotes the exact override / never reached its dry run
    naming the RED check in -IgnoreRedCheck gets past it / says OVERRIDE / still reaches the dry run
    but naming a DIFFERENT check does not wave the red one through

**56 passed, 0 failed, exit 0.**

**The override is asserted deliberately.** An escape hatch nobody has seen open
is as unproven as a gate nobody has seen shut — and if `-IgnoreRedCheck` did not
work, the next person under pressure reaches for a blanket `-Force`.

## Proven in both directions, by behaviour

**The gate:** the missing-check and red-check cases are real defects, not
inverted expectations — an absent file and a check that genuinely exits 1. The
gate was **observed refusing both**, and observed letting the named override
past.

**The drift assertions:** planted a fifth check the script never asks for and
re-ran. **Exactly those two failed, 54/2, exit 1.** They were the only ones to
move, which is what makes them a check rather than decoration.

`--self-test` still exits 1 with every new assertion inverted.

## Also fixed while in there: rule 15, the eighth instance today

`run_script()` shelled out with `text=True` and no `encoding=`. Same defect,
same file class. Fixed with the reason written at the site.

## THE FINDING I DID NOT GO LOOKING FOR

`docs/FINDING_the-live-deploy-script-has-neither-gate-the-testing-one-gained-today-2026-08-27.md`

    grep -c "\.mjs"      scripts/deploy_live.ps1     ->  0
    grep -c "last_build" scripts/deploy_live.ps1     ->  0
    grep -c "last_build" scripts/deploy_testing.ps1  ->  1

**The script that publishes the PUBLIC site runs no browser checks and never
reads the build receipt.** Both gates were added on 2026-08-27, to the testing
script only. `deploy_live.ps1` is dated 2026-08-21 and its own header promises
that *"where it differs it differs because the LIVE site is public, and every
one of those differences is a refusal."* **These two differences are refusals
the public side does not make.** Drift, not design.

Q2 exists because a failed build reached a deploy and **twelve wrong models went
live**. That incident happened on the side that still has no receipt gate.

I confirmed the testing gate works, against a planted failed receipt:

    DEPLOY ABORTED: THE LAST BUILD DID NOT SUCCEED...
        status  failed    exit code  1

**That is Q2's DONE-WHEN satisfied for `deploy_testing.ps1`.**

## What I did NOT do, and why

**I have not touched `deploy_live.ps1`.** It publishes the public site, it has
never been run for real, and only Sleven runs it. The finding names the exact
two blocks to lift and insists every escape hatch comes with them. **That wants
a go-ahead, not a quiet fix.**

Section 8 ends with a printed `NOTE` naming the gap and the finding file —
labelled rather than silent (rule 16), and not an assertion, because there is
nothing to assert about a gate that does not exist and I will not fail a control
for a defect nobody has agreed to fix yet.

Nothing committed, nothing pushed, live site untouched.
