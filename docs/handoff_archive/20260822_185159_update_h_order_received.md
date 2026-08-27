# Update - hologram order received; promoting B5/B6 first, then H1-H9

`docs/ORDER_every-ship-is-a-hologram-2026-08-22.md`. Nine items, run
continuously. B0 is already done, so it runs straight through.

## Before H1, on Sleven's instruction: promote the B5/B6 placement

I held this back at the end of the B run because a local placement run does not
byte-reproduce the committed `hardpoints_fleet.json`. Sleven's call is to
promote: the derivation changed, the dataset did not, and the markers are still
in this morning's positions.

I will report the delta **decomposed**, because the promotion carries two
different changes and lumping them together would hide one:

- **committed -> new**: what actually ships. Includes the vertex-subsample
  difference, which is not B5 or B6 - it is that the geometry was decoded again
  on this machine.
- **my before -> my after**: B6's isolated effect, geometry held constant.
  Already measured: 143 points aimed at a measured extremity, 118 moved on 55
  of 167 ships, median 0.074 of half-extent, crowding 118 -> 117.

The B6 controls are held: **crowding must not get worse**, and a hull already
close to the fixed fractions must barely move. The current file gets moved aside
to `_to_delete/`, not overwritten in place (rule 1).

## The order itself, and the part that changes its shape

Sleven's framing was that RSI's models unblock the hologram look. **They do not,
and nothing does - it was never blocked.** The texture problem is not solved by
finding textures, it is dissolved by not needing them.

Measured on this machine before I start:

    316  ships in the data
    235  .glb model files on disk
    201  ships wired to a model
    115  ships rendering NOTHING
     40  model files on disk wired to no ship at all

Forty models we already own, pointing at nobody. The order names this as the
same defect that hid the Ares Inferno for a week: **a name-matching failure, not
a missing asset.**

## The rule I am holding hardest

**NO FUZZY MATCHING in H2, H3 or H4.** The order records four confident wrong
pairs it has already produced - Dragonfly Black->Yellowjacket, E1 Spirit->C1
Spirit, G12a->125a, Zeus MR->Zeus ES. Exact normalised name, then ClassName,
then stop and report the residue. Manufacturer is asserted as an independent
field on every claimed pair: a Drake file matched to an Aegis ship is wrong
however good the name looked.

**H5 is the deliverable that matters** - the real list of ships with no geometry
in any of the three libraries, as names, not a count. Nothing about RSI gets
fetched, and nothing gets asked of them until that list exists.

Starting with the promotion.
