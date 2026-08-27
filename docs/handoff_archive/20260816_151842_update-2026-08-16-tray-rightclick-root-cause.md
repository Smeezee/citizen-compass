# Update - the tray right-click: root cause found, observed, and fixed

My 2026-08-15 diagnosis was wrong and the erratum says so plainly:
`docs/ERRATUM_tray-right-click-was-never-delivered-2026-08-16.md`.

## The cause

**A message that is SENT is not a message that is POSTED.** `GetMessage` returns
posted messages. Sent messages - which is how the notification area delivers its
callback, and how `TrackPopupMenu` delivers `WM_COMMAND` - go straight to the
window procedure while the thread waits inside `GetMessage`, and never appear in
the `MSG` it hands back.

The tray's window procedure handled nothing at all. It passed every message to
`DefWindowProc`. All the handling lived in the message LOOP, looking for
messages that could never arrive there.

Which is why the tray was half-alive in a way nobody could explain: `wmClose`
and `wmAppOpenWindow` are messages the collector POSTS TO ITSELF, so they came
through the queue and worked. Everything the outside world drove was dropped.

Same defect twice in the same file: even if the menu had opened, `TrackPopupMenu`
SENDS its `WM_COMMAND`, so every menu choice would have been discarded too.

## Observed, not reasoned

`collector.exe -tray-probe` drives both delivery paths and detects a menu by
looking for a window of class `#32768` - a menu EXISTING ON SCREEN, not a call
that returned. On the fixed build:

    SENT: a sent callback opens the menu     menu IS on screen: hwnd=0x44063e
    SENT: it arrived at the WINDOW PROCEDURE  window procedure +1, loop +0

**Negative control fired.** Same probe against a build with the old window
procedure restored: posted path opens the menu, SENT path `menu did NOT appear`.
The symptom reproduces on demand, which is what makes the pass mean anything.

One thing could NOT be checked: `GetForegroundWindow()` returned 0, so no window
in this session held the foreground and nothing can be concluded about whether
the tray window could take it. Printed as COULD NOT CHECK, not as a pass.

## The testing blocker - answered without asking anyone to close anything

I said three times I could not verify this because the running collector holds
the single-instance lock. That is why a defect survived four builds, and it was
my problem to solve.

`-tray-probe` does not take the lock. It puts a SECOND, labelled icon in the
notification area and holds it for three minutes:

    citizen-collector\probe.exe -tray-probe

Sleven right-clicks the icon whose tooltip says **TRAY TEST**. His collector
keeps running. Nothing is sent, captured or written. The probe watches and then
shows a box saying MENU OPENED, or CLICK ARRIVED / NO MENU, or **NOT TESTED** if
no click ever arrived - never a pass for something that did not happen.

## Acceptance is still his mouse

Everything above is root cause plus negative control. It is not the acceptance
test and is not offered as one. What is needed: right-click, on screen, on a
build he is running.

Changed: `tray.go` (window procedure handles the tray messages; one shared
`handleCommand`; three counters; Exit posts WM_CLOSE so the icon is removed
rather than left as a ghost; the stale HWND_MESSAGE comments corrected),
`tray_probe.go` (new), `main.go` (`-tray-probe`). Not committed - no go-ahead.

pilot_dps viewer work stays paused. Nothing in `testing/` touched.
