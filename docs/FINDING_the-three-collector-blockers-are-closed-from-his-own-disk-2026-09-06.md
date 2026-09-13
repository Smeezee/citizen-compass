# FINDING — the collector's three open questions are answered, and the answer has been sitting in `citizen-collector/captures/` since August

**C1, 2026-09-06.** Sleven said his old captures would close them. They do. Two
frames were enough.

---

## What was open

C3's consolidated spec, and every document it consolidated, list three unknowns
gating the reading half. All three have been carried as OPEN since 2026-08-02.

    1. is the game's UI font legible in a captured frame
    2. is the aUEC balance on screen at a kiosk
    3. there is no commodity name list

**Number 3 was closed earlier today** — CIG ships 277 commodity names in
`labels.json` and the snapshot has been on this disk since 27 August.

## What is on the disk

    citizen-collector/captures/     756 PNGs, 757 sidecar JSONs, 3.8 GB
    span                            2026-08-07 to 2026-08-18
    every PNG                       1920x1080, WGC hardware capture

**Each frame carries a sidecar** naming the patch, the build, the location, the
trigger that fired it and the capture method. That sidecar is why finding the
right frames took one query instead of an afternoon: **40 frames were fired by
Sleven pressing the hotkey**, which means he chose them, which means they are the
ones pointed at something.

## Question 1 — the font. ANSWERED YES.

A shop terminal frame from 2026-08-13 reads cleanly **at half size**. Item names,
prices, per-item volume in µSCU, the category and destination dropdowns, the
BUY/SELL tabs, and the station name in the destination field. Nothing is
marginal; nothing needed zoom.

## Question 2 — the aUEC balance at a kiosk. ANSWERED YES.

**Top right of the same frame, labelled `WALLET`, with the figure beside it.**
Same frame as the prices, so the money check the whole provability argument rests
on is available in the single capture that carries the prices — it does not need
a second frame or a second read.

## The thing nobody asked about, and it may matter more

A second frame has `r_DisplayInfo` turned on, and that overlay prints **in plain
readable text**: the zone, the segment, the solar-system coordinates, the patch
build string, the server, the server time, the universe time, and one line that
says outright — **`Current player location : AsteroidClusterBase Nyx Social
Keeger 002`**.

**Location, patch and build come free, as text, with no guessing.** Every design
so far treats "where am I" as something to be inferred from the log or matched
from the scene. **The game will simply print it**, and the sidecars show the
collector was already capturing frames with it on.

That does not make the log redundant — the overlay is only there when it is
switched on, and it is a debug display CIG can change. But **a frame with it on
is self-describing**, which is the cheapest provenance available.

## What this changes

**Nothing in the reading half is blocked any more.** The three unknowns were
answered by material already on this machine — two by a five-minute look at his
own captures, one by a file we sealed in August. **None of it needed research,
new hardware, a model, or anyone's permission.**

**The pattern is worth naming because it is the third time today.** The
`build_frontpage_data.py` that was "thrown away" was untracked in the repo root.
The commodity list that was "missing" was in `labels.json`. These three
"blockers" were in `captures/`. **Every one was a search that asked the wrong
place and got filed as an absence.** That is exactly the failure CIC named on
itself this morning — an absence recorded with an instrument that was never
pointed properly.

## What was NOT checked

**This is a gear and component shop terminal, not a commodity kiosk.** The font
and wallet answers are settled for terminals of this kind. **Whether a commodity
kiosk lays its numbers out the same way is still unproven** and one deliberate
capture at one would settle it.

Nothing was measured about OCR accuracy — this is a human reading a picture, which
answers *legible* and does not answer *machine-readable*. That is the next test
and it needs no new hardware either.

**Rule 21 stands:** these frames are internal. Nothing derived from them is
published, and the frames carry an account name.

*C1, 2026-09-06.*
