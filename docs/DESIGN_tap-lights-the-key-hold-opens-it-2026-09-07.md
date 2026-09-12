# Tap lights the key. Hold opens it.

**C3 · 2026-09-07 · settled interaction model for the keybinding board**
**On disk 2026-09-12. It existed only in the claude.ai project until then.**

Sleven's idea, built and accepted the same session. This replaces the click-to-open
behaviour the board has had since it was first drawn, and it replaces the fixed side
panel that was rejected outright on 2026-09-06.

## The model

**Tap a key** — it lights, and a small see-through tag appears above it naming the key
and its first binding, ending with "hold to open". Nothing locks. The light holds for
about eight tenths of a second, then fades over a fifth of a second. The tag stays a
touch longer, one second, because it is the part you read.

**Hold a key** — a bar fills left to right across the bottom of the keycap. When it
reaches the end the detail opens. The fill time is what makes this feel right or wrong,
so the page carries a switch for it: 0.25s, 0.45s, 0.7s, 1s, defaulting to 0.45s.
Sleven has not yet picked the number.

**Let go early** — it was a tap. The bar stops, the light does its short fade, nothing
opens.

This works identically for the mouse and for the physical keyboard. Pressing the real G
key on the real keyboard runs the same tap-or-hold test as clicking the drawn G.

**Closing** — Escape, clicking the same key again, clicking anywhere off the board, or
the small × on the panel. Before this session there was no way to close it at all, which
Sleven hit immediately.

## Why this beats what it replaces

A single click doing two jobs — telling you which key you touched, and opening a panel —
meant every glance cost a panel you then had to dismiss. Splitting it by pressure means
the cheap question (what is this key?) gets a cheap answer, and the expensive question
(show me everything on it) costs a deliberate extra half-second. The panel stops being
something that happens to you.

It also gives the future rebinding menu somewhere to live without another click target.
Whatever we eventually put behind the hold — the full binding list, the rebind control,
the per-mode breakdown — inherits a gesture the user has already chosen to make.

## The visual treatment, as settled

**Readouts** — three remain. *Glass at the key*: a genuinely translucent card that snaps
to the side of the key with room for it and never covers the key itself, carrying a thin
coloured bar on the edge that faces the key. *The key opens*: the key itself grows into
the panel and the rest of the board drops to 22%. *No box at all*: the board falls to 7%,
the pressed key stays lit, and the answer is set in large type in the space beside it
with no container of any kind. Row ribbon was cut — Sleven did not pick it.

Sleven's stated leaning: a mix of glass and the key-opening, with the key-opening favoured
for the extra room it gives a future menu. Not decided.

> **AMENDED 2026-09-12: THE KEY OPENS IS CHOSEN.** Sleven committed to it after this
> document was written, for the reason it names — the room it leaves a future menu.
> Glass and no-box remain in the page as switchable alternatives and are not the design.

**Key light** — four resting styles for bound keys: filled, glow (a soft bloom with no
hard outline — the outline version was rejected, "more of not the edge"), lit cap, and
underglow. The pressed key overrides all four with an orange ring, which is the one
colour nothing else on the board uses.

**Glow restraint** — the first pass bloomed 88px and bled onto neighbouring keys.
Rejected. The accepted values are a 2px ring, a 13px halo at 52%, and a 26px halo at 16%.
Anything wider reads as mess on a board this dense.

**Motion** — press is 55ms with a slight squash. Release springs back over 300ms and one
faint ring, reaching 8px, leaves the key. The panel fades rather than pops. The first
version of the release ran nearly two seconds and was called out as too long.

## Open, not decided

Which readout wins. What the hold time should be. What actually goes behind the hold once
this stops being a reference and starts being a rebinder. And Sleven wants outside
opinions before committing — the page is private to him, so it either gets shared from
its own share menu into his org, or Code puts it on the live site at a quiet address.
That second option is Code's call, not mine.

> **2026-09-12:** the readout question is closed (the key opens). **The hold time is
> still open and is the one thing outstanding on this page.** The page carries the
> switch; nobody has picked a number.

## Checked and not checked

**Checked:** tap, hold, early release, Escape, click-away, and click-the-same-key-again
were all driven in a real browser and their resulting state read back — the tap leaves no
panel open, the hold does, and all four close paths clear it. Every readout and every key
light rendered and was looked at. No JavaScript errors in any pass.

**Not checked:** how any of the timings feel to a human — I can only measure that the
timers fire, not that 0.45s is the right number. Touch screens: there is no touch handling
at all, so on a tablet or phone the hold gesture is untested and probably broken. Whether
holding a physical key that auto-repeats behaves correctly on every OS — repeat events are
ignored, but that is only tested on one browser. Screen readers. Anything at a window
width other than 1400px.
