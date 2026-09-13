# Update — `ANTHROPIC_API_KEY` is not set anywhere, and the five overlay memos are closed

**Filed 2026-09-09 16:50 CDT.** Header produced by `date`.

## THE OWNER'S QUESTION — NOT SET, IN ANY SCOPE

    Windows USER scope        NOT SET
    Windows MACHINE scope     NOT SET
    this session's PROCESS    NOT SET
    repo .env                 does not name it
    _to_delete/.env archive   does not name it

Read with `[Environment]::GetEnvironmentVariable(...)` per scope, which reads the
registry rather than whatever this shell inherited. **All three returned null** —
not empty string, which is a different and more confusing state.

**And nothing in the repository sets it.** A ripgrep of the tree finds the string
in exactly two files and both are documents ABOUT this question. No script, no
`.ps1`, no scheduled task command line, nothing under `.claude/`.

**That last part is the answer worth having.** A variable absent today could still
be set by a wrapper at the moment an unattended run starts, and "is it set right
now" would have been correct and useless.

**No value was read, printed or logged. Nothing was changed.** `.env` holds four
keys and none is an ANTHROPIC one; names only.

## THE OVERLAY CLUSTER — FIVE MEMOS, ALL CLOSED, NOTHING TO BUILD

**Design withdrew the two-flag order outright** and named their own error: they
grepped `overlay_app.py` for two strings, described it as a bare tkinter popup,
and prescribed `WS_EX_NOACTIVATE` + `WS_EX_TRANSPARENT` for it. **On an ask box
with a text entry those flags remove the feature** — you could never type the
question.

Neither flag is in the file and neither ever was.

**The real defect was already fixed by an earlier session here**, and Design
called it the better finding: taking focus on `show()` is correct and is the
point; **never giving it back was the bug.** `hide()` called `withdraw()` and
nothing else, so after Escape the game stayed deaf until it was clicked.

**Exercised rather than read.** I lifted `_foreground_window` and
`_restore_foreground` out of the file by AST — no `keyboard` import, no
`ask_engine`, no window opened — and put four arguments through the restore path:

    None                            returned, no exception
    0                               returned, no exception
    an hwnd that is not a window    returned, no exception
    the real foreground window      returned, no exception

**The third is the one that mattered**: a window that closed between show and hide
is the ordinary case, and `IsWindow()` catches it before `SetForegroundWindow` is
asked for anything. I did not launch the GUI — a tkinter app with a global hotkey
is not something to start inside an automated session, and every failure path
that needed proving lives in those two helpers.

**Audit's `lift()` heads-up is closed by the borderless finding.** Every
`SetFullscreenState` condition they cited is about EXCLUSIVE fullscreen, and the
game's own log says borderless three times across two dates, corroborated by
`WindowMode=1`. `lift()` stays, and the reason it is safe is now a fact rather
than a judgement.

## TRAY

Six more closed this session. **Build tray: 13 open**, of which one is blocked on
a permission (the Stop hook) and one is blocked behind the sweep (Q49).

Nothing committed.
