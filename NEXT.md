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

# SLEVEN'S RULING, 2026-08-27 14:10 local

> *"I want whatever's next. It all has to be done."*

**There are no decision gates on this queue any more.** The three items that
were waiting on him are decided:

- **Which front gets finished** — all of them, in the order below. C1 does not
  ask again.
- **The Windows runner** — settled by doing. Run the collector selftest and
  find out what actually fails. It is Q3 on Code's list, not a question.
- **Hard rule 16** — adopted. A check draws its truth from a different source
  than the thing it checks, or it is labelled UNPROVEN and says what it could
  not reach.

**Going live is NOT on this queue and will not be raised again until Sleven
raises it.** He has said the site is not ready. He is the one who knows. C1
turned an outside session's recommendation into pressure and that was wrong.

---

# CODE'S QUEUE

### Q1 — 31 SHIPS PRINT ANOTHER SHIP'S NAME ON THEIR ARMOUR. LIVE AND VISIBLE.
**DONE-WHEN** the armour heading is derived from the SHIP, not from the item's
own `Name`, and no ship page prints an armour name naming a different ship.
**BLOCKED-BY** nothing. **This jumps the queue: it is on a page people look at.**

Source: `HANDOFF_weapon-armour-shield-package-for-c1-2026-08-27.md` (C3),
measured on disk, every claim naming its file.

`build_loadout_data.py:740` takes the armour's display name from the item's own
record, and **that field carries the wrong ship's name on 31 of 91 named armour
records - 34%.**

    ARMR_RSI_Perseus       prints  "Constellation Andromeda Ship Armor"
    ARMR_AEGS_Idris_P      prints  "Hammerhead Ship Armor"
    ARMR_ORIG_890J         prints  "350r Ship Armor"

**Scope it honestly: the NUMBERS ARE RIGHT.** The page resolves armour through
each ship's own `Loadout`, so no ship is showing another ship's multipliers.
It is a labelling bug. **But it is on a page whose entire claim is that the
numbers can be trusted, and it says the wrong ship's name out loud.**

**DO NOT FIX THIS BY CORRECTING 31 STRINGS.** Derive the name from the ship.
C3's join is a literal dictionary lookup on a UUID string - wiki
`vehicle.armor.uuid` against `stdItem.UUID` - **285 of 285, 100%, no
normalisation, no lowercasing, no token containment, no fuzzy anything.** It
also covers the 118 placeholder records, which correcting strings never would.

Spot check to reproduce before trusting it: Avenger Stalker →
`b3b23908-e9ab-4c46-93ed-ecd20aaf65c3` → `ARMR_AEGS_Avenger_Stalker` →
Deflection Physical 11 / Energy 9. Both sources agree on every value.

**The control: assert that no rendered armour heading names a ship other than
the one whose page it is on.** That check must go red on the current build -
if it does not, it is not testing the defect.

**Read §7 and §8 of the handoff before starting.** C3 records one thing it got
wrong (Deflection was already built) and that every number in it is **patch
4.9**. And §3 says to CANCEL any "compare shields by damage type" feature -
there is nothing to show. Do not build it.

### Q2 — A FAILED BUILD MUST NOT REACH A DEPLOY
**DONE-WHEN** a build that exits non-zero cannot be followed by an upload in
the same invocation, and the refusal names the build's exit code.
**BLOCKED-BY** nothing.

Found by Code on itself, 2026-08-27: build and deploy chained in one command,
`BUILD EXIT=1` printed, deploy read only its own output and put twelve wrong
models live. **The check Code had written was green, so the thing being watched
agreed with him, and the gate that disagreed was in the output he skipped.**

Q4 put the BROWSER checks in front of the upload. Nothing puts a FAILED BUILD
in front of it, **and a deploy legitimately does not require a build** - so the
gate cannot simply be "a build must have run". It has to be: *if a build ran in
this invocation and failed, stop.*

**The control: chain a deliberately-failing build to a deploy and assert the
upload does not happen.**

### Q3 — SCALE THE 12 FROM `model_scaled.glb`, NOT FROM `model.glb`
**DONE-WHEN** the 12 pre-existing wrong-scale models are at their published
dimensions AND `_verify_holo_placement.py` still passes all 8 checks.
**BLOCKED-BY** nothing. **C1 has ruled - see the reasoning below.**

Code's finding: he rescales from `sc-ships/<ship>/model.glb`, but the deployed
model came from `model_scaled.glb`, and **for some ships those two are not the
same geometry.** Scaling the original therefore produced a hull with a
different bbox centre and half-extent ratio than the markers were derived
against - San'tok.yai off by 29.6%, Vulture 8.5%.

**Scale from `model_scaled.glb`.** It preserves the exact geometry every
downstream artifact was derived against: the hull-geometry boxes, the marker
`unit` values, C1's hardpoint placement scale, and the camera-fit band. The
alternative - rescale then regenerate - is a four-step chain, and for hulls
with no real CGA coordinates it would re-derive GUESSES against a moved hull,
which is churn without gain.

**And the cost of the safe option is zero.** Code's own words: the 12 being
wrong-scale *"is visible to nobody - the viewer frames the camera to whatever
it loads."* There is no reason to take the risky path for an invisible defect.

### Q4 — THE DISCLOSURE BAR ON THE OTHER THREE PAGES
**DONE-WHEN** `_verify_disclosure.mjs` is green with every explanation block on
`find`, `keybinds` and `index` collapsed, and D1 still green.
**BLOCKED-BY** nothing.

The loadout page is the reference implementation and it is built and deployed.
**Eleven amber blocks remain** — keybinds x5, index x4, find x2.

**Audit each one against the rule before touching it, and record the verdict
per block.** Collapse a block that EXPLAINS. Never collapse one that WARNS,
reports an ERROR, or states WHAT THE VISITOR IS LOOKING AT. The download
page's antivirus notice, find's error and empty states, and the keybinds
capture warnings are all NEVER. **A block collapsed that should not have been
is a warning nobody reads.**

### Q5 — THE ROADMAP WATCHER, PAST R0
**DONE-WHEN** R1-R3 of `AMENDS_roadmap-watcher-board-1-is-wrong-2026-08-27.md`
are built and the watcher reports a real board state.
**BLOCKED-BY** nothing. R0 is done — the board is identified.

Key on card presence plus a payload hash. **Never on `updateDate`** — the API
returns Aug 2024 for a card the UI renders as Aug 2021.

### Q6 — RUN THE COLLECTOR SELFTEST. FIND OUT WHAT FAILS.
**DONE-WHEN** `go build` and `.\collector.exe --selftest` have been run and the
result is written down — pass, fail, or could-not-run with the reason.
**BLOCKED-BY** nothing.

**~190 checks have never been executed once.** That is why `capture_keys`
shipped dead in every build. The old reason was that no Claude session could
run a Windows binary — **that is stale for Code**, which ran
`venv\Scripts\python.exe` and `powershell` today.

**Do not write another collector check until these run.** If they cannot run,
the reason is the deliverable.

### Q7 — LABEL EVERY CHECK THAT CANNOT MEET RULE 16
**DONE-WHEN** every check in `checks/` either draws its truth from a real
source or carries an UNPROVEN label naming what it could not reach.
**BLOCKED-BY** Q6 for the collector's set.

Rule 16 is adopted. This is the cost of adopting it, and it makes the board
look worse before better — that is the point. A silent gap becomes a labelled
one.

---

# C1'S QUEUE

### M1 — THE THREE REMAINING EXPLANATION BLOCKS — DONE 2026-08-27
All converted to disclosure bars. Zero `.trip` blocks remain on the page and
the rule itself is gone (see M7).

### M2 — THE LOADOUT BENCH
`BRIEF_the-loadout-bench-is-an-experience-2026-08-26.md`. Approved after seven
prototypes and never built. **The swap loop, not a list of components** —
Sleven's own words: *"the interaction of actually going through the steps of
swapping the parts and understanding what they do needs to be a smooth, fluid
process... I want them to actually enjoy the experience."*

### M3 — HARDPOINT COVERAGE — SUPERSEDED, see M8, M10, M11, M12, M13
This item's numbers are from before any of tonight's work and reading them now
would send someone after problems that no longer exist. **Current state: 245 of
the ship page's classes have every marker on CIG coordinates, 20 have none, and
each of those 20 has a written reason.** M13 carries the list.

### M8 — THE ACCEPTANCE TEST JUDGED THE WRONG FRAME — DONE 2026-08-27 20:15
`build_hardpoint_placement.py` measured mounts against the hull box **as the
file stores it**; `cc_viewer.frame()` recentres every hull on that box before
drawing it. **71 of 258 models are not centred on their own origin**, so those
were judged in a frame nobody renders. M2 Hercules 11/149 inside → 140/149, the
C2's number exactly, on identical decoded data. Four Constellation variants now
agree where one used to disagree.

Passed 138 → 139 (gained M2, Valkyrie, SRV; **lost Aquila and Spirit A1** —
their offsets were flattering them). Overlay 952 → 939 ports; new records 29 →
30 hulls / 2,612 ports.

**I also broke the gate and a check I had just written caught it.** Making it
proportional — refuse above half, withhold ports below — lets a **transposed
lateral/vertical axis pass on every hull tested**, because ships are wider than
they are tall and the swap only displaces about a sixth of the mounts. That is
the defect the gate exists for. Reverted, and the reasoning is recorded in the
source so nobody re-derives it.

New: `checks/_verify_placement_gate.py` — three broken frames plus a negative
control, no database, no browser. Exits 0.

**Two more defects found while looking, both silent:**
- The same ship placed twice under two spellings (`ANVL_Hornet_F7A_MK1` and
  `anvl_hornet_f7a_mk1`), the guard comparing exact strings, both writing the
  same file. Manifest said 182 ships for 180 files. Claims fold to lower case.
- **The overlay reads the placement DIRECTORY, not its manifest**, so a refused
  hull kept its file from an earlier run and kept being emitted. The run
  reconciles its directory now and exits fatally if it cannot — proven by a
  planted control, not asserted. 93 stale files moved to
  `_to_delete/hardpoint-placement-stale-2026-08-27/`.

**Final: overlay 93 hulls / 955 ports · client records 30 hulls / 2,612 ports ·
ship page 163 → 165 classes fully on CIG coordinates · 304 client markers, none
emitting zero.**

**Two broken models, not ours:** `Avenger_Stalker.glb` is a tenth the size of
its own siblings; `Aurora_SE.glb` is 87.6 wide against 8.2 for every other
Aurora.

### M10 — THE HULL RULE WAS BLIND TO 15 SHIPS — DONE 2026-08-27 19:45
`build_hardpoint_transforms.py` takes the `.cga` whose stem equals a contiguous
run of its own folders. **120 of 18,891 entries, and right about all 120** — the
archive is mostly bunk beds and dashboards. But CIG does not always name a
folder for the ship inside it:

    AEGS\Sabre\AEGS_Sabre_Raven.cga          MISC\Freelancer_v2\MISC_Freelancer.cga
    ORIG\300_Series\ORIG_300I.cga            AEGS\Idris_Frigate\Exteriors\AEGS_Idris.cga

**Second rule added: exact equality against CIG's own `ClassName` list in
ships.json.** An authority, not a pattern — it cannot admit a prop because
there is no ship class called `aegs_hab_bunkbed_sq_player`. Javelin and Basher
are ambiguous (two paths each, one under `dmg`) and are dropped and named.

    transforms  116 -> 135 hulls      placement 146 -> 160, 137 -> 150 passed
    overlay     93/955 -> 106/1,082   ship page 165 -> 181 classes on CIG coords

Newly real: the whole Freelancer family, Cutlass Black and Red, Constellation
Aquila and both Phoenixes, 300i, Sabre Raven, Vanguard Hoplite, Fury LX,
MPUV 1T.

**The 4.10 snapshot landed mid-run.** `build_hardpoint_placement.py` takes the
newest by design, so hulls are now scaled against 4.10 lengths and the
manifest's `dimensions` points there. Nobody chose it; the newest changed.
Acceptance still 150/160. Flagged to Code rather than left in a diff.

### M12 — CIG'S OWN RECORD NAMES THE HULL — DONE 2026-08-27 20:30
I wrote in M9 that ships.json carries no geometry path and that I had checked
every field. **I checked for a PATH. The answer is a NAME, one level down.**

    anvl_c8_pisces  ->  Parts[0].Name == "ANVL_Pisces"

309 of 318 classes carry a part-tree root; 183 name a hull other than
themselves. It reaches what no name rule could — `ANVL_C8_Pisces ->
ANVL_Pisces`, `RSI_Ursa_Medivac -> RSI_Ursa_Rover`, `GRIN_MDC -> GRIN_MXC`.
**Replaced the `cls + "_"` prefix expansion**, and it is safe where the earlier
name-expansion was not: only ports whose HardpointName is a node in that hull
are placed, so a module-specific mount gets no position rather than a wrong one.

Root names fed back into the decoder too — a name CIG uses as a root IS a hull
name, which picked up `AEGS_Idris`. One collision needed a tie-break: a
folder-rule path (name AND location agree) beats a class-name-only one. Equal
evidence still drops both.

### M13 — HALF THE FLEET WAS IN A TREE NOBODY SCANNED — DONE 2026-08-27 20:32
`Data\Objects\Spaceships` 23,083 entries, scanned. **`Data\Objects\Vehicles`
1,762 entries, never.** Ground vehicles live there. Cyclone, Storm, Nova, Ursa,
Ballista, Centurion, Spartan, Lynx were all "no .cga anywhere" for that reason.

    transforms 116 -> 153 · placement 146 -> 284 converted, 137 -> 277 passed
    overlay    93/955 -> 167 hulls / 1,720 ports
    ship page  165 -> 245 classes fully on CIG coordinates · 91 -> 20 with none

**The 20 remaining, each with a reason:** ATLS family (a power suit, under
Characters\PowerSuit), GRIN MDC/MTC/ROC (no exterior mount at all), three
Cyclone variants (records name no decoded root), Javelin (two paths, equal
evidence), Glaive and Scythe (asymmetric), MOTH, Starfarer Gemini. **None is a
guess waiting to be taken.**

### M11 — NINE OF TEN REFUSALS WERE A POSE, NOT A FRAME — DONE 2026-08-27 19:58
Reading *which* mounts were outside settled it: the Constellation's three are
the top-turret mounts 0.53–0.71 above a 13.2-tall hull; the Reliant's are its
wing-tip guns and its wings move. Refusing the whole hull threw away 19 good
Constellation ports to avoid 3 arguable ones — **and the fallback was worse than
what was refused.**

**The gate did not loosen.** Second signal: exterior left/right pairs must all
mirror in the converted frame. **A transpose destroys it (0 of N on every hull);
a uniform scale does not touch it.** Complementary to containment by
construction, not by argument.

**The check refuted me again mid-build.** `out == 0 or proven` let a full-hull
offset and a 4x scale through on the Eclipse and Sabre — mirroring survives
both. Bounded by an absolute count of **4**: pose mismatches run 1–3, the
smallest frame error observed is 23. Below the defect, not above it — the
opposite of the proportional gate I had to revert.

    placement 146 -> 160 converted · 137 -> 157 passed · 3 failed
    overlay   93/955 -> 112 hulls / 1,164 ports
    ship page 165 -> 182 classes fully on CIG coordinates, 84 with none

**Still refused, each with a checkable reason:** ARGO_MPUV_Transport (no
exterior mount at all), VNCL_Glaive (2 of 4 pairs mirror), VNCL_Scythe (1 of 4).

**The two Vanduul are NOT a bug — they are asymmetric ships.** Looked at:
the Glaive's "right" missile rack sits at **negative X**, on the left side of
the hull, and its wing guns are 12.9 m apart fore-and-aft, while its nose guns
and countermeasures mirror exactly. **`VNCL_Blade` mirrors perfectly** on all
four pairs from the same decoder in the same run, so the decode is sound.

The cost is real — the Glaive loses 9 good ports over 1 mount outside — and it
is left that way deliberately: the mirror cannot prove the frame of a ship that
is not symmetric, "at least one pair" is unsafe (a transpose left 1 of 39
matching by accident on the Reclaimer), and anything between one and all is a
threshold on a four-pair sample. **What would settle it is a frame proof that
does not assume symmetry.** Written up so nobody hunts a decode bug that is not
there.

### M9 — THE REMAINING 84 CANNOT BE REACHED BY NAME — MEASURED, AND I STOPPED
96 ship-page classes still carry name-derived markers. I tried expanding every
base hull to its name-variants: 75 more hulls placed, **every one passing
acceptance**, which is the shape of a check that cannot fail. It is:
containment is one-sided, so **a Gladius's mounts fit inside a Hammerhead**, and
rescaling each variant by its own Length erases what little discrimination is
left. Gating on the two models' bounding boxes instead admitted only variants
that share the base's model file — already covered. **Reverted whole.**

That question — why the decoder stopped — is now answered and worked: see M10.
**91 classes remain, and 82 of them have no exactly-named `.cga` anywhere.**

Their geometry exists and nothing says which hull is theirs. `ANVL_Pisces.cga`
is in the archive while the page calls the ship `ANVL_C8_Pisces`;
`ANVL_Lightning_F8.cga` while the class is `ANVL_Lightning_F8C`. **ships.json
carries no geometry path — every field on the row was checked.**

I tried a structural join on CIG's own `HardpointName` strings, which are the
`.cga` node names. **Four matches, two of them junk** (the ROC matching the
Prospector on a single shared mining-laser name). Partial coverage looks far
better — Pisces 6/8, Sabre Comet 8/11, Fury Miru 14/16 — **but that needs a
threshold I cannot validate, and the acceptance test cannot referee it: a wrong
hull that is merely larger passes.**

**Stopped there deliberately.** It is the same trap I fell into twice today, and
the third time would be a choice. What would settle it is a second independent
signal that must agree with the structural one. Not a five-minute job, and not
to be guessed at.

### M4 — THE MIRROR THRESHOLD — MOSTLY ANSWERED, see M11
The question was whether a low mirror score means a bad decode or an asymmetric
ship. **It is the ship**, at least for the two hulls it now costs anything:
`VNCL_Blade` mirrors 4 of 4 from the same decoder in the same run while the
Glaive's "right" missile rack sits at negative X. The mirror is now used as a
frame proof rather than a pass/fail on the hull, so a low score only costs
something where a mount is ALSO outside the box — which today is the Glaive and
the Scythe and nothing else.

**Still open, narrowly:** a frame proof that does not assume symmetry, which
would let those two in. Nobody should widen the mirror tolerance to get there.

### M5 — `CURRENT-STATE.md` — SPLIT, DONE 2026-08-27 20:45
**It is no longer eleven days stale.** It was brought forward earlier today and
now leads with 08-27 material. The staleness half of this item is closed and I
am not going to keep claiming it.

**The structural half stands and is worse than the staleness was.** 13,554
words, ordered newest-first, opening with an instruction that everything below a
certain point is history. A reader cannot tell where that point is, so the only
safe read is all of it, every session, forever.

**One live number was wrong and is fixed rather than filed against.** Line 79
said *"ten distinct damage-multiplier profiles"* since 08-22. Three independent
counts say **eight** (`FINDING_both-open-questions-closed...`). Corrected in
place with the correction visible, not silently.

**DONE.** Split into two files, nothing deleted:

    docs/CURRENT-STATE.md                      1,487 words - only what is true
    docs/STATE-ARCHIVE-through-2026-08-27.md  13,801 words - the original, verbatim

The new one carries no "later section wins" rule because it has no later
sections. **It states its own maintenance rule: it does not grow by appending.**
A fact that stops being true is edited or deleted there, and the reasoning goes
in a dated `docs/FINDING_*` or `docs/DECISION_*`. A snapshot, not a log.

The archive's header names its own known-stale parts up front — the collector
section saying "none of it has run on Windows" when it passed 575 checks today,
and hardpoint numbers from before tonight — so nobody has to discover them.

Both written to the claude.ai project as well, since the project instructions
point new sessions at `claude/CURRENT-STATE.md`.

### M6 — THE SHIELD SENTENCE — DONE 2026-08-27 18:20, AND C3'S NUMBER WAS WRONG
C3 ranked *"a shield stops all of a laser's damage and only 45% of a
ballistic's"* first of six things to build, ahead of everything needing a
calculator. **The energy half is exact. The ballistic half is the top of a
range** — `Absorption.Physical` reads Minimum 0, Maximum 0.45, and Energy is the
only channel where the ends meet. Measured by me on 73 shield items, one profile
across all of them.

**And shields carry a second `Shield.Resistance` block** — physical 0–0.25,
distortion 0.75–0.95 — which is NOT the `Durability.Resistance` that
`FINDING_both-open-questions-closed` established as item durability. Different
block, different path. The effective-damage calculator stays blocked.

**Shipped the honest version** on the ship page under the armour matchup table,
stamped `SHIELDS · 4.9`, with the range as a range. Full working:
`docs/FINDING_the-45-percent-is-the-top-of-a-range-2026-08-27.md`.

### M7 — THE DISCLOSURE CSS IS ONE COPY AGAIN — DONE 2026-08-27 18:10
Code extracted my `.disc` rules into `testing/_src/_disc.css` for find, keybinds
and index, and left this page's copy alone because it is not Code's file —
noting loadout could point at the file whenever C1 wanted. **It wanted.** The
rules were diffed first (identical, line for line; only comments differed), then
replaced with the build's `/* CC_DISC_CSS */` marker. The dead `.trip` rule went
with it — zero elements carried the class.

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

*Maintained by C1. Last set 2026-08-27 20:45 local.*
