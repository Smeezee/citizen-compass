# Update — 2A pass 1 complete, and a build defect that was shipping stale code silently

Pass 1 landed. The headline is not the wiring — it's what checking the *built*
output rather than the source turned up.

## The build was shipping a stale device panel, and reporting success

`build_deploy.py` ran `inject_engine.py` **after** `index.html` had already been
written. `_layer.src.html` is read into `layer` at line 59; `index.html` is built
from that in-memory string at line 359; injection ran at line 377. So injecting
updated the file **on disk** but not the copy already **in memory**.

**Effect: a `device_engine.js` change reached `index.html` only on the NEXT
build.** Build once and ship, and the index page carried the previous engine. No
error, no warning, exit 0.

The comment sitting directly above that call said:

> Inject it into both hosts BEFORE anything is copied, so a build can never ship
> a stale copy.

It ran before the *copies*, so `keybinds.html` was fine. `index.html` is not a
copy — it is assembled — and it was not fine. **The comment asserted a guarantee
the code did not provide**, which is the same shape as every silent-success case
on this project.

**Found by grepping the built `index.html` for a symbol the engine patch had just
added, and not finding it.** Nothing else would have shown it.

**Fixed** — injection moved ahead of the layer read. **Proven both directions:**

- old ordering: patch the engine, build once → `index.html` `identityOf=0` (stale)
- old ordering: build a second time → `identityOf=4`
- fixed ordering: revert the engine, build, confirm 0; re-patch, build **once**
  → `identityOf=4` in both `index.html` and `keybinds.html`

This is worth knowing beyond this order: **any past session that patched
`device_engine.js` and built once shipped an index page with the previous
engine.**

## §1 — `sc_export.js` ships as its own file

Added to `PAGES` in `build_deploy.py` **and** to `DEFAULT_ALLOWED_FILES` in
`check_deploy_clean.py`. C1's correction was exactly right and I confirmed the
mechanism: `_allowed` derives from `PAGES` at build time (line 427), the
standalone set does not. Both now agree; standalone guard passes.

Loaded in `keybinds.src.html` before the page's own inline script. Not inlined.

## §2 — stick identity

`patch_device_identity.py`, in the same one-shot anchor-substitution shape as
`patch_two_sticks.py` / `patch_modes_wire.py` / `patch_btn_limit.py`. Implements
the FINDING §5 order: **imported profile GUIDs → remembered per VID/PID → guess
from plug order, labelled as a guess.**

Four things worth recording:

1. **The guess had to change too.** The old free-slot scan only avoided slots
   held by *other guesses*. With resolution in play it must also avoid slots
   already claimed by a profile or a remembered choice, or a guessed stick could
   be handed a number a resolved stick already owns and two devices would both
   call themselves `js1`. `claimedSlots()` closes that.
2. **There has to be a setter, or priority 2 is dead code.** Nothing could ever
   *become* remembered. Clicking the slot chip cycles js1..js8 and stores it
   against VID/PID. A profile-resolved slot is not cycleable — the game's own
   answer is not ours to override.
3. **`SCX` is not present on the index page.** `device_engine.js` is injected into
   both hosts but only `keybinds.src.html` loads `sc_export.js`. Every `SCX` call
   site is guarded; on the index page VID/PID is unavailable and everything falls
   to priority 3 — the old behaviour, now correctly labelled a guess. **The order
   did not mention this and it would have thrown on the index page.**
4. **The boundary-marker guard caught me.** My first version appended the new API
   *after* the `gamepaddisconnected` listener, whose last line is
   `inject_engine.py`'s `END` marker. The build refused: *"device_engine.js no
   longer ends with the boundary marker."* Correct refusal — the new code now
   goes *before* that listener. Recording it because the guard working is worth
   as much as the feature.

## §3 — import / export wired

File input → `SCX.parse(text, DOMParser)` (native browser parser; `@xmldom/xmldom`
stays Node-only). Export → `SCX.build` → `Blob` + `createObjectURL`. An import
hands its `devices` back verbatim; with no import it builds from live joysticks
via `CCDEV.joysticks()` and writes a device block with no rebinds — an honest
empty profile rather than a pretend one, since the action browser is pass 2.

**`mapOrder` and `categories` needed generating — the order's "reference the
existing generated data" could not be satisfied as written.** `kb_modes.gen.js`
is a per-key legend; it carries neither. Rather than paste either into the page
(a second copy of the thing that *is* the byte-identity), I extended
`build_keybind_modes.py` — the generator that already owns that file and already
reads `keybinds_site.json` — to emit `KB_MAP_ORDER` (50 maps, first-seen order)
and `KB_CATEGORIES`. Verified the generator was byte-stable before touching it.

## Acceptance

| # | | |
|---|---|---|
| 1 | build completes incl. deploy guard | ✅ |
| 2 | no hand edits inside the DEVICE PANEL markers | ✅ injected block byte-equals `device_engine.js` in both hosts; `_layer.src.html` unchanged outside it. `keybinds.src.html` differs outside the markers — those are §1/§3's required additions |
| 3 | import → export byte-identical | ⚠️ **proven against the deployed artifacts, not in a browser** — see below |
| 4 | two sticks agree with an imported profile | ❌ **NOT PERFORMED** — needs two sticks |
| 5 | panel distinguishes remembered from guessed | ❌ **NOT PERFORMED** — needs two sticks |
| 6 | `_deploy/` contents exact | ✅ `index.html`, `find.html`, `keybinds.html`, `loadout.html`, `kb_modes.gen.js`, `sc_export.js`, `images/`, `models/` |
| 7 | standalone guard passes | ✅ |

**On 3:** I ran the page's exact code path — `SCX.parse` then `SCX.build` with
`KB_MAP_ORDER`/`KB_CATEGORIES` — loading **`_deploy/sc_export.js` and
`_deploy/kb_modes.gen.js`**, the shipped files. Both fixtures come back
**byte-identical**. What that does not cover is `FileReader` and `Blob`: I checked
the fixtures carry no BOM and use CRLF, so neither should alter the bytes, but
**nobody has clicked the button.** Reported as strong evidence, not as the test
the order asked for.

**4 and 5 are NOT PERFORMED, not passed.** They need hardware I do not have.

## State

`go`-side untouched. Order 1 still green (`ALL CHECKS PASSED`). Nothing staged,
nothing committed, no `git add -A`.

**Passes 2 and 2B are NOT started.** Pass 2 carries the accessibility-font
question I flagged on receipt; I will implement chrome-only unless told otherwise
and will say so plainly.
