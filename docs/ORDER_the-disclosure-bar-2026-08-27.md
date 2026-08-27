# ORDER — the disclosure bar, everywhere

**2026-08-27 · C1 · for Code · approved by Sleven**

Sleven, on seeing the loadout page's provenance box redesigned: *"yes i like
this — use this on set up on everything like this on the website."*

**One pattern, one implementation, used on every explanatory block on the
site.** Not five variations that drift apart.

---

## The problem, in one sentence

**This project explains itself better than any competing tool, and it does it
by putting walls of prose permanently on the page.** The loadout page's
provenance block eats roughly 90 px of the 3D stage on every ship, forever —
and at 1000 px viewport height it is **clipped mid-sentence**, so the paragraph
arguing for full transparency is itself unreadable.

The explanations are good. Their delivery is not.

---

## The pattern

### Collapsed — one bar, and it must still be USEFUL

    [ PATCH 4.9 ]  from Star Citizen's game files · scunpacked 20260801T204744Z    Where these numbers come from ›

Three parts:

1. **A stamp** carrying the single load-bearing fact — the patch, the source,
   the count. Monospace, high contrast, unmissable.
2. **A quiet source line** naming where the data came from.
3. **The opener**, right-aligned.

**A bar that says only "More info ›" is a worse version of what is there
today.** Somebody who never clicks must still learn the two things that matter.
That is the whole reason this is a bar and not a triangle.

Target height: **~38 px**, against ~90-and-clipped today.

### Open — a panel that is laid out, not a paragraph dump

- **Sections side by side**, not one column of prose.
- **The numbers come out of the sentences and become figures.** `316 ships ·
  3,283 components · 27 types` and `7,874 can change · 18,126 fixed` were
  buried mid-paragraph and nobody read them. They are the most concrete thing
  in the block.
- **Where the text explains a piece of UI, show that piece of UI.** The
  CIG-versus-summed section renders the actual `CIG` and `SUMMED` chips, so the
  explanation and the thing explained look the same.
- **Not one word is dropped.** Same sections, same claims, same caveats.

C1 holds a working prototype of both states and can supply exact values.

---

## WHICH blocks collapse — and this is the load-bearing rule

**Collapse a block that EXPLAINS.**
**Never collapse a block that WARNS, that reports an ERROR, or that states
WHAT THE VISITOR IS LOOKING AT RIGHT NOW.**

Applied:

| block | verdict |
|---|---|
| `Where these numbers come from` (loadout, find) | **collapse** — explanation |
| `Showing 14 of 15 weapon mounts…` (loadout, over the stage) | **split** — see below |
| `Read this as a matchup, not a rating` (loadout compare) | **collapse** |
| `What this data does not say` (loadout) | **collapse** |
| `Where the shop data actually is` (loadout) | **collapse** |
| `Reading this panel` (keybinds, index) | **collapse** |
| `UNATTESTED is not rejected` (keybinds) | **collapse** |
| `Known non-purchasable ships` (index) | **collapse** |
| `The download is not available` (find) | **NEVER** — error state |
| `We don't have that item` / `that terminal` / `Nothing is listed here` (find) | **NEVER** — empty states |
| `The price data did not load` (find) | **NEVER** — error state |
| `Your antivirus may quarantine it` and everything under it (download) | **NEVER** — a warning about the visitor's own machine |
| `Ctrl+Alt+Del` / `Windows key` / capture warnings (keybinds) | **NEVER** — they explain why a control will not work while the person is trying to use it |

**The split case.** `Showing 14 of 15 weapon mounts` states what you are looking
at AND then explains why in four sentences. **The count stays visible; the
explanation collapses:**

    14 of 15 mounts shown · why? ›

That block currently sits across the bottom of the 3D stage, which is the one
surface this site has that nobody else does.

---

## Inventory — 13 amber blocks across four pages

Located by the amber treatment's own tokens (`#1A1206` ground, `#6B4C12`
border):

    keybinds.html   x5
    index.html      x4
    loadout.html    x2
    find.html       x2

**Audit every one against the rule above before changing any of them**, and
record the verdict per block. A block collapsed that should not have been is a
warning nobody reads.

---

## Rule 12 — two controls, both able to fail

**D1 — no warning is ever collapsed.** Assert that every block carrying the
never-collapse treatment renders open, on every page. Mutation: collapse the
download page's antivirus notice; the control must go red.

**D2 — no collapsed bar is empty of fact.** Assert that every collapsed bar
carries at least one stamp value AND a source line, not just its opener label.
Mutation: strip the bar down to `More info ›`; the control must go red.

D2 is the one that matters. **The failure mode here is not a bug, it is a
gradual hollowing-out** — each bar getting a little less informative until the
site has traded its best quality for tidiness.

---

## Sequencing

**After the hardpoint picker.** Both touch the loadout page and one of them is
already specified and approved with an acceptance test.

Do the **loadout page's provenance block first** as the reference
implementation, get Sleven's eye on it live, then apply outward to find,
keybinds and index.

Do not deploy the live site. Testing only.
