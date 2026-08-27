# Update - H8 in progress: the staleness flake is measured, not guessed

Section 1 of the flake order says measure before fixing, and it reproduced on
the first attempt. A Go test harness (`citizen-collector/staleness_flake_test.go`,
a `_test.go` file, not in the shipped binary) runs the REAL fixture in a loop
under a per-run watchdog and records which named checks failed.

**Early numbers, idle machine: roughly one run in four fails**, and the four
staleness checks fail as a SET every single time - never independently. That
answers the order's question about the shape of it: one defect with three
dependants, not four defects.

Section 2's diagnosis holds up. The fixture advances a fake clock, which sets a
variable and wakes nothing, then waits four real seconds for the loop's real
one-second ticker to notice.

The fix is in: `autoDeps.pollNow` is a test-only wake channel carrying an
acknowledgement the loop closes when that poll's body has finished, so the
fixture can say "advance the clock, run one poll, tell me when it is done".
`PollSeconds` is set so high the real ticker never fires. No assertion in the
fixture now depends on elapsed real seconds.

The controls the order demands are in too, and they break the loop for real
rather than simulating it: a 1000-hour staleness window (all four must fail),
warn-on-every-poll (the "warns once" check must fail), and never-reset (the
"starts growing again" check must fail). None of those three had ever been
observed failing.

Before/after rates, idle and loaded, go in the ledger once the before-run
finishes.
