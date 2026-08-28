# Update — RULE 14 FIRED. C1 wrote directly into `testing/_src/` at 22:10 and 22:15, and the drift control caught it. Also: Q7 tranche 1 is done.

**2026-08-27 22:28 local · Code (background session)** — the rule 14 event is the
headline, so it goes first.

---

# 1. A SECOND WRITER IN `testing/_src/`

Two files were modified after my last build (21:43) and after tonight's commit
`2fc7008`. **I did not make these edits.**

    testing/_src/cc_viewer.js       22:10:29
    testing/_src/loadout.src.html   22:15:22

Both diffs name their author in their own comments: **"(C1, 2026-08-27 …)"**.

## Hard rule 14

> **`testing/` — Claude Code, and nothing else.** … **C1 does not push files into
> `testing/`** and C2 does not write to the repo at all.

The rule records two previous instances, both on this exact file family:

> a concurrent session rewrote `_layer.src.html` mid-verification, twice in one
> evening. Once it deleted a keybinds overlay and a compliance strip that were
> caught only by a marker check before deploy.

**This is the third.** It was caught the way rule 14 says it must be — *"make an
unauthorised write loud and immediate, and refuse to ship un-provenanced content.
Detect on every build, fail the deploy, name the files that moved"*:

    3. THE COPIED FILES AGAINST _src, EVERY INJECTION DECLARED
      FAIL  loadout.html no longer contains its _src text outside the declared injections
            cc_viewer.js differs from _src/cc_viewer.js
    4. THE ASSEMBLED FILE - index.html, PROVEN BY REBUILDING
      FAIL  and so is every copied file (moved: loadout.html, cc_viewer.js)

**`_verify_deploy_drift.py` is not broken. It is the detector, and this is the
first time it has fired in anger.** I green-lit it at 21:32 tonight; it went red
the moment a write it did not expect landed.

## WHAT was written, because the channel is the problem and the content is not

Both changes are substantial, well-commented, and **quote Sleven's own words**:

**`cc_viewer.js` — the hull becomes translucent.** A new `hullAlpha: 0.86` dial
and a `uAlpha` shader uniform, against *"is there any way we can make it a little
bit more see through, a little bit more transparent"*. `solid` was
`transparent: false`, so the only way to see into a ship was `xray`, a different
look entirely — there was no "a little bit".

**`loadout.src.html` — the panel opens on the side of the screen the marker is
on, and the ship stops moving.** Against *"if I'm looking straight at the ship,
and it would be the ship's right wing but it'd be on my left, it should open the
menu on the left side of the screen."* The old rule opened right and PANNED THE
SHIP to make room, which is the shifting Sleven reported.

**This is authorised work arriving through the wrong door.** I am not reverting
it and I am not going to characterise it as damage. What rule 14 exists to stop
is a write nobody notices, and the point of the detector is that this one did not
go unnoticed.

## The state of play, exactly

- **The deployed testing site (`bbd2a7d7`) does NOT carry either change.**
- **`testing/_deploy` now DOES.** The drift control's section 4 rebuilds by
  design, so at 22:22:32 it rebuilt the payload with C1's `_src` in it. The
  build directory and the served site no longer agree.
- Nothing was deployed, and I have not built since.

## C1's work is GREEN under every control I can point at it

Run after the 22:15 edit, against the current source:

    _verify_stage_panel.mjs      ok   (the panel's own control)
    _verify_ship_page.mjs        ok   242 assertions
    _verify_panel_dismiss.mjs    ok
    _verify_settings_revision.mjs ok
    _verify_disclosure.mjs       ok
    _verify_armour_naming.mjs    ok
    _verify_look_panel.mjs       ok

**So the objection is procedural, not substantive.**

## THE DECISION I AM NOT TAKING ON MY OWN

Sleven's standing instruction is that the day's work reaches the test page the
same day, and this is his own request implemented. Against that, rule 14 says
**refuse to ship un-provenanced content**, and this session neither wrote nor was
handed these changes.

**Say build-and-deploy and I will**, in the next message — the payload is already
rebuilt, the checks are green, and it is one command plus verification. I am not
going to infer it.

---

# 2. Q7, TRANCHE 1 — 11 files labelled

    labelled     22  (7 INDEPENDENT, 15 UNPROVEN)
    unlabelled   75     (was 86)
    malformed     0     GREEN, exit 0

The baseline shrank by exactly 11. The gate fails if a line names a file that no
longer needs it, so the debt list cannot rot into fiction.

**One INDEPENDENT, and it had to earn it:** `_verify_deploy_guards.py` runs the
REAL scripts as subprocesses and reads only their exit codes and printed
refusals. Nothing is imported from them, the payload markers are spelled out
here rather than copied from them, and every input is one the control built — an
absent check file, a check that genuinely exits 1, a receipt planted as failed, a
receipt that is not JSON.

**Ten UNPROVEN, each naming what it could not reach.** The pattern that decided
most of them: `_verify_hardpoint_join.py` and `_verify_hardpoint_alignment.py`
**import the very functions they judge**, so a wrong rule is applied identically
on both sides and cannot be caught by asking it. `_verify_child_markers.py`'s
BEFORE state is the same builder with a switch flipped. `_verify_g3_matcher_delta.py`
diffs the subject's own report against itself. `_verify_dim.mjs` proves the
stylesheet and the theme engine agree with EACH OTHER, which cannot catch both
being wrong together.

**Verified by running all 11.** Ten pass unchanged; the eleventh is
`_verify_deploy_drift.py`, red for the reason in part 1 and not because of its
label.

**Tranche 2** is the seven label and marker controls. Groundwork done:
`_verify_label_threshold.mjs` re-measures its threshold from the fleet each run
and shrinks the stage to make the answer move — that reads INDEPENDENT.
`_verify_marker_absence.mjs` judges the page's ABSENCE MESSAGE against the
generated marker and slot data, which the message logic did not produce.

Nothing committed since `2fc7008`. Nothing deployed. Live site untouched.
