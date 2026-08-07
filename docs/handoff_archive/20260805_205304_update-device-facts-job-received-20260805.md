# Update — received: sourced flight-stick fact file for the keybind page

**When:** 2026-08-05

Logging on arrival per hard rule 13. **Not started** — the MyBook backup is in
flight and was explicitly "stop at the first failure", so this queues behind it.

## The job

Build `data-layer/raw/devices/device_facts.json` plus
`device_facts_findings.md`, so the keybind page can recognise a stick from its
browser gamepad id, name each control correctly, and draw it in the right place.

Seven devices in priority order: VKB Gladiator NXT EVO (**every** variant —
Standard, SCE, Omni Throttle, Premium, left and right hand), VIRPIL
Constellation ALPHA Prime, VIRPIL CDT-AEROMAX, Thrustmaster T.16000M,
Thrustmaster SOL-R 2, Turtle Beach VelocityOne Flightstick II, Winctrl Ursa
Minor.

Five fact classes each: **A** USB identity (VID/PID hex per variant and firmware
mode, plus verbatim `navigator.getGamepads()[i].id` strings — the exact wording
matters more than the numbers because that string is what we match on), **B**
default button numbering with an explicit statement of 1-based (VKB docs) vs
0-based (browser) and which firmware/VKBDevCfg profile it belongs to, **C** axis
order including whether each hat is an HID hat switch or four buttons, **D**
plain-words control inventory, **E** geometry as 0–1 fractions of each face from
the vendor's own layout template.

## The governing rule, noted

**Blank beats wrong.** Every field carries a source URL; anything unsourceable
is `null` with a `_missing` note recording what was looked for and where. A
blank renders as "press it to identify" and is harmless; a wrong number
silently mislabels a control and nobody ever finds out.

That is the same standard already applied to the collector's Game.log parser
(verified vs unverified patterns, null plus a reason rather than a plausible
default) and to job 2's `range_gm`. Consistent with hard rule 11.

## Constraints I will observe

- **No vendor images, 3D models or manuals downloaded into the repo.** Facts and
  coordinates only — we are not licensed to republish their artwork. Geometry is
  to be read from published templates and recorded as fractions, describing the
  positions in JSON without pulling the image.
- **Do not touch `viewer/profiles.js`, anything under `testing/`, or any built
  HTML.** One writer per artifact — hard rule 14. `testing/` is explicitly
  Claude-Code-only-via-C1 in CLAUDE.md, and this job is not that path.
- Primary sources preferred; community sources allowed but that entry is marked
  `confidence: "community"`.
- If a fetch is blocked, that is the answer — hard rule 9. I will not route
  around it via a mirror, cache or archive; I will record it as not found and
  say where I looked.

**Next:** finish and verify the backup, then start this.
