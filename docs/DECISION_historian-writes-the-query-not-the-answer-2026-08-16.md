# DECISION — the Historian's model writes the QUERY, never the answer. Flexible over rigid, and latency is explicitly accepted as the price.

    decided by  Sleven, 2026-08-16, in session
    recorded by C3 (Cowork)
    status      STANDING. Binding on any Historian prototype, including a
                throwaway one.
    supersedes  §2 of WORKORDER_historian-foundations-2026-08-16.md, which
                offered two options and recommended the wrong one. See §1.

---

## The ruling, in Sleven's words

> "I like the idea of flexible. It could be a little longer. I understand for it
> to get the correct answer it has to do the correct steps to get it. So it takes
> a little longer. As long as it's not taken, like, minutes... but, yeah, it can
> take time. I like that idea."

## 1. Correction to the work order first

**The work order presented two options and recommended option 2. That
recommendation is withdrawn.**

    option 1   model gets the question + a pile of data, produces the answer
    option 2   fixed question categories -> fixed query -> model phrases rows
    option 3   MODEL WRITES THE QUERY -> query runs -> model phrases the rows

**Option 2 is safe and rigid, and the work order did not say the rigid part
clearly enough.** A fixed category list means any question nobody anticipated gets
"I don't have that" even when the answer was sitting in the database. That is a
worse failure than it sounds — it is the assistant being wrong while appearing
honest, and it would have needed categories added forever.

**Option 3 is the decision.**

## 2. What was decided

**The model's job is to turn a question into a database query. It is not to
produce facts.**

    question arrives
      -> model composes a QUERY  (its only creative act)
      -> that query RUNS against the real database
      -> model receives the actual rows
      -> model writes them into a sentence in her voice

**Every number she speaks came out of the database moments earlier.** The model
never recalls, never estimates, never fills a gap.

**Why this beats both alternatives:**

- **Flexible like option 1** — it handles questions nobody anticipated, because it
  composes the question rather than remembering the answer.
- **Honest like option 2** — it cannot invent, because it never sees anything
  except real rows.
- **Fails correctly.** A badly composed query returns nothing, and nothing becomes
  "I don't have that." **The failure mode is silence, not fiction**, which is the
  right way round for something whose answers get believed.

## 3. Latency is accepted, and here is what was accepted

**Sleven explicitly traded speed for correctness.** Recording the actual numbers so
nobody later "optimises" the query step away to save a second.

    model composes the query      0.5 - 1.5 s
    query executes                milliseconds
    model phrases the rows        0.5 - 1.5 s
                                  ----------------
    typical                       1 - 3 s
    complex question              up to ~5 s

**Well inside the stated bound of "not minutes."** Repeat questions within the same
patch return from cache immediately, so the common case is faster than this.

**This budget is for the WEBSITE.** The in-flight companion, if it becomes real, has
a stated ceiling near 3 seconds and may need a variation — a narrower model, a
warmed cache, or a smaller query surface. **That is a separate decision and is not
made here.**

## 4. Two properties that come free, and both are worth keeping

**The query is inspectable.** She composed it, so it exists as readable text. She
can show it when challenged, and a wrong answer can be diagnosed by looking at what
she actually asked for. **With option 1 you get a wrong answer and no way to find
out why.** This is also in character — a records-keeper who can show the record.

**Answers cache cleanly.** Identical question plus identical patch produces an
identical query and therefore an identical result. Key the cache on both and
invalidate on patch change. This is what makes the running cost manageable, which
the original design notes correctly flagged as a real constraint.

## 5. THE ONE PIECE OF REAL WORK THIS CREATES — do not do it cheaply

**The query layer must be read-only, enforced at the database, not by instructing
the model.**

A language model composing queries against a database that can be written to is a
serious mistake, and "we told it only to read" is not a control. The enforcement
belongs where it cannot be talked around:

- a database role with **SELECT and nothing else** — no INSERT, UPDATE, DELETE,
  DROP, no schema access
- a statement timeout, so one bad query cannot hold the database open
- a row cap, so a query cannot return the whole catalogue
- the composed query **logged before execution**, every time

**Rule 12 applies.** The check that matters is one that proves a destructive query
is *refused by the database*, not merely never generated. A read-only guarantee
that has only ever been observed not being tested is not a guarantee.

## 6. What this does NOT decide

- **Which model.** Open. It affects the latency numbers in §3 and nothing else
  structural.
- **Whether the query language is SQL or something narrower.** A restricted query
  vocabulary may be safer than raw SQL and is worth considering. Code's call.
- **Anything about the character, the voice, the holo pad or the art.** Untouched.
- **When any of this gets built.** The Historian remains a parallel side project
  that has not started. **This decision exists so the first prototype does not
  quietly pick option 1 by default.**

## 7. What I checked and what I did not

**Checked:** nothing new. This records a decision made in conversation, plus the
correction in §1 which is mine.

**Did NOT check:**
- **The latency figures in §3 are estimates from typical model behaviour, not
  measurements.** Nothing has been built and nothing has been timed. They are the
  right order of magnitude and they should be replaced with real numbers the first
  time a prototype runs.
- Whether the current data layer can answer the queries this implies. The site's
  data lives across a database and a set of derived JSON files, and **a query layer
  spanning both is not a solved problem here.**
