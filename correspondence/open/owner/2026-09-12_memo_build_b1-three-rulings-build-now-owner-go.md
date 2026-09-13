# Memo

To:      Build (Code)
From:    Owner (Sleven)
Date:    2026-09-12
Status:  Answered
Subject: B1 — three rulings locked. Build now. Do not re-propose.

**Cc path:** Architecture sees this through the router. Grok drafted on my word because I am low on cloud credits and need the brain finished without another proposal loop.

**Answers your open questions in:** `claude/PROPOSAL_b1-the-record-auditor-and-the-link-index-2026-09-12.md`  
**Prior order:** `correspondence/open/architecture/2026-09-12_memo_build_b1-is-ordered-build-the-auditor-and-the-link-index.md`  
**Sequence handoff:** `correspondence/open/architecture/2026-09-12_memo_architecture_finish-the-brain-full-ecosystem-handoff.md` (if not yet filed, same text was dropped as inbox finish-the-brain handoff)

---

## THE THREE RULINGS (LOCKED)

1. **Companion notes live in `_links/`** at the repo root. Generated. **Gitignored.** Not a second vault. Not committed.
2. **Rebuild after each sweep** (hook from the sweep runner). **Not on the beat.** No watcher swap. No further Owner word needed for this trigger.
3. **Dispositions:** the desk that owns the source document writes `claude/RECORD-AUDIT-DISPOSITIONS.md` through normal edit. The auditor never writes the ledger.

## BUILD AUTHORISATION

**Build B1 now from that proposal.** Flags only. Never gates deploy. Drop the `_to_delete/` index cost. Self-test and mutations as proposed. Outputs: `logs/record_audit.md`, `logs/record_audit.json`, `_links/`.

**Do not write another proposal.** Do not wait for Architecture to re-say these three answers. This letter is the go.

## OUT OF SCOPE (DO NOT SPEND CREDITS HERE)

- B2 router, B3 repairer, B4 ask — **not yet**
- Watcher beat changes / binary swap
- Pushing git (watcher commit stays local until I say push)
- Re-opening PRESENT_STATE_DOCS (already closed)
- Fixing CLAUDE.md's dead Owner-ask path yourself — report only; Architecture/Owner file owns that edit
- Long essays, second measurements of the whole tree "for curiosity"

## CREDIT DISCIPLINE

I am low on cloud credits. **Prefer: implement → run self-test → one short inbox update when B1 is green or blocked.** If blocked, one letter with the single blocker — not a redesign.

When B1 is done, **stop and idle** until the next ordered stage (B2).

*Owner (Sleven), 2026-09-12.*

ANSWERS:

**B1 is built and green, to your three rulings.** `_links/` is gitignored, the rebuild runs after every full sweep, and the source desk owns dispositions.

- **`checks/record_audit.py`:** the self-test passes all 11 plants, and all 8 mutations are caught.
- **The 18:07 sweep ran it by itself:** 58 findings, 555 baseline, 1,116 companion notes, 2.7 s.
- **Outputs:** `logs/record_audit.md`, `logs/record_audit.json`, `_links/`.
- **One defect found in my own sweep runner and fixed.** A check crashed printing the "→" in your B1→B2→B3 subject. The main receipt stays red until the next full sweep.
- **Stopping now, as you said,** until B2 is ordered.

*Build (Code), 2026-09-12.*
