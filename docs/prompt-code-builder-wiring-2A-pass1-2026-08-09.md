# PROMPT FOR CODE — wire the exporter into the live keybind page and fix stick identity. Pass 1 of 2A; nothing else.

    from    C1, 2026-08-09
    for     Code
    basis   claude/WORKORDER_builder-ui-and-viewer-2026-08-09.md (C3, work order 2, §2A)
            claude/FINDING_exporter-round-trip-passes-2026-08-09.md (C3, §5 — the identity
              resolution order this pass implements)
    depends inbox/prompt-code-swap-the-exporter-2026-08-09.md — LAND THAT FIRST.
              As of right now it has not landed: testing/_src/sc_export.js is still the
              old broken exporter (last modified 2026-08-06, exports SCX but is the
              pre-fix version), test_sc_export.js is still present, and roundtrip.js /
              mutate.js / fixtures/ don't exist in testing/_src yet. Do not start this
              prompt until that order's §7 acceptance criteria all pass.

    C3's order 2 (which this comes from) is two pieces, 2A and 2B, and 2A itself splits
    into two passes by C3's own recommendation: land the exporter wiring and the device-
    identity fix first (this document), because that's the whole of what Sleven actually
    asked for; the 691-action browser and DOF reference are a second, separable pass.
    That second pass also has two open questions only Sleven can answer (font choice,
    whether the index-page overlay gets the builder too) — it's written up separately and
    isn't blocking this one. This document has no open questions; everything below is
    fully specified.

    Everything in §0 is C1 grounding C3's chat-derived claims against the real files —
    same as the correction pass on order 1. One of C3's claims needed a real fix, not
    just confirming; read it before the task list.

---

## 0. What was verified, and the one correction

Read `build_deploy.py`, `inject_engine.py`, `check_deploy_clean.py`, `device_engine.js`,
and `keybinds.src.html` directly rather than trusting the order's description alone.

**Confirmed as C3 described:** `keybinds.src.html` is copied verbatim into `_deploy/` by
`PAGES` (no substitution). `device_engine.js` is the single source injected into both
`keybinds.src.html` and `_layer.src.html` by `inject_engine.py`, between fixed boundary
markers, and right now both hosts are byte-identical to the master (checked
programmatically — not stale). `build_deploy.py` really does derive the deploy guard's
allowed-file set from `PAGES` at build time (`_allowed = {'index.html'} | {_o for _s, _o
in PAGES}`), so adding a line to `PAGES` is genuinely enough for the real build to accept
the new file.

**The one thing that needed correcting:** `check_deploy_clean.py`'s `DEFAULT_ALLOWED_FILES`
is a separate, hand-maintained set literal, used only when the guard is run *standalone*
(`python testing/_src/check_deploy_clean.py`, and the diagnostic one-liner in C3's order's
own Commands section) rather than as part of a real build. It does **not** pick up new
entries from `PAGES` automatically. If `sc_export.js` is added to `PAGES` but not also to
`DEFAULT_ALLOWED_FILES`, the real build will pass clean, but anyone running the standalone
guard check by hand afterward will get a false "unexpected file" failure that contradicts
the build. Fix both in the same commit (§1).

**Where the stick-identity bug actually lives, confirmed by reading it:** `device_engine.js`
line 71-84 — `pads()`, `slotOf(p)`, `prefix(p)`. `slotOf` assigns the next free slot number
1-8 keyed on `p.index`, which is `navigator.getGamepads()`'s array position — the browser's
USB enumeration order. Nothing here reads VID/PID, nothing persists across a session, and
nothing defers to an imported profile. That's the entire bug in one function.

---

## 1. Add `sc_export.js` as a real shipped file

In `build_deploy.py`, add it to `PAGES`:

```python
PAGES = [
    ('keybinds.src.html', 'keybinds.html'),
    ('loadout.src.html',  'loadout.html'),
    ('find.src.html',     'find.html'),
    ('kb_modes.gen.js',  'kb_modes.gen.js'),
    ('sc_export.js',     'sc_export.js'),
]
```

In `check_deploy_clean.py`, add it to `DEFAULT_ALLOWED_FILES` too, so the standalone guard
stays honest:

```python
DEFAULT_ALLOWED_FILES = {
    "index.html",
    "keybinds.html",
    "loadout.html",
    "find.html",
    "kb_modes.gen.js",
    "sc_export.js",
}
```

Ship it as its own file rather than inlining a copy into the page. Inlining creates a
second copy of code that already has an owner (`testing/_src/sc_export.js`, under the
order-1 round-trip suite) — the same rule-14 shape this project keeps hitting.

In `keybinds.src.html`, load it the same way `kb_modes.gen.js` already is (line 260,
`<script src="kb_modes.gen.js"></script>`):

```html
<script src="sc_export.js"></script>
```

Add it before the page's own inline `<script>` block, since that's where the import/export
wiring in §3 and the identity fix in §2 will call into it.

---

## 2. Fix stick identity in `device_engine.js`

Implement the priority order from `FINDING_exporter-round-trip-passes-2026-08-09.md` §5,
already proven correct on the real machine with both sticks handed to the page in the
wrong plug order:

1. **If a profile has been imported, its `<options>` GUIDs decide.** The game wrote them;
   they outrank everything else. `sc_export.js` (now loaded per §1) already exports
   `parseGamepadId` and `guidFromVidPid` — use those rather than re-deriving VID/PID
   parsing a second time in `device_engine.js`.
2. **Otherwise, the player's own choice, remembered per device VID/PID** — not per
   `p.index`, which resets every time the browser re-enumerates. Keyed on VID/PID so it
   survives a replug and a different USB port.
3. **Otherwise, a guess from plug order** — same as today's behavior — **and the panel
   must say so.** `prefix(p)` currently returns `"js"+slotOf(p)` with no way for a caller
   to know whether that was resolved or guessed. Whatever replaces `slotOf` needs to
   expose that distinction so the UI can render something like "js1 — guessed from plug
   order, click to set" instead of presenting a guess as fact.

**Follow the existing patch-script convention rather than hand-editing.** This repo already
has three scripts that modify `device_engine.js` this way —
`testing/_src/patch_two_sticks.py`, `patch_modes_wire.py`, `patch_btn_limit.py` — each a
one-shot anchor-substitution script: read the file, replace an exact, asserted-unique
string, write back with explicit `encoding="utf-8", newline="\n"` (rule 15), `sys.exit`
loudly if an anchor isn't found exactly once rather than silently doing nothing. Write
`patch_device_identity.py` in that same shape, run it once against `device_engine.js`, and
leave it in `testing/_src/` alongside the others as a record of what changed and why — that
history is the point of the pattern, not just the mechanism.

After the patch runs, `python testing/_src/build_deploy.py` re-injects the updated engine
into both hosts automatically (§0) — no separate step needed for that part.

---

## 3. Wire the actual import / export UI

`keybinds.src.html` currently verifies input but has no reference to `export`, `.xml`, or
`ActionMaps` anywhere — confirmed, there's nothing to build on. This pass adds the minimum
that satisfies C3's acceptance test (§4 below), not the full 691-action browser — that's
pass 2, separate and not blocking this one:

- A file input to import a `.xml` mapping file, calling `SCX.parse(xmlText, DOMParser)`
  (browser has a native `DOMParser`, no polyfill needed — the `@xmldom/xmldom` dependency
  from order 1 is Node-only, for the test harnesses).
- An export action calling `SCX.build(bindings, opts)` with `opts.mapOrder` sourced from
  `keybinds_site.json` (same data source `kb_modes.gen.js` is already generated from —
  don't duplicate it, reference the existing generated data) and `opts.categories` from
  `actionmap_categories.json`. Pass `opts.devices` verbatim when round-tripping an import;
  pass `opts.joysticks` (from the now-fixed `slotOf`/identity resolution in §2) when
  building fresh from live gamepads.
- The downloaded file uses the browser's own `Blob`/`URL.createObjectURL` pattern or
  equivalent — whatever this codebase already uses elsewhere for a file download, if
  anything does; otherwise plain and simple is fine, this isn't a place to introduce a new
  pattern.

This does not need the 691-action browser, the DOF reference page, or any font decision —
none of those are required for a file to go in and the same file to come back out.

---

## 4. Acceptance

1. `python testing/_src/build_deploy.py` completes, including the deploy guard, with no
   manual edits needed to make the guard pass.
2. `git --no-optional-locks diff testing/_src/keybinds.src.html` and the same for
   `_layer.src.html` show **no changes between the DEVICE PANEL boundary markers** — the
   identity fix must show up as a diff to `device_engine.js` (and the new
   `patch_device_identity.py`), with the injected copies changing only because
   `inject_engine.py` propagated it, not because either host was hand-edited inside the
   markers.
3. On the built page: import `real_export2.xml` (order 1's fixture, now at
   `testing/_src/fixtures/real_export2.xml`), export, and the downloaded file is
   byte-identical to the input. Same acceptance test as order 1, run through the real
   page instead of the round-trip harness — this is the check that proves the wiring, not
   just the module.
4. With two sticks connected in either plug order, after importing a real profile, the
   page agrees with the file about which one is js1.
5. With no profile imported and two sticks connected, the panel visibly distinguishes a
   remembered-per-VID/PID assignment from a guessed one.
6. `_deploy/` contains exactly `index.html`, the `PAGES` outputs (now including
   `sc_export.js`), `images/`, and `models/` — nothing else.
7. `python testing/_src/check_deploy_clean.py` run standalone also passes clean (confirms
   the `DEFAULT_ALLOWED_FILES` fix in §1 actually took).

---

## 5. What NOT to do in this pass

- Do not build the 691-action browser, the sections/categories browsing UI, or the DOF
  reference page. Separate pass, held pending two decisions only Sleven can make — see
  `claude/note-2A-pass2-and-2B-pending-decisions-2026-08-09.md`.
- Do not touch fonts.
- Do not touch `kb_overlay.inc.html`, or make any decision about whether the index-page
  overlay gets builder functionality. Same holding note.
- Do not touch the 3D viewer.
- Do not add `sc_export.js`'s contents inline into any HTML file — it ships as its own
  file, per §1.
- Do not run the deploy script (`scripts/deploy_testing.ps1`). Build only.
- Do not `git add -A`.
- Nothing commits or pushes without Sleven's explicit go-ahead.

---

## Commands

```
python testing/_src/build_deploy.py
```

```
python testing/_src/check_deploy_clean.py
```

```
git --no-optional-locks diff testing/_src/device_engine.js testing/_src/keybinds.src.html testing/_src/_layer.src.html
```

```
grep -c "DEVICE PANEL rev 2" testing/_src/keybinds.src.html testing/_src/_layer.src.html
```
