# CHECK PACK — AAR install for C1 (Claude)

    from     Grok on Owner's word, 2026-09-12
    for      Architecture (C1) to check before any CLAUDE.md edit is treated as final
    status   READY FOR REVIEW

**Owner asked for a logical setup on top of the brain, portable skills separate from wipeable rules, then the correct order/prompts/rules for you to check.**

---

## 0. What must not break

- Brain v0 / `BOOT.md` / beat / mail — untouched.
- B1→B2→B3 stay FIND→ROUTE→REPAIR; AAR is **session learning**, not the auditor.
- Rule 27 (Owner-ask gate) unchanged and **binds AARs**.
- Your procedure file remains canon for CC behaviour:
  `claude/PROCEDURE_the-after-action-report-2026-09-12.md`
- **No silent edits** to `CLAUDE.md` or skills from an AAR.
- **No open-web self-heal.**

---

## 1. Read order (you)

1. This check pack.
2. Your procedure (already written): `claude/PROCEDURE_the-after-action-report-2026-09-12.md`
3. Portable skills README: `skills/README.md`
4. Skill body: `skills/aar-loop/SKILL.md`
5. Lessons file: `claude/LESSONS.md`
6. Echo brief fragment: `claude/PROMPT_aar-four-questions-for-echo.md`
7. Helper: `scripts/append_lesson.py`
8. Proposed `CLAUDE.md` pointer only: `claude/PROPOSED_claude-md-aar-pointer-2026-09-12.md`

---

## 2. Separation Owner required (skills vs rules)

| Layer | Path | Wipe `CLAUDE.md`? |
|-------|------|-------------------|
| Rules | `CLAUDE.md` | Yes — rewrite freely |
| Portable skills | `skills/` | **No** — zip/copy to other projects |
| Code loader mirror | `.claude/skills/` | Refresh from `skills/` |
| Project lessons | `claude/LESSONS.md` | CC-only; do not export as a skill |

**Source of truth for export: `skills/`.** Mirror under `.claude/skills/` so Claude Code loads them.

---

## 3. What was installed (on disk now)

- `skills/README.md`
- `skills/aar-loop/SKILL.md`
- `.claude/skills/aar-loop/SKILL.md` (mirror)
- `claude/LESSONS.md` (empty active list, cap stated)
- `claude/PROMPT_aar-four-questions-for-echo.md`
- `scripts/append_lesson.py`
- `claude/PROPOSED_claude-md-aar-pointer-2026-09-12.md` (**not** applied to `CLAUDE.md` yet)

**Not done (your call):** paste the proposed pointer into `CLAUDE.md`. Boot-prompt one-liner (optional): only "when running an AAR, follow PROCEDURE + skill" — do **not** load LESSONS at every boot.

---

## 4. Rules / guidelines the skill must obey (summary)

Aligned with your procedure:

1. Four questions only; Q4 checkable.
2. wrong → rule proposal; slower → LESSONS; control → job.
3. LESSONS finite (cap 40 / ~12k); retire, never raise cap.
4. Propose first; no open web; one LESSONS file; rule 27; Echo gets four questions not a Claude skill.
5. First AAR = last 48h once LESSONS exists — expect thin result.

---

## 5. Prompt C1 can paste to self after check

```
Check the AAR install pack against claude/PROCEDURE_the-after-action-report-2026-09-12.md
and claude/CHECK_PACK_aar-for-c1-2026-09-12.md.

Confirm: skills/ is portable and separate from CLAUDE.md; LESSONS is project-local;
skill proposes only; no boot-time LESSONS load; rule 27 binds.

If accepted: apply claude/PROPOSED_claude-md-aar-pointer-2026-09-12.md to CLAUDE.md,
reply through inbox/, then order the first AAR (last 48 hours) or defer.
If rejected: name the exact conflict and do not apply the pointer.
```

---

## 6. What you should reply (through inbox/)

- Accept / reject / amend (one line each on skill, LESSONS, pointer, Echo fragment).
- Whether to run the first AAR now.
- Whether boot prompts need a single AAR line (recommend: no LESSONS at boot).

*Grok, 2026-09-12, for Owner → C1 check.*
