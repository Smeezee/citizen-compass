# PROMPT FOR CODE — MASTER ORDER. Everything outstanding, in one place. Supersedes the scattered set.

    from    C1, 2026-08-12
    for     Code
    basis   A full day of real-hardware testing by Sleven on a friend's machine
              with a VKB Gladiator NXT EVO pair, plus the first ever attempt to
              load a generated profile into Star Citizen.
    status  GO-AHEAD to build, commit, push AND deploy. Sleven: "Let's fix the
              things that are broken. Push a new build."

    SUPERSEDES these, which should not be worked from independently:
      prompt-code-keybinds-axes-and-no-import-2026-08-12.md
      prompt-code-keybinds-detection-and-labels-2026-08-12.md
      prompt-code-keybinds-capture-toggle-and-stick-order-2026-08-12.md
      prompt-code-slot-numbering-and-input-stall-2026-08-12.md
      ERRATUM-slot-swap-is-a-cycle-2026-08-12.md
      prompt-code-MASTER-clear-the-queue-2026-08-10.md
    Findings that remain live as EVIDENCE, not instructions:
      FINDING_vkb-pair-device-report-2026-08-12.md
      FINDING_joystick-axis-vocabulary-2026-08-12.md

    Why one document: eight files accumulated for one job today and at least
    one contradicted another. That is the exact defect this project already has
    a rule against, and it was mine. One writer, one order.

---

## 0. State of play, verified against the tree just now

Live at `daeefc7`, in sync with `origin/main`. What is genuinely **not built**:

```
#kbbq search guard ............... NOT built  (0 hits)
swap-is-a-cycle .................. NOT fixed  (slotOf(p)%8 still present)
holo depth pre-pass .............. NOT built
holo fleet dataset (pos_model) ... NOT built
fonts in _deploy ................. NOT done   (README only)
End / nav keys ................... partial    (2 hits — verify behaviour)
```

Already done and not to be redone: joystick rebind, axis capture, no-import
defaults, device presence, the diagnostic readout, the injector syntax gate.

## 1. THE ROOT CAUSE — the swap control counts instead of swapping

**This one line caused most of today.**

```js
if(!rememberSlot(p,(slotOf(p)%8)+1)){        // device_engine.js
```

`(slotOf(p) % 8) + 1` increments. The control is labelled **"wrong stick? click
to swap"**. Two sticks come up correctly at js1/js2; Sleven clicked swap to put
them the right way round and got js3, then js4 — and it persisted to
localStorage, so it looked like drift.

**Build:** with N sticks connected, the control **exchanges** two slots. Two
sticks → js1 ⇄ js2, both remembered values updated together. Never a value
outside 1..N. Never two devices holding the same number, even transiently. For
3+, cycling among *occupied* slots is fine provided it stays a permutation of
1..N — and if it cycles rather than swaps in that case, **the label must say
so.** "Click to swap" on a counter is what sent him round this loop.

**Keep, both correct as written:** `if(fromProfile(p)) return;` — an imported
profile's own answer is not ours to override. And the refusal, with a stated
reason, when there's no VID/PID to remember against.

**Repair pass:** a stored slot outside 1..N — including the value sitting in his
friend's browser right now — is corrected on load and re-stored, never obeyed.
Consider a `CC_SLOT_KEY` version bump so bad state is dropped once rather than
repaired forever.

## 2. The export — first real one, analysed. Structure is sound; numbering ruins it.

Sleven loaded a generated profile into Star Citizen. **It did not work, and he
could not tell whether it had even taken.** The file:

```xml
<joystick instance="1"/><joystick instance="2"/>
<joystick instance="3"/><joystick instance="4"/>
<options type="joystick" instance="3" Product=" VKBsim Gladiator EVO L    {0201231D-0000-0000-0000-504944564944}"/>
<options type="joystick" instance="4" Product=" VKBsim Gladiator EVO R    {0200231D-0000-0000-0000-504944564944}"/>
```

**The GUIDs are genuinely correct** — PID/VID off the hardware, `504944564944`
is the ASCII of "PIDVID", proper DirectInput form. That is the part that would
have been worst to get subtly wrong, and it is right.

Four defects:

1. **`instance="3"`/`"4"` and every binding `js3_*`/`js4_*`.** Unusable. Fixed
   at source by §1 — **and additionally, the export path must renumber to 1..N
   regardless of UI state.** This is safe: Star Citizen resolves the device by
   the Product GUID, not by the instance number, so renumbering cannot mismatch
   a stick. Belt and braces, so a bad screen can never again produce a dead file.
2. **`<devices>` declares four joysticks, `<options>` describes two.** The
   declared set must equal the described set.
3. **`js3_button29` bound to both `v_flightready` (spaceship_general) and
   `v_atc_request` (spaceship_movement)** — both live in flight, and the
   conflict check did not fire. Check whether it only looks *within* one
   actionmap instead of across those active together.
4. **`js3_rotx` / `js3_roty` were offered and bound with no warning.** Neither
   appears in CIG's `defaultProfile.xml` nor in either real profile. The
   unattested flagging is either not reaching the capture UI or not reaching
   the export. See `FINDING_joystick-axis-vocabulary-2026-08-12.md` for the
   evidence table — `x`, `y`, `z`, `rotz`, `slider1` are PROVEN; `rotx`, `roty`,
   `slider2` are not.

**And build the thing he actually needed and didn't have:** after export, tell
him plainly where the file goes and **how to confirm Star Citizen took it.** He
couldn't tell whether it had stuck. A short, exact instruction — the folder
path, and what to look at in-game to verify — is worth more here than any
further code.

## 3. Input stalls on tab switching

Sleven, live: works, then *"clicking keyboard and mouse after you've clicked
joystick and HOTAS seems to not work"*, then it returns on its own, then dies
again.

**`rafId` has five writers:** the tab handler cancels it directly, `startPoll()`
sets it, `poll()` re-arms it, `ccPresenceTick()` starts it, `gamepadconnected`
starts it. A cancel racing a re-arm leaves either a live loop with `rafId===null`
— after which `startPoll()` starts a *second* — or a dead loop everyone believes
is running.

**Give `rafId` one owner** with explicit start/stop; every other caller goes
through it. **Use the frame counter you built** to verify: switch tabs ten times
and confirm one loop, still climbing. Do not paper over it with try/catch or by
starting extra loops.

## 4. Still unbuilt from before today

- **`#kbbq` search box** — dead while Capture is ON, which is the default. One
  `stopPropagation` guard, matching what `#q` already has at line 944. Confirmed
  still absent.
- **Nav keys** — `End`/`Home`/`PageUp`/`PageDown` should scroll the page in the
  tester, not be swallowed. Two hits exist; verify actual behaviour rather than
  assuming it's done. **A deliberate rebind must still accept them.**
- **Holo viewer** — the white-hull depth pre-pass and the marker cm→m fix, then
  the 167-ship fleet dataset. Neither started. Full spec was in
  `prompt-code-holo-viewer-fixes-and-fleet-2026-08-10.md`; that one is **not**
  superseded, it's simply untouched — work from it directly.
- **Fonts** — copy the five files from `data-layer/derived/fonts-ofl/` into
  `testing/_deploy/fonts/`, rewrite the README that still says "intentionally
  incomplete." Licence closed (OFL 1.1, verified from the packages). **Chrome
  only** — headings, tabs, buttons, marked `.cc-ui`; **not** the 691-row action
  table, which must keep following the reader's accessibility font.
- **Collector shortcut ordering** — move `OfferShortcuts` after the
  single-instance check so a launch that exits doesn't rewrite the Desktop.

## 5. Layout and polish, from the same session

- Two sticks **side by side**, not stacked, on `/keybinds` and `/stick-test`.
  Sleven asked for this directly; it also makes the js1-left ordering useful.
- The panel renders **128 buttons per stick** — that's the HID report size, not
  physical controls (a Gladiator has ~13). Confirm "Hide unused buttons"
  defaults sensibly for a device reporting that many.
- **`axes[8]` has no Star Citizen name** on this hardware and the page says so
  rather than inventing a token. **Correct — keep it**, and make sure that
  statement is visible rather than buried.

## 5b. ONE STICK is now the common case — and it is not covered anywhere

Sleven has borrowed **a single** stick so testing no longer means walking to
another room. That is the setup most of this will now be exercised against, and
it exposes a case nothing above handles.

**With exactly one stick connected:**

- It must be **js1**. Not js2, not whatever index the browser handed out. A
  fresh browser with one stick and no stored choice is the simplest possible
  case and it must be right.
- **Swap is meaningless.** There is nothing to exchange with. Today's cycling
  code would happily turn the only stick into js2, which is exactly the
  original bug in miniature. **Disable the control, or have it say why it does
  nothing** — do not let it produce js2 when N=1.
- The export must carry **one** `<joystick instance="1"/>`, **one** `<options
  instance="1">`, and only `js1_*` tokens. The four-phantom-devices defect in §2
  makes this worth checking explicitly rather than assuming it falls out of the
  N-device fix.
- Layout: one stick should not leave a gap where the second would be.

**Generalise rather than special-case it.** N=1 and N=2 are the same rule —
slots are exactly 1..N — and if the code is written as "reconcile the connected
set to 1..N" then one stick is not a special case at all. If you find yourself
writing `if (list.length === 1)`, the general fix probably isn't general.

**What one stick can now verify without another trip:** axis capture, button
capture, hats, the unattested-token warning, the tab-switch stall and frame
counter, the search box, the End key, detection and presence, export structure
and GUID correctness, and — the big one — **whether Star Citizen accepts a file
we generated.**

**What still needs the pair:** the swap itself, js1-on-the-left ordering, and
side-by-side layout. Build those to spec, state in the report that they are
unverified against real hardware, and do not claim otherwise.

## 6. What NOT to do

- Don't rebuild anything in §0's "already done" list.
- Don't invent an axis token for `axes[8]`.
- Don't emit an UNATTESTED token without saying so.
- Don't touch `MANUAL_MATCHES` — the Cutlass airframe question is Sleven's.
- Don't publish a collector release or install `gh` — not authorised.
- Don't edit inside the injected block.
- Don't `git add -A`.

## 7. Acceptance

0. **One stick, fresh browser → js1.** Swap does nothing, or says why. Export
   carries exactly one `<joystick>`, one `<options>`, and only `js1_*`.
1. Two sticks → js1 and js2. Swap exchanges them. Clicking ten times alternates
   between exactly two states. **No js3, ever.**
2. A stored slot of 3+ is repaired on load.
3. Export contains only `js1_*`/`js2_*`, `<options>` instances 1 and 2, the
   `<devices>` block matching exactly, and the GUIDs following their sticks
   across a swap.
4. Binding one input to two actions live in the same context warns.
5. Binding an unattested axis says so at capture time.
6. KBM→JOY→KBM ten times: input still registers, frame counter shows one loop
   still climbing.
7. `#kbbq` searches with Capture ON. `End` scrolls in the tester; a rebind still
   accepts it.
8. Holo: Sabre renders without white blowout, markers land on the hull, fleet
   dataset spot-checked across all three model-scale conventions.
9. Fonts present in `_deploy`, `OFL.txt` shipped, README truthful, action table
   still switchable.
10. Collector: a launch that exits does not touch the Desktop.
11. `roundtrip.js`, `mutate.js`, `build_deploy.py`, `check_deploy_clean.py` all
    pass clean.

## 8. Then push and deploy

Logical commits, not one lump. Push, verify by re-fetching. Deploy with the
deploy script — **never `wrangler pages deploy`**. Verify live assets
byte-for-byte. Note that the index may serve stale from cache; state that in the
report so a cached page isn't mistaken for a failed publish.

## 9. Report back

Per-item results; the frame-counter behaviour across the tab-switch test; the
`pos_model` vs `unit` choice for the fleet data and which ships you spot-checked;
and **the exact folder path plus the in-game way to confirm a profile loaded** —
that last one is the thing Sleven needs most and currently doesn't have.

## Commands

```
node testing/_src/roundtrip.js
```

```
node testing/_src/mutate.js
```

```
python testing/_src/build_deploy.py
```

```
python testing/_src/check_deploy_clean.py
```
