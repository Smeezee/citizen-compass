# Update — Q45 is master-only, and the crew binary is proven not to contain it. Symbols and strings, both directions.

**2026-08-30 08:20 UTC / 2026-08-30 03:20 local · Code (background session)**

Sleven's ruling applied: `//go:build master` on both files, `pairs/` written by
the master build only, and **absent from the crew binary rather than compiled
and disabled.**

## THE PROOF, BOTH DIRECTIONS

    go tool nm            crew   master
      StorePair              0      2
      NewPairStore           0      1
      ContextAllowed         0      2
      runPairStoreSelftest   0      2
      pairContextAllowed     0      1

    strings only this store would put in a binary
      pairs.jsonl                    0      1
      item_inspect                   0      1
      ground_prompt                  0      1
      "is not on the recorded list"  0      1

    crew   11,747,840 bytes
    master 11,788,288 bytes

**Measured in both directions on purpose.** A search that came back zero for
both builds would prove only that I was looking in the wrong place; the master
column is what makes the crew column mean something.

    crew   --selftest  exit 0
    master --selftest  exit 0

## HOW IT IS WIRED, AND WHAT IT DID NOT FORK

The call site left shared `main.go` and went behind `runVariantSelftests`,
**defined in both variant files** - the pattern `masterOnlyCommands()` and
`registerBenchFlags()` already use. Real in `variant_master.go`, empty in
`variant_crew.go` with the reason written at the site.

**Nothing was forked.** Capture, logging, the send path and the scrub layer are
untouched and remain one implementation each. The only shared file that changed
is `main.go`, by six lines, and it now names a hook rather than a feature.

## ONE THING I AM FLAGGING RATHER THAN DECIDING

`package.go`'s `packageExcluded` still carries `"pairs"`, and `package.go` is
shared - so the literal string `pairs` appears in the crew binary twice.

**It is not the pair store**, and every symbol and distinctive string of the
store is absent. But the ruling says *"must not contain it at all"*, so the
question is whether a defensive exclusion entry counts.

**My read: it should stay.** It costs nothing, it is documentation of a decision
in the place someone will look, and if a crew binary ever packaged a folder that
a master build had written, that entry is what keeps `pairs/` out of the zip.
**Removing it would make the crew build safer in appearance and less safe in
behaviour.** If that reading is wrong, say so and it comes out in one line.

## STILL PENDING

The website's find-checksum and picker fixes are built and uncommitted, waiting
on one clean sweep - the last one measured a moving tree while C1 edited eight
`_src` files mid-run.
