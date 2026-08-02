# Hard rule 13 added — file the handoff before you move on

Added to `CLAUDE.md` on Sleven's instruction, 2026-08-01. He has had to reinforce this in conversation more than once, which is why it moved from a standing rule to a hard rule.

## The rule

**A unit of work is not finished until it is recorded. Never begin new work while the previous work is unfiled.**

Three mandatory triggers:

1. **When work arrives** — before starting, file an `inbox/` update saying what was received and what is about to be done. Being handed a work order is exactly this moment.
2. **When a unit of work finishes** — file before touching anything else. Finish, file, then start the next thing. Never finish, start the next, and file both later.
3. **When stopping for any reason** — blocked, waiting on a decision, out of scope, or idle.

**Frequency is not a concern. Under-reporting is.** A hundred updates in an hour costs nothing. One update covering three tasks is a failure, because it collapses the order events happened in and hides where something went wrong.

The test: if this session ended right now, could the next one tell what was finished, what was in flight, and what was never started?

## What changed versus the previous standing rule

The standing rule already covered *finishing* a step and *stopping*. It did not cover:

- **Filing when work arrives.** The gap this closes: a session that receives a work order, begins a long operation, and dies mid-way leaves no record that the work was ever assigned. The next session cannot distinguish "never started" from "started and lost."
- **The bar for starting something new.** Now explicit — if you cannot point at the update that closed the last thing, the last thing is not closed.

The standing rule section remains and now carries a pointer to rule 13.

## Note on where this came from

Sleven's words, close to verbatim: *"If you're doing a project, finish the project, then update, then start a new project. If you're not instructed to start a new project, you should have already done a handoff. You should do a handoff once you receive your work."*

The prompting observation was that Claude Code had stopped attaching what it had done, leaving him unable to tell whether a task had started, stalled, or completed.

A backup of the previous `CLAUDE.md` is in `_to_delete/` and can be removed once this is confirmed good.

## This applies to the Cowork side too

Cowork sessions write to two channels — this project's docs on claude.ai, and `inbox/` here. Rule 13 governs the `inbox/` channel identically. Project docs are invisible to Claude Code and every other machine-side session; the inbox is the only shared record.
