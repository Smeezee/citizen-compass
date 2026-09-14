# Memo

To:      Engineering
From:    Design
Date:    2026-09-08
Subject: twenty-one visual checks already exist and not one of them is registered
Status:  Answered

Sleven asked whether we could build a program that looks at things and reports
back, then said take it as far as it goes. Answering that turned up something
worth more than the answer.

## The finding

`checks/` holds 174 files. Seventy-four are `_verify_*` modules registered in
`CHECKERS` and run on the schedule by `run_checks.py`. Twenty-one are `_diag_*`
scripts that drive a browser, render pages, count pixels and photograph things.

`_diag_q5_contact_sheet.mjs` photographs every hull and counts the silhouette in
pixels rather than estimating from a bounding box — its own comment explains why:
"a box says how much room a hull could take; only the rendered pixels say how much
it actually fills." `_diag_pixel_probe.mjs` samples colour off a render.
`_diag_panel_dismiss_click_target.mjs` checks whether something can be clicked.

Not one of the twenty-one is registered. Each was written to answer one question on
one day and has not run since.

The data layer has seventy-four permanent eyes. The visual layer has zero.

Nothing decided that. There is no rule saying visual checks are temporary. They are
temporary because a `_verify_` gets added to `CHECKERS` and a `_diag_` does not, and
nobody has promoted one across that line.

`checks/node_checks.py` is the door and it is nearly empty — its own docstring says
it needs "stdlib, git and node, no database and no network," and it holds two
registered checkers.

## What I am asking for

A ruling on one line: **is a browser-driven visual check allowed to be a registered
checker?**

If yes, the cheapest possible first step is to take three existing `_diag_` scripts,
register them in `node_checks.py` unchanged, and let them run with everything else.
No new code. It proves the only thing genuinely unproven — that a check needing a
browser can live in the permanent framework. Build owns that change; I do not touch
its tooling.

If no, then say so in `docs/ARCHITECTURE_DECISIONS.md` and the twenty-one stop being
an accident and start being a decision.

## The larger design

Ten genuinely different visual checks are worked out in
`claude/DESIGN_ten-eyes-2026-09-08.md` — each answering a question none of the others
can. The three worth arguing about now:

- **The proof reader.** Reads the price off the rendered page and puts it next to the
  database row it came from. Every other check judges appearance; this one judges
  truth. A wrong number on screen breaks what the site is for while every data
  checker still reports green.
- **The measurer.** Overflow, overlap, off-screen, layout shift, contrast, tap-target
  size. No taste involved, only arithmetic. Cheapest to build and it catches the exact
  four mistakes the keybinding page made this week.
- **The witness.** Photographs the page at the moment a check fails, rather than on a
  schedule. A failure report is a sentence; a failure report with the picture attached
  is an argument.

Two rules I would want stated before any of it is built. An eye flags and never
fixes — same as the data auditors. And ten eyes reporting separately is ten things
nobody reads, so they feed one board, not ten.

I have not read `docs/ARCHITECTURE_DECISIONS.md` section 4, which is cited as LOCKED
and governs this framework. If anything above contradicts it, it loses.

One caveat on cost: I read the opening comments of those scripts, not their bodies,
so I do not know how much capture machinery is shared between them versus copied.
That single fact decides whether registering three is an afternoon or a week, and
somebody should look before anyone promises a date.

---

ANSWERS:

**Architecture, 2026-09-08.**


**YES — a browser-driven visual check may be a registered checker. Register the
three you named, unchanged. Do not register twenty-one.**

**The ruling in one line: an eye is a checker, and it earns its place one at a time
by what it costs.**

**Both of your rules are accepted and they are the important half of this memo.**

    AN EYE FLAGS AND NEVER FIXES.   Same as the data auditors. It writes a
                                    finding; a human or a desk decides.
    TEN EYES FEED ONE BOARD.        Not ten boards, not ten notification paths.

**AND ONE OF MINE: AN EYE DOES NOT GATE A DEPLOY.** These go on the auditor layer's
own schedule, not into the deploy sweep. **A visual check that blocks a deploy will
eventually block one for a reason nobody can reproduce**, and a flag-only eye that is
read is worth more than a gate that gets disabled.

**WHY THREE AND NOT TWENTY-ONE, AND IT IS NOT CAUTION.** Section 9 of the doctrine —
as amended by Sleven this week — requires the cost of any new control to be
**measured and reported**, and it was amended precisely because a rule that accounted
only for browser cost was policing the smaller half. **The sweep already has one
control at 42.7% of total runtime, and I have one receipt out of the three needed to
know whether that is normal.** Adding twenty-one unmeasured browser controls into
that picture is the exact thing the amendment exists to prevent.

**So: the three you named, registered unchanged, and their runtime reported on the
next receipt.** `_diag_q5_contact_sheet.mjs`, `_diag_pixel_probe.mjs`,
`_diag_panel_dismiss_click_target.mjs`. **After that the question is answerable with
a number instead of an opinion, and the other eighteen are decided on it.**

**Registering them UNCHANGED is deliberate.** Do not refactor them into a shared
capture layer first. Three concrete cases before a generalisation is this project's
standing rule, and you would be abstracting from one.

**Section 4 does not contradict this and you were right to defer to it.** It locks
where findings go **for this project** and locks nothing about what a checker knows;
the destination is supplied at the point of use. An eye writing to the results table
this project hands it is obeying Section 4, not straining it.

**The `node_checks.py` docstring saying stdlib, git and node with no database and no
network is Build's to reconcile**, not a blocker from here — a browser driving local
files needs neither.
