# Update — deployed. The inspector is live with both notices.

**2026-09-04 · Code**

Version ID `8bddb786-6696-4450-9a29-f4737552bd68`. Testing only; the live site
was not touched.

**Sweep vouched for it first: 116 ok, 0 failed, 3 skipped**, payload
`2032094ea51222bd`. No `-IgnoreSweep`.

## Verified from the served bytes

    /_inspect.html -> /_inspect   200, 1,155,664 bytes
    byte-identical to testing/_deploy/_inspect.html : True
    trademark strip  : present
    source notice    : present
    takedown line    : present
    models/Hammerhead.glb  200, 4,153,816 bytes

Cache-busted, and the redirect followed - `_inspect.html` 307s to the
extensionless `/_inspect`, the same as the other pages.

**All three deployed-only controls pass**, which is the first time today:

    _verify_deployed_links.mjs   EXIT=0
    _verify_find_deployed.mjs    EXIT=0
    _verify_picker_deployed.mjs  EXIT=0

`_verify_picker_deployed.mjs` had been red since the glossary entered the build.

## What went out

- **The inspector**, with the source and takedown notice - the point of the
  order. My `_SHIP_CONTENT_PAGES` line is doing its job.
- **C1's see-through fix**: hulls drawn double-sided, 3,287,114 of 139,487,571
  triangles no longer culled, visible on 32 hulls.
- The source notice on all four ship-content pages; correctly absent on
  `find.html`.
- Everything from earlier today that was already built: F1/F2/V1 camera, V3,
  C2b's self-reading patch stamp, the leaked-comment fix.

## Standing, and not mine

- **The 241 thumbnails are deregistered**, pending the unanswered question of
  whether they are CIG assets, screenshots or renders. The mark guard is armed
  with nothing to check and `_verify_community_mark.py` passes 13 of 13.
- **The glossary marks 0 of its 31 terms** on both pages, and the control that
  measures it reports without failing.
- `docs/see-through-ships-2026-09-04.html` is waiting on Sleven's exception
  list - which ships, if any, should stay see-through.

## For Sleven

    https://citizencompasstesting.citizencompass-contact.workers.dev/_inspect.html
