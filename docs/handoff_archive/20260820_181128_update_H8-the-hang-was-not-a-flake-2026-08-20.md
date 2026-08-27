# Update - H8 done, and the ten-minute hang was not a flake at all

## The flake, measured then fixed

|  | runs | failed | rate | hangs |
|---|---|---|---|---|
| before, idle | 120 | 38 | **31.7%** | 0 |
| before, loaded | 60 | 1 | 1.7% | 0 |
| after, idle | 2000 | 0 | **0%** | 0 |
| after, loaded | 2000 | 0 | **0%** | 0 |

The four checks failed **together, always** - 39 failing runs produced exactly
one failure set. One defect with three dependants, as the order guessed.

**The order's §2 was wrong about load, and that is why §1 exists.** It predicts
worse under load. Measured, it is twenty times worse *idle*. I did not chase
the mechanism and I am not guessing at it; the fix removes the timing
dependence entirely rather than widening a timeout, which is why 2000 clean
runs is decisive either way.

The fixture went from ~6 seconds a run to ~9 milliseconds, which is why the
after numbers are 2000 and not 200.

All three controls were observed failing on demand, and they break the **loop**
rather than the assertion. One of them taught me something: "a log that starts
growing again is NOT reported stale" **cannot detect a reset that never
happens** - with the warned flag latched the loop just stays silent and the
count never moves. It detects a reset that clears the flag but not the clock.
That is now written into the code.

## The hang, which outranked all of it

**It recurs, on every single run, and it is not the staleness fixture.**

`-selftest` was reading **the operator's entire Star Citizen log archive** -
243 files, 208 MB on this machine. `mineTargets()` scans four drives for every
Game.log and every logbackups file, and two fixtures reached it:
`runMineSchemaSelftest` (three times, to test a schema-version guard that needs
no logs at all) and `runSendIncludesCapturesSelftest` via `buildExport`.

Measured back to back: **61ms isolated, 240+ seconds not.** Whole selftest:
**13-15 seconds isolated, never returned without it.**

So "ran fine twice, hung the third time" was never random. The duration is
proportional to how much the person has played - it gets slower every session
until it crosses whoever is watching's patience. That is what a straight line
looks like from outside.

And it is not only speed. A selftest that reads a person's whole log archive is
a surprise nobody asked for, whatever it does with the contents.

Fixed once at the top of `selftest()`, not per fixture - the second offender
was only found because the first was fixed. Six consecutive full runs
afterwards: 13-15s, 574 checks, identical, one failure each, and that failure
is the CONSOLE subsystem check correctly refusing a console build.

**No release cut, nothing installed, and the repo's collector binaries were NOT
rebuilt** - every measurement used a probe binary built outside the repo. The
shipped binaries are now behind this source. Your call to close.
