# Update - both committed

- `22d4391` **Three concrete cases, so the shape comes from what they needed** -
  the hull/configuration/routes ruling's first build: Drake Clipper, Aegis
  Tiburon, Aegis Sabre Firebird, plus the verifier and the write-up. No schema,
  no migration, no field on `Ship`.
- `7c9c119` **The hardpoints were always there, under a name that did not join** -
  29 ships recovered, 196 rendering, the DRACO decoder, the placement port and
  its check against C3's own output, the join verifier, and both findings.

Not pushed. `b3ef396` is still the last thing on origin.

Left in the working tree and NOT part of either commit, because they are not
mine and predate this session: `LATEST_HANDOFF.md`, `app/models.py`,
`build_kb_actions.py`, and the handoff-archive changes and deletions.

Still waiting on a human rather than on me:

1. **Left-click opening the collector window.** Right-click is confirmed; the
   left-click rule landed afterwards and only the probe has seen it.
   `citizen-collector\probe.exe -tray-probe` holds an icon for three minutes
   alongside the running collector and reports NOT TESTED if nothing arrives.
2. **The Hercules 29-vs-41 difference** - worth taking back to C3, since the
   number in the finding does not match the dataset the viewer reads.
