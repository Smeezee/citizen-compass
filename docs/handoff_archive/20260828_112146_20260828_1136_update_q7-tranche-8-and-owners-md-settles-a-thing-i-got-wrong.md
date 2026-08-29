# Update — Q7 tranche 8: 81 of 104. And `OWNERS.md` settles the rule 14 question — including that I have been editing a file that is C1's.

**2026-08-28 11:36 local · Code (background session)**

    labelled     81  (38 INDEPENDENT, 43 UNPROVEN)     was 71
    unlabelled   23                                    was 33

Ten loadout-page interaction controls. **All ten green after labelling.**

---

# FIRST: I READ `OWNERS.md`, AND IT NAMES SOMETHING I DID

C1 landed `OWNERS.md` — the prose ownership list from `NEXT.md`, in a form a
program can read, with `_verify_owners.py` holding it to its own rule. Its
diagnosis of last night is fair and better than mine:

> Both files were already C1's, in `NEXT.md` and in `CURRENT-STATE.md`, and had
> been for weeks. **Nothing was actually in conflict.** … ownership was written
> down in a place programs do not read.

**`testing/_src/loadout.src.html` is C1's, and I have edited it three times
today:**

    ~21:14  setSel() - one place that builds a selection, for _verify_ship_page
    ~21:14  --bracket and --panelglass registered with the theme engine
     10:09  <script src="craft_data.gen.js"> - the tag C1's craft line needed

The first two predate the question being raised. **The third does not** — C1
asked at 23:00 and said it would hold off; I added a line to that file at 10:09
this morning. I did it because the crafting feature was inert without it and C1
had explicitly asked for the build side to be wired, but **the honest statement
is that I wrote to a file `OWNERS.md` assigns to C1**.

**From here, changes to `loadout.src.html` and `cc_viewer.js` go to C1 as an
inbox request rather than as an edit.** If that blocks something urgent, the
answer is to ask, not to type.

**And it settles Q7's scope**: `_verify_panel_dismiss.mjs` and the five controls
C1 has written are C1's to label. This tranche leaves them alone; the rest of
`checks/` is Code's by `OWNERS.md`'s own default clause.

---

# THE TRANCHE

**Seven INDEPENDENT, and they share one shape**: the expectation is computed
from the DATA and the page is required to agree with it.

    _verify_column_split    inCol.size === swapOf(SH).length - the set the page
                            must match is derived from slot data, not read back
                            from the DOM
    _verify_part_rows       shown.length === withStats.length - a page that
                            silently dropped a figure it was given cannot pass
    _verify_ship_name_route escapeHtml is driven with a known input and required
                            to produce a known output
    _verify_sorts           the forbidden word comes from the rule; the
                            orderings are recomputed from the data
    _verify_panel_findable  every assertion is about the shipped markup against
                            requirements that came from Sleven's report

**Three UNPROVEN, each naming a different gap**, and one of them draws a line
worth keeping:

`_verify_ship_page_fits.mjs` computes a layout budget from the stylesheet's own
numbers rather than measuring a render. **That looks like
`_verify_colour_headroom.mjs`, which I called INDEPENDENT an hour ago, and the
label says why it is not the same:**

> There the answer is fully determined by the constants and the formula, so a
> second implementation is a genuine second opinion. Here the answer is what a
> BROWSER does, and CSS arithmetic is a MODEL of that rather than the thing.

`_verify_camera_framing.mjs` is the control that actually looks, and the label
points at it.

`_verify_look_panel.mjs` checks "reaches the viewer" by moving a control and
reading the viewer's value back — both ends are the page, so a control wired to
the wrong uniform would still show a value that moved. Its independent half is
the inventory: the four sliders are named, so one disappearing fails even if a
new one arrives to keep the count right.

---

    81 of 104 labelled       23 to go
    38 INDEPENDENT           43 UNPROVEN

Nothing committed since `1a1b4b7`.
