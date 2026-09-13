# Memo

To:      Build
From:    Owner
Date:    2026-09-09
Subject: FIRST JOB ON BOOT — the two halves of the API key guard disagree, and both are live
Status:  Answered
**Read this before anything else. The session that wrote it wound down at 21:40
and flagged this on its way out rather than letting it sit.**

## THE STATE IT LEFT, IN ITS OWN WORDS

    pkg/apikeyguard              AMENDED — refuses a mismatch
    Assert-DeclaredBilling.ps1   AMENDED — refuses a mismatch
    run_checks_scheduled.ps1     calls the amended one. LIVE.
    inbox_watcher.exe            built 21:06 from the PRE-amendment package.
                                 Refuses on PRESENCE. LIVE.
    Assert-NoApiKey.ps1          gone — _to_delete/2026-09-09_apikey_guard_v1/

**One guard, two behaviours, both running.** Nobody can currently say what this
machine does when that variable is set, and that is worse than either behaviour
on its own. **A control whose behaviour cannot be stated is not a control.**

**Rebuild the watcher from the amended package so the two halves agree.** That is
the job. Prove it the way the last session proved the first swap — trip the guard
on a test binary, confirm the refusal reaches `logs/inbox_watcher.log`, confirm
the log does not contain the planted value, and confirm the live binary is
byte-identical to the one you tripped. **That method was right and it is the
standard now.**

## THE RED CONTROL — AND DO NOT MAKE IT GREEN BY WEAKENING IT

`checks/_verify_api_key_guard.py` is **27 passed, 1 failed.** The failing case is
an empty-but-present variable, and the diagnosis was: PowerShell cannot hold one.
Both `$env:X=''` and `[Environment]::SetEnvironmentVariable('X','','Process')`
delete the variable, so the state the test wants to create does not exist on that
path.

**That reads correct to me and I am not overruling it.** But a case that cannot
exist is not a case that failed, and this repository already has the mechanism for
that distinction — `_verify_community_mark.py` and `_verify_panel_dismiss.mjs`
both exit **2** for NOT PERFORMED.

**Two things before you reach for it.**

**It does not unblock a deploy.** `failed` and `not_run` both refuse. So this is a
question about the sweep telling the truth, not about getting past a gate. **Do
not treat it as a way to ship.**

**And prove the impossibility before you declare it.** "PowerShell cannot" is not
"Windows cannot" — a native process may be able to set what PowerShell will not.
**If it genuinely cannot exist on this platform, say so with what you tested and
retire the case with its reason attached. If it can, build it and keep the case.**

## WHAT IS ALSO IN YOUR TRAY, AND THE ORDER I WANT

    1  this
    2  the six old letters — say DONE / SUPERSEDED / NEVER STARTED for each
    3  the card mark build order
    4  the small import
    5  the RAPTOR and family_id work

**Three letters you listed as blocked on the `.claude/settings.json` permission
are NOT blocked.** I authorised that edit this morning in writing and the memo is
in your own tray:
`2026-09-09_20260909_memo_audit-to-build_the-stop-hook-is-authorised-sleven-said-go.md`.
**Read it before you carry any of them forward as waiting on me.**

## ONE THING THAT IS NOT A JOB

The last session filed **twelve timestamped updates** to `docs/handoff_archive/`
today, one per piece of work, and that record is the reason any of tonight could
be reconstructed. **Keep doing exactly that.** It is worth more than the day page
and it is the thing that stops a desk being invisible between reports.

---

ANSWERS:

**Both jobs done. One guard, one behaviour, and the red case was real.**

## THE REBUILD

    old binary   3c15544f...  moved to _to_delete/2026-09-09_inbox_watcher_presence_guard/
    rebuilt      6b22ec29...  byte-identical to the test binary whose guard I tripped
    running      one pid, 8336, since 21:58:19

Proven your way and it is the standard: a TEST binary first, tripped before
anything live moved, the refusal confirmed in `logs/inbox_watcher.log`, the log
confirmed free of the planted value, and the live binary confirmed identical to
the one that was tripped. **It is also reproducible** - the live copy was built
separately and came out the same bytes.

**That the old one was pre-amendment was proven twice, not assumed from its
build time:** it carries neither `CC_ANTHROPIC_BILLING` nor `BILLING NOTICE`, and
its own v1 PRESENCE wording is sitting at `logs/inbox_watcher.log:4132`. The
string detector was proven both ways before it was trusted.

**Six states run against the built binary**, in a scratch project root so no
ALLOWED case could start a second watcher on the real inbox:

    key set, nothing declared     REFUSED 78    the accident
    declared api, no key          REFUSED 78    *** the discriminator ***
    declared "yes"                REFUSED 78    unrecognised, not guessed
    declared api + key set        ALLOWED       BILLING NOTICE in the log
    nothing set                   ALLOWED       silent, correctly
    key present but EMPTY         ALLOWED       NOTE path

The second is the one that proves the swap was needed: a presence-only guard
would have allowed it.

## THE RED CONTROL — NOT MADE GREEN BY WEAKENING IT

**You told me to prove the impossibility before declaring it. It is not
impossible, so nothing was retired.**

The empty-but-present state exists on this platform and I produced it from two
independent launchers. What was actually broken was the instrument:
**`Test-Path Env:X` disagrees with itself inside one process** for an empty
variable - True once, False afterwards, with nothing between the readings but the
readings - while `Get-ChildItem Env:` reported it present every time. The guard's
presence test now reads the environment block.

**No verdict was ever wrong.** What was wrong is that the refusal said *"is not
set at all"* about a variable that was set, and the "present but EMPTY" notice
could never fire at all. **That second one had no case covering it**, because
every existing case was a refusal - so a control now exists for the allowed half.

    fixed guard      30 passed, 0 failed
    OLD guard back   28 passed, 2 FAILED   both new assertions, and only those
    fixed guard      30 passed, 0 failed
    --self-test      the inverted run fails, as it must

**Both new checks have been seen to fail.** Driven with known-bad input, not read.

## THE TWELVE UPDATES

Still doing it. Seven filed tonight, one per piece of work, plus two corrections
of my own errors.

## AND THREE THINGS I DID NOT TOUCH

**The whole billing guard is UNTRACKED** - `pkg/apikeyguard/`,
`scripts/Assert-DeclaredBilling.ps1` and `checks/_verify_api_key_guard.py` all
show `??`. The newest safety control in the project exists only in the working
tree. Nothing committed; it needs your word.

**Section 3 compares the two guards' CONSTANTS, not their behaviour.** This entire
defect was a behavioural disagreement and section 3 passed throughout. A
behavioural comparison is buildable and is not started.

**The guard's own header overstates its contract** - it says `"API"` and a
trailing space must not become permission; the code lowercases and trims, and the
unit tests deliberately assert that they do. The tested behaviour is right; the
prose is wrong. One sentence, not touched, waiting on your word.
