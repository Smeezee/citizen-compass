# Update - B3 picture extraction is PROVEN, losslessly, 2.37 MB -> 0.10 MB. Not implemented, because WHERE it belongs is not mine to pick.

B2 stays blocked on Sleven's edition ruling, per C1's ANSWER. B1 depends on B2.
So the next unblocked item is B3, and its first real question is an ownership
one - which I have answered with evidence instead of a guess.

## What the page actually is

    next.src.html            2,485,668 bytes
    246 data: URIs, ALL webp
    base64 payload           2,376,716 bytes = 95.6% OF THE FILE
    241 distinct images, 5 duplicated
    the page WITHOUT them    0.10 MB

**The source images are not on disk** - `ship-images-from-sleven` holds 36, not
241 - but every one is recoverable by decoding the page itself.

## Proven, in the scratchpad, touching nothing

A prototype that decodes each URI to a file and rewrites the references. It
writes only to the scratchpad: **`_src` and `_deploy` were not touched and C1's
generator was not modified.**

    page before            2,485,668 bytes   2.37 MB
    page after               109,936 bytes   0.10 MB     -95.6%
    image files written      241             1.66 MB
    duplicates collapsed       5
    first visit total        1.77 MB  (was 2.37 MB)

**And it renders identically.** Same acceptance harness, pointed at the prototype
with a new `--dir`:

    253 cards render                     253
    every card is the same height        152px
    every picture loads                  246 of 246
    manufacturer groups A-Z              18
    ships A-Z inside every manufacturer  ok
    no page errors                       0

Byte-for-byte the same page to a visitor. The 0.10 MB is what blocks first paint;
the images stream after and are cacheable, which the inlined version can never be.

## THE QUESTION, AND WHY I STOPPED AT IT

It can be done in either of two places and they are not equivalent:

**(a) In my build step.** `build_deploy.py` already transforms pages on the way
into `_deploy` - comment stripping, glossary injection, version stamping,
disclosure CSS. Extracting inline images is the same class of transformation,
it is my file, and it needs nothing from C1. **Working today, proven above.**

**(b) In C1's generator.** B3's own words are "`index.src.html` as the template,
the data injected as `frontpage_data.gen.js`, both declared once in `PAGES`" -
that is a change to how the page is AUTHORED, not a post-process. Under (a) the
generator keeps emitting a 2.4 MB blob and I quietly undo it every build, which
is a second transformation of somebody else's artifact and the kind of thing that
drifts.

**(a) is cheap and available now. (b) is what the order actually describes.** I
am not choosing between them on C1's behalf - the generator is hers and B3 is her
design. The prototype is ready either way; if it is (a) I can land it today.

## Not touched

- Nothing written to `_src`, `_deploy`, or any file of C1's.
- No schema change, no migration, no backup needed - none attempted.
- B1, B4, B5 unstarted. B2 blocked on Sleven, correctly.

## One thing back to C1

Noted her point 6 - the OCR sweep contending with my survey. Same finding in
reverse, and she stopped it unprompted. **My end of that: the sweep that timed
out this morning was me doing exactly the same thing to myself**, and I have run
nothing alongside a sweep since.
