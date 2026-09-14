# Memo

To:      Engineering
From:    Build
Subject: The record auditor is proposed, not built. The naive version would go red on 596 of 4,903 citations on day one. Ours judges only what was written under tonight's convention.
Status:  Closed

**The proposal:** `claude/PROPOSAL_the-record-auditor-scope-first-2026-09-12.md`.

**One read-only measurement sized it.** Over 1,830 documents, a naive "every cited repo path must exist" check finds **596 of 4,903 citations pointing at nothing**:

- 455 absent - mostly `claude/` project-store documents cited in repository shape, before the convention existed
- 111 moved - 42 of them `inbox/` transit addresses
- 30 set aside

**That is the trap, in numbers.**

## THE SCOPE, IN THREE LINES

- **It asserts:** repository-path citations resolve (R1); memos do not announce missing documents (R2); a `claude/` path with no file is flagged unless the same line says "project store" (R3).
- **Only documents dated on or after 2026-09-12 are judged.** The 596 historic flags go into one baseline file, once.
- **It does not assert:** DONE-WHEN satisfaction and count surfaces (both prose), project-store contents (invisible here), closed-letter markers (already covered twice), or anything written before the convention.

## YOUR CONDITION - THE CASES THAT MUST GO GREEN, WHICH A NAIVE VERSION TURNS RED

- **G1:** a project-store document named as such on the same line.
- **G2:** an `inbox/` path the watcher has since filed elsewhere, resolved by filename.
- **And the one that must STAY red:** tonight's roles-file citation, made before the file existed.

**Cost, measured:** 7 seconds for the full scan, about 0.3% of a sweep.

**It flags, never fixes, and never gates.** It exits 0 and writes one report.

## FOR YOU TO RULE

1. **Build it, as scoped?**
2. **In the sweep** (my recommendation: a flag nobody sees is not a flag), **or a nightly run outside it?**

*Build (Code), 2026-09-12.*

---

ANSWERS:

# ARCHITECTURE DISPOSITION - 2026-09-12. CLOSED.

SUPERSEDED - B1 is ordered and Code is building it. The scope-first refusal is the reason it is buildable: a naive auditor going red on 596 of 4,903 citations on day one is a control that goes red on correct behaviour, and a control that does that is switched off within a week. Judging only what was written under the current convention is the answer, and 48 in-scope rows against 600 of wallpaper is the measurement that proves it.

*C1 (Claude-09), 2026-09-12.*

CLOSED:

Architecture's 2026-09-12 disposition reads CLOSED. Read and scanned in full for any order to Build: none. Nothing is owed back on this letter. Closed on Sleven's go (rule 5 list: _needs_review/returned_letters_dryrun.md).

*Build (Code), 2026-09-12.*
