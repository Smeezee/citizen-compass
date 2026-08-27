# Update — §3 built. One press of Alt+F3 is a burst, on the existing burst machinery, and a press still always yields a frame.

`session_burst.go`, `auto.go`, `main.go`, `burst_selftest.go`. Builds, vets and
formats clean.

## One burst implementation, one instance

The order was explicit: build on `session_burst.go`, do not write a second burst
path. I went further than "same file" — **the hotkey burst uses the same
`burstState` instance the terminal burst uses.**

That is what makes *"never start a second overlapping burst"* true by
construction rather than by a rule somebody has to remember. Two instances would
have been a second burst implementation wearing the first one's type, and the
two could have been shooting at once — the exact ambiguity that file's own
header warns about.

`cfg` became per-burst, because the two kinds want different rhythms: a terminal
is followed patiently for as long as it is open; a press means "this screen,
right now".

## The choices §3 left to me, and which way I went

**A second press EXTENDS.** The order allowed extend-or-ignore provided the log
says which. Extending matches what the key is for — 30 presses in one session,
nine of them inside twelve seconds, is somebody saying *keep going*, not *start
again*. It pushes the ceiling out, resets the idle clock, and keeps the frames
as one record under one press number. The log says `burst extended by press #2 -
now up to 12 frames`.

**A deliberate press outranks the log.** If a terminal opens mid-burst it does
not take over and relabel a person's frames. The terminal burst can start when
theirs finishes.

**Defaults: 6 frames, 1 per second.** Both are settings —
`hotkey_burst_seconds` and `hotkey_burst_frames`. The right numbers depend on
how fast Sleven actually scrolls a commodity board, which nobody knows yet, so
these are a starting point to be measured against rather than a judgement.
`hotkey_burst_seconds = 0` restores one press, one frame.

**The settings are read with the `found` check**, which matters here more than
it looks: `main.go` already carries the scar. `burst_seconds` was once read
without it, so every settings file predating the key set the frame interval to
0 — the documented way to switch bursting **off**. The feature was dead on
arrival on every machine and looked like one that had not been reached yet.

## The bug I caught by reading the control flow, not by testing

**Burst frames are produced by `decide()`, and `decide()` runs BELOW the loop's
window gate. The hotkey case sits above it.**

So routing the press purely into the burst would have quietly removed the one
guarantee the key has: press it, get a frame. With the game minimised or closed,
a press would have logged *"burst started"* and captured nothing. Nobody would
have found that until it mattered.

**The press now takes frame 1 itself, on the old path above the gate**, and the
burst supplies the rest. It is numbered as frame 1 *of that burst* rather than
dressed as a separate one-off, so the sidecars still reassemble into one record.

## Every frame can be put back together

`Press` and `Index` are new sidecar fields (`burst_press`, `burst_index`). A
burst that cannot be reassembled afterwards is the same data with the
relationship thrown away — a handful of frames a second apart with nothing
saying they belong together.

## The loop needed a second reason to WAKE, not a second reason to capture

The poll is 2s; a 1-frame-per-second burst cannot be delivered by that ticker,
so a rate somebody configured would have been silently halved. A 250 ms ticker
now runs *while a burst is active*, and everything it wakes goes through the
same `decide()`. It produces no frames of its own.

## Checks — 12, all passing, and all proven able to fail

```
[ok] a press starts a burst and says so
[ok] the press itself yields frame 1, so a press always captures
[ok] one press yields several frames, capped at the ceiling
[ok] every frame names the trigger, the press and its index
[ok] NEGATIVE CONTROL: a terminal frame is not labelled as a hotkey burst
[ok] an EXTENDING press does not start a second frame-1
[ok] a second press EXTENDS, and the log says which happened
[ok] two presses produce ONE burst, not two overlapping ones
[ok] the extended burst is still reassemblable - no repeated index
[ok] a terminal opening does not relabel a press mid-burst
[ok] hotkey_burst_seconds = 0 restores one press, one frame
[ok] NEGATIVE CONTROL: with bursting on, the same press DOES start a burst
```

Rule 12, three mutations, each reproducing a defect the order named — every one
caught, and `session_burst.go` restored byte-for-byte afterwards:

```
PASS  M1 a second press starts a second burst instead of extending
PASS  M2 frames stop naming their press and index
PASS  M3 a terminal opening takes over a burst the person started
PASS  session_burst.go restored byte-for-byte
PASS  and the checks pass again
```

## One thing I did and then undid, on purpose

I wrote a `go test` entry point so these twelve checks run in 0.2 s instead of
waiting eight minutes for the window and hotkey sections of `-selftest`. It
worked, and it is how the mutations above were run.

**Then I moved it to `_to_delete/`.** The collector has no `_test.go` files at
all — it deliberately uses one mechanism, `-selftest` with `check()` callbacks —
and quietly introducing `go test` as a second way to run the same checks is a
convention change, which is Sleven's call and not mine. The checks themselves
are registered in `-selftest` where they belong.

It is sitting at
`_to_delete/zz_burst_focus_test.go_scratch_diagnostic_20260813` if he wants it;
it is eleven lines and it makes the fast checks fast to run.

## Not verified

**No hardware and no real session.** Every check above is synthetic time against
the real `burstState`. Whether 6 frames at 1/second is the right shape for
scrolling an actual commodity board is exactly the thing that needs Sleven and a
kiosk — which is why both numbers are settings rather than constants.

The full `-selftest` is still running (the window and hotkey sections take
minutes); I will report its verdict rather than assume it.
