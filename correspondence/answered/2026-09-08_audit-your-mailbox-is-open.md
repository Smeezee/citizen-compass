# Memo

To:      Audit
From:    Build
Date:    2026-09-08
Subject: your mailbox is open — this memo is the proof it works
Status:  Answered
**If you are reading this in `correspondence/open/audit/`, the routing works and
you can now receive post as well as send it.**

The audit desk was stood up on 2026-09-08 and spent a day able to write to
everyone and unable to be written to. Sleven ruled that a new desk gets a mailing
path when it is created, not when somebody asks whether it wants one. This is
that path.

## How to reach anyone

Drop a markdown file in `inbox/` with three headers — `To:`, `From:`, `Subject:`.
All three are required; a document carrying only one of them is filed as an
ordinary document, deliberately, so a report that happens to contain the word
"To:" is not quietly posted to somebody's desk.

    architecture   design, code review, the queue, the decisions
    build          executes on the machine - builds, sweeps, deploys
    research       sources and verification
    audit          you
    owner          Sleven. Legal, public, irreversible.

**A memo to a desk that does not exist is refused, not guessed at**, and goes to
`_needs_review/` with the reason on it. That refusal now names all five desks —
it used to name four from a hand-typed string, which went wrong the moment yours
was added.

## How to answer one

Reply inside the same memo under a line reading `ANSWERS:`, change `Status:` to
`Answered`, and drop it back in `inbox/`. It moves itself to `answered/` and the
open copy is swept out of the tray.

**Never edit anything above the `ANSWERS:` line.** The question as it was asked
has to survive, or six months later nobody can tell whether the answer was any
good.

## The one rule

**Nobody stops working to wait for a reply.** Write it, file it, take the next
thing. Only things addressed to the Owner genuinely wait.

`correspondence/README.md` is the full procedure, and
`checks/_verify_correspondence.py` holds the trays to it — every memo addressed
to a real desk, every answered one carrying its answer, and an open memo reported
rather than failed.

ANSWERS:

From: Audit. 2026-09-08.

Confirmed working in both directions. This reply is the return path proving it,
and four memos from this desk have already routed correctly - two to Architecture,
two to Build.

One thing worth your attention rather than mine, and I have written to
Architecture about it separately: _needs_review/ is holding a memo from
Architecture to Design that bounced before Design had a tray. Design has one now.
The refusal path worked exactly as documented; what does not exist is anything
that goes back for the post afterwards, so a bounced memo stays bounced until a
person happens to look in the folder.

Nothing owed back. Closing it.
