# PERPLEXITY BRIEF — find the tools we do not know about

**Filed 2026-09-10. Copy-paste block for Perplexity, which has no access to this
project and is not being given any.**

**DELIBERATELY GENERIC.** The system below is described in shape only — no file paths,
no machine names, no account names, no project names, no internal document titles.
That is the standing boundary and this block was written to respect it rather than
relying on a filter.

---

You are being asked to do discovery, not design. **I want to know what exists that I
have not heard of.** I will do my own evaluation; what I need from you is a
well-sourced map of the landscape.

## WHAT I AM RUNNING, IN SHAPE ONLY

A solo developer operating several AI coding and reasoning agents as separate
"desks", on one Windows machine, with a large markdown documentation corpus (roughly
850 documents) alongside a Python and Go codebase.

The desks communicate by dropping memo files into a watched folder. A small background
service reads the headers and files each memo into a per-recipient tray. Answers route
back to the sender. Everything is plain files on local disk — no database for this
part, no cloud service, no message queue.

Work is moving toward unattended operation: a desk can be woken headlessly, with
permission controls, spend limits and a master on/off gate that fails closed when
absent. One human owner authorises anything that changes state.

**The recurring failure is not crashes. It is silence** — a process that reports
success and produces nothing, a rule enforced by one program and not its twin, a
document filed where another desk cannot read it, a cached answer that looks current
and is not.

## WHAT I WANT YOU TO FIND — SEVEN AREAS

**1. Agent-to-agent messaging and orchestration.** What do people actually use to
coordinate multiple AI coding agents on one machine? File-based mailboxes, queues,
frameworks, or something I have not considered. **I want to know whether my file-based
approach is a known pattern with known limits, or an idiosyncratic thing I invented.**

**2. Detecting "running but not doing the job."** Not crash detection and not spend
limits — the case where a process exits clean and produces nothing. What do mature
unattended systems use? Heartbeats with progress content, outcome verification against
an expected artefact, dead-man switches, something else.

**3. Local knowledge and retrieval over a private markdown corpus.** Tools that index
documents and code WITHOUT sending them to a third party. Local embedding models,
knowledge graphs, AST-based code maps. **Emphasis on fully local — I have a hard
boundary against a document corpus leaving the machine.**

**4. Making an AI agent's memory durable across sessions.** What actually works for
carrying decisions, context and standing rules between sessions of a CLI coding agent?
Plain files, vaults, memory servers, project-scoped instruction files.

**5. Giving an agent non-text input.** Video, screen recordings, audio, images —
watched or read reliably, ideally with local processing. What is real and what is
demo-ware.

**6. Guardrails and permission systems for unattended agents.** Path allow-lists,
fail-closed gates, expiring one-run authorisations, spend ceilings, audit trails.
**Especially: how these are TESTED, since an untested safety control is not a safety
control.**

**7. The productivity tools I am probably missing.** Scheduling, dashboards over
agent activity, cost tracking, diffing what an agent changed, reviewing agent work at
a glance.

## HOW I WANT THE ANSWER

**For each thing you name:**

    what it is, in one or two plain sentences
    a PRIMARY link - the project's own site or repository, not a blog about it
    licence and cost
    LOCAL OR CLOUD - and if cloud, what specifically leaves the machine
    how alive it is - real activity, not a star count
    what it replaces or competes with

**Rank by how likely I am not to have heard of it.** I already know about the obvious
large tools. **The value you add is the thing with two thousand users that solves a
problem I have been working around by hand.**

**Flag anything that is mostly marketing.** A lot of this space is content creators
promoting tools they have not used. If something is widely posted about and thinly
used, say so — that is as useful to me as a recommendation.

**And say plainly where you find nothing.** If an area has no mature answer, I would
rather know that than read a list of near-misses. "Nobody has solved this well" is a
real finding and I will act on it.

## WHAT I AM NOT ASKING FOR

Not a recommendation of which to adopt — that is mine, with evidence. Not a
comparison table. Not tutorials. **Not anything requiring access to my files, my
machine, or my code, none of which you have or will be given.**
