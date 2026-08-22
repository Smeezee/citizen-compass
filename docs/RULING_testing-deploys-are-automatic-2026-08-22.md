# RULING — the testing site deploys itself. The live site never does.

    ruled by  Sleven, 2026-08-22.
    status    STANDING. Applies to every run from now on, not just this one.
    for       Code. Fold into docs/ARCHITECTURE_DECISIONS.md so it outlives
                this order, and into the run rules you already follow.

---

## The ruling, in his words

> "Make it a standing rule that everything goes to the test site. It needs to be
> pushed without permission, and that's only for the testing site. The actual
> live site will be human taken care of."

## What changes

**Every run that changes anything the site serves ENDS BY DEPLOYING TO TESTING.**
No permission, no asking, no waiting. It is the last item of the run, every time.

**The live site is untouched by this.** It is deployed only when Sleven says so,
explicitly, that time. `deploy_live.ps1` is never run on your own initiative.

## Why the old behaviour was wrong

The ask-first rule exists to protect **people who are not in the conversation** —
the live site's visitors, and the machines the collector installs on. **The
testing site has an audience of one, and he is the person the rule was asking.**

The cost was real and it just happened: L1–L17 and M0–M6 finished at 23:16 and
sat invisible. Sleven opened the testing site, saw a build from five hours
earlier, and judged work he could not see. **Work that is not deployed to testing
has not been delivered** — the review surface is the deliverable, not the commit.

## What does NOT change

- **The deploy guard still applies.** `check_deploy_clean.py` still refuses
  unknown files. **Automatic does not mean unguarded** — it refused
  `find_data.gen.js` at H3 and that refusal was correct.
- **Dry run first, always.** `-WhatIf`, read what it would publish, then deploy.
- **Verify from the served bytes.** Fetch the live URL and confirm the change is
  actually there. Not "the deploy succeeded" — *the page came back with the thing
  in it*. This project has been burned three times by a successful deploy that
  published nothing to the URL anybody was looking at.
- **A failed deploy is a BLOCKED item, reported in the ledger with the reason.**
  Never a silent skip.
- **The ledger records the URL and what was verified**, so the next session knows
  what is actually standing on the web.

## One-line version for the run rules

> Every run ends with a testing deploy: dry run, guard, deploy, verify from the
> served bytes, record it. The live site waits for Sleven.
