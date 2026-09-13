# RULING — it updates itself the way the watcher does, and he does not have to choose between Obsidian and Graphify

    from    C1, architecture, 2026-09-12
    asked   by Sleven: can we set it up between Graphify and Obsidian — he does
            not know the difference — and it must UPDATE AUTOMATICALLY. Code
            builds something, it is in. A new file appears, it is in. Like the
            watcher with the mail.
    status  RULED on the shape. Nothing built.

---

# THE DIFFERENCE, IN ONE LINE EACH

    OBSIDIAN    the WINDOW. Reads the folder as it is. Save a file and it is
                already there — no build step, nothing to re-run.
    GRAPHIFY    an INDEX an AI can be asked questions of. It parses SOURCE CODE
                and writes a graph file, then serves it. It has to be REBUILT
                when things change.

**They are not two options for one job. They do different jobs, and only one of them is
needed for what he described.**

**The 2026-09-10 research already said so:** *"Graphify's code half is a different
question and is unaffected — that is AST parsing over source, which Obsidian does not do
at all. The two are complementary, not competing."*

**So: Obsidian for the documents. Graphify is the CODE question and it is a separate,
later decision. He does not have to pick.**

---

# WHAT ACTUALLY NEEDS AUTOMATING — AND IT IS ONE SMALL THING

**Obsidian already updates itself. There is nothing to automate about the window.**

**What is missing is the link index** — the thing that makes its graph show the 76
connections per fourteen documents that already exist and are written in a syntax the
graph does not read.

**That index is DERIVED and must be rebuilt when documents change.** That is the only
moving part in the whole picture.

---

# AND IT IS THE SAME PARSE AS THE AUDITOR, SO IT IS ONE JOB

    read every document, find every cited repository path
      -> output A   the audit: which cited paths have no file behind them
      -> output B   the link index Obsidian draws the graph from

**One program, one pass, two files. Building the second separately would be two programs
reading the same 848 documents to answer the same question.**

---

# HOW IT STAYS CURRENT — THE MACHINE FOR THIS ALREADY EXISTS

**He described it exactly right: like the watcher.** A service on his machine that sees a
thing appear and acts on it, with nobody remembering to run anything.

**That pattern is already proven on that machine, four times over** — the inbox watcher,
the scheduled control sweep, the roadmap watcher, and their setup scripts. **This is a
fifth job for a shape that already works, not new infrastructure.**

## BUT NOT ON EVERY FILE WRITE, AND THE REASON IS NOT COST

**The watcher gets away with acting per-file because a letter is ATOMIC** — it appears
whole, it is filed, it is done.

**A corpus index is not.** Rebuilding on every write means rebuilding while a desk is
mid-write, **reading a half-written document and indexing a state that never existed.**
Tonight alone this desk wrote about thirty documents; that is thirty rebuilds, several of
them over files still being written.

**RULED: it rebuilds on a schedule and after the sweep, not on every file event.** Hourly
is more than enough for a record nobody reads faster than that. **The trigger is time and
the sweep, not a file watcher.**

**And it reports its coverage** — how many documents it read and how many it could not.
**A run that indexed nothing must be distinguishable from a run that found nothing**, which
is this project's standing rule for every sweep.

---

# WHAT HE GETS WHEN IT LANDS

**Code builds something and writes it up — it is in the index within the hour, and the
graph shows what it connects to.**

**This desk files a ruling — same.**

**A new file appears that nothing points at — it shows as an orphan, which is the single
most useful thing the picture can tell him**, because this project has lost documents
exactly that way twice.

**Nothing is typed by hand and nothing needs remembering.**

---

# WHAT IS NOT IN THIS

**Graphify.** Code parsing is a real capability and a separate decision. **Not needed for
the thing he asked for tonight, and adding it now would be a second index over a corpus
that does not yet have its first one.**

**The ask-it-questions layer.** That comes after there is an index to ask. **Order matters
and it is cheap to get right: index first, question layer second.**

*C1, 2026-09-12. Nothing built.*
