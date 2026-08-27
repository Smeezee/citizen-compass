# PROMPT FOR CODE — axes never reach the rebind seam at all, and the import requirement has to go

    from    C1, 2026-08-12
    for     Code
    basis   Sleven, hands-on with a real flight stick, just now:
              "I can click the buttons, and I can remove old key bindings. But
              if I try to put something in new, it doesn't recognize the actual
              y axis or any of the axes as things... the main feature that's...
              is the whole point. We need to be able to keybind flight sticks
              for people so they can just go right into it."
            And, separately:
              "Why are we requiring them to upload something first? Why do they
              have to upload a file from Star Citizen for us to then put it
              into Star Citizen? ... They shouldn't have to bring something out
              of Star Citizen to put something back into Star Citizen. That
              defeats the purpose of user friendly."
    scope   testing/_src/device_engine.js and testing/_src/keybinds.src.html.
              §1 is device-panel code — **`device_engine.js` only**, per the
              trap that already cost this feature one round.

---

## 0. §1 is root-caused, not suspected. Read this before doing anything.

`fireDev()` is called from **exactly two places** in `device_engine.js`:

```
509    fireDev(p,n[1],n[0],press+" ("+dur+"ms)");        <- buttons
523    fireDev(p,"POV hat "+dir...,"PRESS");             <- hats
```

And the branch that handles every other axis, at 528–530, is this in full:

```js
} else {
  var c=(padCenter[p.index]||[])[i]||0;
  if(Math.abs(v-c)>DEADZONE) hot=true;
}
```

**It sets `hot` — the "this device is alive" indicator — and does nothing
else.** No `fireDev`. So a plain axis never produces a token, never reaches
`KBREBIND.capture()`, and cannot be bound. Buttons and hats can; X, Y, Z,
throttle, rudder and sliders cannot, and never could.

This means the previous report's line — *"Axes work as well as buttons"* — is
not true of the shipped code. Flagging that plainly because that sentence is
exactly what would stop the next person looking in the right place. The gates
and the `KBREBIND` seam from `0f0409c` are correct and are **not** the problem
here; the axis simply never arrives at them.

## 1. Make a deliberate axis deflection produce a binding

**The reason axes are silent is legitimate for the tester panel and wrong for
rebinding.** An axis moves continuously — firing `fireDev` on every sample
would flood the live readout, which is presumably why it was never wired. So
don't just add a `fireDev` call to that branch; that fixes rebinding and ruins
the readout.

**Wanted: edge-detected, deliberate-deflection capture, active only while a
rebind is listening.**

- Fire **once** when an axis crosses a deliberate threshold — meaningfully
  above `DEADZONE` (0.12). Something around 0.5 of full deflection is the right
  order of magnitude: a resting stick with drift, or a hand brushing it, must
  never bind. Pick the number, say what you picked and why.
- **Re-arm only after the axis returns near centre.** Otherwise one push of the
  stick fires repeatedly and the "which axis did you mean" answer is whichever
  frame won.
- **Only while `KBREBIND.listening()` is true.** Outside a rebind, that branch
  keeps its current behaviour exactly — `hot` and nothing more. The live tester
  panel must not change at all.
- Centre from `padCenter` as the existing code already does, so a stick whose
  rest position isn't 0.0 (throttles, rudder pedals) is handled the way the
  panel already handles it. **Do not re-derive centring** — reuse it.

**On direction:** an axis has two. Whether Star Citizen wants a plain axis token
(`js1_y`) or a directional one is a real question, and the answer is in the
profile evidence this project already holds — the two real exports in
`testing/_src/fixtures/`. **Read them before choosing.** If they show plain axis
tokens, emit plain ones and ignore direction for binding purposes.

## 2. The token has to be honest about what's proven and what isn't

This project already knows its axis vocabulary is only partly evidenced.
`CURRENT-STATE.md`: `z` is **PROVEN** — a real profile uses `js1_z`. `rotx`,
`roty` and `slider2` are **UNATTESTED**, which is explicitly *not* the same as
invalid.

The device panel already maps axis index to a name (the `axrow` render path).
**Reuse that mapping. Do not invent a second one** — a second naming table for
the same physical thing is exactly the duplicate-writer defect this project has
hit repeatedly.

**If a rebind captures an axis whose token is UNATTESTED, the UI must say so at
the moment of capture** — the same way the gamepad `xi_` refusal already gives a
readable reason rather than guessing. It should still be bindable; the person
just needs to know it's the one that might not take. Silently writing an
unattested token as though it were proven is the failure mode this whole project
is built to avoid.

## 3. Remove the import requirement. This is the bigger fix.

Currently hard-blocked at `keybinds.src.html:1784`:

```js
if(!KBEDIT.hasImport()){
  alert('Import a profile first - there is nothing to change until then, ' +
        'and writing changes against the game defaults would produce a ' +
        'profile you never asked for.');
  return;
}
```

`hasImport()` is `working !== null`, and `working` is only ever set by an
import. So: no upload, no rebinding, at all.

**Sleven is right and the current design is backwards.** The intended user is
somebody who just bought a flight stick and wants a working profile. Sending
them into Star Citizen to export a file first, so they can put a file back into
Star Citizen, is the opposite of the point. And the stated justification doesn't
hold: **Star Citizen's defaults are stock, mandatory and identical for
everyone** — a baseline of defaults isn't a guess, it's a known quantity.

**This is my design error, not a build miss.** My original rebind order framed
capture as "into a working copy of the current binds… keep the original import
untouched," which baked the import-first model in. It was the right instinct for
*editing an existing profile* and the wrong shape for *building one*.

**What to build:**

1. **Rebinding works with no import.** The baseline is the game defaults, which
   the page already carries — `KB_ACTIONS` / `keybinds_site.json` hold 691
   labelled actions with their defaults.
2. **Import stays**, unchanged, for anyone modifying a profile they already
   have. Two entry points into one editor, not two editors.
3. **Say which baseline is in play**, always visible. Replace *"Import a profile
   to start rebinding"* with something that states the state: starting from game
   defaults, or from the file they loaded. Somebody must never be unsure which
   of the two they're editing.
4. **Export writes what the person actually bound.** A Star Citizen actionmap
   overlays the defaults — it does not have to restate all 691. Exporting only
   real changes is both correct and much easier to eyeball.
5. **The zero-rebind case still has to behave.** Today, exporting with nothing
   changed and nothing imported produces "an honest empty profile rather than a
   pretend one." Keep that property.
6. **`roundtrip.js` / `mutate.js` must still pass.** The round-trip guarantee for
   an imported profile is not allowed to regress in service of this.

## 4. The one thing nobody has ever verified, and it now matters much more

**No file this tool has generated has ever been loaded by Star Citizen.**
`verified` is hard-coded false. That was tolerable while the tool only echoed
back a file the game itself wrote. **Once we generate a profile from defaults,
that is no longer a round trip — it is us asserting we know the format.**

So: build it, and **do not let the UI claim the export is known-good.** Whatever
wording is there now about verification must stay honest, and if anything it
should be more prominent on a from-defaults export than on a round-tripped one.

**Sleven settles this in one test:** export from defaults, drop it in
`USER\Client\0\Controls\Mappings\`, load it in-game, see whether the bindings
are there. Say so plainly in the report back, with the exact folder path, so he
can do it without hunting.

## 5. What NOT to do

- **Do not edit inside the injected block.** `fireDev`, `poll`, `startPoll` and
  the axis branch live in `device_engine.js`, and `inject_engine.py` overwrites
  that region of **both** hosts on every build. This already cost a round.
- Do not change the live tester panel's axis behaviour outside a rebind.
- Do not invent a second axis-name table.
- Do not emit an UNATTESTED token without saying it's unattested.
- Do not "fix" the gamepad `xi_` refusal — that's still unsettled evidence.
- Do not regress `roundtrip.js` / `mutate.js`.
- Nothing pushes or deploys without Sleven's go-ahead.

## 6. Acceptance

1. With a real stick, start a rebind and push the Y axis — the binding takes an
   axis token. Same for X and the throttle.
2. A resting stick, and a stick nudged within its deadzone, bind **nothing**.
3. One deliberate deflection fires **once**, not repeatedly, and re-arms only
   after returning near centre.
4. Outside a rebind, the live device panel behaves exactly as it does today.
5. Buttons and hats still bind, unchanged from `0f0409c`.
6. **With no import at all**, a person can open `/keybinds`, bind several stick
   controls, and export a file.
7. The page states at all times which baseline is in play.
8. Export with zero changes still produces the honest-empty result.
9. `roundtrip.js` and `mutate.js` pass.
10. `build_deploy.py` and `check_deploy_clean.py` pass clean.

## 7. Report back

The deflection threshold and re-arm rule you chose and why; what the real
fixtures showed about axis token shape; which axis tokens are PROVEN vs
UNATTESTED and how the UI distinguishes them at capture time; and the exact
in-game folder path Sleven drops the generated file into.

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
