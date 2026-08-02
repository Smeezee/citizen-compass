# WORK ORDER — the loadout reader (Phase 1: Sleven's machine only)

    id            WO-READER-01
    raised by     C2 (Cowork), 2026-08-02
    for           C1 -> Claude Code
    scope         P1 and P2 only. P3 (crew distribution) is NOT authorized yet.
    repo writes   C2 made none

Reads a log file the game already writes. **Nothing touches the game process.**

---

## THE SAFETY LINE — non-negotiable

    ALLOWED   read files the game writes
              read raw OS input
              draw an overlay window (NOT in P1 or P2)

    NEVER     read or write game memory
              inject a DLL, hook any function
              send synthetic input into the game
              modify any game file

Precedent: **SCOverlay**, posted on RSI's own Community Hub — no DLL injection,
no hooking, Raw Input API and file reads only. That is the architecture being
copied.

**P1 and P2 draw no window and register no hotkey.** They read a text file. That
is deliberately the most boring thing that could possibly work, because P3 puts
it on other people's machines.

---

## PRECONDITIONS

    Game.log       C:\Program Files\Roberts Space Industries\StarCitizen\LIVE\Game.log
    logbackups\    same folder, 225 files, 199 MB
    catalogue      data-layer/external-sources/scunpacked-data/snapshots/20260801T204744Z/
                     fps-items.json   (5,420)
                     ship-items.json  (5,384)

**`Game.log` is overwritten on every launch.** `logbackups/` is how sessions
persist. Anything not read before the next launch is gone.

---

## WO-R1 — the parser

**In:** any `.log` from `logbackups/` or the live `Game.log`
**Out:** `data-layer/processed/sessions/<build>_<start>.json`

**Session header** — first ~12 lines of every log:

    FileVersion: 4.9.188.23497                      -> patch
    BackupNameAttachment=" Build(12344265) ..."     -> build number
    Log started on Sun Aug  2 02:43:28 2026         -> session start

**The line that matters:**

    <2026-01-28T22:38:17.463Z> [Notice] <AttachmentReceived> Player[Sleven-K]
      Attachment[rsi_odyssey_undersuit_01_01_01_200000000232,
                 rsi_odyssey_undersuit_01_01_01, 200000000232]
      Status[persistent] Port[Armor_Undersuit]

Regex that works, verified against 15,616 real lines:

    Attachment\[[^,]+, ([^,]+), \d+\].*?Port\[([^\]]+)\]

Group 1 is **ClassName**. Group 2 is **Port**. Timestamp from the line prefix.

**Join:** `ClassName` (case-insensitive) → `stdItem.ClassName` in
`fps-items.json` / `ship-items.json` → `stdItem.UUID` → the item catalogue.
**10,804 ClassNames available.**

**Emit per session:** patch, build, start time, and a list of
`{utc, port, class_name, uuid, item_name, matched: true|false}`.

**Strip and never write:** `Player[...]` handle, `sessionId`, machine specs,
GPU/CPU, and anything from `[Social]`, `[Login]` or `[Network]`.
**Strip at parse time, not later** — a file that never contains a handle cannot
leak one. This costs nothing now and is the whole design in P3.

---

## WO-R2 — verification across all 225 logs

**This is the gate. P3 does not happen unless this passes.**

Measured by C2, read-only, across all 225 logs — these are the numbers to
reproduce:

    attachment lines parsed          15,616
    distinct ClassNames                 298
    joined to catalogue                 249    (84% of distinct)
    unmatched                            49

**The 49 unmatched, classified — this is the part that matters:**

| group | count | what they are |
|---|---:|---|
| character-rig parts | 27 | `body_01_noMagicPocket`, `FP_Visor`, `Head_Teeth`, `Shared_Scalp_Unified`, `brows_001`, `Universal_stubble`, `pcg_*` piercings. Not gear. Correctly absent. |
| system defaults | 5 | `Default`, `Default_LensDisplay_PU`, `FPS_DefaultRadar_Lens`, `PersonalMobiGlas_PU`, `LegacyMobiGlas`. **2,305 occurrences between them** — this is why the raw by-occurrence rate is only 52%. |
| props and consumables | ~17 | `crlf_consumable_oxygen_01`, `un_mre_food_1_a`, `Drink_mug_coffee_fluid_1_b`, `un_cigar_single_1_b`, `Carryable_1H_SQ_medical_bag_1_plasma_a` |

**On real equipment ports the join is effectively complete.** Ports observed:

    Armor_Helmet  Armor_Torso  Armor_Arms  Armor_Legs  Armor_Undersuit
    backpack  weapon_attach_hand_right  weapon_attach_hand_left  wep_sidearm
    wep_stocked_2/3  magazine_attach / _1 / _2 / _3 / _4  optics_attach
    utility_attach_1/2  helmethook_attach  inventory_pocket
    Clothing_Torso_1  Clothing_Legs  Clothing_Feet

**Assert:**

    parsed lines            == 15616
    distinct ClassNames     == 298
    joined                  == 249
    join rate on the equipment ports listed above  >= 95%
    zero player handles, session ids or machine specs in any output file

**A drop in the join rate means the log format moved, not that the player
changed clothes.** Treat it as a hard stop.

**One genuine catalogue gap found, worth chasing separately:**
`crlf_consumable_oxygen_01` appears 58 times and does not join.
`crlf_consumable_healing_01` (MedPen) **does** join. So the OxyPen is missing
from the catalogue where the MedPen is present — a data gap, not a parser bug.

---

## WO-R3 — running it on Sleven's machine

Background service, per the standing rule: **auto-start, silent, no console
window, survives reboot.** Same pattern as `inbox_watcher.exe`.

- Watch `Game.log` for changes while the game runs; on game exit, read the new
  `logbackups/` file to catch anything missed.
- **No window. No hotkey. No tray icon needed in P1.**
- Write one session file per play session.
- Log its own activity to `logs/loadout_reader.log` — **not** to
  `pipeline_log.txt`. (A prior session read the wrong log and declared the inbox
  watcher dead; separate logs, clearly named.)

**Go, or Python?** The project is migrating background services to Go for
single-binary headless reliability. **P3 hands a binary to non-technical
friends** — no Python install, no dependencies, no antivirus argument about a
script. **Recommend Go.** Python is acceptable for P1/P2 if it gets a working
answer sooner, but P3 should be Go and the parser should be written knowing that.

---

## NOT IN THIS ORDER

**P3 — crew distribution. Not authorized.** Requirements are drafted in
`claude/plan-crew-capture-and-description-sourcing.md` §2: consent screen,
field stripping at source, off switch, no installer, and the EAC risk being
accepted on other people's behalf rather than Sleven's own. **It needs its own
order after WO-R2 passes.**

**Screenshot correlation.** Later phase. The game already writes timestamped
JPGs to `LIVE/screenshots/` (`ScreenShot-2026-07-22_11-29-29-35A.jpg`), so
matching them to session state is arithmetic — but it is not this order.

**Anything that draws over the game.** Not in P1, P2 or P3.

---

## WHAT THIS WILL NOT DO — set the expectation now

- **It does not know shop prices or shop stock.** Nothing in the log names an
  item on a shelf. Prices still come from UEX.
- **It does not give a position.** Location appears only as asset-load paths
  like `data/objectcontainers/pu/loc/mod/stanton/station/ser/reststop_cargo/…` —
  enough to say "a reststop in Stanton", not which floor.
- **It only knows what is equipped or carried**, and only for whoever is running
  it.

---

## SIDE FINDING — unrelated, but do not lose it

`StarCitizen/HOTFIX/Data.p4k` is present and readable — **154 GB**.

That is the archive holding `defaultProfile.xml`, the **only** missing piece for
Build C (the keybinding reference). The 910 action names, 130 CIG descriptions,
53 modes and 42 categories are already on disk in `labels.json`; only the default
key assignments are missing.

`GlebYaltchik/sc-keybind-extract` was previously identified as a purpose-built
extractor. **Not attempted. Not part of this order.** Recorded so it is not
rediscovered a third time.

---

## OPEN

1. Go or Python for P1 — see WO-R3.
2. Whether `[Cargo]` lines name commodities. 13,057 in one session, four sampled.
   **If they do, the same reader gives mining and trading data for free.**
3. Whether ship components log as attachments the way personal gear does. Every
   session sampled was on foot. **If they do, the loadout bench gets real data
   from the log.**
4. The OxyPen catalogue gap above.
