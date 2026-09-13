# Memo

To:      Owner
From:    Build
Date:    2026-08-30
Subject: Q47 - the files are swapped; one restart left and it is yours
Status:  Answered

**One action, and the postman stops being you.**

Everything else in Q47 is finished. The new watcher is built and tested; the
scheduled task is still running the **2026-08-01** binary, which knows nothing
about memos.

    running   C:\...\citizen-compass\inbox_watcher.exe        5,736,960 bytes, 2026-08-01
    built     C:\...\citizen-compass\watcher-go\inbox_watcher.exe  5,751,296 bytes, 2026-08-30

## What to run

    Stop-ScheduledTask -TaskName 'Citizen Compass Inbox Watcher'

    # keep the old one - rule 1, and it is what you fall back to
    Move-Item C:\Users\david\citizen-compass\inbox_watcher.exe `
              C:\Users\david\citizen-compass\_to_delete\inbox_watcher.exe.pre-memo-20260830

    Copy-Item C:\Users\david\citizen-compass\watcher-go\inbox_watcher.exe `
              C:\Users\david\citizen-compass\inbox_watcher.exe

    Start-ScheduledTask -TaskName 'Citizen Compass Inbox Watcher'

The `Move-Item` line matters. My first draft of this memo used `Copy-Item -Force`
and told you the old binary was already safe. **Neither was true** - the move
aside is the step the permission layer blocked, so nothing has been preserved
yet, and `-Force` would have overwritten the only copy of a binary that is
currently doing its job. Corrected before you read it rather than after.

I tried to do this myself and **the permission layer refused it**, twice. I did
not work around it, because stopping a scheduled task and replacing a running
binary is exactly the kind of thing that refusal exists for. It is your call.

**Nothing is at risk if it waits.** Memos simply keep being filed as ordinary
documents, which is what has been happening all afternoon.

## Why it is worth doing now

Two memos I wrote today did not reach a tray. The first, at 15:2x, carried
`To:`/`From:`/`Subject:` correctly and the old watcher saw "update" in the
filename and filed it as a status update - its content went into
`LATEST_HANDOFF.md` instead of Architecture's tray. The second, an answer to
Architecture's memo, went to `docs/`. I have filed both by hand.

**Hand-filing works and is what Architecture is doing too, so this is not
urgent - it is just the last piece of a thing that is otherwise done.**

## What is already proven, so you are not approving something untested

`go test ./...` green, `go vet` clean. Six memo tests, four of them negative
controls. I did not take them on trust: disabling the 4,000-byte header cap in
`readMemo` - the exact defect the sixth test exists for - produced

    --- FAIL: TestAQuotedHeaderDeepInADocumentIsNotAnAddress
        a header 5000 bytes down was treated as the document's address

only that test, with a precise message. Reverted and re-verified clean.

`checks/_verify_correspondence.py` is written and green against the live trays,
and its self-test plants eight defects and catches 8 of 8. An open memo is
REPORTED, never failed, so a question sitting in a tray can never block a deploy.

The `Move-Item` step above makes this reversible: the 2026-08-01 binary ends up
at `_to_delete/inbox_watcher.exe.pre-memo-20260830`, so if the new one misbehaves
you stop the task, move that one back, and start it again.

**Filed straight into the tray** - the router that would have delivered this is
the thing the memo is about.

---

## UPDATE FROM ARCHITECTURE, 2026-08-30 15:50 — TWO OF THE FOUR STEPS ARE DONE

Sleven said *"you do it if he can't"*, so I did the half I can reach.

    [done]  the old binary moved to _to_delete/inbox_watcher.exe.pre-memo-20260830
    [done]  the new binary copied into place at the repo root
    [----]  Stop-ScheduledTask  -- needs Windows, which I do not have
    [----]  Start-ScheduledTask -- same

**AND I TESTED IT RATHER THAN ASSUMING.** I dropped a memo whose Subject
contains the word *update* - the exact case the old router gets wrong - and it
was filed to `docs/`. **So the process is still running the old code from the
renamed file.** Windows keeps a running executable alive after its file is
renamed; only a restart picks up the new one.

Both misfiled memos have been recovered into their trays by hand.

**So this is now ONE command, not four:**

    Restart-ScheduledTask -TaskName 'Citizen Compass Inbox Watcher'

If that is not available, `Stop-ScheduledTask` then `Start-ScheduledTask` with
the same name. Either way the files are already where they need to be, and the
old binary is kept rather than deleted if it has to go back.


ANSWERS:

**Done at 15:49. Nothing is owed.**

`Restart-ScheduledTask` does not exist in Windows PowerShell 5.1 - only `Stop`
and `Start` - so the one-liner failed as written. Stop, confirm zero processes,
Start:

    after stop:  0 process(es)
    State:       Running
    PID 15092, started 2026-08-30 15:49, from C:\...\citizen-compass\inbox_watcher.exe

Architecture had already moved the old binary aside and copied the new one in, so
only the restart was left. **A running Windows executable survives its own file
being renamed**, which is why the earlier file swap alone changed nothing and the
next memo still misrouted.

**PROVEN ON THE LIVE PATH, NOT IN A TEST.** I sent a memo whose Subject contains
the word *update* - the exact input that misrouted twice today, once for
Architecture at 15:50 and once for me at 15:2x - and it landed in
`correspondence/open/architecture/`, not in `docs/`. So `classifyMemo` runs
before the update check on the running service, with the input that actually
broke it.

The 2026-08-01 binary is kept at
`_to_delete/inbox_watcher.exe.pre-memo-20260830`. If the new one ever misbehaves:
stop the task, move that back, start it.

**Q47's DONE-WHEN is fully satisfied** - builds with `memo.go`, tests pass and
are proven able to fail, the watcher is redeployed, and a memo dropped in
`inbox/` lands in a tray.

You are out of the postman job.
