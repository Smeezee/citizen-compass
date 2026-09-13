To:      Build
From:    Architecture
Date:    2026-09-09
Subject: build order — the card mark, three states derived at build time, and the one control without which it rots silently
Status:  Open

**Sleven has ruled and the doctrine carries it.** `docs/UX_DOCTRINE.md` Section 21,
dated 2026-09-09. This is the build order.

**Not urgent against the sweep being red or Job B.** Take it when those are clear.

## THE STATES — THREE, NOT TWO

    NEVER CHECKED        last_verified_patch IS NULL
    CHECKED, CURRENT     last_verified_patch == the patch the game is on
    CHECKED, OVERTAKEN   last_verified_patch is behind the patch the game is on

## THE LABELS

    Awaiting check          never checked against anything
    Checked · 4.10          checked, and 4.10 is what the game is on
    Needs re-check · 4.9    checked, and the game has moved past it

**The third label is with Sleven and may change.** Build the mechanism; the string
is one constant. **Nothing is blocked on it** — no row can currently reach either
verified state, so only the first label can appear today.

## THE CHIP — IDENTICAL IN EVERY STATE. HIS RULING.

Same colour, same weight, same position. **No tint, no caution colour, no icon, on
any state including the verified one.** The only thing that changes is the word.

The reason is in the doctrine and it is not a style preference: a visually distinct
chip where a badge sits is the shape a reader skips, worse on a phone. **Do not add
a colour later because a state "feels like" it wants one.**

Same visual weight as the role line. Doctrine Section 39 Level A if nothing moves,
Level B the moment layout does. **The card's fixed height is a ruling and stands.**

## DERIVED, NEVER STORED — THIS IS THE WHOLE DESIGN

Computed where the page is built, from the row's `last_verified_patch` against
**one** current-patch value.

**No per-row state column. No migration on patch day.** When 4.11 ships, every
`Checked · 4.10` becomes `Needs re-check · 4.10` on the next build, by itself.

**A visitor must never have to know which patch is current to read the card
correctly.** That is the requirement the labels are shaped around — the comparison
happens in your build, not in their head.

## THE CONTROL, AND IT IS NOT OPTIONAL

**Every label depends on one value: which patch the game is on.**

**If that value is typed by hand and missed on patch day, every verified card goes
on saying `Checked` about a patch the game has left** — and the mark built to
prevent stale data becomes the thing asserting it. Silently, and on the cards most
likely to be trusted.

**So: the current-patch value is read from a source, and a control asserts it is
current.** Hard rule 12 — without it nothing about this mark can ever fail, and a
mark that cannot be wrong is decoration.

**Two things I am not deciding for you**, because you can see the ground and I
cannot: where the value is read from, and how the control proves itself. **Say what
you pick and why.** If the only honest source is Sleven telling us, then the control
asserts how old the value is rather than whether it is right, and it says so.

## DONE-WHEN

Every card carries its mark, derived rather than stored; the three states render
from real data with no state column; the chip is identical in all three; the
current-patch control exists and has been made to fail on purpose; and the card
height is unchanged.

**Prove the patch-boundary case before you call it done.** Set the current-patch
value forward by one and confirm a verified card flips to the third state with no
data edited. That is the whole point of the design and it is the one thing that
would be easy to build and never test.

## WHAT DOES NOT COME WITH THIS

**No row is verified.** All 254 carry no `last_verified_patch`, so this ships
showing `Awaiting check` everywhere. That is the honest picture, not a defect — and
filling that field is Q61, which is a different job.

**Nothing carries `Checked` until the check behind it is real and can be re-run.**
Sleven's condition, and it means a verified state cannot be faked into existence for
testing on live data.
