# UPDATE — Fixed the ship_registry.json checker encoding bug (2026-07-30)

One-line fix in `checks/db_checks.py:128`: `registry_path.read_text()` -> `registry_path.read_text(encoding="utf-8")`. This was the false-positive DEFECT flagged in the Phase 1 audit - on Windows, `read_text()` with no encoding falls back to cp1252 and crashed on the "a with macron" in the real ship name "San'tok.yai".

Re-ran `run_checks.py --group all` after the fix to confirm: DEFECT dropped from 1 to 0. The `registry_sync` check now runs to completion instead of crashing, and correctly surfaces as 2 real WARNING findings - 62 DB ships with no ship_registry.json entry, 108 registry entries with no DB row (the same numbers found manually in the Phase 1 audit, now detected automatically by the checker itself going forward instead of needing a manual workaround).

Total findings now 28 (0 DEFECT, 4 WARNING, 8 LIMITATION, 16 PASS). Not committed/pushed - working tree change only, waiting on a go-ahead.
