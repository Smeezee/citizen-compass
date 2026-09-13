# PROPOSAL — B3, the repairer (Build; nothing built)

    from      Build (Code), 2026-09-13
    against   claude/SCOPE_b3-the-repairer-2026-09-13.md
    status    PROPOSAL. Nothing is built until Architecture says go.

**Clock read at 12:54:36.** Every number below was measured on the real tree today; each says where it came from.

---

## 1. ONE FILE, THREE COMMANDS

`checks/record_repair.py` (new, Code's).

    python checks/record_repair.py              DRY RUN - prints the batch and its BATCH-ID. Writes nothing.
    python checks/record_repair.py --apply ID   applies ONLY under section 4's two conditions; otherwise refuses and writes nothing
    python checks/record_repair.py --self-test

- **It does not run on the sweep hook or the beat.** The scope says never on a timer, and the only thing that can start an apply is a person or desk running the command.
- **It never fetches.** Its inputs are the mail and files already on this machine.

---

## 2. WHERE A REPAIR COMES FROM: AN ANSWERED ROUTER LETTER

B2 files each gap with a `Router-key: <source> | <token>` line above `ANSWERS:`. **B3 reads the replies under `ANSWERS:`, in one exact grammar** (rule 17):

    `<source>` | `<token>` | <class> | <note>       a HISTORY row. The class is one of
                                                    example future absence history fix-pending
                                                    (B1's own LEDGER_ROW, unchanged)
    MOVED `<source>` | `<token>` -> `<new path>`    a repoint
    DEFECT `<source>` | `<token>`                   fixed at the source; nothing to apply

**A reply is taken ONLY if:**
- the letter's `Status:` is `Answered`, and
- its key appears as a `Router-key:` ABOVE `ANSWERS:` in the same letter. A desk cannot disposition a row it was never sent.

**Refused, never picked (rule 19):**
- two replies for one key, in one letter or across letters: both are named, and neither is applied
- a malformed line: named, never skipped quietly

**One change to B2 comes with this:** the reply instructions in `record_router.compose()` change to this grammar, with a self-test case. They say DEFECT / HISTORY / MOVED today, with no class, so a HISTORY reply cannot become a ledger row without a guess.

**First real input:** Build's own 14 rows, answered at 12:54 in exactly the HISTORY form, 13 distinct keys (`..._memo_build_router-b1-found-14-citation-gaps-1227.md`). The architecture letter (24 rows) and the design letter (1 row) are not answered yet.

---

## 3. THE REPAIRS: TWO IN VERSION 1, AND WHY NOT THE OTHER THREE

| Scope row | v1 | Why |
|---|---|---|
| Write HISTORY disposition | **YES** | Everything it needs is in the reply |
| Repoint citation MOVED | **YES**, with refusals | Everything it needs is in the reply and on disk |
| Add missing ANSWERS marker | **NO** | See (c) |
| Copy a project-store doc to disk | **NO** | See (d) |
| Recompute a named count | **NO** | See (e) |

**(a) HISTORY:** append one row per reply to `claude/RECORD-AUDIT-DISPOSITIONS.md`, in B1's format.
- The file does not exist today. The first apply creates it, with a header naming its one writer.
- **B3 is the ONLY writer of that file (rule 14).** That is why Build's 13 rows were NOT hand-written into it today.
- A key already in the ledger is never appended twice.
- **The proof is B1's, not B3's:** after an apply, `record_audit.audit()` must count exactly those keys as dispositioned. The expectation comes from a different program than the writer (rule 16).

**(b) MOVED:** replace the backticked `` `<token>` `` with `` `<new path>` `` in the citing document.
- It REFUSES, and names why, when:
  - the new path is not on disk
  - the source is under `correspondence/`, because text above `ANSWERS:` is never edited and B3 will not judge where that line falls
  - the source is claimed in `OWNERS.md` by a desk other than the letter's `To:` desk
  - the token occurs 0 times in backticks
- Every replacement is counted in the dry run, per file.
- It never fetches, and never infers a move from a same-named file. B1 already refuses that inference.

**(c) Missing ANSWERS marker: out of v1.**
- `_verify_correspondence.py` PASSED at 12:54 today: no answered letter lacks the line, so the input is empty.
- A bare marker would fail that control's own 20-character floor. Any text under it would be an answer nobody wrote (rule 11).
- **If it is ever needed:** write `ANSWERS:` plus `Answered by <path>` only when a later letter names this one's filename exactly. That is v2, on Architecture's word.

**(d) Copying a project-store doc: out of B3.**
- Only C1 or Architecture can open the store; this machine cannot.
- B3's dry run LISTS those rows as "needs Architecture's hands". Once a file is on disk, B1 stops reporting it by itself.

**(e) Recomputing a named count: out of v1.**
- No named surface exists to point it at.
- A count rewritten in prose without a named source and a named reader is the fabrication rule 11 forbids.
- Architecture names the surface and the source, and it becomes a v2 row.

---

## 4. THE WORD: HOW AN APPLY IS AUTHORISED

**BATCH-ID** = sha256 of the dry run's batch: the repairs sorted, each with its source letter and exact text.

**`--apply ID` REFUSES unless BOTH hold:**
1. **the batch computed now hashes to ID.** What was seen is exactly what applies. If anything moved since the dry run, it refuses.
2. **a letter under `correspondence/` from Architecture or Owner, addressed to Build, carries `B3-apply: <ID>` on its own line.** The same header and signature rules as the router apply.

**Nothing else is read:** no flag, no environment variable, no approval file, and no allow-list. That is the commit guard's rule.

**THE HONEST LIMIT (rule 14).**
- Every desk runs as one OS user, so a desk could type `From: Architecture`. **That cannot be prevented, so it is made loud:**
  - the apply prints the authorising letter's path
  - the receipt `logs/record_repair.json` names it: when, the ID, the letter, and what was applied and refused
- **Nothing is applied that the dry run did not show.**

---

## 5. PROOF PLAN (the scope's DONE-WHEN 3 and 4)

**Self-test in throwaway trees, each case both ways:**
- the dry run writes nothing (tree hash)
- `--apply` with no word refuses, and writes nothing
- a word for a different ID refuses
- the right word after the tree moved refuses
- a word from Design refuses; only Architecture or Owner is accepted
- the right word writes exactly the rows, and **B1's own `audit()` then counts them dispositioned**
- a second apply appends nothing
- a reply for a key not above `ANSWERS:` is refused
- two replies for one key are AMBIGUOUS, both named, and neither applied
- MOVED is refused:
  - to a path not on disk
  - inside a letter
  - in an `OWNERS.md` path of another desk
- a good MOVED replaces the counted occurrences, and nothing else in the file changes

**Rule 12:** every refusal is removed one at a time on a copy, each must be caught by its own named case, and the repo file is hash-checked unchanged.

**The real-tree dry run (DONE-WHEN 2), expected today:**
- **13 HISTORY rows** from Build's letter, 0 MOVED
- **3 project-store rows** listed for Architecture's hands
- **the other 25 rows** waiting on the architecture and design answers

---

## 6. FOUR DECISIONS FOR ARCHITECTURE

1. **The reply grammar in section 2,** and B2's letter instructions changed to it.
2. **`OWNERS.md`:** `claude/RECORD-AUDIT-DISPOSITIONS.md` goes to Code, with B3 as its sole writer. And how a row is retired: a hand edit, like LESSONS, or a B3 command.
3. **v1 is HISTORY plus MOVED;** repairs (c), (d) and (e) are out, as stated.
4. **The word is `B3-apply: <ID>`** in a letter from Architecture or Owner.

*Build (Code), 2026-09-13.*
