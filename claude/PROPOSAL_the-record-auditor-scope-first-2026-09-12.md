# PROPOSAL - the record auditor, scope first (nothing is built)

**Build (Code), 2026-09-12. Written before 03:49 CDT.** The clock read 03:49:12 just after it was filed. The first version said "about 03:50", which was an estimate and not a reading; it is corrected here.

- **Ordered in:** `correspondence/open/build/2026-09-12_memo_build_propose-our-own-record-auditor-scope-first.md`
- **Under:** `claude/RULING_we-write-our-own-auditor-and-tonights-rule-is-what-makes-it-possible-2026-09-12.md`

**Conditions, as ordered:**

- scope before code
- it flags and never fixes
- it never gates a deploy
- its cost is measured before it joins the sweep

**One measurement was taken to size it** (`_needs_review/auditor_measure.py`, read-only). It is below, because it decides the scope.

---

## WHAT THE NAIVE VERSION WOULD DO - MEASURED, AND IT IS WHY THIS WAS NEVER BUILT

**"Every backticked token that looks like a repository path must exist on disk", run over the whole record:**

    documents scanned       1,830   (claude/, docs/, correspondence/, design/, NEXT.md)
    repo-shaped citations   4,903
    pointing at nothing       596   (12%)  - RED on day one

    by kind    455  absent - no file of that name in the indexed folders
               111  moved  - a file of that name exists elsewhere
                           (42 are inbox/ paths: a letter's address before filing)
                30  set aside - the file is in _to_delete/
                 0  named "project store" on the same line (the convention is
                    hours old; nothing written before it follows it)

    by citing  docs/ 429, correspondence/ 143, NEXT.md 14, claude/ 8, design/ 2
    by cited   claude/ 314 (mostly project-store documents in repo shape),
               docs/ 68, inbox/ 42, correspondence/ 33, ...

**596 red on day one is a control that gets switched off within a week.** The outgoing desk wrote that down, and this measurement is its proof.

## WHAT IT ASSERTS

**The scope rule that makes it answerable: judge only what was written UNDER the convention.**

- The convention was ruled 2026-09-12. That is the first line of `claude/FINDING_two-claude-folders-on-two-machines-and-the-receipt-does-not-say-which-2026-09-12.md`.
- **A document is in scope if its own date, in its filename or its Date: line, is on or after 2026-09-12.**
- **The 596 historic flags are reported ONCE as a baseline file, and never again as findings.**

    R1  a repository-path citation that does not resolve
        A citation CLAIMS to be a repository path if it is an absolute path
        under C:\Users\david\citizen-compass\, or a path whose first segment
        is a real top-level folder or root file of this repo.
    R2  a memo that announces a document which does not exist
        R1, applied to letters in correspondence/, flagged separately because
        it is the named shape "a memo believed on the strength of the memo".
    R3  a claude/ citation in repository shape with no file, where the same
        line does not say "project store"
        The two-claude-folders incident exactly. It tells the writer which
        of the two addresses they meant.

## WHAT IT DELIBERATELY DOES NOT ASSERT

- **Whether a DONE-WHEN is satisfied.** `NEXT.md` carries 103 DONE-WHEN lines, and all of them are prose. Deciding one is satisfied is judgement. **A machine that decided it would be the autonomy rule wearing our badge.**
- **Whether a count names its surface.** Also prose. A heuristic would flag half the record and catch the wrong half.
- **What is in the claude.ai project store.** No tool here can see it. The auditor checks citation SHAPE only, never the store's contents.
- **Closed letters without a marker.** The watcher now refuses them at filing, and `_verify_correspondence.py` covers the archive. **A third check would be a second copy of one rule.**
- **Anything written before the convention.** Baseline only.

## THE CASES THAT MUST GO GREEN, WHICH THE NAIVE VERSION TURNS RED

**G1 - a project-store document named as such.** A letter dated 2026-09-12 or later says:

> the Ten Eyes design (project store: `DESIGN_ten-eyes-2026-09-08`)

- **Naive:** red. A claude/-looking name with no file behind it.
- **Ours:** green. The line says "project store", and a bare name is not a repository path.

**G2 - a letter's own address in transit.** A memo cites `inbox/ORDER_x.md`, and the watcher has since filed it to `docs/ORDER_x.md`.

- **Naive:** red.
- **Ours:** green. An `inbox/` path is resolved by filename to where the watcher filed it, which the watcher log records.
- **It is red only if no filing of that name exists.**

**And the case that must STAY red:** a 2026-09-12 memo citing `claude/CIC_rsi-official-ship-roles-2026-09-12.md` before that file reached the disk. That is tonight's four-citations-to-nothing incident, and R1 and R3 both fire on it.

## WHAT IT WRITES, AND WHAT IT NEVER TOUCHES

- **It writes one report:** `_needs_review/record_audit_<date>.md`, plus the one-time baseline.
- **It modifies no document** and deletes nothing.
- **It never gates:** it exits 0 whatever it finds, and says so in its first line.
- **Its rule-12 proof** is planted cases in a temp folder: the three R cases must be flagged, and G1 and G2 must stay green.

## COST - MEASURED

- **The full scan took 7 seconds** (03:47:46 to 03:47:53), over 1,830 files, including a bounded index of the document folders.
- **The current sweep takes about 2,300 to 2,600 s, so this is about 0.3%.**
- **One lesson, recorded:** the first version of the measurement globbed the whole repository once per flag. That was too heavy to run beside a sweep, so I stopped it after about six minutes and made it bounded.

## WHERE IT LIVES - PROPOSED, FOR YOU TO RULE

**`checks/_verify_record_audit.py`**, discovered by the sweep like every `_verify_*`. **It is report-only, so it never turns a sweep red.**

**The alternative is a nightly run outside the sweep.** I recommend the sweep. A flag nobody sees is not a flag, and a sweep receipt is read before every deploy.

**Nothing is built until you say so.**

*Build (Code), 2026-09-12.*
