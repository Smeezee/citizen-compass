# UPDATE — testing layer rolled back; three fixes missing; one new change applied

From Claude-02 (Cowork brainstorming session), 2026-08-01/02. Read-only
investigation plus one applied edit to `testing/_layer.html`. No commits, no
pushes. Live site, database and snapshots untouched.

A fuller write-up was delivered to Sleven as a single file and may be pasted to
whoever picks this up. The essentials are duplicated here so this channel is not
dependent on that being relayed.

## The blocking problem

`testing/_layer.html` on disk is an older version than the archive record
describes. Three fixes dated 2026-08-01 are not present.

**1. Temporal-dead-zone crash — this is why nothing works.**
`apply();` is called at line 628. `let renderer,scene,camera,controls,current,raf,loader;`
is declared at line 631. `apply()` at line 543 does
`if(typeof renderer!=='undefined' && renderer) setTimeout(size,80);`.
`typeof` on a `let` before declaration throws a ReferenceError, so `apply()`
dies at load and every statement after line 628 never runs — 3D viewer boot,
`decorate()`, row wiring, all of it. Fix: hoist the declaration above the call.

**2. Row matching reverted to exact string compare.**
`decorate()` uses `SHIPS.find(s=>s.name===label)`. `grep -c 'CC_NORM\|CC_LOOKUP'`
returns 0 — the normalised lookup index is gone.

**3. RSI links still in matrix rows.**
`releases/latest.html` carries 233 `robertsspaceindustries.com` references
including a per-ship pledge URL per row. `decorate()` wraps `td.innerHTML`
without stripping anything, so the anchor survives inside the clickable span and
nothing guards a click landing on it. `CC_RSI` is absent.

Items 2 and 3 as described above are RECONSTRUCTED from the archive entries
`20260801_115134_update_testing_layer_bugfixes_2026-08-01.md` and
`20260801_125845_update_models_compressed_and_preview_2026-08-01.md`. Those
entries are authoritative — read them and prefer their wording over this note.
Item 1 is exact: line numbers and mechanism verified directly on disk.

**Inference, labelled:** the page has not been run. Reasoning from code, with
`apply()` throwing, `decorate()` never executes, so rows are never rewritten and
the original page renders untouched — original RSI links live, names not
clickable, no viewer. That matches the symptom reported after a rebuild. Strong
hypothesis, not a confirmed diagnosis.

**How it got rolled back is unknown and was not guessed at.** Two relevant facts:
`testing/_deploy/` was built from the fixed version and still works, which is why
the shared link is unaffected; and `_layer.html` was modified at 01:06 UTC
2026-08-02, about four minutes before this session opened it. Check for a
concurrent editor before starting.

## A new change is already in that file — do not clobber it

Applied 01:10 UTC 2026-08-02: the ship still image now remains as a dimmed,
blurred backdrop behind the 3D model instead of fading to zero on model load.

**Restore the three fixes ON TOP of the current file. Do not revert to a backup —
that silently removes this.**

Six replacements, each verified to match exactly once before applying:
tuning vars `:root{ --cc-still-bg-opacity:.20; --cc-still-bg-blur:10px; }` above
the viewer CSS; `#cc-canvas` gains `z-index:1` and `#cc-still` gains `z-index:2`;
new rule `#cc-still.cc-bg` applying the vars with `object-fit:cover`, `padding:0`,
`z-index:0` and `transform:scale(1.08)` to stop blur bleeding at the stage edge;
opening a ship clears `cc-bg` and the `ccBroken` flag; `still.onerror` sets
`ccBroken`; on model load `cc-bg` is applied unless the image failed.

Layering is explicit rather than DOM-order dependent, so load-time appearance is
unchanged. Canvas is `alpha:true` with no `scene.background`, so it shows through.

Verified headlessly against CSS extracted from the edited file rather than
retyped: during load opacity 1 / contain / 24px unchanged; after load 0.2 /
blur(10px) / cover; `elementFromPoint` at stage centre returns `cc-canvas` in
both states so the backdrop never intercepts input; no layout shift; missing
image gives opacity 0, no class, no broken icon; reopening resets cleanly.
NOT verified: behaviour with a real GLB in a real browser.

## Order of work

1. Check nothing else is editing `testing/_layer.html`.
2. Restore fix 1. This alone un-breaks the layer.
3. Restore fixes 2 and 3 from the two archive entries.
4. Rebuild with `python build.py` from `testing/`.
5. Verify in a browser on the local server before republishing anything.

HARD RULE 12 applies with force here — these are the exact fixes previously
reported done that are not present. Do not report them fixed from reading a diff.
Confirm no error at load, a row click opening the detail panel rather than
navigating to RSI, and a ship whose rendered name differs from `SHIPS[].name`
still matching.

## Record, do not act — image provenance

241 `image.webp` files across 241 folders in `sc-ships/`, all dated 2026-07-27,
with a second copy of all 241 in `testing/_deploy/images`. All local; no external
URL dependency.

There is no record of where any of them came from — no licence file, no
attribution, no manifest, no per-image metadata. The only four `MODEL_SOURCE.txt`
files document models copied between ships sharing a chassis and say nothing
about images.

Flagged without interpretation: the Fan Kit Agreement prohibits recoloring,
distorting or outlining CIG assets. The backdrop change applies blur and reduces
opacity. Whether that constitutes distortion is a question for CIG legal, and it
cannot be answered until someone establishes what these images are. The blur is
one line to revert; 241 images of unknown origin already sitting in a
public-facing package is a standing question regardless.

## Boundaries

`static/preview.html`, `releases/latest.html` and `testing/_deploy/` untouched.
No commits, no pushes. Only `testing/_layer.html` and inbox notes were written.
