# PROPOSAL - the watcher commits filed mail and archived updates on a cadence (nothing is built)

    from      Build (Code), 2026-09-13 (clock read at 09:34:56)
    for       Architecture
    order     2026-09-13_memo_build_boot-line-go-the-844-are-not-a-chore-and-a-bounced-answer-is-invisible, item 2
    status    PROPOSAL. Nothing is built.

**The finding behind the order:** two weeks of this project's own mail and archive live in a working tree and in no history. At 09:27 the uncommitted receipt read **856 doc-set files, the oldest from 2026-08-30 04:18.** That is the `skills/` finding at 500 times the size. Handing Sleven an 856-file list once does nothing about the next 856.

**The mechanism exists and nobody wired it:** filed mail is `.md` under `correspondence/`, inside the rule 2 documentation exception, and `7a5a580` and `790fd9b` passed the guard this morning.

---

## 1. MEASURED FIRST

    router filings today (its own log, to 09:34)   94
        into correspondence/                         67
        into docs/handoff_archive/                   24
    by hour     02:00 2 | 03:00 12 | 04:00 18 | 05:00 21 | 06:00 3 | 07:00 0 | 08:00 34 | 09:00 4
    programs in this repository that run `git add` or `git commit`   NONE  (grep of scripts/, checks/,
                                                                          watcher-go/, testing/_src/ and the root)

## 2. YOUR FIVE QUESTIONS

### 1. CADENCE: HOURLY, AND ONLY WHEN SOMETHING NEW WAS FILED

- **Every beat (10 min)** would make about six commits an hour in a burst like 08:00, most of them one letter each. That is noise in the history this exists to protect.
- **Daily** would leave up to a day's mail on one disk. That is the `skills/` risk, only smaller.
- **Hourly** matches the measured bursts (up to 34 filings in an hour). **No new filings means no commit, so an empty hour writes nothing.**
- **It rides the beat** (`ticker.go`): the first beat after the hour turns runs it.

### 2. ONLY WHAT THE ROUTER HAS FINISHED WITH

- **The batch is read from the router's own log, not from `git status`.** It is every path a `✓ ... -> <dest>` line filed:
  - under `correspondence/` or `docs/handoff_archive/`
  - **filed at least one full beat (10 minutes) ago**
  - **still at that exact path now**

  An answer that moved on since it was filed is committed where it now sits, by the same filename resolution B1 uses. It is never re-guessed.
- **Documents the desks write by hand** (`claude/`, `design/`, the rest of `docs/`) **are NOT the watcher's.** Their writers commit them, as Build did this morning. The watcher commits only what it put there itself.

### 3. IT COMMITS AND NEVER PUSHES

- **No `git push`, no remote, and no fetch in the code.** Publication stays Sleven's, and the pre-push guard would refuse anything that is not docs anyway.

### 4. IT REFUSES RATHER THAN ADAPTS

- **Before staging: if the index is not empty, it does nothing this hour.** Someone is mid-commit. It logs one line naming the staged paths, and it never sweeps another writer's staging into its own commit.
- **Each path is checked with `commit_guard.in_doc_set`** before anything is staged. **One path outside the set stops the WHOLE batch.** The watcher never commits the subset.
- **It stages by exact path, never `git add -A`.** The real pre-commit guard then judges the staged set. **If the guard refuses, the watcher unstages exactly what it staged** (`git reset -- <those paths>`), logs the refusal, and stops.
- **Every outcome is a receipt line:** committed N at hash H, nothing new, index busy, refused by the guard, or git did not answer. BOOT.md can show it the way it shows the poller.

### 5. RULE 14: WHO ELSE WRITES THE GIT INDEX, AND HOW THEY CANNOT MEET

- **Today:** Sleven's hand, and the desk sessions running `git add` and `git commit` by hand. **No program does** (see section 1). The watcher would be the first programmatic writer.
- **How they cannot meet:**
  - **Git's own `index.lock`** makes two writers fail rather than interleave. Whichever is second gets an error, never a corrupt index.
  - **The non-empty-index refusal** means the watcher never starts while a desk is staging.
  - **The watcher holds the index for one short critical section** (stage, commit) and releases it. A desk that hits the lock retries; the watcher that hits it tries again next hour.
- **What it cannot stop:** a desk that stages after the watcher's emptiness check and before its commit. The lock makes that fail loudly for one side rather than mixing the two, **and the guard's staged-set judgement still applies to whatever is committed.**

## 3. WHERE IT RUNS: ONE DOC-SET RULE, IN ONE LANGUAGE

**`checks/commit_filed_mail.py`** (new, Code's) imports `in_doc_set`, reads the router's log, and runs git. **The beat only schedules it,** exactly like the uncommitted receipt. A Go copy of the doc-set rule would be the second list your BOOT-line go ruled out.

## 4. THE FIRST RUN IS THE BACKLOG, AND RULE 5 APPLIES TO IT

- **The first real run would commit about 850 files at once.** Rule 5 puts that list in front of Sleven first.
- So **`--dry-run` prints exactly the batch** and writes nothing, and the first real run happens only after he has seen it. **Every later hourly batch is a handful** (measured: up to 34 in the busiest hour).

## 5. TWO DECISIONS FOR YOU

1. **The commit author.** Git's configured user here is Sleven, so a program's commits would read as his hand. **I recommend an explicit author on these commits,** for example `--author="inbox watcher <watcher@citizen-compass.local>"`, so history says which hand made them. **Your call; it touches what his name is on.**
2. **Hourly, or another cadence.** Hourly is my pick, for the reasons in 2.1.

## 6. PROOF PLAN, IN THROWAWAY REPOSITORIES

1. A filed and settled letter is committed. One filed in the last 10 minutes is not, yet.
2. Nothing new means no commit.
3. A non-empty index means nothing staged and nothing committed, with a log line naming the other writer's paths.
4. One path outside the doc set means the whole batch is refused, and the index is untouched.
5. The guard refuses, so exactly the watcher's own paths are unstaged, with no partial commit.
6. It never pushes: a bare "remote" whose refs do not move.
7. A filed letter that moved on is committed at its current path.
8. `--dry-run` writes nothing: the tree and index are hashed before and after.

**Rule 12 mutations on each assertion. Report before building, as ordered.**

*Build (Code), 2026-09-13.*
