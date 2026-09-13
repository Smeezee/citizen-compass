# Memo

To:      Owner (Sleven)
From:    Architecture (C1)
Date:    2026-09-12
Status:  Open
Subject: The watcher source commit — gate run, no approved path exists, so it is three lines from you.

## ALREADY CHECKED

**Asked of Build, read-only, answered 2026-09-12. Nothing was built, staged or committed to find
out — `git add --dry-run` left the index at 0 before and after.**

- **A one-time approval the guard would accept?** **No.** `checks/commit_guard.py` reads one input,
  the staged index. No approval file, no environment variable, no flag, no allow-list, no signed
  message. **There is nothing in it a chat approval could reach.** Unconditional for Code, by
  design.
- **The documentation exception?** **A real mechanism, and it cannot cover this.** The guard
  hard-codes it to tracked `.md` under `docs/`, `claude/`, `design/` and `correspondence/`, plus
  `NEXT.md`, `LIVE.md` and `RECOVERY.md`. Go source is out. **Widening it would be loosening the
  guard, which is not on the table.**
- **An existing order of yours that covers it?** **No.** Ruling 21 and the guard cover
  documentation only.
- **A job Architecture can order instead?** **No.** The only route past the hook is `--no-verify`,
  and the hook's own header reserves that for a human.

**So the answer is the legitimate one: a human hand is required, and it is yours.**

## THE ASK

**Run the three lines below, in a terminal in the project folder or in the Claude Code session with
`!` in front of each. Nothing is pushed.**

## WHAT IT COMMITS

**25 files** — 5 modified, 16 new in `watcher-go`, 3 new in `pkg/apikeyguard/`, and one line in
`go.work`. **Compiled `.exe` files are git-ignored and stay out.**

**This is the exact tree the live watcher `74b08843` was built from.** `go vet` clean and the whole
suite passing at 06:56, unchanged since.

**`go.work` is included because without it the committed workspace file does not list the key-guard
package the watcher now imports.** Code did not prove a fresh clone would fail without it, because
proving it would have meant building. **Included as the safe choice, not as a proven necessity.**

## IF YOU WOULD RATHER NOT TONIGHT

**Nothing is at risk.** The source is on disk and the running binary has two rollback copies. **The
exposure is only that a disk failure or an overwrite loses the mail system**, which has been true
for weeks.

---

Stage the watcher's source — the two folders plus the workspace line listing the key-guard package.

```
git add -- watcher-go pkg/apikeyguard go.work
```

Show what is staged. The last line must say 25 files changed, and nothing outside those folders may appear.

```
git diff --cached --stat
```

Commit exactly that, skipping the documentation-only guard. This is the step only you may take.

```
git commit --no-verify -m "Watcher source enters history: mail router, BOOT.md, the beat, the key guard (committed by Sleven)"
```

ANSWERS:
