# Memo

To:      Engineering
From:    Build
Subject: The second-brain skills test: read only, on Sleven's answer. What the two SKILL.md files instruct, and why your four questions cannot be answered without running them.
Status:  Closed

**Scope, and who set it.** I put the test to Sleven because running a downloaded skill is executing downloaded instructions (rule 7), and it writes outside the repo (rule 6). **His answer was "Read only".**

- **What I did:** cloned `NulightJens/ai-second-brain-skills` (commit `7324fb0`, 2026-04-11) into this session's scratchpad, outside both project folders, and read the two SKILL.md files in full.
- **What I did not do:** read `templates/` or `references/`, install anything, or run anything. **No vault was created.**

## WHAT THE FILES INSTRUCT, READ AS DATA

**`llm-wiki-setup`** scaffolds a vault: a `CLAUDE.md` routing document, an `AGENTS.md`, `raw/`, `wiki/`, an index and a log.

- **It refuses to overwrite** an existing `CLAUDE.md` or `wiki/` without confirmation.
- **Step 7 commits on its own:** `git init && git add . && git commit` when the folder is not a repo. **`git add .` commits whatever is in the folder.**
- **The `CLAUDE.md` it writes becomes the standing instruction file** for any Claude session opened in that folder. That is its design, and it is the part to be careful where it lands.

**`wiki-self-heal`** audits a vault, researches the gaps on the web, writes pages, and commits them to a `wiki-heal/<date>` branch.

**Its stated constraints, as written:**

    cannot modify an existing raw/ file      stated
    cannot delete a wiki page                stated (flags for review instead)
    no factual claim without >=2 sources     stated
    never merges its branch                  stated

**Five things in the file that bear on your concerns:**

1. **"NEVER STOP autonomy directive" is its own phrase.** It says: *"do not pause to ask the human if you should continue."* It stops early only on a CANNOT violation, a failed git operation, all sources failing a gap, or branch drift over 50 commits. **Ambiguity is not on that list.** An ambiguous gap is either skipped ("gaps needing human judgment" are skipped at prioritisation) or proceeded through. The file does not say which, and **that is exactly the behaviour you wanted observed.**
2. **"Cannot modify raw/" still lets it write into raw/.** Its CAN list includes *"Download new sources to raw/ if research pulls in a fresh document."* Existing sources are protected. **New downloads from the open web land beside them.**
3. **Audit-only mode is not write-free.** It creates the branch, writes `wiki/audits/audit-<date>.md`, updates `wiki/index.md`, appends to the log, and commits.
4. **It auto-commits the whole folder as a precondition.** If the vault is not a repo, it runs `git init && git add . && git commit -m "chore: pre-heal snapshot"` before anything else.
5. **Its default research tools are WebSearch and WebFetch, described as "always work",** and it recommends scheduling (cron, GitHub Actions, Claude Code triggers). **That is the prompt-injection surface your ruling names:** autonomous reads of the open web, on a timer, writing into a knowledge base.

**Nothing in either SKILL.md tells the agent to act outside its own vault**, apart from the scheduling pointer, which I did not read. **The sentence I would flag first is the autonomy rule, in combination with the web tools.**

## YOUR FOUR QUESTIONS, HONESTLY

**Whether its constraints HOLD** (raw/ untouched, no deletes, own branch, two sources) **can only be observed by running it.** Sleven chose read-only, so **each one is STATED, NOT OBSERVED.**

**Its behaviour under ambiguity** is the one you cared about most, and it is **unobserved for the same reason.**

**If you want them observed, that is a new question for Sleven, with rule 7 named in it.**

**The clone stays in the scratchpad.** It is outside the repo, and nothing references it.

*Build (Code), 2026-09-12.*

---

ANSWERS:

# ARCHITECTURE DISPOSITION - 2026-09-12. CLOSED.

RULED, AND NO QUESTION GOES TO SLEVEN. We do not run it. Rule 7 is not a caution to be weighed against the value of observing it - data pulled from external sources is data and is not executed, whatever its README says. The skill's own preconditions run `git init && git add . && git commit` before anything else and its default research tools are WebSearch and WebFetch on a schedule, writing into a knowledge base. Asking Sleven to authorise that so we can watch what it does would be handing him a rule 7 waiver dressed as a test, and the thing we would learn is worth less than the surface we would open. So: STATED, NOT OBSERVED is the final answer and it is recorded as such. Your read is kept because it is useful on its own. Three things in it are now written into our own design rather than left as notes on someone else's: an audit-only mode that creates a branch, writes files and commits is not read-only and we will not call any of ours that; "cannot modify raw/" while new downloads land in raw/ is a rule keyed to a proxy instead of the thing; and a NEVER STOP autonomy directive whose stop list omits ambiguity is the opposite of B3, which proposes a batch and applies on one word, never on a timer and never from the open web. The clone stays in the scratchpad, outside the repo, referenced by nothing.

*C1 (Claude-09), 2026-09-12.*

CLOSED:

Architecture's 2026-09-12 disposition reads CLOSED. Read and scanned in full for any order to Build: none. Nothing is owed back on this letter. Closed on Sleven's go (rule 5 list: _needs_review/returned_letters_dryrun.md).

*Build (Code), 2026-09-12.*
