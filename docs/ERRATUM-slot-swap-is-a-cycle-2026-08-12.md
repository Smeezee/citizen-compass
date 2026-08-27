# ERRATUM — the slot bug is the swap control, not reconnect drift. My earlier diagnosis was wrong.

    from    C1, 2026-08-12
    for     Code
    amends  `prompt-code-slot-numbering-and-input-stall-2026-08-12.md` §1 and
              `FINDING_vkb-pair-device-report-2026-08-12.md` §1
    urgent  read this BEFORE building the reconciliation fix — that order
              describes a mechanism that is not the real one.

---

## 1. What Sleven actually said, which settles it

> "It did say JS1 and JS2, but as I was trying to switch them to the right
> side, it ended up calling one JS3 instead of JS1 and JS2."

**The initial assignment was correct.** Two sticks, js1 and js2, exactly as it
should be. The numbers only went wrong **when he used the swap control.**

## 2. I got this wrong and it's worth being precise about how

I wrote that the slots were drifting upward on reconnect, and cited js2/js3
becoming js3/js4 across two observations as evidence of a progressive,
self-worsening fault. **That inference was wrong.** The two observations were
separated by him clicking the swap control, not by a reconnect. I read two
snapshots, assumed the thing between them was a session boundary, and it was a
user action.

The sticky-`padSlot` behaviour I described is real, but it is not what produced
what he saw.

## 3. The actual bug, one line

```js
if(!rememberSlot(p,(slotOf(p)%8)+1)){
```

**`(slotOf(p) % 8) + 1` cycles 1→2→3→…→8→1. It does not swap.**

And the control is labelled **"wrong stick? click to swap"**.

So: two sticks sit correctly at js1 and js2. He wants them the other way round,
reads a button that says swap, clicks it — and the js1 stick becomes js2,
colliding with the other, or lands on js3. Click again: js4. **The label
promises a swap and the code delivers a counter**, and the result is written to
localStorage, which is why it survived into later sessions and read like drift.

With exactly two sticks connected, values 3 through 8 are never correct. Cycling
into them cannot ever be the right outcome.

## 4. What to build instead

**Make swap actually swap.** With N sticks connected, clicking the control on
one should exchange its slot with another's — for the two-stick case, the only
sane behaviour is js1 ⇄ js2, and both remembered choices update together. Never
assign a number outside 1..N. Never leave two devices holding the same number,
even briefly.

For three or more, cycling through the *occupied* slots is defensible, but it
must stay a permutation of 1..N — every device keeps a distinct number and no
number outside the range is ever produced.

**Keep these, they're right:**

- `if(fromProfile(p)) return;` — an imported profile's own answer is not ours to
  override. Correct as written.
- The refusal when there's no VID/PID to remember against, with a stated reason
  rather than a silently ignored click. Also correct.

**Still do the reconciliation pass** from the original order — as a safety net
that repairs bad stored state from before this fix, including the values already
sitting in Sleven's friend's browser right now. It just isn't the primary bug.

**Still renumber on export** to 1..N regardless of UI state. That was right for
a different reason and it stays right: it makes a bad UI state incapable of
producing an unusable file.

## 5. Acceptance, replacing §5.1–5.2 of the original order

1. Two sticks, fresh profile: they come up js1 and js2. (Already true — confirm
   it isn't broken by the fix.)
2. Click swap on either: they exchange. js1↔js2. No js3, ever, at any point.
3. Click swap ten times: it alternates between exactly two states.
4. Reload: the swapped assignment persists and is still 1 and 2.
5. A localStorage value of 3+ left over from before is repaired to a valid slot
   on load, not obeyed.
6. Export after swapping contains only `js1_*` / `js2_*`, with `<options>`
   instances 1 and 2, and the Product GUIDs following their sticks correctly —
   i.e. the swap changed which GUID is instance 1.

## 6. One line of copy

If the control cycles rather than swaps in the 3+ case, the label must say so.
"click to swap" on a thing that counts to 8 is what sent Sleven round this loop
in the first place.
