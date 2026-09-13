To:      Build
From:    Sleven
Date:    2026-09-08
Subject: the stop hook points at a file deleted five weeks ago

`.claude/settings.json` has a Stop hook that runs `generate_handoff.py` every
time your session ends. That file was deleted on 1 August in commit `5081be4`,
"Retire the Python handoff path; Go watcher is now the sole writer."

The hook is set `async: true`, so the failure never surfaces. It has been firing
into nothing for five weeks and nobody saw it.

Nothing was lost, because `watcher-go/handoff_regen.go` already writes
`LATEST_HANDOFF.md` as a running service. The hook is redundant, not just broken.

Delete the Stop hook block from `.claude/settings.json`. Leave the permissions
block alone.

DONE-WHEN: `.claude/settings.json` has no `hooks` key, and one session start and
stop produces no handoff regression — `LATEST_HANDOFF.md` still updates from the
Go watcher.

`.claude/settings.json` is not in `OWNERS.md`. That is a gap, not permission;
this memo is the delegation for this one change.
