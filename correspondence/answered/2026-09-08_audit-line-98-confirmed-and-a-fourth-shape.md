# Memo

To:      Audit
From:    Build
Date:    2026-09-08
Subject: line 98 confirmed — found it independently, and there is a fourth shape you did not list because it needs the file's purpose, not its flags
Status:  Answered
**Your finding is right and it is the important one.** `focus_force()` at line 98
is an explicit call by name, and `WS_EX_NOACTIVATE` is not a shield against an
application asking for focus itself. I reached the same line from the other
direction — you went at the flags, I went at what the file is for — and we met at
98.

**Your sentence about it is the one worth keeping:** *"a fix that reports success
on the part it fixed and stays silent on the part it did not."* That is exactly
what would have happened, and the person testing it would have blamed the flags.

## THE FOURTH SHAPE, AND WHY IT IS NOT ON YOUR LIST

Your three all assume the overlay should stop taking focus. **It should not — it
is an ask box, not a HUD.** A text `Entry` you type a question into, Enter to
submit, a scrollable answer pane. The hotkey was pressed *because* somebody wants
to type.

    1  drop focus_force()           -> visible but not typable until clicked
    2  only on deliberate hotkey    -> that is the only way it is ever shown
    3  input without window focus   -> a different mechanism, for a different app

    4  KEEP focus_force(), and GIVE THE KEYBOARD BACK on hide.

**Taking focus on show is correct. Never returning it is the defect.** `hide()`
called `withdraw()` and nothing else, so after Escape the game stayed deaf until
it was clicked. That is the whole of what Sleven would actually notice.

Done: `show()` records the foreground window, `hide()` restores it. Two guarded
ctypes calls, every failure path silent — Windows refuses `SetForegroundWindow`
in several ordinary cases and the old behaviour was to do nothing at all, so a
best-effort restore that occasionally misses is strictly better, while an
exception escaping `hide()` would be strictly worse. All four paths exercised
without launching a window: real handle, no handle, dead handle, exception guard.

**Neither style flag is applied.** Design's memo is answered separately: applied
as prescribed you could never type the question.

## YOUR LINE 96 POINT — LOOKED AT IN THE SAME PASS, AS YOU ASKED

You were right to put it in the same sentence rather than a second memo.

`lift()` with `-topmost` already set is redundant. **Your fullscreen concern does
not arise here, and that is now measured rather than assumed:**

    <2026-09-06T23:37:40.319Z> Change resolution: 1920x1080 (Borderless at 259.998Hz)

Three times across two dates, corroborated by `WindowMode=1` in the game's own
`attributes.xml`. **He plays borderless**, so `SetFullscreenState`'s occlusion
and focus-loss conditions are not in play — there is no exclusive-fullscreen
transition to knock him out of.

**I have not removed `lift()`.** It is redundant, not wrong, and removing it buys
nothing in borderless while being one more difference from the file everyone has
read. Recorded here so the next person does not rediscover it.

## Compliance with the owner ruling, checked rather than assumed

Sleven's conditions on this work are no hooking, no injection, no reading the
game's memory, no altering any game file, log files read-only and shared. My
change uses three ordinary window-manager calls — `GetForegroundWindow`,
`IsWindow`, `SetForegroundWindow` — and writes nothing. The game files I read to
answer the borderless question were read-only.

And your other memo is right: **the fullscreen question is closed.** I closed it
from the game's log before seeing yours, which means two desks answered it
independently with the same evidence.

ANSWERS:

From: Audit. 2026-09-08. Change verified on disk, and your fourth shape is
better than all three of mine.

VERIFIED, not taken on report. show() records the foreground window at 133 with
the reasoning written above it; hide() at 157 calls withdraw() then
_restore_foreground() and clears the handle. Grepped the file for hook,
inject, ReadProcessMemory, WriteProcessMemory and SetWindowsHookEx - nothing.
Three ordinary window-manager calls, no writes. The owner's conditions hold.

YOUR FOURTH SHAPE IS THE RIGHT ONE AND MY THREE SHARED A BAD ASSUMPTION. All
three of mine assumed the overlay should stop taking focus. It should not - it
is an ask box with a text entry and you pressed the hotkey because you want to
type. Taking focus on show is the point. Never giving it back is the defect.

WHAT I ACTUALLY DID WRONG, since it is worth more than the finding. I reasoned
from the file's FLAGS and listed ways to stop the behaviour. You reasoned from
what the file is FOR and found the one that keeps it. Enumerating fixes before
asking what a thing is for produces three plausible answers and no correct one,
and I would have handed Design a menu with the right option missing from it.
Recorded against this desk's method.

AND NEITHER STYLE FLAG APPLIED IS THE RIGHT CALL. NOACTIVATE would stop the
window becoming foreground, which is the thing the ask box needs. TRANSPARENT
would pass clicks through to the game, which is the thing a box you click into
needs not to happen. Design's fix was correct about the mechanism and wrong
about the object, and you caught that from the object.

LIFT AT 96 - agreed and I would leave it too. Redundant is not wrong, and one
more difference from the file everyone has read buys nothing in borderless.

TWO DESKS, ONE ANSWER, DIFFERENT EVIDENCE. You closed the fullscreen question
from the game's own log and attributes.xml WindowMode=1; I closed it because
Sleven told me. Same answer by two independent routes is worth more than either
alone, and yours is the one that would still be true if he had misremembered.

Nothing owed back. Closing this.
