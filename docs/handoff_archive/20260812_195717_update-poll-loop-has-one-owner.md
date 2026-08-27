# Update — §3 done. rafId went from five writers to one, and the three harnesses are now build gates that I have watched fail.

`device_engine.js`, both host pages, `build_deploy.py`. Built clean. **Not deployed.**

## One owner, and cancellation stops being what correctness rests on

`pollStart()` / `pollStop()` own the handle. `poll()` no longer touches `rafId`
at all — it returns `false` to ask the loop to stop. The hosts call
`CCDEV.pollStop()` instead of reaching into `rafId` themselves, which removes
the two writers that lived in another file entirely.

**The mechanism is a generation counter, not a tidier cancel.** Every start and
stop bumps `pollGen`; a frame carries the generation it was scheduled under and
returns without re-arming if that generation has been superseded.

That matters because **`cancelAnimationFrame` cannot take back a callback the
browser has already dispatched.** Any design where correctness depends on the
cancel winning has a case it cannot cover. Here the cancel is only an
optimisation — a frame nobody can recall still cannot keep a second loop alive.
Starting is idempotent by construction, so "call it twice" is safe without
anyone remembering a guard.

## The double loop, demonstrated

`_verify_poll.js` drives the engine with a controllable `requestAnimationFrame`,
so it can hand back a frame the browser had already committed to — the one
interleaving that is genuinely uncancellable. With both generation guards
removed:

```
  FAIL  an already-dispatched frame does NOT re-arm after a stop
          a superseded frame queued 1 more
  FAIL  starting again gives exactly ONE loop, not two
          queued 2
  FAIL  and exactly one frame runs
          ran 2, queued 2
```

**`queued 2` / `ran 2` is the symptom, reproduced**: two loops, both re-arming,
neither cancellable. With the guards in place, 13/13 pass.

**Acceptance 6 is in there as a check, not a claim:** ten KBM→JOY switches,
never a second loop, `loopRunning` 1 at the end, frame counter still climbing.
`ccDiag()` now reports `loopRunning` and `staleFrames` — `polls` alone could
never answer "is there exactly one loop", because two loops just make it climb
twice as fast and nobody can see that by eye. `staleFrames` is allowed to be
non-zero; it means the guard did its job.

Also kept as a check: **the loop can be restarted after it self-stops.** That is
`FINDING_device-poll-cannot-restart-2026-08-10` — where the only way back on was
a `gamepadconnected` event — asserted so it cannot come back.

## Where I nearly fooled myself, and the rule that caught it

My first mutation removed **one** of the two generation guards. The suite still
passed the substantive check, because the second guard covered for it. I would
have reported "the checks can fail" on the strength of a counter going to zero.

**That is exactly the shape this project keeps finding**: a check that passes
for a reason unrelated to what it claims to test. The mutation now removes both
guards, i.e. actually models the old behaviour, and four checks go red.

Second instance of the same thing today — mutation M22 in the §2 work did it
too. Both were caught only by insisting the mutant fail, rather than by reading
the code and being satisfied.

## The harnesses are gates now, and I have watched them refuse a build

Three behavioural harnesses exist because three behaviours shipped broken. Ones
that run when somebody remembers protect nothing on the build where it matters.
`build_deploy.py` now runs `_verify_slots.js`, `_verify_conflict.js` and
`_verify_poll.js` **before it writes anything**, and fails closed — including
when `node` is absent, and when a gate file has gone missing (a deleted gate is
not a gate that passed).

**It also syntax-checks every executable inline script on both pages.** The
existing gate covered the injected engine only; the rebind flow, the export bar
and the action browser had never been parsed by anything before a deploy —
which is how a newline inside a string literal reached both hosts on 12 August
and was caught only because somebody happened to run `node --check` by hand.
`<script type="application/json">` data islands are skipped, because a check
that cries wolf is how checks get switched off.

**Both new gates proved against known-bad input, then restored:**

```
  PASS  inline-JS gate rejects a broken script block
  PASS  behavioural gate rejects a one-stick regression
  PASS  both files restored byte-for-byte
  PASS  the build passes again afterwards
```

The second plants a change that still *parses* — `if(n<2)` becomes `if(n<0)`, the
one-stick bug in miniature — so only the behavioural gate can catch it. The
restore is compared byte-for-byte rather than assumed.

**One ordering fact worth knowing:** `inject_engine.py` runs *before* the gates,
so a failed build can leave both hosts carrying an already-injected copy of the
engine that failed. Harmless — the next successful build re-injects from the
master — but I checked all four files afterwards rather than assuming it, and
none carried the planted `if(n<0)`.

## Not claimed

Still no browser and no hardware. The tab-switch behaviour is proven against a
controlled frame queue, not against Chrome, and §5b's list of what needs the
pair is unchanged.

Next: §4/§5 — nav keys, fonts into `_deploy`, the collector shortcut ordering,
side-by-side layout, and the 128-button default.
