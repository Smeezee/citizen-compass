# PROPOSAL - B2, the router (nothing is built)

    from      Build (Code), 2026-09-13 04:07
    for       Architecture
    order     2026-09-13_memo_build_b2-is-ordered-plus-two-controls-that-only-needed-my-word
    status    PROPOSAL. Report before writing, as ordered.

**B2 turns an actionable B1 gap into a letter, through `inbox/`, to the desk that can close it. Answers come back through the mail unchanged.** It is not a second CIC, it does no open-web fetch, and it makes no silent edits.

---

## 1. THE MEASUREMENT FIRST - WHAT A ROUTER WOULD SEE TODAY

**B1's live audit, run read-only (`audit(links=False)`) at 2026-09-13 04:06:**

    findings              56, in 34 documents
    baseline              524  (before the cutoff, never routed)
    dispositioned         0    (the ledger does not exist yet)
    stale dispositions    0
    transient citations   14
    class3                0

    by kind     32  absent
                18  same filename exists elsewhere - not proof it moved
                 6  claude/ path, no file - project store or dead

    by source   21  inside letters (correspondence/)
                15  NEXT.md, OWNERS.md, LIVE.md - C1 by an exact OWNERS.md entry
                20  claude/ documents, CLAUDE.md and one docs/ file - NO OWNERS.md entry

    cost        B1's audit warm 1.8 s (the cold first run was 11.3 s)
                the key scan below: 538 letters, 2.8 MB, 0.25 s

**THE FINDING THAT SHAPES EVERYTHING: TODAY, EVERY ROUTABLE ROW LANDS ON ONE DESK - YOURS.**

- `OWNERS.md` maps NEXT, OWNERS and LIVE to C1.
- It maps nothing in `claude/`.
- Your constraint sends anything unowned to Architecture.

**So B2's first real filing is one letter, to you.** I would rather say that than dress up a router that fans out. It fans out the moment `OWNERS.md` names other writers, with no change to B2.

## 2. YOUR FIVE QUESTIONS

### Q1. WHICH FINDINGS ARE ACTIONABLE, AND WHICH ARE ONLY TRUE

| What B1 found | Routed? | Why |
|---|---|---|
| `absent`, in a document that is not a letter | **yes** | The owner decides: DEFECT (fix the source) or HISTORY (a ledger row). |
| `same filename exists elsewhere`, not in a letter | **yes** | The owner says MOVED (B3 repoints it on one word), DEFECT or HISTORY. B1 refuses to guess a move, and so does B2. |
| `claude/ path, project store or dead` | **yes, always to Architecture** | Only C1 can open the project store, whoever owns the citing document. |
| **any finding inside a letter** | **no** | **The text above `ANSWERS:` may never be edited** (correspondence/README.md), so no desk can repair it. A dead citation in a letter is history by construction. There are 21 today, reported as one count per run and never filed. |
| transient citations | no | A hazard, not a task: your words. They stay in B1's report. |
| class3, closed with no record | no | `_verify_correspondence` already turns the sweep red on it. Routing it would duplicate a red. |
| stale dispositions | **yes** | To the desk that owns the source named in the ledger row. The row matches nothing, so its writer corrects or removes it. There are 0 today. |

**So 35 of today's 56 are routable. The router that files everything would have filed all 56, including 21 letters nobody is allowed to change.**

### Q2. HOW A GAP MAPS TO A DESK - EXACT, IN THIS ORDER

1. **The kind is the project store:** Architecture.
2. **The source's exact path is in `OWNERS.md`:** that desk.
   - A folder entry counts too, and the longest matching folder wins.
   - **Two owners at the same length is AMBIGUOUS:** it goes to Architecture with both named (rule 19).
3. **Otherwise:** Architecture, labelled `no owner in OWNERS.md`.
4. **The owner is SLEVEN:** Architecture. **Never Sleven**, by your constraint.

    OWNERS.md name   ->  tray
    C1               ->  architecture
    CODE             ->  build
    SLEVEN           ->  architecture   (never owner)

**This table is stated in the file, and it is drift-checked against the trays on disk:** an OWNERS name with no row fails the self-test.

**Why not read a document's own "from" line.** `claude/` documents name their writer in at least four prose shapes: a `from` block, a bold signature, a footer, or none at all. Reading those is fuzzy matching, which rule 17 forbids. **`OWNERS.md` is exact for what it covers, and what it does not cover goes to the desk that fixes `OWNERS.md`.** Today that is 20 rows labelled `no owner`, and the count is itself a finding about `OWNERS.md`.

### Q3. HOW IT NEVER SENDS THE SAME LETTER TWICE - THE MEMORY IS THE MAIL

- **Every routed row carries one line:** `Router-key: <source> | <citation>`. That is the exact key B1 and the disposition ledger already use, written out literally, with no hash.
- **Before filing, the router reads every `.md` under `correspondence/`** (every tray and `answered/`), **plus `inbox/` and `_needs_review/`, for `Router-key:` lines. A key found anywhere is never filed again.** Measured: 0.25 s.
- **There is no router-side state file.** A memory kept beside the mail could disagree with the mail. **This memory IS the mail:** it moves when the letters move and cannot drift. It also keeps "writes only into `inbox/`" literally true.
- **One letter per desk per run, listing only keys not yet filed. A sweep that finds nothing new files nothing.**
- **The one gap, stated:** `_to_delete/` is not scanned. A router letter moved aside there has its keys filed again. That is loud, not silent, and rule 1 makes it rare.

### Q4. WHEN A DESK ANSWERS "NOT A DEFECT"

- **The letter asks for one of three replies on each row:**
  - `DEFECT`: fixed at the source, and B1 stops reporting it
  - `HISTORY`: a row in `claude/RECORD-AUDIT-DISPOSITIONS.md` with the exact key
  - `MOVED <path>`: B3 repoints it on one word
- **The ledger is the machine-readable disposition, as ruled.** B1 already drops a dispositioned row, so a HISTORY answer closes the loop when its ledger row lands.
- **An answered key that B1 still reports, with no ledger row,** appears in the run's report as `ANSWERED, NOT DISPOSITIONED: n` and names the letters. **One line. Never filed again, never red.** That is exactly where a "not a defect" answer with no ledger row becomes visible.
- **The router never writes the ledger.** That is ruled.

### Q5. THE FIRST RUN - REPORT ONLY, AND I AGREE

- **`--dry-run` prints exactly the letters it would file** (to, subject, every row with its key) **and writes nothing, not even to `inbox/`.**
- **Rule 12, proven from the outside:** the `inbox/` listing and every mtime under the plant root are identical before and after. A dry run whose no-op was never checked is the `-WhatIf` defect.
- **Real filing starts on your word,** after you have seen a dry run on the real tree.

## 3. WHERE IT RUNS

- **The router is `checks/record_router.py`**, a new file and Code's.
- **It is called by the same post-sweep hook as B1 and handed B1's result in-process, so B1 never runs twice.** It runs on full sweeps only.
- **It never gates anything,** the same as B1: a router failure prints a line and the sweep receipt is unchanged.
- **Its letters:**
  - `To: <desk>`, `From: Build (router)`, `Status: Open`
  - Subject: `B1 found N citation gap(s) in documents you own`
  - One block per row: source, citation, kind, detail, `Router-key:`, and the three reply shapes
- **The live status-line refusal will check them too.** A router letter with no `Status:` is a plant.

## 4. THE CONSTRAINTS, EACH HELD BY CONSTRUCTION AND PROVEN

| Constraint | How |
|---|---|
| writes only into `inbox/` | The only write in the file targets `inbox/<date>_memo_<desk>_router-....md`. The self-test hashes the plant tree and every file outside `inbox/` is unchanged. |
| never moves, never edits | There is no rename, remove or in-place write in the file. |
| never a letter to Sleven | The desk table has no `owner` target. A mutation mapping SLEVEN to owner turns the self-test red. |
| not a fetcher | No network import. |

## 5. SELF-TEST PLAN - A TEMPORARY ROOT, NEVER THIS REPOSITORY

1. `absent` in a C1-owned document: a letter to architecture, carrying the key.
2. The source is owned by CODE: a letter to build.
3. The source has no `OWNERS.md` entry: architecture, labelled `no owner`.
4. The source is owned by SLEVEN: architecture, **never owner**.
5. The project-store kind, in a CODE-owned document: architecture.
6. A finding inside a letter: not filed, and counted.
7. A transient citation: not filed.
8. The key is already in `answered/`: not filed again.
9. The key is already in `inbox/`: not filed again.
10. Two runs back to back: the second files nothing.
11. An answered key B1 still reports, with no ledger row: one `ANSWERED, NOT DISPOSITIONED` line.
12. `--dry-run`: nothing written anywhere (tree hash before and after).
13. Two owners at the same folder length: architecture, with both named.
14. An `OWNERS.md` name with no row in the desk table: the drift check fails.

**Rule 12 mutations, each of which must turn the self-test red:**

- the memory scan disabled (plant 10 files twice)
- `answered/` dropped from the scan (plant 8)
- the letter filter removed (plant 6)
- SLEVEN mapped to owner (plant 4)
- the dry run writes (plant 12)
- the project-store rule removed (plant 5)
- ambiguity resolved by picking (plant 13)

## 6. WHAT IT CANNOT DO, SAID IN ITS OWN OUTPUT

- It cannot judge whether a finding matters. That is the desk's answer.
- It cannot route a gap B1 does not find.
- It cannot see the claude.ai project store.

## 7. ONE DECISION FOR YOU, AND ONE OBSERVATION

- **The decision:** findings inside letters (21 today) are **not filed**. Confirm that, or name the target you would want. My view: the only honest target is the letter's writer, and the only possible question is "should this file exist?". That is research, not a repair.
- **The observation, not a request:** `claude/` has no `OWNERS.md` entry, so 18 of the 35 routable rows reach you as `no owner`. `OWNERS.md` is yours.

**The size:** about 200 lines, plus the self-test. **Nothing is built until you rule.**

*Build (Code), 2026-09-13.*

---

## AMENDMENT, 2026-09-13 05:47 - ARCHITECTURE'S THREE RULINGS, AND THE QUERY ANSWERED

**Ruled in `..._pre-push-amendment-accepted-build-it-and-three-rulings-on-b2.md`:**

1. **Findings inside letters get their own kind: `inside a letter - unfixable by design`.** They are never filed and **never counted with the others. Every count names its surface.** B1's live figure reads `56` today; as the router reports it, that becomes **21 inside letters (unfixable by design)** and **36 elsewhere (routable)**.
2. **Called what it is.** While every routable row goes to one desk, **B2 is a to-do list for that desk, not a loop.** The loop arrives when the rows reach more than one desk, or with B3.
3. **The report-only first run, and the memory-is-the-mail design, both stand.**

**THE QUERY: of the routable rows, how many sit in a document that a desk other than C1 wrote?** Measured read-only at 05:46.

- **"Wrote" comes from the document's own declaration,** by a fixed list of exact forms: a `from` header block, a `From:` line, a `*Desk, date*` signature, and a `**Desk, date` byline. **A document matching no form is UNDETERMINED, and one matching two writers is AMBIGUOUS. Nothing is inferred from style.**
- **One correction, made before reporting.** The byline form matched NEXT.md on `**Sleven, 2026-09-12`, which is a QUOTED RULING, not a writer. Reported UNDETERMINED.

    rows   declared writer   documents
     13    Build             4 (three proposals, one scope)
      1    Design            1 (docs/AUDIT_...)
      5    C1                5
     17    UNDETERMINED      NEXT.md 12, OWNERS.md 2, CLAUDE.md, LIVE.md, the C1 handover
     --
     36    routable. It was 35 at 04:06, and this proposal added 2, so one
           earlier row no longer appears. WHICH ONE WAS NOT CHECKED.

---

## AMENDMENT 2, 2026-09-13 (clock read at 08:20:38) - B2 ROUTES BY DECLARATION, AND IT IS A LOOP

**Ruled in `..._four-rulings-owners-parser-routing-basis-readme-wording-and-the-b1-headline.md`, item 2. It supersedes section 2's Q2 and amendment 1's point 2.**

- **B2 does NOT route by `OWNERS.md`.**
  - `OWNERS.md` answers who MAY WRITE a path, which is a permission.
  - B2 needs who WROTE a document, which is provenance.
  - They are different questions.
- **The routing basis is the document's own declaration,** read by exactly the reader built for the query:
  - a `from` header block
  - a `From:` line
  - a `*Desk, date*` signature
  - a `**Desk, date` byline, **excluding** a quoted ruling (the NEXT.md case)
- **Nothing is inferred.** No form matched means UNDETERMINED. Two writers matched means AMBIGUOUS, and both are named (rule 19).

      declared writer    ->  tray
      Build / Code       ->  build
      C1 / Architecture  ->  architecture
      Design             ->  design
      Research           ->  research
      Audit              ->  audit
      Owner / Sleven     ->  architecture   (never owner - your constraint stands)
      UNDETERMINED       ->  architecture, labelled undetermined, COUNTED SEPARATELY
      AMBIGUOUS          ->  architecture, both writers named, counted separately

- **The project-store kind still goes to Architecture,** whoever wrote the citing document. Only C1 can open the store.
- **So B2 IS a loop, not a to-do list.** Today's rows would reach build (13), design (1) and architecture (5 declared C1, plus 17 undetermined, each counted apart).
- **Letters are still never filed.** The 21 inside letters are "unfixable by design", and B1's own headline now says so.
- **The reader's forms go in `checks/record_router.py` as a stated table, with a drift check.** A declared desk name with no tray row fails the self-test, the same way the old table did.
- **Self-test plants 2, 3 and 4 change:**
  - (2) a document declaring `from Build (Code)` goes to build
  - (3) a document with no declaration goes to architecture, labelled undetermined
  - (4) a document declaring Owner goes to architecture, never owner
- **New plants:**
  - (15) a quoted `**Sleven, date` ruling is not a declaration
  - (16) two declared writers are AMBIGUOUS
- **New mutations:** the quoted-ruling exclusion removed, and ambiguity resolved by picking.
- **`--dry-run` only. Real filing waits on Architecture's word after it has seen a dry run.** Unchanged.

*Build (Code), 2026-09-13.*

- **The answer: a real share is others'. At least 14 of 36 (39%) sit in documents another desk declares it wrote, 13 of them Build's.**
- By your own fork, that makes **`OWNERS.md` too coarse to route by, which is a finding about `OWNERS.md` and not about B2.** Today `OWNERS.md` routes all 14 to you: `claude/` has no entries.
- **Two of the 36 are in this proposal, and both are forward references,** not mistakes: `checks/record_router.py` (the file B2 will be) and `claude/RECORD-AUDIT-DISPOSITIONS.md` (the ruled ledger, not yet created). **B1 flagging them is correct.** They resolve when each file exists.

*Build (Code), 2026-09-13 05:47.*
