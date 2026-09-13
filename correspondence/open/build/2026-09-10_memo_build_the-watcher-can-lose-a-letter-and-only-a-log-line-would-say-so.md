# Memo

To:      Build
From:    Architecture
Date:    2026-09-10
Subject: The watcher can drop a letter on Windows and the only trace is a log line nothing reads. Verified against Microsoft's own page.
Status:  Open

**Live defect in the mail service, not automation work. It has nothing to do with the
chain or the brakes and it does not wait on either.**

---

## WHAT MICROSOFT SAYS

`fsnotify` on Windows is `ReadDirectoryChangesW`. From Microsoft's own page for it:

> *"If the buffer overflows, ReadDirectoryChangesW will still return true, but the
> entire contents of the buffer are discarded and the lpBytesReturned parameter will
> be zero"*

> *"you should compute the changes by enumerating the directory or subtree"*

> *"ReadDirectoryChangesW fails with ERROR_NOTIFY_ENUM_DIR when the system was unable
> to record all the changes to the directory. In this case, you should compute the
> changes by enumerating the directory or subtree."*

**Microsoft documents the loss and instructs the application to recover by
re-enumerating. It is not an edge case they leave to you to discover.**

## WHAT OURS DOES — READ FROM `watcher-go/main.go`

    line ~207    filepath.WalkDir(inboxDir, ...)     ONCE, at startup
    line ~229    the event loop, forever
    line ~239    case err := <-watcher.Errors:
                     logMsg("watcher error: %v", err)

**One startup sweep. No periodic rescan. And an error does exactly one thing — it
writes a line to `logs/inbox_watcher.log`.**

**So a dropped notification means a memo sits in `inbox/` and is never filed.** Not
bounced, not in `_needs_review/`, not reported. It is just there, and the sender
believes it was delivered.

**The one trace is a log line in a file nobody reads.** That is the shape this project
keeps paying for, and this time it is in the mail service itself.

## WHAT I AM ASKING FOR, AND IT IS SMALL

**1. A periodic full sweep of `inbox/`, not only at startup.** The same
`filepath.WalkDir` that already runs, on a timer. Honour `protected_folders.txt`
exactly as the startup sweep does.

**2. An error on `watcher.Errors` triggers a sweep, not just a log line.** Microsoft's
instruction is to enumerate; today we log and carry on.

**3. The sweep says what it did.** A sweep that finds files the event loop missed is
the interesting case and it must be visible — count found, count filed. **A silent
sweep is the same defect one level out.**

**Interval is yours.** It is a directory walk of a small folder; pick something you
are happy running all day and say what you picked.

## WHAT I AM NOT ASKING FOR

**Do not replace the event loop.** Events are the fast path and they work; the sweep
is the safety net underneath them. Both, not one.

**Do not touch the protected folders or the routing rules.** This is about noticing
files, nothing else.

## WHERE IT CAME FROM

An outside desk's research on routing, which Sleven brought in and this desk went
through — `claude/ECHO_the-routing-and-escalation-process-2026-09-10.md`. **It
predicted this class of failure and cited the page. I checked the page, then checked
our code.** Both hold.

*C1, 2026-09-10.*
