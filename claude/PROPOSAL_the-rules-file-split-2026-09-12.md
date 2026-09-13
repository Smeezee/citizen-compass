# PROPOSAL — THE SPLIT OF `CLAUDE.md`. Nothing edited. For Sleven's word.

    from       C1, architecture
    date       2026-09-12
    ordered    Owner, 2026-09-11: propose the split. Nothing deleted, nothing
               edited without his word, measure before and after.
    condition  NO EDIT TO CLAUDE.md UNTIL HE HAS SEEN THE PROPOSED CORE IN FULL.
               Section 6 is that core, in full.

---

## 1. THE FINDING THAT CHANGED THE PROPOSAL, AND IT IS THE FILE ARGUING AGAINST ITSELF

**The file's first instruction is *"Read the Hard Rules below."* It points at a block that
does not contain rules 24, 25 and 26.**

`## HARD RULES` runs L14–L389 and holds rules 1–23. **Rules 24, 25 and 26 sit at L511–589
as subsections of `## Known caveats`** — a different H2, 118 lines further down, past four
intervening sections.

**Those three are the rules about how to deal with Sleven himself:** read the mail before
you answer him; scope is a list, not a memory; an unknown is researched, not returned to
him. **A session that obeys line 3 literally never reaches them.**

**And the file states the discipline it has broken, twice.** L16: *"This is the ONLY
numbered rule list in the project."* L31–32: *"If you add a rule, add it here and nowhere
else."* **The rules were added to the file and not to the list.**

**That is the argument for the split, and nobody had to make it — the file grew past its
own structure and then documented the growth.**

## 2. THE TEST, APPLIED, AND IT DOES NOT CUT WHAT ANYONE EXPECTED

**His test: a rule stays in the core if breaking it costs something no check would catch.**

**Applied honestly, almost every rule stays.** Nothing catches a deletion, a fabrication, a
missing backup, a fetch under `/media/`, or a question handed to Sleven that a search would
have answered. **I can find no numbered rule that a check reliably catches.**

**So the test does not separate rules from rules. It separates RULES FROM THEIR
EVIDENCE.**

    what the file actually contains
      the rules, stated                    roughly 370 lines
      incidents, war stories, rationale,   roughly 230-250 lines, 38-40%
      aphorisms and repo inventory

**The 624 lines are not 624 lines of rule.** They are twenty-six rules and the price of
each one, written down beside it.

**AND THAT IS WHY THE ADVICE HE READ IS WRONG FOR THIS FILE.** *Wipe it every six months*
assumes a rules file accumulates guesses. **This one accumulates incidents** — a 234-file
mutation with no dry run, three handoff generators fighting over one file, a decoder that
failed all day while the session reported camera percentages as progress, an April Fools
ship ordered onto the front page as fact. **Wiping it deletes the receipts, and a rule with
no receipt is a rule the next session argues with.**

## 3. SO THE SPLIT IS: THE RULE STAYS, ITS EVIDENCE MOVES — AND THE POINTER GOES FIRST

**His condition 1, applied literally.** No line is deleted. Every incident lands in a named
document, and **the pointer is written into the core before the line leaves**, so there is
never a moment when a rule has lost its evidence.

    docs/RULES-EVIDENCE.md   NEW. Every incident, war story, rationale and
                             aphorism, keyed to its rule number. A reader who
                             wants to know why rule 5 exists reads the 234-file
                             mutation there.
    docs/CURRENT-STATE.md    TAKES `## Known caveats` (L486-508). It is current
                             broken state - "Not yet fixed", "Not yet fully
                             reconciled" - and state belongs in the state
                             document. PUTTING VOLATILE STATE IN THE RULES FILE
                             IS THE MECHANISM BY WHICH THE RULES FILE GROWS.
    docs/                    TAKES `## How the handoff pipeline works`
                             (L413-454) and `## What's here` (L458-482).
                             Orientation, not rule.
    docs/RULES-EVIDENCE.md   ALSO takes the standing LATEST_HANDOFF section
                             (L391-409), which is rule 13 stated a second time
                             at length. The file says so itself at L239-240.
                             Not deleted - recorded as the original, promoted.

## 4. THE NUMBERS DO NOT MOVE, AND THIS IS NOT NEGOTIABLE

**L27–29: numbers 1 to 15 must not be renumbered, because around a hundred check files cite
rules 12, 14 and 16 by number.**

**Every rule keeps its number, including 24, 25 and 26 — which move INTO the list where
they belong without changing what they are called.** The split touches where words live,
never what a rule is called. **A renumbering would silently break a hundred citations and
no check would catch it**, which is the same test that kept the rules in the core.

## 5. FOUR CONTRADICTIONS FOUND WHILE READING IT, AND THEY ARE DELIVERABLE ON THEIR OWN

**None of these is caused by the split. They are in the file now.**

**A. `generate_handoff.py` is alive and dead in the same document.** L474–475 lists it as a
current pipeline component *"(maintains LATEST_HANDOFF.md)"*. L415–416 says the Go watcher
is the ONLY writer of that file and never to invoke a generator directly. L440–448 says the
script is retired, lives at commit `5081be4`, and is nowhere on disk. **A reader working
from L474 goes looking for a live Python generator; if they found a copy they would then be
told not to run it.**

**B. Rule 14 keeps a stale rule in the very paragraph that argues against keeping stale
rules.** L255–264 records that the `testing/` assignment *"used to read 'Claude Code, and
nothing else'"*, that this was false by August, and that `OWNERS.md` wins. L268–270 then
argues for *"deleting a stale rule rather than leaving it to be reconciled by whoever trips
on it next"* — **while the stale rule is the thing you are reading.** It already cost a
stalled queue item on 2026-08-30 when Code correctly stopped.

**C. Rule 1's promise against the file's own record, 400 lines apart.** L44–46 says things
are moved to `_to_delete/`, never deleted. L445–448 records that
`_to_delete/python_handoff_path_retired_20260801/` never existed and the three files are
nowhere on disk. **The document carrying rule 1's promise described a location that was not
there** — so anyone checking whether rule 1 had been honoured found an empty answer. Found
by the audit desk, already self-documented. **Named here because the correction and the
promise should not be 400 lines apart.**

**D. The single-list discipline against the file's own filing.** Section 1 above.

## 6. THE PROPOSED CORE, IN FULL — HIS CONDITION 2

**Every rule, stated. Nothing dropped. Evidence pointered, not carried.**

    # Citizen Compass — HARD RULES

    Claude Code runs here with permissions skipped, so this file IS the
    safety mechanism. Treat every rule as if a human were about to be asked
    to approve the action and you are answering for them.

    This is the ONLY numbered rule list in the project. Add a rule here and
    nowhere else. NUMBERS NEVER CHANGE - about a hundred check files cite
    rules 12, 14 and 16 by number.

    These are prohibitions, not preferences. When a rule and an instruction
    conflict, the rule wins: stop and ask. If unsure whether an action falls
    under a rule, assume it does.

    WHY EACH RULE EXISTS, with the incident that bought it:
    docs/RULES-EVIDENCE.md. Read it when a rule looks unreasonable.

     1  NEVER DELETE. No rm, del, Remove-Item, rmdir, shutil.rmtree, anywhere
        in this repo. Move it to _to_delete/ and say so. Sleven deletes.
        Applies to files you believe are duplicates, empty, generated or junk.
     2  NO COMMIT OR PUSH without Sleven saying so, in that message, for that
        change. "He said yes to something similar" is not a go-ahead.
        NEVER git add -A: stage by name, every time.
        EXCEPTION, 2026-09-12: Code may commit named documentation files once
        the guard that refuses an undeclared path is proven.
     3  NO DESTRUCTIVE DATABASE OPERATION outside the guarded harness. No DROP,
        TRUNCATE, DELETE FROM or alembic downgrade against a database you did
        not create in this process. Do not weaken run_e2e_test.py's guards.
        Do not set CC_E2E_ALLOW_REMOTE=1. The real database sees only
        alembic upgrade head and forward-only importers.
     4  VERIFIED BACKUP before anything destructive or irreversible. Run
        Backup-CitizenCompass.ps1 and CHECK ITS OUTPUT, not that it ran. If you
        cannot verify it, stop and report that you stopped.
     5  DRY RUN BEFORE BULK. Anything touching more than ~10 files runs
        report-only first, prints what it would change, and stops until Sleven
        has seen the list. Includes in-place edits, batch renames, format
        conversions and rescale passes.
     6  NEVER WRITE OUTSIDE THIS REPO without asking - every time, even if told
        something similar before. Named and off-limits: ~/.claude.json,
        .claude/, MCP registration, Task Scheduler, the registry, environment
        variables, antivirus settings.
     7  NEVER EXECUTE CODE YOU DOWNLOADED. ~29,000 third-party files here have
        never been malware-scanned.
     8  NEVER EDIT FAN KIT, TRADEMARK, LICENSING OR LEGAL TEXT. Rule 8 governs
        EDITING that text, not what the project may use - see rule 9.
     9  WHERE INFORMATION COMES FROM DOES NOT MATTER. CREDIT DOES. A failed
        fetch is not an answer; go and get it elsewhere and say where.
    10  NEVER EXECUTE AGAINST A LIVE BLENDER SESSION WITH UNSAVED WORK.
    11  FAIL CLOSED, AND NEVER FABRICATE. No invented value, no guessed
        citation, no asserted confidence you do not have.
    12  A CHECK THAT CANNOT FAIL IS NOT A CHECK. Prove it can go red before you
        trust it green. A process that exits 0 having done nothing is the
        failure mode this project pays for most.
    13  FILE THE HANDOFF BEFORE YOU MOVE ON.
    14  ONE WRITER PER ARTIFACT. Make the second writer impossible, not
        discouraged. OWNERS.md IS THE LIST AND IT WINS OVER ANY PROSE,
        INCLUDING THIS FILE. Check it before naming an owner.
    15  EVERY FILE OPEN STATES ITS ENCODING. The Windows default is cp1252 and
        it cannot represent the ship names this project holds.
    16  A CHECK DRAWS ITS TRUTH FROM A DIFFERENT SOURCE THAN THE THING IT
        CHECKS. Same-path checks prove only self-consistency.
    17  NO FUZZY MATCHING. Anywhere, in anything. A near-match that is wrong is
        worse than no match, because it looks like an answer.
    18  READ THE CLOCK FROM THE MACHINE. Never estimate it.
    19  AMBIGUITY IS REFUSED, NOT RESOLVED BY PICKING. Drop both candidates and
        name them. Rule 19 applies AFTER the search, never instead of it - an
        unresearched unknown is unresearched, not ambiguous (see rule 26).
    20  EVERY DATA ROW CARRIES last_verified_patch. A number with no patch
        attached is a number with no date on it.
    21  SCREENSHOTS ARE INTERNAL WORKING MATERIAL.
    22  DO NOT FETCH ANYTHING UNDER /media/ ON robertsspaceindustries.com.
    23  RIGHTS AND CREDENTIALS ARE CLOSED. Do not re-raise either. Sourcing is
        settled by rule 9.
    24  READ THE MAIL BEFORE YOU ANSWER SLEVEN. Every time.
    25  SCOPE IS A LIST, NOT A MEMORY. A stalled job is REPORTED, not quietly
        swapped for something that produces cleaner numbers.
    26  AN UNKNOWN IS RESEARCHED, NOT RETURNED. Sleven is the decision-maker,
        never the fallback researcher and never the pair of hands. The same
        for execution: if one desk is blocked, route to another. Handing him a
        command is the last resort, and when it is one, say the system is
        blocked rather than presenting it as the workflow.
        THE STANDING OBLIGATION: every repeatable manual step is a defect in
        the machine. The next question is how to remove it permanently, not
        how to get past this one.

**That is 26 rules in roughly 95 lines against 624.**

## 7. WHAT I WOULD NOT DO, SAID SO IT IS ON THE RECORD

**I would not cut a rule to hit a line count.** Anthropic's guidance is under 200 lines and
the core above is under 100, but that is a consequence of moving evidence, not of dropping
anything. **If the test had said a rule was expendable I would say so; it does not say that
about any of the twenty-six.**

**I would not let the evidence file become optional reading and then shrink.** It is the
reason the rules survive being argued with. **The core's pointer to it is a rule of the
core, not a footnote.**

## 8. THE MEASUREMENT — HIS CONDITION 3

**Before-and-after on the same wake, with the usage logging Build already has.** The
multiplier is in
`claude/FINDING_the-304000-is-the-rules-file-read-once-per-tool-call-2026-09-10.md`: the
file is re-read once per tool call, so the saving is per-call and not per-session.

**The honest prediction, so it can be wrong in public: roughly six-sevenths of the rules
file's per-call cost.** If the measured saving is much smaller than that, the file was not
the multiplier and I want that on the record rather than quietly dropped.

---

**NOTHING IS EDITED. `CLAUDE.md` is untouched. The evidence file does not exist yet. This
document is the proposal and his word is the gate.**

*C1, 2026-09-12.*
