# Update — Q26 measured against the deployed payload. The three survivors are real, there are SIX not three, and my instrument was wrong twice before it was right.

**2026-08-29 12:30 local · Code (background session)**

`offhull.py` is not in this repository, so the method was rebuilt:
`checks/_diag_offhull.mjs`. Diagnostic, not a gate - it needs a browser, which
is why C1 kept theirs out of the sweep too.

## THE RESULT, AGAINST THE SITE AS SERVED

    DRAK_Corsair    7 of 15 dots on the hull exactly
      port 94  37px  7.05% of hull span      port 80  18px  3.43%
      port 70  24px  4.57%                   (+ four under 15px)
      port 93  19px  3.62%
    TMBL_Storm_AA   2 of 5
      port 1   17px  2.96%                   port 4   16px  2.79%
    VNCL_Glaive     6 of 9
      port 43  29px  5.33%                   port 44  18px  3.31%

**C1's three all reproduce.** `DRAK_Corsair` 80/93/94, `TMBL_Storm_AA` 4,
`VNCL_Glaive` 43 - every one still off the hull on the payload deployed an hour
ago.

## BUT THERE ARE THREE MORE AT C1'S OWN THRESHOLD

C1's audit named only dots at 15px and above. Applying that same cut to this
measurement finds **three the fleet-wide audit did not list**:

    DRAK_Corsair   port 70   24px
    TMBL_Storm_AA  port 1    17px
    VNCL_Glaive    port 44   18px

**Six, not three.** I am not claiming C1's audit was wrong - it measured 259
hulls at one framing and this measured three at another, and I cannot re-run
theirs. What I can say is that on the served payload these six are off the hull
and three of them are not on anyone's list.

## THE NAMED CAUSE, AND IT IS C1'S HYPOTHESIS CONFIRMED BY EYE

The ringed screenshot shows it: the Corsair's four sit in open space **above the
tail fin, above the wing root, and below the fuselage** - adjacent to the hull,
not on it. Inside the model's axis-aligned box, outside its mesh. **The box is
not the hull**, exactly as C1 said.

**I have not widened the acceptance test and will not.** A containment gate that
passes these is not a gate with the wrong number in it; it is a gate measuring
the wrong shape.

## MY INSTRUMENT WAS WRONG TWICE, AND BOTH WOULD HAVE SHIPPED A WRONG ANSWER

**1. It counted the viewer's own chrome as hull.** "Any pixel that is not the
field colour" includes the Display button, Start spin, the mounts pill and the
drag-to-rotate hint. **A dot over the Display button would have measured as ON
THE HULL.** Caught because the hull's bounding box came back 788px wide on all
three ships - the frame, not the ship - which is impossible. Then confirmed by
looking at the picture rather than the number.

**2. A faint ring on the canvas's own rounded border survived that fix**, about
ten pixels in the outermost column, still holding the bounding box at full
width. Now only the largest connected blob counts as the ship.

Spans went 788 / 788 / 788 -> **525 / 574 / 544**. The distances did not move,
which is luck rather than vindication: for these particular dots the ship was
always nearer than the contamination. It would not always be.

**And a third thing, which is why C1's numbers and mine differ at all:** a pixel
distance is not a property of the ship, it is a property of how big the ship
happens to be drawn. `VNCL_Glaive` port 43 is 16px in C1's audit and 29px here,
and neither is wrong. Every distance is now also reported as a **fraction of the
hull's own on-screen span**, which is comparable between runs.

**Threshold sensitivity checked before trusting any of it:** 6, 12, 18, 30, 50
all give the same ports at the same distances. The answer does not depend on
where the line is drawn.

## STANDING

    Q26  measured. The three are six, the cause is named, and the fix is not
         mine to design - a containment gate that uses the mesh rather than the
         box is C1's pipeline.

New file: `checks/_diag_offhull.mjs`. Probes parked in
`_to_delete/probes-20260829/`. Nothing committed.
