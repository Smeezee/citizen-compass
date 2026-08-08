# Update: four jobs received - hotkey dead in --auto is blocking a live session

**Received 2026-08-06.** Working Job 1 first: it blocks a capture session
Sleven is about to run.

1. **JOB 1 (time-sensitive)** - `--auto` never registers the hotkey.
   `main()` enters the auto branch, calls `runAuto(...)` and returns, and
   `parseHotkey`/`RegisterHotKey` sit *after* that return, so Ctrl+Alt+F9 is
   dead in auto mode with no log line and no sign. Register inside the auto
   branch before the poll loop, tag frames `Trigger{Kind:"hotkey"}`, and report
   registration failure on stdout **and** in `collector-auto.log`.
   Add a selftest check that the hotkey is REGISTERED in auto mode, with a
   negative control on an invalid hotkey string - if both pass identically the
   check is not looking at registration.
2. **JOB 2** - `--gamelog <path>` override; print chosen path and *how* it was
   chosen every `--auto` start; warn if the file has not grown in N minutes
   while a game window exists.
3. **JOB 3** - heartbeat line in `collector-auto.log` during quiet periods.
4. **JOB 4** - the push.

## Job 4 status correction, in advance

**That work is already done and already pushed.** In the previous session
Sleven gave the go-ahead, `.wrangler/` was added to `.gitignore` as the sixth
commit *by pattern rather than by path*, and all six went up as
`0570426..8017efc`. `git status` no longer shows `.wrangler/` at all.

The rules landed as `.wrangler/` and `wrangler-account.json`, neither carrying a
leading or embedded slash, so git matches them at any depth - verified at the
repo root, at `testing/_deploy/.wrangler/cache/`, and at two arbitrary nested
paths, with an unrelated file at the same depth confirmed *not* ignored.

There **is** one genuinely unpushed commit: `62d3b1f`, the deploy-time guard
from last turn's follow-up. It will be listed explicitly before anything is
pushed.
