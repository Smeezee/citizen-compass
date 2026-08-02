# DESIGN — one handout a day that fills itself

Written 2026-08-02 in answer to: *"have we figured out how to put all information into one detailed handout at the end of the day? like, it just constantly funnels in there every bit of information that we find out."*

---

## What already exists, honestly

**The funnel is built and it works.** Any session writes a `.md` into `inbox/`, `inbox_watcher.exe` picks it up, and it lands in `LATEST_HANDOFF.md`. That has been running all week and it is the reason work survives between sessions.

**Four things are wrong with it**, and only the last one is hard.

**1. It grows without a ceiling.** `LATEST_HANDOFF.md` is 88,427 bytes and climbing. A handout nobody can read is the same as no handout. There is no boundary in it — Tuesday and Friday sit in one undifferentiated pile.

**2. There is no "day."** It is a continuous stream. "What happened today" cannot be answered without reading everything and doing the date arithmetic by hand.

**3. Two channels that do not sync.** claude.ai project docs are invisible to Claude Code and every machine-side session; `inbox/` is invisible in claude.ai. Today both are kept in step by a human-in-the-loop writing each thing twice. **That works until someone forgets, and then two records disagree with no way to tell which is right.**

**4. Summarising needs judgment, and the Go watcher has none.** The Python generator had an optional local-AI compression path. It was parked, and retiring Python deleted the only implementation. Go never had one. So nothing in the pipeline can write prose.

---

## The design decision that matters

**Separate the record from the summary. Never let one process do both.**

Every false claim this project has produced came from a summary, not from data:

- "Phase 1 is complete" — while source 6 had never been started
- "The stray watcher was stopped" — nothing stopped it; it exited on its own
- "Three fixes were rolled back" — they were applied at build time, correctly, the whole time
- "Part B has stopped" — the process was alive and writing 26 seconds earlier
- "Source 2 verified complete" — on a run whose `main()` returned `None`

Every one of those was plausible, well-written, and wrong. **A summariser's job description is to discard detail, which means a wrong summary is indistinguishable from a right one until someone goes back to the source.**

So:

- **The rollup is mechanical.** Deterministic, complete, no interpretation. Go can do this perfectly.
- **The narrative is a session's job**, written on top, and marked as interpretation.

This is the same rule as "auditors flag, never fix," applied to prose.

---

## Part 1 — the daily rollup (mechanical, Go)

At a fixed hour, the watcher writes `docs/daily/YYYY-MM-DD.md` from everything filed that day. No new capture mechanism — sessions already write to `inbox/`.

**Sections, in this order**, because it is the order a returning reader needs:

1. **Decisions made** — anything a session recorded as a choice, with who made it
2. **Completed** — work reported finished, each with how it was verified
3. **Defects found** — new problems, with severity
4. **Still open** — carried from yesterday's rollup, minus anything closed today
5. **Corrections** — anything filed today that contradicts an earlier record. **Its own section, because this project generates them and they are the most valuable lines in the file.**
6. **Raw entries** — every inbox item in full, so nothing is lost to grouping

**Rules the generator must follow:**

- **Never drop an entry.** Grouping and deduplication are for the summary sections; section 6 carries everything verbatim.
- **A day with nothing filed still gets a file** saying so. Otherwise a watcher that quietly died looks identical to a quiet day. This project has already had a scheduled process stop with nobody noticing.
- **Every claim carries its source** — which inbox file, which session, what time.
- **Never write a status that was not stated in an entry.** No inference. If nothing said "complete," nothing is complete.

**On growth:** once a day is rolled up, its entries are archived out of `LATEST_HANDOFF.md`, which then holds only the current day plus a standing "open items" block. The full history stays in `docs/daily/`. The running file stops growing without bound and stays readable.

---

## Part 2 — the claims register

The recurring failure is a claim entering the record without evidence and being quoted forever after.

**Every line asserting something is done carries one of three marks:**

- `[verified]` — checked against the artifact, with what was checked named
- `[reported]` — a session or tool said so, unconfirmed
- `[inferred]` — reasoned from other facts

**`[reported]` is not `[verified]`, and the rollup never promotes one to the other.** Claude Code refusing to gate an in-progress pull, and refusing to declare Part C's third difference resolved on its own, are both this rule working. Making it a field rather than a habit means it holds when nobody is being careful.

Anything `[reported]` for more than a week and never verified gets surfaced in section 4. **An old unverified claim is exactly the kind of thing that gets believed because it has been sitting there a while.**

---

## Part 3 — kill the two-channel problem

Machine side becomes authoritative. `inbox/` is the only place anything is filed.

The daily rollup is then exported to the claude.ai project as one doc per day. A session that wants the project record up to date copies the rollup rather than writing a second original.

**Nothing is authored twice.** Today's arrangement — a human writing each finding into two places — works right up until it doesn't, and the failure is silent.

---

## Part 4 — the narrative, written by a session

Once a rollup exists, a session can be asked to write the top of it: what mattered today, what it means, what should happen next. Marked as interpretation, sitting above a complete mechanical record that anyone can check it against.

**That is the actual handout**, and it is only trustworthy because the thing underneath it is not a summary.

If local AI is ever wanted for this, note that **handoff compression no longer exists in any form** — retiring `generate_handoff.py` removed the only implementation. It would be a new Go feature to build, not a switch to flip.

---

## Effort, honestly

Parts 1 and 3 are the bulk of the value and both are mechanical Go work on an existing watcher — days, not weeks. Part 2 is a convention plus a field. Part 4 is free; it is asking a session.

**Ranked behind the Path C auditors**, which are already 60% built and sitting on 874 unread findings. This is the right next thing after that.

---

## What it looks like when it works

End of day, one file, ordered so the first screen answers "what changed and what do I need to do." Nothing hand-copied. Nothing summarised twice. Every claim traceable to the entry that made it, and every unverified claim visibly marked as unverified until someone checks it.
