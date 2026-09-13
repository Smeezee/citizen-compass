# Update — two orders received: inspector orientation, and two Carrack bundles removed

**2026-09-04 · Code**

    ORDER_every-ship-faced-backwards-in-the-inspector-2026-09-04   (C1, 18:25)
    ORDER_drop-the-two-carrack-c8x-packages-rebuild-2026-09-04     (C1, 18:37)

Both ask for the same thing from me - build and deploy testing - so one rebuild
covers both.

## 1. Every ship faced backwards in the inspector

Sleven walked 93 of the 258 and wrote "shows facing away from the user" on twenty
of them before he stopped bothering, because it was every ship: *"I stopped
reporting it because it became mundane... it was distracting me from the
purpose, which is to look at the actual ship."*

The inspector's orbit opened at `th = 0.9` - positive Z, behind the hull. C1 has
set it to `Math.PI + 0.9` in both the initial state and `orbit.set()`, and
widened the fit radius 1.2 -> 1.45 for the ATLS being too close.

**Worth recording because it is the same defect I fixed in the viewer this
morning, in a different file.** V1 was `cc_viewer.js` opening at +Z when forward
is -Z. The site has been correct since; the inspector was written separately and
repeated it. C1 confirms `cc_viewer.js` is untouched and still opens at
`-d * 0.85`, and Sleven asked specifically that this not fold over into the
project - it does not, and that is read from the viewer's code rather than
assumed. I verified the same thing independently this morning against the point
clouds: the Sabre is 3.7 m wide at low Z and 23.3 m at high Z, so low Z is the
nose.

## 2. The two Carrack C8X entries are RSI store bundles, not ships

`Carrack_Expedition`, `Carrack_Expedition_w_C8X` and `Carrack_w_C8X` are
**byte-identical, all three 876,628 bytes** - so `Carrack_w_C8X` was showing the
Expedition's hull under the plain Carrack's name. Neither was referenced anywhere
on the site. Moved to `_to_delete/`, not deleted. Register 258 -> 256, models
directory 256, inspector list 256.

`C8X_Pisces_Expedition.glb` is the real snub and is untouched.

Sleven's marks are keyed by filename and survive; his counter will now read out
of 256.

## My part

Build, sweep, deploy, verify. Both sets of changes are C1's, in C1's files, and
both were verified by them before the orders were written.

The newest order was written one minute before I read it, so I am checking the
tree has stopped moving before building rather than repeating today's two
race conditions.

## Noted, not acted on

C1 reports **12 more models the site cannot reach** - five pairs or singletons
byte-identical to another file (Ballista Dunestalker/Snowblind, Mole
Carbon/Talus, Caterpillar BIS/Pirate, Cutlass Black BIS, Nox Kue), and four with
**unique geometry that no visitor can see** (Dragonfly Yellowjacket, Hammerhead
BIS, Nautilus Solstice, Reclaimer BIS). The second group is closer to the
30-ship routing problem than to this one. **Sleven named two ships and C1
removed two ships** - the rest is his call.
