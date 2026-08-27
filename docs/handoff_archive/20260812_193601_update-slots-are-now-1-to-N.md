# Update — §1 done. The swap control swaps. Proven against the old code, which fails 14 of 18.

`device_engine.js`. Build not run yet; `node --check` clean.

## What replaced what

`(slotOf(p) % 8) + 1` is gone, and so is the thinking behind it. The old code
answered *"which slot is this device?"* one device at a time, which is why a
click could only ever increment — a per-device answer cannot see the other
stick, so it cannot exchange with it.

The new model reconciles **the whole connected set at once**: with N sticks, the
slots in use are a permutation of **1..N**, computed that way rather than
repaired into shape. Priority order is unchanged — profile GUIDs, then a
remembered choice, then plug order, still admitted as a guess.

**§5b needed no special case, which is the test the order set.** There is no
`if (list.length === 1)` anywhere in it. One stick is 1..1, so it is js1, and
swap has nothing to exchange with. That falls out of the rule.

## Verified by behaviour, both directions — `testing/_src/_verify_slots.js`

The harness runs the **shipped file** inside a `vm` with browser stubs, and
clicks the swap control through the real delegated `document` click handler
rather than calling an internal.

```
node testing/_src/_verify_slots.js                      ALL 18 CHECKS PASSED
node testing/_src/_verify_slots.js <pre-fix engine>     FAILED 14 of 18
```

**The second line is the point** (rule 12). A gate whose failure path has never
executed is an untested gate. What the old code actually did, as recorded by the
harness rather than described:

```
two sticks, ten clicks   2,2 | 3,2 | 4,2 | 5,2 | 6,2 | 7,2 | 8,2 | 1,2
```

That first state is worse than the reported symptom: **`2,2` — both sticks
holding js2 at once.** The report was "it goes to js3, then js4"; the step
before that was a duplicate slot, which nothing would have shown him.

Other known-bad inputs now covered:

- a stored `js5` on a lone stick — the state in his friend's browser — is not
  obeyed, and is **re-stored as 1**, so it heals rather than being re-derived
  on every load. Old code: `got js5`.
- two devices both remembering js1. Old code: `got 1,1`.
- unplugging the second stick. A remembered js2 stops being legal, so the
  survivor becomes js1. Old code: `got js2`.

## Decisions worth recording

**Each click is an exchange of exactly two slots at every N, so "click to swap"
is a true label and did not need weakening.** The order allowed a cycle for N>=3
provided the label said so. A cycle turned out not to be necessary: the clicked
stick exchanges with whichever holds the next slot, which walks it through every
position while moving exactly two devices per click. The harness asserts that —
*"every click exchanges exactly two slots"* — so if anyone later makes it a
genuine cycle, the label and the code go red together.

**Guessed slots are deliberately never persisted.** Writing one to localStorage
would freeze plug order and silently promote an admitted guess into a remembered
choice nobody made. Only a correction or a real click is stored.

**`CC_SLOT_KEY` bumped to `cc.js.slots.v2`.** v1 is left in place, not cleared —
inert once nothing reads it. The reconciler heals bad values anyway; the bump
drops today's known-bad state once instead of repairing it forever. The harness
seeds **both** keys, so if a future edit starts reading v1 again the repair test
fails rather than passing for the wrong reason.

**`padSlot` deleted.** It cached one device's guessed slot — the per-device
thinking the reconciler replaced. Leaving a variable called `padSlot` that no
longer governs slots is how the next person gets misled.

**Refusals are never silent now.** The control returns *why* nothing happened
and the panel renders it (`Nothing was changed: ...`), instead of
`console.warn` to a console nobody has open. With one stick the button renders
`disabled` and without the `cc-slot` class, so it is unreachable by the delegated
handler as well as by pointer.

## Not claimed

**No hardware. None of this has touched a real stick.** Two- and three-stick
behaviour is verified against synthetic pads only. Per §5b that is stated, not
glossed: the swap itself and js1-on-the-left ordering still need the pair.

Next: §2, the export path — renumber to 1..N regardless of UI state, and make
the `<devices>` set equal the `<options>` set.
