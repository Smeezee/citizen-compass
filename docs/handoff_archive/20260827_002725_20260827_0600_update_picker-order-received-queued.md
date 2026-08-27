# Update — hardpoint picker order received, queued behind C3

**2026-08-27 · Code**

Received `docs/ORDER_the-hardpoint-picker-2026-08-27.md`. Approved by Sleven
after seven prototypes. It replaces the permanent hull labels with the
dot -> hover chip -> docked picker loop, on every ship.

**Queued behind the standing queue, as instructed - not in front of it.** The
standing queue has one item left, C3, and I am resuming it now.

**Scope noted, and I will hold to it:** the hull-marker interaction and the
picker that opens from it. The left-panel rebuild stays parked. **The "inside
the ship" dock from the prototype is explicitly out** - Sleven called it sloppy
and it needs its own pass.

**Two hard requirements recorded up front so they are not treated as
preferences:**

1. **The sort tabs use the vocabulary already settled in `loadout.html`'s WATCH
   table** - DPS, Alpha, EM, IR, Mass, Shield HP, Regen, Cooling, Power. Not
   new words. And the tabs are per component type: a cooler must never be
   offered "biggest hit".
2. **The picker never scrolls.** Best 4 by the active sort plus the fitted part
   pinned - five rows, on every ship and every component type. Re-sorting is how
   a person reaches the rest.

**Before it ships it gets tested on the RSI Polaris (29 mounts) and the Perseus
(37), not the four-mount Vulture the prototype used.** If 29 dots is
unworkable I will report it with a screenshot rather than ship it and let
Sleven find out. F3's headless Chromium is already installed under `checks/`
and can take that screenshot.

Also filed from that order, explicitly not in scope and worth not losing:
**markers are weapons-only, which is wrong for industrial ships.** The
Vulture's two salvage heads get no marker while its two countermeasure
launchers do. On a salvage ship the salvage arms are the defining hardware and
they are invisible on the hull.
