# Update - order filed for the intermittent staleness selftest

**2026-08-20** - Sleven asked for the G7-FINDING to become a real order rather
than a ledger note. Filed:
`docs/ORDER_collector-staleness-selftest-flake-2026-08-20.md`.

Not started, not fixed - the collector was out of scope for the 08-19 run and
still is. This is the write-up.

What the order establishes, from reading the fixture rather than guessing:
the flake is a race between a FAKE clock and a REAL ticker.
`fakeClock.Advance` (gamelog_selftest.go:37) sets a variable and notifies
nothing; the loop only notices at its next real 1-second tick (auto.go:912,
PollSeconds: 1 at gamelog_selftest.go:196); the assertion waits four real
seconds. Idle that always works, loaded it does not.

Two things worth knowing that came out of writing it:

1. **The four failures are one defect plus three dependants.** The last two
   report NOT PERFORMED *because* the first never fired - the fixture gates
   them deliberately.
2. **The quieter half is the worse half.** The two "must not increase" checks
   sleep for real and then assert a count did not change, so under load they
   pass *because nothing has run yet*. They fail spuriously in the safe
   direction and pass spuriously in the dangerous one. Only the visible
   direction had been noticed.

Also recorded: somebody has been here before. A comment at
gamelog_selftest.go:259 documents this exact intermittency and closed the
dangerous consequence - two false PASSes became two honest NOT PERFORMEDs.
The order says explicitly not to undo that gate; the fix goes underneath it.

The order leads with MEASURE, not fix: a flake that reproduces once in forty
cannot be shown fixed by running it twice, and there is no second chance to
collect a "before" number. Every fix item carries a control that must be
observed failing on demand - including the obvious wrong fix, which is
widening a timeout until nothing ever fails.

The 10-minute hang from run 3 is in there as §5, flagged as observed and NOT
diagnosed, with the note that if it recurs it outranks the rest.

**Not committed.** Rule 2 - the commit/push go-ahead covered the 08-19 G order
and does not carry over. The file is in the working tree and in docs/.
