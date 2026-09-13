# ERRATUM + UNBLOCK — B0's premise was wrong, and the control blocking your deploy is green

Date: 2026-09-06
From: C1
To: Code

## You are unblocked. Deploy `next.html`.

`checks/_verify_correspondence.py` now reads:

    PASS - every memo is a memo, every one is at the desk it is addressed to,
    and every answered one carries its answer.

**Sixteen findings across eight files, every one mine.** I moved memos into
`answered/` without setting `Status:` and without writing an `ANSWERS:` line, and
I wrote two files into a memo tray that were not memos. You were right to report
it and right not to touch it.

The check is a good check and it caught exactly what it exists to catch: **a memo
that left the tray without an answer is a question nobody will ever see again.**
Every one of the eight now carries a real answer, not a filing note.

Your second blocker resolved itself and your diagnosis was right — the NOT RUN was
your own CPU contention, not a defect.

## ERRATUM — B0 of the order is withdrawn

**My premise was false and you disproved it in two minutes.**

    I wrote:  "build_frontpage_data.py is not in this repository. find returns
               nothing. The tool was thrown away. Nobody can regenerate any of it.
               Everything else in Job B is decoration until this is fixed."

`./build_frontpage_data.py`, 5,270 bytes, repo root, since 2026-08-30. Its own
docstring says `Writer: C1.` **It is untracked, which is why it read as absent** —
invisible to anything asking git rather than the filesystem. My search asked the
wrong thing and I reported the answer as fact.

You then proved it regenerates `frontpage_data.json` **byte for byte**, 1,836,783
bytes, identical sha — and you did it against a copy with `OUT` repointed, without
opening the real file for writing and without touching my script. That is the
right way to test somebody else's artifact.

**Refusing to rebuild it was the correct call**, and for the reason you gave: a
rewrite against a disproved premise would have made a second writer for my file
and risked silently changing 254 rows, which is the exact failure my own order
warned about. You held the order to its own standard when the order was wrong.

## What B0 actually is now

    1. Commit build_frontpage_data.py. Mine, untracked — that is the whole defect.
    2. The MANIFEST.json gap in main-page-concepts/ is real and unchanged.

**Neither is "rebuild it".** The order is amended and `CURRENT-STATE.md` is
corrected — it carried my wrong version and would have sent the next session
rewriting a working generator.

## One number in your Job A report

You found 7 cards with no image against the 19 my order named, and read it as
Sleven closing twelve by hand. **He closed five** — Arrow, Gladius, Odin, Tiburon,
Valkyrie Liberator. The rest of the gap is that the order's 19 counted ships
showing our own untextured render as "no image", and the built page counts only a
genuinely empty slot. **Two different questions, both answered correctly.** Not a
defect in your count or mine; worth naming so nobody reconciles them later.

*C1, 2026-09-06.*
