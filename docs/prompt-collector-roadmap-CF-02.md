# CF-02 — the collector: what's left, and where it grows

    from    C1, 2026-08-08
    for     Sleven (phase 0). C1 WRITES PHASES 1-3 ITSELF - see the writer note.
    status  phases 0 and 1 are ordered. Phase 3 is options, not a plan.
    reason  Sleven: "what's the next steps on getting everything fixed up?
            and expand it on. I want to keep expanding the collector."

    supersedes nothing. CF-01 rev 3 stays valid; this is what comes after it.

---

## 0. The one-line summary

**Everything written on 2026-08-07 exists as source and has never executed.** The
binary on disk is from 00:41 that morning. Until it is rebuilt, every fix is a
claim. Phase 0 turns claims into facts and costs about fifteen minutes.

---

## PHASE 0 — prove tonight's code. Sleven runs this. Nothing else proceeds first.

```
cd C:\Users\david\citizen-compass\citizen-collector
go build -o collector.exe .
.\collector.exe --selftest
```

Four acceptance checks. **Each one has a stated failure shape, because a check
whose failure looks like success is not a check (hard rule 12).**

### 0a. The selftest is the NEW selftest

Open `collector-selftest-results.txt` and read the header, not the verdict.

- **Expect:** `WHEN=` today's date, `VARIANT=master`, and the mining checks present.
- **Failure shape:** `RESULT=PASS` with `WHEN=2026-08-07T17:49:36-05:00` and
  `VARIANT=crew`. That is the stale file already sitting there. **A PASS that
  predates the code it covers reads exactly like a PASS that covers it.** If the
  timestamp did not move, the build did not happen — check for a compile error
  scrolled off the top.
- The 18 `mine_selftest.go` checks have never run once. This is their first execution.

### 0b. The crash is gone

Start it and leave it alone for **25 minutes** with the game closed. The old
failure was a metronome: 14m04s, 42 times on 2026-08-07 between 08:34 and 20:50.

- **Expect:** no `fatal error: too many callback functions` in `collector-auto.log`,
  and no `supervisor: collector STOPPED UNEXPECTEDLY`.
- **Failure shape:** the supervisor restarts it in 2 seconds and the window looks
  completely normal. **This is why the bug survived a full day undetected.** Do not
  judge this from the window. Read the log.

### 0c. The interval is actually 60 seconds

- **Expect:** `auto mode started: poll 2s, debounce 3s, interval 60s (1m)`.
- **Failure shape:** `interval 10m`. That is what it says right now — and
  `collector-settings.txt` has said `interval_seconds = 60` since 17:48. **The
  setting is correct and the old binary is silently discarding it.** If it still
  says 10m after rebuilding, the build did not take.

### 0d. The hotkey — the only test that counts

Launch **PTU**, on **Vulkan**, and press Alt+F3.

- **Expect:** a capture line reading `via polling`.
- **Failure shape:** `via message`, or nothing at all. `via message` on Vulkan
  would mean the renderer theory is wrong too and we are back to zero — say so
  rather than accepting it as a pass.
- **DX11 proves nothing.** It already worked. Testing on DX11 is testing the
  control, not the fix.
- Build detection needs no test: the log already shows
  `derived from the captured window's process image path`. Settled.

**Report back the four lines. Not "it worked" — the lines.** Two of the four
failure shapes above are invisible from the window.

---

## WRITER NOTE — read before touching `citizen-collector/`, amended 2026-08-08

**Rev 1 of this document said phases 1-3 were "Code's job, via C1." That was wrong
and it recreated the exact rule-14 failure this project had at 17:17 on 2026-08-07**,
when C1 filed an order into `inbox/` and then wrote the same files itself without
withdrawing the order. Code blocked on mtimes and nine live `claude.exe` processes,
and only Code's discipline stopped anything being lost.

**Corrected: C1 is the sole writer in `citizen-collector/` and is writing there now.**
This document is a plan of record, **not an order to Code.** Nobody else opens that
folder until C1 states in writing that it has stopped. If a future session finds this
file and reads it as a work order, that session is the second writer — stop and ask.

---

## PHASE 1 — the gap between "works for Sleven" and "works on a stranger's machine"

Ordered by what blocks what. **Written by C1**, after phase 0 passes.

### 1. Screenshot masking — the hard blocker

Nothing goes to another person until this exists. A frame carries the handle,
nearby players' names, party members and chat. On this machine those are Sleven's
own; on a tester's machine they are a stranger's, and that stranger has not
agreed to hand them over. The export already defaults screenshots OFF and warns —
that is a stopgap, not the fix.

**Design note, because the obvious approach is wrong:** do not mask by
pixel-position. HUD layout moves with resolution, aspect ratio and UI scale, so a
fixed rectangle silently stops covering anything on a different monitor. Mask by
locating the region, and **fail closed** — if the masker cannot find the region it
was built to find, it drops the frame rather than shipping it unmasked. And give
it a negative control: a fixture frame with a known handle in it that the test
asserts is gone.

### 2. Make the supervisor honest

It restarted 42 times and told nobody. **That is the same defect class as the
silent shop parser** — a component that fails quietly looks identical to one that
had nothing to do.

- Restart count and reason surface in the UI, not only the log.
- **Restart count goes into the export as data.** A session with four restarts has
  holes in it, and whoever consumes that data is entitled to know. Flag, never
  auto-fix — the project's existing auditor rule, applied to collection.

### 3. Visible sign of life

CF-01 job 4, still unbuilt. The `alive:` heartbeat every 3 minutes is real and
works — but it is in a log file, and nobody reads a log file mid-flight. Sleven
has no speakers, so audio is out. A tray icon that changes state is the remaining
option.

### 4. Startup diagnostics (CF-01 §2a)

Log renderer, window flags and elevation at startup. **The whole hotkey saga cost
four wrong theories and a day**, and every one of them would have been settled in
ten seconds by a startup line stating the renderer. The miner already extracts
this from `Game.log` after the fact; the collector should state it about itself,
up front.

### 5. First-run consent screen and a README for a non-technical tester

Plain language: what it reads, what it never reads, that nothing leaves the
machine unless they click the button, and how to stop it. **Written to be read by
someone who did not build it.** Right now there is no installer and no
instructions — handing over a folder of Go source and an exe is not a test, it is
an imposition.

---

## PHASE 2 — two decisions that must be made BEFORE the exe reaches a second machine

**These are cheap now and extremely expensive later.** Both become unfixable the
moment other people's data exists in the wild.

### 2a. The export has no schema version

`gamelog-dataset.json` is whatever `MineStore` happens to marshal to. The first
time a v0.1 export and a v0.4 export need merging, the shape has to be inferred
from its contents. Add a `schema_version` and a `tool_version` at the top level
now, while there is exactly one producer and it is on this desk.

### 2b. There is no contributor identity, and merging without one is actively wrong

This is the sharper of the two. Three people report the same price at the same
kiosk. Is that three independent confirmations, or one person's log counted
thrice?

- **Dedup across contributors** and genuine independent corroboration gets deleted —
  the exact signal that makes crowd-sourced pricing worth more than one person's.
- **Don't dedup** and one person exporting twice inflates the count.

**Both answers are wrong, and no amount of later cleverness recovers the
distinction if it was never recorded.** What is needed is a random per-install ID —
generated once, stored locally, **not derived from handle, machine name, hardware
or anything else about the person**, and shown to them so it is not a secret. It
identifies a *source of observations*, not a human.

**CLOSED 2026-08-08. Sleven chose the random per-install ID:** generated once, stored
locally, shown to the person so it is not a secret, never derived from handle, machine
name or hardware. It identifies a source of observations, not a human. A self-typed
nickname was rejected on the grounds that people would use their Star Citizen handle
and put a real identifier into the one dataset the pipeline exists to strip handles
out of.

---

## PHASE 3 — expansion. Four directions, real costs, not a ranking.

**DECIDED 2026-08-08: Sleven picked A (wire up the existing parsers) as the first
expansion.** B, C and D stay on this list, unstarted, in this order of preference
unless he says otherwise. He also settled contributor identity — see §2b, now closed.

Sleven said yes to the collector growing. These are what growing looks like, in
rising order of cost.

### A. Wire up the parsers that already exist — cheapest thing on this list

Three parsers in `gamelog.go` **compile today and are connected to nothing**:
`objectcontainer`, `spawn_location`, `RequestLocationInventory`. Plus the four
transaction families the archive mining found. This is pure text — no OCR, no new
risk surface, no new privacy surface beyond what is already scrubbed.

C3's standing objection is correct and should be respected: `objectcontainer`
fires on *boarding*, so its frames show cockpit interiors, and most boardings are
the player's own ship. **Use it as a data event, not as a capture trigger.**

Cost: low. Value: immediate, and it is data no other tool has.

### B. Live tailing as a trigger, not just post-hoc mining

Today the miner reads log files after the fact. Tailing during play means the log
can *trigger* a capture — the player opened a shop, so take the frame now. That
turns the 60-second interval from the primary mechanism into a backstop.

**This is the highest-value-per-line item on the list**, because it fixes the
thing that made the kiosk test fail. Text tells you when something happened;
capture is only needed for what text does not carry.

Cost: low-medium. Depends on nothing else.

### C. Change detection for the standing-still blind spot

Pixel diffing so a still screen with a changing panel still gets caught. The
interval trigger only half covers this. Cheaper than it sounds and independent of
everything else.

Cost: medium. Value: fills a known gap rather than opening new ground.

### D. Engineering / component state — the expensive one Sleven already approved

Live component health, temperature, power draw and wear are runtime state. They
are not in any game file and not, so far as anyone has checked, in the log.

**Check the log before building any of it.** The archive turned up quantum fuel
per route, which nobody expected and which is exactly the kind of number a fitting
display wants. **Text beats OCR every time**, and some of what looks like it needs
a screen reader may already be sitting in a text file. This is also a live
question for C3's loadout work — its tier-3 list and this are the same list.

Cost: high, and it is the only item here that needs reading pixels for meaning
rather than for the record.

---

## What is deliberately NOT proposed

- **Visual ship recognition.** Authorised in principle, gated on the model
  question, and it is a research project rather than a collector feature. Not now.
- **Any automatic sending.** Export stays manual. Standing rule, not up for review.
- **Any hooking, injection, memory reading or synthetic input.** Standing rule.
- **Chat zone sampling.** Hard exclusion, not a filter.

---

## Constraints carried forward

- One writer per artifact. **`citizen-collector/` has exactly one writer and rule
  14 was already broken there once on 2026-08-07, by C1.** Whoever takes phase 1
  owns the folder alone.
- Nothing commits or pushes without Sleven's explicit go-ahead.
- No `git add -A` until the CRLF/LF churn is settled.
- `Game.log` does not enter the repo.
- Every check gets a negative control.
