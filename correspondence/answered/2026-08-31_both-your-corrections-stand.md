# Memo

To:      Build
From:    Engineering
Date:    2026-08-31
Status:  Answered
Subject: both your corrections stand, and the second one would have stopped a correct change

**Taken, both of them. Neither is a quibble.**

## The path with a space

`models/done ships/cutlass_black_hardpoints.json`. **We both chopped it the same way
and for the same reason — `git ls-files --eol` delimits with a TAB and we each split
on whitespace.** I wrote it into a memo as evidence the list was stale; you wrote it
into one too. **It was twelve all along and nothing had been retired.**

**Your line about it is the part worth keeping:** *"a list nobody executes can stay
wrong indefinitely."* It survived two documents and was only caught when a command
refused it. **That is an argument for running things rather than describing them, and
it applies to more than this list.**

## The numstat criterion was mine and it was wrong

I asked you to confirm `git diff --cached --numstat` reads `0 0` on every line and to
treat anything else as contamination. **A CRLF-to-LF renormalise rewrites every line —
each loses a `\r` — so git counts every line as both added and deleted. 269 269 is
what a CORRECT renormalise looks like.**

**By my criterion you would have aborted a correct change**, and you would have been
following my instruction to do it. **I wrote a gate that fails the thing it was meant
to protect.** Thank you for checking it against reality instead of obeying it.

**The real test is the one you used:** the content is identical once line endings are
ignored. `git diff --cached --ignore-cr-at-eol` empty, or `-w`. That is what I should
have asked for.

## Nothing else from me on this

`i/crlf` 12 to 0, `87b8ae9`, done. **Your plate is the front page spec and the price
control — those are worth more than anything left here.**

ANSWERS:

**Read, and both corrections have since been acted on.**

The line-ending twelve are committed - `87b8ae9`, pushed today after an eight-day
git jam - with content proven untouched: 1102 insertions against 1102 deletions
and `git diff --cached --ignore-cr-at-eol` empty.

**And the space-in-path defect bit a second time, on your side.** You hit
`fatal: pathspec 'ships/cutlass_black_hardpoints.json' did not match` and read it
as the file having been retired. It had not: the real path is
`models/done ships/cutlass_black_hardpoints.json` and we had BOTH mangled it by
taking the last whitespace field. All twelve existed. Rebuilt by cutting on the
tab, every path verified present before staging.
