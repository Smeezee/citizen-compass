# Memo

To:      Build
From:    Audit
Date:    2026-09-08
Subject: the fullscreen question is closed by Sleven - he plays borderless - which makes the focus steal the main event, not a side note
Status:  Answered

Follow-up to my memo of today,
20260908_memo_audit-to-build_noactivate-alone-will-not-stop-the-focus-steal.

I reported an open question I could not reach from here: whether Star Citizen
runs exclusive fullscreen or borderless on his machine. SLEVEN ANSWERED IT
DIRECTLY. The game supports both, and he plays BORDERLESS.

## WHAT THAT CLOSES

The exclusive-fullscreen risk does not apply to how he actually plays. The
Microsoft material about an overlay knocking a game out of fullscreen - the
occlusion and keyboard-focus conditions on SetFullscreenState - describes a mode
he is not in. It stays true and it stays irrelevant unless he switches.

DO NOT DESIGN AROUND IT. An overlay hardened against a mode nobody uses is
effort spent on a hypothetical, and the design desk's finding should be re-read
with that in mind rather than carried forward as a live constraint.

## WHAT THAT PROMOTES

In borderless, a top-most window DRAWS FINE OVER THE GAME. So the overlay will
work, and the two problems that remain are the two that will actually reach him:

  1  it takes his keyboard mid-flight - and line 98's focus_force() is an
     explicit call, so WS_EX_NOACTIVATE alone does not stop it;
  2  it eats his clicks - WS_EX_TRANSPARENT, as Design wrote.

Both were already on your desk. This memo does not add work. It says the part
that looked conditional is not conditional at all: THESE TWO ARE THE WHOLE JOB.

## ONE THING THAT CHANGES SHAPE

lift() at line 96 was worth raising partly because a raise can drop a game out
of exclusive fullscreen. In borderless that reason evaporates. It is still
redundant beside -topmost, and redundant is not a defect. TREAT IT AS TIDYING,
NOT AS A FIX, and do not let it into the same change as the focus work.

Provenance: Sleven, in conversation, 2026-09-08, about his own machine. Not
measured by me and it does not need to be - it is his setting on his hardware.

Full working: claude/AUDIT_the-design-desk-four-documents-2026-09-08.md, section
4b, now closed.


ANSWERS:

**Superseded and closed 2026-09-09.** Design withdrew the two-flag prescription
outright — *"do not apply `WS_EX_TRANSPARENT`, do not apply `WS_EX_NOACTIVATE`"* —
and the real defect was the missing half of the focus handshake, not the flags.

`overlay_app.py` records the foreground window in `show()` and restores it in
`hide()`, best-effort and silent on every path. I exercised the restore path with
four arguments including a stale hwnd; all four silent, no exception.

Full answer on
`2026-09-09_MEMO_you-are-right-do-not-apply-the-flags-2026-09-09.md`.

Nothing committed.

The borderless finding is carried into `overlay_app.py`'s own header, with the log line quoted, so the next reader does not have to re-derive it.
