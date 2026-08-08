# Update: Job B - five commits prepared, NOT pushed, awaiting go-ahead

**2026-08-06.** Staged by name throughout. `git add -A` was never used.
**Nothing has been pushed.** Hard rule 2 - waiting on explicit confirmation.

## Correction to the job's premise

The three groups named in the order - **backup fixes, collector auto mode,
process-lock proof** - were **already committed and already pushed** before this
session started:

- `37324ce` Fix two silent successes in the backup, and verify per file
- `8de0a57` Land the collector, and let it capture on its own
- `83c326b` Prove the process lock refuses, instead of reading that it should
- `0570426` Refuse to ship anything in _deploy that is not a known asset

`git rev-list --left-right --count origin/main...main` returned `0 0`, and the
archive holds `20260806_165853_update-jobB-pushed-20260806.md`. So that work was
not outstanding. What was actually sitting uncommitted is a later, different
set, and that is what has been grouped below.

## The five commits

| commit | what | files |
|--------|------|-------|
| `099d35b` | Add citizen-collector to the Go workspace | 1 |
| `5fe63ba` | Build the starmap route tables, keep bulk shards out of git | 8 |
| `e204fb9` | Stop uex_corp.py blaming a missing token for a missing library | 8 |
| `0964c09` | Record the rulings, findings and work orders from the dig | 28 |
| `253b647` | File the 2026-08-05/06 session record | 32 |

`5fe63ba` tracks the five small route tables (~1.4 MB) and leaves the 68 MB of
`pairs/` shards out, verified by checking what `git add -n` would actually take
rather than trusting the ignore rules to mean what they say.

`0964c09` includes the licensing, Fan Kit and trademark documents **committed
exactly as authored, unaltered** (hard rule 8 - recording that text is not
editing it).

## Deliberately NOT committed - six items left in the working tree

- `.wrangler/` - **see the warning below**
- `.uex_snap_name` - 17-byte transient marker
- `rescale_run_output.log` - 183 KB run log
- `_c1_verify_wo.py` - throwaway with hardcoded `/sessions/rcw-.../mnt/` paths
  from a different machine; would not run here
- `testing/_src/_modelfolders.txt`, `testing/_src/_scunpacked_names.json` -
  generated lists, referenced by no build script

None were deleted. All are still on disk exactly where they were (hard rule 1).

## WARNING - the leaked wrangler file is back, at the repo root

`0570426` exists because a `.wrangler/cache/wrangler-account.json` inside
`testing/_deploy/` was published to the internet. **That same file now exists at
the repo root:**

```
.wrangler/cache/wrangler-account.json
  account id   ad974500ce73c9694e94213c4d762f3e
  account name Citizencompass.contact@gmail.com's Account
```

It is untracked, it did not go into any commit above - **and it is not in
`.gitignore`.** The deploy-side whitelist added in `0570426` guards
`testing/_deploy/`; it does not guard the repo root. A single `git add -A` puts
the account id and the contact email address into public git history
permanently.

**Recommend adding `.wrangler/` to `.gitignore`.** Not done unprompted, because
it changes what is about to be reviewed for push. One line, and it closes the
root-level hole the same way the deploy-level one was closed.

## Also flagged, not fixed

The commodities provenance landed with its integrity artifacts inside a
directory named `_integrity_scan.json` - a **directory** carrying a `.json`
extension. Committed as found rather than renamed, because
`docs/URGENT_path-join-bug-is-live-fired-tonight.md` reports that
path-construction bug as still open and unattributed. Renaming it would have
destroyed evidence of a live defect.

**Waiting on:** go-ahead to push these five commits to `origin/main`.
