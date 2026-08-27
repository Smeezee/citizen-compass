# ORDER — the ship faces away, and there are too many dots

**2026-08-26 · C1 · for Code · three defects Sleven found in the first pass
after F1/F2 landed**

**F1/F2 WORKED.** He opened the Harbinger and the hull was there. Everything
below is what he could see once there was something to see.

---

## V1 — every ship on the site is shown from behind

His words: *"It was perfectly right there on the page. Didn't look like a ship.
It just looked like a blob of colours until I rotated it."*

**The camera is parked behind the tail, above.** `frame()` sets:

    this.camera.position.set(d * 0.75, ty + d * 0.42, d * 0.85);

Positive Z. And this project's own hardpoint placer states the model frame
explicitly, from measurement rather than assumption —
`place_hardpoints.py` lines 28-34:

    Z  forward = -Z.  At the low-Z end the Sabre is 369 cm wide; at the
                 high-Z end it is 2338 cm, the full wingspan. A Sabre's
                 nose is a point and its tail is the wings, so low Z is
                 the nose. The Aquila agrees.
    Handedness: with forward = -Z and up = +Y, right = forward x up = +X.

**Forward is -Z. The camera sits at +Z. It has been looking at the back of
every ship in the fleet since the viewer shipped.** A fighter seen tail-on,
from above, is a shapeless mass with a wing sticking out of it — which is
exactly what he described, and exactly what a render from that direction shows.

**The fix is the sign on one term:**

    this.camera.position.set(d * 0.75, ty + d * 0.42, -d * 0.85);

That is a front three-quarter view: nose toward the viewer, slightly above,
slightly to one side. It is the angle RSI's own holoviewer opens on and the
angle every ship page in the genre uses, for the reason that it is the one
angle from which a ship reads as a ship.

**Do not add per-ship orientation data for this.** The frame is already
established fleet-wide and already proven — the entire hardpoint placer depends
on it. One convention, one line, 239 hulls.

**V1b — a control.** Render a sample of hulls and assert the camera's opening
position has negative Z relative to the target. Mutation: restore the positive
sign; the control must go red. This belongs with F3 and is the cheapest
possible use of the real browser.

---

## V2 — one dot per gun, including every gun inside every turret

> **APPROVED BY SLEVEN, 2026-08-26.** One marker per physical mount, clicking
> it opens the weapons on that mount into the same picker the list uses. The
> count line is rewritten with it. This is a go — build it after V1/V3 deploy,
> C1 and C4.



His words: *"there's also way too many hard points on it."*

The Harbinger shows **34**. The Asgard shows **42**. The Polaris shows **133**.

**This is C1/C2 working exactly as ordered, and the order was half right.**
Before it, a gun mounted inside a turret inherited no position and got no
marker — the Retaliator showed 4 of its 24 weapons and the page was lying by
omission. C1/C2 fixed that by giving every child gun its turret's position.
**So a four-gun turret now plants four markers on one spot.** Fleet markers
went 1,252 to 3,707 and the label solver has been drowning ever since.

**The fix is one level of nesting, not a retreat.** A PortId is already a path
— `15.loadout.0.loadout.0` is a gun, inside mount `15.loadout.0`, inside turret
base `15`. Group markers by the first segment. One marker per physical mount;
clicking it lists the weapons on it and opens any of them into the same picker
the list uses. **No information is lost and nothing is hidden** — the thing that
changes is that a turret with four guns is drawn as one turret rather than four
coincident dots.

Measured across all 165 hulls that carry markers:

| | markers today | one per mount |
|---|---|---|
| fleet total | **3,707** | **1,366** (63.2% fewer) |
| median ship | 17 | **8** |
| ships over 40 markers | **21** | **0** |
| RSI Polaris | 133 | 29 |
| RSI Perseus | 105 | 37 |
| Aegis Hammerhead | 92 | 18 |
| Aegis Idris-M | 92 | 30 |
| Anvil Asgard | 42 | 15 |
| Aegis Vanguard Harbinger | 34 | **13** |
| Aegis Retaliator | 24 | 9 |
| Drake Vulture | 6 | 4 |

**This also retires the label-crowding problem rather than deciding it.** The
open question was whether to turn labels off on 65 hulls; at 8 markers on a
median hull there is room for all of them, and the Polaris's "95 of 133 have no
room" becomes 29 markers on a 181-metre ship.

**The count line must stay honest.** It says "34 hardpoints" today; it should
say what it now means — mounts, and the weapons on them — not quietly report a
smaller number for the same ship.

---

## V3 — the Display panel is open by default and covers the ship

Not reported by Sleven, found while measuring V1: **the settings panel is open
on load and occupies roughly the left 40% of the viewer stage.** At 900 px wide
it hides most of the hull; at 1600 px it still covers the nose of a
front-quarter view.

Every screenshot taken of this page in the last four days has the panel over
the model, including the ones used to argue about how the hull renders.

**Default it closed.** The button that opens it is already visible, already
labelled, and its settings already persist — H1f/Q3 made the panel findable and
its state permanent, which is what makes closing it by default safe: somebody
who opens it once keeps it open.

---

## Order of work

1. **V1.** One character. Deploy and let Sleven look — it changes the first
   impression of all 239 ships and nothing else.
2. **V3.** Also trivial, same deploy.
3. **V2.** Real work, and the one that needs the count line rewritten with it.
4. F3, A1-A2, then A3-A4.

Do not deploy the live site. Testing only.
