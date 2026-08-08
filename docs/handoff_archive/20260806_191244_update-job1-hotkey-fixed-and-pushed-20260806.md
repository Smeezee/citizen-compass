# Update: JOB 1 DONE - hotkey now registers in --auto. Pushed.

**2026-08-06.** The blocking defect is fixed, proven by mutation, and on
`origin/main` as `8017efc..1eadf97`. **Sleven can run the live session.**

## The fix

`main()` entered the auto branch, called `runAuto` and returned. `parseHotkey`
and `RegisterHotKey` sat *below* that return and were never reached in `--auto`.

Registration now happens **in the auto branch, before the poll loop**. Presses
reach `runAuto` on a channel and produce `Trigger{Kind:"hotkey"}` with the key
name in `Note`, so a manual frame is distinguishable from an automatic one
afterwards. Manual capture **bypasses the debounce** - that exists to stop
automatic triggers flooding the folder and has no business overruling a human.

Registration failure is reported **on stdout AND in `collector-auto.log`**, and
auto mode continues regardless. The console hides moments later, so the log line
is the only record that survives. Losing manual capture is bad; losing
unattended capture as well, because of it, would be worse.

### One design point worth knowing

The listener owns its own **locked OS thread**. `RegisterHotKey` with a NULL
window delivers `WM_HOTKEY` to the queue of the *thread that registered it* and
nobody else can receive it. Manual mode gets away with using the main goroutine
only because it then sits in `GetMessage` forever - `runAuto`'s select cannot.
`Close()` posts `WM_QUIT` to that same thread so `UnregisterHotKey` runs where
the registration actually lives; calling it from elsewhere is a no-op with a
success-shaped return.

## The test - and why there are two kinds

Sixteen checks now run under `-- hotkey (auto mode) --`. The unit checks ask
**Windows** whether the key is registered, by trying to take it and requiring a
refusal, rather than asking our own variables.

**They pass, and they would not have caught this bug.** It was a wiring defect
in `main()`, not a logic defect in `runAuto` - which is exactly why 34 checks
and 13 mutations missed it.

So there is also an **end-to-end check that runs the real binary in real
`--auto` mode as a child process** and probes registration from outside.

### Proven by mutation (hard rule 12)

Registration was removed from the auto branch in a scratch copy, reproducing the
original defect. Result:

```
ELEVEN unit checks        still [ok  ]
[FAIL] --auto REGISTERS the hotkey (end to end)
[FAIL] e2e probe distinguishes the two runs
```

**Only the end-to-end checks fail.** That is the entire argument for that file
existing, and it is now demonstrated rather than asserted.

The negative control uses an invalid hotkey string and requires the key to be
left UNREGISTERED. The two probe results are additionally compared against each
other - per the brief, if both came out identical the probe would not be looking
at registration, so that comparison is its own recorded check.

Full `--selftest` **PASS**, exit 0.

## Job 4 - pushed, with a correction

The five-commits-plus-`.wrangler` description was already complete. That work
went up **last turn** as `0570426..8017efc`, with the ignore rule written as a
**pattern** (`.wrangler/`, `wrangler-account.json`, neither carrying a slash, so
they match at any depth) and verified at four locations.

What was actually outstanding was two commits, now pushed:

```
62d3b1f Run the deploy guard at deploy time, not only at build time
1eadf97 Register the hotkey in --auto, where it was never reached
```

Checked before pushing: nothing matching `wrangler`, `.env`, `password`,
`secret` or `.dump` in either diff.

## Still to do

- **Job 2** - `--gamelog <path>` override, print chosen path and how it was
  chosen, warn when the watched file has not grown while a game window exists.
- **Job 3** - heartbeat line in `collector-auto.log`.
- **New job** - the `--ui` desktop launcher. Full spec received (the first copy
  was truncated mid-sentence; the resend completed it). Doing Jobs 2 and 3 first
  because the launcher's status panel displays exactly what they produce.
