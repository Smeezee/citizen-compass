# ORDER — the collector's staleness selftest is intermittent, and an intermittent check is not one

    from    Code, 2026-08-20, at Sleven's instruction
    for     whoever picks up the collector next
    origin  G7-FINDING in docs/LEDGER_shop-price-layer-2026-08-19.md.
              Found while building the collector for the 08-19 G order.
              NOT fixed then: touching the collector was explicitly out of
              scope for that run, and the finding is worth its own order.
    scope   citizen-collector/gamelog_selftest.go and the loop it drives.
              This is a TEST-FIXTURE defect. Nothing here says the staleness
              WARNING is broken - see §1, which is the first thing to settle.
    status  Not started. No run rules attached: this is small enough to do in
              one sitting, and §1 may change what the rest of it should be.

---

## 0. What was observed, exactly

Building the collector on 2026-08-19 (`build.ps1 -Both`, both binaries clean,
PE subsystem 2) I also ran `-selftest` several times. The real `collector.exe`
passed: **0 failures across 584 checks.**

A second binary — the same source built without `-H=windowsgui`, used as a
control to prove a PE-subsystem reader could return 3 — was run three times:

| run | result |
|---|---|
| 1 | **5 failures**: the CONSOLE subsystem check (correct — it *is* a console build) **plus four staleness checks** |
| 2 | **1 failure**: the CONSOLE check only. The four staleness checks passed. |
| 3 | **HUNG.** Killed at 10 minutes. Not diagnosed. See §5. |

Same binary, same machine, same fixture, three different answers. The machine
was busy during run 1 — a 235-model geometry decode and a full check sweep had
just run — and idle by run 2.

The four:

    staleness warning fires on a dead log
    staleness warning names the fix
    staleness warns once per stall, not every poll        (reported NOT PERFORMED)
    a log that starts growing again is NOT reported stale (reported NOT PERFORMED)

**Those are not four defects. They are one, plus its dependants.** The last two
report NOT PERFORMED *because* the first did not fire — the fixture gates them
on there being a warning to count. That gate is correct and someone put it
there deliberately; see §2.

**Nothing here has been shown to be wrong with the collector's staleness
warning.** Every symptom is consistent with a fixture that asks a real-time
loop a question and does not wait long enough for the answer. §1 exists so that
is established rather than assumed.

---

## 1. FIRST, MEASURE IT. Do not fix anything yet.

**Run the staleness fixture in a loop and count.** 200 runs, or as many as fit
in twenty minutes, on an otherwise idle machine — then again with the machine
deliberately loaded (a geometry decode is a convenient load, and it is what was
running when this first appeared).

Record, in the ledger:

- the failure rate idle, and the failure rate loaded
- **whether the four ever fail INDEPENDENTLY of each other.** If "fires on a
  dead log" always fails first and the others always follow, this is one defect
  with three dependants and the fix is one change. If "names the fix" ever
  fails while "fires" passes, that is a *second*, different problem and this
  order is wrong about the shape of it.
- whether run 3's hang recurs, and at what rate

**Why this comes first, and why it is not ceremony:** §2 below is a diagnosis I
am confident of from reading the code, and confidence from reading the code is
exactly what this project has been burned by. A comment claimed a build flag
for months. Seven files claimed `-H windowsgui`. The number is what settles it,
and it is also the only way to prove the fix afterwards — **a flake that
reproduces once in forty cannot be shown fixed by running it twice.**

*Acceptance:* two numbers in the ledger, and a statement of whether the four
fail together or separately.

---

## 2. The mechanism, so it is not re-derived

`citizen-collector/gamelog_selftest.go` drives the real auto-loop with a
**fake clock** and asserts on a **real-time** poll:

    gamelog_selftest.go:37   fakeClock.Advance() sets a variable. That is all
                             it does. It notifies nothing and wakes nothing.
    gamelog_selftest.go:196  the fixture runs the loop at PollSeconds: 1
    auto.go:912              the loop ticks on a REAL time.Ticker
    auto.go:855              stalenessAfter = 5 * time.Minute (fake time)

So the sequence at `gamelog_selftest.go:245` is:

    clock.Advance(stalenessAfter + time.Second)          // instant, silent
    ok = waitFor(func() bool { ... }, 4*time.Second)     // ~4 real polls

The loop only discovers that five fake minutes have passed the next time its
**real** one-second ticker fires and it happens to read the clock. `waitFor`
(line 103) polls the sink every 10ms for four real seconds. On an idle machine
that is four chances and it always works. Under load, a 1s ticker drifts and a
goroutine may simply not be scheduled — and four seconds stops being enough.

**That is the whole flake, and it is a race between a fake clock and a real
ticker.** Note that the fixture already solves this correctly elsewhere: at
line 216 it waits on a *definite signal* before touching the clock, with a
comment saying the race "already produced a red result on working code."

### And the second, quieter half — which matters more

The two remaining checks do this:

    clock.Advance(30 * time.Second)
    time.Sleep(1500 * time.Millisecond)
    check("staleness warns once per stall, not every poll",
          sink.count("has not grown in") == firstCount, ...)

They sleep for real, then assert a count **did not go up**. On a loaded machine
where the loop has not polled at all, that assertion is true *because nothing
happened yet*. **It passes by being too slow to observe the defect it exists to
catch.** The same pattern appears again in the "starts growing again" check
with two more bare 1500ms sleeps.

So the fixture has flakiness in both directions: the positive checks fail
spuriously under load, and the negative checks **pass** spuriously under load.
Only the first kind is visible, which is why only the first kind got noticed.

---

## 3. SOMEBODY HAS ALREADY BEEN HERE, AND THEY FIXED THE OTHER HALF

`gamelog_selftest.go:259-267` carries this, written before I ever saw the file:

> BOTH of the remaining checks compare a count against firstCount, so if the
> warning above never fired, firstCount is 0 and "the count did not go up" is
> trivially true — they would report a pass having measured nothing. That is
> the SILENT SUCCESS pattern, and it was observed for real: an intermittent
> miss on the positive check above left these two green while asserting 0 == 0.
> They are now gated on there being something to count.

**So this intermittency is not new. It was hit, understood, and the dangerous
consequence was closed — a flake that produced two false PASSes now produces
two honest NOT PERFORMEDs instead.** That was the right call and it is why the
08-19 run could see the problem at all.

**What was not done was fixing the flake itself.** Which is fair — a false PASS
is an emergency and a false FAIL is an annoyance. But the note treats "an
intermittent miss on the positive check" as a fact of life, and §2 says it is a
fixable race. That is what this order is for.

**Do not undo that gate.** It is load-bearing. The fix goes underneath it.

---

## 4. THE WORK

**S1. Make the loop's observation of the clock deterministic.**
The fixture must be able to say "time has advanced *and the loop has seen it*"
rather than advancing a variable and hoping. Cheapest shape that achieves it:
give `fakeClock.Advance` a way to signal, and have the fixture wait on the
loop's *next completed poll* rather than on a wall-clock timeout — the same
technique line 216 already uses for the tailer, applied to the clock.

Whatever shape is chosen, the requirement is: **no assertion in this fixture
may depend on how many real seconds elapse.**

*Acceptance:* the §1 loop, re-run at the same count, idle **and** loaded, with
zero failures.
*Control, and it is the load-bearing one:* **break the staleness warning on
purpose** — comment out the warning, or set `stalenessAfter` absurdly high —
and confirm all four checks FAIL, every run, loaded and idle. A fixture that no
longer fails spuriously is worthless if it also stopped failing genuinely, and
that is the exact way this could be "fixed" wrongly: by widening a timeout
until nothing ever fails.

**S2. The two negative checks must be able to fail.**
Per §2's second half, `count == firstCount` after a real sleep can pass because
nothing has run. Make them wait for a *definite* number of polls to have
happened and only then compare.

*Control, both halves:* make the loop warn on **every** poll and confirm "warns
once per stall" FAILS. Make growth **not** reset the staleness clock and
confirm "starts growing again" FAILS. Neither has ever been observed failing on
demand, which by rule 12 means neither is yet known to work.

**S3. Say in the results whether a check was skipped for load.**
If any timing dependency genuinely cannot be removed, the fixture must report
that case as NOT PERFORMED with the reason, exactly as the existing gate does.
Never as a pass.

**S4. Sweep the fixture for the same pattern elsewhere.**
`gamelog_selftest.go` is not the only fixture mixing a fake clock with real
sleeps — `grep -n "time.Sleep" citizen-collector/*_selftest.go` and report what
else asserts a negative after a bare sleep. Report the list; fix only what §1's
measurement shows is actually flaking.

---

## 5. THE HANG — observed, not diagnosed

The third consecutive run of the control binary's `-selftest` produced no
output and was killed at ten minutes. Runs 1 and 2 of the same binary completed
in well under a minute.

**I did not investigate this and I am not going to guess at it here.** It may
be the same fixture — a `waitFor` that never satisfies is a four-second
timeout, not a hang, so if it *is* this area it is something else, such as the
loop failing to shut down. It may equally be the hotkey or tray fixtures
contending across back-to-back runs, which have nothing to do with staleness.

Treat it as a separate question that §1's loop will answer for free: run the
selftest two hundred times and the hang either recurs or it does not. **If it
recurs, it outranks everything else in this order** — a selftest that
occasionally never returns will eventually be run by a person who concludes the
collector is broken.

---

## 6. WHAT MUST NOT HAPPEN

- **Do not fix before §1 measures.** The rate is how the fix gets proven, and
  there is no second chance to collect a "before" number.
- **Do not widen a timeout and call it fixed.** That is the failure mode this
  order is most likely to produce. It converts a visible flake into an
  invisible one and satisfies every acceptance line except S1's control.
- **Do not remove the `firstCount == 0` gate** at line 260. It is what turned
  two false PASSes into two honest NOT PERFORMEDs, and it is the reason this
  defect was visible at all.
- **Do not weaken or delete any of the four checks.** The staleness warning is
  what tells an operator their Game.log path is wrong; a collector that quietly
  watches a dead file is the single most useless state it can be in.
- **Do not cut a release and do not install anything.** Standing.
- **Do not `git add -A`.**

---

## 7. AT THE END, REPORT

- The two failure rates from §1, idle and loaded, before and after.
- Whether the four fail together or separately — it decides whether this was
  one defect or two.
- Each of the three S1/S2 controls **observed failing on demand**, named.
- Whether the §5 hang recurred, and how often.
- Anything in §2 that turned out to be wrong. It is a diagnosis from reading
  the code, and the whole point of §1 is that this project does not accept
  those on their own.
