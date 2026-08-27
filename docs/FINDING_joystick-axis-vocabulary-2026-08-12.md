# FINDING — the authoritative joystick axis vocabulary, straight from CIG's defaultProfile

    from    C1, 2026-08-12
    for     Code — feeds the axis work in
              `prompt-code-keybinds-axes-and-no-import-2026-08-12.md` §2
    method  read directly from `data-layer/processed/defaultProfile.plain.xml`
              (218 KB, CIG's own file, already extracted and converted) and
              cross-checked against the two real profiles in
              `testing/_src/fixtures/`. Counted, not recalled.

---

## 1. Star Citizen ships with 839 default joystick bindings

Attribute counts in `defaultProfile.plain.xml`:

```
keyboard="   995
gamepad="    865
joystick="   839
mouse="      182
```

**This settles a question the from-defaults work depends on.** A flight-stick
owner starting from stock is not starting from nothing — CIG ships real stick
defaults. Building a profile from defaults is grounded, not invented.

## 2. The axis vocabulary, complete

Every non-button, non-hat joystick value CIG's own defaults use:

```
   7  y
   7  x
   1  rotz
   1  slider1
```

Plus `hat1_up` / `hat1_down` / `hat1_left` / `hat1_right`, and `button1..N`.

## 3. Cross-check against the two real profiles

Non-button, non-hat tokens in the fixtures — files Star Citizen itself wrote on
a real machine:

```
   3  js2_y      3  js2_x
   2  js2_rotz   2  js1_z
   2  js1_x      1  js1_y
   1  js1_rotz
```

## 4. What this changes

| token | CIG defaults | real profiles | status |
|---|---|---|---|
| `x` | yes | yes | **PROVEN** — both sources |
| `y` | yes | yes | **PROVEN** — both sources |
| `rotz` | yes | yes | **PROVEN** — both sources |
| `z` | no | yes | **PROVEN** — a real profile the game wrote |
| `slider1` | yes | no | **PROVEN** — CIG's own defaults |
| `rotx`, `roty`, `slider2` | no | no | **still UNATTESTED** |

**Two upgrades against `CURRENT-STATE.md`, which currently records only `z` as
proven:** `x`, `y` and `rotz` are attested twice over, and `slider1` is attested
in CIG's own file. `rotx`, `roty` and `slider2` remain unattested and must keep
saying so — absence here is weak evidence, not proof of invalidity, and a stick
with more axes than CIG's reference hardware would plausibly use them.

**For the axis-capture UI:** the five proven tokens cover X, Y, twist and a
throttle/slider — which is most of what a HOTAS owner binds. Those should
capture with no caveat. Anything outside that list keeps the unattested warning
the order already requires.

## 5. Worth noting, not acted on

`joystick=" "` and `joystick=""` both appear. An empty value and a
single-space value are almost certainly both "unbound", but they are not the
same string, and anything comparing them must handle both — a parser that
treats `" "` as a binding would emit a phantom.
