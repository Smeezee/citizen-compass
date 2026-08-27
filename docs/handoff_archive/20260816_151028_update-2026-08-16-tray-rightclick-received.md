# Update - received: the tray right-click has never worked. pilot_dps paused.

Taking the tray defect ahead of the pilot_dps viewer work, which is paused after
reading the data (167 ships, 143 carry pilot_dps, 24 do not - matching the order's
numbers; the per-hardpoint link needs the gun nested inside the mount, which
`hardpoints_fleet.json` does not carry and `ship_mounts.json` may). Nothing in
`testing/` has been touched.

My earlier diagnosis was wrong and I am not defending it. I attributed a dead
right-click to my own HWND_MESSAGE change and reverted it as the fix. Sleven says
it never worked on any version, including builds that predate HWND_MESSAGE
existing in this codebase, so the revert cannot have been the fix and the
reasoning that produced it was reasoning from source rather than from observation
- the exact failure this project keeps finding.

Root cause to be OBSERVED, on the three things named: whether the menu is ever
created, whether the tray window receives the notification at all, and whether
the owner window can take the foreground (TrackPopupMenu does nothing, silently,
when it cannot).

The testing blocker is mine to solve and I will not report it again as a reason
for not knowing.
