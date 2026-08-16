# ERRATUM - the tray right-click, root cause observed

**2026-08-16.** Supersedes my diagnosis of 2026-08-15, which was wrong.

---

## WHAT I SAID, AND WHY IT WAS WRONG

On 2026-08-15 I attributed the dead tray menu to my own change parenting the
tray window to `HWND_MESSAGE`, reasoning that a message-only window cannot take
the foreground and `TrackPopupMenu` needs an owner that can. I reverted it and
called that the fix.

That reasoning is sound in general and irrelevant here. Sleven reports the menu
has **never** opened, on every version, including builds made before
`HWND_MESSAGE` existed anywhere in this codebase. The revert therefore cannot
have fixed anything, and the comment block it left behind in `tray.go` asserted
a cause that the timeline rules out.

It was reasoning from source, which is the failure mode this project keeps
paying for. The correction below is observed instead.

---

## THE ACTUAL ROOT CAUSE

**A message that is SENT is not a message that is POSTED.**

`GetMessage` returns *posted* messages. *Sent* messages - `SendMessage`,
`SendNotifyMessage`, and everything the shell uses to deliver notification-area
callbacks - are delivered **directly to the window procedure** while the thread
sits inside `GetMessage`, and never appear in the `MSG` that `GetMessage` hands
back.

The tray's window procedure was:

```go
wndProc := syscall.NewCallback(func(h uintptr, msg uint32, w, l uintptr) uintptr {
	r, _, _ := procDefWindowProcW.Call(h, uintptr(msg), w, l)
	return r
})
```

It handled nothing. Every tray message went to `DefWindowProc` and was
discarded. All the handling lived in the message **loop**, checking
`m.Message == wmTrayCallback` on messages `GetMessage` returned - which the
shell's callback never is.

That also explains, exactly, which parts of the tray *did* work: `wmClose` and
`wmAppOpenWindow` are messages this program **posts to itself**, so they arrived
through the queue and the loop saw them. Every path the program drove itself
worked. Every path the outside world drove was dropped. Nobody noticed, because
the code that would have handled it was present, correct-looking, and
unreachable.

**Second instance of the same defect, in the same file:** `TrackPopupMenu`
*sends* its `WM_COMMAND` to the owner window. So even on a build where the menu
had opened, every menu choice would have been discarded by the same
`DefWindowProc` line. The menu would have appeared and done nothing.

---

## HOW IT WAS OBSERVED, NOT REASONED

`collector.exe -tray-probe` (`citizen-collector/tray_probe.go`) drives the tray
both ways a message can reach a window and reports what came out. It detects a
menu by looking for a window of class `#32768` - the class Windows has given
every popup menu since 3.0 - so what is checked is *a menu existing on screen*,
not a `TrackPopupMenu` call having returned.

Measured on the fixed build:

```
[ok  ] POSTED: a posted callback opens the menu       menu IS on screen: hwnd=0x43063e
[ok  ] POSTED: it arrived through the message LOOP    loop has now seen 1 callback(s)
[ok  ] SENT:   a sent callback ... opens the menu     menu IS on screen: hwnd=0x44063e
[ok  ] SENT:   it arrived at the WINDOW PROCEDURE     window procedure +1, loop +0
[ok  ] a SENT menu command reaches its action         action fired: "open pictures"
```

`window procedure +1, loop +0` is the finding stated as a number: the delivery
path the notification area actually uses reaches the window procedure and is
invisible to the loop.

**The negative control fired.** The same probe was run against a build with the
pre-fix window procedure restored:

```
[ok  ] POSTED: a posted callback opens the menu
[FAIL] SENT:   a sent callback ... opens the menu     menu did NOT appear
[ok  ] SENT:   it arrived at the WINDOW PROCEDURE
```

The posted path works and the sent path does nothing - which is precisely the
symptom, reproduced on demand. A check that cannot fail is not a check; this one
fails on the broken build and passes on the fixed one.

**One thing could not be checked and is not being reported as passed.**
`GetForegroundWindow()` returned 0 during the run, meaning no window in the
session held the foreground at all. Nothing can be concluded about whether the
tray window could have taken it. The probe now prints that as COULD NOT CHECK.
It did not prevent the menu from appearing.

---

## THE FIX

`tray.go`:

- the window procedure handles `wmTrayCallback` (right- or left-button up ->
  `showMenu`) and `WM_COMMAND`, then falls through to `DefWindowProc`
- the `WM_COMMAND` switch that lived in the message loop is now one method,
  `handleCommand`, called from both paths, so the two cannot drift apart the way
  they already had
- three counters - `trayCallbackViaWndProc`, `trayCallbackViaLoop`,
  `trayMenuShown` - so the next report of this is a number rather than an
  argument
- the stale comment blaming `HWND_MESSAGE` is replaced with this cause

`Exit` also now posts `WM_CLOSE` instead of returning out of the loop, so the
icon is removed on the way out rather than left as a ghost.

---

## THE TESTING BLOCKER, WHICH WAS ALSO THE REASON THIS SURVIVED

I said three times that I could not verify this because the running collector
holds the single-instance lock. That was a real constraint and a bad answer.

`-tray-probe` runs **without taking the lock**, so it puts a second, clearly
labelled icon in the notification area and holds it for three minutes while
Sleven right-clicks it. His collector keeps running. Nothing is sent, captured
or written. The probe watches only, and reports whether a real click arrived and
whether a menu appeared - and says NOT TESTED, never PASS, if no click ever came.

**Acceptance is still a human's mouse.** Everything above is the root cause and
the negative control. It is not the acceptance test and is not offered as one.
