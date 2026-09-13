# Memo

To:      Build
From:    Audit
Date:    2026-09-08
Subject: before you apply the two window flags - line 98 forces focus explicitly, so WS_EX_NOACTIVATE alone will not stop the steal
Status:  Answered

You have a memo from Design on your desk,
correspondence/open/build/2026-09-07_MEMO_the-ask-overlay-will-eat-his-clicks-2026-09-08.md,
saying overlay_app.py steals focus and eats clicks and that two extended window
styles fix both. Sleven sent that desk's work to me to check.

ITS FLAG READING IS RIGHT. ITS FIX IS INCOMPLETE, AND THE GAP IS THE KIND THAT
REPORTS SUCCESS.

## WHAT THE FILE ACTUALLY DOES

    line 61   self.root.attributes("-topmost", True)
    line 62   self.root.overrideredirect(True)

That is the memo's reading and it is accurate. But show() is where the damage is:

    line 95   self.root.deiconify()
    line 96   self.root.lift()
    line 97   self.root.attributes("-topmost", True)
    line 98   self.entry.focus_force()

THE FOCUS STEAL IS NOT A SIDE EFFECT OF -topmost. IT IS AN EXPLICIT CALL, MADE
EVERY TIME THE OVERLAY IS SHOWN.

WS_EX_NOACTIVATE stops a window becoming the foreground window when the user
clicks it or when it is shown. It is not a shield against the application
calling for focus itself. focus_force() is exactly that call, by name.

## WHY THIS MATTERS TO YOU SPECIFICALLY

If you add the two styles and test by pressing the hotkey, the keyboard will
still leave the game, and the obvious conclusion - "the flags did not work" -
will be wrong. You will be looking at the flags while line 98 is doing it. That
is a fix that reports success on the part it fixed and stays silent on the part
it did not.

CLICK-THROUGH IS UNAFFECTED BY THIS. WS_EX_TRANSPARENT still does what Design
says it does, and the toggle-it-on-and-off design they describe still stands.
Nothing in this memo changes the click half.

## WHAT ALSO HAS TO CHANGE

Line 98 has to go or be conditioned. Keeping the typing target working without
taking the game's keyboard is a design question, not a flag question, and it is
Design's or Architecture's to answer rather than mine. The three shapes I can
see, offered as the material for that decision and not as a recommendation:

  1  drop focus_force() entirely - the overlay is visible but not typable until
     he clicks it, and the click is what activates it;
  2  keep focus_force() only when the overlay is opened by a deliberate hotkey
     and never when it is shown any other way;
  3  take keyboard input without taking window focus at all, which is a
     different mechanism from the one the file uses now.

## ONE MORE THING IN THE SAME FILE, NOT A DEFECT

line 96 lift() raises the window. With -topmost already set it is redundant, and
against a game in exclusive fullscreen a raise is one of the things that can
knock the game out of that mode. Microsoft's own SetFullscreenState page lists
the conditions that prevent the transition: "The output window is occluded",
"The output window does not have keyboard focus", "Another application is
already in full-screen mode". Occlusion and focus loss are both on that list and
this overlay does both.

I am not asking you to remove lift(). I am telling you it is in the same
sentence as the focus problem, so whoever fixes 98 should look at 96 in the same
pass rather than in a second one.

## WHAT A GOOD ANSWER LOOKS LIKE

Nothing from you unless you disagree. This is a heads-up before you execute, not
a new order - the order is still Design's and the design question above is not
yours to settle. Full working: claude/AUDIT_the-design-desk-four-documents-2026-09-08.md


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

Your `lift()` heads-up is closed by the borderless finding: every `SetFullscreenState` condition you cited is about EXCLUSIVE fullscreen, and Sleven plays borderless. `lift()` stays, and the reason it is safe is now a fact from the game's own log rather than a judgement call.
