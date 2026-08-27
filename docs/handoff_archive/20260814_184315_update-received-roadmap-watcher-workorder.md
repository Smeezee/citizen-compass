# Update — received the roadmap watcher work order. Building from it alone; the three superseded docs stay shut.

`docs/WORKORDER_roadmap-watcher-2026-08-14.md`, from C3. Receipt per rule 13.

Sleven: the work order supersedes `WORKORDER_rework-tripwire-build-spec` and BOTH
copies of `AMENDS_tripwire-release-view-only`, and both AMENDS now redirect here.
**I have not opened any of the three** - §7 says one of them is wrong and states
which, and reading it anyway is how the wrong instruction gets absorbed.

## What is being built

```
stage 1  GET  robertsspaceindustries.com/api/roadmap/v1/boards/1   build + schedule now
stage 2  POST robertsspaceindustries.com/graphql (deliverables)    build now, schedule on his word
cadence  every 4 hours, in config, hourly explicitly out
manual   a "check now" command that runs THE SAME code path as the timer
signal   card presence, plus a per-card payload hash
NOT      updateDate - the API says 2024, the UI says 2021, same card
surface  every result names which board it came from
```

## The five minutes §9 asks for, before building

§9 says it did NOT check whether `boards/1` is the only board, and that this is
worth checking first - if Constellation work lands on another board number,
stage 1 misses it for a reason unrelated to any decision in the order. Doing
that first.

If the endpoint is blocked from here I will report the block and build against
the documented shape rather than routing around it (rule 9).

## The three things §9 flags as unverified, which I am carrying forward as risks

- The endpoints, the no-session result and the date discrepancy all come from
  CIC and C3 did not independently confirm them. **The no-session claim is
  load-bearing for stage 2.**
- Whether `boards/1` is the only board.
- What the UI's "Updated Aug. 11th, 2021" actually reads - it is not
  `updateDate`, and whatever it is would be the better field to store.

## Second item, queued not started

Sleven, separately: the inbox watcher never overwrites, so a correction lands
under a timestamped filename nobody opens - C3 hit exactly this today with the
two AMENDS files, and it is §7 of this very order. To be fixed at the watcher
rather than by remembering. **Starting it only once the watcher build is done**,
so the two do not tangle.
