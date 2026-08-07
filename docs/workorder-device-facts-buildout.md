# Work order — wire device_facts.json into the device panel (D3/D4/D5 buildout)

    from      C3 (Cowork), 2026-08-07
    for       C1 -> Code
    inputs    data-layer/raw/devices/device_facts.json (in repo, 7 devices)
              data-layer/raw/devices/device_facts_findings.md (in repo, read this first —
                it has the per-device confidence/gap notes that matter for UI decisions)
              claude/FINDING_device-panel-D3-D4-D5-and-device-facts-status.md (prior state,
                what's actually built vs. planned)
    status    ready to start. Not blocked on anything except Code's own priority queue.

---

## Why this order exists

`claude/workorder-device-facts.md` asked for sourced facts on 7 flight sticks so the device
panel's D3 (unified control model), D4 (layout), and D5 (guided mapping wizard) could be built
on real data instead of guesses. That research is done and in the repo. This order is the
buildout that consumes it. Read `device_facts_findings.md` before touching code — it tells you
which devices have real button-index data (VKB: none, Ursa Minor: 10 of 44, T.16000M: 1 of 16)
and which are inventory-only (everything else), because the UI has to behave differently for
"I know exactly which button that is" vs. "I know this device has a button roughly here."

## What's still open per the prior status finding

- **D3 — unified control model.** Never built. The crash/double-count risk from mixing axis
  and button events is defused, but there's no `control:{id,label,x,y,inputs:[]}` object per
  the original design. This is the foundation the wizard (D5) needs.
- **D4 — layout.** Side-by-side both-devices works. Two gaps: the "0 tiles at rest" default
  doesn't hold (a hide-unused toggle exists but defaults off, so 40 tiles show at rest instead
  of 0) — flip that default. The add-on-device toggle for pedals/throttle quadrants (separate
  from the two main sticks) doesn't exist at all — needs building.
- **D5 — guided mapping wizard.** Fully unbuilt. No wizard, no checklist, nothing.

## What device_facts.json actually gives you, honestly

Per-device confidence varies a lot — don't treat the file as uniformly reliable:

- **VKB Gladiator NXT EVO** (Sleven's own hardware, priority 1): solid USB VID/PID (0x231D +
  4 PIDs), solid control inventory (13 named controls), **zero sourced button indices** — VKB
  documents by physical label only, not number, because numbering shifts with firmware mode.
  Geometry is qualitative grid-bucket estimates, not real coordinates — don't use it for pixel
  placement yet.
- **VIRPIL ALPHA Prime**: 9 of 17 controls have a community-sourced button index (indicative,
  not a VIRPIL factory table — flag as such if surfaced in UI). Zero geometry.
- **VIRPIL CDT-AEROMAX**: control inventory only, zero button indices, zero geometry, one open
  conflict in hat count (2 vs 3 four-way hats — unresolved).
- **Thrustmaster T.16000M**: best USB ID in the set. Only the trigger (button 1) has an exact
  index; everything else is known by zone only (3 grip, 12 base). Hat confirmed as a real
  single HID hat-switch, not 4 buttons — safe to rely on.
- **Thrustmaster SOL-R 2**: this is a HOSAS pair (two sticks), not one device — UI needs to
  handle that distinction if it doesn't already. 19 named controls, zero button indices, zero
  geometry.
- **Turtle Beach VelocityOne Flightstick II**: doesn't ship until 2026-09-21. Control inventory
  only (nothing to plug in yet, so no button/axis/hat data exists anywhere). Don't build a
  device profile expecting numeric fields to fill in soon — there's a hard calendar floor.
- **WinWing/WINCTRL Ursa Minor Fighter/Space**: best partial button map in the set (10 of 44),
  but the device-variant itself is a guess (product line has 3 devices; Fighter/Space chosen as
  most SC-relevant, unconfirmed), and one PID is claimed by two grips — flag both as open.

## Recommended build sequence

1. **Build the D3 `control` model** keyed off `device_facts.json`'s per-device control list,
   with `hid_index: null` rendering as "press it to identify" in the wizard (per the work
   order's own rule — never guess a number to fill a gap).
2. **Fix D4's two gaps**: flip the hide-unused-tiles default to on (0 tiles at rest), add the
   pedals/throttle-quadrant toggle as a genuinely separate device slot, not folded into the two
   main sticks.
3. **Build D5's wizard** on top of the D3 model: for each control with a known `hid_index`,
   confirm on first press; for `null` ones, prompt "press the control you mean" and record
   whatever index actually came back from the browser Gamepad API at runtime — this is how the
   VKB and most other devices' numbering gets filled in for real, from Sleven's own hardware,
   instead of waiting on vendor PDFs.
4. **Surface confidence in the UI**, at least at the device level (`documented` / `community` /
   the Turtle Beach not-yet-shipped case) — a `community`-tier VIRPIL mapping showing with the
   same visual weight as a kernel-confirmed Thrustmaster hat would be misleading.

## Explicitly not in this order

- Re-fetching the blocked vendor domains (`forum.vkb-sim.pro`, `support.virpil.com`,
  `support.turtlebeach.com`) — that's a research task for whoever has unblocked browser access
  (Sleven or Code from the Windows machine), not a code change. If Code does end up pulling
  those pages by hand, feed corrections back into `device_facts.json` directly (update the
  relevant `hid_index`/geometry field, bump confidence, add the source URL) rather than a new
  parallel file.
- Resolving the WinWing PID conflict or confirming the Ursa Minor variant — needs the real
  hardware/box, not a code decision.
- Re-running Turtle Beach after ship date — flagged for a future session, not blocking this
  build.

## Testing note

Sleven has his VKB Gladiator NXT EVO powered on and available today. Once D5's wizard exists
even in a rough form, it's the fastest way to validate the whole pipeline against real
hardware — every `null` VKB button index gets a real answer the moment he runs through it once.
