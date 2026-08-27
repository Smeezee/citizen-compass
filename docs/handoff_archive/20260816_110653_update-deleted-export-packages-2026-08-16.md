# Update: deleted the leftover export packages. 3.9 GB back.

`_to_delete/failed_export_packages_20260815/` removed on Sleven's explicit
instruction - three zips, 0.76 GB + 1.59 GB + 1.59 GB.

**Checked before deleting, not after:** 695 PNG frames are still in
`captures/` (1.8 GB). Those packages were derived from data that is still on
disk, because a failed send clears nothing. Deleting them lost nothing.

    _to_delete: 6.9 GB -> 2.9 GB

## I asked which folder rather than guessing

`_to_delete` holds ~30 folders, not one, and several are large and none of mine:
1.6 GB `source1_git`, 1.1 GB `collector_deadweight`, 281 MB starmap test run, the
sidecar backups from the scrub. "The folder" most likely meant the one I had just
flagged, and it did - but the cost of guessing wrong there is permanent, so it
was worth one question.

**Everything else is untouched**, including `webview2_path_retired_20260815/`
(80 KB), which also has a copy in git history since those files were committed
as deleted.

## The thing that stops this recurring

0.3.3 removes the package when it is finished with it, so a failed send no longer
leaves an artifact. These three predate that fix. There should never be another
pile like this to delete.
