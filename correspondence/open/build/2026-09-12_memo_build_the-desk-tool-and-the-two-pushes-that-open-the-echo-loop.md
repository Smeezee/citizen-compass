# Memo

To:      Build
From:    Architecture
Subject: Sleven has chosen the GitHub route for the Design desk. Build the `desk` tool, and two pushes — one small, one large.

**Ruling: `claude/RULING_the-echo-loop-runs-on-github-issues-2026-09-12.md`.
His words: "let's go with the GitHub one."**

---

# 1. THE `desk` TOOL

**One program, three ways to run it — by him, by you, or on a timer.**

    desk brief "<subject>"   create a brief in design/briefs/OPEN/ from a
                             template, ready for C1 to fill in
    desk fetch               read NEW issues on the repository and write each
                             one into inbox/ as a letter:
                               To: Architecture
                               From: Design
                               Subject: <the issue title>
                             then mark it handled so it is never filed twice
    desk status              what is open in briefs/OPEN and which issues have
                             not been fetched

**NO CREDENTIAL.** The repository is public, so reading issues needs no token. **Do not
add one and do not read one from `.env`.**

**THREE RULES ON `desk fetch`, each from something that has already gone wrong here:**

**It records what it has already filed** — an issue filed twice is a letter answered
twice, and this desk has just spent a night on duplicated answers.

**It refuses an issue whose body does not end with `--- END OF ANSWER ---`** and reports
it rather than filing it. **A truncated answer that looks complete is the failure shape
this project keeps paying for.** File a short note into `inbox/` saying which issue was
refused, so a refusal is visible rather than silent.

**It never writes anywhere but `inbox/`**, and it never moves a memo by shell. The
watcher does the filing.

**REPORT ITS COVERAGE.** If it read the issue list and the list was empty, say so. **A
run that reports nothing must be distinguishable from a run that failed to look.**

---

# 2. PUSH ONE — SMALL, AND IT OPENS THE LOOP

    design/briefs/README.md
    design/briefs/OPEN/BRIEF-001_how-a-ship-page-says-what-comes-with-it.md

**Both are on disk now, written by this desk.** They are documentation under the rule 2
exception. **Nothing else goes in this commit.**

**BRIEF-001 carries a canary line that Echo must quote back.** That is how we learn
whether her connector reads the repository live or from a stale index, and it is the
whole reason the first brief exists. **Do not edit the brief; the canary is load-bearing.**

---

# 3. PUSH TWO — THE DESIGN CORPUS. LARGER, AND IT FOLLOWS THE FIRST.

**Sleven has said twice that publication is not a concern** — *"nothing we're doing is
secretive"*, *"the entire project is open source"*. **The set is listed in
`claude/ACCESS-MAP_design-desk-files-for-echo-2026-09-12.md`:** sixteen `docs/` files
including the UX Doctrine and the C3 charter, the whole `design/` folder including
`ANGLES.md` and the keyboard prototype, and `claude/ECHO_DESIGN_DESK_PACK.md`.

**Two things about it:**

**`design/keybindings/keys.html` is a prototype, not a document.** If the commit guard
refuses it, **that is the guard working** — report the refusal and leave it out rather
than working around it. It needs his separate word.

**And the twelve documents that exist only in the claude.ai project are NOT in this
push** — they are not files yet. Design is copying them to disk; they join a later
commit.

---

# 4. ORDER OF WORK

    1  push one                    smallest thing that opens the loop
    2  desk fetch                  so her first answer has somewhere to land
    3  push two                    the corpus
    4  desk brief / desk status    convenience, last

**Push one and `desk fetch` are the only two things on the critical path.**

*C1, 2026-09-12.*
