# Memo

To:      Build
From:    Owner
Date:    2026-09-10
Subject: Two things in the `_replies` path that fail silently, both read out of the watcher source, and one thing I checked and cleared

Status:  Open

**You are mid-build on step B. This is not a stop and it is not a critique of the
design — it is two things that will fail QUIETLY if they are not handled, in the exact
way this project has already paid for once.** Read it before the probe, not after.

---

## 1. `inbox/_replies/` MUST EXIST BEFORE THE PROBE RUNS

**If the allowance is `Edit(inbox/_replies/**)` and that directory does not exist, the
desk cannot create it, cannot write the reply, and the run exits 0 reporting success
with nothing on disk.**

**That is not a theory. It is the measured failure of 2026-09-10** — a desk read the
letter, got the numbers right, could not write, and the run returned exit 0,
`subtype: "success"`, `is_error: false`. $0.19 for nothing. **Every signal the launcher
checks said clean.**

**A path allowance is permission to WRITE AT a path. It is not permission to bring the
path into existence.** Whether your harness creates a missing parent is a question with
a real answer, and the answer decides whether the probe proves anything.

**So: create it with a `.keep`, committed, before the run** — or prove the desk can
create it and say which you did. **Either is fine. Assuming is not.**

## 2. A REPLY IN A SUBDIRECTORY IS INVISIBLE TO THE FLOOD GUARD

From `main.go`, and the comment says it is deliberate:

    // pendingInboxFiles counts files still waiting at the top of inbox/.
    //
    // Top level only, and deliberately: the protected subdirectories under
    // inbox/ are not a work queue, and counting them would make the watcher
    // believe it is permanently busy and never regenerate.

**`_replies/` is a subdirectory, so replies sitting in it count as ZERO pending.**

**Consequence: the coalesce never engages for replies.** Each one takes the full
expensive tail — `rescanAndScore()` plus `regenerateHandoff()`, measured at about
seventy seconds together. **Ten replies is ten full runs instead of one.**

**And the reason coalescing exists is a CORRECTNESS reason, in your own comment:** a
slow tray means acting on an order that has already been withdrawn. Three orders landed
on one row on 2026-09-07, each reversing the last.

**This is a regression, not a break. It does not stop step B and it must not delay it.**
But it is the difference between the reply path being usable and the reply path being
the slowest part of the machine, and it is much cheaper to see now than after the
doorbell is wired.

**Not asking you to fix it inside step B.** Name it, put it where the supersede
requirement went, and carry on.

---

## 3. WHAT I CHECKED AND CLEARED — THE WATCHER DOES RECURSE, SO THE REPLY WILL BE FOUND

I expected this to be the defect and it is not. **From `main.go`, verified rather than
assumed:**

    addWatchRecursive(inboxDir)   walks and watches every existing subdirectory
    handleFsEvent                 a NEW directory gets watcher.Add AND a walk of
                                  anything already inside it, then processPath on
                                  each file
    the startup sweep             WalkDir over the whole tree, not the top level

**So a memo written into `inbox/_replies/` is picked up and routed like any other,
including when the folder is created after the watcher started.** That half is sound
and you do not need to do anything about it.

**`isProtected` keys on the FIRST path segment under `inbox/` only** — so `_replies`
is unprotected and stays unprotected, and it cannot accidentally shadow either
protected folder. Also fine.

---

**Nothing here authorises anything new. No database work, no deployment, no
unrestricted execution, and the Looking Project is excluded entirely.**
