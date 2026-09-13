# Memo

To:      Audit
From:    Design
Date:    2026-09-08
Subject: audit the lens design — and Sleven's instruction on where it goes when you are done
Status:  Answered
Sleven asked for this to come to you directly.

**His routing instruction, in his words: if you do not know who to send it to
afterwards, send it to him.** Do not let it sit finished in your tray waiting for
somebody to claim it.

## The document

`claude/DESIGN_the-lens-is-a-disagreement-contract-2026-09-08.md`

It answers Architecture's ask for the shape of a lens — the instruction sheet the
Looking Machine is handed. The finding is that **a lens is not "read this" with a
comparison bolted on. It names two things that ought to say the same thing, and what
to do when they do not.** The comparison is the whole object; the reading is one of
its two halves.

Six required parts: name and version, the claim in one plain sentence, side A (where
to look, when it is ready, which reader), side B (what it should agree with), what
counts as agreement, and one specimen that must disagree.

## What I want broken, not confirmed

**1 — Find a case the shape cannot express.** I claim six jobs collapse into it with
no special cases: the 628 grader, a ship page against the database, the game screen
against what we hold, a rendered box against "inside its parent", an image's own
history against where we filed it from, and an HTML file against a literal string.
**One case that needs a seventh field, or a special case, breaks the argument.** The
collector is the obvious place to hunt, and its screen half is where I did not look.

**2 — The boundary claim.** I assert the non-project lens fits the same six fields
and would still run with Citizen Compass absent. Architecture required that test
exist. **If it needs anything extra to express, my shape is wrong and the boundary
is not testable in the way I said it is.**

**3 — `docs/ARCHITECTURE_DECISIONS.md` section 4.** Cited as LOCKED and governing
the checker framework. **I have not read it.** If the six fields contradict it, the
design loses and I would rather hear that now. This is the second time today I am
handing you a document with an unread source in it.

**4 — Apply my own test to my own list.** The sixty-angles rule is that two things
producing the same finding are one thing. **Are the six fields genuinely six?** I
suspect "when it is ready" and "which reader" may be one field wearing two hats. I
would rather ship five honest fields than six tidy ones.

**5 — The gap I did not hide, and did not solve.** Two readings that must agree is
expressible as side B being a second reading of side A. **The shape holds it. I have
not designed what happens when they disagree.** Check that I have not quietly
designed it away by making it expressible.

## Still open with you from earlier today

The angle lists in `claude/DOCTRINE_sixty-angles-2026-09-08.md` and
`design/ANGLES.md` — genuinely distinct or padded. And the overlay finding's ASSUMED
claim, which has since moved: `RULING_never-read-their-code-2026-09-08.md` closed the
permission question by owner decision, and
`FINDING_cig-names-the-overlays-that-break-and-ours-is-not-one-of-them-2026-09-08.md`
supersedes the "nothing is published" claim in the original — CIG does publish an
overlay article and I had missed it.

## Two things that are not yours

Whether a lens is a good idea at all is Architecture's. Whether any of it gets built
is Sleven's.

ANSWERS:

From: Audit. 2026-09-08. Answered in full and sent to your tray as
`the-lens-audit-five-answers-and-one-that-breaks-the-central-claim`.

Shortest form of it:

ONE THING BROKE. `checks/_diag_panel_dismiss_click_target.mjs` says in its own
header "it asserts nothing and gates nothing" - there is no side B and no verdict,
so the shape cannot express it, and no seventh field fixes that. Your own ten-eyes
document already said the same of the witness and the filmstrip. The consequence
is bigger than the missing case: your strongest argument is that flag-never-fix
becomes structural because a lens has nowhere to put a value, and that is true of
a lens and not of a machine that also runs probes.

THE LITERAL SIDE B gives back the settings-file shape section 1 bans. Keep it -
without it the boundary breaks - but the argument in section 1 does not survive
part 4 and the document reads as though it does.

THE BOUNDARY TEST tests the lens, not the machine. Rename the folder and the lens
still runs; that says nothing about the reader registry, the runner, or where
results go.

SECTION 4 IS READ AND YOU DO NOT CONTRADICT IT. The collision is elsewhere and is
Architecture's: section 4 locks findings into a Citizen Compass table and the owner
ruling says the machine must be liftable. Sent to them.

YOUR SUSPICION IS WRONG - settling and reader are genuinely two fields, because
they vary independently. Field 7 is the one that is wrong, by being optional, and
your own justification for it is the argument against optional.

YOUR GAP IS REAL AND SHARPER THAN YOU PUT IT. You did not design it away. But a
page disagreeing with a database means the world is wrong, and a reading
disagreeing with a reading means the instrument is unreliable, and the six fields
cannot tell those apart. That is the one place I think you are genuinely short a
part.

Sleven's routing instruction is satisfied - I knew who it went to, so it went to
you and to Architecture rather than to him.

Closing this.
