# Update — the 74 became 1, the overlay cluster is closed, and I mangled two memos on the way

**Filed 2026-09-09 16:55 CDT.**

## THE SWEEP BLOCKER IS DOWN TO A SINGLE FINDING

I reported `_verify_correspondence.py` red with 74 findings. **Architecture has
been clearing them while I worked — 73 closed. One left**, and it is in their own
tray:

    correspondence/open/architecture/2026-09-08_where-the-sweep-time-goes.md
    is marked 'answered' but is still in an OPEN tray

**It is a Build memo and I still did not fix it.** The trace says the incomplete
action is theirs:

    2026-09-07 21:35:06   the watcher filed it to open/architecture,
                          so its Status was Open when it arrived
    2026-09-08 02:00:07   the file was modified - Status became Answered

**There is no `ANSWERS:` line.** Zero characters of answer. That is a recipient
marking a memo answered in place and not completing the second half.

Re-dropping it as it stands trades one finding for another — it would land in
`answered/` and immediately trip *"filed as answered and carries no ANSWERS:
line"*, a closed drawer holding nothing. Setting it back to `Open` would overrule
their edit on their tray on a guess. **Rule 19: two readings, so I refused to pick
one.** Memo sent naming both one-line fixes.

**I also declined to deploy past it.** `deploy_testing.ps1` carries
`-IgnoreRedCheck`, a deliberate and loud override, and memo filing has nothing to
do with the payload — so Q49 could ship past it. **Overriding a gate because the
thing it caught is inconvenient to me is exactly the reasoning that override
exists to make visible rather than easy.** Architecture can say the word.

## THE OWNER'S API KEY QUESTION — NOT SET, ANYWHERE

User scope, machine scope, this process, `.env`, and the archived `.env`: all
absent. **And nothing in the repository sets it** — the string appears in exactly
two files and both are documents about the question. No value read, printed or
logged; nothing changed.

## THE OVERLAY CLUSTER — SIX MEMOS CLOSED, NOTHING BUILT

Design withdrew the two-flag order and named their own error. Neither flag is in
`overlay_app.py` and neither ever was. The real defect — `show()` taking focus,
`hide()` never giving it back — was already fixed here; I lifted the two helpers
out by AST and put four arguments through the restore path, including a stale
window handle. All four silent, as designed. No GUI launched.

Audit's `lift()` heads-up is closed by the borderless finding: every
`SetFullscreenState` condition they cited is about exclusive fullscreen.

## AND AN ERROR OF MINE, REPAIRED AND RECORDED

I closed three memos through an **unquoted shell heredoc**, and the shell ate
every backticked term before it reached the files. Two ANSWERS blocks landed with
holes where `overlay_app.py`, `WS_EX_TRANSPARENT`, `WS_EX_NOACTIVATE`, `show()`,
`hide()` and a memo filename should have been.

Repaired in place the same minute, **and each repaired block now carries a filing
note saying it was changed after filing.** No claim, number or outcome was
affected — only names that had been blanked. An ANSWERS block that changes after
it is filed should say so rather than be quietly corrected.

**The mechanical fix:** every heredoc that carries project prose is quoted
(`<<'EOF'`), and the timestamp is substituted afterwards rather than expanded
inside it. That is what produced this file.

## STILL RUNNING

A full sweep, started before this batch. It is the second of the three receipts
Sleven wants before setting a runtime ceiling, and it will name anything red
besides the one memo.

**Build tray: 10 open** (counted at filing). Nothing committed.
