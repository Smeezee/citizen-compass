# FINDING — The stick panel is the hardpoint viewer with a different mesh

**Desk:** C3 · **Date:** 2026-08-31
**Companions:** `FINDING_nothing-in-the-browser-knows-where-a-stick-button-is-2026-08-31.md`, `DESIGN_dont-draw-the-stick-2026-08-31.md`
**On disk 2026-09-12. Existed only in the claude.ai project until then.**

> **THE RECOMMENDATION IS SUPERSEDED. THE STRUCTURAL INSIGHT IS NOT.**
> "Geometry first" is overridden by Sleven's ruling of **2026-09-08 — our own
> photographs only.** Community 3D models, their licences and their rendering are off
> the table with it.
> **What survives, and is the most reusable thing this desk has produced:** a flight
> stick is the ship hardpoint viewer with a different mesh, and the same rule that
> decided the ship viewer decides it the same way.

The Owner said 3D-printed stick parts exist and we should be able to find what we need. He was right, and it changes the recommendation in the companion design.

## What is actually out there

MEASURED (fetched 2026-08-31):

- **Cults3D** lists **23 free VKB models** and **34 free VIRPIL models** under its brand tags.
- **Printables** has a VKB tag carrying community models including a **Gladiator NXT base**, plus VKB-to-VIRPIL/Thrustmaster mechanical interfaces and desk-mount adapters for Gunfighter III and Gladiator-K.
- **GrabCAD** hosts a VIRPIL library — GrabCAD is a CAD library, so STEP rather than mesh-only.
- The **HOTAS/HOSAS/SIMPIT wiki** maintains a 3D Printing page as a community index.
- Complete open sticks exist with source, not just meshes: **Akaki-Joystick** (GPL-3.0, STL, includes a grip with face buttons, thumb button and trigger) and **OpenJoystick** (GPL, ~86% OpenSCAD — *parametric source*, which is text and scriptable, not a frozen mesh). Also **The Hawks 6DOF HOSAS** on Printables (free STL, grip + buttons + base; the page states no formal licence, only Prusa's site terms).

These exist because people print mounts, adapters and extensions, and you cannot design a mount without modelling the real hardware accurately. The measuring work has already been done by somebody.

**And from the makers themselves:** VIRPIL's own downloads page already carries a **3D Files** section (currently throttle detents) and publishes **"Configurator 2.0 Control Layouts"** for named grips — WarBRD, CDT-AERO-L, CDT-AERO-R. If those layouts are the physical-control-to-button-number mapping, that is the manufacturer publishing exactly what this whole thread has been chasing, for free, themselves. NOT CHECKED — twenty minutes, highest value per minute of anything in these three documents.

> **2026-09-10 — this is now MOOT as a mapping source.** CIC read VIRPIL's, VKB's and
> WinWing's documentation to the end. VIRPIL layers shift state across 128 slots, so
> even a published layout describes one layer of a control that reports several
> numbers. **There is no fixed table to publish.**

## Why geometry beats both a photo and a drawing

A model gives us the two things we needed at once: exact placement, and a picture we own outright. Rendered ourselves, it is our asset — our angle, our lighting, our colours, consistent across the whole library, with no photo licensing, no tracing, no ragged community snapshots shot in different rooms.

## The part that matters most

**This is not a new pipeline. It is the ship hardpoint viewer.**

The standing decision on ships is Blender-placed hardpoint markers plus Three.js raycasting, restricted to physically visible and mountable hardpoints, with internal components handled by a menu-driven overlay instead. A flight stick is the same problem with a different mesh:

- Physical buttons, hats, triggers and levers **are** the visible, walked-up-to hardpoints. Markers in world space, picked by raycast.
- Firmware configuration, axis curves, deadzones and shift layers are the **internal components** — not physically pointed at, so they belong in the menu overlay, exactly as power plants and coolers do.

The same rule that decided the ship viewer decides the stick viewer, and it decides it the same way. Blender is already installed on the Owner's machine; Three.js is already in the stack. Adopting this adds a mesh and a marker table, not an architecture.

It also makes the ergonomic check literal rather than argued: with real geometry, "can the thumb reach this without regripping" is a distance in the model, not my opinion.

## Honest limits

1. **A community-printed stick is not a Gladiator.** Its buttons are somewhere else. Open models mostly buy us an excellent *generic* grip — which is a large upgrade to the unknown/taught tiers, where the fallback stops being a numbered grid and becomes a real rendered object — but it does not by itself deliver panels for named popular models.
2. **Mount and adapter models often model the base and the mounting interface, not the grip's button faces.** Each model has to be opened and checked for what it actually contains.
3. **Licences vary per model and per host** — GPL-3.0 on Akaki, GPL on OpenJoystick, unstated on at least one Printables model, Creative Commons variants elsewhere, GrabCAD's own terms. Whether rendering a GPL or share-alike model creates obligations on the *rendered image* is a real question and is not mine to answer. Nobody here is a lawyer. Owner territory. **ANSWERED 2026-09-08: none of them are used.**
4. **A mesh is not a button map.** Geometry tells us where a shape is; it does not say which HID index that shape reports. The manual, the maker's control layout, or the teaching walkthrough still supplies that. Geometry and identity are two separate acquisitions. **This limit turned out to be the whole story — see the 09-10 ruling.**

## Revised recommendation

Supersedes the hybrid in `DESIGN_dont-draw-the-stick`:

- **Geometry first**, photo second, hand-drawn art last. A model serves every view — hero, card, and the dense working overlays — from one asset, and it is the only option that also answers reach questions honestly.
- **Chase VIRPIL's published control layouts before anything else.** If the makers already publish the mapping, most of the sourcing argument evaporates.
- **The generic open-source grip is worth adopting on its own merits**, independent of any named model, because it fixes the worst-looking state in the whole feature — the stick we have never seen.
- Community contribution still closes the long tail, but the ask changes: not just a photo and a walkthrough, but "you own this stick and you already modelled it for a mount — share the model."

> **ALL FOUR BULLETS ARE SUPERSEDED by the 2026-09-08 own-photographs ruling and the
> 2026-09-10 button-number ruling.** Kept verbatim so the reasoning is legible, not so
> anybody acts on it.

## Mock

`stick3d.html` — "The Stick in Three Dimensions". Rotatable, markers picked by raycast, four overlay modes, ghost-the-body toggle. **The mesh is procedural — generated from primitives.** It is not any real product, nothing was downloaded or traced, and it exists only to show the viewer works and that markers sit in world space on a stick exactly as they do on a hull.

> **2026-09-12: `stick3d.html`, `panels.html` and `grip.html` are NOT in the repository.**
> They were built in a session workspace and never committed. **Treat them as gone
> unless a copy turns up.** Nothing depends on them — the reasoning above is the asset —
> but a later reader should not go looking for files that are not there.

## Checked / not checked

**CHECKED:** Cults3D VKB and VIRPIL tag counts; Printables VKB tag and named adapter/base models; the existence of a GrabCAD VIRPIL library; the HOTAS wiki 3D printing page; Akaki-Joystick licence (GPL-3.0) and contents; OpenJoystick licence (GPL) and that it is OpenSCAD source; The Hawks model contents and its lack of a stated licence; VIRPIL's downloads page contents.

**NOT CHECKED:** whether VIRPIL's Control Layouts are the button mapping (do this first); what any individual model file actually contains; per-model licence terms and whether they reach a rendered image; whether VKB has ever released CAD or dimensions (a forum thread asking for Gunfighter STEP files exists but could not be read — robots); whether maker configuration software can reassign HID button numbers, which remains the biggest technical risk to any fixed layout and is still open from the first finding. **THAT LAST ONE IS NOW CLOSED — yes, and shift state is worse than reassignment.**

**Not a build order.** For C1.
