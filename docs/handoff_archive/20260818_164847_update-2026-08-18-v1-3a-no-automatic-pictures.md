# Update - 3a done: nothing takes a picture on its own any more

Selftest: **517 checks, 0 failing.**

## What was actually there

The interval control was removed from the window on 2026-08-16 because "nothing
captures on a timer". The engine underneath kept firing for two more days on:

    interval          a plain timer, default 120s
    state_change      any watched field changing
    event             loading screen, client spawned, terminal open, transaction
    session burst     a run of frames for as long as a shop terminal was open
    held keys         a picture every couple of seconds while a key was down

## Removed, not disabled

`decide()` is gone entirely - the function that turned all of the above into a
capture. So are the session burst (`burstState.Begin`), the value gate, the
interval config, the `-interval-seconds` and `-interval` flags, and the settings
keys `interval_seconds`, `capture_low_value`, `burst_seconds`,
`burst_max_frames`.

**Two settings templates existed** - one in `auto.go`, one in `package.go` -
and both offered automatic capture. Both are cleaned. That duplication is worth
closing properly later; it is the one-writer rule with a copy-paste in it.

**What survives, and why:** the hotkey burst. Holding the key while a long list
scrolls is the person's own press continuing, not the program deciding. The log
tailer and detector also survive - they read every line for the diary and tell a
hotkey capture whether you were in the world.

**Held keys are now RECORDED, not photographed.** §7 wants the activity listed;
it never wanted a picture per pulse of a mining laser.

## The check that proves it

`no_auto_capture_selftest.go` drives the REAL loop with a log containing one
line of every kind that used to fire, on a clock that jumps 37 seconds per
call - so every interval this program ever had elapses many times over.

    §6: a log full of loading screens, spawns, terminals, transactions
        and state changes produces NO pictures        captured 0 times
    §6: NEGATIVE CONTROL - the same fixture with a key press DOES capture

Reading the source would not have caught the original defect: somebody read the
source and removed the control while the engine ran on. This measures behaviour.

One thing the fixture caught about itself: the template check first searched for
the key names anywhere and failed on the comment EXPLAINING that they are gone.
A check that forbids documenting a removal is pushing the wrong way, so it now
tests for an assignment line.

## Found, not fixed

`go vet` reports unreachable code at `ui.go:404`. It predates this work and is
not part of §6; flagging rather than touching it mid-item.

Not committed. 3b next: it runs itself.
