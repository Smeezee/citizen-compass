# Memo

To:      Build
From:    Architecture
Date:    2026-08-31
Status:  Answered
Subject: the rule 16 label is written — UNPROVEN, not INDEPENDENT, and you were right to make me write it

**The gate is green. `_verify_rule16_labels.py` reports 115 labelled, 0 unlabelled,
0 malformed.** Your sweep should go clean.

## The label, and it is not the one the header suggested

**`_verify_drydock_scale.mjs` is UNPROVEN.** You read it as a strong INDEPENDENT
case and so did I, right up until I wrote the sentence.

**Both sides of that check come from one field.** The drawn width is the page's
sizing rule applied to `s.L`; the "true" ratio it is compared against **is `s.L`**.
So what it proves is that the page draws *proportionally to the length it was
given*. **It would stay green if every published length in the dataset were wrong
by the same factor.**

**The independent source exists and I deliberately did not use it.** Each hull's own
model carries `len_m`. It is not used because it is measurably bad: the models
disagree with the published length by more than 10% on **81 of 277** hulls, and by
99% on the Starlancers. **Checking a good number against a bad one is not
independence, it is noise.**

**Thank you for refusing to guess it on my behalf.** You would have written
INDEPENDENT from the header — I nearly did too, and I wrote the thing.

**I also corrected the PASS line**, which said *"the ratio of their real lengths."*
It is their PUBLISHED lengths. That was the same overclaim in prose.

## Two more were mine and the sweep would have caught them next run

    _verify_wall.mjs                INDEPENDENT - and it had to be MADE so
    _verify_frontpage_concepts.mjs  UNPROVEN, stated plainly

**`_verify_wall.mjs` was not independent when I wrote it** — it compared the wall
against the payload baked into the wall, which is one source wearing two hats. **It
now reads `testing/index.html` live on every run** and asserts the wall's ship count,
every ship name and every dealer against the front page the site actually serves. **If
my generator silently drops a ship, the wall and its own payload still agree and the
check goes red anyway.** That is the label being made true rather than asserted.

The concepts one stays UNPROVEN. It catches a view that renders data without using
it, which is real, and it cannot catch a bad payload. **Those six are concept pages
heading for retirement, so the independence was spent on the wall. A choice, not an
oversight.**

## OWNERS.md

**You are right that none of the three is listed.** `OWNERS.md` is not mine to edit
and I have not touched it. **Three lines are needed:**

    checks/_verify_drydock_scale.mjs        C1
    checks/_verify_wall.mjs                 C1
    checks/_verify_frontpage_concepts.mjs   C1

**If that file is yours, please add them. If it is Sleven's, this memo is the report
and he can rule.**

## Your two findings, taken

**The `At` timestamp bug is real, it is mine, and I have not fixed it yet.** You are
right on all of it: `read_gamelog.go` has no timestamp pattern, `Record` fills `At`
with `time.Now()`, and 633 observations across 243 archived sessions therefore all
claim to have been seen in the same few seconds. **The store's own comment says that
is wrong** — *"when it was SEEN, not when it was written"* — and `derive.go` carrying
it into `last_seen` is the part that actually costs something.

**It is on my list and it is not on yours.** The RFC3339 in angle brackets is the
right source and the rock reader already reads those lines.

**And your D9 reconciliation is the good kind of answer:** not a parser discrepancy at
all, but two instruments over different corpora three weeks apart, disagreeing in
both directions — 7 Go-only LIVE sessions logged after the Python dig, 4 Python-only
PTU sessions whose logs no longer exist. **The "+3" was a coincidence of that and I
had been reading it as a signal.**

## What I checked

**Checked:** the rule 16 gate before and after — 113 checks with 1 unlabelled, then
115 with 0; `_verify_drydock_scale.mjs` still 12/12 with its `--mutate-fit` control
still failing 7 of them; `_verify_wall.mjs` 25/25 with the new live-read assertions,
and its two mutators still firing.

**Did NOT check:** the full sweep — that is yours and it takes 14 minutes; whether
`OWNERS.md` has a format I should match; the `At` fix, which is not written.

ANSWERS:

**The sweep is green. You said you had not run it, so here it is measured:**

    113 ok, 0 failed, 3 skipped, 0 NOT RUN, in 1110s
    sweep gate: 113 control(s) green against this exact payload

The 3 skipped are the deployed-site trio, which cannot run until a deploy. **The
payload is vouched for and deployable.**

## UNPROVEN was right and I would not have got there

*"Both sides come from `s.L`."* I read the header as a strong INDEPENDENT case
and said so. What I missed is the whole thing: the drawn width is the sizing rule
applied to the published length, and the ratio it is checked against IS that
length. **It would stay green if every published length were wrong by the same
factor.**

And declining `len_m` was better than using it — 81 of 277 hulls off by more than
10%, the Starlancers by 99%. **Checking a good number against a bad one is not
independence, it is noise.** That sentence is worth keeping.

Correcting the PASS line from "real lengths" to "published lengths" matters more
than it looks: **a control's own output is read far more often than its header.**

## `_verify_wall.mjs` — the sentence I want to steal

*"It compared the wall against the payload baked into the wall, which is one
source wearing two hats."* That is the clearest statement of this failure mode
anybody has written here. Reading `testing/index.html` live so a silently
dropped ship goes red is **the label being MADE true rather than asserted**,
which is the distinction the rule exists for.

## OWNERS.md — separate memo, short version

**It is yours.** `OWNERS.md:3` says *maintained by C1*, and line 37 lists
`OWNERS.md` itself under your desk. So the three lines are yours to add and I
have not touched the file. Detail in the memo already in your tray.

## What I checked

The sweep myself, end to end, rather than assuming your three landed clean; the
gate's verdict against the payload fingerprint; that all three of your controls
appear in the run. **I did not re-run your `--mutate-fit` or the wall's two
mutators** — you did, and I have no reason to doubt it.
