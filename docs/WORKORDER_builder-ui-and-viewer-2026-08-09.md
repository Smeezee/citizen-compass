# WORK ORDER 2 — putting the builder UI and the 3D viewer on the test site. Written because everything below was in a chat window and nowhere else.

    from      C3 (Cowork), 2026-08-09
    for       C1 — two orders, 2A and 2B, to be turned into prompts for Code
    follows   inbox/WORKORDER_swap-the-exporter-2026-08-09.md  (land that first)
    evidence  claude/FINDING_exporter-round-trip-passes-2026-08-09.md
              claude/FINDING_fixed-hardpoints-derived-2026-08-09.md
    method    read the real build scripts off the project machine — build_deploy.py
              (21,290 bytes), inject_engine.py, check_deploy_clean.py, build.py —
              rather than reasoning from the partial repo copy I had staged.

---

## 0. Why this document exists

Sleven's objection was correct and is the important part of this order: I described the
build-pipeline risk in a chat message and did not write it down. **A chat message is not a
record.** When this session ends, anything that lives only in it is gone, and the next
session rediscovers it — or does not, and walks into the trap.

That is the same failure this project already has on record from WO-UI-01, which existed in
the claude.ai project but not in the repo and so never reached Code.

## 1. First — a correction to what I said in chat

I said `build_deploy.py` "substitutes its own copies of some blocks" into the keybind page,
and that patching the source layer could silently do nothing. **That is too broad and it is
wrong as applied to `keybinds.src.html`.**

I have now read the build. What actually happens:

**`keybinds.src.html` is copied VERBATIM** to `_deploy/keybinds.html` by a `PAGES` list.
No substitution, no templating, no generation. Edits to it land exactly as written.

The substitution machinery — and there is a lot of it — applies to `_layer.src.html`, which
becomes `_deploy/index.html`. That is the main site page, not the keybind page.

**There is exactly one block of `keybinds.src.html` that gets overwritten**, and it is the
one that matters here. `inject_engine.py` runs from inside the build and copies
`device_engine.js` into the page between two fixed boundary markers:

    START   /* ================================================================
               DEVICE PANEL rev 2
    END       if(dev!=="KBM") renderDevice(); });

Anything a person writes between those two markers is destroyed on the next build, without
a warning, because the script's whole purpose is to guarantee one writer. It is not a bug —
it is a guard, and a good one. But it means the device-identity fix has to go into
`device_engine.js` and nowhere else.

The correct statement, which is what should have been in the first order: **the keybind page
is freely editable except for the device panel, which has exactly one writer.** That is a
much smaller trap than I described, and the job is correspondingly smaller.

## 2. The build pipeline, written down

This is the durable part of this document. Verified by reading the files, not inferred.

    python testing/_src/build_deploy.py

runs, in this order:

1. Builds `_deploy/index.html` from `releases/latest.html` + `_layer.src.html`, with
   inlined three.js, an embedded model map read out of `CC_MODELS` in the layer, several
   asserted substitutions, and a password gate injected as the first thing in `<body>`.
   Written with `newline=''` — **do not change that**; it is what makes the artifact
   byte-reproducible across Windows and Linux, and it has already been lost once.
2. Runs `inject_engine.py`, which injects `device_engine.js` into **two** hosts:
   `keybinds.src.html` **and** `_layer.src.html`. Hard-fails if either host is missing or
   if a boundary marker appears anything other than exactly once.
3. Copies `PAGES` verbatim into `_deploy/`:

       keybinds.src.html -> keybinds.html
       loadout.src.html  -> loadout.html
       find.src.html     -> find.html
       kb_modes.gen.js   -> kb_modes.gen.js

   A missing source is a hard failure, deliberately, because a build once dropped
   `keybinds.html` silently and the tab would have 404'd on a deploy reporting success.
4. Runs the **deploy guard** (`check_deploy_clean.enforce`). `_deploy/` is served publicly,
   so the build refuses to finish if anything unexpected is sitting in it. Allowed files are
   `index.html` plus whatever `PAGES` produces — derived from `PAGES`, not duplicated.
   Allowed directories are `images` and `models`.

**Three consequences that decide how both jobs below are done:**

- **Adding a page is one line in `PAGES`.** The deploy guard follows automatically because
  its allowed set is computed from `PAGES`. Add the line, or the build refuses to finish and
  tells you why.
- **A new top-level directory under `_deploy/` will fail the guard.** Only `images` and
  `models` are allowed. Anything else needs a deliberate edit to
  `DEFAULT_ALLOWED_DIRS` — which should be argued for, not slipped in.
- **`_layer.src.html` is a second host for the device engine, and the main page carries its
  own keybind overlay** (`kb_overlay.inc.html`, 40 KB). A device-panel change reaches both
  hosts automatically. **A keybind-UI change made only in `keybinds.src.html` does not.**
  Nobody has flagged this before and it is a live drift risk: the overlay on the index page
  and the standalone keybind page can disagree, and only one of them is under the
  single-writer guard.

---

# ORDER 2A — the builder UI on the live keybind page

## 2A.1 What the page does today, and what it does not

`_deploy/keybinds.html` verifies inputs. Press a button, see it light up. That is real and
useful and it is where Sleven started: *"there's no way to actually help somebody set up
their key binds."*

It contains **no reference to `export`, `.xml` or `ActionMaps` anywhere.** There is no
export path at all. The exporter is not wired to it and never has been.

## 2A.2 What the prototype adds

`Downloads/citizen-compass-keybind-builder.html`, built from
`inbox/` sources, adds four things the live page has none of:

1. **Browsing 691 actions** across 9 categories and 35 described sections, each section
   carrying a plain-English description of what the player is actually programming.
2. **An AXES & DOF reference** — the six degrees of freedom explained, and every Star
   Citizen axis name with its evidence status (`x y z rotz` PROVEN, `slider1` PROVEN from
   the defaults only, `rotx roty slider2` UNATTESTED).
3. **Import, edit, export** of a real mapping file — including the 202-of-247 case that
   matters, clearing a game default.
4. **Device identity** — js1/js2 from an imported profile's GUIDs, else the player's choice
   remembered per VID/PID, else a guess that says it is a guess.

## 2A.3 Where each piece has to land

| piece | file | why |
|---|---|---|
| device identity, stick swap fix, VID/PID memory | **`device_engine.js`** | single writer; anything put in the page between the boundary markers is destroyed on the next build |
| the exporter | **`sc_export.js` added to `PAGES`** | ship it as its own file rather than inlining a copy — inlining creates a second writer, which is the rule-14 shape this project keeps hitting |
| the 691-action browser, sections, DOF page, import/export UI | `keybinds.src.html` | copied verbatim; edits land as written |
| the same, for the index-page overlay | `kb_overlay.inc.html` | **or an explicit decision not to**, recorded — see §2A.5 |
| fonts | decide — see §2A.4 | |

Adding `sc_export.js` to `PAGES` is one line:

    ('sc_export.js', 'sc_export.js'),

and the deploy guard's allowed set updates itself, because it is computed from `PAGES`.

## 2A.4 Two things the prototype does that the site should probably not

**It inlines the fonts.** ~115 KB of base64 woff2 for Saira Condensed, Rajdhani and Chakra
Petch, so the file works with no network. That was right for a downloadable prototype and is
wrong for a page served from a CDN. Either serve them as font files — which needs a new
allowed directory and therefore a deliberate guard edit — or drop to the system stack
already used elsewhere. **I have no opinion worth more than Sleven's here; he asked for the
font to match Star Citizen, so this is his call, not Code's.**

**It inlines `data.json`** — 127 KB of action data. The site already generates
`kb_modes.gen.js` (46.8 KB) from repo data and copies it as its own file. The builder data
should follow that existing pattern rather than invent a second one: generate it from
`data-layer/processed/keybinds_site.json` at build time, ship it as a file, add it to
`PAGES`. **Do not paste a snapshot of the data into the HTML** — that creates a second copy
of information that already has an owner, and it will drift the first time the source data
changes.

## 2A.5 The decision this order cannot make

**Does the keybind overlay on the main index page get the builder too, or does it stay a
verifier and link out to the full page?**

Both are defensible. Duplicating 691 actions and a DOF reference into a 40 KB overlay that
is injected into a 332 KB page is a lot of weight for a hover panel. Leaving them different
is fine if it is *chosen*; it is a defect if it just happens.

Either way, **write the answer down**, because the two files are not under a common writer
and nothing in the build will notice them diverging.

## 2A.6 Acceptance for 2A

1. `python testing/_src/build_deploy.py` completes, including the deploy guard.
2. The device-panel boundary markers still appear exactly once in both hosts — if
   `inject_engine.py` exits non-zero the build stops, so this is proven by the build passing.
3. `git diff` on `keybinds.src.html` shows **no change between the boundary markers**. If it
   does, that work was done in the wrong file and is about to be deleted.
4. On the built page: import `real_export2.xml`, export, and the downloaded file is
   byte-identical to the input. This is the same acceptance test as order 1, run through the
   real page instead of the prototype. It is the one check that proves the wiring, not just
   the module.
5. With two sticks connected in either plug order, after importing a real profile, the page
   agrees with the file about which stick is js1.
6. `_deploy/` contains nothing beyond `index.html`, the `PAGES` outputs, `images/` and
   `models/`.

---

# ORDER 2B — the 3D viewer as a page

## 2B.1 A correction here too: this is less blocked than I said

I told Sleven the viewer was gated on a model-serving decision. Having read the build, that
was overstated.

`_deploy/models/` **already exists, is already an allowed directory, and is already public** —
the password gate covers HTML only, which was established on 2026-08-07 when
`models/100i.glb` was fetched directly and returned binary. The build hard-fails if that
directory is empty. Sleven took the decision to proceed with that known, recorded in
`claude/RULING_ship-models-provenance-and-proceed.md`.

So the viewer introduces **no new exposure question**. That part is settled and I should not
have re-raised it as open — this is the second time I have re-litigated something already
decided, after the test-site static-asset item, and it is a pattern I need to stop.

## 2B.2 What is actually open, which is narrower

**Format and size.** The prototype inlines four hulls as quantised geometry, gzipped and
base64'd, at 13.3 MB in one HTML file. That is fine for four ships handed to one person. It
does not scale to 235, and it is the wrong shape for a page anyway — a browser should fetch
the hull it needs, not all of them.

The site's existing viewer path is `.glb` under `_deploy/models/`, loaded through
GLTFLoader with DRACO. The holo prototype uses Fan Kit `.ctm` geometry, a different source
and a different decoder. **These are two pipelines and the project should not end up
maintaining both by accident.**

The real question for Sleven, and it is a design question rather than a technical one:

> Is the holographic viewer a *different view of the same models the site already ships*, or
> is it a separate thing built on the Fan Kit's 14 hulls?

If the former, the prototype's geometry pipeline is throwaway and the work is to apply the
holo shading and the hardpoint markers to the existing `.glb` loader. If the latter, it is a
second model set with a second decoder, permanently.

**I would put the first well ahead of the second** on the standing priority order —
maintainability first. Two model pipelines is exactly the kind of thing that is cheap today
and expensive for five years. But the Fan Kit hulls are cleaner geometry and Sleven has seen
and liked how they render, so this is his call to take, not mine to assume.

## 2B.3 What is portable from the prototype regardless of that answer

These do not depend on which model set wins, and are worth keeping either way:

- **`inbox/hardpoints.json`** and `inbox/place_hardpoints.py` — positions are derived from
  mount names plus hull shape and are expressed in both centimetres and normalised units,
  so they survive a change of model source.
- **The marker, label and detail-panel behaviour** — hover to name, click to open, far-side
  markers faded, one marker per physical hardpoint with the gun and its gimbal listed
  together, turret guns marked as not pilot-controlled.
- **The honesty line on every hardpoint panel** — that the position is derived and that
  CIG's own field is null for all 53,651 mounts. **This is not decoration and must not be
  dropped in a port.** It is the difference between an estimate and a claim.
- **The Mirror L/R control**, because left/right rests on an assumption about handedness
  that nothing in the meshes can confirm.

## 2B.4 Mechanics, when it is time

- A new page is one line in `PAGES` and a `*.src.html` in `_src/`.
- Geometry must live under `_deploy/models/` — that directory is already allowed. **Any new
  top-level directory fails the deploy guard** and needs a deliberate, argued edit to
  `DEFAULT_ALLOWED_DIRS`.
- Vendored three.js is already in `testing/_src/vendor/three` and is what the site builds
  against. The prototype's postprocessing chain (Pass, CopyShader, ShaderPass, MaskPass,
  EffectComposer, RenderPass, LuminosityHighPassShader, UnrealBloomPass) needs to come from
  that same vendored copy, not from a second download.

---

## 3. Sequencing, and what I would not do

Order 1 first — it is small, it is testable, and it is the thing that is currently broken.

**2A next, and I would split it**: land the exporter wiring and the device-identity fix
first, so the page can import and export a real profile with the sticks identified
correctly. That is the whole of what Sleven originally asked for. The 691-action browser and
the DOF reference are a second pass on top and can be reviewed on their own.

2B last, and only after Sleven answers §2B.2. Writing viewer code before that answer risks
throwing it away.

## 4. Still outstanding, unchanged by any of this

- **No file this tool generated has been loaded by Star Citizen.** Ten minutes of Sleven's
  time and it is the only thing that settles whether any of the keybind work is real.
- **The stuck device-tab bug** needs an F12 console reading from a machine with real sticks.
  It does not reproduce headless, and I will not write a fix on a theory.
- One machine, one stick vendor. Another maker could format the `Product` name differently
  and nothing we have would catch it.
- The hardpoint rules have been run on four hulls. The vocabulary work found 63.6% of mounts
  sit in within-ship name collisions, so the separation pass will do more work on other
  ships and some will hit its "cannot separate" report. That report exists so the failure is
  visible; someone has to actually read it when the other 312 are run.

---

## Commands

Build the test site:

```
python testing/_src/build_deploy.py
```

Check that no work was done inside the injected device-panel block:

```
git --no-optional-locks diff testing/_src/keybinds.src.html
```

Confirm the boundary markers still appear exactly once in each host:

```
grep -c "DEVICE PANEL rev 2" testing/_src/keybinds.src.html testing/_src/_layer.src.html
```

See what the deploy guard would object to, without building:

```
python -c "import sys; sys.path.insert(0,'testing/_src'); from check_deploy_clean import enforce; enforce('testing/_deploy')"
```

Deploy, only when the build is clean:

```
powershell -ExecutionPolicy Bypass -File .\scripts\deploy_testing.ps1
```
