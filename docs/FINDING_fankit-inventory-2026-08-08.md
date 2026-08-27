# FINDING — the Fan Kit is already on the machine. Opened, inventoried, and read end to end. Technical answer: it does NOT solve the hardpoint/skin problem.

    from      C3 (Cowork), 2026-08-08
    for       Sleven + C1
    ask       "go through the fucking fan kit, read every single fucking inch"
    method    Found it already downloaded and extracted at
              C:\Users\david\Downloads\Fankit_2025_11_19\ (plus the zip, 532 MB).
              Listed every file, read the Agreement PDF, the Guidelines PDF, and the
              notes.txt in full. Opened one .ctm model's binary header directly to
              confirm what's actually inside it, not just the filename.

---

## Correction on the record first

Every open-items list in this project (`CURRENT-STATE.md` item 8, and the same framing
repeated in `FINDING_ship-models-no-texture-data-verified.md` and elsewhere) has been
saying "nobody has opened the Fan Kit yet." **That's wrong and it's been wrong for a
while** — the zip's on-disk timestamp is from before today. CIG approval (2026-07-28)
was already correctly recorded as settled. The Fan Kit itself just never got closed out
the same way. Fixing both docs now so this stops resurfacing.

## What's actually in it — full inventory, 395 files, ~550 MB

    01_AUDIO         13 .mp3           official soundtrack cues (Sabre trailer, First
                                        Light, Main Theme, Majesty of Space, Mind Games)
    02_HOLOVIEWERS   14 .ctm           3D ship models — see below, this is the one
                                        that matters
    03_LOGOS         57 .png           manufacturer brand marks (black/white/color),
                                        Made By The Community logos, SQ42 endslate
    04_WALLPAPERS    270 .jpg + 4 .png key-art wallpapers, 4K/tablet/mobile/social sizes
    05_FONTS         15 .otf + 2 .pdf  Banu, Xi'an Xiinthlea, Xi'an Xiinchil in-universe
                                        typefaces, with spec sheets
    06               Fankit_Agreement_2025_11_19.pdf — the license
    07               Fankit_Notes -2025_11_19.txt — the manifest (matches what's on disk)
    08               Fankit_Guidelines.pdf — the how-to-use-it guide

## The 3D models — this is the section that was actually in question

**14 ships, not 235.** Aegis Sabre, Anvil F7C-M Super Hornet, Aopoa Khartu-al, ARGO
MPUV Cargo, Banu Defender, CNOU Mustang Alpha, Crusader Mercury Starrunner, Drake
Cutlass Black, Esperia Blade, Kruger P-52 Merlin, MISC Freelancer MAX, Origin 600i
Explorer, RSI Constellation Aquila, Tumbril Cyclone. A "hero ship per manufacturer"
showcase set, not a catalogue.

**Format is OpenCTM (`.ctm`), not glTF/FBX/OBJ.** Opened `Tumbril Cyclone.ctm`'s raw
binary header directly rather than trusting the extension:

    magic         OCTM
    version       5
    method        MG2 (compressed)
    vertices      80,094
    triangles     144,714
    UV maps       1
    attribute maps 0
    comment       empty (no material name, no metadata)

**One UV map, zero attribute maps, empty comment field. No embedded texture, no
material reference, no node/hierarchy data of any kind** — CTM is a pure-geometry
format; it does not carry any of that even optionally. This is a single static mesh
per file, same as the 235 `.glb`s already on record in
`FINDING_ship-models-no-texture-data-verified.md`. Checked the folder for companion
texture files (any image sitting alongside the `.ctm`s) — none exist; it's 14 mesh
files and nothing else in that folder.

**So the answer to the standing open question is no.** This does not hand the project
real node hierarchies or real textures. It's UV-mapped bare geometry for 14 ships,
same limitation as what's already in the repo, just fewer ships. It does not shortcut
hardpoint placement (still needs a person in Blender either way, which was already
the plan) and it does not solve the skin/livery texture gap. Worth having confirmed
directly rather than continuing to treat it as an unknown, but it's a closed door, not
an open one.

## The logos, wallpapers, fonts, audio — this is the useful half

**57 official manufacturer logos**, each in black/white (most) or black/white/color
(Aegis, Anvil, Consolidated Outland) variants, plus 3 "Made By The Community" logo
files and 2 MISC Mirai sub-brand marks. This is real, usable site-chrome material —
matches what the earlier finding said the Fan Kit would cover "most of."

**274 wallpaper images** at 4K/tablet/mobile/social crops — decorative use, not
data-relevant to anything the site currently needs, but on hand.

**3 in-universe fonts** (Banu, Xi'an ×2) with spec PDFs — stylistic option for the
site if ever wanted, unused currently.

**13 official soundtrack tracks** — no current use case identified.

## What the Guidelines document actually says — recorded verbatim, not interpreted

This directly answers the standing "image-marking vs atlas conflict" open item
(blocked on "reading what the Fan Kit's own docs say about applying the mark").
Quoting CIG's own guide, not my reading of it:

- **The "Made By The Community" logo** goes "to the corner of any images with no
  less than 50% opacity and use a reasonably legible size." Two logo variants
  supplied (black-ring/white-ring).
- **A required trademark notice** must accompany it: *"Star Citizen®, Roberts Space
  Industries® and Cloud Imperium® are registered trademarks of Cloud Imperium Rights
  LLC."* Minimum 10-point font. On a website: "displayed on the home page, on a
  navigation area that is always visible regardless of scrolling, or both."
- **An alternate text-only option exists** ("This is an unofficial Star Citizen Fan
  Site" / "Made By The Community" / "This is a Fan Made item") but the guide states
  it "must be approved by our legal department" via a request submitted on the Fan
  Kit site before use — that approval step is not optional per the document's own
  wording.
- **What not to do, stated as a hard list, applied to "all images and assets":** no
  recoloring, no flipping/reversing, no distorting, no outlines or drop shadows, no
  patterns/textures/effects applied on top.

Not drawing a conclusion about what this means for the atlas/sprite-sheet approach —
that's the call the standing rule reserves for Sleven — but the actual constraint is
now on record instead of "nobody's read it yet": legibility and 50% opacity are the
named requirements, not a fixed pixel size, and the exact notice text is specified
above word for word.

## The Agreement — facts only, no interpretation

Read in full, all 16 clauses. Recording the ones that are operationally relevant, not
opining on any of them:

- Non-commercial use only (2i) — already the project's own position, consistent.
- Revocable at CIG's sole discretion at any time (6).
- CIG can demand removal of any use it disapproves of (2h).
- Must give CIG the site's URL(s) so they can verify compliance (2k) — the project's
  2(k) notification history is exactly this clause.
- Must preserve any watermarks/notices in Fan Kit assets, unaltered (2j).
- No sublicense, not transferable (13). No rights to any other CIG property beyond
  what's literally in the kit (12).
- Liability capped at $10 total (4).
- Governed by California law, Los Angeles County venue (9).

This is not new information relative to what CIG generally states, but it's now
actually sourced from the document itself rather than inferred from the FAQ, per the
project's own "record what CIG has said, verbatim" rule.

## Bottom line

The Fan Kit was already sitting on the machine, already downloaded, already
extractable — that part of the open-items list was stale, not accurate, and it's
fixed now. Read every file name, both PDFs, the notes file in full, and opened one
model's actual bytes to check the claim rather than the label. Result: the branding
assets (logos, the exact notice text, the exact marking rule) are genuinely useful and
now on record precisely. The 3D models are not the hardpoint/skin answer — 14 ships,
texture-free bare geometry, same ceiling as what's already in the repo.
