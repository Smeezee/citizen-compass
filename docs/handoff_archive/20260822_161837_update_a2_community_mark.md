# Update - A2, the "Made By The Community" mark

A2 done. Applier, pixel-level detector, and a build that refuses to finish while
a CIG-sourced image is missing the mark.

- `scripts/community_mark.py` composites the Fan Kit mark bottom-right at 70%,
  following the hologram-concept precedent rather than inventing a second
  approach. CIG's prohibitions are structural, not commented: one scale factor
  for both axes so it cannot be distorted, never transposed so it cannot be
  flipped, its own pixels copied so it cannot be recoloured, nothing drawn on
  top. Below CIG's 50% opacity floor it raises instead of clamping.

- MY FIRST DETECTOR WAS WRONG, and measuring it is what found that. The obvious
  statistic - "is the corner brighter where the mark is opaque" - scored 5.36 on
  a mid-grey fixture against 57 and 68 on dark and light ones. The mark is not a
  flat silhouette: 72% of it is opaque and that region averages luminance 113,
  mid grey. It would have reported the mark MISSING on exactly the mid-tone
  images a ship render actually produces. Replaced with correlation against the
  mark's own structure: marked 0.968-0.999, unmarked at most 0.021.

- The negative control RUNS THE REAL BUILD, not a copy of the guard: an unmarked
  CIG-sourced image makes build_deploy.py exit 1; the same image marked makes it
  exit 0.

- THAT CONTROL SCORED A FALSE PASS ON ITS FIRST RUN. Registering a CIG asset
  also trips A3's contact gate, so the build failed before ever reaching the
  mark guard - and "an image without the mark is refused" went green. Refused,
  but for the wrong reason. It now supplies a contact and asserts which refusal
  it got. Ninth silent-success instance logged.

## Reported, not fixed - hard rule 8

The 241 ship thumbnails already on the site do not carry the mark.
`docs/workorder-image-provenance-and-renders.md` establishes that the upstream
pack is governed by terms naming "Made by the Community", and equally that it is
NOT established whether any individual image is a CIG asset, a screenshot or a
render. Marking all 241 is a bulk mutation of the site's whole visual surface
(rule 5) on a Fan Kit compliance question (rule 8 - report it, do not fix it),
and Part 2 of that same work order plans to replace every one of them with our
own renders. That is Sleven's decision, not one I take silently.

The mark file itself is NOT committed to the repo - it is read from the Fan Kit
on disk or from CC_FANKIT_DIR. Copying a CIG asset into a public git repo is a
separate decision from the one already taken.

Next: A4, the off switch - the item the order says matters most.
