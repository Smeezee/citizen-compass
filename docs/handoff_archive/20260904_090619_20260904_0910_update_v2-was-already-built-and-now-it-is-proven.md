# Update — V2 was already built. What was missing was the control, and it is written.

**2026-09-04 · Code**

## I did not write V2. C1 already had.

Sleven authorised V2 as one change. Before writing anything I read the code, and
**the whole of V2 is already in `testing/_src/loadout.src.html`** and has been
since 2026-08-30 - `mountRoot()`, `mountsFor()`, the multi-weapon list, and the
count line rewritten to say mounts and weapons. It went out in my 09-02 deploy
and **is live on testing now**: the served page carries `function mountRoot`,
six references to `mountsFor`, and the footer "One dot per physical mount."

**The change I was about to make would have been wrong.** I had planned to group
the markers in `build_deploy.py` - my own file, which is why it looked safe.
C1's design deliberately does the opposite: **every port keeps its marker in the
generated data**, and only the DRAWN dots are grouped. Grouping at the generator
would have destroyed the per-port markers `onStage()` and the picker depend on,
and no per-ship count would have revealed it, because the counts would have come
out right.

Reading first cost ten minutes. It would have been a day to find afterwards.

## The order's table is measured against data that has since moved

The order's numbers were taken when the fleet held 3,707 markers on 165 hulls.
It now holds **6,019 on 259**. So the absolute figures cannot match, and I am
reporting what is actually true rather than the table:

    fleet          6,019 port markers  ->  2,188 mounts drawn   (63.6% fewer)
    median hull       19 -> 7
    hulls over 40     32 -> 0

The order predicted 63.2% fewer, median 17->8, over-40 21->0. **Same shape, and
the per-ship targets land exactly:**

    Harbinger  34 -> 13  (order: 13)     Idris-M    92 -> 30  (order: 30)
    Polaris   131 -> 29  (order: 29)     Asgard     42 -> 15  (order: 15)
    Hammerhead 92 -> 18  (order: 18)     Retaliator 24 ->  9  (order:  9)
    Vulture     6 ->  4  (order:  4)

Seven of eight exact. The eighth, the **Perseus**, reads 17 where the order said
37 - and its port count is 65 today against the order's 105. Its data changed;
the rule did not. Named rather than rounded away.

**The Polaris line now reads: `29 mounts · 131 weapons · 23 labeled, 6 with no
room`.** The order's complaint was "133 hardpoints · 95 have no room".

## What was actually missing: nothing asserted the wording

The grouping is covered - `_verify_label_threshold.mjs` proves no weapon is lost
to it. **The count line's wording was covered by nothing.** `renderLabelCount()`
could be reverted to `${total} hardpoints` and all 113 controls would have
stayed green while every busy hull under-reported its guns by a factor of four.

One assertion wide, and it is the half of the order that says "the count line
must stay honest".

**Written: `checks/_verify_count_line.mjs`. RULE16: INDEPENDENT** - it derives
the expected mount and weapon counts from the raw PortId paths with its own
implementation of the grouping rule, and compares them against the text the page
rendered. It never calls the page's `mountsFor()`, so agreement means something.

**8 assertions, and it chooses its exemplar hulls from the data** rather than
naming a ship whose numbers will move - the trap `_verify_label_threshold.mjs`
already fell into once, by hard-coding a literal 9 that later named a different
hull's answer.

**Proven against known-bad input. Both mutators exit non-zero:**

- `--mutate-oldcount` - the line goes back to "N hardpoints" always. Caught: the
  Polaris reads `29 hardpoints`, and three assertions fail.
- `--mutate-nogroup` - `mountRoot()` stops grouping. Caught twice over: the line
  reads **`131 hardpoints · 103 with no room`**, which is the original defect
  reproduced exactly, and section 3 reports the page disagreeing with this
  file's own grouping on the first hull it reaches.

Section 3 also re-proves fleet-wide what the order promised: all 259 hulls group
identically under two separate implementations, and **every one of the 6,019
port markers is still reachable through a mount.** Grouped, not dropped.

## State

Nothing deployed - V2 was already live and the new control is not part of the
payload. Full sweep running to confirm the control integrates; the runner
discovers `checks/_verify_*.mjs` by glob, so it is swept without being listed
anywhere.

`checks/_verify_count_line.mjs` is a new file under `checks/`, which OWNERS.md
makes Code's by default. No C1-owned file was touched for this.
