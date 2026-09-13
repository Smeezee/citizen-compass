# FINDING — this desk's own web fetch served a stale file, and it nearly became a report that a desk was wrong

    from    C1, architecture, 2026-09-12
    status  Caught before it reached him. Recorded because it is the third
            read-surface to lie tonight and the first one that was mine.

---

## WHAT HAPPENED

**Design reported the corrected BRIEF-001 live on GitHub**, with a revision change and
every corrected fact enumerated.

**This desk fetched the raw file to verify and got the OLD content** — ten parent ships,
no G12 note, no revision marker. **On that basis the next sentence was going to be that
she was wrong.**

## WHAT WAS ACTUALLY TRUE

**Checked by a second instrument — the file's commit history in a real browser:**

    21da1f7   BRIEF-001 corrected: CIG's own support table, fourteen parents,
              the canary kept
    f44a1cd   The Design desk's first brief goes out

**Two commits. The correction was pushed. SHE WAS RIGHT AND THE FETCH WAS WRONG.**

## THE CAUSE, AND IT IS DOCUMENTED

**The fetch tool caches responses per URL for fifteen minutes, and GitHub's raw endpoint
sits behind its own CDN cache on top of that.** This desk had fetched that exact URL twice
in the preceding twenty minutes while checking whether the push had landed. **Every one of
those checks warmed a cache that then answered the question wrongly.**

**Checking repeatedly made the instrument LESS reliable, not more.** That is the part
worth remembering.

## THE RULE THIS EARNS

**A cached read is not a current read, and the tool that caches does not say so in its
answer.** Same family as: a write receipt is not a delivery; a clean reconciliation is not
correctness; a path in a memo is not a location.

**For anything where CURRENCY is the question — has it landed, has it changed, is it
there yet — use an instrument that cannot cache: the commit history in a real browser, or
the file on disk.**

**Third read-surface to lie tonight.** RSI's store pages returned a shell that looked like
a loaded page. A bridge write reported success and left the previous version. And now
this. **All three looked like success.**

*C1, 2026-09-12.*
