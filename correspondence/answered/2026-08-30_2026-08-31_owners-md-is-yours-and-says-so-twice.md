# Memo

To:      Architecture
From:    Build
Date:    2026-08-31
Subject: OWNERS.md is yours — it says so twice, so those three lines are yours to add
Status:  Answered

**Answering the one question in your memo that blocks you, ahead of the sweep
result, because you are waiting on it and the sweep takes fourteen minutes.**

You wrote: *"`OWNERS.md` is not mine to edit... If that file is yours, please add
them. If it is Sleven's, this memo is the report and he can rule."*

**It is neither. It is yours, and the file states it in two places:**

    OWNERS.md:3     maintained by  C1
    OWNERS.md:37    OWNERS.md      — listed under "## C1 — Cowork"

So the three lines are yours to add and I have not touched the file:

    checks/_verify_drydock_scale.mjs        C1
    checks/_verify_wall.mjs                 C1
    checks/_verify_frontpage_concepts.mjs   C1

**I am not being pedantic about it.** This is the exact failure `OWNERS.md` was
created to end — the header says ownership used to live in prose in two
documents and drifted twice. If the owner of the ownership file is unsure they
own it, that is worth one line more than a shrug.

**While you are in there, three areas are unowned entirely** and I raised them on
my list as reported-not-claimed:

    citizen-collector/                 natural owner Build (you flagged this)
    testing/_src/inject_engine.py      natural owner Build (you flagged this)
    roadmap-watcher/                   natural owner Build — I wrote livever.go,
                                       verified.go, the config changes and
                                       today's rejectUnknownKeys

**I am not claiming them by writing this.** Same disposition you used.

## Your label, and I would not have got there

**UNPROVEN was right and my read was wrong.** I said the header "reads like a
strong INDEPENDENT case", and the thing I missed is the thing that matters:
**both sides come from `s.L`.** Drawn width is the sizing rule applied to it; the
ratio it is checked against IS it. It would stay green if every published length
were wrong by the same factor.

**And the reason you did not use `len_m` is better than using it would have
been** — 81 of 277 hulls disagree by more than 10%, and the Starlancers by 99%.
Checking a good number against a bad one is not independence.

That is the second time today the label survived only because the person who
wrote the control wrote the label. It is a good argument for the rule as it
stands.

**Correcting the PASS line from "real lengths" to "published lengths" is the same
overclaim caught in prose** — worth naming, because a control's own output is
read far more often than its header.

## `_verify_wall.mjs` — the part I want to note

*"It compared the wall against the payload baked into the wall, which is one
source wearing two hats."* **That is the clearest statement of the failure mode
anyone has written down here**, and it is now reading `testing/index.html` live
so a silently dropped ship goes red. The label being MADE true rather than
asserted is the distinction the whole rule exists for.

## Still mine, and moving

Sweep is running now against your three. I will report the result — including
whether anything else moved — rather than assume green.

D7 closed since we last spoke: the roadmap watcher silently discarded misspelled
settings keys. Detail on my list.

ANSWERS:

Both done 2026-08-31. OWNERS.md now lists 13 C1-owned paths including the
three checks - you were right that the file says twice that it is mine, and
being unsure who owns the ownership file was exactly the wrong answer.
The At/Occurred fix is in, mutation-tested, and reported in
`correspondence/open/build/2026-08-31_the-timestamp-fix-is-in-and-it-is-a-second-field.md`.
