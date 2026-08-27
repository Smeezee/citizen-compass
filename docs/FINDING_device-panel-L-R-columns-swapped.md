# BUG — device panel shows L stick in the right column, R stick in the left column

    from      C3 (Cowork), 2026-08-07
    for       C1 -> Code
    reported  Sleven, screenshot of the live testing device panel
    fix type  display order only — do not touch device/button data bindings

---

## What's wrong

On the device panel (`testing/_src/device_engine.js` + `patch_two_sticks.py`'s
`dvcols.pair` column layout), the two VKBsim Gladiator EVO sticks render in the
wrong screen positions:

- **js1 — "VKBsim Gladiator EVO R"** currently renders in the **left** column.
- **js2 — "VKBsim Gladiator EVO L"** currently renders in the **right** column.

They're swapped. The R stick should be on the right, the L stick should be on
the left — matching how the physical HOTAS pair actually sits on the desk.

## What must NOT change

Sleven confirmed the buttons/axes work correctly — this is purely a visual
column-position swap. **Do not renumber, relabel, or remap anything**: js1
stays wired to whatever data source it's currently wired to (the R stick's
buttons/axes), js2 stays wired to the L stick's. Only which screen column each
one's box renders in should change.

## Likely cause and the two ways to fix it

`patch_two_sticks.py` almost certainly places columns in `js1, js2` order —
i.e., connection/enumeration order, not physical L/R identity. That's why this
flipped: the two sticks happened to enumerate R-first this session.

Two options, in order of robustness:

1. **Quick fix (what was asked for):** swap the two column positions so js1's
   box renders on the right and js2's box renders on the left. Fixes it for
   right now.
2. **Better fix, prevents recurrence:** `claude/workorder-device-visual-map.md`
   already flagged that `js1`/`js2` assignment is connection-order-based and
   "could follow the wrong stick" on a replug — this bug is that exact risk
   showing up. Instead of hardcoding which js-index goes in which column, sort
   columns by the device label itself (each one already says "EVO R" or
   "EVO L" in its name) so the layout is correct regardless of which stick
   happened to connect first. This fixes today's bug and stops it from coming
   back the next time the cables get plugged in a different order.

**Recommend option 2** since option 1 alone will silently break again on a
future session where the sticks enumerate in the other order — but either is
Code's call on effort vs. thoroughness.

## Acceptance

- L stick's column renders on the left, R stick's column renders on the right,
  regardless of js1/js2 assignment.
- Every button and axis still reads from the same underlying joystick index it
  does today — verify by pressing a known button on the physical R stick and
  confirming it still lights up in the (now-relocated) R column, not the L one.
