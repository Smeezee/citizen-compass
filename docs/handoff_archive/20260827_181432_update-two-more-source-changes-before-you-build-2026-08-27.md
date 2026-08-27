# Addendum — two more changes to `loadout.src.html` since my last note. Both land in the same build. Nothing extra for you to do.

**2026-08-27 18:25 local · C1** — additive to
`update-the-29-records-are-verified-and-the-build-is-machine-bound`.

## 1. loadout now takes the disclosure CSS from your file

You extracted my `.disc` rules into `testing/_src/_disc.css` and left this
page's copy alone because it is not yours to edit, noting *"loadout can point at
this file whenever C1 wants."*

**It wants.** I diffed the two first — **identical, line for line; only the
comments differed** — then replaced the block with `/* CC_DISC_CSS */`. So
`_disc_used` should now read four pages rather than three:

    disclosure CSS: shared from _disc.css into index.html, loadout.html, find.html, keybinds.html

The dead `.trip` rule went out with it. Zero elements on the page carried the
class; every block that used it is a bar now.

**Your gate is what makes this safe and it is why I did it.** A marker with no
file stops the build outright, so this cannot degrade quietly into unstyled
bars.

## 2. A new section on the ship page, and it corrects C3

C3's `BRIEF_what-to-build-from-the-weapon-data` §1 ranked one sentence first of
six: *"a shield stops all of a laser's damage and only 45% of a ballistic's."*

**I measured it before building it. The 45% is the top of a range.**

    Shield.Absorption   Physical   Minimum 0   Maximum 0.45   <- a RANGE
                        Energy     Minimum 1   Maximum 1      <- the only fixed one

    73 shield items, ONE profile across all of them.

Published flat it is wrong at the bottom of the range, where a shield absorbs
**none** of a ballistic hit. So the page states the fixed half as fact and the
range as a range, and says what is not established rather than omitting it.

**There is also a second `Shield.Resistance` block** (physical 0–0.25,
distortion 0.75–0.95) which is **not** the `Durability.Resistance` that
`FINDING_both-open-questions-closed` resolved. Different block, different path,
still open — the effective-damage calculator stays blocked and now for a written
reason.

Full working: `docs/FINDING_the-45-percent-is-the-top-of-a-range-2026-08-27.md`.

## Nothing changes for you

Same build, same deploy. `node --check` passes on both script blocks. The three
lines worth reading in the build output:

    client marker records added for 29 hull(s) the dataset had none for
    client hardpoint overlay: 952 port(s) moved onto CIG positions
    disclosure CSS: shared from _disc.css into ... loadout.html ...

A zero or a missing loadout.html in any of those means the build is not seeing a
file, and that is worth catching before the upload.

— C1
