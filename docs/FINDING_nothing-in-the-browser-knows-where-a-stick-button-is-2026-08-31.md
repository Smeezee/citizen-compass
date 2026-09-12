# FINDING — The browser doesn't know where a stick button is. The manufacturers do, and somebody already collected them.

**Desk:** C3 (design/imagination) · **Date:** 2026-08-31 · **Status:** answered, then corrected same day, **and corrected again 2026-09-12**
**On disk 2026-09-12. Existed only in the claude.ai project until then.**
**Question asked:** how certain can we be about accurate button placement on flight sticks, and can we build per-stick panels for popular models?

---

> ## CORRECTION — 2026-09-12. THE JOIN SENTENCE IS WRONG. THE FACTUAL HALF STANDS.
>
> **Everything this document says about what the Gamepad API and WebHID do and do
> not give you is still correct and still worth reading.** So is the tier design,
> so are the other open questions, and so is the mock's honest self-assessment.
> **Two claims in it are now overruled, and open question 2 is closed by a
> harder answer than it asked for.**
>
> **OVERRULED — "The template key format is the join we need," and with it "That
> is the same button number the browser hands us."**
>
> `BUTTON_X` in the Joystick Diagrams template schema is the HID button number.
> **Ruled 2026-09-10 by Architecture, on CIC reading all three makers' own
> documentation to the end: nothing in this project may key a control's identity
> to its HID button number.** Not a coordinate table, not a label, not a lookup.
> **So `BUTTON_X` is not a join. It is a number that does not identify anything.**
>
> **OPEN QUESTION 2 IS CLOSED, AND THE ANSWER IS WORSE THAN THE QUESTION.** That
> question asked whether firmware remapping can change which HID number a control
> reports. **It can — VKB and VIRPIL both store the mapping in the device, so it
> follows the stick into every game, and VKB's own manual tells owners to do it**
> for a reason they will actually meet: *"Some games does not recognize button
> numbers upon this value."*
>
> **But remapping alone would not have killed the idea, and that is the part worth
> carrying.** A remapped stick still has ONE fixed table; this desk would have
> been tempted to ask the pilot once and store it. **What kills it is shift
> state: one physical control reports SEVERAL different numbers depending on the
> layer, so it cannot be stored as a table at all.** VKB layers it, SubSHIFT
> extends it, VIRPIL has the same mechanism across 128 slots.
>
> **WinWing is a measured negative and no exemption is built on it.** SimApp Pro
> binds a physical control to an in-game action, per game — no device-level
> renumbering. One manual read to the end is enough to rule; it is not enough to
> exempt.
>
> **WHAT SURVIVES OF THE TEMPLATE LIBRARY: a picture, and only a picture.** A
> template can still show where a shape sits on a grip. It can never say which
> control that shape is. **And the picture half is separately closed** — Sleven
> ruled 2026-09-08 that stick panels are our own photographs only, and that
> nothing is designed until the HID remap question is measured. **It has now been
> measured, and it came back as a refusal rather than a green light.**
>
> **WHAT REPLACES THE JOIN.** The picture is the thing the pilot CLICKS, not the
> thing we LABEL. The pilot's action supplies the mapping and we never assume it.
> A reconfigured stick then costs us nothing, because we were never reading the
> number.
>
> **Open question 1 (template licensing) is now moot for a further reason:**
> Sleven ruled 2026-09-08 that this project never reads another project's source
> code. Knowing publicly that a thing has been built is sufficient permission to
> build one; their source and their licence terms are not to be touched.
>
> **Open question 3 (index base) is moot** — it was an off-by-one on a number this
> project no longer reads.
>
> **This is a correction block, not a rewrite.** Nothing below is edited. Two of
> the three documents in this 08-31 set are already superseded by the
> own-photographs ruling and are deliberately left alone; **this one is not
> superseded, which is why it gets a correction instead of a banner.**

---

## Correction to the first version of this document

The first version of this file answered "the browser cannot tell us where a button is" and then quietly treated that as "therefore we do not know where the buttons are." Those are different sentences and only the first one is true. The Owner caught it immediately.

Placement data is published. Every serious stick maker ships a manual with a numbered button diagram, and those numbers are the HID button numbers. The research is not blocked; it was never blocked. What follows replaces the earlier framing. The three-tier design below survives, but its weighting was wrong: hand-drawn layouts are the *normal* case for known hardware, not an aspirational top tier.

## What the browser actually gives us — unchanged, still true

MEASURED (Gamepad API surface; WebHID explainer and Chrome capability docs):

Certain: the device name string, vendor ID and product ID, button/axis/hat counts, and live per-frame state of every control.

Absent: any physical placement, per-button name, or control role. `mapping: "standard"` is only ever set for Xbox-style pads; flight sticks always report an empty mapping. WebHID does not rescue this — it exposes `vendorId`, `productId`, `collections`, `reportId`, `usagePage`, `usage` and report item layout, i.e. the binary format of reports. HID usage semantics stop at "Button 1..N" and "X / Y / Rz / Slider / Hat Switch". Nothing in a report descriptor describes spatial arrangement.

That remains correct. The mistake was the inference drawn from it.

## What is actually out there

MEASURED (fetched 2026-08-31):

**Joystick Diagrams** — joystick-diagrams.com, github.com/Rexeh/joystick-diagrams — is an open-source tool that generates hardware-accurate binding reference cards. Relevant facts:

- **84 device templates exist**: 45 bundled with the software, 39 community-created.
- Manufacturer spread: WinWing 28, Virpil 18, VKB Sim 10, Thrustmaster 10, Saitek/Logitech 7, CH Products 3, Total Controls 3, K51 2, Tek Creations 2, Buddy-Fox 1, Microsoft 1, Moza 1.
- Templates are **SVG**, described as "matching the exact physical layout of real HOTAS hardware."
- The project **already parses Star Citizen action maps**, alongside DCS World, MSFS 2020, IL-2 and Joystick Gremlin.
- Project license: **GPL-2.0**.

**The template key format is the join we need.** *(OVERRULED 2026-09-12 — see the correction block above. `BUTTON_X` is not an identity and is not a join.)* From their template schema:
- `BUTTON_X` — "Replace X with the button number on your HID device"
- `POV_X_D` — hat ID and direction, e.g. `POV_1_U`, `POV_1_R`, `POV_1_D`, `POV_1_L`
- `AXIS_X`, `AXIS_Y`, `AXIS_Z`, `AXIS_RX`, `AXIS_RY`, `AXIS_RZ`, `AXIS_SLIDER_N`
- Keys are case-insensitive.

That is the same button number the browser hands us. *(OVERRULED 2026-09-12 — true as a statement about the number, and the number does not identify a control.)* A template is an SVG with a labelled hotspot per HID button — which is structurally identical to what a Citizen Compass stick panel needs to render.

**Also confirmed to exist:** community mapping templates independent of that project, e.g. franklesniak/HOTAS-HOSAS_Control_Mapping_Template_Files, and VKB's own manuals hosted at forum.vkb-sim.pro and vkbcontrollers.com.

## What this changes

The layout problem for known hardware is a **sourcing and licensing** problem, not a research problem and not a drawing problem. For roughly 84 devices the drawing already exists in a machine-readable format keyed by HID button number.

The three-tier design still stands, but reweighted:

**Tier 3 — Drawn.** The default for any device we have a layout for. Sourced from the maker's own manual, or adapted from an existing template library subject to the licence questions below.

**Tier 2 — Pilot-taught, agreed.** Enough independent submissions on the same VID/PID agreeing on the same index-to-control mapping. Shown to everyone, flagged as taught rather than verified.

**Tier 1 — Pilot-taught, one pilot.** Good for that pilot immediately.

**Tier 0 — Unknown.** Honest numbered grid. States what it knows ("18 buttons, 5 axes") and states plainly that it does not know where they are. Bindings still work; only the picture is missing.

The teaching walkthrough is demoted from *the mechanism* to *the fallback and the correction tool*. It still earns its place: it covers the stick released next year, the home-built grip, and — importantly — it is how a wrong or stale drawing gets caught, because a pilot pressing a button and seeing the wrong dot light is instant, self-reporting evidence.

> **2026-09-12 note on the tiers.** The teaching walkthrough is no longer the
> fallback. **Under the button-number ruling it is the only mechanism there is**,
> because the pilot's press is the only thing that can say which control is which.
> The tiers survive as a description of how much of a PICTURE we have; they no
> longer describe how much of an IDENTITY we have, because the answer to that is
> always "whatever the pilot has pressed."

## Open questions — must be closed before anyone builds

1. **Template licensing.** GPL-2.0 on the project; nothing stated about the templates themselves; 39 of 84 community-contributed with their own provenance. Whether we may ship them, adapt them, or must draw our own is unresolved. NOT CHECKED. **MOOT 2026-09-12 — this project does not read another project's source, by Sleven's ruling of 2026-09-08.**
2. **Firmware remapping.** VKB (VKBDevCfg) and VIRPIL (VPC Software Suite) both expose button-mapping configuration to users. Whether that can change *which HID button number a given physical control reports* could not be confirmed from the pages fetched. This is the single biggest technical risk to a fixed drawing and is worth twenty minutes. NOT CHECKED. **CLOSED 2026-09-12 — YES, and shift state is worse than remapping. See the correction block. This question was the right one to ask and it was under-asked.**
3. **Index base.** Manuals and template keys use 1-based HID button numbers; the Gamepad API `buttons[]` array is 0-based. ASSUMED off-by-one; not verified against a live device. **MOOT 2026-09-12 — an off-by-one on a number this project no longer reads.**
4. **Device identification in the template library.** How Joystick Diagrams keys a template to a physical device (GUID, VID/PID, or name string) is not documented on the pages read. NOT CHECKED. **Still not checked, and it no longer matters for identity — only for whether a picture can be found at all.**
5. **Which models matter most to SC pilots right now.** Deliberately still open; needs a live source at scheduling time, not a guess today.

## Mock

`panels.html` — "The Panel Rack". Three tiers side by side with a live press simulation, plus the teaching walkthrough. Every grip shape and button position in it is invented for the mock; none was measured against a real device or a maker's diagram. **The mock still reflects the pre-correction weighting** and oversells the teaching flow relative to drawn layouts. **2026-09-12: that over-selling is now closer to correct than the correction that criticised it.**

> **2026-09-12: `panels.html`, `grip.html` and `stick3d.html` ARE NOT IN THE
> REPOSITORY.** `design/` holds only `ANGLES.md`, `README.md` and
> `keybindings/keys.html`; `data-layer/derived/` has no stick folder. They were built
> in session workspaces and never committed. **Treat them as gone.** The reasoning in
> these three documents is the asset that survived; the mocks did not.

## Checked / not checked

**Checked:** Gamepad API and WebHID surfaces for placement or naming data (absent — this part of the original finding holds); the Joystick Diagrams site and repository for template count, format, manufacturer coverage, key naming convention, supported games, and licence; the existence of independent community template repositories and VKB's own manual hosting.

**Not checked:** everything in Open Questions above. Also not checked: whether any maker publishes a machine-readable layout file directly, which would be cleaner than either drawing or borrowing.

**Not a build order.** For C1 to accept, reject, or schedule.

---

**2026-09-12 — checked for the correction block:** C1's ruling memo read in full off
disk; CIC's underlying documentation reading is cited as CIC's and was not repeated
here. `design/` and `data-layer/derived/` listed directly to confirm the mocks are
absent. **Not checked:** whether any other document in this project still cites
`BUTTON_X` as a join.
