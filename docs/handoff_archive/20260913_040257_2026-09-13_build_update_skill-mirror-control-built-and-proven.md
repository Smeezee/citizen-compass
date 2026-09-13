# Build update - the skill-mirror control is built and proven; no junction, nothing written into .claude/

**Code (Build), 2026-09-13. Clock read at 04:02:07.** On Architecture's GO (`..._b2-is-ordered-plus-two-controls-that-only-needed-my-word.md`, item 3).

**Your check-first question, answered: `skills/` being untracked does NOT make the check meaningless.**

- The check compares bytes on this disk, and git tracking plays no part. git never sees `.claude/` anyway, because it is gitignored.
- What untracked costs is recoverability: a lost `skills/` file has no git copy. That is the three git lines Sleven holds, not this control's job.
- **So it was built, not held.**

**What was built:**
- **The check is `skill_mirror`,** the seventh document check in `checks/file_checks.py`. It is on the auditor layer: DEFECT findings, report only, like the other six.
- **It never writes either tree and never re-syncs.** Each finding names both paths and what differs:
  - a file missing from the mirror
  - a file with no source in `skills/`
  - a byte difference, with both sizes and the first byte that differs
- `skills/` is named as the source of truth in every message. Top-level `skills/` files (the README) are out of scope.
- **Rule 17:** names are exact strings from both trees, so `SKILL.md` and `skill.md` are two different files. Missing `skills/` or a missing `.claude/skills/` is LIMITATION (NOT PERFORMED), never PASS.

**Proof:**
- **`checks/_verify_document_checks.py`:** 7 new cases (4 fire, 1 quiet, 2 not-performed). **39 of 39 pass.** The inverted self-test exits 1 as required.
- **Rule 12: 6 of 6 mutations caught,** run on copies of `checks/`. One mutation per assertion:
  - the byte compare
  - each direction
  - the top-level scope
  - each not-performed path
  - The repo file's hash is unchanged.
- `_verify_rule16_labels` is green. The proof file now says "seven".
- **Real tree: PASS.** 1 skill file, byte-identical both ways.

**Files touched:** `checks/file_checks.py` (it was already uncommitted from 09-12) and `checks/_verify_document_checks.py` (it has never been in git). Nothing committed.

**Next:** the pre-push guard's SUBJECT/CARRIED addition, reported before it is written.
