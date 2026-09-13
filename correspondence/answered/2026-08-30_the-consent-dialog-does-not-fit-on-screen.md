# Memo

To:      Owner
From:    Build
Date:    2026-08-30
Status:  Answered
Subject: the consent dialog does not fit on this screen — "move the limit" is the wrong half of that choice

**Architecture put two options in your tray: trim the wording, or move the 2,600
limit. I measured before you decide, and one of them is unsafe.**

## The measurement

    consent text     2,838 characters, 67 lines, longest line 75 chars
    assertion        consent_selftest.go:225  len(text) <= 2600
    rendered in      MessageBoxW (user32), Segoe UI 9pt, 18 px per line
    text height      1,206 px
    screen workarea  1,032 px on this machine (1920 x 1080)

**The text alone is 174 px taller than the screen, before a title bar or a
button row exists.** With chrome it is roughly 1,316 px against 1,032 — over by
~284 px, about fifteen lines.

**The conclusion does not depend on my chrome estimate.** Count zero pixels for
the window furniture and it still does not fit.

## Why that matters more than a failing assertion

**A Windows message box has no scrollbar.** It is not a scrolling control and
never has been. Text that exceeds the screen is drawn off the bottom and cannot
be reached — no keyboard, no mouse, no resize.

So the last ~15 lines of the consent text are, on this machine, **not readable by
the person agreeing to it.**

That changes the shape of your decision:

    trim the wording      fixes the assertion AND the unreadable tail
    move the limit        fixes the assertion ONLY, and leaves people agreeing
                          to text they cannot see. It would also delete the one
                          signal that caught this.

**The 2,600 was protecting something real.** It reads like an arbitrary round
number and it is not.

## What I am NOT doing

**I have not touched the wording and will not.** It is yours by rule, and this
memo exists to inform the choice, not to make it.

I have also not drafted a trim. If you want one, say so and I will propose cuts
for you to approve or reject — but nothing goes in without you approving the
words.

## What I checked and what I did not

**Checked:** the length and line count straight out of `consent.go`'s
`consentText` literal, not taken from Architecture's memo; the display path is
`modUser32.NewProc("MessageBoxW")` at `consent.go:228`; text metrics measured
with `SystemFonts.MessageBoxFont` against this machine's working area; longest
line 439 px, so the box does no wrapping and the 67 lines are 67 rendered rows.

**Did NOT check:** the exact chrome height — it is an estimate, and the finding
survives without it. **I did not render the dialog**, because doing so would put
a modal box on your screen. If you want it confirmed visually rather than by
measurement, that is one command and your call.

**Also worth knowing:** this is measured on a 1920x1080 display. On a laptop it
is worse. On a taller screen it may fit, which means the defect is invisible to
whoever happens to have the bigger monitor.

---
ANSWERS: C1, 2026-09-06, carrying Sleven's ruling.

**Neither option was the answer, and your measurement is why.** Sleven ruled:
*"There doesn't need to be any consent on the collector right now. at all because
the collector is gonna be rebuilt on only my computer. Once I finish building it,
then we will reevaluate all the consent it needs and figure out how to properly
do it before it's ever shipped to anybody."*

So the 2,838-character text, the 2,600 assertion and `consentVersion = 4` retire
with the old program rather than being trimmed or raised.

**Your work was not wasted — it is the reason nobody quietly raised the limit and
shipped an unreadable tail.** A message box has no scrollbar and roughly fifteen
lines were unreachable. That measurement turned a one-line patch into a ruling.
