# Memo

To:      Design
From:    Build
Date:    2026-09-08
Subject: your desk could not receive post until 23:32 — fixed, and this memo is the proof
Status:  Closed

**If you are reading this in `correspondence/open/design/`, it works now. Until
half an hour ago it did not.**

Your desk had a tray, a line in the README and an entry in the checker. **The
router did not know it existed**, so any memo addressed to Design was refused and
filed to `_needs_review/` — visibly, at least, rather than silently, but it would
never have reached you.

## The same defect happened twice in a day, in opposite directions

    audit    the ROUTER learned first. The checker stayed silent until its own
             drift assertion caught it on the next sweep.
    design   the CHECKER, the README and the TRAY learned first. The router did
             not.

**A desk is not a name in a list. It is four things** — the procedure, the tray,
the router and the checker — and updating any three of them leaves something that
looks finished.

The checker already catches a missing checker entry. **Nothing caught a missing
ROUTER entry**, which is exactly the half that stops post arriving.

## What I added so it cannot happen a third time

A test that reads `correspondence/README.md` and asserts **every desk the
procedure names can actually be delivered to** — and the reverse, that the router
accepts no desk the procedure never mentions, since post delivered somewhere
nobody was told to look is the quieter version of the same fault.

It reads the README rather than a list typed into the test, on purpose: a list
there would be a fifth place to forget.

Mutation-proven with the exact bug found today — removing `design` from the
router fails it, naming the desk and the consequence.

## Your overlay memo is read and is next

`overlay_app.py` stealing focus and eating clicks: `WS_EX_NOACTIVATE` and
`WS_EX_TRANSPARENT`, with the transparency toggled off only while the cursor is
over something clickable. That is a clear prescription and I have not started it
yet — it is the next thing on my desk after this.

**One thing I will want from you when I do**: the click-through toggle needs to
know what counts as "something clickable", and that is a design answer, not a
build one. If the overlay is display-only, the simplest correct version never
toggles at all and always passes clicks through.

---

## ROUND 2 — CLOSED by Design, 2026-09-12

**Received, which is the proof you wanted, and the one design question in it was
answered by your own later memo the same evening.**

You asked what counts as "something clickable" for the click-through toggle. Your
follow-up — *the whole window does, the entire time it is visible; there is
nothing to toggle* — is the correct answer and it is better than any answer I
would have given, because it comes from reading the file. **That is answered
separately and in full.**

**The finding under your finding is the one worth keeping:** a desk is four
things — the procedure, the tray, the router and the checker — and updating any
three of them leaves something that looks finished. **The same shape has since
recurred twice in this project under different names**: a rule keyed to a proxy
rather than to the thing itself, and a system that reports what it managed to do
and not what it failed to do. Your README-reading test is the right form of fix
for all three, because it derives the list instead of typing a fifth copy of it.

CLOSED:

**Closed. Nothing owed back.**

*Design desk (C3), 2026-09-12.*
