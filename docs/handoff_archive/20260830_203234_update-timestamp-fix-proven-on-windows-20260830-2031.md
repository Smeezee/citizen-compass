# Update — the sweep is green and C1's timestamp fix is proven on Windows

## Sweep: 113 ok, 0 failed, 0 NOT RUN, 3 skipped, 1110s

C1 labelled `_verify_drydock_scale.mjs` **UNPROVEN**, found two more of their own
unlabelled controls, and made `_verify_wall.mjs` genuinely independent. Gate says
**113 controls green against this exact payload**. The 3 skipped are the
deployed-site trio, which cannot run until a deploy.

**The payload is vouched for and deployable. I have NOT deployed** — that is one
of the four things that stop for Sleven, and the glossary would ship inert.

## C1's timestamp fix — built and PROVEN on the machine it runs on

They fixed it on Linux and said plainly: *"proven on Linux and unproven on the
machine it actually runs on."* Now proven.

    go build clean · go vet clean · --self-test exits 9, 49 printed of 50 sites
    all four new assertions green, including the one that matters:
    "a source with NO timestamp does not borrow the reader's clock"

**Archive run: all 633 observations carry `occurred`, and the dates are real** —
spread across twenty-nine months rather than all claiming the same few seconds:

    2024-03 21 · 2025-11 24 · 2026-01 166 · 2026-02 154 · 2026-06 97 · 2026-08 10

    at       = 2026-08-31T01:29:07Z      when we read it
    occurred = 2025-11-23T23:52:28.451Z  when it happened

**And the part that actually cost something is closed:**

    facts carrying last_seen        251
    still stamped with the READ date  0

A January price and a June price are finally different on the field that
separates them.

## The defect was worse than I reported

I said "no timestamp pattern at all". **C1 found `reTS` was declared and wired to
nothing** — the pattern was written and then never used. That is worse in the way
that matters: reading the file would show a timestamp being handled. **Same shape
as the glossary's `/* layer absent: page still works */` guard**, and that is two
in one day: code that reads as if it does something and does nothing.

## A decision I took rather than deferred

C1 flagged that re-reading the archive was a decision, not a consequence. **I
took it, because the fix could not be proven on Windows without it** — a build
and a self-test prove the code, not that real logs yield real dates.

Measured rather than assumed:

    observations   1867 -> 2500
    a fact         3 occurrence(s), read 4 times     (was 3 and 3)

**Readings rose, occurrences did not.** The event ids held; the fourth reading
collapsed onto an existing occurrence, so confidence did not inflate. That was
the whole worry and it is answered with a number.

The 1,867 older rows still have no `occurred` and still fall back. Untouched.

## Also closed since the last update

**D11** — the memo router double-stamped filenames already carrying a date
(`2026-08-30_2026-08-31_...`, seen twice). One regex, two tests both directions,
mutation-proven with the literal original defect, deployed.

**D7** — the roadmap watcher silently discarded misspelled settings keys.

## Open

D1, D6 (not mine to action), D8, D10. Two decisions with Sleven: the consent text
(measured — the dialog clips about fifteen lines) and the twelve line-ending
files. C1 has not changed `GLOSS_ON_PARTS` yet, so the glossary is still inert.
