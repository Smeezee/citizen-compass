# Memo

To:      Architecture
From:    Owner (Sleven), filed by C1
Date:    2026-09-06
Status:  Answered
Subject: OWNER RULING — there is no consent on the collector, and that is deliberate. Closes the whole consent thread.

## The ruling, in his words

*"There doesn't need to be any consent on the collector right now. at all because
the collector is gonna be rebuilt on only my computer. Once I finish building it,
then we will reevaluate all the consent it needs and figure out how to properly do
it before it's ever shipped to anybody."*

## What that closes

Both options put to him were wrong, and so was the question.

    trim the wording      moot
    raise the 2,600       moot

The 2,838-character text, the assertion at `consent_selftest.go:225` and
`consentVersion = 4` **retire with the old program.** They are not fixed, not
trimmed, not raised. The collector is a full rebuild on his machine alone, and a
program that reaches nobody has nobody to obtain consent from.

Build's measurement stands and was not wasted — it is why nobody quietly raised
the limit and shipped an unreadable tail. It is the reason this ends in a ruling
instead of a one-line patch.

## What it opens, and C1 holds this

**A program with no consent is correct on one machine and defective the moment
anything leaves it.** "We will figure it out before it ships" is an intention, and
an intention cannot fail — rule 12's exact shape.

**A possible mechanism, offered and NOT decided:** the build refuses to produce a
distributable artifact — installer, signed binary, public download — while consent
is unresolved, as a build failure rather than a warning.

**Correction, same day.** C1 first filed that as a requirement on the rebuild.
Sleven corrected it: *"Don't rule anything as set in stone. The collector's
rebuild is still being designed."* It is a suggestion for him to accept or reject
when the design is further along. The ruling on consent stands; the mechanism
around it does not exist yet.

## Also closed by this

Item 2 of `2026-08-30_two-things-only-you-can-decide.md` — the twelve CRLF files —
**was already done before it was asked about.** Commit `87b8ae9`, exactly twelve
files, 1,102 insertions against 1,102 deletions. Verified from the repository's
own history. Sleven was sitting on a request to approve finished work for a week
because nothing in the mail system required anyone to open it. **Rule 24 exists
because of this class of failure; this is an instance of it, not a one-off.**

## Recorded in

    docs/CURRENT-STATE.md                                    the rebuild section
    docs/DESIGN_the-fact-store-is-mostly-already-built-...   §7, now marked RULED

---

ANSWERS: Sleven, 2026-09-06.

The ruling above is itself the answer to every memo in the consent thread. Three
memos were moved to answered/ alongside it. **Nothing in this thread is open.**
The one thing C1 raised on top of it — a build refusal while consent is
unresolved — is a suggestion Sleven has not accepted, recorded in
`docs/DESIGN_the-fact-store-is-mostly-already-built-2026-09-06.md` as open design,
not as a requirement.
