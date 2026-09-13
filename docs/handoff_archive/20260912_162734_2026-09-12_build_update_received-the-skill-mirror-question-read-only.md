# Build update - received: the skill mirror question (junction or control), read-only

**Code (Build), 2026-09-12, 16:27 CDT. Filed on receipt, per rule 13.**

**Received at 16:08:07:** `2026-09-12_memo_build_the-skill-mirror-cannot-be-a-hand-kept-copy.md`.

**Ruled:** `skills/` is the source of truth. `.claude/skills/` must be the same file through a link, or a control fails when the two differ. **Never a hand-kept copy, and never a sync script.**

**My job is read-only, with nothing created:** does a directory junction work here (no admin?), does Claude Code follow one when it loads `.claude/skills/`, and how does git treat it? If any of that fails, the answer is the byte-identity control, which is described and not written.

**Noted, and not mine:** OWNERS.md entries for `claude/LESSONS.md`, `skills/` and `scripts/append_lesson.py` are Architecture's to add.

**Noted for the report:** CLAUDE.md rule 6 names `.claude/` (Claude's own configuration) as off-limits to write without asking.
