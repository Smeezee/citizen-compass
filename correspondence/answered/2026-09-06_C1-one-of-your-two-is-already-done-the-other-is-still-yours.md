# Memo

To:      Owner
From:    C1 (Architecture)
Date:    2026-09-06
Subject: the memo from 30 August put two things in your tray. One is already done. The other is one word, and Build's measurement changed which word.
Status:  Answered

**That memo has sat for a week. It should not have, and the fault is the mail, not
you: nothing in the system made anyone open it. Rule 24 exists now for that reason.**

---

## Item 2 — the twelve files. DONE. Nothing needed from you.

Commit `87b8ae9`, *"Twelve files stop looking modified: CRLF leaves the index,
nothing else moves."* Exactly twelve files, 1,102 insertions against 1,102
deletions — the signature of a pure line-ending change and nothing else.

**Verified from the repository's own history, not from a memo saying so.** Item 2
is closed. You were asked for a go-ahead on something that had already been done.

## Item 1 — the consent text. Still yours, and one option is now unsafe.

You were offered two one-line fixes: trim the wording, or move the 2,600 limit.

**Build measured before you chose, and the measurement kills one of them.**

    consent text     2,838 characters, 67 lines
    rendered height  1,206 px
    your screen      1,032 px of usable height

The text alone is 174 px taller than your screen **before** a title bar or a
button row exists. Count zero pixels for the window furniture and it still does
not fit.

**A Windows message box has no scrollbar. It never has.** Text past the bottom is
drawn off the screen and cannot be reached — no keyboard, no mouse, no resize.

So roughly the last fifteen lines of the consent text **cannot be read by the
person agreeing to it.**

That changes what the two options mean:

    trim the wording    fixes the failing test AND the unreadable tail
    move the limit      fixes the test only. People keep agreeing to text they
                        cannot see, and it deletes the one signal that caught it.

**The 2,600 was not an arbitrary round number.** It was protecting readability and
it did its job.

C1 re-measured the character count independently on 2026-09-06 and confirms 2,838
against the assertion at `consent_selftest.go:225`, `consentVersion = 4`.

## What nobody will do without you

**Nobody touches consent wording but you.** Not C1, not Code, not Research. If you
want a trim drafted for you to approve or reject line by line, say so and one gets
drafted — and nothing goes in until you approve the words.

There is a third path worth naming so you are choosing from all of them: **stop
using a message box.** A real window with a scroll region would hold any length of
text and the limit could go away honestly rather than by being raised. That is a
bigger job than one line and it is only worth it if the wording is going to grow
again.

## What C1 checked and what C1 did not

**Checked:** commit `87b8ae9`'s file list and diff shape; the consent literal's
length; the assertion and the version constant.

**Did NOT check:** whether the 2,838-character text is still the wording you
approved. If it has drifted from what you signed off, that is a different and
larger problem than either fix.

    1. Trim the wording, or replace the message box?
    2. Do you want a trim drafted for you to rule on?

---

ANSWERS: Sleven, 2026-09-06, in his own words.

*"There doesn't need to be any consent on the collector right now. at all because
the collector is gonna be rebuilt on only my computer. Once I finish building it,
then we will reevaluate all the consent it needs and figure out how to properly
do it before it's ever shipped to anybody."*

Both options in the tray are moot. The consent text, its 2,600 assertion and
`consentVersion = 4` retire with the old program. Item 2 was already done before
it was asked about — commit `87b8ae9`.
