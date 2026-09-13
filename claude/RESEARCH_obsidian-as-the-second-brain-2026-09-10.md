# RESEARCH — Obsidian as the second brain, and what it does that the paid options do not

**Filed 2026-09-10 by the Adjutant desk. Research only. Nothing installed, nothing
changed, no authorisation requested yet.**

---

## THE HEADLINE, BEFORE THE DETAIL

**The free layer of Obsidian — no plugins, no AI, no keys — solves more of this
project's stated problem than any of the paid options under consideration, and costs
nothing to try.**

The problem, in this project's own words, is a filed finding titled *"this project
keeps reinventing the same idea."* 848 documents. Desks that cannot see what another
desk wrote. **That is a retrieval and connection problem, and the free layer is aimed
squarely at it.**

**Everything below the free layer is where the same boundary question as Graphify
comes back.**

## 1. WHAT IT ACTUALLY IS

A desktop and mobile application that reads a folder of plain markdown files. **No
database. No import. No conversion. No cloud account required.** The folder — called a
vault — is exactly the files that were already there.

**Free for personal use.** Sync and publish are paid add-ons and neither is needed.

**The reversibility is the important property:** point it at a folder, and if it is
not useful, close it. The files are untouched. **There is no migration to undo and no
format to escape from.**

## 2. WHY THE FIT HERE IS UNUSUALLY GOOD

**This repository is already a vault.** 848 markdown documents in `claude/` and
`docs/`, plus the correspondence trays, plus the day pages in the desk logs. Nothing
needs restructuring.

**And the structure was already started.** `inbox/Citizen Compass AI Brain/` carries
numbered folders — `00 start here` through `09 session logs`, plus `archive`. The
project memory records it as *"scaffolded but unfinished, queued as a future project,
no timeline set"*, dated 2026-07-30. **The idea is six weeks old and half-built
already.**

**It works on a phone.** Given how this project is actually run — voice, mobile, and
frequently away from the desk — a knowledge system that only exists on the Windows
machine is a knowledge system that is unavailable most of the time.

## 3. THE FREE LAYER, IN DETAIL — THIS IS THE PART TO TRY

    BACKLINKS      every document shows what points AT it, computed, not typed
    GRAPH VIEW     the whole corpus as a picture; ORPHANS ARE VISIBLE
    LOCAL SEARCH   across every file at once, instantly
    TAGS           and saved queries over them

**The orphan property is the one worth naming.** A document nothing links to is
either dead or lost — and this project has lost documents by filing them where a desk
could not read them, twice in one night, at a cost of roughly twenty desk-hours.

**None of this involves a model. Nothing leaves the machine. There is no key, no
spend, and no refusal problem.**

## 4. THE AI LAYER — TWO REAL CANDIDATES, BOTH VERIFIED

### Smart Second Brain — a plugin, actively maintained

    community plugin, v2.0.5, 35 releases, ~66,000 downloads
    requires Obsidian 1.11.4+, desktop AND mobile

Semantic search, an automatic topic graph, and an agent that reads and writes notes.

**The finding that matters: search and the graph work with NO AI provider configured
at all.** The model is only needed for the agent. **So a meaningful part of the value
is available without any boundary question.**

**And it runs fully local when a model is wanted** — Ollama or oMLX, with nothing
leaving the machine. Cloud providers (OpenAI, Anthropic, OpenRouter) are optional, not
required. **Ollama is already installed on this machine** — there is an `.ollama`
folder in the home directory.

### obsidian-second-brain — a Claude Code skill, not a plugin

    github.com/eugeniughelbur/obsidian-second-brain
    4,400 stars, MIT licence

Persistent memory for Claude Code and seven other CLI agents, stored as plain markdown
in a vault. Roughly 47 commands: save, ingest, daily notes, synthesis, health checks,
research, and scheduled background agents.

**Core vault commands need no API key.** The research commands optionally use Grok,
Perplexity, Gemini or the YouTube API, and fall back to free sources without them. A
`--free` flag disables the paid backends outright.

**Two of its design choices match decisions this project reached independently
tonight:**

- **Background agents are inert by default and must be opted in to arm.** That is
  fail-closed by absence — the same posture as the master switch.
- **Health checks flag stale facts.** Stale-thing-that-looks-current is this
  project's signature defect, hit twice tonight alone.

**That convergence is a point in its favour and also a reason for caution** — see
below.

## 5. THE RESERVATION, AND IT IS THE SAME ONE AS GRAPHIFY

**This project is already building a memory system: correspondence trays, handoff
archives, `CURRENT-STATE.md`, desk day pages, and a set of standing rules about which
of those is authoritative for what.**

**Adopting a second one that also stores decisions, people, tasks and daily state
creates two systems for one job.** That is duplicated authority, which is the defect
this repository has paid for more than any other — and no amount of good design in the
second system fixes it.

**So the reservation is not about the tool. It is about the boundary.** If it is
adopted, it needs one sentence settled first: **what does the vault hold that the
correspondence system does not, and which one wins when they disagree?**

**The free layer does not raise this question at all**, because it stores nothing — it
only shows what is already there. **That asymmetry is the whole reason for the
recommendation below.**

## 6. THE BOUNDARY QUESTION, STATED PLAINLY

**A vault pointed at this repository would contain the same material the curated
export is being designed to protect** — machine paths, an account name, the switch
path, an ACL audit, and a separate project named explicitly.

    FREE LAYER          nothing leaves the machine. No question to answer.
    LOCAL MODEL         nothing leaves the machine. Ollama is already installed.
    CLOUD MODEL         the vault's contents go to a third party. Same refusals
                        the export design is working out, or do not do it.

**These are not three options to weigh. They are one decision already made elsewhere
tonight, applied to a second tool.**

## 7. RECOMMENDATION

**Install Obsidian. Point it at the repository. Add nothing else.**

No plugins, no AI provider, no key, no spend. **Look at the graph, look at what is
orphaned, and see whether the free layer answers the question before anybody evaluates
a paid one.**

**It costs an install and ten minutes, it changes no file, and it is reversible by
closing the window.** If the graph over 848 documents turns out to be the answer, that
settles the Graphify document-half question for free — and if it does not, the paid
evaluation starts from evidence rather than from a guess.

**Decide on the AI layers afterward, and decide the duplicated-authority question
before, not after.**

## 8. WHAT THIS DOES NOT SETTLE

**Graphify's code half is a different question and is unaffected** — that is AST
parsing over source, which Obsidian does not do at all. The two are complementary, not
competing.

**Nothing here is authorised.** No install, no plugin, no vault created, no repository
change.
