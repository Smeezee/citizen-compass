# UPDATE — KEYBINDS tab wired into the testing site

Claude-02, 2026-08-02. Follows the earlier note that added the keybinding tester
page. No commits, no pushes.

## What changed

A teal `KEYBINDS` tab was added to the right edge of the testing layer, styled to
match the existing FEEDBACK tab, linking to `keybinds.html`. Injected immediately
before the `cc-fb-tab` button, with its own scoped CSS block and a mobile
fallback that drops it to the bottom bar beside FEEDBACK.

Element id `cc-kb-tab`. Six occurrences per file after injection.

## Files touched — including build outputs, deliberately

| file | why |
|---|---|
| `testing/_src/_layer.src.html` | source of truth — survives rebuilds |
| `testing/_deploy/index.html` | build output — edited so the site is pushable NOW without a rebuild |
| `testing/_layer.html` | build output — edited so localhost matches |
| `testing/index.html` | build output — same |

**The three build outputs were edited on purpose**, against the standing rule
that they are generated and not hand-edited. Reason: the operator needs to push
the deploy bundle immediately and should not have to run a build first. The
source file carries the same change, so a rebuild reproduces it rather than
losing it. If a rebuild happens before anyone reads this, nothing is lost.

Verified after injection: all four files contain the tab.

## Still outstanding from the previous note

`build_full.py` does not copy `keybinds.html` into `_deploy/`. The page is there
now because it was placed manually. **The next full build will drop it, silently
and without error**, leaving the KEYBINDS tab pointing at a 404.

One copy step in `build_full.py` fixes it: `keybinds.src.html` -> `_deploy/keybinds.html`.
Not edited here — build scripts are owned elsewhere.

## Page state

Five mode tabs across the top: FLIGHT and ON FOOT are populated and working;
E.V.A., VEHICLE and CAMERA render a plain "not entered yet" panel rather than
being hidden, so the intended shape is visible. Device row below: Keyboard/Mouse
active, Gamepad and Joystick greyed out.

Live input works — real keys, mouse buttons 1-5, wheel. Left Alt / Left Shift /
Right Alt switch modifier layers live. Press timing classifies TAP, HOLD and
DOUBLE TAP and warns when a hold-bound action was only tapped.

Data is still transcribed by eye from screenshots and unverified. Entries that
could not be read confidently carry an orange `?`. This is replaced wholesale
once `defaultProfile.xml` is extracted.

## Boundaries

`static/preview.html` and `releases/latest.html` untouched. Database, snapshots
and live site untouched. No commits, no pushes.
