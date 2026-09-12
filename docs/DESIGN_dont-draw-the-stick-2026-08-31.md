# DESIGN — Don't draw the stick

**Desk:** C3 · **Date:** 2026-08-31 · **Companion to:** `FINDING_nothing-in-the-browser-knows-where-a-stick-button-is-2026-08-31.md`
**Question:** given enough time, could we acquire what the actual joystick looks like, rather than rudimentary placeholder art?
**On disk 2026-09-12. Existed only in the claude.ai project until then.**

> **SUPERSEDED TWICE — read this before the body.**
> **1.** The hybrid recommendation below is superseded by
> `FINDING_the-stick-panel-is-the-hardpoint-viewer-2026-08-31.md` — geometry first,
> photo second, drawn art last.
> **2.** Both are then overridden by Sleven's ruling of **2026-09-08: stick panels are
> OUR OWN PHOTOGRAPHS ONLY**, and nothing is designed until the HID remap question is
> measured. **It has since been measured and came back a refusal** — Architecture,
> 2026-09-10: nothing in this project may key a control's identity to its HID button
> number, because shift state makes one control report several.
> **Path 2 below (the 84-template library) is dead as an identity source and survives
> only as a picture.** Path 4 (ask the makers) is untouched by any of it.
> Kept for the acquisition reasoning, which is still the best summary of the options.

## The reframe

Every option below assumes the panel must be a *drawing* of the stick. It doesn't. A photograph of the hardware with the hotspots positioned on top gives a better-looking panel than any vector art we would produce, and it turns an art problem into an acquisition problem — which is far cheaper and which the community can solve for us.

The hotspot layer is pure data: a list of `BUTTON_X` keys with x/y coordinates in the photo's frame. That layer is ours, it is small, it is diffable, and it is completely independent of where the picture came from. Swap the photo later for a nicer one and the coordinates rescale.

> **`BUTTON_X` IS NOT AN IDENTITY** — 2026-09-10 ruling. The hotspot layer stands as
> geometry; what it may NOT do is take its meaning from a HID number. The pilot's press
> supplies the mapping.

This also composes with the teaching walkthrough already designed. A pilot who owns an undrawn stick submits two things: a photo on a plain surface, and sixty seconds of pressing named controls. That is a complete panel for a device nobody at this desk has ever touched.

> **The teaching walkthrough is no longer the fallback. It is the only mechanism there
> is**, because the press is the only thing that can say which control is which.

## The four acquisition paths, with real tradeoffs

**1. Photograph it ourselves or take community submissions.** Best-looking result, cleanest ownership if we or a contributing pilot took the shot. Costs: consistency across devices shot by different people in different light; photos are visually noisy behind data overlays; the reach-zone shading and coverage colouring read worse over a photo than over flat vector. Needs a shooting spec (angle, background, resolution) to avoid a ragged-looking library. **THIS IS THE ONE SLEVEN RULED FOR, 2026-09-08, and it is scoped to our own photographs.**

**2. Reuse the existing template library.** 84 SVG templates already exist and are already keyed by HID button number (see companion finding). Fastest path by a wide margin. Blocked on the licence question, which is genuinely unresolved — GPL-2.0 on the project, nothing stated about the templates themselves, and 39 of the 84 are community-contributed with their own provenance. **DEAD: the key is the HID button number, and 2026-09-08 rules that this project never reads another project's source.**

**3. Draw our own vector art from the makers' published diagrams.** Safe default, fully ours, consistent by construction, and works perfectly with every overlay mode. Slowest. The *layout* is factual; the makers' specific artwork is theirs, so this has to be genuine redrawing rather than tracing. Finite job — the top ten sticks likely cover most SC pilots.

**4. Ask the manufacturers.** VKB, VIRPIL and WinWing are small enthusiast companies with active community forums. Thrustmaster publishes a press page and a brand-assets page, which at least establishes that one maker distributes assets under stated terms (terms not read — NOT CHECKED). Cost is one email each. Best possible outcome, and this project already operates on exactly this footing with CIG's Fan Kit, so it is a familiar and provable posture rather than a novel ask. **STILL LIVE, and it is owner territory — contacting a company is Sleven's alone.**

None of these is legal advice and nobody here is a lawyer; paths 2 and 3 both need a real answer on rights before anyone commits time.

## Recommended shape

Hybrid, and it falls out of the modes already designed:

- **Photo** for the hero panel and the printable/shareable Card view — the two places where looking real matters most.
- **Flat vector** for the dense working views (Bind, Coverage, Reach, Conflicts), where data legibility beats realism and a clean silhouette is genuinely the better tool.

Same coordinate table drives both. The photo and the vector are two skins over one hotspot list, so acquiring either one later never invalidates the other.

Start with path 4 in parallel with path 1, because both are cheap and neither blocks. Path 2 stays parked until the licence question has a real answer. Path 3 is the fallback that always works.

## What this desk can and cannot contribute

**Can:** turn a numbered manual diagram or a clear photograph into an accurate hotspot coordinate table; write the schema, the renderer, the overlay modes, the shooting spec, and the submission flow.

**Cannot:** produce accurate vector art of hardware from a product photo. The grips in `grip.html` are approximations and will stay approximations. The picture has to come from outside this desk.

That division is the actual answer to the question: the coordinates are a code and data job we own, and the likeness is an acquisition job we don't.

## Checked / not checked

**Checked:** that a template library of 84 hardware-accurate SVGs exists and is keyed by HID button number; that Thrustmaster publishes a press page and a brand-assets page.

**Not checked:** the terms on any of those assets; whether VKB or VIRPIL have any stated policy on community reuse of their images or diagrams; whether a photo-based panel actually holds up under the Reach and Coverage overlays at real sizes — that needs building once and looking at it, and this desk cannot judge how it looks.

**Not a build order.** For C1.
