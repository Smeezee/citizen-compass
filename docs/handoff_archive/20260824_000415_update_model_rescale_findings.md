# UPDATE — Model rescale run found missing/corrupt 3D assets (2026-08-24)

Ran the sc-ships/ rescale-to-0.01 pass across 246 ship folders. 0 were already correct, 238 got rescaled cleanly. 1 ship(s) have a real problem with their model.glb (missing, empty, or unreadable) and need real 3D source files before they can be rescaled or used.

1 ship(s) have a candidate sibling model but NOT auto-copied - the evidence wasn't strong enough (different file sizes between trim variants, proven in this repo to mean different hulls): Fury. See the needs-review doc for candidates.

6 ship(s) have no sibling model anywhere in this repo, need real source data: 85X, Arrastra, Mantis, Merchantman, PTV, _corrupt_backup

Ships needing a new/replacement 3D model file:

- `C:\Users\david\AppData\Local\Temp\claude\C--Users-david-citizen-compass\56eed803-6938-4cf6-aeac-6c54abf4dd5a\scratchpad\sc-ships-dryrun\Asgard` — model.glb: File exists but Blender could not import it: Error: Couldn't parse glTF. Check that the file is valid


Also missing a preview image only (cosmetic, non-blocking): 238 ship(s).

Full details: `_needs_review\model_rescale_missing_assets__20260824000412.md` (per-ship table) and `model_rescale_report__20260824000412.json` (machine-readable). This is also now a permanent checker (`missing_or_corrupt_3d_model_check` in checks/file_checks.py) so future audit runs catch this automatically going forward, not just this one-off rescale pass.
