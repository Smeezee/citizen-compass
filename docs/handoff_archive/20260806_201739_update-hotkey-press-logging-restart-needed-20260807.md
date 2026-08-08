# Update: hotkey press now logged on arrival - SLEVEN MUST RESTART TO GET IT

**2026-08-07.** Committed `d314540`. Binaries rebuilt.

## ACTION NEEDED: the running session cannot see this fix

**PID 5000 is still running the binary loaded at 22:03:41.** A running process
executes the code already in memory; rebuilding the exe on disk does not change
it. **The new log line only exists after the collector is restarted.**

Since the whole point is diagnosing tonight's silent Ctrl+Alt+F9, the diagnosis
needs a restart before the next press is meaningful. Not done unasked - stopping
a live capture session is Sleven's call.

## What changed

One line, logged the instant a press is received, before the window gate and
before any capture is attempted:

```
hotkey press received (Ctrl+Alt+F9)
```

Previously the log held `hotkey registered` and then nothing until a capture
**succeeded**, so these were indistinguishable:

- the press **never arrived** - nothing reached the process
- the press **arrived and failed** - capture broke downstream

Now: press the key and look. A line means it arrived. No line means it did not.

The "no game window" path now reads `press received but no game window`, so it
presents as a consequence of an arrival rather than an unrelated event. The
failure path already carried its reason.

**On the suspected cause:** if Star Citizen in exclusive fullscreen is taking
the key before any global hotkey sees it, there will be **no line at all**, and
that is the proof. This does not fix that problem - it makes it diagnosable
rather than suspected, which has to come first.

Third instance of this defect class in this binary, after the auto log that only
wrote on capture and the hotkey that was never registered.

## Tested with the capture deliberately failing

That is the case that used to be silent, so it is the one worth proving:

```
[ok] no press means no receipt line       <- negative control
[ok] a press is logged ON RECEIPT
[ok] a failed capture states its reason
[ok] receipt is logged BEFORE the outcome
```

Order is asserted because a capture that hung forever would otherwise still
leave no evidence the press arrived.

## Live session evidence (untouched, still running)

```
[22:13:45] captured 20260807T031343Z_0024.png  <- interval:10m
[22:15:46] alive: watching ...\LIVE\Game.log, 347 bytes read since last line, 1 captures total
```

The interval fallback fired and the heartbeat's capture counter incremented -
both Job 3 features confirmed in production.

## A bad check of my own, caught and corrected

I verified the rebuilt binaries with `strings ... | grep -c` and reported
"ABSENT - binary is stale". **`strings` is not installed here**, so the command
produced nothing and the zero count meant nothing - a check that could not
succeed reporting a definite negative. Re-done with `grep -a` plus a control
string that must be present: both binaries contain the new line, 3 matches each.

Same lesson as everything else tonight - a check whose failure mode is
indistinguishable from its success mode is not a check.

## Unpushed

`8594ed3`, `c6a74a2`, `d314540`.
