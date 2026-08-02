# UPDATE — Model rescale run found missing/corrupt 3D assets (2026-07-30)

Ran the sc-ships/ rescale-to-0.01 pass across 242 ship folders. 0 were already correct, 234 got rescaled cleanly. 1 ship(s) have a real problem with their model.glb (missing, empty, or unreadable) and need real 3D source files before they can be rescaled or used.

Chassis cross-reference auto-copied 4 model(s) from a sibling ship that shares the same hull (livery/edition variants only, provenance noted in each folder's MODEL_SOURCE.txt): Caterpillar Pirate Edition <- Caterpillar, P-72 Archimedes Emerald <- P-72 Archimedes, Pulse <- Pulse LX, Ursa Fortuna <- Ursa

1 ship(s) have a candidate sibling model but NOT auto-copied - the evidence wasn't strong enough (different file sizes between trim variants, proven in this repo to mean different hulls): Fury. See the needs-review doc for candidates.

6 ship(s) have no sibling model anywhere in this repo, need real source data: .cache, 85X, Arrastra, Mantis, Merchantman, PTV

Ships needing a new/replacement 3D model file:

- `sc-ships\Asgard` — model.glb: File exists but Blender could not import it: Error: Couldn't parse glTF. Check that the file is valid


Full details: `_needs_review\model_rescale_missing_assets__20260730183923.md` (per-ship table) and `model_rescale_report__20260730183923.json` (machine-readable). This is also now a permanent checker (`missing_or_corrupt_3d_model_check` in checks/file_checks.py) so future audit runs catch this automatically going forward, not just this one-off rescale pass.
