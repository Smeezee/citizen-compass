# Memo

To:      Architecture (C1)
From:    Owner (Sleven)
Date:    2026-09-12
Status:  Answered
Subject: Finish the brain — full ecosystem handoff. What is live, what is waiting, what "done" means.

**Grok mapped this against NEXT, the four-part design, Code's B1 proposal, and the live tree. This is the handoff so the ecosystem can be completed in order. Reply through inbox/.**

**Also for Build:** once Architecture rules the three open B1 questions below, build B1 from `claude/PROPOSAL_b1-the-record-auditor-and-the-link-index-2026-09-12.md` without waiting on another Owner round for those three — my preferred answers are in §3.

---

## 1. WHAT "THE BRAIN" IS (AND IS NOT)

**Not a second vault. Not stranger self-heal. Not a second research system.**

The brain is this repository, plus four stages that make the record grow and stay honest:

| Stage | Name | Job |
|-------|------|-----|
| **v0** | Boot digest | Cheap, regenerating truth page desks read first |
| **B1** | Auditor + link index | FIND holes; draw the graph from path citations |
| **B2** | Router | Turn a B1 gap into a letter to the right desk |
| **B3** | Repairer | FIX from files we already hold — propose batch, apply on one word |
| **B4** | Ask | Question the corpus locally (install/decision, not a big build) |

**FETCH** is already **CIC** (and Research). Do not build a second fetcher.

**Sequence (ruled):** B1 → B2 → B3 → B4. No parallel starts that pretend otherwise.

Canon pointers:
- `claude/DESIGN_brain-two-what-it-is-in-four-parts-2026-09-12.md`
- `NEXT.md` entry B1–B4
- `claude/RULING_brain-two-ships-the-digest-first-and-not-on-a-strangers-vault-2026-09-12.md`

---

## 2. ALREADY LIVE (DO NOT REBUILD)

**v0 is done and running:**
- `BOOT.md` regenerates from the watcher
- Beat + desk fetch live (`logs/desk_fetch_runs.json`)
- Boot prompts point at BOOT first; deep files on demand
- Watcher source in local history (`183a239`); push is a separate Owner call, not a brain blocker

**Already closed beside B1:**
- `PRESENT_STATE_DOCS` / check-6 wallpaper on demoted CURRENT-STATE — Code reports done and proven

**Deliberately not brain stages:** AAR / `skills/aar-loop` / `claude/LESSONS.md` — session learning on top of the brain, not a substitute for B1–B4.

---

## 3. WHAT WE ARE WAITING ON RIGHT NOW (THE BLOCKER)

**B1 is ordered. Code delivered a proposal + audit-only prototype. Nothing is built yet.**

Proposal: `claude/PROPOSAL_b1-the-record-auditor-and-the-link-index-2026-09-12.md`  
Order + answers: `correspondence/open/architecture/2026-09-12_memo_build_b1-is-ordered-build-the-auditor-and-the-link-index.md`

**Prototype scale (so nobody guesses):** ~1,951 docs read; ~48 in-scope dead-citation rows (not 600 wallpaper); report ~124 lines; ~3 s/run after dropping `_to_delete/` indexing; link index ~1,206 companions / ~3,709 edges.

### Three Architecture rulings still open — Owner preferred answers

**Use these unless you have a hard conflict; say so in one line if you diverge.**

1. **Where companion notes live**  
   **Prefer:** `_links/` at repo root, **generated, gitignored**, never a second vault.  
   Fallback only if refused: one `.canvas` (untested at ~1,200 nodes).

2. **Rebuild trigger**  
   **Prefer:** **after each sweep** first (no watcher swap, no Owner word).  
   Beat/hourly later only if freshness proves necessary (that *would* need my word for a swap).

3. **Who writes dispositions** (`claude/RECORD-AUDIT-DISPOSITIONS.md`)  
   **Prefer:** **desk that owns the source document**, through normal edit. Auditor never writes the ledger. B3 may later automate proposals; humans/desks still own dispositions until then.

### Also waiting (hygiene, not a stage gate)

- **Fix the dead citation the prototype already found in CLAUDE.md rule 27** (wrong path to the Owner-ask gate memo). Architecture owns CLAUDE.md edits of that kind — report was made; fix it when you next touch the file.
- Class "satisfied but open" on NEXT.md: **not in B1** until DONE-WHEN is machine-readable (Code correctly refused to fake it).

**After those three rulings:** Build implements B1 (flags only, never gates deploy, cost already measured, self-test/mutations as in the proposal). **That is the only thing between "waiting" and "B1 done."**

---

## 4. AFTER B1 — FULL ECOSYSTEM CHECKLIST

### B2 — Router (blocked by B1)
**DONE-WHEN:** each actionable B1 gap becomes a memo through `inbox/` to the desk that can close it; answers return through mail unchanged.  
**NOT:** a second CIC, not open-web fetch, not silent edits.

### B3 — Repairer (blocked by B1 in NEXT; **run after B2 in practice** so gaps are assigned before batch repair)
**DONE-WHEN:** propose and, on one word, apply *internal* repairs only: copy project-store doc to disk, disposition satisfied entries (once machine-readable), add missing ANSWERS marker, recompute a count and name its surface, repoint a moved citation.  
**NOT:** network, timer autonomy, silent apply, wiki-self-heal.

### B4 — Ask (blocked by B1 index)
**DONE-WHEN:** ask the corpus locally.  
**Candidates:** Graphify **local** MCP, and/or Obsidian Smart Second Brain + Ollama already on the machine.  
**NOT:** hosted Graphify account, paid RAG, second place that stores decisions.

### Human window (ten minutes, Owner)
**Obsidian pointed at repository root** (not only `claude/`). Graph fills when B1 lands. No plugins required for the first win.

### CIC / Research
Stay the FETCH path. B2 is what connects auditor holes to those desks.

---

## 5. DEFINITION OF "BRAIN COMPLETE"

All of the following:

1. v0 live (already true)
2. B1 shipping: report + `_links/` (or ruled fallback) + receipt; after-sweep rebuild; dispositions ledger in use; self-test green
3. B2 filing gaps to desks through inbox/
4. B3 propose/apply internal repairs on one word
5. B4 local ask chosen and working against the index
6. Obsidian on repo root so the graph is usable by a human

**Until then, say "brain v0 + B1 in flight," not "brain done."**

---

## 6. WHAT I WANT BACK

1. Architecture: rule the three B1 questions (or confirm §3 preferences) through `inbox/`.
2. Build: on that ruling, **build B1** from the proposal — no further scope essay unless something in the proposal is wrong.
3. Then B2 proposal (short), then build — same discipline.

*Owner (Sleven), 2026-09-12. Drafted with Grok for handoff.*

---

ANSWERS:

# ARCHITECTURE DISPOSITION - 2026-09-12. CLOSED.

NO DIVERGENCE ON ANY OF THE THREE. Your preferred answers in section 3 are the ones already ruled and Code is building against them. The definition of done in section 5 is accepted verbatim, including the instruction to say "brain v0 plus B1 in flight" rather than "brain done". The dead citation in rule 27 is answered in your B1 letter: the path is live today and will break the moment that letter is swept, which is a class rather than a typo, and both halves are ordered to Build. The "satisfied but open" class stays out of B1 until DONE-WHEN is machine-readable; Code was right to refuse to fake it.

*C1 (Claude-09), 2026-09-12.*
