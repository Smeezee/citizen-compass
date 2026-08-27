# Update — M2 first cut. The swap loop's fourth step exists now: KEEP OR UNDO.

**C1, 2026-08-27 16:58 local.** `testing/_src/loadout.src.html`. `node --check`
passes. Not built or deployed — that is yours.

## What was missing, and it was the last quarter of the brief

Sleven's brief describes four steps: *pick a part, understand what it does, see
what it changes, **keep or undo**.* The page shipped the first three.

**"Back to stock" is not undo, and the difference is the whole point.** It
throws away every change at once. A person who made six swaps and regretted the
sixth had exactly one option: **lose all six.** So the cost of trying the sixth
swap was the five before it — and a page whose entire argument is *experiment*
was quietly charging for experiments.

The comment above that button already said *"failure has to be free or nobody
experiments, and experimenting is how this page teaches."* **The button just
did not deliver it.**

## Three things, all in my file

**1. `Undo`** — one action, one swap back. Also **Ctrl+Z**, because it is what
everybody tries first and costs one line. Guarded off inputs and textareas so
it can never steal an undo from a text box.

Undo **selects the port it just changed** rather than clearing the selection.
An undo that shows nothing is indistinguishable from the page losing your work.

**2. A change ledger** — one row per port that differs from stock, with the
part's name, what it replaced, and its own `revert`. Clicking the name selects
that port so you can look at what you did, not just read that you did it.

**Derived from the BUILD, not from the log**, deliberately. The log is history
and undo empties it; *what have I changed* has to stay true however the build
got here — **including a build restored from a shared link, which has no log at
all.**

**3. `revert` is logged like any other swap**, so undoing a revert works. If it
wrote the build behind the log's back, Undo would walk backwards into a state
that never existed.

Undo appears only when there is a swap to undo — **not** when the build merely
differs from stock. Those are different questions, and a shared link is the
case that separates them: it differs from stock with no history, and offering
Undo there is a button that does nothing.

`Back to stock` now clears the log with the build, for the same reason.

## One defect I made and caught before filing

The ledger named `PARTS[id]`. **The page's part table is `P`.** `PARTS` does not
exist, so every row would have rendered a raw class name — and it would have
looked like missing data rather than a typo, which is the expensive kind of
wrong. Fixed, and the reason is written into the line.

## What I want from you

Build, deploy, and **a check with a control that can fail**:

    swap a part, assert the ledger shows one row and Undo is offered
    press Undo, assert the build is back and the ledger is empty
    THE CONTROL: seed a build from a shared link (no history) and assert
      Undo is HIDDEN while the ledger still shows the changes

That last one is the assertion I would most like an independent opinion on. It
is the case I reasoned about rather than observed, and if it is wrong the page
offers a dead button to every person who follows a shared build.

*C1*
