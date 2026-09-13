# Memo

To:      Build
From:    Owner
Date:    2026-09-09
Subject: AMENDMENT to the startup guard — a legitimate reason to set that key exists, found after I ordered it
Status:  Answered
**The guard order stands. One thing changed underneath it and you need it before
you build.**

## WHAT CHANGED

`claude --bare` — the mode that skips the expensive startup read — **requires
`ANTHROPIC_API_KEY` and deliberately ignores subscription login.** Anthropic's own
words, `code.claude.com/docs/en/headless`, *Start faster with bare mode*:

> "Set `ANTHROPIC_API_KEY` before running it, because bare mode doesn't use your
> subscription login"

> "In bare mode, Claude Code never reads OAuth credentials or the system keychain."

**So there is now a legitimate reason for that variable to be set**, which there
was not when I gave you the order.

## WHAT THE GUARD MUST NOT BECOME

**A guard that refuses on presence alone will one day block a run somebody meant
to make**, and the fix at that moment will be to switch the guard off. **A control
that gets switched off in a hurry is worse than no control**, because everyone
believes it is still there.

## SO

**Build it to refuse an UNDECLARED key, not any key.** The run declares which
billing it intends; the guard's job is to catch the mismatch between what was
intended and what the environment actually holds — and to refuse loudly, naming
the mismatch, never the value.

**How you express "declared" is yours** — you can see the entry points and I
cannot. What I am asking for is that the guard distinguishes *deliberate* from
*accidental*, rather than treating every key as an accident.

**Nothing here uses bare mode today**, so this is not urgent work. It is the
difference between a control that survives and one that gets disabled the first
time it is inconvenient.

## ONE MORE THING FROM THE SAME PAGE, FOR WHEN THE UNATTENDED WORK IS BUILT

> "`--bare` is the recommended mode for scripted and SDK calls, and will become
> the default for `-p` in a future release."

**If bare becomes the default, scripted runs stop using the subscription by
default.** Not today's problem. **Worth knowing before anything is designed around
`claude -p` being subscription-billed**, because that is exactly what the
automation proposal assumes.

Full record: `claude/VERIFIED_the-automation-proposal-first-four-claims-2026-09-09.md`.

---

ANSWERS:

**DONE, in both languages, and the mismatch table is the one you specified.**

    declared              usable key   verdict
    subscription / unset  no           allowed - the ordinary case
    subscription / unset  YES          REFUSED - the undeclared key
    api                   YES          allowed, and SAID OUT LOUD in the log
    api                   no           REFUSED - declared metered, cannot do it
    anything else         -            REFUSED - not guessed at

`pkg/apikeyguard` and `scripts/Assert-DeclaredBilling.ps1` both refuse a mismatch
rather than a key. `run_checks_scheduled.ps1` calls the PowerShell half;
`inbox_watcher.exe` and `roadmap-watcher` call the Go half. **The watcher binary
was rebuilt tonight so the running copy matches the amended package** - until then
one guard had two behaviours and both were live.

**Your reason is the part that shaped it, and it is written into both files** -
*"a control that gets switched off in a hurry is worse than no control, because
everyone believes it is still there."* A `claude --bare` run now declares
`CC_ANTHROPIC_BILLING=api` and proceeds, with the billing said out loud in the log
before the invoice exists. Nothing has to be disabled to make a legitimate run
work, which was the whole point.

**Permitting quietly is treated as the same defect as refusing quietly.** The
allowed metered path writes a BILLING NOTICE, and it was proven on the built
binary, not read in the source.

**On the future you flagged** - that `--bare` may become the default for `-p`: the
guard is shaped for it already. A scripted run that starts billing without saying
so is refused rather than silently allowed, which is the failure that change would
otherwise introduce. Nothing to do today; recorded so it is not rediscovered.
