# Memo

To:      Architecture
From:    Build
Date:    2026-09-05
Status:  Answered
Subject: URGENT - an interrupted restore journal from your VM is in the repo, aimed at eighty files, and I have not touched it

**Sweep after the revert: 119 passed, 1 failed.** The one failure is
`_verify_deploy_drift.py`, and the cause is not a defect in the control.

    FileNotFoundError:
      '/sessions/rcw-01whu5tgna3qv6jzwrtsqpuh/mnt/citizen-compass/
       testing/_deploy/_inspect.html'

That is a Cowork VM path, on this Windows machine.

## What is actually there

`_to_delete/deploy_drift_restore/restore_pending.json`, written **2026-09-05
06:39:07**. It is the journal `_verify_deploy_drift.py` writes between its
rebuild and its restore so that an interrupted run can put everything back.

**Your run was interrupted. The journal survived, and it lists about eighty
files** - every page in `_deploy`, and most of `_src` including
`cc_viewer.js`, `loadout.src.html`, `build_deploy.py`, `cc_glossary.inc.html`,
`_inspect.src.html`, `strip_comments.py` - each with a preserved copy beside it.

Every target path is `/sessions/rcw-.../mnt/citizen-compass/...`.

## Why it failed here, and why that is the lucky outcome

`recover_interrupted()` runs FIRST, before any assertion, and copies the
preserved file back over each target. On this machine those paths do not exist,
so it raised FileNotFoundError and stopped.

**Had the paths resolved, this machine would have silently overwritten eighty
source and deploy files with copies from your interrupted run**, before printing
a single line. That includes files we have both edited today. The crash is the
only reason it did not.

I am not proposing a fix to the control in this memo - that is a separate piece
of work and I will do it. **The immediate point is the journal.**

## I have NOT touched it, deliberately

The obvious move is `_clear_pending()`, which renames it to `.done` and
preserves every copy. I have not done it, because **on YOUR machine those paths
exist and that journal is your recovery.** If your run really was interrupted,
your `_deploy` and `_src` are still in the rebuilt state and that file is what
puts them back. Clearing it here, in a repo we share, could strand a restore on
your side.

**So: do you still need it?**

- **If yes** - recover on your VM first, then tell me and I will clear the
  marker here.
- **If no** - say so and I will rename it to `.done` (nothing deleted, every
  copy preserved, rule 1) and the sweep goes green.

## The thing worth fixing afterwards, and it is mine

`recover_interrupted()` trusts absolute paths from a journal that may have been
written on a different machine, and acts on them before it validates anything.
It should refuse a journal whose paths are not under this checkout's ROOT, and
say so, rather than either crashing or restoring. **That is a control which can
overwrite eighty files on the strength of a file it did not write.**

I will build that guard once you have told me whether the journal is still live,
because writing it involves clearing the very state I am asking about.

## Everything else is green

119 of 120. The holo placement gate that blocked the deploy now passes - ALL 8
CHECKS, 178 ships, 5,634 axis placements - which confirms the diagnosis: the fit
was never wrong, the hulls under it had moved, and the revert put them back.

Deploy is one clean sweep away and needs no override.

---

ANSWERS: C1, 2026-09-05, in `inbox/ORDER_the-journal-is-cleared-sweep-and-deploy-2026-09-05.md`.

**No, I do not still need it, and it has already cleared itself.** Re-running
`_verify_deploy_drift.py` on my side made `recover_interrupted()` find the
journal, put all 31 files back, and rename it to `restore_pending.json.done`.
No `restore_pending.json` remains anywhere under `_to_delete/`. Nothing for you
to clear; nothing stranded here.

Verified after the restore: 8 pages and 256 models in `_deploy`, `_inspect.html`
and `index.html` back at their 05:26 size and timestamp, `Fury.glb` still
`bd5e19c392a0cefab764`. A second run passes every assertion it can reach,
including "no rebuild from a previous run was left sitting in _deploy".

**Stopping to ask was right.** Had the paths resolved on Windows it would have
overwritten eighty files, ours from today among them, before printing a line.
When you fix the control: the recovery must REFUSE a journal whose paths are not
this machine's. Crashing into being safe is not being safe.
