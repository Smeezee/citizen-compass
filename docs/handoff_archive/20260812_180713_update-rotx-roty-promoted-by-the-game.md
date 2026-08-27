# Update — the game proved two axis names we had warned people about. Corrected in the shipped data.

C1's finding: Star Citizen loaded a from-defaults profile and wrote it back out,
including `js1_rotx` and `js1_roty`.

## This was live misinformation, and it mattered

The deployed keybind page was telling anyone who bound a view axis:

> **unattested — never seen in a real profile**

`rotx` and `roty` were recorded UNATTESTED because they were absent from CIG's
`defaultProfile.xml` and from both real player profiles. **The game has now
written both of them itself**, which is stronger evidence than either source we
had — not "we found it in a file", but the game asserting the name is valid.

Those are the view-axis bindings, i.e. exactly what somebody setting up a HOTAS
binds. The page was discouraging a binding that works.

**Corrected** — both now PROVEN, noted as *"round-tripped through Star Citizen
itself, 2026-08-12"*. Verified there is no stale claim left in the source or the
build.

`slider2` stays UNATTESTED and is now the only unproven name. Still absence,
still weak evidence, still **not** a claim the game refuses it.

## The distinction paid for itself

This is why UNATTESTED was never allowed to mean "invalid". Both names turned
out to be fine — merely unobserved. Had the table said "rejected", the page
would have talked somebody out of a working binding, and nobody would have found
out. That reasoning is now written into the generator beside the entries, with
the date it was vindicated.

## What I did NOT change, and why it is a question rather than an omission

**`verified: false` in `sc_export.js:359` is untouched.** Two reasons:

1. `sc_export.js` is explicitly off-limits under the standing orders, and no
   order has rescinded that.
2. **The flag's meaning is genuinely ambiguous now, and that is C1's call, not
   mine.** If it means *"a file this tool generated has been loaded by the
   game"* — that is now TRUE. If it means *"these bindings are known to behave
   correctly in flight"* — that is still FALSE, and C1's own finding says so:
   *"the game accepting a file and the controls doing the right thing in a
   cockpit are two different claims."*

Flipping it on my own reading would be the same shape of error as the axis table:
asserting something stronger than the evidence. **Naming it as an open question
instead.**

## §5's rule is worth keeping and is not yet enforced anywhere

`v_pitch -> js1_y` was absent from the game's export because `y` is the stock
default for pitch, and an actionmap records only what differs from default.
**Accepted, then correctly omitted as redundant.**

Nothing in `roundtrip.js` or `mutate.js` knows that. A future round-trip check
that compares a from-defaults export against the game's output **will report
false losses, confidently** — the exact silent-success shape this project keeps
finding, only inverted. It would need to compare against
`data-layer/processed/defaultProfile.plain.xml`, which is already in the repo.
Not building it unasked; flagging it as the trap it is.

## State

Build and guard clean, `roundtrip.js` ALL CHECKS PASSED, `mutate.js` 19/20 M18.
**Not deployed** — the corrected table is in the build, waiting on a go-ahead.
