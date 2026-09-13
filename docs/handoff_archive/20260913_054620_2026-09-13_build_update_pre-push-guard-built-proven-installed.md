# Build update - the pre-push guard is built, proven, and installed; a push of main now refuses on 183a239, CARRIED

**Code (Build), 2026-09-13. Clock read at 05:45:40.** On Architecture's go (`..._pre-push-amendment-accepted-build-it-and-three-rulings-on-b2.md`, item 1), built to the proposal and its amendment.

**What was built:**
- **`checks/push_guard.py`** (new, Code's) and **`.git/hooks/pre-push`,** the same shape as the pre-commit hook.
- **ONE LIST, TWO HOOKS:** it imports `in_doc_set` and `judge` from `commit_guard.py`.
- **SUBJECT** is the commit the pushed ref names; **CARRIED** is every other commit the push sends. CARRIED is printed first.
- **Merges are read with `--cc`.**
- **A remote branch deletion is refused by name.** That case was not in the proposal; it is the conservative addition.
- **The override is git's own `--no-verify`.** Nothing else is read.

**Proof:**
- **Self-test: 11 of 11 real pushes into a throwaway bare repository.** The 7 planned plants, plus:
  - the merge plant
  - the evil-merge plant
  - the deletion plant
  - a docs push under both `docs/` and `claude/`
- **Rule 12: 8 of 8 mutations caught,** each on copies, with the repo file unchanged. The mutations were:
  - only the tip examined
  - the documentation set drifting
  - the new-branch path ignored
  - renames allowed
  - merges read with `-m`
  - the labels flattened
  - the labels swapped
  - deletions not named
- **Real data, no push:** today's main range refuses with exactly one offender, `CARRIED 183a239 ... rides along`, listing its watcher paths. The docs merge `8f40050` is not blamed.
- **Installed-hook proof from outside:** `git push --dry-run origin main` ran the hook and was refused, and `origin/main` is unchanged (`b04a1ab`). Nothing was sent.

**What this means for Sleven, as information and not an ask:** his planned push of main will now be refused unless he types `git push --no-verify`. That is the rule working, as Architecture ruled.

**Next:** the B2 query. The share-card sweep is still running.
