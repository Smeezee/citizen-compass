# FINDING — the "no texture" gap is a hologram display waiting to happen. Demonstrated, not just proposed.

    from      C3 (Cowork), 2026-08-08
    for       Sleven + C1 + Code
    ask       Sleven: "make a holographic looking version of the ship and stamp it with
              made by community... show them what the paint looks like in a static photo,
              separately, sourced from CIG's own site"
    method    Built a real proof of concept from the Fan Kit's own geometry rather than
              describing the idea in the abstract. Tools used: `ctmconv` (official OpenCTM
              converter) to decode the model, a hand-written wireframe renderer
              (numpy + matplotlib) with depth-based glow, PIL to composite the required
              marking. Not a mockup — the actual 80,094-point mesh, actually rendered.

---

## The idea, confirmed technically

The "no texture data" finding from earlier today (`FINDING_fankit-inventory-2026-08-08.md`)
looked like a dead end for display purposes. It isn't. **A hologram is supposed to look like
glowing lines, not painted metal — the absence of texture data is exactly the material a
holographic-style render needs, not a gap in it.**

Demonstrated on `Tumbril Cyclone.ctm`: decoded the real mesh, drew every edge as a glowing
cyan wireframe (depth-cued — nearer edges brighter, further edges dimmer), on a dark
background, and composited the required "Made By The Community" logo plus the exact
trademark-notice sentence from the Guidelines PDF directly onto the image. Delivered to
Sleven as `hologram_demo_marked.png` — a real rendered output, not a description of one.

**This satisfies the marking rule as specced, not approximated:** logo in the corner, well
over the 50% opacity floor (used 70%), reasonably legible size, trademark notice present and
legible. If this style ships for real, the same compositing step (or its Three.js equivalent)
is the whole marking requirement, solved once and reused on every render.

## Bigger than the Fan Kit — this is a whole-fleet display option, not a 14-ship one

**The Fan Kit's 14 `.ctm` files are not special here.** They're texture-free for the same
reason the project's own 235 `.glb` models are texture-free (`FINDING_ship-models-no-texture-data-verified.md`,
2026-08-07) — no material data, bare UV-mapped geometry. **The hologram render technique
applies identically to the entire existing 235-ship library.** Nothing about it depends on
the file coming from the Fan Kit specifically. Worth being clear about this so nobody scopes
the follow-up work as "the 14 Fan Kit ships" when it's actually "all ship pages."

## The second half of Sleven's idea — a real, separate rights question, not answered here

Sleven's proposal has two parts: the hologram (above, resolved), and a **static reference
photo showing the ship's actual official paint job**, sourced from CIG's own website,
displayed alongside the hologram rather than attempting to texture the model itself. That
second part is a genuinely different question from anything checked today:

- **The Fan Kit does not contain per-ship official photos.** Nothing in today's inventory
  covers this — it's a different asset, from a different place (RSI's own site, not the
  Fan Kit download).
- **What's already on record, verbatim, not reasoned about:** RSI's Terms of Service §XIII.D
  permits reproducing images/graphics/artwork/trademarks/logos "designated for fansite use."
  Whether a product-page ship photo qualifies as within that designation is **not something
  C3 is deciding** — per the standing project rule, Fan Kit / trademark / licensing
  interpretation is Sleven's call alone. Flagging it rather than quietly assuming an answer
  either way.

**Recommendation, not a ruling:** if Sleven confirms product-page ship photos are fair game,
the pairing (hologram + a small "actual paint" reference thumbnail, sourced and credited)
is a clean, buildable pattern. If not, the hologram alone still stands on its own as a real
answer to the original ship-display problem — it doesn't depend on the second half landing.

## Handoff

This is a proof of concept, not a build — C3 doesn't build or test site code. The demo image
and this write-up are meant to save Code build time by confirming the visual direction works
before anyone writes the real Three.js version. Recommend C1 turn this into a work order
scoped to: (1) a reusable hologram-wireframe shader/render path usable across all 235+ ship
models, not just the Fan Kit's 14, (2) the marking composite (logo + notice) built once as a
shared component, (3) the CIG-website-photo pairing held pending Sleven's rights call above.
