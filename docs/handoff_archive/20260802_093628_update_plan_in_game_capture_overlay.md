# PLAN — in-game capture: what it would actually take

**From C2. 2026-08-02. Planning only. Nothing built, nothing written to the repository.**

Two answers here. The store-link question is §1 and it is short. The overlay
question is §2 onward, and it turned out better than expected — **the hard part
is already solved by a file the game writes.**

---

## 1. THE RSI STORE LINK ROUTE — dead end for the group that needed it

Measured across all 7,728 items.

    items carrying an RSI store link                    1,387
    price-without-description group                       461
      ...of those with a store link                        34   (7%)

    all items with no description                       2,384
      ...with a store link                                716   (30%)

    store links by section:  Liveries 601 · Armor 348 · Miscellaneous 127
                             Personal Weapons 106 · Clothing 101 · Undersuits 37

**34 of 461. The cheap fix is not there.** Worse, the links are unreliable as
image sources even where they exist — `ORC-mkX Arms Iceborn` points at
*Medical-Career-Kit-Medium*, and several Morozov-SH pieces share one
*Sangar-Helmet-And-Mo…* bundle page. **They are pledge-bundle pages, not item
pages.** An image scraped from one would frequently be the wrong object.

And 601 of the 1,387 are Liveries, which get no doorway and no screenshots.

**Conclusion: screenshots are the route for the 461. There is no shortcut.**

---

## 2. WHAT ALREADY EXISTS — do not rebuild it

`overlay_app.py`, `ask_engine.py` and `ASK_OVERLAY_SETUP.md` are already in the
repo. A `Ctrl+Shift+Space` global-hotkey popup, `tkinter`, runs headless under
`pythonw.exe`, searches local project files, falls back to a DuckDuckGo scrape,
answers through local `qwen3:14b` via Ollama.

**That is the shell.** What Sleven is asking for is a second mode inside it —
capture rather than ask. Its known limitations already recorded: hotkey
conflicts, and needing to run as Administrator to receive a hotkey while an
elevated game window has focus.

---

## 3. THE SAFETY BOUNDARY — non-negotiable, and there is a precedent

Star Citizen runs **Easy Anti-Cheat**. RSI's own knowledge-base article is
vague about third-party software — it addresses modded game files and says
nothing specific about overlays or capture tools — so the boundary has to be
drawn from what is demonstrably accepted rather than from a written permission.

**The precedent is `SCOverlay`, posted on RSI's own Community Hub.** It displays
in-game action names as keys are pressed, and it is built to be anti-cheat safe
by construction:

- **no DLL injection**
- **no function hooking**
- native Windows Raw Input API only
- reads the player's own `actionmaps.xml` off disk
- draws a transparent top-most window

**That is exactly the architecture to copy, and the line not to cross:**

    ALLOWED    read files the game writes
               read raw OS input
               capture the screen at OS level
               draw an overlay window

    NEVER      read or write game memory
               inject a DLL, hook any function
               send synthetic input into the game
               modify any game file

Anything in the second list risks a ban on Sleven's own account and would put a
Fan-Kit-compliant site next to a tool that violates the ToS. **The first list is
enough — see §4.**

---

## 4. THE FINDING — the game already logs the loadout, by name we can join

Read from `StarCitizen/LIVE/Game.log` and `LIVE/logbackups/`.

**Every session log carries the exact build:**

    FileVersion: 4.9.188.23497
    ProductVersion: 4.9.188.23497
    BackupNameAttachment=" Build(12344265) 01 Aug 26 (19 43 20)"

**Screenshots are already timestamped to the second** —
`ScreenShot-2026-07-22_11-29-29-35A.jpg` — and log lines are UTC to the
millisecond. **Correlating a screenshot to what was happening is arithmetic, not
guesswork.**

A real 39,159-line play session carries `[Cargo]` 13,057, `[Inventory]` 2,800,
`[Missions]` 1,536, plus location-bearing asset paths like
`data/objectcontainers/pu/loc/mod/stanton/station/ser/reststop_cargo/…`.

**And the `[Inventory]` lines are the prize:**

    <2026-01-28T22:38:17.463Z> [Notice] <AttachmentReceived> Player[Sleven-K]
      Attachment[rsi_odyssey_undersuit_01_01_01_200000000232,
                 rsi_odyssey_undersuit_01_01_01, 200000000232]
      Status[persistent] Port[Armor_Undersuit]

That middle field is a **ClassName**, and ClassName is a join key we already
hold — `stdItem.ClassName` in `fps-items.json` / `ship-items.json`, and the
suffix of `labels.json`'s `item_Desc_<ClassName>` keys.

### Tested, one session, against 10,804 catalogue ClassNames

    distinct attachment ClassNames in the session      49
      joined to the catalogue                          28
      not joined                                       21

**Every one of the 21 misses is a character-rig part** — `body_01_noMagicPocket`,
`FP_Visor`, `PU_Protos_Head`, `Head_Teeth`, `Shared_Scalp_Unified`, `brows_001`,
`Head_Eyelashes`, `universal_necksock_01`. Not gear, and correctly absent from an
item catalogue.

**On actual equipment the join rate is effectively 100%:**

    Armor_Undersuit   rsi_odyssey_undersuit_01_01_01        Odyssey II Undersuit Alpha
    Armor_Helmet      rrs_specialist_light_helmet_01_04_01  Arden-SL Helmet Archangel
    Armor_Torso       rrs_specialist_light_core_01_04_01    Arden-SL Core Archangel
    Armor_Arms        rrs_specialist_light_arms_01_04_01    Arden-SL Arms Archangel
    Armor_Legs        rrs_specialist_light_legs_01_04_01    Arden-SL Legs Archangel
    backpack          rrs_combat_light_backpack_01_04_01    Arden-CL Backpack Archangel
    wep_sidearm       klwe_pistol_energy_01                 Arclight Pistol
    magazine_attach_1 klwe_pistol_energy_01_mag             Arclight Pistol Battery (30 cap)
    medPen_attach_1   crlf_consumable_healing_01            MedPen (Hemozal)
    mobiglas_attach   MobiGlas                              mobiGlas Original Casing

### What this changes

**The player's real loadout is readable from a log file, with zero process
interaction.** No injection, no memory, no ToS question — the same safety class
as a tool RSI hosts a post about.

That does three things at once:

1. **It solves screenshot labelling.** A screenshot taken at 22:38:17 can be
   auto-tagged with everything equipped at 22:38:17 — with UUIDs, because
   ClassName resolves to UUID. The naming-by-UUID discipline from the capture
   protocol stops being manual.
2. **It delivers `claude/historian-loadout-context.md` without the manual step.**
   That doc assumed a player builds a loadout in the bench and hands it over.
   They would not have to. *"My power plant is dying, can I fix it at Everus"*
   becomes answerable because the log already said what is fitted.
3. **It is a differentiator no competitor has.** All four crafting tools and both
   keybinding tools are catalogues. **None of them knows what you are actually
   wearing.**

---

## 5. ARCHITECTURE — three layers, each independently useful

**L1 — the log reader (build first, no UI at all).**
Tail `Game.log`. Parse `<AttachmentReceived>` into
`{timestamp, port, class_name, entity_id}`, resolve ClassName → UUID → catalogue
row. Capture `FileVersion` at session start as the patch stamp. Emit a rolling
`session_state.json`.
**Testable entirely offline against the existing `logbackups/` — 39,159 lines of
real session already on disk.** No game needed, no overlay needed, no risk.

**L2 — capture and correlate.**
Use the game's own screenshot key so the game writes the file. A watcher on
`LIVE/screenshots/` matches each new file to the nearest L1 state by timestamp
and writes a sidecar: patch, UTC time, equipped items with UUIDs, and the last
location-bearing asset path seen.
**Deliberately no screen-capture API at first.** The game already writes a clean
JPG; adding an OS capture path buys nothing and adds a moving part.

**L3 — the overlay, extending `overlay_app.py`.**
A second hotkey that says *"tag the last screenshot"* and offers the equipped
items as the pick list, plus a free-text field for what a shop kiosk is showing.
**This is where a human closes the gap the log cannot** — the log knows what is
worn, not what is on a shelf.

**Order matters.** L1 is useful on its own (the Historian gets a loadout), L2 is
useful without L3 (screenshots arrive labelled), and L3 is pure convenience. If
the project stops after L1 it has still gained something real.

---

## 6. WHAT THIS CANNOT DO — state it before anyone assumes otherwise

- **It cannot read shop shelves.** Nothing in the log names an item on a kiosk.
  Prices and stock still come from UEX, or from OCR, or from Sleven typing them.
- **It cannot give a precise position.** Location comes from asset-path loading
  events — "a reststop in Stanton" — not coordinates. Good enough to say which
  station; not good enough to say which floor.
- **OCR is a separate project, and I would not start it.** Reading item names off
  a shop UI means handling the game's font, scaling, HDR, and every UI change per
  patch. Two of the four crafting sites already have community submission forms
  because this is harder than it looks.
- **It only ever knows Sleven's own session.** This is a personal capture tool,
  not telemetry, and it should stay that way — the moment it collects anyone
  else's data it becomes a privacy question and a very different conversation.

---

## 7. RISKS

- **EAC risk is low but not zero.** File reads and an overlay window are the
  SCOverlay pattern, but EAC behaviour changes without notice and RSI's article
  is not a permission slip. **Never run capture during anything competitive, and
  stop at the first sign of an EAC warning.**
- **Log format is undocumented and will change.** `<AttachmentReceived>` is an
  internal debug line, not an API. Parse defensively, assert the join rate stays
  near 100% on gear, and treat a sudden drop as "the format moved," not "the
  player changed clothes."
- **Administrator rights.** Already recorded in `ASK_OVERLAY_SETUP.md` — a
  global hotkey will not fire over an elevated game window unless the overlay is
  elevated too. That is a real friction point for L3, and it is why L1 and L2
  are designed to need no hotkey at all.
- **Log rotation.** `logbackups/` is how sessions persist; `Game.log` is
  overwritten on launch. **Anything not read before the next launch is gone.**

---

## 8. NOT VERIFIED

- **Whether `[Cargo]` lines name cargo contents.** 13,057 of them in one session
  and I only sampled four — they looked like elevator/platform loading, not
  manifests. **Worth a proper look; if they carry commodity names and amounts,
  the mining and trading side gets the same treatment as gear.**
- **Whether ship components appear as attachments** the way personal gear does.
  The sampled session was on foot. **If they do, the loadout bench gets its real
  data from the log too.**
- **Whether the location asset paths resolve to our 479 shops or 1,774 positioned
  entities.** They are file paths, not UUIDs, and the mapping is unproven.
- **Whether the join rate holds across sessions.** One session, 28 of 28 on gear.
- **Current EAC behaviour toward overlay windows.** Read RSI's article and the
  SCOverlay post; ran nothing.
