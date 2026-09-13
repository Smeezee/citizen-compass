# ORDER — the page now clears the stale marks itself. Rebuild and deploy.

From: C1 (Cowork), 2026-09-05
For: Code
Supersedes: task 1 of `ORDER_fix-the-marked-ships-and-deploy-2026-09-05`

You were right that nothing outside the browser can reach those marks, and right
not to bury a migration in a file the order did not name. **It is my file, so I
have done it in `testing/_src/_inspect.src.html`** rather than leave Sleven
pasting into a console. He asked where he was even supposed to look, which is
the answer to whether a console snippet was the right shape of fix.

Your snippet's matching logic is the logic I used - by exact filename for the
three superseded ones, by what he WROTE for the seventeen orientation marks,
because the filenames were never what those seventeen had in common. That call
was correct and I kept it.

## What went in

`retireStaleMarks()` runs once, before the ship list is built so the counts and
tick marks it draws are already corrected. Then `showRetired()` puts a panel on
screen naming every mark it retired and why, with an OK button.

- **Runs once ever.** Guarded by `state.__stale_marks_20260905`, a timestamp
  written on completion. It cannot run twice.
- **Deletes nothing.** Sets `resolved` and `resolved_why`, clears `bad`. `note`
  and the reason chips are untouched, so a resolved entry still says everything
  it said.
- **Not silent.** A migration that rewrites a person's own notes without telling
  him is worse than the stale count it fixes. He sees the list.
- Anything not matching either rule is left alone.

`node --check` passes on the page's script block.

`docs/clear_stale_marks_console_snippet.js` is now redundant. Leave it - it is a
correct record of how the marks were identified.

## TASKS

1. Build and deploy testing. This carries **two** source changes: the camera fit
   from `ORDER_camera-fit-fixed-build-and-deploy-2026-09-05` and this.
2. After deploying, re-run your corner projection on **ATLS, ATLS GEO and
   Reliant Kore** and report the three margins. If any is still negative, say
   so - do not raise `CC_FIT_MARGIN` to make it pass.
3. Confirm the page loads with 0 console errors and the ship list still reads
   256.

```
python testing/_src/build_deploy.py
```

```
powershell -ExecutionPolicy Bypass -File .\scripts\deploy_testing.ps1
```

## Standing constraints

- Testing only. Do not deploy the live site.
- Do not `git add -A`. Nothing commits or pushes without Sleven's go-ahead.
