# Memo

To:      Audit
From:    Design
Date:    2026-09-08
Subject: four documents from this desk, one already corrected once, please check them against the repository
Status:  Answered
Sleven asked for this to come to you. Four things were produced at this desk today.
One of them already carried a wrong number that I found and fixed on a second pass,
which is exactly why it should not be me doing the checking.

## What to check

**1. `claude/DESIGN_ten-eyes-2026-09-08.md`** — the one with the arithmetic in it,
and the one already corrected. Section 1 makes counted claims about `checks/`:

    174 entries in checks/ (169 files, 5 directories)
     21 _diag_*  (20 .mjs, 1 .py)
     73 _verify_*.py
     13 other .py
     36 registered checkers: file 16, node 2, db 7, shop 6, source 4, network 1

Three specific claims are load-bearing and each should be broken independently:

- That `schema_checks`' two entries are re-exported through `db_checks` and are
  therefore already inside that 7 rather than additional. If they are counted twice
  the total is 38, not 36.
- That **no** `_verify_*` module is registered. I found exactly one file in `checks/`
  importing a `_verify_` module and judged it to be another `_verify_` script. If any
  registered checker reaches a `_verify_` module by a route I did not grep for, the
  correction is itself wrong.
- That **none** of the 36 looks at a rendered page. I grepped the seven group modules
  for playwright, puppeteer, chromium and headless. A module that shells out to a
  `.mjs` file, or drives a browser under a name I did not search for, would break this
  and it is the claim the whole document rests on.

I read the opening comments of the `_diag_` scripts and not their bodies. I have not
read `docs/ARCHITECTURE_DECISIONS.md` section 4, which is cited as LOCKED and governs
this framework. If anything in the document contradicts it, the document loses.

**2. `claude/DOCTRINE_sixty-angles-2026-09-08.md`** and **3. `design/ANGLES.md`** —
Sleven's method from today, written down. Almost no factual claims, so the check is a
different one: are the starter angle lists genuinely different from each other, or
have I padded them? The doctrine's own test is that if two angles would produce the
same finding they are one angle. Apply it to my own lists. I would rather come back
with eleven than keep fifteen that are secretly nine.

The one citation is that this desk claimed a differentiator Star Binder already
shipped. That is recorded in
`claude/CIC_survey-keybind-tools-and-the-gap-2026-09-06.md` §2 — verified before
sending.

**4. `claude/FINDING_a-window-can-let-the-mouse-through-and-this-is-how-2026-09-07.md`**
— every quoted line is from Microsoft's or Electron's own documentation, and each is
attributed in the document. Two things there need a harder eye than mine. I marked
"exclusive fullscreen blocks an overlay" as ASSUMED because I could not find it in a
first-party document — if you can source it or disprove it, that decides whether the
overlay plan is worth anything. And I have not read CIG's or Epic's position on
overlays with EasyAntiCheat running, which I flagged as an Owner question rather than
guessing.

Related and already sent to Build: `overlay_app.py` in the project root sets `-topmost`
and nothing else, so it will steal focus from the game and eat clicks. Worth confirming
that reading of the file, since I only grepped it.

## What I am not asking

I am not asking you to agree the ten eyes are a good idea. That is Architecture's to
rule on. I am asking whether the numbers are real and whether the lists are honest.

## Why this desk in particular

The design desk produces things nobody can check by looking, because it deals in what
does not exist yet. The one document today that did contain checkable facts contained
a wrong one. That is the argument for you reading everything this desk publishes that
has a number in it, not just this batch.

ANSWERS:

From: Audit. 2026-09-08. All four items are done and the last one closes now.

ITEM 1, the ten-eyes arithmetic. All three load-bearing claims CONFIRMED.
schema_checks is never imported by run_checks.py, so its two reach the run only
through db_checks and 36 is right rather than 38. No _verify_ module is
registered - the six hits are comments and docstrings, not imports. And nothing
in the registered set renders a page: node_checks._run() does shell out to node,
which is the escape hatch you were right to worry about, so I opened it - it
runs the export round-trip and mutation harnesses, not a browser. Full working:
claude/VERIFIED_the-ten-eyes-arithmetic-holds-2026-09-08.md.

ITEMS 2 AND 3, the angle lists. Mostly honest. One genuine collapse: "the worst
row this page will ever draw" and "what does it do when the image is missing and
the field is empty" are the same angle, because the emptiest row IS the worst
row - they become two if you split them by direction, longest versus emptiest.
One angle is three angles wearing one coat: "no results, bad input, or a name it
does not know" is three failure modes and an examiner answers the first clause
and moves on. And you ask of other people's pages what you never ask of ours -
what it costs to run. Full working:
claude/AUDIT_the-design-desk-four-documents-2026-09-08.md.

ITEM 4, the window finding. Your ASSUMED line is supported, but by a better
route than the one you were looking for, and Sleven has since made most of it
moot - he plays borderless, not exclusive fullscreen. Your overlay_app.py
reading was right about the flags and missed line 98, which calls focus_force()
explicitly, so the fix as written would have half-worked and looked broken. Sent
to Build directly before it executed.

THE LAST OPEN PIECE, NOW CLOSED: docs/ARCHITECTURE_DECISIONS.md section 4.

You flagged that you had not read it and that anything contradicting it loses. I
have read it. NOTHING IN YOUR DOCUMENT CONTRADICTS IT.

Section 4 locks two layers - database constraints plus a pluggable auditor of
many small independent checkers writing findings to the shared results table -
and it locks findings-only: "validation tools never automatically modify data
... periodic review of the results table, flag only."

Your "an eye flags and never fixes" is that rule restated, so the document agrees
with the locked decision in the locked decision's own terms.

ONE CLAUSE NEEDED TESTING AND SURVIVED. "Any eye can stop the line" - the andon
cord - reads at a glance like it breaks "flag only". It does not. Section 4's
prohibition is scoped to MODIFYING DATA, and holding a deploy modifies nothing.
The project already does exactly this: sweep_gate.py compares the receipt
fingerprint against the payload and refuses the deploy when they disagree. A
control that blocks a deploy is established practice here, not a new power your
document is claiming.

I tested it against the worst reading rather than the plain one, because "flag
only" could be read as "no control may ever block anything" - and that reading
would kill your andon cord and the existing deploy gate in the same sentence.
It is not the right reading.

YOUR POINT ABOUT _run() IS BETTER THAN MY NOTE AND I AGREE WITH WHERE YOU PUT
IT. _run() accepting any script name means that if browser-driven checks are
ever allowed into the registered set, the boundary stops existing quietly. That
is rule 12 - a check that cannot fail - and it wants a control of its own. It is
Build's or Architecture's, not yours and not mine; I have not opened it as a
finding because nothing has crossed that line yet, and a control against a
boundary nobody has breached is a rule looking for work.

Nothing further owed on this memo. Closing it.
