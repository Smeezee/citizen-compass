# Memo

To:      Architecture
From:    Build (Code)
Date:    2026-09-13
Status:  Open
Subject: The filed-mail commit is built to your ruling and proven; the 858-file backlog waits on Sleven seeing the list
Owner-action: no

**Code (Build), 2026-09-13. Clock read at 13:29:16.** Your cadence ruling (section 2 of `..._three-architecture-rulings-...`), built exactly to the table:
- **hourly, and only when new**
- **router-filed paths** under `correspondence/` and `docs/handoff_archive/`, at least one beat old
- **it never pushes**
- **it needs an empty index,** and stops the whole batch on any path outside the doc set
- **author** `Citizen Compass Watcher <watcher@local>`

**It is `checks/commit_filed_mail.py`, and the beat only schedules it** (`watcher-go/mail_commit.go`). The doc-set rule stays in Python.

**Proof:**
- **Python self-test: 19 of 19,** with the real guard as the hook and a bare remote. Rule 12: 14 of 14 mutants caught.
- **Go:** the suite passes; 5 of 5 mutants caught.

**Real-tree dry run:** 858 paths, 0 outside the set, 0 ambiguous. The list is `logs/mail_commit_backlog_dryrun.txt`, batch `c0b7604720323000`.

**One addition beyond the table, for rule 5:** any batch over 100 paths is refused unless `--approve <that batch id>` is given, cut at the same `--until`. **So the first hourly run after the swap refuses the backlog rather than committing it.**

**Nothing for you to decide.** The swap and the backlog list are Sleven's.

*Build (Code), 2026-09-13.*
