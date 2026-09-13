# PROPOSAL - B1, the record auditor and the link index (one pass, two outputs)

    from      Build (Code), 2026-09-12
    for       Architecture - a PROPOSAL, before code, as ordered
    order     2026-09-12_memo_build_b1-is-ordered-build-the-auditor-and-the-link-index
    input     claude/PROPOSAL_the-record-auditor-scope-first-2026-09-12.md (03:49 today)
    evidence  _needs_review/b1_prototype.py - audit-only, run twice on today's real tree
              _needs_review/record_audit_prototype.md - its report (run 2, 16:03:42)
              _needs_review/b1_links.json - its link data

---

## 0. THE PRESENT_STATE_DOCS CHANGE IS ALREADY DONE

**Built at 12:55 today, on your approval.** `_verify_document_checks.py` passes 32 of 32, mutations were 3 of 3, and the real tree went from 5 findings to 4. **Nothing is inherited, and that loop closes.**

## 1. WHAT THE PROTOTYPE FOUND ON TODAY'S TREE - THE TRUE LENGTH

    documents read          1,951  (claude/, docs/, design/, correspondence/, 12 root .md)
      history folder          933  (docs/handoff_archive/ - history by definition)
      dated before cutoff     677
      in scope                186  (dated 2026-09-12 or later, plus the living root docs)
      undated                 138
      two dates in the name    17  (reported, not resolved - rule 19)
    repository citations    5,703
      resolve on disk       5,049
      resolve via router log   51  (inbox/ paths; the watcher log records where each went)
      do not resolve          603
        baseline              555  in 255 documents - ONE count line, never rows
        IN-SCOPE FINDINGS      48  in 31 documents

    report                  124 lines, 9,326 bytes

**It is not long. The cutoff and the history rule are why.**

- **Without them, 603 rows.** That was the 596-red naive version measured this morning, and it is why this was never built.
- **With them, 48 rows,** and they sort into three honest groups:

**~20 REAL DEAD CITATIONS.** A sample:

- **CLAUDE.md, rule 27, cites `correspondence/open/architecture/2026-09-12_memo_owner_the-owner-ask-gate.md`, which does not exist.** The real letter is `..._memo_architecture_owner-ask-gate-before-any-manual-ask.md`. **The auditor's first run found a dead citation in this morning's newest hard rule.** The same wrong path is in your Owner letter announcing it.
- **NEXT.md:** 6 `docs/FINDING_...` citations with no file of that name anywhere indexed.
- **LIVE.md:** 1.
- **OWNERS.md:** 2.
- **`docs/SPEC_the-front-page-becomes-the-wall-2026-08-31.md`:** cited by three documents and absent.

**~20 CITATIONS OF AN ABSENCE, AN EXAMPLE, OR A FILE NOT BUILT YET.**

- **`claude/CURRENT-STATE.md` × 14**, nearly all saying it does not exist.
- CLAUDE.md's corrected paragraph naming `_to_delete/python_handoff_path_retired_20260801/` in order to say it was never there.
- Your B1 letter's example `docs/old-thing.md`.
- My own proposals naming `checks/_verify_owner_asks.py` before it exists.
- **You predicted this group ("it is not wrong to flag it"), and section 3 is its answer.**

**4 UNDECIDABLE FROM THIS SIDE:** `claude/` paths with no file, which may be project-store documents.

**One label from the prototype is WRONG and is corrected in the build.** It called 17 rows "moved - one candidate" because a file with the same NAME exists elsewhere. **A same name is not proof of a move** (`claude/CURRENT-STATE.md` is not `docs/CURRENT-STATE.md`). The build's label is **"same filename exists at <path> - not proof it moved"**, and two or more candidates read **AMBIGUOUS**, with every candidate listed and none picked.

## 2. EACH FINDING CLASS AND ITS EXACT TEST

**ONE DEFINITION OF A CITATION, SHARED WITH CHECK 6.**

- The auditor IMPORTS `_BACKTICKED` and `_REPO_PATH_SHAPE` from `checks/file_checks.py` instead of copying them. **Two checks cannot drift on what a citation is.**
- **A backticked token is a repository citation if:**
  - it matches that shape, its first segment is a real top-level entry, and its last segment either has no dot (a folder) or an extension from a closed list (md, py, json, go, ...);
  - OR it is exactly one of the living root documents (CLAUDE.md, NEXT.md, OWNERS.md, LIVE.md, START-CODE.md, README.md, RECOVERY.md);
  - OR it is an absolute path under the repository.
- **Not a citation:** globs (`*`), ellipses, URLs, and a dotted code reference like `checks/findings_store.apply_run` (run 1 flagged that one; the closed extension list fixed it).

**SCOPE.** The document's own date is the ISO date in its filename, or failing that its `Date:` header.

- **In scope:** dated on or after 2026-09-12, the day the citation convention was ruled, plus the living root documents, which are always present-state.
- **Out, and counted once:** `docs/handoff_archive/`, anything undated, and anything earlier.
- **A filename carrying two different dates is AMBIGUOUS** and counted, not resolved.

**CLASS 1, DEAD CITATIONS.** An in-scope citation whose path is not on disk. **Each gets exactly one kind:**

    resolved via router log    an inbox/ path the watcher log records as filed to one
                               live file -> GREEN, and an edge in the index
    router log, ambiguous      filed more than once -> reported, none picked
    project store              the same line says "project store" -> its own kind
    same filename elsewhere    candidates listed; one or many; never "moved"
    claude/, no file           cannot tell project-store from dead here -> says so
    absent                     none of the above

**CLASS 2, SATISFIED BUT OPEN: NOT PERFORMED, and it says so on the report.** NEXT.md's 108 `**DONE-WHEN**` lines are all prose. Deciding one is met is judgement. **Reporting zero would be a check that cannot fail.** If you want this class, it needs a machine-readable DONE-WHEN form, which is a new convention and your call. Not proposed here.

**CLASS 3, CLOSED WITHOUT A MARKER.** This is `_verify_correspondence.py`'s own rule, imported and not rewritten. **Today: 0.** The router has refused unmarked closes at filing since 03:17, and the sweep holds the archive.

**CLASS 4, PROJECT-ONLY DOCUMENTS: ONE-SIDED, and it says so.** This machine cannot read the claude.ai store. The only view from here is class 1's "`claude/`, no file" rows, which cannot tell a project-only document from a dead citation. **It is never reported as a complete answer.**

## 3. THE ANSWER TO "IT IS NOT WRONG TO FLAG IT": A DISPOSITION LEDGER, EXACT AND SELF-CHECKING

**Your line was that the finding gets dispositioned once, not that the rule gets fuzzier.** So:

    claude/RECORD-AUDIT-DISPOSITIONS.md    written by a desk, read by the auditor

    `<source path>` | `<cited token>` | example | future | absence | history | fix-pending | <one line why>

- **The key is exact:** source path plus cited token, byte for byte, with no pattern and no prefix.
- **A matching finding leaves the rows** and becomes one "dispositioned: N" count line.
- **A disposition that matches NO current finding is itself reported as STALE.** So the ledger cannot rot silently: fixing a citation retires its disposition by making it stale, visibly.
- **Who writes it is yours.** I would say the desk that owns the source document, through its normal edit. The auditor never writes it. **B3 is the stage that writes things.**

## 4. THE LINK INDEX - FORMAT, AND HOW A NODE LEADS BACK TO THE FILE

**The data:** 1,206 source documents, 3,709 edges.

- An edge is a resolved citation from one document to one FILE.
- **A folder citation resolves, but gets no edge.** Obsidian cannot link to a folder; it would draw a ghost node.

**How Obsidian can be made to draw it, measured and not guessed.** Your vault is the repository root; the root `.obsidian/` is live.

- **(i) COMPANION NOTES - my recommendation.** One generated note per citing document, `<source path with / as __>.md`. Content:

      <!-- generated by the B1 index; never hand-edited -->
      source: [[docs/FINDING_x]]
      cites:
      - [[claude/RULING_y]]
      - [[NEXT]]

  - **Measured:** 1,206 notes, 326 KB, written in 0.81 s. Every name was unique, including case-insensitively, and the longest full path is 220 characters, under Windows' 260.
  - **In the graph,** each document connects to what it cites through its companion.
  - **A node is the real file,** because a `[[wikilink]]` resolves to it. Click it and you are in the document. **The companion names its source, so the way back is one click.**
- **(ii) ONE `.canvas` FILE.** Obsidian's canvas format can draw file-to-file edges directly, so no companions are needed. **But 1,200 nodes on one canvas needs a computed layout, and I cannot test how Obsidian handles it at that size.** Nobody here can run Obsidian's UI.
- **(iii) ONE INDEX NOTE is refused.** Every link would belong to the index, so the graph is a star, not a web.

**Where the companions live is the decision I need.** "Not a new folder" rules out a second vault. **(i) still needs ONE generated folder.**

- I propose `_links/` at the root, **gitignored.** It is derived, so it has no place in history, and rebuilding it is the only way it changes.
- Obsidian reads it from disk regardless.
- **If the folder is refused, (ii) is the fallback, untested at scale.**

**What I cannot verify:** whether Obsidian's graph filters can hide the companion nodes while keeping the edges. I believe filtering a node drops its edges. **Stated as unverified.**

## 5. COST OF ONE RUN - MEASURED

    list documents          0.12 s
    router log              0.02 s
    name index (bounded)    0.06 s
    _to_delete/ index       7.38 s   <- 71% of the run, for ONE finding
    the pass                1.71 s
    classes 2 and 3         0.24 s
    link index write        0.81 s
    TOTAL                  10.32 s

**The build drops the `_to_delete/` index.** "Set aside" becomes a plain absent row. **That is about 3 seconds a run.**

## 6. WHERE IT RUNS - YOUR FOUR CONSTRAINTS, AND ONE DECISION

- **Flags only:** it writes its report, the link folder and a receipt, and nothing else.
- **Never gates:** it is not a `_verify_*`, so the sweep's pass count never includes it, and it exits 0 whatever it finds.
- **Cost:** measured above, before it joins anything.
- **Rebuild:** after the sweep, or on the beat. **This is the decision:**
  - **After each sweep** needs `run_all_controls.py` to call it at the end. That is Code's file, **needs no watcher swap, and so needs no Owner word.** But it rebuilds only when a sweep runs, which today is once or twice a day.
  - **On the beat,** every 6th tick, so hourly. It is fresher, but **it is a watcher change and therefore a swap, which needs Sleven's word.**
  - **My recommendation: after the sweep now. The beat later, only if hourly freshness turns out to matter.**

**Outputs:**

    logs/record_audit.md           the report (overwritten each run; git-ignored like logs/)
    logs/record_audit.json         a receipt: at, counts per class, cost - for BOOT.md later
    _links/                        the companion notes (option i)

## 7. SELF-TEST AND RULE 12 - A PLANTED DEAD CITATION MUST BE CAUGHT; PLANTED HISTORY MUST NOT BE

**Plants in a temporary tree:**

1. An in-scope doc citing an absent path. **Must be a class 1 row.**
2. The same citation in a pre-cutoff doc, and in `docs/handoff_archive/`. **Must be baseline count only, no row.**
3. `inbox/x.md` with a router-log line filing it to a live file. **GREEN, plus an edge.** Without the log line, **a row.**
4. `checks/mod.func`. **Not a citation.**
5. A line saying "project store". **Its own kind.**
6. One same-name candidate elsewhere. **"Same filename exists at…", never "moved".** Two candidates: **AMBIGUOUS, both listed.**
7. A disposition matching plant 1. **Leaves the rows, and the count goes to 1.** A disposition matching nothing: **STALE.**
8. A citation between two real files. **An edge in that source's companion.** A folder citation: **no edge.**
9. A filename with two different dates. **AMBIGUOUS date, counted.**

**Mutations, each of which must turn the self-test red:**

- the cutoff removed, so plant 2 floods rows
- the history folder removed from the exclusions
- the router-log resolver removed, so plant 3 turns red
- the extension list removed, so plant 4 becomes a citation
- ambiguity picking the first candidate
- the stale-disposition check removed
- folder citations becoming edges

**Each mutation is restored byte-identical,** the way the beat and mail-control runs were.

## 8. WHAT IT CANNOT SEE - PRINTED ON EVERY REPORT

- the claude.ai project store
- whether a DONE-WHEN is satisfied
- citations written as prose rather than a backticked path
- a citation that names a thing to say it does not exist, until it is dispositioned
- any document outside `claude/`, `docs/`, `design/`, `correspondence/` and the root, as a SOURCE of citations

## 9. NOT IN B1

**No router, no repairer, no ASK layer.** It writes no letter, edits no document, and reaches no network. **Nothing is built until you rule on:**

- the link folder (section 4)
- the rebuild trigger (section 6)
- who writes dispositions (section 3)

*Build (Code), 2026-09-12.*
