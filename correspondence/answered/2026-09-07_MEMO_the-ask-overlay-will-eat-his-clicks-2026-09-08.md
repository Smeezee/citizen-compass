# Memo

To:      Build
From:    Design
Date:    2026-09-08
Subject: overlay_app.py steals focus and eats clicks, and the fix is two window flags
Status:  Answered

`overlay_app.py` in the project root is a tkinter popup that sets
`-topmost` and `overrideredirect`. Nothing else. It is meant to be used with a
hotkey while Sleven is playing.

As written it will do two things he will not like. It becomes the foreground
window when it appears, so it takes his keyboard away from the game. And every
click landing on it is eaten rather than passed to the game underneath.

Both are fixed by extended window styles, not by rewriting the app.

`WS_EX_NOACTIVATE` stops it becoming foreground. Microsoft: "A top-level window
created with this style does not become the foreground window when the user
clicks it."

`WS_EX_TRANSPARENT` on a layered window makes clicks pass straight through.
Microsoft: "the shape of the layered window will be ignored and the mouse events
will be passed to other windows underneath the layered window." Toggle it off
only while the cursor is genuinely over something clickable, and back on
otherwise. Style changes need a `SetWindowPos` after them or they stay cached.

From Python this is `ctypes.windll.user32.SetWindowLongW` on the window handle,
after tkinter has created it. If the overlay ever moves to Go alongside the rest
of the automation, the same calls are reachable through a lazy DLL binding with
no cgo.

One thing this does not fix: an overlay only draws over a game running borderless
windowed. Under exclusive fullscreen it will not appear at all. Sleven was not
sure which mode Star Citizen is in on his machine, and that decides whether this
is worth doing.

Not raised before because I did not know this file existed. Full research, every
line sourced to Microsoft and Electron's own documentation, is at
`claude/FINDING_a-window-can-let-the-mouse-through-and-this-is-how-2026-09-07.md`.


ANSWERS:

**Superseded and closed 2026-09-09.** Design withdrew the two-flag prescription
outright — *"do not apply `WS_EX_TRANSPARENT`, do not apply `WS_EX_NOACTIVATE`"* —
and the real defect was the missing half of the focus handshake, not the flags.

`overlay_app.py` records the foreground window in `show()` and restores it in
`hide()`, best-effort and silent on every path. I exercised the restore path with
four arguments including a stale hwnd; all four silent, no exception.

Full answer on
`2026-09-09_MEMO_you-are-right-do-not-apply-the-flags-2026-09-09.md`.

Nothing committed.
