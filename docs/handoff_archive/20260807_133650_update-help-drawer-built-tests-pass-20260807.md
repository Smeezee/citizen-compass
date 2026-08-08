# Update — HELP drawer built, 38 tests pass with negative controls (2026-08-07)

Built into `testing/_src/_layer.src.html` (the `#cc-kb` keybind overlay, which
is what the KEYBINDS tab opens and what ships as `index.html`). Not
`keybinds.src.html` — nothing on the site links to `keybinds.html`, and the
DISPLAY / FEEDBACK tab stack the order places HELP alongside exists only in the
layer.

## The shrink is new behaviour, and it works

Every pre-existing drawer overlays. This one reflows, measured on the built page
at 1920x1080:

    #cc-kb width   closed = 1874px    open = 1454px    delta = 420px

The keyboard board genuinely re-lays-out into the narrower region — keys narrow,
the mouse block moves in, nothing is hidden behind the panel. It uses its own
`body.cc-help-open` class rather than the shared `cc-drawer-open`, which already
means "tabs, get out of the way" to three other tabs.

## What went in

- `#cc-help-tab` — right edge, `z-index:100004` so it stays clickable above the
  keybind overlay (`#cc-kb` is 100003; the other tabs at 100002 are covered by
  it). Persistent, never auto-opens.
- Graph renderer walking `keybind_troubleshooting.json` as a graph: questions
  with `how_to_check` always rendered, the choice node, fixes with steps + note
  + a continue button that follows `then` and names the retest it leads to.
  `end_not_covered` renders as a dead end with no invented route out.
- Back-a-step history — a wrong answer costs one click.
- Vendor matching on `usb_vid` **alone**, parsing the VID out of the Gamepad
  API's `id` string (Chrome `(Vendor: 231d …)` and Firefox `231d-0200-…` forms).
  `known_gotcha` gets its own callout. A vendor with `usb_vid: null`
  (turtle_beach) is skipped by construction, so it can never be auto-matched.
- The one line on the binding screen, under the device selector row, opening the
  drawer at `q_selector_setting`.

## The trap

`keybinds.src.html` is copied verbatim, so the model/thumbnail substitution list
was never the risk here. Two things were:

1. `inject_engine.py` overwrites everything between the DEVICE PANEL boundary
   markers on every build. The drawer is appended well outside that region.
2. `check_deploy_clean.enforce` allows only `index.html` plus the `PAGES`
   outputs, so a sidecar JSON would have failed the deploy guard.

So both JSON payloads are substituted into the page by `build_deploy.py` from
`data-layer/processed/` — one writer, no pasted copy to drift. The build asserts
the placeholder exists, asserts none survives, and the renderer refuses to draw
if it ever sees one. **That guard fired for real on the first build** (the
runtime check named the token itself and tripped its own tripwire), which is
incidental proof the check can fail.

## Tests — 38 pass, every one seen to fail first

`testing/_src/test_help_drawer.js` (playwright/chromium, 1920x1080).

- **Shrink.** Negative control neutralises *only* the reflow rules, leaving the
  drawer opening and visible — i.e. exactly an overlay drawer — and asserts the
  width assertion then fails. A test that only checked "the drawer appeared"
  would pass in that state; this one does not.
- **Graph.** All 17 nodes reachable from start, every link resolves. Negative
  control plants a dangling link, confirms both the break and the node it
  orphans are reported, then confirms removing it returns clean.
- **Fix routing.** All 11 `then`-carrying fixes clicked through the real UI and
  asserted to land on their retest node. `end_not_covered` asserted to offer no
  continue button.
- **Vendor.** 231d → VKB, 3344 → VIRPIL, Firefox-form id resolves too. Unknown
  VID → generic fallback and asserted *not* to name any wrong manufacturer. A
  VKB VID planted as a **product** id asserted not to match. turtle_beach
  asserted unmatchable.
- **Read on screen** at 1920x1080 — question, fix, choice and dead-end nodes.

Screenshots are regenerable via `testing/_src/shot_help_drawer.js`; they were
kept out of the repo deliberately.

`testing/_src/cc_help.inc.html` was the authoring copy and is now spliced into
the layer. Moved to `_to_delete/help_drawer_inc_spliced_20260807/` rather than
deleted (rule 1), so there is exactly one copy of the block.

**Next:** deploy to testing via `scripts/deploy_testing.ps1` and re-run the
tests against the deployed URL, not the local build. Nothing committed yet.
