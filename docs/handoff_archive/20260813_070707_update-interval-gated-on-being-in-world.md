# Update — §2 built. The collector no longer photographs the main menu, and the interval is 120s.

`auto.go`, `gamelog.go`, `auto_selftest.go`. Builds and vets clean.

## The gate

When the game is not in the world, **no interval capture is taken at all**. No
main menu, no loading screen, no shader-optimisation wait.

**No new detection was written**, per the order. `appears_in_game` is derived
from `gamerules`, and the auto detector was already tracking `gamerules` in its
own state because a change to it is itself a trigger. The loop hands that across
to the runner; nothing new looks at a window or guesses at anything.

**One definition of "in the world", not two.** The predicate moved into
`inGameFromRules()` in `gamelog.go`, used by both the sidecar's
`appears_in_game` and the gate. Two copies would agree today and diverge the
first time one was edited — and the failure mode would be frames arriving with
sidecars saying they should not have been taken.

**Unknown fails OPEN, deliberately and out loud.** A log that has not yet stated
`gamerules` is not a statement that the player is in a menu. A wrong skip costs a
frame of real gameplay; a wrong capture costs 3 MB. Those are not symmetric, so
the tie goes to capturing, and the function says so where it is defined.

**Events and the hotkey are not gated.** If `terminal_open` resolves while the
flag reads menu, that is evidence the flag is wrong, not a reason to lose the
frame.

**The skip does not consume the interval clock.** Skipping is not taking a
picture, so entering the world produces a frame immediately rather than up to
another two minutes later.

**It says why once per state change**, not once per interval — a line every 120
seconds through a menu session is how a log stops being read.

## 60 -> 120

`defaultIntervalSeconds` and the settings template. The comment now records all
three values and what measurement moved each one, so the next person to change
it argues with data rather than taste.

**An existing file saying 60 still loads** — and now *says so*:

> `settings: interval_seconds = 60 comes from collector-settings.txt and
> overrides the built-in default of 120s. Delete the line to take the default.`

That line is new. The existing rule in this file is "never silently ignore a
setting sitting on the user's disk"; this is the same rule pointed the other
way. Without it, the only symptom of an old settings file is *"I updated and the
interval did not change"*, with nothing anywhere explaining why.

## Checks, each with its negative control

```
[ok] auto: ten minutes in the main menu produces NO interval capture
[ok] auto: and it says why, once
[ok] auto: the pause is not re-announced every interval
[ok] NEGATIVE CONTROL: in the world, the interval still fires
[ok] auto: with gamerules never seen, the interval still fires (fails open)
[ok] auto: a terminal_open captures even when the flag says main menu
[ok] auto: entering the world after a long menu captures at once
```

**The negative control is the one that matters.** "No menu frames" would be
satisfied perfectly by an interval that never fires at all — a gate that is
really an off switch. The in-world case has to fire for the menu case to mean
anything.

## Expected effect on the 818 MB baseline

Two multiplications, and I want to be honest that only one of them is
predictable:

- **120s instead of 60s halves the interval frames.** Arithmetic.
- **The gate removes an unknown but large share of them.** The measured session
  had 104 interval frames and at least one recorded its own location as *"main
  menu (Frontend_Main, not in world)"*, but I have no breakdown of how many of
  the 104 were menu versus in-world, so I will not invent a percentage.

**The real number needs a real session**, which is §9's ask and which I cannot
produce without playing the game. What I can say is the direction and the
mechanism; the figure has to be measured, not estimated.

## A pre-existing selftest failure, reported not fixed

Two checks fail, and they failed before I touched anything:

```
[FAIL] sent-rows: first export carries the one pending row   rows=309 keys=309
[FAIL] sent-rows: confirming marks exactly the exported row  marked=309
```

**This test only passes on a machine with no Star Citizen installed.** It seeds
a temp store with one fixture row, and its own comment says it is bypassing
`MineTargets()` "which scans real drive letters for a real game install". But it
then calls `BuildExport`, which calls `MineAll`, which calls `MineTargets()`
unconditionally — so on Sleven's machine it mines the 235 real logs into the
temp store and finds 309 rows where it expects 1.

The author believed they had avoided exactly this. They had not: the bypass is
one call level above where the scan actually happens.

**Not fixed here, deliberately.** It is export-path work, and the export path is
where §6's guard lands — which is held pending C1's §5 correction. Fixing it now
would mean touching `export.go` twice, the second time against a definition that
has not arrived. It should be done with §6.

**One thing I have not yet confirmed and will not claim:** whether the selftest
process exits non-zero with those two failures present. The first run reported
exit 0, which would be a silent success of exactly the kind rule 12 names — but
that reading came from a backgrounded shell whose output was truncated, so it is
not trustworthy either way. A clean run is in flight and I will report the
actual exit code rather than assume it.

Next: §3, the hotkey burst.
