# Update - four-from-the-floor received. Running R4 first, then R1, R2, R3.

`docs/ORDER_four-from-the-floor-2026-08-23.md`, read end to end.

**R4 first**, because it is the one costing Sleven real time on every session:
returning to a list restores the exact scroll offset AND the list state - search
text, role filter, sort, highlighted row. Browser Back and the page's own "All
ships" control land in the same place. Restored on load, not after a repaint.
Every list-to-detail move on the site, not only ships.

Its negative is noted as load-bearing: **return to a list never visited this
session and assert it is at the TOP**, so a stale offset from a different list
cannot pass.

**R1 is NOT a defect and I am not treating it as one.** The Reclaimer has 15
working markers, every one resolving to a real port with a real name, and it is
ONE over H1b's invented threshold of 14. The fix is to stop counting: the solver
already answers the real question - can these be labelled without colliding -
and `solveLabels()` reports exactly that. Placement result replaces the count.
Third time tonight a working feature has been read as a broken page.

**R2** lifts brightness into the site chrome so every page has it, sharing ONE
stored preference with the ship page. The viewer's style and hull-colour
controls stay where they are: those are about the model, brightness is about the
page.

**R3** puts feedback on every page carrying its own context - ClassName, tab,
selected port, snapshot, patch - and shows the person the payload before it
sends.
