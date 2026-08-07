# WORK ORDER — the crew collector: data gathering with no AI, no tokens, no cost

    id       WO-COLLECT-01
    from     C2, 2026-08-05
    for      C1 -> Claude Code
    scope    a small program Sleven and his crew run while playing.
             NO language model. NO API. NO tokens. NO running cost.
    repo     C2 wrote nothing

**Hard constraint, stated first because it shapes every decision below: nothing
in this tool may call a language model or any paid service.** It runs offline on
a player's machine and costs nothing per use. The AI Historian is a separate
product and its vision work is filed separately.

---

## 1. WHY THIS CAN WORK WITHOUT AI

**We are not reading unknown text. We are matching against a list we already
hold.**

    7,728   item names
    ~200    commodity names
    479     shop names
    96/324/73/60/5/117   systems, planets, moons, stations, cities, outposts

**That turns an open-ended reading problem into a closed-vocabulary match**,
which classic OCR plus fuzzy matching does well and a language model is not
needed for. `Ag-icium` resolves to Agricium because nothing else is close. A read
matching nothing is discarded, not guessed.

**Tesseract** is the obvious engine: free, offline, mature, no account, no
network. **Nothing else is required.**

---

## 2. WHAT IT COLLECTS — and what it must never touch

**Collect:**

    item / commodity name      OCR, matched to our list
    price                      OCR, digits beside a matched name
    shop identity              from the log if available; else OCR; else the
                               player picks from a short pre-filtered list
    location                   log asset paths - system and place type
    patch / build              log header, every session
    UTC timestamp              log, to the millisecond
    capture id                 a random per-install id, NOT a person

**Never collect, and strip at the source before anything is written:**

    player handle              the log carries Player[...] - drop it
    session id, shard id
    machine specs, GPU, CPU
    anything from [Social], [Login], [Network]
    chat, in any form
    other players' names, ever

**Strip on their machine, before the file exists.** A file that never contains a
handle cannot leak one. This costs nothing now and is the whole design later.

---

## 3. THE THREE PARTS

### Part A — the log reader

**Already specified as `WO-READER-01`. Unchanged. It is the foundation.**

Reads `Game.log`, gives patch, build, UTC timestamps, gear worn, and rough
location. **Testable entirely offline against the 225 logs already on Sleven's
machine — no game running, no risk.**

**Assert first: 249 of 298 ClassNames join to the catalogue**, and the misses are
character-rig parts and system defaults. **If that rate drops on someone else's
logs, the format moved and nothing ships until it is understood.**

### Part B — the capture

**Uses OBS, which the player already has or installs once.** No custom capture
code, no injection, no overlay drawn over the game.

**Recording settings — the point is small files that stay readable:**

    resolution   NATIVE. Do not downscale. Text needs pixels.
                 This is the one setting that must not be cut.
    frame rate   5 fps. A shop menu is a still picture.
    encoder      NVENC (hardware) - near-zero cost to game frame rate
    rate control CQP ~20, not fixed bitrate
    optional     crop to the region the menu occupies

**Why this is small:** frame rate drives file size, resolution drives
readability, and they are separate dials. A static menu at 5 fps has almost no
frame-to-frame difference, so the encoder stores almost nothing.
**Estimate: a few hundred MB per hour instead of several GB. Not measured —
measure it on the first session.**

**Two modes, same pipeline:**

- **Live** — OBS virtual camera. The tool reads it like a webcam and processes
  frames as they arrive.
- **Later** — recorded clips, read in batch. More accurate, no time pressure.

**Scrolling is a feature, not a problem.** Scroll a shop list once slowly and the
same item passes through twenty or thirty frames. **Twenty-eight reads of
"Arclight Pistol" against two of "Arciight Pistoi" gives a confident answer
by vote.** Repetition beats OCR accuracy — this is why a single screenshot is the
wrong tool and a slow scroll is the right one.

### Part C — the companion window

**On a second monitor. Not an overlay over the game.**

Everything else here stays clear of the game process; drawing on top of it is the
only piece with any exposure, and it is unnecessary when a second screen exists.

    Stanton · Everus Harbor           from the log
    patch 4.9.188                     from the log
    watching · 4m12s
    ------------------------------
    last read:  Casaba Outlet
      Arclight Pistol       4,050
      Arclight Battery        320
      ... 11 more
    ------------------------------
    session: 3 shops · 47 prices

**Why it matters:** the player sees it working. A misread is caught while they
are still standing at the kiosk, not three days later. **If it shows nothing,
they know to scroll again now.**

---

## 4. REVIEW — nothing publishes unconfirmed

**The collector produces candidates, never facts.**

A separate review step, off the game machine: the frame, the extracted
name/price pairs, and yes / fix / discard.

**Three reasons this is not optional:**

1. **Standing rule: auditors flag, they never auto-fix.** An OCR pass is an
   auditor.
2. **The whole site position is honesty about confidence.** Unreviewed
   machine-read prices published as fact would be worse than UEX's tier C.
3. **A wrong price strands somebody at a station.**

**Every row carries:** `captured_by` (install id), `captured_at`, `patch`,
`source: screenshot`, `confirmed: true/false`, and the frame it came from.
**That is better provenance than UEX has.**

---

## 5. DISTRIBUTION — it goes on friends' machines

**Requirements, all of them about trust rather than features:**

- **One file, one folder, no installer.** Uninstall = delete the folder.
- **Go, not Python.** Single binary, no runtime to install, no dependency
  argument, no "install Python first" conversation with a non-technical friend.
  Matches the project's existing move to Go for background components.
- **A consent screen on first run.** One page: what it reads, what it sends, how
  to stop. **It does nothing until they click yes.**
- **A visible indicator whenever it is watching**, and an off switch that works
  without uninstalling.
- **Expect antivirus false positives.** A small unsigned binary that reads game
  files is exactly that shape. **Do not tell friends to add exclusions** — that
  is a bad habit to teach. Plan for signing, or accept the friction.

---

## 6. WHAT IT WILL NOT DO — set this before anyone expects it

- **No stock quantities** unless they are on screen.
- **No precise position.** Location resolves to "a reststop in Stanton", not a
  floor.
- **No other players.** It only ever knows the session it is running in.
- **No AI.** It does not answer questions, explain anything, or reason. It reads
  a list and matches it. **That is the point.**

---

## 7. BUILD ORDER

1. **The ten-minute in-game test.** Open a kiosk, open the mobiGlas with a
   destination, run `r_DisplayInfo` 1–4, screenshot each, **with OBS already
   recording.** Then read that session's log. **This decides how much OCR is
   needed at all** — if the log names the shop, Part B only has to read item rows.
2. **Part A, the log reader.** Offline, no risk, useful alone.
3. **Prove the join across all 225 logs** before anything goes to another person.
4. **Part B on commodity kiosks only** — the simplest screen in the game, and
   the data we have **none** of.
5. **Part C, the companion window.**
6. **The review step.**
7. **Then the crew**, with the consent screen and field stripping.

**Steps 2 and 3 are worth doing even if the rest never happens** — the log reader
alone gives the player's loadout, which is the thing the Historian needs.

---

## 8. NOT VERIFIED

- **Whether a shop kiosk logs anything.** Step 1. Decides the design.
- **Whether any console command reports the current station.** Same test.
- **How readable a Star Citizen price board is in a compressed 1080p frame.**
  **The whole of Part B rests on this and it is unanswered.** Send stills from
  the first recording before building anything.
- **Real file size at 5 fps.** Estimated, not measured.
- **Whether Tesseract handles the game's font** without training. It is thin and
  stylised. **If it struggles, the fallback is a per-font training pass, not a
  language model.**
- **Whether the `[Cargo]` lines name commodities.** 13,057 in one session, four
  sampled. **If they do, cargo and refinery data comes free with no OCR at all.**
