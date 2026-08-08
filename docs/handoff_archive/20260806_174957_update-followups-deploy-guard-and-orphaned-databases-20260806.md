# Update: two follow-ups - deploy guard closed, orphaned databases recorded

**2026-08-06.** Both of Sleven's lower-priority follow-ups. One commit made
(`62d3b1f`), **not pushed** - the push go-ahead covered the six commits that
went up as `0570426..8017efc`, and hard rule 2 does not carry forward.

---

## 1. The deploy guard - the whitelist was in the wrong place

**`build_deploy.py` already refuses to finish a build that would leave anything
unexpected in `_deploy`.** That part was fine. The problem is what it protects.

**It guards the BUILD. It never guarded the DEPLOY** - and a deploy does not
require a build. `scripts/deploy_testing.ps1` contained **zero** references to
`check_deploy_clean`, confirmed by count. It went straight from "does
`_deploy` exist" to uploading it.

That is exactly the sequence that leaked the file:

1. a wrangler run executed from inside `_deploy` failed and left `.wrangler/`
   behind - **no build involved**
2. the next deploy uploaded the directory as it stood

Running `deploy_testing.ps1` without rebuilding would have republished it, with
the build guard never executing once. The whitelist added in `0570426` was in
the wrong place to stop the incident it was written for.

### What changed

The same checker now runs inside `deploy_testing.ps1`, on the actual bytes about
to be uploaded, **before the credential section** - so a refusal never reaches a
code path that can talk to Cloudflare.

**It fails closed.** A missing checker, a missing exit code, or the checker's own
`exit 2` ("could not check") all refuse the deploy. Unverifiable is not clean.

### Proven by behaviour, against the real script (hard rule 12)

Run on a scratch project tree so nothing could reach the live site:

| case | result |
|------|--------|
| clean tree | guard passes, control continues past it |
| **`.wrangler/` planted in `_deploy`** | **DEPLOY REFUSED** - "hidden directory would be PUBLISHED", aborted at the guard |
| checker file absent | **DEPLOY ABORTED** - "refusing to deploy unverified content" |

The middle case is the actual 2026-08-06 leak reproduced, and it is now stopped.

`check_deploy_clean.py --selftest` also passes its own six checks, with the
negative controls firing.

### Checked and NOT a defect

I suspected the build's computed allow-list had drifted from
`DEFAULT_ALLOWED_FILES`, because `_deploy` legitimately contains
`kb_modes.gen.js`. **It has not drifted** - `PAGES` includes that entry at
`build_deploy.py:347` and the two sets match exactly. Recorded so nobody re-opens
it.

### Also cleaned up

`testing/_deploy/` is confirmed clean of any `.wrangler` or
`wrangler-account.json` - the copy planted while proving the gitignore pattern
was moved to `_to_delete/ignoretest_20260806/`, not deleted.

---

## 2. Four orphaned scratch databases - NOT dropped, recorded by name

These exist on the local Postgres instance right now. **They are left over from
earlier runs, not from tonight's work.** Recording them by name here so they are
not rediscovered in three weeks as a mystery:

```
cc_restore_test_20260730_233853
cc_restore_test_20260801_144501
cc_restore_test_20260801_203049
cc_restore_test_20260805_205238
```

**I did not drop them, and will not.** Hard rule 3 forbids `DROP DATABASE`
against a database this process did not create, and this process created none
of these. **Dropping them is Sleven's call.**

### What they are

Each holds a full restored copy of `citizen_compass` as it stood on that date -
so they contain stale ship data, and the oldest is a week old. They are
harmless, but they are not free: each is a complete copy of the database.

### Why they exist

`Test-DatabaseBackup.ps1` drops its scratch databases in step 4, so a run that
exits before step 4 leaves its database behind. All four dates line up with runs
that ended early - the 2026-08-05 one matches the aborted backup run that also
produced the zero-byte `.pullsummary.json` noted in the path-join bug report.

Tonight's runs cleaned up after themselves correctly: all six scratch databases
created this evening were dropped by the guarded `Remove-ScratchDb`, and a
post-run query confirmed none of tonight's remain.

### The obvious fix is not obviously safe

A startup sweep that drops everything matching `cc_restore_test_*` would clear
these automatically - but that is a process dropping databases it did not
create, which is the exact thing hard rule 3 prohibits. It would also be a
standing destructive operation running unattended.

**Not implemented. It needs an explicit decision rather than a quiet addition.**
A safer middle option, if wanted: have the script *report* pre-existing scratch
databases at startup and refuse to proceed until they are cleared by hand.

---

**Awaiting:** go-ahead to push `62d3b1f` (the deploy-time guard). Nothing else
outstanding.
