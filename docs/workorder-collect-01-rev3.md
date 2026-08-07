# BUILD ORDER — the crew collector

    id       WO-COLLECT-01 rev 3 — supersedes rev 1 and rev 2
    from     C2, 2026-08-05
    for      C1 -> Claude Code
    status   complete build order. No open design questions.

**Two things changed from rev 2.** The font problem is now **specified and
solved** rather than flagged as a risk — §3. And the fixed regions are replaced
by **a grid of independent zone watchers** — §2, Sleven's design.

---

## 0. WHAT IT IS

**One Windows folder. No installer.**

    citizen-collector\
      collector.exe          Go, statically linked, single binary
      atlas\                 glyph atlases, one per resolution   (§3)
      names.dat              item / commodity / shop / location vocabulary
      zones.json             zone grid definitions               (§2)
      config.json            written on first run
      captures\              output

Unzip, double-click. **Uninstall = delete the folder.** No registry, no
services, no admin rights, **no OBS, no Python, no AI, no API, no tokens.**

**Screen capture: `Windows.Graphics.Capture`, with DXGI Desktop Duplication as
fallback.** OS-level. **No injection, no hooking** — the boundary from
`WO-READER-01` is unchanged.

---

## 1. THE THREE INPUTS

    the game log      patch, build, UTC time, gear worn, rough location.
                      Free, no reading required. WO-READER-01.
    the screen        zone watchers, §2
    a manual key      grabs and reads the current frame in full.
                      For anything transient.

---

## 2. ZONE WATCHERS — a grid, not fixed regions

**Fixed region definitions break every patch and cannot catch anything we did not
anticipate. A grid does neither.**

### The grid

Divide the client area into **a 6 × 4 grid — 24 zones.** Stored in `zones.json`
as fractions of the window, never pixels, so it survives any resolution.

Each zone runs independently and holds a small state machine:

    IDLE      sample 16 pixels, 10x/sec, hash them.  Cost: negligible.
    CHANGED   hash differs from last -> something appeared or moved
    SETTLING  hash changed again -> still moving, do not read yet
    STABLE    hash unchanged for 150 ms after a change -> READ NOW
    READING   full-region read, then back to IDLE

**Reading only ever happens on STABLE.** A panel sliding open, a scene loading,
or a camera pan never triggers a read — they never settle. **This is what keeps
24 zones affordable.**

### How they work in harmony

**Neighbour merging.** Zones that go STABLE within the same 150 ms window and
share an edge are **one panel**. Merge them and read as a single region.
A shop list spanning six zones is read once, not six times.

**Whole-screen suppression.** If more than 14 of 24 zones change at once, that is
a scene load or a camera cut. **Read nothing. Reset all zones to IDLE.**

**A read budget.** At most **4 region reads per second**, whichever zones have
the largest change area. Everything else waits. **The budget is the ceiling on
cost, and it is fixed regardless of what is on screen.**

**Zone learning.** Each zone keeps a running tally of what has been successfully
matched in it — item names, prices, location names, nothing. After a session or
two, `zones.json` records that zone 3,1 usually holds prices and zone 0,0 usually
holds the info panel. **Learned zones get priority in the budget and a tighter
expected-content filter.** Nothing is hardcoded; it is learned per player, per
resolution, per UI layout.

**This is why it survives a patch.** CIG moves a panel, the zones relearn. No
region file to update, no silent breakage.

### What each zone reports

    zone id · change area · settle time · extracted text ·
    matched entities · confidence

---

## 3. READING THE FONT — glyph atlas, specified

**This is the answer to "Tesseract may not read the game's font." It is not a
fallback. It is the design.**

**Why not general OCR:** Tesseract's strength is handling arbitrary unknown
fonts. **We do not have that problem.** Star Citizen renders **one UI font, at a
handful of sizes, white-on-dark, no anti-alias variation between frames.**
Tesseract's weakness — thin stylised faces — is exactly our case. **We are
paying its cost and getting none of its benefit.**

**What we do instead: match glyphs against a known atlas.**

### 3a. Building the atlas — once, by the player, guided

**A calibration mode in the tool.**

1. Player opens a shop or the info panel and presses the calibrate key.
2. The tool captures the region and **segments it into text lines**, then into
   **character cells** — threshold to binary, find columns of background between
   glyphs.
3. The tool shows the player the captured strip and asks: **"type exactly what
   this says."**
4. Character count is matched to cell count. **Each cell is now a labelled
   bitmap.**
5. Repeat over 3–4 strips until every character in the alphabet, digits,
   and punctuation is covered. **Ten minutes, once.**
6. Write `atlas\<width>x<height>_<fontsize>.atlas`.

**Ship Sleven's atlas with the tool.** Most players run 1920×1080 or 2560×1440
with default UI scale, so **most people never calibrate at all** — the bundled
atlas matches. Calibration exists for anyone whose setup differs.

### 3b. Matching at runtime

1. Threshold the region to binary. **The game's UI is high-contrast; a fixed
   threshold at ~60% luminance works and is one operation.**
2. Segment into lines by horizontal projection, into cells by vertical.
3. For each cell, compare against every atlas glyph of that height.
   **Score = count of matching pixels / total pixels.**
4. Best score wins. **Below 0.80, emit `?`.**
5. Assemble the string.

**Pure integer comparison, no libraries, no DLL, no model.** Faster than
Tesseract by a wide margin and **exact on a fixed font** rather than
probabilistic.

### 3c. Then the vocabulary does the rest

**The string does not need to be perfect.** Match it against the known list —
7,728 items, ~200 commodities, 479 shops, the location set — using **Levenshtein
distance, accept at ≤ 20% of string length.**

`Ar?light Pist?l` resolves to Arclight Pistol because nothing else is close.
**A string matching nothing is discarded, never guessed.**

**Prices are easier still:** digits, commas, and the aUEC suffix. Ten glyphs.
**A price that fails to parse is dropped, never rounded or inferred.**

### 3d. Voting

A row visible for two seconds at 10 fps is read twenty times. **Take the majority
string per row.** Twenty-eight-to-two settles it.

**This is the accuracy mechanism, and it is why scrolling slowly matters** — and
why a single screenshot was always the wrong tool.

---

## 4. FEEDBACK — sound first, screen optional

**Default: sound.** Works on one monitor, in any display mode, including
exclusive fullscreen.

    short tone     matched something new
    lower tone     read text, matched nothing
    silence        nothing being read

**The beep rate is the scroll-speed gauge.** Tones stop while still scrolling =
going too fast. **Learned in one session, without looking away from the game.**

**Optional: a ~200×40 top-most status chip.** *"watching · 47 captured"*.
**A top-most window is not injection** — SCOverlay is exactly this and is posted
on RSI's Community Hub. It will not draw over exclusive fullscreen, which is why
sound is the default.

---

## 5. OUTPUT

**There is no video. Frames are read and discarded.**

    captures\session_<patch>_<utc>.json
    captures\crops\<row-id>.png          ~200x40 strip per row

    { "captured_at": "...", "patch": "4.9.188.23497",
      "install_id": "<random per install, NOT a person>",
      "location": {"system":"Stanton","place":"reststop","shop":"Casaba Outlet"},
      "rows": [ {"name":"Arclight Pistol","matched_id":1234,"price":4050,
                 "confidence":0.93,"frames":28,"zone":"3,1","crop":"r001.png"} ] }

**A session is kilobytes of JSON and a few hundred KB of crops. It fits in a
Discord message.**

**Stripped before the file exists, never written:** player handle, session id,
shard id, machine specs, GPU, CPU, `[Social]` / `[Login]` / `[Network]` content,
chat, other players' names.

---

## 6. GETTING IT BACK

**"Export session" → one zip → they send it however you already talk.**
No server, no account, no upload endpoint. **Do not build infrastructure for five
people.**

**It lands in a holding pen. Sleven approves before anything reaches the data.**
A misconfigured install must not be able to quietly poison prices.

---

## 7. FIRST RUN

One consent page. **Nothing runs until they click yes.**

- reads: the game log, and the screen while the game is focused
- never reads: chat, other players, anything outside the game window
- sends: **nothing, automatically, ever.** Export is manual.
- stopping: a key, or close it
- removing: delete the folder

**Audible or visible indicator whenever it is watching. No silent operation.**

---

## 8. BUILD ORDER

1. **Log reader** (`WO-READER-01`). Offline, no risk, useful alone.
2. **Capture + the zone grid**, reporting change events only. **No reading yet.**
   Prove 24 zones cost nothing and that STABLE fires where expected.
3. **Calibration mode and the atlas builder** (§3a). **Sleven builds the first
   atlas.**
4. **Glyph matching + vocabulary** (§3b–c) on the **info panel only** — smallest,
   highest-contrast, fixed target.
5. **Commodity kiosks** — simplest list screen, and the data we have **none** of.
6. **Voting, sound, export.**
7. **Review pen.**
8. **Then the crew**, with consent and stripping.

**Sleven runs 1–7 himself before anyone else installs anything.**

---

## 9. ACCEPTANCE

    24 zones idle                      < 1% of one CPU core
    read budget                        never exceeds 4 regions/sec
    scene load                         >14 zones changing triggers zero reads
    atlas match                        >= 0.80 per glyph or emit '?'
    vocabulary match                   Levenshtein <= 20% of length, else discard
    price parse failure                dropped, never inferred
    output                             contains no handle, no chat, no other player
    export                             one zip, sends in a chat message
    nothing publishes                  without passing the review pen

---

## 10. NOT VERIFIED

- **Whether WGC captures Star Citizen in exclusive fullscreen.** Generally yes;
  untested. DXGI fallback exists for this.
- **Whether 6×4 is the right grid.** A guess. **Make it a config value and tune
  it on the first real session.**
- **Whether 150 ms is the right settle window.** Same — configurable, tune it.
- **Whether the game's UI anti-aliases differently at different scales**, which
  would need one atlas per UI scale as well as per resolution.
- **Antivirus.** A small unsigned binary that reads game files and captures the
  screen is exactly that shape. **Expect it. Do not tell friends to add
  exclusions.** Plan for signing or accept the friction.
- **Whether a shop kiosk logs anything.** Still the ten-minute test, and it would
  make §2's job smaller.
