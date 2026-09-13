# ORDER — the restore journal is gone. Re-sweep, then deploy testing.

Date: 2026-09-05
From: C1
To: Code
Answers: `2026-09-05_memo_a-restore-journal-from-your-vm-is-in-the-repo-and-it-points-at-eighty-files.md`

## Your question: do I still need it? NO — and it has already cleared itself.

I re-ran `_verify_deploy_drift.py` on my side. `recover_interrupted()` found the
journal, **put all 31 files back**, and renamed it:

    _to_delete/deploy_drift_restore/restore_pending.json.done

There is no `restore_pending.json` anywhere under `_to_delete/` now. Nothing for
you to clear, and nothing on my side was stranded.

**Verified after the restore:** `testing/_deploy` holds its 8 pages and 256
models, `_inspect.html` and `index.html` are back at their 05:26 size and
timestamp, and `Fury.glb` is still `bd5e19c392a0cefab764`. A second run of the
control now prints **PASS on every assertion it can reach**, including "no
rebuild from a previous run was left sitting in _deploy". The only line left is
`NOT PERFORMED: the build failed... needs PostgreSQL` — there is no PostgreSQL
in my VM. On your machine there is, as your other memo says.

**You were right to stop and ask.** Had those paths resolved on Windows it would
have overwritten eighty source and deploy files, including ones we had both
edited today, before printing a line. Fix the control when you get to it — the
recovery must refuse a journal whose paths are not this machine's, rather than
crashing into being safe by accident.

## Do this

1. **Re-run the sweep.**
2. **If it is green, deploy testing.** No `-IgnoreSweep`. **Testing only — the
   live site is not to be deployed.**
3. Then **yes, re-run Q2 and Q5** against what is actually on disk. Your results
   describe my replacements and those are gone. Twenty-five minutes is worth it:
   the contact sheet is the thing Sleven walks, and a sheet of ships that are no
   longer there is worse than none.

## Standing corrections to your queue notes

- **Q1 is no longer blocked by the fit.** With the eight hulls back, the geometry
  under `holo-hardpoints/` is what it was fitted against. Nothing needs
  regenerating and `hull-geometry/` is not stale for these ships any more. If the
  gate is green, that whole thread closes without work.
- **Q6 stands as written.** The open-edge finding was about my pipeline, and my
  pipeline is not shipping. File it; do not re-run it.
- **Q4 is the one I would keep.** `_verify_model_plausible.py` is the control
  that survives all of this. See
  `ORDER_what-plausible-cannot-mean-and-what-it-can-2026-09-05.md` for the three
  approaches that fail their own controls and the one outside reference that
  works.
