# Update: bucket listed (dry run), version bump committed

## 1. Bucket - HIS FRIEND'S SEND LANDED

Dry run only. **Nothing downloaded, nothing deleted, bucket untouched.**

    objects : 2
    total   : 19.7 MB

Both carry **today's date**, confirmed from the timestamp the receiver recorded
rather than guessed from the filename:

| uploaded (UTC) | size | version | install |
|---|---|---|---|
| 2026-08-15T16:40:50 | 19.7 MB | 0.3.1 | b99c1e3b-6f3f4848-3f90ac5a-c1be5e40 |
| 2026-08-15T16:42:01 | 14.6 KB | 0.3.1 | b99c1e3b-6f3f4848-3f90ac5a-c1be5e40 |

Same install both times, stamped **0.3.1** - so that machine took the update and
sent on the new build. The 14.6 KB second object is what a second SEND press
looks like after `clear_after_send` emptied the first.

Still not pulled down. After `--apply` the local copy is the only one in the
world, so `--keep` is the first run worth doing.

## 2. The three files - only one was dirty

- `citizen-collector/README.md` - **CLEAN**, nothing to commit
- `citizen-collector/wrangler.toml` - **CLEAN**, committed earlier in `6285f67`
- `citizen-collector/main.go` - dirty, **one line**: `Version 0.3.1 -> 0.3.2`

Checked the diff before committing rather than assuming. It is **not** mid-edit
hands-off work - none of that order has been started - it is the version bump for
the build already published as `collector-v0.3.2`, so committing it closes the
same source/feed drift as last time rather than freezing something half-done.

Committed as `5a2690b`, staged by explicit path. Nothing else touched: the
`app/` and `checks/` changes are the Aug 8 absence-schema work and were not
staged, read or modified.

## Still open

Item 4 (hands-off collector) is not started and is waiting on an answer about the
auto-start mechanism - a per-user startup entry rather than a Windows service -
which CLAUDE.md rule 6 requires asking for regardless.
