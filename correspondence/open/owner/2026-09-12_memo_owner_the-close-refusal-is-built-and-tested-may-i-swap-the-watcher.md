# Memo

To:      Owner
From:    Build
Subject: The watcher repair that stops an unmarked close from blocking a deploy is built and tested. May I swap it in? Same procedure as your STEP A, written out below.
Status:  Open

**One question at the bottom. Nothing has been swapped.**

## WHAT IT FIXES

**Tonight two sweeps, 44 minutes each, were spent on letters filed as Closed without the `CLOSED:` marker.** The mail check finds them only at sweep time, and a red sweep blocks the deploy.

**The repair moves the check to FILING time.** Architecture ordered it, and it is the first of the three mail repairs.

- A Closed or Done letter without its record is refused to `_needs_review/`, with a one-line reason telling the writer what to add.
- **It never reaches `answered/`, so it can never block a deploy again.**

## THE PROOF, ALREADY DONE ON THE SOURCE

- `go test ./...` passes, including seven new tests. The first one is tonight's exact case: a bare `CLOSED.`.
- **With the new check disabled, all four refusal tests fail.** With it restored, they pass. So the tests can see the defect.
- **The new binary should differ from the running one by this change alone.** File times show no other watcher source changed since the running binary was built on 2026-09-10.

    new      watcher-go/inbox_watcher_pending_20260912.exe   sha256 1594d21deb4d3bd1...
    running  inbox_watcher.exe                                sha256 f9d983b2ea7c8541...

## THE SWAP, IF YOU SAY GO - YOUR STEP A PROCEDURE

1. **Preserve the running binary first** under a dated rollback name: `_to_delete/inbox_watcher.exe.rollback-20260912`. The path comes back in the report.
2. Stop the one watcher process, copy the new binary into place, and start it the way the scheduled task does.
3. **Confirm exactly one watcher process is running,** not two and not zero.
4. **Verify on the live tree with test letters only,** each clearly named as a test:
   - A Closed letter with only a bare `CLOSED.` must land in `_needs_review/` with the reason. It must NOT reach `answered/`.
   - A Closed letter WITH a proper `CLOSED:` record must land in `answered/`.
   - An Open letter must still reach its tray. This checks that normal mail is untouched.
5. **Close out every test letter** by moving it to `_to_delete/`, and name each one in the report.
6. **Run the mail check** and confirm it passes with the test letters gone.
7. **Report and stop.**

**Timing:** after tonight's second deploy. The sweep for the "0 m" dimension fix is running now, and I will not swap the mail service mid-sweep.

## THE QUESTION

1. **Go, or not yet?**

*Build (Code), 2026-09-12.*
