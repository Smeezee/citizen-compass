# Update — joystick/HOTAS rebinding works. The first attempt silently vanished, and a gamepad gap turned up.

## The order's scope was wrong, and the build proved it by erasing my work

C1 scoped this to `keybinds.src.html`. **It cannot be done there.** `fireDev()`,
`poll()` and `startPoll()` all live inside the **DEVICE PANEL block**, which
`inject_engine.py` rewrites from `device_engine.js` on every build.

I edited `keybinds.src.html`, built, and the build silently reverted all three.
`grep` for the new guard afterwards: **0 occurrences in the source, 0 in the
built page** — and the build reported success the whole way through. The
browser harness then failed with `rafId=null` and cells stuck on "press a
key…", which is what sent me looking.

That is the *"patching only the source layer can silently do nothing"* hazard
the 2A pass-1 order warned about, arriving for real. Redone as
`patch_rebind_device_capture.py`, in the same one-shot anchor-substitution shape
as the other four patch scripts. **Now verified to survive:** the guard appears
3 times in `device_engine.js`, 3 in `keybinds.src.html`, 3 in the built
`keybinds.html` **and 3 in the built `index.html`** — one build, both hosts,
because the injection-ordering fix from earlier today is doing its job.

## What was built

**The seam is `fireDev()`**, exactly as C1 suggested — it is already the one
place a real device press has become the game's own token. A rebind takes that
string rather than growing a second mapping beside it, which is why hats and the
axis/button dual identity come through correct for free.

**Both poll gates ungated during a rebind.** `poll()` opens with
`if(dev==="KBM") return`, and `startPoll()` has the same condition — so on the
Keyboard/Mouse tab, where the action browser lives, the gamepad loop was not
running at all. That is precisely why "press a joystick control" did nothing.
Neither gate depends on `dev` alone any more.

**The prompt text now describes what it accepts:** *"press a key, mouse button,
or any joystick / HOTAS / gamepad control"*.

## Verified against the shipped code

Driven through the built page's own `KBEDIT`:

```
js1_button3   accepted, and it is what the action holds
js1_hat1_up   accepted - full compound hat token, not a synthetic guess
js2_button12  accepted - second stick
js1_x         accepted - an AXIS, not just a button
a hat rebind changes EXACTLY ONE LINE:
   was <rebind input="js1_button17"/>   now <rebind input="js1_hat1_up"/>
nothing lost: 247 in, 247 out
```

`roundtrip.js` ALL CHECKS PASSED · `mutate.js` 19/20 M18 · guard clean.

**One of my own checks was vacuous and I caught it.** The first export
assertion looked for `js1_button3` anywhere in the output — and passed, on
bindings that were already in the fixture, while the rebind had done nothing at
all. The fixture is joystick-only, so those tokens were always there. Rewritten
to assert the **action+token pair**, which is the actual claim.

## NEW GAP: an XInput gamepad cannot be rebound, and two parts of the page disagree

```
xi_a  ->  REFUSED: "input 'xi_a' has no recognised device prefix
                    (expected kb1_, mo1_, js1_, gp1_)"
```

`device_engine.js:163` emits `xi` for a standard-mapping gamepad
(`isStd(p) ? "xi" : "js"+slotOf(p)`). `sc_export.js`'s `famOf()` knows only
`kb`, `mo`, `js`, `gp`. So:

- **the tester tells people** *"Type `xi_a` into a Star Citizen binding"*
- **the exporter refuses `xi_a`**

They cannot both be right, and **I do not know which is.** `gp1_` is what
`sc_export.js` expects and matches the game's own prefix vocabulary; `xi_` is
the panel's convention. **Neither fixture contains a gamepad binding** — both
real profiles are joystick-only — so there is no evidence on this machine to
settle it.

**Refusing is the correct behaviour for now** and it refuses with a readable
reason. Silently translating `xi_` to `gp1_` would write a token nobody has
ever seen the game accept. Needs one real gamepad profile exported from the
game to resolve; flagging rather than guessing.

**Joystick and HOTAS — the actual subject of the order — work.**

## What is NOT verified

No HOTAS on this machine. I drove `fireDev` with the tokens a stick produces,
which exercises everything from that point on — but **nothing here proves
`poll()` samples a real device.** The gates are code-verified and the token path
is proven; the first real stick press is still the test that matters.

Headless Chrome also began hanging partway through this work (a stray process
holding a profile lock), so the final UI pass ran in Node against the built
page's modules rather than in a browser. Stated rather than glossed.

Build only. Nothing staged, nothing committed, not deployed.
