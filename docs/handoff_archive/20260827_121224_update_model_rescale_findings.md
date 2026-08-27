# UPDATE — Model rescale run found missing/corrupt 3D assets (2026-08-27)

Ran the sc-ships/ rescale-to-0.01 pass across 19 ship folders. 1 were already correct, 18 got rescaled cleanly. 0 ship(s) have a real problem with their model.glb (missing, empty, or unreadable) and need real 3D source files before they can be rescaled or used.

Also missing a preview image only (cosmetic, non-blocking): 19 ship(s).

Full details: `_needs_review\model_rescale_missing_assets__20260827121221.md` (per-ship table) and `model_rescale_report__20260827121221.json` (machine-readable). This is also now a permanent checker (`missing_or_corrupt_3d_model_check` in checks/file_checks.py) so future audit runs catch this automatically going forward, not just this one-off rescale pass.
