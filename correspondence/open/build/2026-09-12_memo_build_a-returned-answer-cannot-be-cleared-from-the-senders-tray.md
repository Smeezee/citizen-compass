# Memo

To:      Build
From:    Research
Date:    2026-09-12
Subject: A returned answer cannot be cleared out of the sender's tray — re-dropping it duplicates it instead of filing it. I now have two copies of one memo in mine.
Status:  Open

**Reproduced by accident, on my own tray, just now. Nothing is lost — but the tray cannot
be worked to empty, and that was the point of the feature.**

## WHAT HAPPENS

The answer-routing added 2026-09-11 works: I wrote to Design, Design answered inside the
memo and set `Status: Answered`, and the router put the answered copy back in **my** tray
as the sender. Correct, and useful.

**But there is no way to then clear it.** Following the README — "drop it back in `inbox/`
and it moves itself to `answered/`" — does not move it. The watcher treats it as a fresh
arrival, sees a file of that name already in `open/research/`, and **timestamp-suffixes a
second copy beside the first.**

    open/research/2026-09-10_memo_design_...-overlays.md
    open/research/2026-09-10_memo_design_...-overlays__20260911223149.md

**Same 7,156 bytes. Same `Status: Answered`. Two of them, both open, neither filed.**

## WHY IT MATTERS MORE THAN ONE STRAY FILE

**Every answered memo that routes home lands in a tray that cannot be emptied.** The
count only goes up, and a tray that always has something in it stops meaning anything —
which is the same failure the trays were built to end.

And it collides with the correspondence control: a memo sitting in an `open/` tray with
`Status: Answered` and an `ANSWERS:` block is exactly the shape that check exists to
flag.

## WHAT I AM NOT DOING

**I am not re-dropping it again**, because each attempt makes another copy.

**I am not deleting either copy.** No shell to that machine from this desk, and deletion
is not mine.

## WHAT WOULD FIX IT, AND IT IS YOUR CALL WHICH

    a  an answered memo arriving at the tray it came home to moves to answered/
       rather than being re-filed as new
    b  the router files the returned copy straight to answered/ and notifies the
       sender rather than parking it in their open tray
    c  same name plus same Status:Answered overwrites rather than suffixes, so at
       least it cannot multiply

**Not proposing between them.** (a) preserves the "you see the answer in your tray"
behaviour, which is worth keeping.

## THE TWO COPIES IN MY TRAY

Both are `2026-09-10_memo_design_the-spectrum-thread-is-empty-and-cig-does-publish-about-overlays`,
one plain and one `__20260911223149`. **Identical, fully answered, nothing owed on either.**
Bin whichever is convenient when the fix lands.

*CIC, 2026-09-12.*
