# Device facts — findings

    from      C3 (Cowork), 2026-08-07
    for       C1 -> Claude Code (viewer/profiles.js), and Sleven directly re: VKB
    order     claude/workorder-device-facts.md
    output    data-layer/raw/devices/device_facts.json (this doc's companion)

---

## What this is

All 7 devices from the work order, researched in parallel, one research pass each. **No field
was guessed.** Every fact carries a source URL; anything that couldn't be sourced is `null`
with a reason recorded in that device's `missing_summary`. Blank beats wrong, per the work
order's own rule — a blank control renders as "press it to identify," a wrong number silently
mislabels a control and nobody notices.

## Summary table

| Device | Confidence | Controls listed | Button index sourced | Button index blank | Geometry sourced | Control inventory rows |
|---|---|---:|---:|---:|---:|---:|
| VKB Gladiator NXT EVO | documented | 17 | 0 | 17 | 12 (approximate) | 13 |
| VIRPIL Constellation ALPHA Prime | community | 17 | 9 | 8 | 0 | 9 |
| VIRPIL CDT-AEROMAX | community | 9 | 0 | 9 | 0 | 11 |
| Thrustmaster T.16000M | documented | 4 | 1 | 3 | 0 | 9 |
| Thrustmaster SOL-R 2 HOSAS | documented | 0 | 0 | 0 | 0 | 10 |
| Turtle Beach VelocityOne Flightstick II | documented | 7 | 0 | 7 | 0 | 8 |
| WinWing/WINCTRL Ursa Minor Fighter/Space | community | 10 | 10 | 0 | 0 | 8 |

**Read this table honestly, not optimistically.** "Controls listed" and "control inventory
rows" are well populated across the board — what each device physically *has*, in plain
words, is solid for every device except the still-unshipped Turtle Beach stick. Button-index
and geometry are the categories that actually feed the wizard's "which raw input just fired"
and "where do I draw it" logic, and those are thin everywhere except the VKB numbering (still
0 sourced) and the Ursa Minor's partial 10-of-44 button map.

## Why button numbering and geometry are thin across the board — one real cause, not seven

Every device hit the same wall: **the vendor's own control-layout diagram and button-mapping
reference exist, but render as an image or PDF, not text** — VKB's template PDFs, VIRPIL's
Configurator 2.0 diagrams, Thrustmaster's manual illustrations, WinWing's manual diagrams.
The tools available this research pass can read web pages and PDF text, but not extract
coordinates from a vector/pixel drawing, and in two cases (`forum.vkb-sim.pro`,
`support.virpil.com`) the domain itself was blocked at the sandbox's network level on every
fetch path tried — direct fetch, the web-fetch tool, and in one case a third-party
text-extraction proxy. That reads as an environment limit, not evidence the data doesn't
exist.

**Recommended next step, concrete:** pull these specific pages from the Windows machine,
outside this sandbox, and transcribe the diagrams by hand or with a proper PDF/image tool:

- `forum.vkb-sim.pro` — the "List of USB Device IDs; Linux Virtual Controller Support" thread
  and the interactive PDF configuration-sheet threads (most likely home of a real button-index
  table for Sleven's own hardware).
- `support.virpil.com` — the Button Mapping FAQ and Configurator 2.0 control-layout pages for
  both the ALPHA Prime and CDT-AEROMAX.
- `support.turtlebeach.com` — the VelocityOne Flightstick II technical-specifications article
  (may still be thin since the device hasn't shipped, but worth checking before the 09-21
  ship date).

## Per-device notes worth knowing before this feeds a build

**VKB Gladiator NXT EVO (priority 1, Sleven's own hardware).** USB VID/PID solidly
cross-confirmed (0x231D, 4 PIDs for L/R and OTA variants) across 3 independent technical
sources. Control inventory (all ~13 named controls: A1 Ministick, A2-A4, B1, C1, D1, Main
Trigger, Rapid Fire Trigger, F1-F3, Sw1, En1, throttle wheel) is well sourced from VKB's own
product pages and template PDFs. **Button index is 0-for-17 sourced** — VKB's own materials
refer to every control by physical label, never a raw number, because the device is fully
remappable and the numbering shifts with firmware mode (native ~128-button vs a 32-button
game-compatibility split). This isn't a research gap so much as a fact about how VKB documents
the device — the physical-label scheme functions as the canonical reference in place of a
number. Geometry is qualitative grid-bucket estimates, not measurements — flagged as such in
every row, should not be trusted for precise drawing yet.

**VIRPIL Constellation ALPHA Prime and CDT-AEROMAX.** Both are grips with no USB connector of
their own — they mount on a base, so "the grip's VID/PID" is really whatever base it's plugged
into. Confidence is `community` for both since the primary source (VIRPIL's own site) couldn't
be read past product-copy level. ALPHA Prime has a partial button map (17 controls, 9 indexed)
from one community Star Citizen keybind repo's default export — indicative, not a VIRPIL
factory table. CDT-AEROMAX has zero sourced button indices. Both have zero geometry.

**Thrustmaster T.16000M.** Best-corroborated USB identity in the set (VID 0x044F / PID
0xB10A, confirmed by 3 independent sources including real hardware reports). Only 1 of 16
buttons has an exact index (the trigger, Button 1) — the rest are known only by zone (3 grip
buttons, 12 base buttons) not individual position. Hat confirmed as a genuine single HID
hat-switch, not 4 buttons — this one's actually useful and solid.

**Thrustmaster SOL-R 2 HOSAS.** Confirmed as a real, current product — importantly, **a pair
of two sticks, not one** — that distinction matters for the wizard UI. 19 named controls
sourced from Thrustmaster's own manual. Zero button indices, zero geometry, and the one USB
PID found comes from a single uncorroborated third-party source. The weakest "documented"
entry in the set despite the confidence label — the label reflects strong control-inventory
sourcing, not strong numbering/geometry.

**Turtle Beach VelocityOne Flightstick II.** Confirmed real, but **pre-order only, shipping
2026-09-21** — nobody outside Turtle Beach has a unit, so USB identity, button numbering, and
axis index order don't exist anywhere yet, full stop. This isn't a research gap, it's a
calendar gap. Control inventory (38 inputs, 8 axes, the named subsystems) is solid from
Turtle Beach's own announcement material. **Re-run this one device after the ship date.**

**WinWing/WINCTRL Ursa Minor.** Name resolved cleanly — WINCTRL is WinWing's current
storefront rebrand, not a mis-transcription — but "Ursa Minor" itself is a product line with
three different devices (Airline, Fighter/Space, and a paired Throttle); the Fighter/Space
Joystick was chosen as the Star-Citizen-relevant guess, not confirmed. Best partial button map
in the set (10 of 44 buttons labeled, from two independent community sources), but one PID
(`0xbc2a`) is claimed for both the L and R grip by two different sources — an open,
unresolved conflict, not a settled fact. Manual-derived numeric values (axis ranges, button
diagram numbers) came through automated PDF summarization rather than a raw-PDF read, so they
carry real transcription-error risk and should be spot-checked before being trusted fully.

## Not this pass's call

- **Wiring `device_facts.json` into `viewer/profiles.js` and the diagram generator** — Code's
  job, covered in the companion work order.
- **Re-running the blocked vendor domains from outside this sandbox** — whoever has direct
  browser access (Sleven, or Code on the Windows machine) is best positioned for this; it's
  the single highest-value follow-up since it's the same root cause across 5 of 7 devices.
- **Resolving the WinWing PID conflict, or confirming which Ursa Minor variant Sleven actually
  has/means** — a factual question only a look at the real hardware or box can answer.
