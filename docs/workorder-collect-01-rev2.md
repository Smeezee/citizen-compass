# BUILD SPEC — the crew collector, fully specified

    id       WO-COLLECT-01 rev 2 — supersedes rev 1
    from     C2, 2026-08-05
    for      C1 -> Claude Code
    answers  what kind of program, what gets installed, and how the data comes back

**Two changes from rev 1, both simplifications, both because non-technical
friends have to run this.**

---

## 1. WHAT IT IS

**A single Windows program in a folder. No installer.**

    citizen-collector\
      collector.exe          one file, Go, statically linked
      tessdata\eng.traineddata   OCR language data
      names.dat              our item / commodity / shop vocabulary
      config.json            written on first run
      captures\              output goes here

**Download the zip, unzip it anywhere, double-click the exe.**
**Uninstall = delete the folder.** Nothing in the registry, nothing in Program
Files, no services, no admin rights.

**Go, not Python** — one binary, no runtime to install, no "install Python first"
conversation. Matches the project's existing move to Go for background
components.

---

## 2. CHANGE ONE — NO OBS. It captures the screen itself.

**rev 1 read frames from OBS's virtual camera. Drop that for the crew build.**

It means every friend installs OBS, configures a scene, sets the frame rate,
enables the virtual camera, and starts it before playing. **That is five ways to
get it wrong before our program has run a line.**

**Instead: capture directly, using Windows' own API.**

    Windows.Graphics.Capture (WGC)     preferred, Win10 1903+
    DXGI Desktop Duplication          fallback

**Both are operating-system level. Neither touches the game process.** This is
the same class of capture Snip & Sketch and Xbox Game Bar use. **No injection, no
hooking** — the boundary set in `WO-READER-01` is unchanged.

**Result: one download, nothing else to install, nothing to configure.**

**OBS stays in the picture for Sleven only**, when he wants full recordings for
film study. **It is not part of the crew path.**

---

## 3. CHANGE TWO — 10 fps, not 5

rev 1 said 5 fps. **Too low for scrolling.** A shop row on screen for under a
fifth of a second can fall between frames.

**10 fps. Still trivial for static content**, and roughly halves the chance of
skipping a row.

**And it only samples at 10 fps when something is worth sampling** — see §4.

---

## 4. HOW IT DECIDES WHEN TO LOOK

Three watchers, three costs, running together.

**Watcher A — the info panel, top right. Always on, once a second.**
Fixed position, plain debug text, high contrast, does not move. **Cheapest and
most reliable read in the whole design.** Gives location and patch continuously
with no player action.

**Watcher B — panel detection. Ten times a second, a few pixels.**
Sample a handful of pixels where the shop kiosk and the mobiGlas draw. When they
change from background, **a panel opened** — start reading that region at 10 fps.
When they return to background, stop.

**This is what keeps it cheap.** Full-region reading only happens while a panel
is actually up.

**Watcher C — the manual key.** For anything transient: the interaction prompt
that appears when you walk up to something, a notification, anything that flashes.
**Press it, it grabs and reads the current frame properly.**

**Deliberate beats automatic for anything that appears and vanishes.** Do not
promise reliable automatic capture of popups.

---

## 5. HOW IT READS

**No AI. No API. No tokens. Ever.**

**Closed-vocabulary matching.** We already hold every name it could possibly see:
7,728 items, ~200 commodities, 479 shops, and the full location list. **OCR does
not need to be right, it needs to be close.** `Ag-icium` resolves to Agricium.
**A read matching nothing is discarded, never guessed.**

**Engine: Tesseract**, bundled as a DLL beside the exe. Free, offline, no
account.

**Fallback if Tesseract cannot read the game's font** — and it may not, the face
is thin and stylised: **glyph template matching.** The game uses one font at
known sizes, so every character is a known bitmap. Build an atlas once from a
screenshot and matching becomes pixel comparison — **simpler, faster, and pure Go
with no DLL at all.** Brittle to resolution changes, which is why it is the
fallback rather than the default.

**Voting across frames is the accuracy mechanism.** A row visible for two seconds
at 10 fps is read twenty times. Twenty-eight-to-two in favour of "Arclight
Pistol" is a confident answer. **This is why scrolling slowly matters and why a
single screenshot is the wrong tool.**

---

## 6. WHAT THE PLAYER SEES AND HEARS

**Default: sound only. Works on one monitor, in any display mode, including
exclusive fullscreen.**

    short tone     captured and matched something new
    lower tone     read text but matched nothing
    silence        nothing being read

**The beep rate is the scroll-speed gauge.** If the tones stop while still
scrolling, they are going too fast. **A player learns the right speed in one
session without looking away from the game.**

**Optional: a small status chip**, ~200×40, top-most, in a corner.
*"watching · 47 captured"*.

**Correcting rev 1:** a top-most window is **not** the risky kind of overlay.
SCOverlay is exactly that and is posted on RSI's own Community Hub. **Injection
is the danger; a normal window drawn on top is not.** It will not show over
exclusive fullscreen, which is why sound is the default.

---

## 7. WHAT IT WRITES — and how small it is

**The video never leaves the machine. There is no video.** Frames are read and
discarded.

Per session, in `captures\`:

    session_<patch>_<utc>.json     the rows
    crops\<row-id>.png             one small strip per row, ~200x40

**The rows:**

    { "captured_at": "2026-08-05T21:14:03.221Z",
      "patch": "4.9.188.23497",
      "install_id": "a random per-install id, NOT a person",
      "location": { "system": "Stanton", "place": "reststop", "shop": "Casaba Outlet" },
      "rows": [
        { "name": "Arclight Pistol", "matched_id": 1234,
          "price": 4050, "confidence": 0.93, "frames": 28, "crop": "r001.png" }
      ] }

**A whole session is a few hundred rows — kilobytes of JSON plus a few hundred KB
of crops.** It fits in a Discord message.

**The crops are why it is reviewable.** Every row carries the strip of screen it
came from, so a claim can be checked without anyone sending gigabytes. **Better
provenance than UEX has.**

**Never written, stripped before the file exists:** player handle, session id,
shard id, machine specs, GPU, CPU, anything from `[Social]` / `[Login]` /
`[Network]`, chat, other players' names.

---

## 8. HOW THE DATA COMES BACK

**Do not build infrastructure for five people.**

**"Export session" makes one zip. They send it however you already talk —
Discord, email.** Zero servers, zero accounts, zero maintenance, works today.

**It lands in a holding pen, not in the site.** Sleven reviews and approves
before anything reaches the data. **A friend's misconfigured setup must not be
able to quietly poison the prices** — same standard as everything else: nothing
publishes unreviewed.

**If it ever outgrows that**, a shared cloud folder is next and an upload
endpoint after that. **Building either now solves a problem that does not
exist**, and the project's own rule is two or three concrete cases before
generalising.

---

## 9. FIRST RUN — the consent screen

One page. **Nothing runs until they click yes.**

- what it reads: the game's log file, and the screen while a shop panel is open
- what it never reads: chat, other players, anything outside the game window
- what it sends: **nothing, automatically. Ever.** Files are exported by hand.
- how to stop: a key, or close it. **Off means off.**
- how to remove it: delete the folder

**A visible or audible indicator whenever it is watching.** No silent operation.

---

## 10. BUILD ORDER

1. **The ten-minute in-game test.** Kiosk, mobiGlas with a destination,
   `r_DisplayInfo` 1–4, screenshots of each, then read the log. **Decides how
   much reading is needed at all.**
2. **Send stills of a shop list and the info panel.** **The entire reading half
   rests on whether that font is legible in a compressed frame, and nobody has
   checked.**
3. **Log reader** (`WO-READER-01`) — offline, no risk, useful alone.
4. **Watcher A** — the info panel only. Simplest possible loop, proves capture
   and reading end to end on the easiest target.
5. **Watcher B** on commodity kiosks — the simplest screen in the game, and the
   data we have **none** of.
6. **Sound, then export, then the review pen.**
7. **Then the crew**, with consent and stripping.

**Sleven runs steps 3–6 himself before anyone else installs anything.**

---

## 11. NOT VERIFIED

- **Whether Tesseract reads Star Citizen's font.** §5. **The single biggest
  unknown. Answer it with step 2 before building anything.**
- **Whether a shop kiosk logs anything**, and whether any console command reports
  the station. Step 1.
- **Whether WGC captures a game in exclusive fullscreen.** It generally does;
  **not tested.** DXGI fallback exists for this reason.
- **Whether panel positions are stable across resolutions and aspect ratios.**
  Region definitions will need to be per-resolution data files, not code.
- **Antivirus behaviour.** A small unsigned binary that reads game files and
  captures the screen is exactly the shape Defender flags. **Expect it. Do not
  tell friends to add exclusions** — plan for signing or accept the friction.
- **Whether 10 fps is enough at the scroll speed people naturally use.** Measure
  on the first real session.
