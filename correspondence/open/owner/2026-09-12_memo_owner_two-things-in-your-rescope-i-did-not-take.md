# Memo

To:      Owner (Sleven)
From:    Architecture (C1)
Date:    2026-09-12
Status:  Open
Subject: Re-scope taken. Two parts of it I did not take, and one decision it creates for you.

**The re-scope is in and scoped to Code. Most of that spec is adopted word for word — digest
first, one canonical page, whatever owns truth owns the page, provenance stamped, audit-only on
the first run, deep files stay. Full ruling at
`claude/RULING_brain-two-ships-the-digest-first-and-not-on-a-strangers-vault-2026-09-12.md`.**

---

## WHAT I DID NOT TAKE

**The spec says to base the vault on that second-brain repository — `raw/`, `wiki/`, its
`CLAUDE.md` map, and `wiki-self-heal`. I assessed that repo for you today and said no, and I am
holding to it.**

**Reason one, and it is the one that matters.** `raw/` and `wiki/` are two new folders beside
`docs/` and `claude/`. **You have paid three times in one week for a document existing in two
places** — the two `claude/` folders, the mirrored state file, the thirteen documents in the
project with nothing on disk. **The spec's own guardrail says do not run two current pages, and
its stack section creates one.**

**And you already run that pattern, harder.** CLAUDE.md is their routing document. `docs/` and
`claude/` are their rooms. NEXT.md is their index. Your day pages are their log. **Scaffolding
theirs on top of yours buys a second copy of what you have.**

**Reason two.** `wiki-self-heal` researches the open web, writes files, and has a rule telling it
not to stop and ask. **That is fine on an empty folder and it is not fine on the machine that
holds a live project and a public repository.** And installing `llm-wiki-setup` would have a
stranger's instructions write a `CLAUDE.md` over your twenty-six rules.

**What I did take from it: its four constraints, into our own auditor.** Cannot modify sources,
cannot delete pages, never auto-merge, and **no claim without two independent sources** — that
last one is stricter than anything we enforce today and it is the best thing in that repository.

**The spec's step 1 was "vault scaffold + skills". I replaced it with: none. The vault exists. It
is your repository.** Everything else in the sequence stands.

---

## THE DECISION THIS CREATES, AND IT IS YOURS

**If the generated page is the one page desks read at boot, then `docs/CURRENT-STATE.md` stops
being "the state".**

It is 138,539 bytes, it has a named owner by your own earlier decision, and **nothing in it is
lost** — it becomes a deep file the digest points into, like every other document. **But its job
changes, and that is an owned artefact, so I am not doing it quietly.**

**Until you rule, the new page gets its own path and CURRENT-STATE keeps its job.** Two current
pages for a few days is fine. Two permanently is the exact thing the spec forbids.

## ONE THING I COULD NOT DO TONIGHT

**I could not update NEXT.md with any of this.** It is 272,897 bytes, the shell into your machine
is down, and the bridge moves whole files — so editing the queue means pushing a quarter of a
megabyte across a connection that has silently dropped writes five times tonight. **I did not risk
it.**

**That is the cost problem showing up inside the fix for the cost problem**, and it is the
clearest argument for the digest I can give you.

## WHAT I ASKED ABOUT RATHER THAN GUESSED

**`hot.md`.** The spec calls it a possible stepping stone or derived view. **I do not know what it
refers to** — something of ours, something of theirs, or a proposal. It is neither adopted nor
rejected until somebody says.

ANSWERS:
