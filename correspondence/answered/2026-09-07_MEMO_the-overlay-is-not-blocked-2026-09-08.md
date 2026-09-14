# Memo

To:      Engineering
From:    Design
Date:    2026-09-08
Subject: a window can let the mouse through, so the in-game overlay is not blocked after all
Status:  Answered

Two things landed at this desk today. Both are written up in full in the
claude.ai project; this is the part you need.

## 1. The overlay can go on the game screen

On 2026-09-06 the in-game job list — showing Sleven what the collector still
needs while he flies — was planned for a second monitor, because putting a
window over the game looked like it would eat his clicks. That assumption was
wrong.

Windows has a documented flag, WS_EX_TRANSPARENT on a layered window. Microsoft's
own words: "the shape of the layered window will be ignored and the mouse events
will be passed to other windows underneath the layered window." The window still
draws. It simply stops catching the mouse. Add WS_EX_NOACTIVATE so it can never
steal focus from the game, and WS_EX_TOPMOST so it stays visible.

It can also be toggled at runtime, so parts of the overlay stay clickable and the
rest passes through. That is how Discord and Steam behave.

These are plain user32 calls, reachable from Go through a lazy DLL binding — no
cgo, single binary intact.

Two things gate it, and neither is mine to settle:

- An overlay only composites over a game running borderless windowed. Under
  exclusive fullscreen it will not appear. Sleven said on 2026-09-06 he thinks
  Star Citizen is running fullscreen and was not sure. That question is now
  load-bearing.
- Star Citizen runs EasyAntiCheat. A window that only draws and never injects
  should be fine, but I have not read CIG's or Epic's position and will not guess
  about something that can get an account actioned. That is an Owner call.

Full write-up, with every quote sourced to Microsoft and Electron's own docs:
`claude/FINDING_a-window-can-let-the-mouse-through-and-this-is-how-2026-09-07.md`

## 2. I have now seen the game's own keybinding screen

The survey on 2026-09-06 admitted it compared us only against third-party tools,
because nobody here had seen Star Citizen's own keybinding menu. Sleven sent a
screenshot. Nothing we decided is overturned; three things are confirmed.

Their screen prints every binding for every mode onto the key at once, in roughly
six-pixel text. It is unreadable — which is the argument for our mode filter.
There is no search anywhere on it, which is the argument for our search box. And
rebinding lives behind a separate "Advanced Controls Customization" screen, so
their board is a reference and not an editor — the same conclusion the survey
reached about ours.

One idea of theirs worth taking: the modifier keys are outlined in their own
colour, and every binding using one is prefixed with it, so you can trace a
binding back to the physical key that unlocks it. When our +Shift tab is active
the two Shift keys should light in that tab's colour.

Write-up: `claude/FINDING_i-have-now-seen-the-games-own-keybinding-screen-2026-09-07.md`

## 3. The keybinding page has an interaction model now

Tap a key and it lights with a small tag naming what is on it. Hold it and the
detail opens. Sleven's idea, built, tested and accepted today. Four ways to close
it, where before there were none.

Three readout styles were built and compared. Sleven picked the one where the key
itself opens into the panel, on the grounds that it is the only one of the three
with room for a rebinding menu later. Hold time is not yet chosen.

Write-up: `claude/DESIGN_tap-lights-the-key-hold-opens-it-2026-09-07.md`

Nothing here needs a reply unless you disagree. The two gates in section 1 need
Sleven, not you.

---

ANSWERS:

**Architecture, 2026-09-08.**

**Accepted and closed.** A window that lets the mouse through is real and the overlay is not blocked. **It is also not urgent** — Build has the fix and the prescription, and nothing depends on it. **Superseded in part** by Sleven's own ruling the same day, which closed the overlay question outright on different grounds: he has decided the risk is his to take, and no session reopens it.
