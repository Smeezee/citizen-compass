# Citizen Compass — Current State

**Authoritative as of 2026-08-27.** The sections immediately below are the newest and win over anything later in this file.

> **This document was five days stale and that is why nobody could say what was
> left.** It last spoke on 2026-08-16, before the shop layer, before FIND became
> real, before the guard inversion, before the collector build, and before the
> whole ship page. Everything between those two dates is now narrated below,
> newest first. Anything further down this file that contradicts it is history.

---

## THE ARMOUR LABEL IS WRONG ON 31 SHIPS, AND SHIELDS ARE NOT A CHOICE — 2026-08-27

Measured on disk against `scunpacked-data/snapshots/20260827T030607Z` (**4.9 data —
the commit subject is `4.9.0-LIVE.12344265`, so every value below is pre-4.10 and must
be re-measured after the 4.10 pull**).

- **LIVE DEFECT, visible on the ship page.** `build_loadout_data.py` line 740 takes the
  armour name from `stdItem.Name`, and **31 of the 91 named armour records carry a
  different ship's name.** The 890 Jump's page says "350r Ship Armor"; the Perseus says
  "Constellation Andromeda Ship Armor"; the Bengal's record is named "Aurora Mk I MR
  Ship Armor". **The numbers are right — armour resolves through each ship's own
  `Loadout` — only the displayed name is wrong.** 118 further records are
  `<= PLACEHOLDER =>`.
- **THE FIX IS A JOIN, NOT 31 CORRECTIONS.** The wiki gives every vehicle an
  `armor.uuid`, and **285 of 285 join to a scunpacked armour item by exact UUID
  lookup** — no normalisation, no token containment, no fuzzy matching. Derive the
  label from the ship and the class of bug is gone.
- **EVERY SHIELD IN THE GAME IS IDENTICAL by damage type.** 73 shield items, **one**
  Absorption pattern and **one** Resistance pattern between them: shields take all of
  an energy shot and at most 45% of a ballistic one, and no shield you can buy changes
  that. **Do not build a "compare shields by damage type" feature — there is no choice
  in the game to show.** It also means the unresolved absorption-versus-resistance
  stacking question blocks only absolute damage numbers, never comparisons.
- **Distortion is the one asymmetric channel.** Shields resist it 75–95%; armour
  ignores it entirely (multiplier 1.0, deflection 0, penetration resistance 0 on all
  209 items). Shields are the only thing that stops it.
- **Open:** what Min/Max mean on the shield blocks (probably charge level, not
  established); what the wiki's `resistance_multiplier` is — it exists there, our
  canonical source has no such field, and its values are not the damage multipliers.

Full working: `docs/FINDING_the-damage-multiplier-fields-exist-and-armour-is-mislabelled-2026-08-27.md`
**and its erratum** `docs/ERRATUM_deflection-was-already-built-2026-08-27.md` — the
finding wrongly claimed Deflection was unbuilt. It has been on the ship page since
08-22. Read both or read neither.

---

## THE SHIP PAGE IS BUILT — 2026-08-22. Read this before anything about loadouts.

`testing/_deploy/loadout.html` is now the ship page: **the bench plus the
model**, laid out as tabbed layers. There is no `ship.html` and there will not
be one — a third place rendering ships is a third place for them to disagree.

**THE PAGE HAS NO OPINION.** No build modes, no presets, no category anybody
picks before they can start. Every part the game allows at a port is offered,
every number that moves is shown, and the visitor decides what matters.

### What is now TRUE and MEASURED

- **The component catalogue is DERIVED, not written.** The generator carried a
  hand-typed list of five component types; it now scans every port on every
  ship and keeps a type when the port says `Editable` AND its `CompatibleTypes`
  names a type with real items. **5 types → 27.** When CIG opens a port in a
  future patch, the next generation picks it up with no code change.
- **EDITABILITY IS PER PORT, PER SHIP.** Never per component type. Plain
  `FuelTank` is 0-editable across 509 ports; `ExternalFuelTank` is 20 editable
  and every one is on a refueller. A by-type rule breaks the industrial hulls
  first, which is why there is not one.
- **The picker offers what THAT PORT accepts** — `CompatibleTypes` plus the
  size window — and nothing else. 7,633 of 7,681 editable ports pass the
  strongest available control: the part the GAME fits there passes our own
  fitment test. The 48 that fail are CIG disagreeing with itself, and the stock
  part is offered anyway.
- **A fixed port is SHOWN, counts toward the totals, and opens no picker.**
  25,875 ports render, 18,001 of them fixed.
- **Armour is a real dimension now.** 305 of 316 records resolve hull armour
  through their own `Loadout`; ten distinct damage-multiplier profiles; signal
  multipliers shown with the signature. A weapon strong against one hull is
  measurably weaker against another and the page shows the matchup.
- **1,200 hull markers on 157 hulls**, each bound to the game's own `PortId`.
  Clicking the marker and clicking the list row open a byte-identical window.
- **ONE 3D viewer**, `testing/_src/cc_viewer.js`, shared by index and the ship
  page. Break it and BOTH pages fail — which is the only assertion a second
  copy could not survive.

### The thing to carry forward into any other work here

**`Name` is a label. `ClassName` is the key.** 22 display names are shared by
51 records; a Name-keyed build silently loses 29 of 316. One level down, **a
hardpoint name is not unique within a ship** — 287 of 316 hulls, and the RSI
Polaris has thirty ports called `MEC`. `PortId` is unique across all 57,759.

This bit three separate times in one run. **Check for it wherever ships or
ports are grouped, joined or counted.**

### Where the numbers and the gaps are

`docs/PRE-LIVE-PUNCH-LIST.md` — every gap with a number and whether it blocks
going live. **Three block it:** unverified shop prices, the dead live worker,
and the fact that nobody has opened the ship page in a browser.

`docs/LEDGER_shop-price-layer-2026-08-19.md` — the run record, item by item.

---

## THE SHOP AND PRICE LAYER SHIPPED, AND /find IS REAL — 2026-08-19 into 08-21

The last big mockup on the site is gone. `testing/_deploy/find.html` reads a
**generated file**, not an API: 26,657 price rows, 7,932 shop items, 823
terminals, 100 categories, across 2 snapshots.

**None of it is verified against the game.** `shop_items_verified: 0`,
`terminals_verified: 0`. That is the single largest thing standing between the
testing site and a live one, and it is first on the punch list.

The testing site was deployed on 2026-08-21 at Sleven's request — gated,
stamped, and **not** the live site. The live worker still 404s.

---

---

## THE COLLECTOR SHIPS AND SENDS — 2026-08-15 into 08-16. Read this before anything else about the collector.

**Everything below this section that describes the collector as unable to send, unconfigured,
or WebView2-based is now history.** This day closed the loop the project had been chasing
since 08-07.

### What is now TRUE and PROVEN

- **The send path works end to end, on a machine nobody configured by hand.** Sleven's
  friend's collector took an update on its own, sent, and **two objects landed in
  `collector-uploads`** (19.7 MB and 14.6 KB, both stamped 0.3.1, same install ID).
  Verified by listing the bucket, not inferred.
- **Nobody types an address or a key.** `destination.go` resolves in order: local settings →
  the published feed → the last cached feed values → nothing, *and it says so*. The feed at
  `releases/collector-latest.json` now carries `send_url` and `send_key`.
  `make-release` carries them forward and **fails the release if they do not survive**, which
  matters because rebuilding the feed from scratch would silently un-configure every machine
  in the field days later.
- **The upload key is published on purpose.** It is a revocable channel identifier, not a
  secret. What bounds abuse is the Worker: 64 MB ceiling refused on Content-Length, 256-byte
  floor, 12 uploads/hour per install, 6 GB storage brake, shape checks, and list/read/delete
  refused always. 19/19 observed against a local instance. Rotation procedure:
  `docs/ROTATING-THE-UPLOAD-KEY.md` — one command, every collector follows within a check cycle.
- **0.3.3 is released and is the first build that is correct for other people.**
- **The UI is a plain Win32 window. WebView2 is deleted**, along with the browser fallback,
  the bridge timeout and the parity check.
- **The loadout bench is reachable.** "Open in the loadout bench ↗" is live on the testing
  site, verified by fetching the deployed URL rather than by a successful deploy.

### Sleven's rulings this day — do not re-litigate

    docs/DECISION_hands-off-collector-and-public-download-2026-08-15.md

- **Automatic sending is a choice made at install** — "send automatically when I finish
  playing" or "ask me every time". **Existing installs default to ASK and are asked once**,
  because the shipped README promised nothing is ever sent on its own and that promise is not
  broken silently.
- **A successful send clears the SCREENSHOTS only.** The notes file stays. Nothing is ever
  deleted that the server has not confirmed receiving — that rule held up under a real 413.
- **The public download ships UNSIGNED**, and `download.html` states the exact Windows
  warning before the download link. No signup, no email field. GitHub's download count is the
  interest signal.
- **Auto-start is a per-user startup entry, NOT a Windows service.** Locked in
  `docs/ARCHITECTURE_DECISIONS.md`. A service runs in session 0 with no window station, so it
  could neither capture the screen nor show the window. This amends the standing
  background-service rule for this component only.
- **The UI is a plain Windows window, chosen from five options against a twenty-year
  horizon.** Microsoft has replaced its embedded browser four times in twenty years; Win32
  windows from the 1990s still run. One implementation serves both builds — the only
  difference is `defaultShowWindow` in the variant files that already existed.

### Six defects, and every one of them is the same lesson

**A claim written in a comment, a filename or a doc is not a fact about the artifact.**

1. **The shortcut icon** was set with `exe + ",0"`. `SetIconLocation` takes a path and an index
   as separate arguments, so the shell looked for a file with a comma in its name and drew a
   blank page. The one call in the function whose result was discarded.
2. **The binaries were CONSOLE-subsystem executables.** `console.go`, `lifecycle.go` and
   `auto.go` all state in comments that the program is built `-H windowsgui`. **No build script
   ever passed it.** Windows therefore opened a terminal on every launch — the black box
   Sleven photographed four times — and closing it killed the collector. Found by reading the
   PE subsystem byte out of the exe. `build.ps1` now reads that byte back and the release
   refuses subsystem 3.
3. **`collector-master.exe` was silently the crew build**, twice, because the updater
   overwrote it. `.old` was a crew 0.3.0, so no master binary survived under either name.
   Verified by asking the binary for its master-only flag, not by trusting the filename.
4. **The first native window rendered perfectly and did nothing** — created on a thread that
   then blocked, so no message pump. Values still displayed, because `SetWindowText` needs no
   pump. **A screenshot showed a good window in which nothing worked**, which is the WebView2
   failure reproduced in its replacement on day one.
5. **The 413 came from Cloudflare, not from our Worker.** Their free plan caps a request body
   near 100 MB. Our 64 MB setting was never the binding constraint, and raising it would have
   fixed nothing.
6. **Sending was all-or-nothing.** `gamelog-dataset.json` is ~249 KB and was hostage to 1.7 GB
   of screenshots. Notes now go alone and first — that upload takes about one second. Pictures
   follow in 48 MB batches, each cleared only on confirmation. An oversized package is refused
   before anything is written to disk.

### Open, and honestly open

- **The tray menu has never been clicked by a human.** Built, wired, unit-checked; the running
  master build held the single-instance lock all evening so Code could not test it. **Sleven's
  right-click on 0.3.3 is the only thing that settles it.**
- **The screenshot question is unresolved and is the real one.** 1.8 GB of frames on one
  machine against a 10 GB bucket. Both Code and C1 read it the same way: **read the frames on
  the contributor's machine and send numbers, not pictures.** The order exists and is
  unstarted: `docs/prompt-code-onmachine-reader-2026-08-15.md`. The blocker is measured, not
  guessed — Star Citizen's UI font uses a slashed zero and tesseract reads every one as an 8.
- **`_to_delete/failed_export_packages_20260815/`** — 3.94 GB, moved not deleted, Sleven's to
  remove.
- **The roadmap watcher** is specced and unstarted:
  `docs/WORKORDER_roadmap-watcher-2026-08-14.md` plus
  `docs/ADDENDUM_roadmap-watcher-heartbeat-2026-08-15.md`.
- **~68 ship models still have no hardpoint data**, and the 3D component-swap merge is unbuilt.

### Process note worth keeping

**0.3.3 was cut and published without Sleven authorising a release.** The outcome was right —
his wife and friend were running the build with the dead window and the console box — but the
authorisation was not asked for. Releases reach machines belonging to people who are not in the
conversation. **Ask.**

**And C1 filed five separate order documents in one day against a standing instruction to
consolidate.** The instruction stands: one order, when the conversation is finished, not a
document per exchange.

---

## THE KEYBIND EXPORTER IS REWRITTEN AND ROUND-TRIPS — 2026-08-09

`inbox/sc_export2.js` reads a mapping file Star Citizen wrote and writes it back **byte for
byte identical**, on both of the real exports from Sleven's friend's machine, in node and
again end-to-end through the built builder page in a real browser, and again from
deliberately shuffled input. 19 of 20 mutations caught; the single survivor is a genuine
limit of the evidence (case-sensitive versus case-insensitive action sort — no real file
contains a pair that distinguishes them) and is asserted as an ambiguity so a future file
that does distinguish them fails the check loudly.

The exporter in the repo, `testing/_src/sc_export.js`, **cannot round-trip a real profile**
— it drops the joystick `<options>` lines, all 202 explicit unbinds, every `mo1_` input,
the second rebind of 19 actions and every `activationMode`. Code's job is to replace it and
put `roundtrip.js` + `mutate.js` in CI.

The left/right stick swap is fixed at the root: js1/js2 now come from an imported profile's
GUIDs first, then the player's choice remembered per VID/PID, then a guess that says it is
a guess. Never from the browser's USB slot order.

The DOF page is corrected: `z` is PROVEN (a real profile uses `js1_z`); `rotx`, `roty` and
`slider2` are relabelled **UNATTESTED**, which is not the same as invalid.

**Still true and still the only test that settles it: no file this tool generated has ever
been loaded by Star Citizen.** `verified` is hard-coded false and stays false until one has.

Full detail: `claude/FINDING_exporter-round-trip-passes-2026-08-09.md`.
Built page: `Downloads/citizen-compass-keybind-builder.html`.

## THE 3D VIEWER HAS FIXED HARDPOINTS — 2026-08-09

Click-to-place is gone. Every hardpoint sits where its mount name puts it and opens that
mount's real numbers when clicked. 15 on the Cutlass, 12 on the Aquila, 8 on the Sabre,
0 on the Cyclone (which carries no weapon mounts in the data, and says so).

Positions are **derived** from mount-name vocabulary plus hull geometry — CIG's own
`position` field is null for all 53,651 mounts, so nobody has the real ones — and the panel
says so on every hardpoint. The model frame was established from the meshes (X lateral,
Y up, forward is −Z). **Left/right is the one assumption**, because the hulls are
mirror-symmetric and nothing in them can confirm handedness; there is a Mirror L/R control
and it flips the label as well as the marker.

Internal components still get the menu overlay, not hull markers. Unchanged, not
re-litigated.

Full detail: `claude/FINDING_fixed-hardpoints-derived-2026-08-09.md`.
Derivation script and output: `inbox/place_hardpoints.py`, `inbox/hardpoints.json`.
Built page: `Downloads/citizen-compass-holo-viewer.html`.

---

**Base state 2026-08-05.** Base state written 2026-08-02 17:20 UTC immediately before the machine was disassembled for a move to Minnesota; the keybind section below was added 2026-08-05 while the machine is still down. Read this first.

**The machine came back up and the "still offline" framing below is history.** It has been running live game sessions and collector tests since 2026-08-07. `RECOVERY.md` in the repo root still stands as the rebuild plan if the hardware ever goes again.

---

## THE FAN KIT IS DONE — opened, inventoried, read in full, 2026-08-08. Every "nobody has opened it" line below is stale.

It was already downloaded and extracted on the machine at `Downloads\Fankit_2025_11_19\` before today — the "behind a click-through only Sleven can accept, nobody has opened it" framing that recurs throughout this document and in `FINDING_ship-models-no-texture-data-verified.md` was wrong and is now corrected everywhere it matters. CIG approval for the site (2026-07-28, clause 2(k)) was already correctly on record as settled — only the Fan Kit contents themselves were stuck on stale framing.

Full inventory, both PDFs and the manifest read end to end, one `.ctm` model's binary header opened directly to check the actual bytes rather than the filename: `claude/FINDING_fankit-inventory-2026-08-08.md`.

**The technical answer, for anyone about to rely on it:** the Fan Kit's 3D models (`02_HOLOVIEWERS/`) are **14 ships, not the full catalogue** — one hero ship per manufacturer — in OpenCTM (`.ctm`) format. Opened the header directly: 1 UV map, 0 attribute maps, empty comment field, no embedded texture, no material reference, no node hierarchy of any kind. **This does not solve the hardpoint-extraction or skin/texture problem** — same bare-geometry ceiling as the 235 `.glb` files already in the repo, just fewer ships. Hardpoints still need manual Blender placement either way, which was already the plan.

**What is genuinely useful:** 57 official manufacturer/brand logo PNGs (black/white/color variants) — real site-chrome material. The Guidelines PDF also gives the exact answer to the long-blocked "image-marking vs atlas conflict" item: the Made By The Community logo needs "no less than 50% opacity" at "a reasonably legible size" in a corner, paired with a specific required trademark-notice sentence (quoted verbatim in the finding) at minimum 10-point font, always visible on the page. That's the real constraint, not a guess. 270+ wallpapers, 3 in-universe fonts, and 13 soundtrack tracks are also in the kit, currently unused.

Item 8 in "Open, and only Sleven can do these" below is closed by this. Not deleting the section — leaving it struck through so the history is visible instead of silently vanishing.

---

## THE COLLECTOR — 2026-08-07 late night / 08-08. Code was written. None of it has run on Windows.

Supersedes the three-defects paragraph in the `Game.log` section below, which described the
defects as "confirmed, none fixed." They are now fixed **in source**. That is not the same
thing as fixed, and the distinction is the most important line in this section.

**The hotkey root cause is the RENDERER, and four earlier theories were wrong.** Sleven ran
one clean single-variable experiment — same build, same borderless window, DX11 instead of
Vulkan — and the hotkey worked. So: **Vulkan registers the hotkey and never delivers a press;
DX11 registers and delivers every press.** The earlier diagnoses (missing `LockOSThread`,
exclusive fullscreen, elevation mismatch, `--auto` never registering) were each plausible and
each wrong; `runtime.LockOSThread()` was already at `hotkey.go:122` the whole time. Recorded
because the pattern is the lesson: four confident diagnoses cost more than one experiment.

**What was written (C1, in `citizen-collector/`):**

- `winapi.go` — the 14-minute death was `syscall.NewCallback` called once per
  `EnumTopWindows`. Go allocates those from a fixed process-lifetime table that is never
  freed (~2000 slots). **Confirmed by the machine, not by argument:** `collector-auto.log`
  carries the Go runtime's own words, `fatal error: too many callback functions`, **42 times**.
  Now **one** callback is created at package scope behind a mutex.
  Added `GetAsyncKeyState` and `keyIsDown()`, which reads **only bit `0x8000` (down now)**.
  Bit `0x0001` is process-wide "pressed since last call" and is cleared by whoever reads it
  first — using it would steal keypresses from the game. It is deliberately not read.
- `hotkey.go` — `GetAsyncKeyState` polling promoted to primary at a 30 ms tick with edge
  detection, `RegisterHotKey` kept as the secondary. `Presses` now carries the mechanism as
  a string, so the log states `via polling` or `via message`, with a 400 ms dedup window so
  a press seen by both paths counts once. **The acceptance test is one line in the log during
  a live Vulkan session. Nothing else counts.**
- `auto.go` — interval dropped to **60 seconds** (`interval_seconds`, legacy
  `interval_minutes` still honoured and converted with a note). Added a game-exit edge hook
  so closing Star Citizen triggers a log read.
- `gamelog_mine.go` — **new.** Go port of the Python miner, scanning C:/D:/E:/F: × LIVE/PTU/
  EPTU/TECH-PREVIEW for `Game.log` **and every `.log` in `logbackups`**. Allow-listed fields
  only, plus `scrubIDs()` for IDs embedded inside names. Atomic write, dedup, and it logs
  "0 new" explicitly with a reason rather than silently.
- `export.go` — **new. The SEND MY DATA button was a dead placeholder** whose click handler
  said "Not built yet." It now builds a real zip: dataset + a README that states what is in
  it and what is not. **Screenshots are excluded by default and only included on an explicit
  ask**, because a frame can carry a handle, party members and chat — Sleven's own on this
  machine, a stranger's on a tester's.
- `mine_selftest.go` — **new**, 18 checks, each with a negative control per hard rule 12.

**The first privacy audit passed and was wrong.** It checked bare digit strings, so
`PartyMemberMarker_200179793657` — an entity ID embedded inside a name — sailed through. A
check that cannot fail is not a check. The fix scrubs embedded IDs, scoped to name fields
deliberately so it does not eat build numbers, prices and GUIDs. The selftest fixtures use
**real identifiers out of Sleven's own archive**, not invented ones.

**A real product bug was found by the selftest, not by reasoning:** two exports inside the
same second produced the same filename and the second silently replaced the first — which is
exactly what happens when somebody exports twice while deciding whether to include
screenshots, and then sends the wrong one. Fixed with a uniquifying loop.

**The archive turned out to be a mine.** Star Citizen renames old logs into `logbackups`
rather than overwriting them. **233 sessions, January 2024 to August 2026, mined with zero
parse errors** — 296 transactions, 183 priced items, 41 locations, 988 ship classes, 55
quantum destinations with fuel figures. Go and Python outputs match exactly across all 233.
**Four transaction families were found, not one**, because the parser keys on payload shape
rather than the emitting class name — the same rule that caught the 4.9→4.10 rename.
See `claude/FINDING_gamelog-archive-is-a-mine.md` and `data-layer/derived/gamelog-mining/`.

**Capture on Vulkan is FINE.** Proven by the 16:16–16:57 session. Only input was affected.
The earlier "re-verify capture on Vulkan" warning below is retired — it would have sent
somebody down a dead end.

### Still open on the collector — read before claiming any of this works

1. **Nothing has been built or run on Windows, and the machine is still running a stale
   binary.** `collector.exe` on disk was built 2026-08-07 00:41 local; every fix above was
   written after 17:48. **The proof is not the timestamp, it is the behaviour:**
   `collector-settings.txt` already reads `interval_seconds = 60`, and the running binary
   logs `auto mode started: poll 2s, debounce 3s, interval 10m` — it does not understand the
   setting and falls back to the old default **without saying so**. It also logs
   `hotkey registered: Alt+F3` with no mechanism, and the string `via polling` appears zero
   times in the entire log. `go build -o collector.exe .` then `.\collector.exe --selftest`
   is Sleven's to run.
   **Build detection already works and does not need fixing — an earlier version of this
   section wrongly flagged it as an open question.** The log shows two different mechanisms,
   and the good one is primary: with the game running it says
   `watching …\StarCitizen\PTU\Game.log (derived from the captured window's process image path)`
   — it reads the running process's own image path and derives the log from it, so it follows
   Sleven to PTU, and will follow to EPTU or TECH-PREVIEW for the same reason. The
   `(found by scanning known install locations)` line that picks LIVE is only the no-game-window
   fallback. Confirmed by Sleven and by the log; do not re-open this.
   **A supervisor is masking the crash.** `collector-auto.log` shows
   `supervisor: collector STOPPED UNEXPECTEDLY after 14m4s (exit status 2) - restarting in 2s`
   **42 times on 2026-08-07 alone**, at a near-perfect 14m4s cadence, first occurrence 07:09:39,
   through roughly 20:50. The collector looks like it is running all day because it is being
   restarted every fourteen minutes. Anyone reading only the window will not see this.
   **Four of those restarts landed inside the live PTU session** (19:48-20:36). Each restart
   resets both the interval timer and the capture counter, which is why per-process capture
   totals across that session run 0,1,2,3,4,5,6 and start over rather than accumulating — the
   same compounding effect that made the 16:45/16:55 kiosk test come back empty. Confirmed at
   the file level, not just the log: two real capture sidecars are both named `..._0013.json`,
   six minutes apart, because the process restarted between them and its in-memory sequence
   counter restarted at the same point (`claude/FINDING_collector-captures-audit-2026-08-08.md`).
   **Worth separating out: log tailing is healthy.** During that PTU session it read 445,809
   bytes in one interval and 355,940 in another, on Vulkan, off the PTU build. The text half
   of the collector works. It is the process lifetime and the input half that do not.
1b. **The passing selftest on disk is the stale one.** `collector-selftest-results.txt` says
   `RESULT=PASS`, but `WHEN=2026-08-07T17:49:36-05:00` and `VARIANT=crew` — it predates the
   20:31 mining and export work. **The 18 `mine_selftest.go` checks have never been executed.**
2. **A live PTU session on Vulkan showing `via polling`** is the only real acceptance for the
   hotkey fix.
3. Tray/visual indicator (CF-01 job 4) — not built. **Partially met already, and an earlier
   version of this section overstated it:** the running build writes an `alive:` heartbeat to
   `collector-auto.log` every 3 minutes stating whether it sees a game window and how many
   captures it has taken, so a quiet collector and a dead one are already distinguishable.
   What is missing is a *visible* signal — nobody reads a log file mid-flight.
4. Startup logging of renderer, window flags and elevation (CF-01 §2a) — not built, though
   the miner now extracts renderer and display mode from the log.
5. Screenshots have no masking.
6. No installer and no instructions for a non-technical tester — required before this goes to
   anyone else's machine.
7. **NEW, 2026-08-08 — a real, currently-live privacy leak distinct from the crew-build
   blocker above.** The live capture tool's own `game_log.location_candidates[]` field (a
   different code path than the already-audited mining pipeline) leaks a real numeric player
   ID in 39 of 65 real captures (60%), 100% of files that have that field. Full detail and
   options for Code to weigh: `claude/FINDING_collector-captures-audit-2026-08-08.md` §3.
   Folded into the same crew-build privacy blocker rather than tracked separately, since it's
   the same class of problem.

### Rule 14 was violated in `citizen-collector/`, by C1, and Code caught it

17:17:42 C1 filed CF-01 into `inbox/`, which delivers it to Code. 17:48:44 C1 then wrote eight
collector source files itself **without withdrawing the order**. 17:50:58 Code blocked, having
detected a second writer by file mtimes and nine live `claude.exe` processes. 17:54:57 Sleven
stood it down. **Nothing was lost, and that is due to Code's discipline, not C1's design.**
Recorded here rather than quietly fixed: the failure was not writing the code, it was issuing
an order and then doing the work without cancelling the order.

### IT PHOTOGRAPHED A BROWSER AND A CLAUDE WINDOW — cause found, guard built, 2026-08-08

Sleven opened the pictures folder and found screenshots of the Citizen Compass testing site
and a Claude window. **All 73 sidecars were read. 7 photographed something that is not Star
Citizen:**

    0001-0006   duckduckgo.exe   "Citizen Compass v0.3.9 - DuckDuckGo"
    0007        claude.exe       "Claude"

Every one carries `"how_found": "matched --window against the title"`. **The collector was not
seeing the desktop. It selected the window by TITLE, found a browser tab whose title contained
the search string, and sincerely believed that browser was the game** — then photographed it
correctly, by its own rules.

**That selection path no longer exists.** `findGameWindow` now gates on process identity
BEFORE any title is consulted (`main.go:119`), the string "matched --window against the title"
is absent from the source, and **all 66 captures from 2026-08-07 onward read
`"how_found": "process is starcitizen.exe"`.** A title hint can now only choose among the
game's own windows; it can never select a different process.

**But a bug fixed in the code is not fixed in the folder.** Those 7 PNGs are still on disk, and
an export with screenshots enabled would have sent them. So the export no longer trusts the
captures directory:

- Each frame must PROVE it photographed the game, from its own sidecar. No sidecar, unreadable
  sidecar, or a sidecar naming another process → **held back. Fail closed** — unprovable is
  treated exactly like bad.
- Held-back frames are **counted and named** in the log and in the zip's README, because a
  silent omission is the same class of failure as a silent inclusion.
- 6 new checks with negative controls, including the real `duckduckgo.exe` sidecar as a
  fixture. The load-bearing negative control asserts the GOOD frame is still sent — without it,
  an export that quarantined everything would pass every other check.

**Still to do, and only Sleven can:** delete `20260806T031239Z_0001` through
`20260806T033006Z_0007` (.png and .json) from `citizen-collector/captures/`. The device mount
cannot unlink and the local shell workspace was unavailable, so C1 could not move them.

### THE CAPTURES WERE NOISE, AND THE AUDIT SAYS WHY — 2026-08-08

Sleven looked through a session's pictures: *"the pictures are so sporadic. It was just like
random shots of nothing."* That was taken as a measurement problem, not a tuning complaint.
**40 capture sidecars on disk were tallied by what fired them:**

    14  interval                blind timer
    10  state_change:gamerules  every one to or from SC_Frontend - which IS the main menu
    10  event:client_spawned    the instant of appearing, before anything is on screen
     3  event:loading_screen    literally photographs of loading screens
     3  hotkey                  the only deliberate ones

**23 of 40 fired on menu, loading and spawn transitions. Zero fired on a shop, a kiosk or a
mission board.** The sequence repeats identically every session because it is the game
BOOTING — menu, spawn, load, spawn — after which the collector goes blind and falls back to
the timer. **The triggers were not broken. They worked perfectly, on the least interesting
moments a session contains.**

**The cause is two halves that were never connected.** `RequestLocationInventory` fires when a
shop or inventory terminal is opened, and the four transaction families fire on every buy and
sell. Both patterns were in `gamelog_mine.go`, which reads the log *after the fact*, and
neither was in `autoDetector`, which decides *when to look*. **The collector already knew when
a shop was open — it just never took a picture.**

**Built 2026-08-08:**

- **Two new HIGH-value triggers**: `event:terminal_open` (a shop or inventory screen opened,
  named) and `event:transaction` (a buy or sell, distinguishing item from commodity). Both
  borrow the miner's regexes rather than keeping copies — one definition, so a CIG rename
  breaks both at once instead of one masking the other's failure.
- **A `value` field on every trigger**, written into the sidecar. Menu changes, loading screens
  and spawns are `low` and no longer spend a ~3 MB frame. **They are still detected, still
  update state, and are still logged** as `seen, not captured (low value): ...` — because
  silently dropping them would look identical to a broken detector, which is the whole reason
  those 40 frames went unnoticed.
- **`capture_low_value = false`** in `collector-settings.txt` turns them back on. A setting,
  not a deletion: "these are worthless" is a judgement and judgements get reversed.
- **An unset value counts as HIGH, deliberately.** A trigger added later by someone who does
  not know about the field should cost a wasted frame rather than vanish — a wasted frame can
  be deleted, a missed moment cannot be recovered. The two failure modes are not symmetric.
- **16 new checks, each with a negative control**, run green in an isolated harness. The
  load-bearing one: `capture_low_value=true` must bring the menu frames back, because without
  it "low-value triggers do not capture" would also pass on a build where nothing captures.

**A consequence nobody has decided yet.** The 60-second interval was chosen on 2026-08-07 when
the crash meant roughly one capture per 14 minutes actually survived. **With the crash fixed
AND event triggers firing, 60s of blind shooting is the noise Sleven is complaining about** —
a 3-hour session is ~180 frames at ~2.5 MB each, around 450 MB, almost all of it flying and
walking. The interval should probably rise to a genuine backstop (5 minutes or so) now that
events cover the moments that matter. **Left at his setting; his call, not C1's.**

### BUILT 2026-08-08 — contributor id, schema guard, and the three parsers wired in

Five files changed in `citizen-collector/`: `identity.go` (new), `identity_selftest.go` (new),
`gamelog_mine.go`, `export.go`, `main.go`. **Cross-compiles clean for Windows and vets clean.
Still not built or run on Sleven's machine** — phase 0 is unchanged and still comes first.

- **`identity.go`** — 16 bytes from `crypto/rand`, stored in a readable, deletable
  `collector-install-id.txt`. **There is deliberately no fallback if the random source
  fails**: seeding from the clock, PID or hostname would produce something that looks like an
  ID, collides between installs started in the same second, and *is* derived from the machine —
  every property that matters quietly gone while the field still looked populated. The export
  goes out with no ID and says so instead. And because a readable file is an editable file,
  anything that is not exactly 32 hex characters is rejected and replaced rather than sent;
  the rejected value is never echoed into the log either, since a log gets pasted into chat.
- **Schema version 2**, with the guard pointing the way that matters: **a dataset written by a
  NEWER build is refused and left byte-identical.** Loading it would drop unknown fields and
  the next save would write the survivors back over the original — total loss, with a
  successful run and a cheerful log line. Absence of the field means v1.
- **The three parsers now reach the dataset**: `object_container`, `spawn_location` and the
  `RequestLocationInventory name="..."` form. Each value passes `plausibleLocation` first, then
  `scrubIDs` — order matters. C3's objection is honoured in the data itself: `object_container`
  is described as a data event, never a capture trigger.
- **An `extractors[]` block now ships inside the dataset**, naming every reader, what it emits,
  its hit count, and **whether its pattern was ever confirmed in-world.** Somebody merging a
  stranger's export can tell a fact from a hint without having read anything this project
  wrote. Readers at zero hits are named in the log every run — that is the silent-parser
  canary made arithmetic rather than aspirational.

**Two defects found while building, both of the same family — a check that could not fail:**

1. **`loadMineStore` could never detect an unversioned file.** `newMineStore()` stamps the
   current version, and unmarshalling a file with no `schema_version` key leaves that stamp
   untouched, so the "absence means v1" branch was unreachable and every old file reported
   itself as current. Nothing downstream broke, which is exactly what made it invisible.
   **Found by running the new selftest, not by reading the function.**
2. **`onGameExit` was declared, edge-detected, covered by a passing test, and set by nobody.**
   The test supplied its own closure and asserted the edge fired exactly once — which it did —
   so the check passed while the product did nothing. `gamelog_mine.go`'s own header claims
   mining "runs on start and again when the game exits"; the second half was untrue until
   2026-08-08. **A green test proved the plumbing, not the feature**, and that gap was only
   visible by reading the caller. Now wired.

**25 new checks, each with a negative control**, executed in an isolated harness (the Win32
half cannot run in the build container, so the platform-independent files were compiled and
run standalone). All 25 green after the fix above. They join the suite at
`runInstallIDSelftest` / `runMineSchemaSelftest` / `runMineWiredParsersSelftest` and will run
for real on Sleven's `--selftest`.

### The road from here — CF-02, and two decisions Sleven took 2026-08-08

Order: `docs/prompt-collector-roadmap-CF-02.md` and `claude/prompt-collector-roadmap-CF-02.md`.
Phase 0 is Sleven's to run (rebuild, then four acceptance checks, each with its failure shape
written down because two of the four are invisible from the window). Phase 1 is the gap between
"works here" and "works on a stranger's machine": screenshot masking as the hard blocker, an
honest supervisor, a visible sign of life, startup diagnostics, and a consent screen plus a
README written for someone who did not build it.

**DECISION — expansion order.** Sleven picked **wiring up the three parsers that already
compile and are connected to nothing** (`objectcontainer`, `spawn_location`,
`RequestLocationInventory`) plus the four transaction families found in the archive, ahead of
live log triggers, change detection, and component-state capture. Cheapest item available,
pure text, no new privacy surface, and it produces data no other tool has. C3's standing
objection is respected: `objectcontainer` fires on *boarding*, so it is used as a data event,
never as a capture trigger. The other three remain on the list in CF-02 §3, unstarted.

**DECISION — contributor identity, taken before the exe reaches a second machine.** Every
export carries a **random per-install ID**: generated once, stored locally, shown to the person
so it is not a secret, and **never derived from handle, machine name or hardware**. It
identifies a *source of observations*, not a human. The reason it could not wait: three people
reporting one price at one kiosk is either three independent confirmations or one person's log
counted three times, and **both dedup and no-dedup are wrong answers if the distinction was
never recorded.** A `schema_version` and `tool_version` go in the same header for the same
reason — cheap with one producer on this desk, unfixable once other people's exports exist in
the wild. Rejected: a self-typed nickname, because people would use their Star Citizen handle
and put a real identifier into the one dataset the whole pipeline strips handles out of.


---

## The ship loadout / fitting display — tasked to C3, 2026-08-08

Sleven asked for a way to display everything the game gives you about a fitted ship — the
guns and where they sit, the engine pack, the shield generator, total firepower, IR rating,
engine heat — taking inspiration from the community loadout tools, **"even if it's a temporary
method for now."** He also answered C3's open engineering-hologram question: *"If it means the
collector gets to grow, I am down for that."* Live component condition is now a stated
long-term goal, not a cost to avoid.

**Before tasking it, C1 verified the thing that decides the shape of the job.**
`data-layer/external-sources/scunpacked-data/snapshots/20260801T204744Z/ship-items.json` —
29 MB, 5,384 records — was read directly, not inferred. **Every stat Sleven named by name is
in that file.** Firepower is `Weapon.Damage`; IR is `Emission.Ir`; EM is `Emission.Em`; engine
heat is `Temperature` + `Thruster`; power draw is `ResourceNetwork`. Shield, QuantumDrive and
MainThruster carry full stat blocks. Worked example, read out of the file: Dominance-1
Scattergun — Sustained 396.5, AlphaTotal 504, Em.Maximum 248, Ir 0.

**So this is a display problem, not a data-acquisition problem.** No session should spend time
re-establishing what we hold.

**The one genuinely unverified thing is the join:** nobody has confirmed that `ships.json`
`Loadout[]` resolves cleanly against `ship-items.json`. That join is the whole build — clean
means a straightforward display job, 70% with a long tail means the tail *is* the work. C3 is
instructed to **report the match rate and classify the residue before proposing anything**,
using this project's own `ship_resolution.json` method, and to say plainly whether it joined
on a real identifier or on a name. Order: `docs/prompt-c3-ship-loadout-display.md`, filed by
the watcher 2026-08-07 20:54, and `claude/prompt-c3-ship-loadout-display.md` in the project.

**ANSWERED, same evening — `docs/FINDING_ship-loadout-display-research.md` (C3, 21:05).
The join is not the risk.** `Loadout[]` is a **nested tree, not a flat list** — items carry
their own child loadouts — and walking it across all 316 ships gives **36,584 fitted-component
instances**, separate from 21,175 empty port definitions describing what *could* mount there.
Raw match rate is **19,826/36,584 = 54.2%**, and **C3 was right not to report that number
alone.** Broken down: **100% matched, no exceptions**, for MainThruster, ManeuverThruster,
WeaponGun, Turret, WeaponDefensive, MissileLauncher, Missile, Shield, CargoGrid, FuelIntake,
FuelTank, Cooler, PowerPlant, Radar, SelfDestruct, Armor, LifeSupportGenerator and
FlightController. WeaponAttachment is 97%, and **every one of the 33 misses is the same fire
extinguisher magazine** — an FPS item correctly absent from a ship-item catalogue. The 0%
categories are Display, Misc, Seat, Door, and the controller nodes — **a category boundary, not
a join failure**, because CIG does not model doors and screens as statted purchasable items.
**Every category Sleven named by name is 100% joined on a real identifier.** Second thing worth
knowing: `ships.json` **already carries CIG-computed aggregates** for the stock loadout —
`ShieldsTotal`, `Power`, `Cooling`, `Emission` broken down by contributing component group, and
`Distortion.Pool` — so some of the maths that looked like it needed building is already done
upstream and only needs checking against our own totals.

**FOLLOW-UP, 2026-08-08 overnight — the aggregation formulas behind those precomputed totals
are now proven, code-verified, across all 316 ships.** `claude/FINDING_ship-aggregation-rules-proven-2026-08-08.md`
(C3): shields (top-2-generator redundancy cap, 267/267 exact on spaceships), DPS (the
`IsPilotSlaveable` outermost-lock rule, 275/275 exact against the real `PilotDps` ground
truth, with the `FixedWeapons.DpsTotal` vs `PilotDps` trap documented), and 10 of 11 power
categories at 100%. Cooling(Shields-mode) turned out to be Power's own numbers reused, not
independently derived — also 315/315 exact. WeaponGun's power residual, Cooling's
Quantum-mode, and Emission/Distortion remain open, reported honestly rather than guessed.

---

## `Game.log` IS A DATA SOURCE — added 2026-08-07 late evening, read before touching the collector

**`claude/FINDING_gamelog-is-a-data-source-4.9-vs-4.10.md` (C1, 2026-08-07).** Verified against two real logs off Sleven's machine — LIVE 4.9 and PTU 4.10.189.12935.

- **Star Citizen writes shop transactions to `Game.log` in plain text**, with price, shop name, kiosk id, item GUID, item name and quantity. This project holds **zero sell prices** and has listed the SELL tab as a dataset that does not exist. It exists, and it is being written to disk every time anyone buys or sells. **A large part of the collector's "reading" half is text parsing, not OCR.**
- **The line changed shape between 4.9 and 4.10 — this is the part that matters.** `CEntityComponentShopUIProvider::SendShopBuyRequest` became `CEntityComponentShoppingProvider::SendStandardItemBuyRequest`, and gained a `currencyType` field. One patch, two breaking changes to something CIG does not consider an API. **Parse on the `SShopBuyRequest` payload shape rather than the emitting class, read fields by name not position, and make the parser able to report that it has stopped matching** — a silent shop parser after a patch looks identical to a player who did not go shopping. Record the build alongside every parsed row and warn on an unseen build.
- **Also confirmed live in 4.10:** `RequestLocationInventory` resolves and names places (`Nyx_Levski`, `RR_JP_NyxCastra`); `VehicleListQuery` returned 17 entitlements, an **exact match** to the 17 ships in Sleven's own PTU photos; ship identity for own and foreign craft appears without targeting anything (`DRAK_Vulture_…`, plus `GLSN_Basher`, `GLSN_Shiv`, `ORIG_315p`, `MISC_Prospector`, `DRAK_Herald`, `RSI_Aurora_Mk2`, `AEGS_Avenger`); quantum routes log destination **and fuel estimate**, a dataset nobody has. Inventory Store/Equip logging is new in 4.10 and verbose, not yet assessed.
- **4.10 renders on Vulkan; 4.9 was DX11.1.** Every assumption in the capture path was formed against a DX11 client. **Re-verify capture on Vulkan before the next test session.**
- **Privacy surface got wider, not narrower.** Other players' handles sit in ordinary lines (`Containerstadt`, `ruf4s`, and `Solotov09` in the LIVE log) alongside Sleven's own `playerId`, shard id and session id. `Game.log` **does not go in the repo** — copy it to `Downloads`. Any parser emits only the fields it was built to emit: never a raw line, never a context field. `playerId` is stripped even though it is Sleven's own. Still a hard blocker on any crew build.
- **Three collector defects, confirmed, none fixed.** (1) The 14-minute silent death is `syscall.NewCallback` in `winapi.go:EnumTopWindows` — Go caps process-lifetime callbacks and it allocates one per call. (2) **The hotkey is dead and the earlier diagnosis was wrong** — `runtime.LockOSThread()` is already at `hotkey.go:122` with a correct comment; recommendation is to stop diagnosing and replace the mechanism with `GetAsyncKeyState` polling. (3) No visible sign of life; Sleven has no speakers, so audio is not an option and the "no silent operation" rule is unmet.
- **Why the live test nearly produced nothing:** the crash resets the interval timer, so a 10-minute interval inside a 14-minute lifetime yields **exactly one capture per cycle at an unpredictable moment**. Sleven stood at a kiosk at 16:45 and 16:55 and got nothing. **Drop the interval to 60 seconds once the crash is fixed.** He called this before the test, and the advice to freeze the capture path was wrong — it protected a path that was already broken.

**This supersedes the sequencing argument in `claude/HANDOFF-C3-expanding-what-the-collector-captures.md`.** Visual ship recognition is not cancelled, it is narrowed: the log covers ships the client already knows about, so recognition is for the ones it does not — derelicts, distant hulls, anything the player has not interacted with.

---

## STANDING PROJECT FOCUS, declared by Sleven 2026-08-07 evening — read this before picking a task

**The collector and the ship-model/hardpoint/skin work are now one combined focus, not two separate threads.** Sleven's own framing: better ship models feed the collector's ship-recognition training, and the collector is a way to keep gathering the information the project runs on — "it's all interconnected... back and forth." Sessions picking up work should treat these as the priority set over other queued work unless Sleven says otherwise:

- Getting WO-UI-01 (the collector-as-a-program rebuild) built and working — in front of Code now.
- Fixing the two live-test bugs (hotkey dead in `--auto` mode; auto log gives no "still alive" signal) and the privacy blocker (player/session/shard IDs not stripped) before any crew build.
- The ship-model question: `claude/FINDING_ship-models-no-texture-data-verified.md` (2026-08-07) — verified directly on disk, not assumed: **all 235 `.glb` models currently have zero texture/skin data**, just bare gray geometry (though it is UV-mapped, so a texture could be added later without remodeling). Also found in passing: 4 of the 5 Aurora trim files are byte-identical duplicates — no visual difference between those trims right now. Hardpoints still require manual Blender placement either way (already the plan, doesn't need file-extracted hardpoints). Skins need a texture source, which is a rights question, not a technical one — see that finding's rights table.
- ~~The one door that could resolve both the hardpoint and skin question cleanly: CIG's official Fan Kit reportedly includes 3D models, but nobody has opened it.~~ **CLOSED, 2026-08-08 — see the Fan Kit section at the top of this document.** It's open, it's read, and it does not resolve either question: 14 ships, bare geometry, no textures, same ceiling as the existing `.glb` set.
- Expanding what the collector captures (`claude/HANDOFF-C3-expanding-what-the-collector-captures.md`) and the visual ship-recognition plan both lean on whatever the ship-model answer turns out to be, which is why these are one focus, not two. **Both are now further constrained by the `Game.log` finding at the top of this document.**

---

## READ NEXT — 2026-08-07 has a full day of new work this doc does not narrate

This file was not rewritten today; a large amount happened on 2026-08-07 (item-taxonomy rulings, mission/location data breakdown, and more — see the project doc list). Before trusting anything below as current, read `claude/HANDOFF-all-sessions-2026-08-07.md` and the newest `claude/session-handoff-*.md`/`claude/session-log.md` entries first, same as the reading-order rule below already says. Two pieces of 2026-08-07 work worth knowing about specifically, since they're new derived data in the repo, not just docs:

- **Mission templates and full location hierarchy — done, in the repo.** `docs/FINDING_missions-and-locations-full-breakdown.md` (C3, 2026-08-07) resolves the starmap down to system → planet/moon → outpost/city for 2,066 entities (`data-layer/derived/location-gazetteer/`), joins all 5,107 contracts to system and, where possible, planet/moon (`data-layer/derived/contracts-by-system/contracts_full.json`, supersedes the same-day `contracts_by_system.json`), and counts real mission templates: 106 (GeneratorClass family, exact) + ~700-1,051 (MissionBrokerEntry family, estimated — DebugName has no clean template ID, see the finding's methodology and open judgment calls before treating that half as settled). Also lands a 74-faction roster (`data-layer/derived/mission-templates/factions.json`) that was sitting unused in the game files. Nothing here is wired into the site yet — this is data-layer work, not a feature.
- **Keybind page — 238 plain-language "what does this key do" descriptions drafted, and now wired in and deployed.** `docs/WORKORDER_keybind-descriptions-wire-in.md` (C3, 2026-08-07) documents that the keybind page is further along than the 2026-08-02/05 planning docs show (six-mode split, device-panel lag/hat fixes already shipped in commits `3254dea` through `232cac2`), and that the one real gap left against Sleven's instruction ("show what the key will do in game and be helpful") was description text — `build_keybind_modes.py` had no `desc` handling at all. 238 descriptions live at `data-layer/processed/keybind_descriptions_draft.json` + `.MANIFEST.json`, covering every keyboard-bound labeled action without a real CIG description. One real bug caught before shipping: `v_yaw_left`/`v_yaw_right` mean different things under `spaceship_movement` vs `vehicle_driver` — description data must join on `(action, map)`, never `action` alone. A follow-up accuracy pass (`docs/FINDING_keybind-descriptions-verification-pass.md`) cross-checked the drafts against CIG's own site (nothing usable there — video-first pages) and a currently-maintained fan reference (scfocus.org); all 5 originally-low-confidence rows moved up, 2 more moved medium→high, nothing moved down. Final: 171 high / 67 medium / 0 low, `source: cc_draft` throughout. **Update, 2026-08-07 late: the wire-in is done and deployed (commit `fe62c09`).** `build_keybind_modes.py` now has a `real_cig_desc()` gate that rejects a "description" which merely repeats the label — which is what 122 of the 210 existing `desc` values in `keybinds_site.json` turned out to be. **5 rows are flagged for Sleven's eye and his review pass has not happened.**

- **Device panel D3/D4/D5 and the device-facts research — verified against the actual repo, not the planning docs.** `docs/FINDING_device-panel-D3-D4-D5-and-device-facts-status.md` (C3, 2026-08-07). D1 (lag) and D2 (hats) are fully done and match their acceptance criteria exactly. D3 (unify a control's axis + button into one data model) is only partially done — the crash/double-count risk is defused but the actual `control:{id,label,x,y,inputs:[]}` model was never built. D4 (layout) is mostly done — both devices side by side works; the "0 tiles at rest" default doesn't (a toggle exists, defaults off, 40 tiles show by default); the add-on-device toggle for pedals/throttle quadrants is missing entirely. **D5 (guided mapping wizard) is fully unbuilt** — no wizard, no checklist, nothing. **`claude/workorder-device-facts.md`'s vendor stick-geometry research has not been started at all** — `data-layer/raw/devices/` doesn't exist in the repo.
  - **Update, 2026-08-07 — CLOSED, all 7 devices done.** `claude/workorder-device-facts.md` is complete. `data-layer/raw/devices/device_facts.json` + `device_facts_findings.md` are in the repo (C3, same day). None of the 7 are fully solved — this is sourced-fact research, not finished data — but every device has a real control inventory and an honest confidence rating. VKB Gladiator NXT EVO (Sleven's own hardware): solid USB VID/PID and 13-control inventory, zero sourced button indices (VKB documents by physical label, not number — numbering shifts with firmware mode). VIRPIL ALPHA Prime: 9 of 17 buttons community-sourced; CDT-AEROMAX: 0 of 9. Thrustmaster T.16000M: best USB ID in the set, only 1 of 16 buttons indexed (the trigger), hat confirmed as a real single HID hat-switch. Thrustmaster SOL-R 2 (a HOSAS pair, not one stick): 0 button indices. Turtle Beach VelocityOne Flightstick II: still pre-order only, ships 2026-09-21 — its nulls are a calendar fact, not a research gap, re-run after ship date. WinWing/WINCTRL Ursa Minor Fighter/Space: best partial button map (10 of 44), but the device variant itself is an unconfirmed guess and one PID is claimed by two grips. Full writeup: `claude/FINDING_device-facts-all-7-devices-2026-08-07.md`. Build order for Code confirmed delivered — see the `inbox/` correction below — at `docs/workorder-device-facts-buildout.md`: covers building D3's real `control:{id,label,x,y,inputs:[]}` model, closing D4's two remaining gaps (hide-unused default, add-on-device toggle), and building D5's guided wizard from scratch.
- **The first-time flight-stick owner tooling — two new datasets on disk, not yet committed.** Built 2026-08-07 late, after CIC's competitor research came back. `data-layer/processed/keybind_troubleshooting.json` (v2) is a **branching** yes/no diagnostic — 17 nodes: 4 questions each carrying a `how_to_check`, 1 symptom-choice node with 8 options, 12 fixes. Every fix routes back to a retest node so nobody is left at a dead end. Validated on Sleven's machine: 17/17 reachable from `start`, PASS, **and the negative control — a deliberately planted broken link — was detected**, per hard rule 12. `data-layer/processed/vendor_support.json` is the "we cannot help you, here are the people who built your stick" hand-off: 5 vendors matched **on USB vendor ID only, never product ID**, each with a `known_gotcha`. Turtle Beach's `usb_vid` is deliberately `null` because the Flightstick II has not shipped, and guessing an ID to make the join work would route someone to the wrong manufacturer's support page. The HELP drawer that surfaces this is built and shipped (commit `ba25d9c`) with genuine content reflow measured at 1874px → 1454px — a pull-out that shrinks the page, not an overlay — and 38 tests including a negative control. **Still open: Sleven's review of the 4 medium-confidence entries and the drawer wording, and `keybinds.src.html` is a second standalone copy of the keybind page that did not get the drawer.**
- **7,728-item taxonomy — three rulings still open, waiting on Sleven.** `claude/workorder-catalog-01-fullset-junkdrawer-manufacturer-commodities.md` has the questions (Full Set bundling, junk-drawer bucket destinations, which of three commodity counts is authoritative). The manufacturer-inference piece needs no further sign-off and is ready for C1 to build. **Update, 2026-08-07 evening (C3):** the 366-item junk-drawer classification pass that was stuck in `_needs_review/` (JSON array, watcher needs an object) has been moved to its proper home at `data-layer/derived/junk-drawer-taxonomy/` — no longer stuck, but the underlying ruling is still open.
- **The collector became a real thing on 2026-08-07, and everything about it is newer than this document.** Read `claude/FINDINGS-live-collector-test-2026-08-07.md` first — the ten-minute in-game test finally ran, answered all six of its questions, and found two defects no synthetic test could see (the hotkey was never registered in `--auto` mode, the one mode people run; and the auto log only wrote on capture, so a quiet collector and a dead one looked identical). It also produced data that exists in no game file: live mission-board payouts with expiry timers, refuelling rates, three vendors' item prices, and proof that a purchase can be derived from a frame pair — wallet delta 1,626 equals the helmet's listed price, to the credit. `claude/workorder-collector-as-a-program.md` (WO-UI-01, **rev 2, CONSOLIDATED — supersedes the chat spec and both addenda**) is the job now in front of Code: the window becomes the program, it auto-detects LIVE/PTU/EPTU, it starts and stops with the game, and one button packages the captures for sending. **Hard blocker on any crew build:** the live test proved player handle, shard id, session id and other players' names all appear in ordinary frames and none are stripped, against the standing rule that they are stripped before the file exists. Nothing has left the machine, so nothing has gone wrong yet. **This is now a standing project focus, not just a queued item — see the top of this document.** **And see the `Game.log` finding at the very top: a second PTU session the same evening changed what the collector should be built to do.**
- **Expanding what the collector captures is an open design conversation, owned by C3.** `claude/HANDOFF-C3-expanding-what-the-collector-captures.md` (C1, 2026-08-07) is the draft it starts from: three parsers already in `gamelog.go` that compile and are wired to nothing (`objectcontainer` — a ship *is* an object container in SC, so boarding one is free ship identity from the game itself; `spawn_location`; `RequestLocationInventory`); pixel change-detection as the cheap fix for the standing-still blind spot the interval trigger only half covers; and visual ship identification, wanted because targeting notifies the other player and reads as hostile, and derelicts return a number instead of a name. **The tractability argument is the 3D models the project already owns** — they render labelled synthetic training images, normally the expensive half of object detection, and the flattened models written off for hardpoint work are perfectly adequate for silhouettes. **Nothing in that document is authorised to be built**, and its sequencing claim (log triggers first, because they generate recognition's validation set) is explicitly flagged as its weakest part. C3 adds to that file; it does not fork it. **C3's §11 disagreement stands and is worth reading: `objectcontainer` fires on *boarding*, so its frames show cockpit interiors rather than exterior hulls, and most boardings are the player's own ship.** **See `claude/RULING_ship-models-provenance-and-proceed.md` and `claude/FINDING_ship-models-no-texture-data-verified.md` for where the model question stands, and `claude/FINDING_gamelog-is-a-data-source-4.9-vs-4.10.md` for what supersedes its sequencing.**

---

## Reading order for a new session

1. **This document.**
2. `RECOVERY.md` (repo root) — what lives off the machine, and how to rebuild what does not.
3. `claude/finding-description-rights-correction.md` — **read before doing anything with item descriptions.**
4. `claude/session-log.md` and the newest `docs/handoff_archive/` entries for what happened last.
5. Specialised docs as needed.

Older docs are history. Where they disagree with this one, this one wins.

---

## The project

Free, non-commercial fan-made Star Citizen reference. *"Know where to buy, before you fly."*

- **Live:** citizencompass.netlify.app — v0.3.9, 254 ships, hand-deployed
- **Testing:** citizencompasstesting.citizencompass-contact.workers.dev — Cloudflare, one-command deploy
- **Repo:** github.com/Smeezee/citizen-compass — pushed to `origin/main` at `ba25d9c`, 2026-08-07
- **Local:** `C:\Users\david\citizen-compass`
- Licence CC BY-NC 4.0, credit "Built by Sleven"

---

## Build C is UNBLOCKED — the keybind blocker was a wrong tool, not a hard problem

**Added 2026-08-05. Order: `claude/workorder-keybind-extraction.md` (WO-KB-01).**

Build C has been parked on `defaultProfile.xml` being "inside a custom archive format Python's `zipfile` rejects." That framing was wrong in the part that mattered. `Data.p4k` is a Zip with CIG's additions — partial encryption plus ZSTD alongside STORE and DEFLATE. `zipfile` cannot read that and never will, but **`dolkensp/unp4k` has read it for years and is current: v4.0.87, 23 May 2026, ZSTD stated in its own README.** Nothing needs writing to open the archive. It is a download and one command.

**It does not extract 154 GB.** The filter is a case-insensitive substring match on each entry's full path, read from the source — `defaultprofile.` pulls exactly one file.

**Three traps, all confirmed from source, all in the order:**

- A filter ending in `xml` triggers a `.dcb` special case and drags out hundreds of megabytes of DataForge. Ending the filter at the dot avoids it.
- Output lands relative to the shell's working directory, not next to the exe.
- **`unp4k` does not convert CryXML, and `defaultProfile.xml` is CryXML.** The extracted file is named `.xml` and is not text. `unforge.exe` converts it. A binary file handed to an XML parser does not crash — it yields nothing, and "0 keybinds" reads like a finding rather than a mistake.

**The schema is confirmed, not guessed**, taken from the struct tags of a working parser of this exact file:

```xml
<actionmap name="…" version="…" UILabel="@ui_CG…" UICategory="@ui_CC…">
  <action name="…" keyboard="…" UILabel="@ui_CI…" UIDescription="@ui_CI…Desc" activationMode="…"/>
</actionmap>
```

That is the missing join, and it matches what is already on disk exactly: the action's `UILabel` is one of the 910 `ui_CI*` keys, `UICategory` is one of the 53 `ui_CC*` modes, the actionmap's `UILabel` is one of the 42 `ui_CG*` groups. Nothing has to be inferred.

**`parse_defaultprofile.py` is written and tested — 19 of 19 checks pass, 9 of them against input it must reject**, including the CryXML-binary case and a wrong-localisation-file gate that fails the run rather than emitting 910 blank labels. It captures every input device, not just the keyboard, because `kb1_mouse4` is real — mouse buttons hide under the keyboard prefix. Unknown attributes are kept verbatim and reported by name, so a CIG schema change surfaces as a line of output instead of as missing data.

**The payoff:** `keybinds.src.html` ships 105 keys transcribed by eye from screenshots, unverified, carrying orange `?` markers. The parser's crosscheck sorts them into agree / disagree / not-in-the-file. **Keep the transcribed set afterwards** — the disagreement count is the only measurement we will get of how accurate reading a screenshot actually is, and this project makes that trade often.

**Still needs the machine.** The archive is at `StarCitizen\HOTFIX\Data.p4k`, 154 GB, on Sleven's disk. Everything that could be done without it is done.

---

## Phase 1 is COMPLETE

Commit `afe00dc`. Five sources collected and gated, two correctly ruled out. **Nothing promoted to the database** — Stage 1 is collect and seal.

Source 6 (UEX) landed as `20260801T235530Z`: 114 files, 12.4 MB, **23,734 item prices, 823 terminals, 288 vehicle prices, 7,728 items of which 5,566 carry a UUID.** `data_tier: C` recorded with UEX's own ±20%/±100% tolerance. All five gates in order.

**The catch that made it real:** Claude Code was told Part B had stopped. It checked anyway, found the process alive with 39 of 100 categories unfetched, and waited. Gating then would have sealed an incomplete snapshot and passed every check. **A status brief is not evidence** — carried as a standing rule.

---

## Path C is COMPLETE — the auditor layer runs itself

The checker layer existed at ~60% and had been producing findings nobody read: 874 stranded in a fallback log because `run_checks.py` passed `db_conn=None` unconditionally. The fallback was the only path, permanently, even with a working database.

Now: **890 observations collapsed to 274 findings, 27 open DEFECTs**, on a schedule, with a lifecycle.

**The lifecycle rules are the load-bearing part.** A finding is CLOSED only by a run that looked and did not find it. A checker that errored or was skipped sends its findings to UNKNOWN, never CLOSED — *a checker that stopped running must never look like a problem that went away.*

New checkers: `snapshot_integrity`, `cross_source_disagreement`, `uex_join_health`, `checker_health`, `missing_encoding`, `schema_ownership`.

---

## Ship identity is RESOLVED — `data-layer/ship_resolution.json`

Method, on Sleven's call: anchor on the 254 live ships as the trusted set, match outward into the 316 game files, **classify the residue rather than discard it.**

```
254   live ships
221   matched to a game file
  0   ambiguous
 33   no game file — every one already flagged pledge_only
 89   game files not on the site
```

**Zero purchasable ships unaccounted for.** The 33 are corroboration, not a gap: the site calls them concept ships and the game files agree by not containing them.

Four that looked like gaps were name mismatches: Ares Inferno/Ion are `crus_starfighter_*`, Nova Tank is `tmbl_nova`, and 600i Explorer is the base `orig_600i`.

**Lesson worth keeping:** no automated name match will ever be complete. "Ares Inferno" and "Starfighter Inferno" share one word. The residue always needs someone who knows the domain.

---

## The 89 leftovers are special editions, not unknown ships

73 edition/base pairs compared field by field:

```
53   differ ONLY in fitted components — 7 to 11 of them
18   mechanically identical to the base
```

**They are factory loadouts, not variants.** A "Wikelo War Special" is the same hull with military parts fitted. The 18 identical ones are cosmetic — every Best In Show edition, the ATLS colours, the CitizenCon Mustang.

Only **one** genuinely distinct ship in eighty-nine: the Anvil F8A Lightning.

### And the site's model cannot express any of it

Wikelo has three real terminals in UEX and **zero ship prices at any of them.** Teach's Ship Shop has 38. Paints attach to ships mechanically via `required_tags` and carry `event_source` — Concierge, Subscriber, IAE, Luminalia, Best In Show.

The dealer columns answer one question: *which shop sells this for aUEC.* They cannot describe a ship traded at Wikelo, a livery from a subscription, or a loadout that arrives fitted.

**Recommendation on record** (`docs/finding-editions-paints-acquisition.md`): add an acquisition **field** with six routes — shop, pledge, trade, award, subscription, factory. The matrix becomes a view over `route = shop` and does not change. **Settle it before Build A generates thousands of pages with "where to buy" baked into the template.**

---

## Testing site — deploys in one command, on Cloudflare

```
powershell -ExecutionPolicy Bypass -File .\scripts\deploy_testing.ps1
```

Netlify preview is kept deliberately as a milestone build, updated a few times a month. **Netlify deploys are currently credit-blocked**, so it sits on v0.3.9 until that clears.

Cloudflare's free tier does not meter bandwidth, which for 349 MB of ship models is the real reason for the move — the credit block was only the trigger.

**The testing site is a Cloudflare Worker with static assets, NOT Pages.** `wrangler pages deploy` publishes to a second, different URL while reporting success — a silent-failure shape this project has now seen five times. Use the deploy script.

**The password gate does not cover static assets.** The HTML asks for a password ("Private preview"); on 2026-08-07 `models/100i.glb` was fetched directly and returned binary. Anything under `_deploy/` that is not HTML is on the open internet. Sleven is aware, and the build-then-ask strategy in `claude/RULING_ship-models-provenance-and-proceed.md` was set with that known.

**Tab layout settled:** DISPLAY and FEEDBACK stay on the right edge as page tools. MANUFACTURERS, KEYBINDS and FIND moved to a left dock that is **vertically centred rather than stacked downward**, because the old `44% + Npx` scheme put the fifth tab at 1045px on a 1080px viewport. The LOADOUT tab is removed by decision — that entry point belongs on the ship page.

**`testing/_src/` is the source of truth** and now lives on disk; until 2026-08-02 it existed only inside an ephemeral cloud session. `build_deploy.py` is repo-relative with vendored three.js, byte-reproducible across platforms, and **proven to reproduce the deployed artifact exactly**. Note that `build_deploy.py` substitutes its own copies of some blocks — **patching only the source layer can silently do nothing**, which is why `testing/_src/inject_engine.py` now makes `device_engine.js` the single writer of the device panel and hard-fails inside the build rather than warning.

---

## Crafting data — WO-1 and WO-2 complete

- `item_descriptions.json` — 5,344 matched on UUID, zero name-based joins
- `blueprint_index.json` — 1,597 rows, split page-per-file

**The split matters:** the combined index was 10.9 MB, two-thirds of it source lists. Page p99 went from 63,706 bytes to 3,129 — a 20× reduction — by moving `sources[]` behind the disclosure WO-3 already specified. **Rows over 20 KB: 74 → 0.**

Every one of the six `source_kind` values now renders a summary block; 48 previously showed a disclosure with nothing above it.

---

## STOP — item descriptions may not be publishable

`claude/finding-description-rights-correction.md`, filed 2026-08-02 17:11.

C2 retracted its own position that wiring in the 5,344 CIG-written descriptions was the highest-value work available, **because nobody checked whether we are allowed to publish them.**

- The wiki's claim that CIG granted reuse of Comm-Link text cites a **legacy RSI forum comment whose URL is now dead.**
- RSI ToS §XIII.D permits reproducing *images, graphics, artwork, trademarks and logos* designated for fansite use. **Text is not in that list.**

**No live exposure** — nothing deployed carries CIG's descriptions. But WO-1's output is committed and **must not ship until this is settled.** Rule 8 puts Fan Kit, trademark and legal text solely with Sleven.

**Note for WO-KB-01:** the 130 CIG-written keybind descriptions in `labels.json` are the same class of material and fall under the same open question. The default *bindings* are facts about how the game is configured and are not affected; the description text is. **Ship the keys, hold CIG's descriptions until the rights question is settled.** The 238 descriptions that did ship are Citizen Compass's own text, written from scratch — that is why the `real_cig_desc()` gate exists, and why it rejects a "description" that is only the label repeated.

---

## Architecture decisions taken 2026-08-02

**Static JSON, not FastAPI.** Page-per-file, not a bundled index. The reason is the site's zero-runtime-dependency property, not the file count — the count would have flipped on whether "items" meant 7,728 priced or 21,849 game files. Budget: ~11,225 served against a 20,000 Cloudflare cap.

**One writer per artifact** — now hard rule 14, enforced by construction rather than by everyone remembering. This project hit that defect three times: two handoff watchers, a near-second scheduled task, and three sessions on one layer file. **It happened a fourth time on 2026-08-07**, when C1 wrote a base spec and then two addenda that contradicted it and never revised the base; Code caught it, and the consolidated rev 2 is the fix. **A fifth is live and unresolved:** `keybinds.src.html` is a second standalone copy of the keybind page and did not receive the HELP drawer. Delete it or make it a generated artifact — do not maintain both by hand.

**Every file open states its encoding** — hard rule 15, machine-enforced by the `missing_encoding` checker. Four cp1252 incidents on real ship names preceded it; `tok.yāi` is a shipping product, not an edge case.

**Schema authority split:** `ship_registry` declared in `models.py`; the three `pipeline_*` tables excluded via `include_object` with schema-init owning their DDL. A `schema_ownership` checker asserts every table is claimed by exactly one authority. Closed a live hazard where `alembic revision --autogenerate` would have dropped **3,751 rows** including the findings table.

---

## Session roles

- **C1** — Cowork session that constructs orders and is the only Cowork session authorized to write to the repository.
- **C2** — earlier Cowork research session (closed 2026-08-07); its handoff was inherited by C3.
- **C3** — Cowork research session, 2026-08-07 onward: reads/verifies source data, produces findings and work orders. Does not do legal/rights analysis (Sleven's alone) and does not build/test code (Code's job). Has permission (granted 2026-08-07) to write derived data and doc findings/work-orders directly into `inbox/` and `data-layer/derived/` — not git operations, not the database, not Code's build/test tooling.
- **CIC** — Claude in Chrome research session. Reads the open web: competitor tools, vendor documentation, community reports. **Its output is a claim until someone verifies it locally.** On 2026-08-07 it reported the `.glb` generator tag as `THREE.GLTFExporter` — true upstream, false on our copies, because the project's own compression pass overwrote it.
- **Code** — Claude Code. Executes what C1 gives it. **C1 writes prompts for Code, not work orders** — Sleven's own correction, 2026-08-07.

**A work order that exists in the claude.ai project but not in the repo has not been delivered.** This cost the project real time on 2026-08-07: WO-UI-01 was filed to the project and sent as a chat file, and Code — which reads the repo — never received it. Anything Code is expected to act on goes into `inbox/`.

**Correction, 2026-08-07 evening (C3):** an earlier version of this doc, written a short time before this one, claimed `inbox/` was "broken — confirmed self-clearing." **That was wrong, and the mistake was C3 not knowing the pipeline existed, not a real bug.** `inbox/` has a Go watcher (`watcher-go/`, logs at `logs/inbox_watcher.log`) that does exactly what it's supposed to: picks up anything dropped at the top level, classifies it, and files it — a generic doc goes to `docs/`, an `update-*`/`HANDOFF_*` doc gets archived to `docs/handoff_archive/` and folded into `LATEST_HANDOFF.md`'s narrative, anything unrecognized goes to `_needs_review/` — then regenerates `LATEST_HANDOFF.md`. Two protected subfolders (`Citizen Compass AI Brain`, `citizen-compass-testing-ground`) are explicitly excluded from auto-processing, and those were the only things C3 found still sitting in `inbox/` when checking — which is why C3 wrongly concluded everything else had vanished. Confirmed via the watcher log: both `workorder-device-facts-buildout.md` and `workorder-station-directory-pullout.md` were picked up within seconds of being dropped and correctly filed to `docs/`. **The lesson generalises: C3 checked git for the file rather than running `ls inbox/`, and dropped the same file three times.** Note for future sessions: a plain "(doc)" filing goes to `docs/` but does **not** automatically get narrated into `LATEST_HANDOFF.md`'s "RECENT UPDATES" section — only `update-*`/`HANDOFF_*`-style docs trigger that. C1 cleaned the duplicate-collision copies into `_to_delete/watcher_duplicate_workorders_20260807/`. **Net effect: nothing was lost, nothing is currently broken. Read `logs/inbox_watcher.log` before ever concluding a drop failed.**

**Note, 2026-08-07 evening, on derived data that doesn't fit the watcher's format:** the watcher's classifier needs a JSON object at the top level; a JSON array gets shunted to `_needs_review/` even when the data itself is fine. When that happens with something that's clearly derived analysis output (not a doc for the watcher to route), the fix is to write it directly to `data-layer/derived/<topic>/` with a `MANIFEST.json` alongside it, matching the pattern already used by `location-gazetteer`, `mission-templates`, etc. — bypass the watcher rather than reshape the data to suit it.

**Note, 2026-08-07, on running git through the device mount:** the mount cannot unlink, so an ordinary `git status` can strand a `.git/index.lock` that blocks every later git command. C1 did exactly this. Use `git --no-optional-locks` for read-only git commands over the mount, and if a lock is already stranded, `del` it from a real shell on the machine.

---

## Open, and only Sleven can do these

**HOW TO READ THIS LIST — added 2026-08-15, and it is the point of the list.**

Every entry carries a **state**, the date it was **raised**, and the date it was
**last confirmed**. Three states only:

    OPEN      re-checked on the "confirmed" date and still outstanding
    UNKNOWN   nobody has re-checked it since it was raised. NOT the same as open.
    CLOSED    ruled or done, with the ruling named

**UNKNOWN is the important one, and most of this list is UNKNOWN.** An item nobody
has looked at in a week is not a fact about today — it is a note from the past.
**Do not present an UNKNOWN item to Sleven as an open job.** Re-check it first, or
say plainly that it has not been confirmed since the date shown.

**This is the same lifecycle rule the checker layer already uses**, adopted after 874
findings sat in a fallback log looking green: *a finding is CLOSED only by a run that
looked and did not find it; a check that was skipped goes to UNKNOWN, never CLOSED.*
**This list is a findings list that had no lifecycle attached, and it caused the same
loop twice in 24 hours** — the rights question and the credentials, both re-raised at
Sleven because this list still said they were open. See
`docs/RULING_rights-questions-are-settled-2026-08-14.md` and
`docs/RULING_credentials-are-rotated-2026-08-15.md`.

**When Sleven closes something in conversation, it gets written here the same day.**
A closing that only exists in a chat transcript will be lost, and the next session
will ask him again.

---

**1. Credentials — UEX token, PostgreSQL password, Cloudflare token**

    state           CLOSED
    raised          2026-08-07
    last confirmed  2026-08-15
    ruling          docs/RULING_credentials-are-rotated-2026-08-15.md

All three rotated by Sleven. **Seven older documents in `docs/` still describe them
as exposed — those are stale and are not evidence of an open item.** Do not re-raise.

**2. Description rights / CIG rights as a whole**

    state           CLOSED
    raised          2026-07-28
    last confirmed  2026-08-14
    ruling          docs/RULING_rights-questions-are-settled-2026-08-14.md

Compliance rests on the existing practice — everything goes to the test site and is
verified first — and the site URL has not changed. The 5,344 CIG-written item
descriptions are separate and ALSO not an open question: ship the keys and the facts,
hold CIG's prose (`claude/finding-description-rights-correction.md`). **Do not
re-raise either as a question, a caveat, or a flag.**

**3. Offsite backup**

    state           UNKNOWN
    raised          2026-08-07
    last confirmed  2026-08-07 - never re-checked
    what would      confirm whether a copy now lives somewhere other than the
    close it        trailer

The backup itself is fixed and verified as of 2026-08-07: repointed to the My Book on
D: with E: as a second mirror, per-file verification 951/951 sc-ships and
58,257/58,257 external-sources on both, database restore-verified at 232 ships in =
232 out. **Both drives are in the same place as the machine**, so this is about
geography, not integrity. Nobody has asked since.

**4. Three item-taxonomy rulings**

    state           UNKNOWN
    raised          2026-08-07
    last confirmed  2026-08-07 - never re-checked
    detail          claude/workorder-catalog-01-fullset-junkdrawer-manufacturer-commodities.md

**5. Five mission-template DebugName tokens — game-knowledge call**

    state           UNKNOWN
    raised          2026-08-07
    last confirmed  2026-08-07 - never re-checked
    detail          claude/FINDING_missions-and-locations-full-breakdown.md, section 3

Tokens inside Star Citizen's internal mission names: `Group`, `Inhabited`,
`NoNonHostiles`, `CrossStanton`, `DC`. **Not keybind-related** — mislabeled as
"keybind tokens" in versions of this document before 2026-08-07. The call: is each
one cosmetic flavour (strip it, same template) or a real mechanical difference (keep
it, distinct template)? Moves the Family B estimate by roughly 350 templates — 700
against 1,051.

**6. Review the flagged rows**

    state           UNKNOWN
    raised          2026-08-07
    last confirmed  2026-08-07 - never re-checked

The 5 keybind descriptions the wire-in flagged, the HELP drawer wording, and the 4
medium-confidence entries in `keybind_troubleshooting.json`.

**7. Paste the Worker URL into the collector settings**

    state           CLOSED
    raised          2026-08-15
    last confirmed  2026-08-16
    closed by       nobody has to paste anything, ever

**Superseded by the zero-config destination.** The Worker is deployed, the feed carries
`send_url` and `send_key`, and two real uploads from a second machine are in the bucket.
Nobody types an address or a key on any machine, ever. Local values in
`collector-settings.txt` still win when present, as a deliberate escape hatch.

---

**CLOSED, kept so nobody reopens them:**

- ~~Open CIG's Fan Kit and check what its 3D models contain~~ **CLOSED 2026-08-08.**
  It was already on the machine. 14 ships, bare geometry, does not resolve the
  hardpoint/skin problem — but the logos and the exact image-marking requirements are
  real and usable. `claude/FINDING_fankit-inventory-2026-08-08.md`.
- ~~The OFL fonts blocked on a licensing go-ahead~~ **CLOSED — verified on disk
  2026-08-15.** All four `.woff2` files plus `OFL.txt` are in `testing/_deploy/fonts/`.
- ~~The 24 shared 3D models~~ **CLOSED 2026-08-14 by Sleven's ruling.** A shared hull
  is correct unless the ships differ in external shape.
  `docs/DECISION_shared-hulls-are-fine-unless-the-shape-differs-2026-08-14.md`.

**Settled, recorded here so nobody reopens it:** ship-model provenance. `claude/RULING_ship-models-provenance-and-proceed.md` — proceed on a fan-made basis, approach CIG for permission before any public launch. Rule 8. Do not relitigate.

---

## Queued, specced, nothing started

`claude/workorder-keybind-extraction.md` (**WO-KB-01 — ready to run the moment the machine is up; two commands and a tested parser**) · `docs/order-front-end-build.md` · `docs/workorder-craft-01.md` + addendum · `docs/workorder-loadout-real-data.md` · `docs/workorder-image-provenance-and-renders.md` · `docs/workorder-patch-link-resolver.md` · `docs/design-daily-handout.md` · rule 14 enforcement proposal · `claude/workorder-catalog-01-fullset-junkdrawer-manufacturer-commodities.md` (waiting on Sleven's three rulings) · `docs/WORKORDER_ui-01-collector-as-a-program.md` (**in front of Code now — standing project focus**) · `claude/workorder-device-facts.md` (**CLOSED 2026-08-07**) · `docs/workorder-station-directory-pullout.md` (needs C1's attention specifically for the capture-mechanism overlap with WO-UI-01).

**Not yet written, and now the highest-priority collector job:** the three collector fixes — the `syscall.NewCallback` crash, the hotkey replaced with `GetAsyncKeyState` polling, and a visual activity indicator — plus dropping the capture interval to 60 seconds, plus a shop-transaction log parser built to the rules in `claude/FINDING_gamelog-is-a-data-source-4.9-vs-4.10.md` §2, plus wiring the three parsers that already compile and are connected to nothing.

**Also open, smaller:** the two new JSON datasets (`keybind_troubleshooting.json`, `vendor_support.json`) are on disk and **still untracked**. The `NotForRelease`/`WorkInProgress` filter — the live site may currently be advertising unreleased content. The path-join bug that produced a malformed `data-layerrawhardpoints/` folder (185 MB `ship_specs.json`, 295 ships — **do not bin it**). Hardpoint extraction scaled from 1 ship to 295. The 890's 582 materials collapsed while keeping the node tree. Four orphaned scratch databases to drop. The render pipeline for hull training data is authorised by the ruling and not started. Burst mode and ship-tagging for a PTU photography session, deferred until the collector fixes land.

---

## One caution for the next session

**Do not `git add -A` on this repo until the line endings are settled.** 50 tracked files show as modified with 191,317 insertions and 191,317 deletions — pure CRLF/LF churn, verified byte-identical after stripping CR. `releases/latest.html`, `static/preview.html` and the `SHA256SUMS` files are among them. The committed versions are correct; the working-tree noise is harmless unless someone commits it.

**As of 2026-08-07 late evening, everything is pushed.** C3's untracked work went in as `cce3d3e`, the keybind descriptions as `fe62c09`, the HELP drawer as `ba25d9c`, and `origin/main` is at `ba25d9c`. The six previously-unpushed commits (`366dba9, 1008fc8, c0c6fff, f62b6fb, 73c4a4d, a6681be`) are included in that. **Nothing is pushed without Sleven's explicit go-ahead.**

---

## THE ROADMAP WATCHER — 2026-08-14. Approved, specced, not built.

**Point C1 at one file: `docs/WORKORDER_roadmap-watcher-2026-08-14.md`.** It is
complete and standalone. It supersedes `WORKORDER_rework-tripwire-build-spec-2026-08-14.md`
and both copies of `AMENDS_tripwire-release-view-only-2026-08-14.md`, which now
contain nothing but a redirect.

**What it is for:** CIC established three independent ways that CIG has said nothing
about a Constellation rework. That answer expires. This watches CIG's roadmap so
"nothing yet" gets re-checked automatically.

**Sleven approved both endpoints, staged.** Release View
(`GET /api/roadmap/v1/boards/1`) goes on a timer now; the Progress Tracker GraphQL
endpoint is built now and scheduled when he says. **Every 4 hours, in config.** Plus
an on-demand "check now" command that must run the same code path as the timer.

**Key on card presence plus a payload hash. Never on `updateDate`** — the API returns
Aug 2024 for the same card the UI renders as Aug 2021.

## THE INBOX WATCHER DEFECTS BIT A LIVE DOCUMENT — 2026-08-14. Still unfixed.

**Both known defects were observed in production today, not in theory.**

**It never overwrites.** A corrected document keeps the plain filename on the WRONG
version and the correction lands under a timestamped one nobody opens:

    AMENDS_tripwire-release-view-only-2026-08-14.md                  rev 1, WRONG
    AMENDS_tripwire-release-view-only-2026-08-14__20260814180543.md  rev 2, right

Rev 1 misstated a decision of Sleven's and carried his name. **Anyone reading the
obvious filename would have built the wrong thing.** Both files have been
overwritten with a redirect, so this instance is closed.

**It routes to the wrong place.** `WORKORDER_rework-tripwire-build-spec-2026-08-14.md`
was filed into `docs/handoff_archive/` rather than `docs/`, so the amendment
referenced a work order that was not where anyone would look.

**Neither defect is fixed. This will happen to the next corrected document.** The
fix is not C3's lane. Someone needs to own it.
