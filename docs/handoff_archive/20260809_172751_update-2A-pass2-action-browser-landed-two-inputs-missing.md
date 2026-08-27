# Update — 2A pass 2: browser, DOF table and link-out landed. Two inputs do not exist and were not invented.

Pass 2 is built and green where it can be. **Two of the order's inputs are not in
this repo**, so two acceptance points are NOT MET rather than worked around.

## What landed

**`build_kb_actions.py`** — new generator at repo root, same pattern as
`build_keybind_modes.py`, reading `data-layer/processed/keybinds_site.json` and
writing `testing/_src/kb_actions.gen.js` (110 KB) with `encoding="utf-8",
newline="\n"`. Added to `PAGES` and to `DEFAULT_ALLOWED_FILES`. Nothing pasted
into the page.

The order's figures are exact and fall straight out of the data:

```
691 labelled actions
  9 named categories  + 1 Uncategorised bucket (105 actions)
 34 named sections    + 1 Ungrouped bucket       (9 actions)  = 35 sections
208 of 691 actions carry a per-action description
```

**Both buckets are named and listed, not dropped.** 105 actions carry no
category and 9 carry no section. Filtering them out would have shown 586 of 691
and looked tidy. The page states the counts explicitly — including that the
Uncategorised bucket is *not* a tenth category — so nobody has to reverse-engineer
why the numbers do not add up.

**The axis evidence table**, corrected per FINDING §8: `x y z rotz` PROVEN,
`slider1` PROVEN (shipped defaults only), `rotx roty slider2` **UNATTESTED**.
The page states in prose that **UNATTESTED is not rejected** — never seen in any
file read so far, which is a weaker claim than "the game refuses it" and is the
only one the evidence supports.

**The overlay links out.** One `<a href="keybinds.html">` added to
`_layer.src.html`'s tester overlay. Verified it contains no `KB_ACTIONS`, no DOF
content and no import/export UI.

**Font plumbing**, minus the fonts. `@font-face` rules pointing at `fonts/`,
applied to **chrome only**, with full fallbacks so the page is correct and
readable today. `fonts` added to `DEFAULT_ALLOWED_DIRS` as the deliberate,
argued guard edit the order asked for, with the reasoning in a comment beside it.

## NOT MET, and why — neither was worked around

**1. The font files do not exist and I could not obtain them.**

Acceptance 2 ("`_deploy/fonts/` contains the three typefaces") is **NOT MET**.
No font files are anywhere in this repo. Getting them means a network fetch plus
a redistribution decision, and the second is not mine: all three families are, to
my knowledge, under the SIL Open Font License, which requires the licence text to
travel with them. **Licensing is Sleven's alone (rule 8), so I reported the
requirement rather than satisfying it.**

`_deploy/fonts/README.txt` names the four exact filenames the page expects and
the OFL obligation. Drop the files in and it works — no code change needed.

Acceptance 3 is therefore **half met**: the browser works, the typefaces do not
render yet.

**2. The 35 section descriptions do not exist in repo data.**

`keybinds_site.json` carries a per-**action** `desc` on 208 rows and **no
section-level description field at all**. The descriptions the order refers to
live in a prototype that is not in this repo — I searched.

**Thirty-five plausible sentences written by me would be indistinguishable from
real ones and impossible to audit later.** So `KB_SECTION_DESC` is emitted empty
and the page renders a section description only when one exists. When the
prototype's text turns up, it drops into the generator and the page picks it up
with no further change.

## One more correction to the order

**There is no copy step for `images/` or `models/` to mirror.** The order says to
find the existing copy logic and match it. There isn't any — both directories
live persistently in `_deploy/` and the build *reads* them from there
(`build_deploy.py:35-37` globs `_deploy/models/*.glb` and refuses to build if it
is empty). So `fonts/` needs no copy step either, and inventing one would have
been the second mechanism the order explicitly warns against.

## And a correction to something I said earlier today

In `RULING_holo-viewer-models-keybind-overlay-and-fonts-2026-08-09.md` I wrote
that marking the builder's content `.cc-ui` would exempt it from the
accessibility font switcher. **That was wrong**: the switcher lives in
`_layer.src.html` and `keybinds.src.html` has none — I checked, the count is
zero. The `.cc-ui` conflict does not arise on that page.

**The underlying concern is real but sharper than I stated.** Because that page
has *no* font control at all, whatever the 691-row table is set in is what every
reader gets, with no escape. Saira Condensed is a condensed face and harder to
read at low vision. So SC faces are on chrome only and the reference table stays
on the system stack — same recommendation, correct reasoning.

## Acceptance

| # | | |
|---|---|---|
| 1 | build completes incl. guard | ✅ |
| 2 | `_deploy/fonts/` allowed by `DEFAULT_ALLOWED_DIRS` | ✅ — but **contains no typefaces, NOT MET** |
| 3 | renders in SC typefaces / browses 691 across 9 cats, 35 sections | ⚠️ browser ✅, typefaces ❌, **section descriptions ❌ — no source data** |
| 4 | DOF shows the corrected table | ✅ |
| 5 | `_layer.src.html` shows a link and nothing else | ✅ |
| 6 | `device_engine.js` unchanged by this pass | ✅ |
| 7 | `_deploy/` contents exact | ✅ `index.html`, 6 PAGES outputs, `images/`, `models/`, `fonts/` |

No regression: `roundtrip.js` **ALL CHECKS PASSED**, and both fixtures still
round-trip **byte-identical** through the rebuilt `_deploy` artifacts.

## State

Nothing staged, nothing committed, no `git add -A`. Deploy script not run.
**2B is not started.**
