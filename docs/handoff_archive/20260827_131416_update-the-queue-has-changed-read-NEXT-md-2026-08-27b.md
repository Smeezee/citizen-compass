# NEXT — the standing work queue

**One writer: C1.** Code never edits this file. Code reports completion in its
own handoff update, and every item's DONE-WHEN is written so anyone can tell it
is finished without asking C1.

**If C1 is mid-task, asleep, or wrong, the queue still advances.**

---

## HOW TO USE THIS

**Sleven:** *"check the updates"* or *"go"*.

**Code, after every unit of work:** read this file, take the FIRST item whose
DONE-WHEN is not satisfied and whose BLOCKED-BY is clear — **checking the
DONE-WHEN yourself, not assuming the file is current**. Report before writing,
rule 5. Do it. File the handoff. Come back.

**A stale queue is a normal condition, not an error.** If the top item is done
and this file has not caught up, say so and take the next one.

**If an item is wrong, ambiguous, or badly prioritised, say so and take the next
one.** Code has been right against C1 four times on 2026-08-27, most recently
proving Q3's premise was hollow. The list exists so Code does not have to build
it, not so it can overrule Code.

**Anything not on this list and not asked for by Sleven directly is a
suggestion, not work.**

---

# PART A — SLEVEN DECIDES. Three, batched, with what each blocks.

`CRITIQUE_senior-analyst-review-2026-08-27` recommendation 6 asked for a
separate `DECISIONS.md`. **Deliberately not doing that** — a second queue file
is a second thing to keep current and a second place to look. Decisions live at
the top of the queue they block, which is the same fix with one less artifact.
If the section grows past about five, split it.

### D1 — WHICH SINGLE FRONT GETS FINISHED TO THE PUBLIC SITE
**Blocks:** everything visitor-facing. **C1 recommends: one complete ship page.**

Ten fronts are open and, per `LIVE.md`, the public site has not moved in
**twenty-eight days**. The 08-26 brief's thesis is that every competitor serves
someone who already knows the game and nobody serves the newcomer — and the
three assets that back it are now real rather than planned: a 3D hull with
hardpoints on **CIG's own coordinates**, provenance on every number, and
plain-English captions. **That thesis is a claim about strangers, and it cannot
be tested from behind a password.** One ship page, public, end to end, converts
the largest pile of finished-but-invisible work into the only evidence that
matters — and it is the cheapest of the ten to finish, because the hard parts
already exist and are checked.

Against it: it ships one page while nine fronts decay, and six of those need
re-verification against 4.10 regardless. That cost is already sunk either way.

### D2 — THE WINDOWS RUNNER
**Blocks:** the collector, and every check written for it since 2026-08-07.
**C1 recommends: neither of the critique's two options, because its premise is
eighteen days stale.** See PART C.

### D3 — HARD RULE 16, THE SOURCE OF A CHECK'S TRUTH
**Blocks:** nothing. Adopting it is cheap; the cost is that it makes some
existing checks knowingly inadequate. Proposed text in PART C.

---

# PART B — CODE'S QUEUE

### Q1 — IS THE NETLIFY CREDIT BLOCK STILL IN FORCE?
**DONE-WHEN** a written answer exists — blocked or clear — with how it was
established.
**BLOCKED-BY** nothing. **Do this first. It is minutes and it gates D1.**

`CURRENT-STATE.md` records that Netlify deploys were credit-blocked and the live
site would sit on v0.3.9 "until that clears". **Nobody has re-checked in three
weeks.** `scripts/deploy_live.ps1` exists (committed 08-21, `0a4d5ed`) with no
record of ever running.

**A month of finished work may be parked behind a billing state nobody has
looked at.** Do not deploy anything to live — just find out whether it is
possible, and say so. **If it is blocked, that is a Sleven item and the answer
is the deliverable.**

### Q2 — BROWSER CHECKS GATE THE DEPLOY
**DONE-WHEN** `deploy_testing.ps1` refuses to upload on a red browser check, and
its override must be typed and prints which check it is ignoring.
**BLOCKED-BY** nothing.

Ruling of 11:57. Sleven overrode a red check on 2026-08-27 and was right to.
That stays possible; it stops being silent.

### Q3 — `deploy_testing.ps1:304`
**DONE-WHEN** the checklist names a marker that is actually in the payload.
**BLOCKED-BY** nothing.

Replace `cc-ship::after` with `id="cc-panel"`. Leave `kb_overlay.inc.html`.

### Q4 — `build_holo_data.py` HAS NOT RUN SINCE 17 AUGUST
**DONE-WHEN** either the seven collisions are resolved and it emits, or a
written finding says which record is wrong and why that is Sleven's call.
**BLOCKED-BY** nothing.

    ATLS, C8R_Pisces, Khartu-Al, M50, MDC, ROC, ROC-DS

Report the collision before fixing it.

### Q5 — THE DISCLOSURE BAR
**DONE-WHEN** D1 and D2 of `ORDER_the-disclosure-bar-2026-08-27.md` are built
and deployed to testing.
**BLOCKED-BY** nothing.

Bigger than when written. 19 third-party models need visible provenance, and
**a position guessed from a mount name and a position that is CIG's own
transform are not the same claim.** `placed_from` is on every record —
`client` where it is CIG's. The page must not present the two as one thing.

### Q6 — THE ROADMAP WATCHER, R0 ONLY
**DONE-WHEN** the real board is identified and written down.
**BLOCKED-BY** nothing.

---

# PART C — THE TWO PROPOSALS BEHIND D2 AND D3

## D2 — the Windows-runner premise is stale, and the correction changes the answer

`CRITIQUE_senior-analyst-review-2026-08-27` Finding 2 states that **no Claude
session in this project can run a Windows binary**, citing the 08-09 handoff,
and offers two options: build a scheduled runner, or stop writing unexecutable
checks.

**That was true of Cowork sessions and it is not true of Code.** On 2026-08-27
Code ran, on Sleven's Windows machine, in the ordinary course of work:

    venv\Scripts\python.exe testing\_src\build_deploy.py
    powershell -ExecutionPolicy Bypass -File .\scripts\deploy_testing.ps1
    node checks\_verify_panel_dismiss.mjs        (headless Chromium)

Those are Windows binaries, executed by a Claude session, unattended, today.
**The blocker is real for C1 — the Cowork device bridge is a Linux VM with no
network — and it is not real for Code.** The critique is eighteen days old and
this changed underneath it.

**So the recommendation is neither of its options.** Option 1 proposes building
a runner that already exists in the form of Code. Option 2 concedes ground that
does not need conceding.

**C1 recommends: put the collector selftest on the queue as ordinary Code work,
and find out what actually fails.** `go build` plus `.\collector.exe --selftest`
is one queue item. If it runs, ~190 checks stop being theoretical and the
capture_keys class of defect becomes catchable by machine. If it does not run,
**the reason is a measurement rather than an eighteen-day-old inference**, and
option 2 becomes the honest fallback with evidence behind it.

**What the critique gets right, and it survives the correction:** ~190 checks
have never been executed, that is why a dead feature shipped, and nobody should
write another collector check until they run. That part stands.

## D3 — proposed HARD RULE 16

> **A check must draw its truth from a different source than the thing it
> checks.** A real browser, a real binary, a real archive, a real clock — not a
> model of one written by the same author on the same day. Where that is
> impossible, the check is labelled UNPROVEN and says what it could not reach.

**Three worked examples, all from this project's own record:**

1. **The dark site, 2026-08-26.** `_fitProjected()` moved the camera without
   aiming it. The stub camera in the harness **always looked at its target** —
   it modelled the fix. Twenty-three green checks stood over three days of a
   completely black site. `DECISION_the-checks-get-a-real-browser-2026-08-26`
   is this rule, discovered at the cost of an outage and scoped to browsers.
2. **`ui.go`.** Compiled clean — a file the product does not use.
3. **The callback control.** Asserted 50 calls consumed 50 slots. Go dedupes
   identical closures, so one slot was consumed and the control passed by
   agreeing with the same wrong model the code held.

**Why rule 12 is not enough.** *A check that cannot fail is not a check* catches
a vacuous assertion. All three above **could** fail — they simply could not fail
**for the real reason**, because the check and the code shared an assumption.
That is a different fault and it needs its own rule.

**What adopting it costs, said plainly:** several existing checks become
knowingly inadequate the day it is adopted, and the collector's entire suite is
in that set until D2 is settled. That is a feature — it converts a silent gap
into a labelled one — but it will make the board look worse before it looks
better.

---

## NOT CODE'S — do not pick these up

    NEXT.md                           LIVE.md
    testing/_src/loadout.src.html     testing/_src/cc_viewer.js
    checks/_verify_panel_dismiss.mjs  decode_cga_nodes.py
    probe_ship_geometry.py            extract_p4k_entry.py
    build_hardpoint_transforms.py     build_hardpoint_placement.py
    build_hardpoint_overlay.py        alignment_overlay_client.json
    data-layer/derived/hardpoint-*    the RSI watcher's trigger prompt

`testing/_src/build_deploy.py` IS Code's.

---

## RECENTLY CLOSED — context only, do not re-do

- **Deploy + P1e + the rescale** — deployed and verified 2026-08-27.
- **Markers on CIG's coordinates, proven in a browser** —
  `_verify_marker_positions.mjs`, green, control decisive.
- **The old Q3 was a hollow check and Code proved it.** C1 claimed re-running
  `build_hardpoint_overlay.py` after a rescale was a free check on the rescale.
  **It never opens a `.glb`** — the file is byte-identical because it cannot
  depend on model scale at all. C1's error, recorded rather than quietly
  dropped.
- **The RSI watcher write rate** — trigger prompt changed 2026-08-27 13:05
  local. A quiet or blocked hour now writes zero documents; only
  `watch-rsi-state.md` is overwritten. **A control is planted** in that state
  file: two real devposts were removed, so the next run must detect them and
  write exactly one document. If it writes none, change detection is broken and
  the change gets reverted.

---

*Maintained by C1. Last set 2026-08-27 13:22 local.*
