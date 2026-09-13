# RULING — we do not rewrite their skill. We write our own auditor, and the rule that makes it buildable was written tonight.

    from    C1, architecture, 2026-09-12
    asked   by Sleven: it is just a program — why not rewrite it with the parts
            that are useful to us and close the holes?
    answer  Right instinct, and when you strip the holes out almost none of
            their file survives, because it is shaped to their filing system.
            What survives is one page: an idea and four rules.

---

# WHAT IS ACTUALLY WORTH TAKING — AND IT IS SHORT

    the idea        an auditor that reads the record, finds gaps,
                    contradictions, orphans and stale pages, and REPORTS
    four rules      cannot modify a source file
                    cannot delete — flags for review instead
                    works on its own branch, never merges itself
                    no claim without >=2 independent sources
    one habit       audit-only first, before anything that writes

**That is the whole transferable payload.**

# WHAT WE DROP, AND WHY NOTHING IS LEFT AFTER

    the autonomy rule                 told not to stop and ask
    git init && git add . && commit   commits the whole folder before starting
    downloads into raw/               "cannot modify raw/" still lets web files
                                      land there
    writing during audit-only         it branches, writes and commits anyway
    the entire vault scaffolding      CLAUDE.md routing, raw/, wiki/, index, log

**The last one is the reason a rewrite is not a rewrite.** Their instructions are written
against THEIR filing system. **Ours is `docs/`, `claude/`, the correspondence trays,
`NEXT.md`, `CCDesk-logs` and a claude.ai project store — none of which their file knows
exists.**

**So keeping the useful parts means keeping an idea and four sentences, and writing
everything else from nothing. That is not a rewrite; it is a fresh control that happens to
have been prompted by reading theirs.**

---

# AND OURS HAS A BETTER SPEC THAN THEIRS, BECAUSE WE PAID FOR IT

**Their auditor looks for gaps in a knowledge wiki. Ours has to look for gaps in a RECORD
OF WORK, which fails differently. Tonight alone produced the list:**

    a document cited at a path that does not exist
      docs/CURRENT-STATE.md cites docs/SPEC_the-front-page-becomes-the-wall
    documents in the project store with no file on disk
      twelve of them, and the roles file blocked a job for hours
    a queue entry satisfied and still reading as open work
      R1, for two weeks
    a memo announcing a document that is not there
      named as a shape on 2026-09-10 and it happened again
    a closed letter with no ANSWERS marker
      turned the sweep red three separate times tonight
    a count taken on the wrong surface
      five instances this week, every one of them this desk's

**Every line is an incident with a date. That is a better specification than anything in
their file and it did not come from them.**

---

# THE TRAP, AND IT KILLED THIS CHECK TWICE ALREADY

**A control that verifies every cited path exists on disk goes RED IMMEDIATELY** — on
mirrors, and on memos legitimately citing project-only documents.

**That is exactly why the document-citation check was named twice and never built.** The
outgoing desk wrote the reason down: *"A check that goes red on correct behaviour is
switched off within a week."*

**So the scope gets written before the check does. That rule stands and this does not get
an exception.**

## WHAT CHANGED TONIGHT, AND IT IS THE WHOLE UNLOCK

**The check was unbuildable because there was no convention to check against. There is
one now.**

**Ruled tonight, out of the two-`claude/`-folders incident:** *a desk citing a document
cites it by the path a shell on that machine can open. A project-store path and a
repository path are different addresses and must never be written the same way.*

**With that convention the check stops being "does every path exist" — which is
unanswerable — and becomes "does every path that CLAIMS to be a repository path exist",
which is answerable and goes green on correct behaviour.**

**The rule that makes the control possible was written eight hours before the control was
proposed. That is the order things should happen in and it almost never does.**

---

# THE ORDER

**Build proposes it before building it**, with the scope written first, and named
explicitly: **what it asserts, what it deliberately does not assert, and one case that
must go GREEN which a naive version would turn red.**

**It flags and never fixes.** It writes a report, not a correction. **An auditor that
edits the thing it audits is the autonomy rule wearing our badge.**

**It does not gate a deploy.** Standing ruling on eyes and auditors: a flag that gets read
is worth more than a gate that gets disabled.

**And its cost is measured and reported before it joins the sweep** — section 9, and one
existing control is already 42.7% of the run.

*C1, 2026-09-12.*
