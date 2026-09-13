# Build update - B1 is green and rebuilds after every sweep; one runner defect found and fixed

**Code (Build), 2026-09-12. Clock read at 18:09:37.** This is the one short update Sleven asked for.

## B1: DONE

- **`checks/record_audit.py`**, auditor layer. It flags only, never gates, and never fixes.
  - The self-test passes all 11 plants, and all 8 mutations are caught, each restored byte-identical.
- **Hooked to run after every full sweep** in `checks/run_all_controls.py`. The 18:07 sweep ran it by itself, and it printed "record audit: 58 findings, 0 dispositioned, 0 stale, 555 baseline; 1116 companion notes; 2.69 s".
- **Outputs:**
  - `logs/record_audit.md` and `logs/record_audit.json`
  - `_links/`: 1,116 companion notes and 3,166 edges, gitignored
- **Cost:** 2.7 to 2.9 s per run. The first run took 8.7 s because it wrote all 1,111 notes at once.
- **Fixed on the way:** the tool's own chat log `.aider.chat.history.md` was being read as record. Dotfiles are now skipped, with a plant and a mutation to hold that.

## FOUND ON THE WAY, AND FIXED IN MY OWN FILE

- **The 18:07 sweep went red on `_verify_correspondence.py`, and it was a CRASH, not a finding.** It printed a letter subject containing "→" (Sleven's "B1→B2→B3" letter) to a cp1252 stdout.
- **The cause was the runner:** it decodes a check's output as UTF-8 but never told the check to write UTF-8.
- **The fix is one argument** in `run_all_controls.py`: the child gets `PYTHONIOENCODING=utf-8`.
- **Proof:** `--only _verify_correspondence.py` now passes, where the full sweep crashed on the same letter.
- **The main receipt stays red (18:07, 129/1) until the next full sweep.** No deploy is pending.

## HELD, PER SLEVEN'S "STOP AFTER B1"

Architecture's owner-ask control (red) and the skill-mirror control are both ruled and not started. **Either can go on a word.**

**Uncommitted, and Code files need Sleven:**

- `checks/record_audit.py`
- `checks/run_all_controls.py`
- `checks/file_checks.py`
- `checks/_verify_document_checks.py`
- `.gitignore`
