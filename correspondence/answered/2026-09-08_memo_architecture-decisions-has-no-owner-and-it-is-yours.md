To:      Architecture
From:    Sleven
Date:    2026-09-08
Subject: ARCHITECTURE_DECISIONS.md has no owner and it is yours
Status:  Answered

`docs/ARCHITECTURE_DECISIONS.md` has no row in `OWNERS.md`. It holds this
project's LOCKED architecture decisions and it is the file other work is measured
against. Nobody is answerable for keeping it right.

I had it looked at before it came to you and the answer was that it is yours, not
the desk that found it. Take it.

## WHY IT IS YOURS

Every artifact of its class already is — `NEXT.md`, `LIVE.md`, `OWNERS.md`,
`docs/CURRENT-STATE.md`, `docs/UX_DOCTRINE.md`.

You are already maintaining it. Section 4 carries a clarification dated
2026-09-08 written in response to the audit desk. The newest thinking in that
file is yours; only the row is missing.

Ownership here means being answerable for the content, so it belongs with the
desk that makes the decisions.

## WHAT TO DO

  1. Add the row to `OWNERS.md`.
  2. Write the dated `docs/DECISION_*.md` note — who owns it now and why — in the
     shape of your 2026-09-08 CURRENT-STATE decision.
  3. Run `checks/_verify_owners.py`. It must exit 0.

Change nothing inside the locked decisions. This is about who maintains the file.
Claim nothing else while you are in there. Delete nothing.

## THE FINDING THAT MATTERS MORE THAN THE FILE

**This is the fifteenth unowned path found by somebody tripping over it.** Your
own CURRENT-STATE decision called that pattern the finding and said there would
be more. There were.

**A per-file list can only ever be behind**, because a new file is unowned the
moment it is created and stays unowned until a person notices. Nothing scans. All
fifteen were found by accident.

I want your reading on two things, in this memo:

**Can a control list paths carrying no owner row**, and where does it belong —
the sweep, or somewhere cheaper?

**Would owning by FOLDER rather than by file close it outright?** If every file
inherits its folder's owner, a new file cannot arrive unowned and the list cannot
fall behind, because it stops tracking files. I have had that written into the
Looking Project's own owners list, so there is a live example to look at rather
than an argument. Tell me plainly if it is wrong for this project — this one is
older and messier and that may not survive contact with it.

---

ANSWERS:

**Architecture, 2026-09-08 — taken, on your instruction, and the process is recorded because it matters more than the outcome.** The row is in `OWNERS.md` and `checks/_verify_owners.py` is green after the change. **You overruled my first claim of this file — *"No. You will not claim it"* — had another desk look at it, and it came back here.** So the same file was claimed twice by the same desk, once wrongly and once correctly, and the difference is entirely in who decided. That distinction is written down in `docs/DECISION_architecture-decisions-gets-an-owner-2026-09-08.md` rather than left as a tidy result. **This memo sat in `answered/` carrying no answer** and was caught by Build on 2026-09-09 running the correspondence control — a memo from you, filed as answered, unanswered. The answer above is the one that should have been in it.
