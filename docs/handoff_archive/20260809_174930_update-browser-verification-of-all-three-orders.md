# Update — the three orders verified in a real browser, and the three.js revision finally confirmed

Every one of the three orders shipped with the same caveat: *nothing has been
seen in a browser*. Chrome and Edge are both installed on this machine, so that
caveat did not have to stand. Headless Chrome, against the **built `_deploy`
files**, not the sources.

## Pass 2's action browser — VERIFIED, was only code-checked before

Rendered `_deploy/keybinds.html` and parsed the resulting DOM:

```
section headers in #kbblist : 35
action rows in #kbblist     : 691
per-action descriptions     : 208
unbound cells               : 330
DOF rows                    : 8   (5 PROVEN / 3 UNATTESTED)
header line                 : "691 actions, 9 categories, 35 sections
                               (105 carry no category, 9 no section - both listed, not dropped)"
count line                  : "691 of 691 shown"
```

Every number matches what the generator reported. Acceptance 3's browsing half is
now observed rather than inferred. **The typefaces remain the one unmet part** —
still no font files.

## Pass 1's export — VERIFIED IN A BROWSER, including the two things Node could not test

This is the one I explicitly flagged: the Node proof could not exercise
`FileReader` or `Blob`, and those are the difference between "the module
round-trips" and "the button works". A harness in the scratchpad (not in the
repo) drove the **real** ones against the **deployed** `sc_export.js` and
`kb_modes.gen.js`:

```
SCX loaded, KB_MAP_ORDER has 50 maps
real_export.xml : FileReader preserved the bytes: true
real_export.xml : parsed 247 binds, 3 device options
real_export.xml : BUILD === ORIGINAL: true
real_export.xml : AFTER Blob ROUND TRIP === ORIGINAL: true
real_export2.xml: FileReader preserved the bytes: true
real_export2.xml: BUILD === ORIGINAL: true
real_export2.xml: AFTER Blob ROUND TRIP === ORIGINAL: true
```

Native browser `DOMParser`, real `FileReader.readAsText`, real `Blob` — bytes
preserved end to end, both fixtures.

**Proven able to fail, per rule 12.** Corrupting a single tag (`<ActionMaps` ->
`<ActionMapZ`) flipped both files to `false` and the harness named the exact
line and both versions of it. A comparison that has never failed is not a
comparison.

What is still not covered: nobody has physically clicked the input and picked a
file from a file dialog. Everything either side of that click is now proven.

## 2B's holo viewer — PARTLY verified, and the gap is named rather than papered over

`_deploy/holo.html` in headless Chrome:

- WebGL canvas created ✅
- both displayable ships listed in the picker ✅
- the "no model in the library" panel renders, naming Cutlass Black and
  Constellation Aquila ✅
- **the ship model never finishes loading** — status stays on `loading Sabre.glb`

A probe to tell a page bug from an environment limit, because from the outside
they look the same:

```
THREE.REVISION                     : 128
fetch models/Sabre.glb             : OK, 1,772,312 bytes
GLTFLoader without DRACO           : errored exactly as it should -
                                     "No DRACOLoader instance provided"
GLTFLoader WITH the page's wiring  : TIMED OUT - the draco worker never resolved
```

So the bytes are reachable, the loader is alive, and the file genuinely needs the
decoder. **The DRACO worker does not resolve under headless Chrome.** That is a
known shape of headless limitation, and the page's `_loadLibrary` override is
**functionally identical to the one `index.html` ships** — same branches, same
base64 decode, differing only in indentation and `var` vs `const`, which I
checked directly after an over-strict string comparison said otherwise.

**I am not claiming the viewer renders a ship.** The evidence says the wiring
matches a mechanism that works in production and that nothing upstream of the
worker is broken. It does not say a hull appears on screen. That still needs one
real browser session.

## The three.js revision is confirmed: r128

The 2B order flagged this as unverified and I reported that I could not confirm
it — `vendor/three/build/` holds only `three.min.js` and my grep for a REVISION
string found nothing. **The browser answers it directly: `THREE.REVISION` is
`128`,** matching the `three@0.128.0` CDN tag in `_layer.src.html`. Correcting my
earlier "unverified, so not claimed".

That also settles the postprocessing question if it is ever revisited: the files
would need to come from **r128 specifically**, which is now a checked fact rather
than an inference from a script tag.

## Net effect on the three orders

| | before | now |
|---|---|---|
| pass 1 acceptance 3 | proven in Node only | **proven in a browser**, FileReader + Blob included |
| pass 2 acceptance 3 | code-verified | **691/35/208 observed in the DOM**; fonts still unmet |
| 2B acceptance 2 | not verified | page initialises; **model render still unverified**, cause isolated |
| 2B revision | unverified | **r128 confirmed** |

Harnesses live in the session scratchpad, not the repo — they are diagnostics,
not deliverables. Nothing staged, nothing committed.
