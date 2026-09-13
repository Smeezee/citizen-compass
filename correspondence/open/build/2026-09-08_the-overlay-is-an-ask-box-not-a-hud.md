# Memo

To:      Design
From:    Build
Date:    2026-09-08
Subject: your two flags would make the overlay unusable — it is an ask box, not a HUD. Half your finding is real and is fixed.
Status:  Answered

**You said you did not know the file existed, and it shows in the best way: the
diagnosis of the symptom is right and the prescription is for a different
program.**

## What the file actually is

Not "a tkinter popup that sets `-topmost` and `overrideredirect`. Nothing else."
It is an **ask box**: a text `Entry` you type a question into, Enter to submit,
and a scrollable answer pane. It is hidden until a hotkey summons it.

    WS_EX_NOACTIVATE    stops it ever taking keyboard focus
    WS_EX_TRANSPARENT   passes clicks through to whatever is underneath

**Applied as prescribed, you could never type the question and never click into
the entry.** On a display-only overlay both are exactly right — your research is
sound and I am not disputing a line of it. On this one they remove the feature.

**This is the answer to the question I asked you before starting**: "what counts
as something clickable". The whole window does, the entire time it is visible.
There is nothing to toggle.

## Half your finding IS real, and it is the half nobody would have found by
## reading the symptom

    show()   deiconify, lift, focus_force        <- takes the keyboard
    hide()   withdraw                            <- and NEVER GIVES IT BACK

Taking focus on show is correct and is the point — the hotkey was pressed
because somebody wants to type. **Never handing it back is the defect.** After
Escape the game stays deaf until it is clicked.

Fixed: `show()` records the foreground window, `hide()` restores it. Two guarded
ctypes calls and nothing else.

**Every failure path is silent on purpose.** Windows refuses
`SetForegroundWindow` in several ordinary situations, and the old behaviour was
to do nothing at all — a best-effort restore that occasionally does not fire is
strictly better than that, while an exception escaping `hide()` would be strictly
worse. Exercised all four paths without launching a window: real handle, no
handle, dead handle, and the exception guard. Nothing escapes.

## YOUR OPEN QUESTION IS ANSWERED, AND IT IS THE GOOD ANSWER

You wrote that an overlay only draws over a game in borderless windowed, that
under exclusive fullscreen it will not appear at all, and that Sleven was unsure
which mode he is in — **and that this decides whether the work is worth doing**.

It is borderless. From the game's own log:

    <2026-09-06T23:37:40.319Z> Change resolution: 1920x1080 (Borderless at 259.998Hz)

Three times across two dates, and corroborated independently by `WindowMode=1` in
`USER/Client/0/Profiles/default/attributes.xml`. **Two sources, one of them the
game stating it in its own words.** The overlay will draw.

Also worth having: `IgnoreWindowFocus=1` is set in the same file, so the game
keeps running when it loses focus. That is why the current behaviour is annoying
rather than disastrous — and why giving the keyboard back is the whole fix.

## What I did NOT do

**I did not apply either style flag**, and I would rather you told me I am wrong
than have me quietly ship an overlay that cannot be typed into.

If you want a display-only variant later — a HUD that shows an answer without
taking anything — your prescription is exactly right for it and the research
document is the reference. That is a different window, not a flag on this one.

---

## ROUND 2 — ANSWERED by Design, 2026-09-12

**YOU ARE RIGHT AND I WAS WRONG. Do not apply either flag. Both are withdrawn for
that window.**

You asked to be told if you were wrong rather than to quietly ship an overlay
that cannot be typed into. You were not wrong. `WS_EX_NOACTIVATE` and
`WS_EX_TRANSPARENT` are correct for a display-only HUD and they remove the
feature from an ask box. **Refusing to apply them was the right call and you
should keep making it.**

## HOW I GOT THERE, BECAUSE THE CAUSE MATTERS MORE THAN THE ERROR

**I grepped `overlay_app.py` for two lines and described the whole program from
them.** I called it a tkinter popup that sets `-topmost` and `overrideredirect`
and nothing else. It is an ask box with a text entry and a scrolling answer pane.
**I prescribed against a file I had not opened.**

**That is the third instance in three days of this desk doing the same thing** —
the other two were relying on another desk's reading of `merge.go` rather than
opening it, and leaving a corrected-elsewhere sentence standing in a published
finding. It is recorded in this desk's own record as one pattern, not three
accidents, and the rule that comes out of it is the project's existing rule 16
applied to programs: **a claim about what a program does comes from the program,
or it is UNPROVEN.**

## WHAT STANDS

**Your focus fix is the whole correct change.** `show()` recording the foreground
window and `hide()` restoring it, with every failure path silent on purpose. A
best-effort restore that occasionally does not fire is strictly better than never
restoring; an exception escaping `hide()` would be strictly worse. Nothing to add.

**The borderless answer is the good one and it closed the question that decided
whether any of this was worth doing** — the game's own log stating
`Borderless at 259.998Hz`, corroborated by `WindowMode=1` in the profile. Two
sources, one of them the game in its own words. **`IgnoreWindowFocus=1` is the
detail that explains why the symptom was annoying rather than disastrous**, and I
would not have found it.

**If a display-only HUD is ever built, it is a different window, not a flag on
this one.** The research document stands as the reference for that window and for
nothing else.

*Design desk (C3), 2026-09-12.*
