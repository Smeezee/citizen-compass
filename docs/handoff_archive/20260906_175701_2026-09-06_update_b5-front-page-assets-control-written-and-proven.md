# Update - B5 started. One control written and PROVEN: the front page's pictures are real, and any page showing CIG artwork says where it came from.

B2 is blocked on the five hand-entered families, B1 sits behind B2, B3 shipped.
B5's checks are the unblocked work, and three of its six are writable today.
**Written the one that guards what is live on testing this minute.**

    checks/_verify_front_page_assets.py       RULE16: INDEPENDENT

## What it asserts

    1  every picture the built pages ask for exists on disk
                                              241 referenced, 0 missing
    2  every picture's NAME matches its own CONTENT
                                              241 hash-named, 0 lying
    3  every page that shows ship artwork carries the source and takedown notice
                                              next.html, 241 pictures, notice present

## Why 2 is worth more than "the file exists"

C1's generator names each picture by the SHA-256 of its own bytes, which turns
the filename into a **verifiable claim** rather than a label. A truncated upload,
a half-written copy or a swapped file all keep the name and change the bytes -
existence alone passes every one of those. This recomputes the hash and tests the
claim.

## Rule 16, and it is INDEPENDENT rather than a comfortable label

    the references     read out of the BUILT page's text
    the pictures       read off the FILESYSTEM
    the name's claim   tested against the file's OWN recomputed bytes
    which pages must   derived from what each page SHOWS - pages that reference
    carry the notice   ship imagery - and NEVER from build_deploy.py's
                       _SHIP_CONTENT_PAGES

**That last one is the point.** Reading `_SHIP_CONTENT_PAGES` would prove the
build agrees with itself and nothing more. If somebody drops `next.html` out of
that set, this control still finds a page full of CIG artwork with no notice, and
still goes red. The order called that "the one failure on this list that is not
recoverable by a later build" - now something watches it.

## Rule 12 - PROVEN, and against a damaged COPY

`--prove` builds a small tree in the scratchpad, breaks exactly one thing, and
runs this file against it as a subprocess so the EXIT CODE is proven too:

    ok   the undamaged copy passes - or nothing below means anything    exit 0
    ok   one picture removed -> 'every referenced picture is present' fails  exit 1
    ok   one byte flipped, name unchanged -> the hash claim fails       exit 1
    ok   the source notice stripped -> the artwork page is refused      exit 1
    ok   images/ absent -> NOT PERFORMED (exit 2), never a pass         exit 2

**testing/_deploy is never opened for writing**, so there is no restore to
interrupt and no `restore_pending` journal to recover. Controls here have
historically mutated the live tree and restored it; that is where an interrupted
restore comes from, and this one avoids the failure mode rather than handling it.

## A LIMIT I WROTE INTO THE FILE RATHER THAN LEAVE TO BE FOUND

**This control reads `testing/_deploy` and does not rebuild it, so it is an
instance of the ordering hazard I filed this morning, not an exception to it.**
Run inside the sweep, another control could be mid-rebuild and this one would
report a picture missing that is not missing.

The hash assertion is immune - it compares bytes to name, both read from the same
directory at the same instant. The reference assertion is not. Both facts are in
the file's header.

## State

    123 checks, 0 unlabelled, 0 malformed rule-16 labels
    the new control is discovered by the sweep and passes standalone

Full sweep running to confirm it in context. **Nothing shipped** - this is a
check, the payload is untouched, and the deployed site is unchanged since 16:39.

## Still blocked, unchanged

B2 on five hand-entered families (CSV-FM, RAPTOR, Starlancer BLD, Hurricane,
Intrepid). B1 behind B2. `build_frontpage_data.py` untracked, needs Sleven.
The 241 unreferenced images await his word - rule 5 list filed, nothing moved.
