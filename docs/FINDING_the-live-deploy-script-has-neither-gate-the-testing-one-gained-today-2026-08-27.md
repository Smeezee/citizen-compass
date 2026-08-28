# FINDING — `deploy_live.ps1` has neither of the two gates added to `deploy_testing.ps1` today

**2026-08-27 22:55 local · Code (background session)**
Found while reproducing `_verify_deploy_guards.py`'s three failures. Not looked for.

---

## The claim, and how to check it in ten seconds

    grep -c "\.mjs"      scripts/deploy_live.ps1     ->  0
    grep -c "last_build" scripts/deploy_live.ps1     ->  0
    grep -c "last_build" scripts/deploy_testing.ps1  ->  1

**The script that publishes the PUBLIC site runs no browser checks and does not
look at the build receipt.** The script that publishes the password-gated
testing site does both.

---

## What each gate is, and why it exists

**1. The build receipt.** `deploy_testing.ps1` reads
`testing/_src/.last_build.json` and refuses when the last build failed. Proven
by behaviour just now, against the control's own throwaway project with a
planted failed receipt:

    DEPLOY ABORTED: THE LAST BUILD DID NOT SUCCEED, so this payload is not
    trustworthy.

        status     failed
        exit code  1

    To upload anyway:  .\scripts\deploy_testing.ps1 -IgnoreFailedBuild

**That is `NEXT.md` Q2's DONE-WHEN satisfied** — the refusal names the exit
code, and it fires before anything is uploaded. Q2 exists because a build and a
deploy were chained in one command, `BUILD EXIT=1` was printed, the deploy read
only its own output, **and twelve wrong models went live.**

**Went LIVE.** The incident Q2 was written for happened on the side that still
has no receipt gate.

**2. The browser checks.** `deploy_testing.ps1` runs four `.mjs` checks and
refuses on a red one, and refuses when a check FILE is missing:

    DEPLOY ABORTED: browser check missing: checks\_verify_panel_dismiss.mjs -
    refusing to deploy unverified content. A check that is not there has not
    passed.

C1's ruling, 2026-08-27 11:57, written into the script at line 264: *"browser
checks gate the DEPLOY, not the build."* **The deploy it gates is one of two,
and it is not the public one.**

---

## Why this is a defect rather than a deliberate asymmetry

`deploy_live.ps1`'s own header, lines 16-20:

> This is a mirror of scripts/deploy_testing.ps1 and deliberately so: the same
> unknown-file guard on the same bytes, the same fail-closed handling when the
> guard cannot run, the same payload sanity checks, the same credential
> handling, the same -WhatIf. **Where it differs it differs because the LIVE
> site is public, and every one of those differences is a refusal.**

Both differences found here are the opposite: **a refusal the public side does
not make.** The file is dated 2026-08-21; both gates were added on 2026-08-27,
to one script. This is drift, not design.

It is also the shape of defect this repo already names. A `-WhatIf` that never
reaches the code it guards reports a safety it does not provide (rule 12,
2026-08-01). **A gate that exists on the rehearsal and not on the performance is
the same sentence with the word "flag" swapped out.**

---

## What it is NOT

- **Not currently exploitable by accident.** `deploy_live.ps1` has never been
  run for real - its own header says so - and only Sleven runs it.
- **Not a claim that the live site is unguarded.** The unknown-file deploy
  guard, the payload sanity checks, the LIVE-payload check and the worker-name
  check are all present and all pass their control.
- **Not urgent in the sense of "go live".** Going live is Sleven's call and is
  not on the queue. This is about the button being right *when* he presses it.

---

## The patch, described exactly, NOT applied

I have not edited `deploy_live.ps1`. It publishes the public site, it has never
been run for real, and it is one command away from a thing this project cannot
take back. **This wants a go-ahead, not a quiet fix.**

When wanted, it is two blocks lifted from `deploy_testing.ps1` with the
project-relative paths already correct in both:

1. **Receipt gate** - `deploy_testing.ps1` lines ~113-160, plus its
   `-IgnoreFailedBuild` switch, verbatim. The receipt path is
   `testing\_src\.last_build.json` under `$ProjectPath` in both scripts,
   because both publish `testing\_deploy`.
2. **Browser-check gate** - lines ~264-347, plus `-IgnoreRedCheck` and its
   comma-splitting note. The check list is project-relative
   (`checks\_verify_*.mjs`) and identical for both payloads.

**Every escape hatch must come across with them.** A gate with no documented way
past it gets bypassed by editing the script, and then the bypass is invisible.

## The control has to come with it

`_verify_deploy_guards.py` currently asserts these behaviours for
`deploy_testing.ps1` only. Adding the gates without extending the control gives
the live script a guard nobody has ever seen fail — **an untested gate wearing a
reassuring name**, which is rule 12 verbatim. The control's fixture needs the
check files it does not currently create; that work is separate and is mine.
