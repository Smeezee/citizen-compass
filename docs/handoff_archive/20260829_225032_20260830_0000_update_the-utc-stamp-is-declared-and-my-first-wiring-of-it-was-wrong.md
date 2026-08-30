# Update — the UTC date stamp is a declared injection now, narrowed twice, and my first wiring of it compared a file against itself.

**2026-08-30 04:00 UTC / 2026-08-29 23:00 local · Code (background session)**

Option A, as Sleven asked. `build_deploy.py:741` stamps the UTC date into
`index.html` twice; across 00:00 UTC a rebuild is not byte-reproducible, and
section 4's whole proof is "rebuild and require the bytes not to move".

## DECLARED AS NARROWLY AS THE VENDOR MARKER AND THE TRADEMARK STRIP

Tolerated: **`index.html`, the literal text `testing <ISO date>`, the same
number of occurrences on both sides, every stamp in a file agreeing with every
other, and EVERY OTHER BYTE IDENTICAL.** Anything else is not this.

    stamp only, both occurrences   ACCEPTED
    stamp + a hand edit            refused - changed somewhere other than the stamp
    only ONE occurrence moves      refused - the stamps within one file disagree
    an extra stamp appears         refused - the stamp count changed: 3 -> 2
    identical files                refused - the stamps are not the difference
    a hand edit, no stamp move     refused - the stamps are not the difference

**The third row is a hole I opened and closed.** My first version tolerated one
stamp moving while the other did not - "only the stamp changed" is true of that,
and it is also a page telling a viewer two different things about which build
they are looking at. The build substitutes both from one `_stamp`, so they
cannot legitimately disagree.

## AND THE WIRING WAS WRONG BEFORE IT WAS RIGHT

The first version called the comparison **after** the `finally` that restores
`_deploy`. So it compared the snapshot against the file the snapshot had just
been restored onto - itself - and reported *"the stamps are identical"* on a
plant designed to make it fire.

**It only surfaced because the plant was supposed to go GREEN and went red.**
A test that expects a pass catches a class of defect that a test expecting a
failure never will: I would have shipped a declaration that could not fire and
believed it worked, because everything I had run until then was supposed to
fail. The comparison is now taken inside the try, before anything is put back,
and the comment at the site says why.

## PROVEN END TO END, NOT JUST IN A UNIT

    planted the 08-29 stamp        PASS + "DECLARED: the testing date stamp
                                   moved (2 occurrence(s), every other byte
                                   identical)"
    planted stamp + a hand edit    FAIL - "it is NOT the declared stamp: the
                                   file changed somewhere other than the stamp"
    clean run                      exit 0
    --self-test                    exit 1, correct

`testing/_deploy/index.html` was restored to the real build afterwards and the
hash checked against the copy taken before the plants: `0fe83cfc32c3` both
sides.

## STILL TRUE, AND NOT FIXED BY THIS

**The served site and the local payload still differ by that stamp** - the
deploy shipped `08-29`, local says `08-30`. This makes the drift control honest
about it; it does not make them match. And `sweep_gate.py`'s fingerprint is
still content-based, so a clean receipt still goes stale at UTC midnight.
Both are in the finding.
