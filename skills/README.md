# skills/ — portable agent skills (not rules)

**This folder is the skill pack.** Copy or zip it for another project.

- **Rules live in `CLAUDE.md`** (project-specific, wipeable).
- **Skills live here** (reusable tools/workflows).
- **Project lessons** stay in `claude/LESSONS.md` (Citizen Compass only — do not ship lessons as if they were universal skills).

## For Claude Code on this machine

Claude Code also reads `.claude/skills/`. **That is the same skill, not a second copy to keep in step by hand.** Either `.claude/skills/` is a link to this folder, or a control fails when the two differ — **ruled 2026-09-12, because a mirror maintained by remembering is the defect this project has paid for three times in one week.**

**Never edit both.** Edit `skills/`. Source of truth for export: **`skills/`**.

## Layout

```
skills/
  README.md          ← this file
  aar-loop/
    SKILL.md
```

## Adding a skill

1. Create `skills/<name>/SKILL.md` with YAML frontmatter (`name`, `description`).
2. Make it reachable at `.claude/skills/<name>/SKILL.md` so Code loads it — by link, not by copying.
3. Do **not** bury skill bodies only inside `CLAUDE.md`.
