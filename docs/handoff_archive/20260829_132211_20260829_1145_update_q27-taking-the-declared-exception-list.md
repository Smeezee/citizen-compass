# Update — Q27 taken. Declared exceptions, not a re-taken baseline, and C1's reasoning for that is right.

**2026-08-29 11:45 local · Code (background session)**

Sleven said go, Q27 first. Filing before I start, rule 13.

**C1 asked me to choose and said it would not argue twice. I am not choosing
differently: the declared-exception list is correct and re-taking the snapshot is
not.** Absorbing a loss into a baseline is the exact failure
`_verify_marker_census.py` exists to prevent, and it would be the same failure
in my file. A baseline re-taken quietly and one re-taken on purpose look
identical in six weeks; three declared entries that print on every run do not.

**And C1 is right that the red control produced the day's best evidence.**
Section 6 says 244 hulls changed and names exactly three moved markers. A
fleet-wide change to the containment rule moved three markers and nothing else,
with the four pinned negative controls holding. That is worth more than the pass
would have been.

## THE CORRECTION I AM ACCEPTING

Q21's DONE-WHEN said `MISC_Hull_C` port **2**. It is port **34**, the nose
turret. Port 2 is at fore/aft -0.97267, inside the box, and was never an
escapee. **I spent time hunting a port with nothing wrong with it.** C1 has
owned that. What I will note for myself: I reported "port 2 PRESENT" as a
finding without asking whether the number in the order was right, which is the
same trust I would not extend to a check's own output.

## WHAT I AM BUILDING

Three declared exceptions in `_verify_child_markers.py`, each carrying its
reason and printed on every run:

    BANU_Defender 50   cig -1.32494 fore/aft  -> REMOVED
    BANU_Defender 51   cig  1.32494 fore/aft  -> REMOVED
    MISC_Hull_C   34   cig -1.27827           -> demoted to est -1.00356

**The third is not a removal and must not be declared as one.** The mount kept
its marker; the CIG position was withheld and it fell back to a name-derived
estimate the page now labels `est`. A control that calls that "removed" would be
recording the wrong event.

Rule 12 applies: the list has to be proven not to hide a fourth. I will plant a
loss that is NOT declared and confirm the control still goes red.
