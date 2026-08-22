# ORDER — three columns, a viewer that stops spinning, and markers that work. RUN CONTINUOUSLY.

    from    C1, 2026-08-22, from Sleven looking at the deployed page.
    for     Code
    status  GO. No stop points. Run rules are §1 of
              docs/ORDER_shop-and-price-layer-RUN-CONTINUOUSLY-2026-08-19.md.
              Testing deploy at the end is automatic (D1).
    ledger  APPEND, items P-.

    NOT IN SCOPE, deliberately:
      * The hologram/wireframe render pass. CIC is researching it now and the
        order comes after. **Do not restyle the material or lighting.**
      * The two weak greps in `_verify_shared_viewer.mjs` §1-§2 you offered to
        fix. **Leave them.** They are mostly ABSENCE checks, which a text search
        is the correct instrument for, and the viewer is about to be rewritten
        for the render pass - strengthening them now means writing them twice.

---

## 0. WHAT SLEVEN SAID, and the target that governs everything

> "The 3D viewers are a little bit too wide. It runs screen to screen on each
> side... we need to merge some of the critical stuff along the sides, like it
> used to be, where there was little boxes that said things and you could click
> them."

> "We are filling up way too much space with empty space, and we need to compact
> this. I would love it to where the user never has to scroll to see anything on
> this menu. It's all accessible right there in a very neat and well thought out
> manner."

**THE TARGET: the ship page fits on one screen.** That is measurable and §P7
measures it. It is also the reason for every other item here.

**RULED AND CLOSED — the hardpoint placement is accepted as it stands.** Sleven:
*"the hardpoints, they look correct... generalized hardpoint, it's fine. We could
fine tune them later by hand if necessary."* **Do not re-derive, re-place or
re-verify marker positions.** The N9 honesty note stays exactly as written.

## 1. THE LAYOUT

**P1. THREE COLUMNS.** Approved by Sleven from this sketch:

    Redeemer · Aegis · Gunship         9,803,430 aUEC · $330 · RSI ↗
    ┌──────────────┬─────────────────────────┬──────────────┐
    │  COMPONENTS  │                         │   READOUT    │
    │  clickable   │       3D VIEWER         │  stat tiles  │
    │  slot boxes  │   bounded · stop spin   │              │
    └──────────────┴─────────────────────────┴──────────────┘
      Loadout · Engineering · Liveries · Where to buy · Specs

- **Left: the components, as clickable boxes.** This is the thing Sleven liked on
  the old index panel and wants back — a box naming the slot and what is fitted,
  which opens the picker. Fixed ports stay folded away per N7.
- **Centre: the model**, bounded, not edge to edge.
- **Right: the readout.** Stat tiles.
- **Header:** name, manufacturer, role, in-game price, pledge price, RSI link.
- **Tabs below**, unchanged from M1.

**P2. THE VIEWER IS BOUNDED.** It stops running the full width. Give it a sane
maximum and let the columns take the rest.
*Control:* at 1920×1080 the canvas occupies **no more than half** the page width.

**P3. COMPACTION PASS.** *"Way too much space with empty space."* Tighten the
stat tiles, the gaps and the padding. **Nothing decorative may cost a row.**
*Control:* count the vertical pixels from the top of the page to the bottom of
the tab strip, before and after. **Report both numbers.**

## 2. THE VIEWER

**P4. A CONTROL TO STOP THE ROTATION.** *"The ship just constantly spins. There's
not a way to stop the spin. I don't see a stop button anywhere."*
`autoRotate` and something called `pause` already exist in the page and **nothing
is exposed.** Put a visible control on the canvas. Rotation state persists while
the person is on the page.
*Control:* the control exists, is reachable by keyboard, and toggling it actually
halts rotation — assert the rotation value, not the presence of a button.

**P5. THE MARKERS DO NOTHING WHEN CLICKED, AND THIS IS A BUG.**
Sleven: *"they don't do anything. I click them and they do nothing."*
The click listener and the raycasting are both present in `loadout.html`, so this
is wired and not landing.
**C1's suspicion, to be checked not trusted: the model is rotating under the
cursor**, so the raycast at mouse-up hits a marker that has moved. **Diagnose it
properly** — it may equally be the raycast targeting the wrong object, a layer
mismatch, or sprite geometry the raycaster does not hit.
*Control, and it must be behavioural — this is the erratum's lesson:* project a
known marker to screen coordinates, dispatch a real click there, and **assert the
picker opened for THAT PortId and no other.** Do the same with rotation running
and with it stopped. **Asserting that a listener exists is worthless** — that is
exactly what let every ship name point at RSI.

## 3. THE SECOND BUILD

**P6. `Try another alongside` GIVES NO VISIBLE FEEDBACK.**
Sleven: *"all it does is kinda refresh the bottom menu, and it's like, okay, that
moved. Let me scroll down a little bit. And then you see that there's a build A
and a build B."*
**A button whose effect you cannot see has not worked, as far as the person
pressing it is concerned.** The second build must appear **where the eye already
is**, not below the fold. Same for `Discard this one` in reverse.
*Control:* after the click, the second build's first component row is **within the
viewport** at 1920×1080 without scrolling.

## 4. THE MEASURE

**P7. NO SCROLLING TO SEE THE PAGE.** At **1920×1080**, everything in §P1 —
header, three columns, tab strip — is visible **without vertical scroll**. The
components column and the readout may scroll **within themselves**; the page must
not.
*Control:* measure the rendered document height against the viewport at
1920×1080 and assert it fits. **Then measure at 1366×768 and report the number** —
do not fail on it, but say how far off it is, because that is the next decision.
**Wide monitors do not count as passing.** Sleven runs an ultrawide; most visitors
will not.

**P8. SWEEP + DEPLOY.** Every control in `checks/`, deploy to testing per the
standing rule, verify from the served bytes.

## 5. WHAT MUST NOT HAPPEN

- **Do not touch the material or lighting.** §0. That order comes after CIC.
- **Do not re-place or re-verify hardpoint positions.** §0. Settled.
- **Do not fix the shared-viewer greps.** §0.
- **Do not assert a listener exists and call a click fixed.** P5.
- **Do not let the viewer run edge to edge.** P2.
- **Do not deploy the live site. Do not cut a release. Do not `git add -A`.**

## 6. REPORT

- Page height before and after, at 1920×1080 and at 1366×768.
- What the marker click turned out to be — the actual cause, not the fix.
- Anything here you think is wrong. **P7 is the part most worth arguing with** —
  if a full ship page genuinely cannot fit 1920×1080 without something important
  being cut, **say what would have to go** rather than shrinking type until it
  technically fits. Sleven's words are "neat and well thought out", not "smaller".
