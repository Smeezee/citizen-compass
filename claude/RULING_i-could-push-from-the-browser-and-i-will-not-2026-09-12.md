# RULING — this desk can reach GitHub through the browser and will not push with it. And the shell being down is a different problem than he thinks.

    from    C1, architecture, 2026-09-12
    asked   by Sleven: you are already connected to GitHub through an extension,
            so shouldn't you be able to do it? And the shell problem needs
            fixing.
    answer  Could, yes. Should, no — and the reason is mechanical rather than
            cautious. The shell is a real problem and it is not the one
            blocking the push.

---

# 1. YES, IT IS TECHNICALLY POSSIBLE

**Claude in Chrome drives his real, signed-in browser.** It read the repository tree, the
commit history and the issues list tonight. **GitHub's web interface allows editing a file
and committing it directly.** Nothing stops it.

# 2. AND IT BYPASSES THE ONE SAFETY MECHANISM THIS PROJECT JUST FINISHED BUILDING

**Every commit goes through Code, and Code's commits pass a guard that refuses anything
outside the documentation set.** That guard is the entire basis of the rule 2 exception,
and the exception was granted only after the guard **was seen refusing a real path.**

**A commit typed into a web form passes through no guard at all.** It is the same act with
the check removed.

# 3. THE MECHANICAL REASON, WHICH IS WORSE THAN THE RULE

**A browser commit goes to GitHub. His local clone does not have it.**

**So the working copy on his machine is immediately behind the branch, and the next commit
Code makes is made from a tree that is missing a file it does not know about.** That is
two writers on one branch with no coordination — **the exact shape that produced a stale
`.git/index.lock`, duplicated answers and a superseded document tonight.**

**One writer to the index. That is Code. It is not a formality and it is not timidity.**

---

# 4. THE SHELL IS A DIFFERENT PROBLEM AND IT IS NOT THE BLOCKER

**`device_bash` cannot mount his folders** — the tool reports a Windows update of
2026-09-08. **Claude Code is explicitly unaffected, which is why Code still works
normally.**

**But even with a working shell this desk would not push**, because the rule is not about
capability. **So fixing the shell would not have moved a single file tonight.**

## WHAT IT ACTUALLY COST TONIGHT, MEASURED

**Close to nothing.** Everything this desk needed to do was reading and writing files, and
both work through the bridge — roughly forty documents and memos were filed without a
shell.

**The two places it bit:** no `git log` or `git status` to establish state, and no way to
run a check or a sweep. **Both of those belong to Code by rule anyway**, so the standing
instruction already covers them: one desk blocked, route to another that can run it.

**The honest verdict: it is an inconvenience this desk routed around all night, not a
blocker.** It is worth fixing when it can be, and it is not worth prioritising over the
eight things currently in flight — **and it cannot be fixed here in any case, since it is
a platform issue being tracked upstream.**

---

# 5. WHAT ACTUALLY REMOVES THE WAIT, AND IT IS ALREADY ORDERED

**The `desk` tool.** `desk brief` writes a brief and commits it; `desk fetch` pulls
answers back. **Once that exists, a brief reaching GitHub is one command that Code or a
timer runs — not a conversation, not a memo, not a wait.**

**That is the fix for the latency he is actually feeling, and it is being built tonight.**

*C1, 2026-09-12. Nothing pushed from a browser.*
