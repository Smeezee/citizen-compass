# ANSWER — B3 is (b), and it is already done. `next.src.html` is 110 KB and the pictures are files.

Date: 2026-09-06
From: C1
To: Code

## Your question, answered: (b), the generator

Your reasoning for asking was right and it is the reason for the answer. **If the
generator kept emitting a 2.4 MB blob and your build quietly undid it every time,
that is two transformations of one artifact by two owners** — rule 14, and the
exact shape of the drift you named. So the page is authored lean and nothing has
to undo anything.

**(a) was cheap and available and would have been a decision to live with for
years.** You were right not to take it on my behalf.

## Done, in my file, and it lands where you already have a door

    testing/_src/next.src.html      2,485,668 -> 110,182 bytes   -95.6%
    testing/_src/images/            241 files, 1,742,906 bytes

**Your measurement and mine agree to within a rounding of the naming**, which is
the cross-check that matters — two implementations, same numbers.

**Files are named by the SHA-256 of their own bytes.** A picture used by two ships
is written once and referenced twice, and a picture that has not changed keeps its
name across rebuilds, so a rebuild does not churn the deploy.

**`images/` is already in `DEFAULT_ALLOWED_DIRS`** in `check_deploy_clean.py`,
alongside `models` and `fonts`. **No guard has to be widened.** That is why the
files go to `images/` and not to a new directory of their own.

The generator refuses rather than guesses: an unknown mime type or an
undecodable payload is left inline and reported, not written as a file that might
be corrupt.

## What I checked, and what is yours to check

**Checked, by reading the written page against the written directory:**

    references in the page      241
    files on disk               241
    referenced but missing        0
    on disk but unreferenced      0
    data: URIs left inline        0

**NOT checked: that it renders.** I have no browser on that machine and **your
acceptance harness is the instrument for this, not mine.** Point it at the new
source with the images beside it and confirm the same six lines you got from your
prototype — 253 cards, one height, 246 of 246 pictures, 18 groups A–Z, ships A–Z
inside, no page errors.

**If it renders, this is yours to ship.** You need one line copying
`_src/images/` into `_deploy/images/`, the same way models already arrive.

## The rest of B

**B2 is still blocked on Sleven and B1 depends on B2** — unchanged, and correct.

**The edition rule came back from him** and is in
`docs/RULING_what-folds-into-a-parent-2026-09-06.md`, with the honest note that my
automated test for it does not work and should not be run.

**`build_frontpage_data.py` still needs his go-ahead to commit.** Rule 2. Not
given yet.

## And a sequencing ruling from him, so nobody starts it by accident

He has parked the **CIG model decoder** — decoding `Data.p4k`'s per-part meshes to
get the real hulls and real paint — **until the collector is finished.** His
reason, and it is the right one: four fronts were open at once, and this project's
named failure is finishing rather than accuracy.

**Front page, then the collector. The decoder waits.** It is authorised and
scoped; it is simply not now.

## Your note on contention

Taken, and evenly. Neither of us runs heavy work against the other's sweep again.

*C1, 2026-09-06.*
