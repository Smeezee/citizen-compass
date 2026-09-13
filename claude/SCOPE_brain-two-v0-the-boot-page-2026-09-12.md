# SCOPE - brain two v0, the regenerating boot page (a scope, not a build)

**Build (Code), 2026-09-12. The prototype run was at 05:29:37 CDT.**

- **Ordered in:** `correspondence/open/build/2026-09-12_memo_build_brain-two-v0-the-regenerating-boot-page.md`
- **Under:** `claude/RULING_brain-two-ships-the-digest-first-and-not-on-a-strangers-vault-2026-09-12.md`

**Nothing is built.**

- A throwaway prototype, `_needs_review/brain2_v0_prototype.py`, generated ONE example page to a scratch path, `_needs_review/brain2_v0_example.md`. That way its real length is measured, as asked.
- **It reads the tree and writes that one file. It edits nothing it reads.**
- **Nothing from `NulightJens/ai-second-brain-skills` was used.**

---

## THE MEASUREMENT THAT DECIDES THE DESIGN

    the example page        115 lines, 6,756 bytes, ~1,700 tokens
    generated in            0.15 s, reading 7 files (NEXT.md 272,897 bytes among them)
    the boot read it replaces  ~115,000 tokens  (claude/FINDING_the-automation-is-not-
                               the-expense-the-boot-read-is-2026-09-12.md)
    ratio                   about 1.5% of the read

**One regeneration costs almost nothing.** It is one short read of seven files. **So v0 can regenerate on every watcher cycle and never need to be clever about when.** That is the property the rest of this scope leans on.

## 1. THE SECTIONS - AS THE EXAMPLE HAS THEM

    STAMP              generated at, by what, and every input file with its size
                       and modification time - at the TOP, not a footer
    WHAT THE PROJECT IS   two lines, pointing at CLAUDE.md
    WHAT IS LIVE       public site version + its own verification date (LIVE.md);
                       last sweep receipt; last build receipt; testing-site version
                       (NOT RECORDED ON DISK - see section 3)
    WHAT IS OPEN - LETTERS   per desk: open count + newest open letter and its age
    WHAT IS OPEN - THE QUEUE NEXT.md items in their own words, unjudged
    RECENT RULINGS / DECISIONS / FINDINGS   newest first, dated, by path
    WHO OWNS WHAT      OWNERS.md's desk sections, as pointers
    DISAGREEMENTS      every conflict the generator detects, both sources named
    WHAT THIS PAGE CANNOT KNOW   stated on the page, every time
    DEEP FILES         pointers, with sizes, into everything the page summarises

**Tonight's example is 115 lines, well under the 200 target.** It holds all nine sections.

## 2a. AMENDED AFTER SLEVEN'S RULING: THE GENERATED PAGE IS THE STATE

**Architecture's amendment** (`2026-09-12_memo_build_the-open-question-in-the-v0-scope-is-answered`) says Sleven ruled that the generated page is the canonical current page. **That changes my recommendation below, from A to a dedicated file.**

**If the page IS the state, it cannot live inside `LATEST_HANDOFF.md`.** That file is 49,101 bytes, because of its append-only update log, so a desk reading "the state" would pay about 12,000 tokens to reach 115 lines.

**RECOMMENDED PATH: `STATE.md` at the repository root.**

- **It is short and generated.** Its one writer is the watcher. It has no hand edits, and **a hand edit is a bug report against the generator.**
- **The handoff's known-wrong "CURRENT STATE (auto)" section becomes one line:** "The current state is `STATE.md`, generated <time>." That leaves one current page, one writer, and the wrong figures gone.
- **`docs/CURRENT-STATE.md` keeps its owner and its history.** It becomes a deep file that `STATE.md` points into, and it stays in place with nothing lost.
- **`STATE.md` does not collide with `docs/CURRENT-STATE.md`,** in path or in name.

**The watcher change is a swap, which needs Sleven's word, as before.** Until the page is proven, the two current pages coexist, exactly as ruled.

## 2b. EVERY BOOT INSTRUCTION THAT SENDS A DESK TO CURRENT-STATE OR NEXT - LISTED, NOT EDITED

**These are instructions to read the file:**

    claude/PROMPT_boot-c1-the-merged-desk-2026-09-12.md   :165, :248-250  read order
                                                        3 CURRENT-STATE, 4 NEXT
    claude/PROMPT_boot-a-new-c1.md                       :223, :281-282, :290
    claude/HANDOVER_the-old-c1-last-report-2026-09-12.md :126 "Read docs/CURRENT-STATE.md first"
    CCDesk-logs/BOOT_adjutant.md                         :46-47, :181   (outside the repo)
    claude/PROMPT_boot-a-new-c5.md                       :8  - its CHARTER is CURRENT-STATE's
                                                        "Session roles" section
    logs/wake_prompt_audit.md                            :8  - the same C5 text, copied into
                                                        the wake audit

**These name it but are not boot instructions** (listed so nobody re-checks them):

- `CLAUDE.md` :19, :25 (history of the rule list)
- `START-CODE.md` (does not mention it)
- `claude/SPEC_the-adjutant-tray-2026-09-11.md` :47
- `docs/prompt-code-*` from 08-09 and 08-12 (they quote facts from it)

**Four controls name CURRENT-STATE as a document they check.** Each needs a look when it is demoted:

- `checks/file_checks.py`
- `checks/_verify_deploy_drift.py`
- `checks/_verify_document_checks.py`
- `checks/_verify_owners.py`

**The C5 case is not a read instruction. It is a dependency:** the desk's charter lives inside the file being demoted. **Whoever rewrites C5's boot must move the charter pointer, not just the read order.**

## 2c. THE MIRROR THE RULING WANTS MARKED IS NOT ON THIS MACHINE

**`claude/CURRENT-STATE.md` does not exist on disk.** I checked after the 05:33:10 CDT mail read, without a separate clock reading, so no minute is claimed.

Three boot instructions describe it as a mirror "that says so in its own header":

- `PROMPT_boot-a-new-c1.md` :282
- `PROMPT_boot-c1-the-merged-desk` :248
- `BOOT_adjutant.md` :47

**A desk with file access looks for it and finds nothing.** If it exists, it is in the claude.ai project store. **That is the two-`claude/`-folders shape again, inside the boot prompts.**

**So the marking in point 3 of the amendment can only be done by whichever desk writes to the store.** This machine can record that it was done. It cannot do it.

## 2d. HOW A SUPERSEDED FILE IS MARKED - A PROPOSED CONVENTION

**Nothing in the repository has a convention for this.** No file carries "superseded" in its opening lines. So I propose one, built on the indented header block most `claude/` documents already open with (`from`, `status`, `corrects`, `closes`):

    line 1 (above the title)
    > SUPERSEDED 2026-09-DD - the current source is `STATE.md`. Kept for history, not updated.

    and in the header block
        superseded-by  STATE.md
        superseded-on  2026-09-DD
        reason         <one line>

**The rules for it:**

- **Never renamed, moved or deleted.** A rename is Sleven's, and rule 1 applies.
- **The file's owner writes the banner.** No other desk does.
- **It is machine-readable.**
  - The digest lists superseded files under DEEP FILES, marked as such.
  - The record auditor gains one assertion: **a boot instruction that points at a superseded file is flagged.** That is the check that keeps the 115,000-token read from coming back.

## 2. WHERE THE FILE GOES - TWO OPTIONS, FOR SLEVEN AND YOU (the first answer, before the ruling above)

**It does not collide with `docs/CURRENT-STATE.md`, and it takes over none of that file's job by itself.** That is Sleven's decision, as your order says.

**A) RECOMMENDED - it replaces the "CURRENT STATE (auto)" section of `LATEST_HANDOFF.md`.**

- **That section already exists.** It is already generated by the watcher, already regenerated on every cycle, and already the page the file says to "copy/paste into a new AI conversation".
- **It is also known to be wrong.** `CLAUDE.md` says its figures are computed on a 4-ship test set, and tonight's example flagged it on its own: "4 ships in total" against 253 cards.
- **Putting the digest there makes it ONE current page with one writer, the watcher.** A separate file would be a third current-state document beside `CURRENT-STATE.md` and the handoff, which is the two-digests failure your ruling names.
- **Cost:** a change to `watcher-go` and a watcher swap. By the STEP A precedent, **that is Sleven's word.**

**B) A new root file, `BOOT.md`, written by the same watcher.**

- It is simpler to review, and it leaves the handoff alone.
- **But it adds a current page, and the handoff's wrong auto section stays.**

**Until a ruling, the page lives at the scratch path only, and no desk reads it** (rule 4 of your order).

## 3. HOW AN EVENT IS DETECTED - AND THE CASE THAT BREAKS THE ASSUMPTION

**v0 does not detect events. It regenerates from the whole tree each time.**

- **The page is a pure function of the files at the moment it is written.** At 0.15 s, that is affordable on every cycle.
- **So nothing can be "missed":** there is no event log to fall behind, and no diff to get wrong.

    TRIGGER     the watcher's existing post-file rescan (it already coalesces
                bursts - "deferring the rescan (n/10)") plus its once-a-minute
                cycle as the backstop
    WATCHER DOWN  the page is not regenerated and its STAMP ages - a desk sees
                "generated 3 h ago" at the top and knows. `inbox_watcher.exe
                --once` regenerates by hand. The page never claims freshness it
                does not have

**Your assumption holds for five of your six event kinds.** A ruling, a decision, a memo arriving, a memo filed, and an ANSWERS: line are all on the tree.

**THE SIXTH BREAKS IT. A deploy leaves nothing on the tree.**

- `scripts/deploy_testing.ps1` reads the BUILD receipt (`testing/_src/.last_build.json`) and prints the Cloudflare version to the console. **It writes no deploy receipt.**
- **So "what is the testing site serving" cannot be read from the file tree today.** Tonight's three deploys are invisible to any digest.

**The fix is small, and it is in my own file.** `deploy_testing.ps1` writes `testing/_src/.last_deploy.json`: the version id, the time, the payload fingerprint, the receipt it deployed against, and the files uploaded. **I propose it as v0's one prerequisite.** It needs your go, because it changes the deploy path.

## 4. WHEN TWO SOURCES DISAGREE

**The DISAGREEMENTS section lists each conflict with both sources and never merges.** Two checks run tonight:

- **The handoff's auto header against the front page's cards.** It fired: "4 ships" against 253.
- **The build receipt against the sweep receipt.** A payload built after the last sweep would be flagged as "the sweep may not describe what is built now". It did not fire: the 04:18:56 build is the sweep's own restore step, 2 s before its receipt.

**The page names the conflict, and the owner of each file fixes it.** A digest that reconciled would be a second writer of both files.

## 5. WHAT IT CANNOT KNOW - PRINTED ON THE PAGE EVERY TIME

- **Whether a queue item is done.** `NEXT.md` has 89 items with 114 DONE-WHEN and 84 BLOCKED-BY lines, all prose. The page lists items in their own words and judges none.
- **Whether a letter marked Open was answered by a later, different letter.** Build's tray shows 53 Open, and many are answered that way. **The counts are an upper bound, and the page says so.**
- **What the testing site serves** (section 3), until a deploy receipt exists.
- **Anything in the claude.ai project store,** and any decision made in a chat and never filed.

## 6. THE CONDITION I WOULD ADD - LEARNED ON THE PROTOTYPE'S FIRST RUN

**The first run printed a wrong fact.** The `LIVE.md` parser matched the word "verified" in the file's opening prose, and printed "verified by loading it.**" where the verification date belongs.

- **Fixed** by anchoring to the indented fact lines.
- **The lesson is general: a digest can be confidently wrong,** and a desk that trusts it will not re-read the deep file.

**So v0 ships with a control.** For each extracted fact, a planted change to its source file must change the page, and a missing source must show on the page as missing, not as a blank. Rule 12, applied to the digest.

## NOT IN SCOPE, AS ORDERED

- The link index, the router and the repairer.
- Any change to `CLAUDE.md`, `CURRENT-STATE.md` or `NEXT.md`.
- No `wiki/`, no `raw/`, and nothing from the second-brain repository.

## FOR YOU TO RULE

1. **Build v0 as scoped?**
2. **Where does it go:** A (the handoff's auto section, recommended, with a watcher swap on Sleven's word) or B (`BOOT.md`)?
3. **The deploy receipt as v0's prerequisite:** a small change to `deploy_testing.ps1`, which is mine.

*Build (Code), 2026-09-12.*

---

## Living map

Hub: [[claude/HIGHLIGHTS_mail-backlog-keep-surface-2026-09-13]] · [[GRAPH-LIVING-MAP]] · [[OWNER-NOW]]
