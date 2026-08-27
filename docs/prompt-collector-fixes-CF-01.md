# Code job CF-01 rev 3 — four collector fixes, in this order

    for      Claude Code
    from     C1, 2026-08-07
    rev      3 - THE HOTKEY IS SOLVED. Sleven ran a one-variable experiment:
             DX11 instead of Vulkan, everything else identical. The hotkey
             works on DX11 and does not on Vulkan. Section 2 is rewritten
             around that result; capture is proven fine on Vulkan and only
             input fails. Revs 1 and 2 are superseded IN PLACE, per hard
             rule 14 - there is no addendum and there never will be one.
    repo     citizen-compass / citizen-collector
    approved Sleven, 2026-08-07: "I 100% am down with making it 60secs and I do
             want to get the bugs fixed and the hotkey fixed as well."

**Read this whole file before writing anything.** Two of the four jobs are not
what an earlier session said they were, and the evidence for that is quoted
below rather than asserted.

**Evidence base.** `citizen-collector/collector-auto.log`, 8,610 lines, covering
2026-08-06 through the PTU 4.10 session on 2026-08-07 16:16-16:59 local. Every
count and timestamp in this document was read out of that file. Do not take my
word for any of it — the greps are given so you can re-run them.

---

## 0. WHAT IS ALREADY RIGHT — do not "fix" these

The last round of work landed and it is the only reason this job can be written
precisely instead of speculatively. Leave it alone:

- **The heartbeat.** `alive: game running, watching <path>, N bytes read since
  last line, N captures total`. 148 of them in the log. This is what proved the
  collector was awake, which install it was on, and whether the log was growing.
- **The `hotkey press received` line, logged on receipt before anything is
  attempted.** The comment above it in `auto.go` explains why it exists. It is
  the single most valuable line in the file — see §2.
- **The supervisor and the unclean-shutdown notice.** `PREVIOUS RUN DID NOT SHUT
  DOWN CLEANLY. It was pid N, started …, and left no shutdown line.` This is how
  the crash became measurable.
- **PTU auto-detection.** It works, and it worked during the live session:

      16:16:53  startup: watching …\LIVE\Game.log (found by scanning known install locations)
      16:17:59  watching …\PTU\Game.log (derived from the captured window's process image path)

  66 seconds from launch to the correct install. That is fine. Do not touch it.

---

## 1. THE CRASH — `too many callback functions`

### The evidence

    $ grep -c "too many callback functions" collector-auto.log
    28

Three of those 28 are inside the PTU session, and the supervisor timed every one:

    16:30:55  supervisor: collector STOPPED UNEXPECTEDLY after 14m2s (exit status 2) - restarting in 2s
    16:45:01  supervisor: collector STOPPED UNEXPECTEDLY after 14m4s (exit status 2) - restarting in 2s
    16:59:07  supervisor: collector STOPPED UNEXPECTEDLY after 14m4s (exit status 2) - restarting in 2s
    17:29:57  supervisor: collector STOPPED UNEXPECTEDLY after 14m0s (exit status 2) - restarting in 2s

14m2s, 14m4s, 14m4s, 14m0s - the fourth one landing during the DX11 test, so it
is not renderer-dependent either. That is not a race and not a memory leak. That
is a fixed budget being spent at a fixed rate.

The stack names the caller:

    main.findGameWindow(...)
    syscall.NewCallback(...)
    fatal error: too many callback functions

### The cause, confirmed from source

`winapi.go` line 259:

```go
// EnumTopWindows walks every top-level window. Callback returns false to stop.
func EnumTopWindows(fn func(h HWND) bool) {
	cb := syscall.NewCallback(func(h HWND, _ uintptr) uintptr {
		if fn(h) {
			return 1
		}
		return 0
	})
	syscall.SyscallN(procEnumWindows.Addr(), cb, 0)
}
```

`syscall.NewCallback` allocates out of a **fixed, process-lifetime table that is
never freed**. This function allocates a fresh one on every call, and
`findGameWindow` calls it on the 2-second poll tick. ~420 calls a minute × 14
minutes ≈ the cap. The arithmetic matches the observed 14m2s exactly.

This is the only `NewCallback` call site in the collector:

    $ grep -rn "NewCallback" citizen-collector/
    winapi.go:261

### The fix

One package-level callback, created once, dispatching through a guarded
package-level function pointer. Sketch, not gospel — write it the way you think
is right, but it must allocate exactly one callback for the life of the process:

```go
var (
	enumMu       sync.Mutex
	enumFn       func(HWND) bool
	enumCallback = syscall.NewCallback(func(h HWND, _ uintptr) uintptr {
		if enumFn(h) {
			return 1
		}
		return 0
	})
)

func EnumTopWindows(fn func(h HWND) bool) {
	enumMu.Lock()
	defer enumMu.Unlock()
	enumFn = fn
	defer func() { enumFn = nil }()
	syscall.SyscallN(procEnumWindows.Addr(), enumCallback, 0)
}
```

`EnumWindows` is synchronous — it does not return until the enumeration is
finished — so holding the mutex across the call is correct and not a deadlock
risk. Say so in a comment, because the next reader will wonder.

### Acceptance, and hard rule 12 applies

**A check that cannot fail is not a check.** A test that runs `EnumTopWindows`
100 times and passes proves nothing, because 100 was always fine.

- **Positive:** call `EnumTopWindows` **at least 3,000 times** in one process and
  assert it does not die. That is roughly 100 minutes of real polling, compressed.
- **Negative control, required:** a second test that calls `syscall.NewCallback`
  directly in a loop and **asserts the process would have exhausted the table** —
  i.e. demonstrate the failure mode still exists and that the fix is what avoids
  it. If you cannot make the negative control fail, the positive test is
  measuring nothing and you should say so rather than ship it.
- Add it to the existing selftest suite so it runs with everything else.

**Also fix the supervisor's wording while you are here.** It currently says a
crash means "killed from outside (Task Manager, a script, sign-out) or it crashed
hard." Tonight it was neither of those in any useful sense — it was a known,
diagnosable defect. If the process dies with a Go `fatal error:` on stderr, the
supervisor should say so and quote the first line of it, not offer a list of
guesses.

---

## 2. THE HOTKEY — SOLVED, by Sleven, with a one-variable experiment

### It works, and here is the proof

    [2026-08-07 17:28:39] hotkey press received (Alt+F3)
    [2026-08-07 17:28:40] captured 20260807T222839Z_0054.png  <- hotkey (manual)
    [2026-08-07 17:28:42] hotkey press received (Alt+F3)
    [2026-08-07 17:28:44] captured 20260807T222843Z_0055.png  <- hotkey (manual)
    [2026-08-07 17:30:16] hotkey press received (Alt+F3)
    [2026-08-07 17:30:18] captured 20260807T223017Z_0056.png  <- hotkey (manual)

Three manual captures, zero failures. Before this the counter had never left
zero across 40 registrations.

### The variable was the RENDERER, and nothing else

**Sleven changed one thing: he ran Star Citizen on DirectX 11 instead of
Vulkan.** Not elevation. Not the display-mode setting — he was borderless for
both. One variable, clean result:

    Vulkan  →  registers, never delivers a press
    DX11    →  registers, delivers every press

### What that means, and the correction it forces

Rev 2 declared the fullscreen theory dead because the game was borderless. **That
was too strong, and this is the correction.** Vulkan applications can hold true
exclusive presentation through `VK_EXT_full_screen_exclusive` **regardless of
whether the window is styled borderless**. Windows sees a borderless window; the
presentation path is exclusive anyway. So the display-mode setting in the game's
menu was never the thing that decided this — the renderer was.

This is now the fourth explanation for this bug. It is the first one with a
controlled experiment behind it rather than a plausible story, which is why it is
being written as a finding and the previous three were not.

### The separation that matters most — capture is fine, input is not

The 16:16-16:57 PTU session ran on **Vulkan**, and it captured:

    16:18:22  captured …_0040.png  <- state_change:gamerules ""->"SC_Frontend"
    16:30:12  captured …_0045.png  <- interval:10m
    16:55:05  captured …_0047.png  <- interval:10m

**So the capture path works under Vulkan. Only the input path fails.** That is a
real narrowing and it retires the open worry from
`claude/FINDING_gamelog-is-a-data-source-4.9-vs-4.10.md` §3 that DXGI/WGC/GDI
might all need re-verifying against the new renderer. They do not. Do not spend
time there.

### DX11 is a workaround with an expiry date — do not treat it as the fix

Star Citizen 4.10 moved to Vulkan as its renderer; 4.9 was DX11.1. CIG is
retiring the DX11 path. **Telling a user "run DX11" is a fix that stops working
on a schedule we do not control, and it asks them to give up the renderer CIG is
shipping.** It is fine as tonight's unblock. It is not the answer.

### 2a. Log the renderer, the window, and the elevation — build this

Once the game window is found, record once per session:

- **the renderer.** `Game.log` states it plainly at startup. This is the single
  most valuable line and it is free — no Win32 call needed, just a parse of a
  file already being read.
- window style and extended-style flags; whether the window rect equals the
  monitor rect; whether it is topmost
- whether the collector's process is elevated, and whether the game's is

Two nights running, the answer has been a fact nobody was recording. This section
exists so there is not a third.

### 2b. `GetAsyncKeyState` polling is now the PRIMARY fix, not the fallback

Rev 2 had this as a maybe. The experiment promotes it, because it addresses the
mechanism that actually failed: `RegisterHotKey` depends on the OS **delivering a
message** to a background application, and that is precisely what an exclusive
Vulkan presentation path interferes with. `GetAsyncKeyState` reads the keyboard's
own async state directly and does not depend on message delivery at all. That is
the difference between the two, and it is the difference that matters here.

- **Keep `RegisterHotKey` as well.** It demonstrably works on DX11 and it is
  cheaper than polling. Run both.
- Poll on the existing locked thread at 25-50 ms. Do not spin.
- **Edge-detect.** Fire on the up→down transition, once; require the key to go up
  before it can fire again. `ModNoRepeat`'s behaviour must be preserved.
- **Deduplicate.** Both mechanisms seeing one press produces one capture.
- **Tag which mechanism delivered it** —
  `hotkey press received (Alt+F3, via polling)` vs `(via RegisterHotKey)`. On the
  next Vulkan session that tag answers, in one line, whether polling actually
  solved it. Without the tag we would be back to inferring.
- Keep the receipt line where it is, logged before anything is attempted. It is
  the only reason any of this could be established from evidence.

**Still not a low-level keyboard hook.** `WH_KEYBOARD_LL` would likely also work
and sits closer to the line in *"no injection, no hooking, no reading game
memory, no synthetic input."* `GetAsyncKeyState` injects nothing, hooks nothing,
and touches no other process. **If you conclude polling cannot survive an
exclusive Vulkan presentation, stop and say so with your reasoning rather than
reaching for the hook.** That is Sleven's call.

### 2c. The elevation question — demoted, not dismissed

Rev 2's thirty-second "run as administrator" test was not run, because the
renderer change answered the question first. Elevation is no longer the leading
suspect. **Do not build anything for it.** The §2a logging will record it, and if
polling turns out to fail under Vulkan too, that is the next thing to look at.

### Acceptance

- Drive a synthetic key-state source: not pressed → pressed → held 2s → released
  → pressed. Assert **exactly two** fires.
- Negative control: the same sequence with the modifier never down fires **zero**
  times, and the test must fail if the edge detector is broken.
- Assert dedup: both mechanisms reporting one press produces one capture.
- **The real acceptance test is a live one and it is Sleven's:** one PTU session
  on **Vulkan**, pressing the key, and a `via polling` line in the log. Nothing
  synthetic can prove this one. Say so in the handoff rather than implying the
  unit tests settled it.

---

## 3. THE VISUAL INDICATOR — narrowed, one option dropped

Standing rule: **no silent operation.** Sleven has no speakers, so `beep()` in
`winapi.go` does not satisfy it. The rule is currently unmet.

**Sleven has a second monitor arriving soon.** That resolves the design question
rev 1 left open, and it removes the ugliest option:

- **A. System tray icon that changes state** — idle / watching / just captured /
  crashed. Never appears in a capture, cheap, works today. **Build this now.**
- **B. Always-on-top overlay pip** — **dropped.** It would land in the frames
  unless the capture path masks that rect, and masking adds a way for a capture
  to be quietly wrong. Contaminating the dataset in order to indicate that the
  dataset is being collected is a bad trade, and the second monitor removes the
  only reason to consider it.
- **C. A readable status panel in the collector's own window** — captures count,
  which install is being watched, last trigger, time since last capture, and
  whether the log is still growing. Sized to be legible from across a desk on a
  second screen. **Build this after A.** It is the heartbeat made visible, and
  the heartbeat has already proven its worth.

C is not decoration. Every number in this document came out of the heartbeat
lines; putting the same four facts on screen means the next session is diagnosed
while it is happening rather than the next morning.

---

## 4. THE INTERVAL — 60 seconds, and the unit has to change

Sleven's call, explicit: **60 seconds.** His reasoning from the last session
stands and was correct: *"we should have added more recessive capturing. Ten
minutes was way too long."*

### The catch

The interval is minutes-only, in three places:

```go
IntervalMinutes int // 0 = interval fallback off
return autoConfig{PollSeconds: 2, DebounceSeconds: 3, IntervalMinutes: 10}
now.Sub(r.lastCap) >= time.Duration(r.cfg.IntervalMinutes)*time.Minute
```

and in `collector-settings.txt`:

    # Take a picture every this many minutes even when nothing changes.
    # Set to 0 to turn the timer off completely.
    interval_minutes = 10

`interval_minutes = 1` would technically give 60 seconds today, but it caps the
resolution at one minute forever and the next thing he asks for will be 30
seconds. Change the unit properly.

### The change

- Introduce `interval_seconds`, default **60**. `IntervalSeconds int` in
  `autoConfig`. 0 still means off.
- **Read `interval_minutes` if it is present**, convert it, and log that it did
  so and what it converted to. Do not silently ignore a setting that is sitting
  in a file on his disk — that is the same silent-failure shape as everything
  else in this document. If both keys are present, `interval_seconds` wins and
  the log says which one lost.
- Update the trigger tag. It currently reads `interval:10m`. Make it
  `interval:60s`. The tag is written into the capture record, so keep it
  parseable — do not switch between `m` and `s` depending on the value.
- Rewrite the comment in the settings file to match, and keep the "set to 0 to
  turn it off" line — it is good.

### Watch the debounce

`debounce_seconds = 3` and a 60-second interval do not conflict, but a state
change landing 1 second after an interval capture now happens far more often
than it did at 10 minutes. Confirm the precedence comment in `auto.go` still
holds — *"a real state change always beats the interval"* — and that the interval
timer is reset by ANY capture, not only by an interval capture. If it is not,
that is a bug and it is now much more visible than it was.

### Acceptance

- The selftest drives the fake clock. Assert a capture at 60s, 120s, 180s with
  no state changes.
- Assert a state change at t=45s produces a capture AND pushes the next interval
  capture to t=105s, not t=60s.
- Assert `interval_seconds = 0` produces **zero** interval captures over a
  simulated hour — this is the negative control, and it must fail if you wire the
  zero case wrong.
- Assert an old settings file containing only `interval_minutes = 10` still works
  and logs the conversion.

---

## 5. ORDER, AND WHY

1. **The crash.** Everything else is measured in a process that currently dies
   every fourteen minutes. Fixing this first makes every later test trustworthy.
2. **The interval.** Small, self-contained, and it is what Sleven actually asked
   for. Get it in.
3. **The hotkey.** No longer an unknown. Build §2a (log the renderer, the window
   and the elevation) and §2b (polling alongside `RegisterHotKey`, tagged by
   mechanism). It cannot be proven finished without a live Vulkan session, so
   hand it back saying that plainly.
4. **The tray indicator.** Independent of the other three.

**Do not commit or push.** Nothing goes into git without Sleven's explicit
go-ahead. And **do not `git add -A` on this repo** — ~50 files carry pure CRLF/LF
churn (191,317 insertions and 191,317 deletions, verified byte-identical after
stripping CR). Stage the files you actually touched, by name.

---

## 6. WHAT IS NOT IN THIS JOB

The `Game.log` shop-transaction parser is a **separate** job and will be written
separately, deliberately. See
`claude/FINDING_gamelog-is-a-data-source-4.9-vs-4.10.md`. A half-finished parser
must not be able to take the capture path down with it, and the capture path is
what has to be solid before the next test session.

**One correction to that finding, arising from tonight and worth carrying back
into it:** it warns that every assumption in `capture_dxgi.go`, `capture_wgc.go`
and `capture_gdi.go` was formed against a DX11 client and needs re-verifying
against Vulkan. **That warning can be retired.** The 16:16-16:57 PTU session ran
on Vulkan and captured successfully on state changes and on the interval. The
capture path is fine. Only input was affected, and §2 covers it.
