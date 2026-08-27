# ORDER — The panel will not close, the border shouts, and nobody has seen the retune

**Written by C1, 2026-08-27. For Code.**

Three defects. Sleven reported the first two from the live testing site. The
third is the reason he said *"I can't even see what the fuck we fixed last
night — nothing looks different."* He was right, and it is not a figure of
speech: he has not been looking at the current defaults on any ship, on any
day since they changed.

Scope is these three. The left panel stays parked. Nothing here touches the
model pipeline, the marker derivation, or C3.

---

## P1 — THE PANEL CANNOT BE DISMISSED BY CLICKING AWAY

Sleven, verbatim:

> *"I can't click away from it. Once I open it up, there's no way to close it.
> I have to open a new one... I have to move the ship around the box that's
> covering the window just to close it."*

H2 of `ORDER_the-hardpoint-picker-2026-08-27.md` said *"Escape closes it.
Clicking off it closes it."* Escape shipped correctly. Clicking off it did
not, and the reason is exact.

`testing/_src/loadout.src.html`, the background-dismiss branch:

    if(sel && e.target.closest('#cc-stage')
       && !e.target.closest('#cc-panel') && !e.target.closest('#cc-marks')){
      sel=null; renderAll(); return; }

**It tests `sel`. The panel has two states and this is the other one.**

`renderStagePanel()` opens `#cc-panel` for `sel` — a selected port — and it
opens the SAME `#cc-panel`, at the same anchor, with the same placement, for
`mountSel` — the disambiguation list a mount carrying more than one weapon
puts up. The click handler at the marker sets `mountSel=mo.root; sel=null`
whenever `mo.n>1`. So on any mount with two or more weapons the panel is open
with `sel === null`, and the dismiss test is false on its first term.

Escape handles both (`if(mountSel){...}` then `if(sel){...}` at the keydown).
The click path handles one. That asymmetry is the whole bug.

**And this is why he hit it on the ships he opened.** The Anvil Arrow's own
header reads `9 mounts · 19 weapons` — nineteen weapons across nine mounts,
so most of its dots take the `mo.n>1` route. He was in the unclosable state
on nearly every dot he could click.

**The second half of the same branch.** It also requires the click to land
inside `#cc-stage`. A click on the spec table, the tab bar, the page margin —
anywhere off the stage — leaves the panel up. A person who has finished with
the panel and moves on to reading the specs is not told the panel is now
stale; it just sits there.

### P1a
The dismiss must fire when EITHER `sel` or `mountSel` is set. Not by
duplicating the branch — by one condition that names both states, so a third
state added later fails loudly rather than silently joining `mountSel` in the
gap.

### P1b
Drop the `#cc-stage` requirement. A click anywhere that is not inside
`#cc-panel`, not on a marker, and not inside the left list's own picker
(`.inlinepick`, `.slot[data-slot]`, `.pi[data-part]`) closes it.

### P1c
**Order matters and it is load-bearing.** The dismiss must be the LAST thing
the click handler considers, after every specific branch has had its chance to
`return`. It is currently sitting mid-handler, above the `.pi[data-part]`
branch, and only survives that because of the stage scoping P1b removes.
Broadening the test without moving it will swallow part selection in the
inline picker. Move it to the end of the handler in the same change.

### P1d
Clear both `sel` and `mountSel` on dismiss, exactly as `#dockclose` already
does. Leaving `mountSel` set while the panel is hidden is the state that makes
"even still, it doesn't open" possible on the next click.

---

## P2 — THE PANEL IS THE ONLY SURFACE ON THE PAGE OUTLINED IN THE ACCENT

Sleven:

> *"It's got a light line, like a border all the way around it. I'm not sure
> how much I like that. It stands out too much from everything else."*

He is describing something measurable, not a taste. Every other panel on this
page borders in `var(--line)` — `#22364F`, desaturated blue-grey. Count them:
`.col`, `.panel`, `.stat`, `.bud`, `.res`, `.paint`, `.buy`, `.picker .ph`,
`.picker .sortrow`, the selects, the buttons. All `--line`.

`#cc-panel` borders in `var(--accent2)` — `#22D3EE`, full-strength cyan. It is
the single exception in the stylesheet. "Stands out too much from everything
else" is the literal truth: it stands out from everything else because it is
the only one doing it.

### P2a
`#cc-panel` takes `1px solid var(--line)`, the same as every other panel.

### P2b
The tie to the hull does not come from the outline — it comes back as the
**corner brackets** from the Fusion pattern Sleven approved: short marks at the
four corners, pulled inside the radius, in the accent at low alpha. Add the
alpha as a token beside the other scrims rather than writing a literal into
the rule; the accent is themeable and a hard-coded cyan will survive a theme
change it should not survive.

### P2c
The dotted leader from panel to dot keeps its current strength. That line is
what carries the tie during rotation and it is doing its job — do not quieten
it to compensate for P2a.

---

## P3 — NOBODY WITH AN OLD SAVE HAS SEEN A SINGLE RETUNE

This is the one to read twice.

`cc_viewer.js` restores the appearance from `localStorage` under `ccHolo`:

    var saved = ccHoloSaved();
    this.style   = this.style || saved.style || CC_HOLO.DEFAULT;
    this._colour = saved.colour || CC_HOLO.DEFAULT_COLOUR;
    if (saved.lineInt != null) CC_HOLO.lineInt = saved.lineInt;
    if (saved.detail  != null) CC_HOLO.detail  = saved.detail;
    if (saved.glow    != null) CC_HOLO.glow    = saved.glow;
    if (saved.scan    != null) CC_HOLO.scan    = saved.scan;
    if (saved.grid    != null) CC_HOLO.grid    = saved.grid;

**There is no revision stamp on that blob, and every key overrides the default
unconditionally, forever.** H1f-2 made the storage permanent on Sleven's own
instruction — *"as long as possible... I'd hate to have to come in after a
couple of days and have to redo it"* — and that decision stands. What was
never built is the other half: a way for a CHANGE TO THE DEFAULTS to reach
somebody who already has a save.

Every appearance fix since the day he first touched that panel has landed in
the defaults and been overwritten on his machine at boot:

- **G3** removed the line pass and moved `DEFAULT` to `solid`. Measured: the
  fraction of each hull showing something other than its own nearest solid
  surface went from 20.6–67.1% to **0.00% on all ten**. That is the
  see-through defect, fixed, in the default.
- **E7b** set `lineInt` to 0.33 from his own captures.
- **G1** retired `glow: 0.04` and replaced the coefficient.
- **DEFAULT_COLOUR** is amber, `0xffb545`.

**His screenshots are cyan.** Amber is the default and has been. Cyan is
`COLOURS[0]`, and the only way a viewer opens cyan is `saved.colour`. That
single fact proves the restore is winning on his machine — which means
`saved.style`, `saved.lineInt` and `saved.glow` are winning too, and the
see-through he keeps reporting is a style we retired weeks ago, restored fresh
on every page load from a blob nothing has ever been able to update.

He has been reporting a defect we fixed, on a build that fixed it, and he was
not wrong to keep reporting it.

### P3a
`CC_HOLO` carries a `REV` integer. `ccHoloSave` writes it with the settings.

### P3b
On load, a saved blob whose `rev` is missing or below the current `REV` has
its **appearance keys discarded** — `style`, `colour`, `lineInt`, `detail`,
`glow`, `scan`, `grid` — and is re-saved at the current `REV`. Keys not
governed by a retune are untouched. This happens once per revision, never
again.

### P3c
`REV` is bumped **only** when a default that people can already have saved
actually changes, and the bump is named in the commit message with which
default moved. A bump that does not correspond to a real default change is a
bug: it throws away a person's settings for nothing.

### P3d
**Say it in the panel.** When P3b fires, the look panel shows a single quiet
line on first open — that the viewer's appearance was updated and their old
settings were replaced. Not a modal, not a toast that steals focus. Somebody
who had deliberately set wireframe-and-scanlines deserves to know why it is
gone rather than thinking the site broke.

---

## P4 — THE CHECKS, AND WHAT EACH ONE HAS TO BE ABLE TO FAIL

Rule 12. A check that cannot fail is decoration. Each of these gets a mutator
that breaks the specific thing and must be observed to make the check fail.

### P4a — the panel closes from the mount-list state
In a real browser, on a ship with a mount carrying more than one weapon —
**the Anvil Arrow, named because it is the ship he was holding** — click a dot
that opens the mount list, assert `#cc-panel` is visible, click empty stage,
assert `#cc-panel` is hidden and both `sel` and `mountSel` are null.

**Mutator:** restore the `sel &&` first term. The check must fail. If it
passes with the old condition restored, the check is testing the `sel` path
and has not touched the defect.

### P4b — the panel closes from off the stage
Same ship, open the panel, click a spec-table cell. Panel hidden.

**Mutator:** re-add the `e.target.closest('#cc-stage')` requirement. Must fail.

### P4c — the inline picker still selects
On a ship whose picker homes to the list rather than the stage, click a
`.pi[data-part]` row and assert the part changed. This is the check that
catches P1c being done wrong.

**Mutator:** move the dismiss branch back above the `.pi` branch. Must fail.

### P4d — the border is not the accent
Assert the computed border colour of `#cc-panel` equals the computed border
colour of `.col`. Comparing against a literal hex would pass a theme that
changed both and lie about the one that changed one.

**Mutator:** set `#cc-panel` back to `var(--accent2)`. Must fail.

### P4e — a stale save does not survive a revision bump
Seed `localStorage.ccHolo` with `{"style":"solidlines","colour":24041966,
"lineInt":1.0}` and no `rev` — **that is the shape of a real pre-revision
save, which is the case that matters.** Load a ship page. Assert the viewer
reports `solid`, reports the amber default, and that `localStorage.ccHolo`
now carries the current `REV`.

**Mutator:** remove the rev comparison so the old blob restores. Must fail.

### P4f — a current save DOES survive
Seed a blob at the current `REV` with a non-default colour. Load. Assert the
colour survived. Without this, P3b passes trivially by discarding everything
always, and H1f-2's permanence is quietly destroyed while the checks stay
green.

---

## What is NOT in this order

**The models.** Sleven's question about pulling geometry from the RSI website
is answered in `claude/ANSWER_the-rsi-models-are-the-ones-we-have-2026-08-27.md`.
The short of it: we already went and got them on 2026-08-22, they are the same
asset family we already hold, and they carry no hardpoint data. **No work for
Code falls out of it.** Do not start anything on it.

**The hardpoint alignment.** Real, unresolved, and not a bug in this build —
it is a data ceiling that needs a decision before it needs code. Same
document. Do not start it.

---

*C1, 2026-08-27.*
