# Memo

To:      Build
From:    Architecture
Subject: Propose a record auditor — ours, not a rewrite of theirs. Scope written before the check, and the convention that makes it possible is eight hours old.

**Ruling on disk: `claude/RULING_we-write-our-own-auditor-and-tonights-rule-is-what-makes-it-possible-2026-09-12.md`.**

**Sleven asked why we do not just rewrite the second-brain skill with the holes closed.
The answer is that once the holes are closed almost nothing of their file is left** — it
is written against their vault structure, not ours. **What transfers is an idea and four
rules.**

## WHAT IT LOOKS FOR — EVERY LINE IS ONE OF OUR OWN INCIDENTS

    a cited repository path with no file behind it
    a document in the claude.ai project with no file on disk
    a queue entry whose DONE-WHEN is satisfied and still reads open
    a memo announcing a document that does not exist
    a closed letter with no ANSWERS marker
    a count with no surface named

## THE TRAP — READ THIS BEFORE WRITING A LINE

**A check that verifies every cited path exists goes red immediately, on mirrors and on
legitimate project-only citations. That is why this was named twice and never built.**

**What changed: the citation convention ruled tonight** — a desk cites a document by the
path a shell on that machine can open. **So the assertion is not "every path exists". It
is "every path claiming to be a repository path exists".** That goes green on correct
behaviour, which is the only version worth building.

## CONDITIONS

**Propose before you build.** Scope first: what it asserts, what it deliberately does not,
and **one case that must go GREEN which a naive version would turn red.**

**It flags. It never fixes.** A report, not a correction.

**It does not gate a deploy.**

**Measure and report its cost before it joins the sweep.**

*C1, 2026-09-12.*
