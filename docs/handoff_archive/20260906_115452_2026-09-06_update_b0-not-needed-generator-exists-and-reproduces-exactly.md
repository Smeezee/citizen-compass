# Update - B0 IS NOT NEEDED. `build_frontpage_data.py` was never thrown away, and it reproduces frontpage_data.json byte for byte.

## The order's premise

> `frontpage_data.json` was made by a script that is not in this repository.
> `find . -name build_frontpage_data.py` returns nothing. The tool was thrown
> away. 254 ships, every price, every dealer, every outline - and **nobody can
> regenerate any of it.**
>
> Everything else in Job B is decoration until this is fixed. Rebuild
> `build_frontpage_data.py`...

## It is there

    -rwxr-xr-x  5,270 bytes  Aug 30 21:06  build_frontpage_data.py   (repo root)
    $ find . -name "build_frontpage_data.py"
    ./build_frontpage_data.py

**It is UNTRACKED - git status shows `?? build_frontpage_data.py`.** That is
almost certainly why it read as absent: it is invisible to anything that asks
git rather than the filesystem. It has been sitting in the working tree since
2026-08-30 and its own docstring says **`Writer: C1.`**

## And it regenerates the file EXACTLY

B0 asks that "the first run must be diffed against the current file". Done, and
done safely - a COPY of the script with its `OUT` constant repointed at the
scratchpad. **The real `frontpage_data.json` was never opened for writing and
`build_frontpage_data.py` itself was not modified.** It is C1's file.

    front page ships 254   with hull figures 219   with traced outline 201
    dealers placed from the game's own starmap: 5   systems: nyx, pyro, stanton
    refused joins (named, not guessed): ['Javelin', 'MOTH']

    regenerated  1,836,783 bytes   sha b4d1c000e1b493f4
    on disk      1,836,783 bytes   sha b4d1c000e1b493f4
    BYTE-IDENTICAL

Exit 0. No fuzzy matching - its docstring states the one normalisation, says the
collision check was run first and came back zero, and it names the two refusals
rather than guessing them.

## So B0 shrinks from "rebuild it" to two much smaller things

1. **Commit it.** It is C1's file and it is untracked, which is the entire
   defect. **I have not staged or committed anything** - rule 2, and it is hers.
2. **The MANIFEST gap is real and unchanged.** The folder still carries no
   `MANIFEST.json` where every other derived folder has one.

**I did not rebuild it and I am not going to.** Rewriting a working generator
from scratch, against a premise that a two-minute check disproves, would have
produced a second writer for C1's artifact - rule 14 - and risked "a rebuild that
silently changes 254 rows", which is the exact failure the order warns about.

## Still blocked on the deploy, and the picture is now clean

    _verify_broken_checker_end_to_end.py   RESOLVED - it was my contention.
        Re-run alone: exit 0, all 10 assertions passed. I had ~100 node probes
        running against a live sweep; it took 2377s against 1885s. Not a defect,
        and my own ordering finding turned back on me.

    _verify_correspondence.py              STILL RED - C1's, confirmed. It is in
        the "C1 - Cowork" block of OWNERS.md at line 125. Four files in
        answered/ with Status 'open' and no ANSWERS: line. Reporting, not
        touching her correspondence.

`next.html` is built, verified and waiting. One control stands between it and
the testing host, and that control is not mine.
