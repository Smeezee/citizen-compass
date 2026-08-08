# Update: CAUGHT - the shipped binaries were stale. Rebuilt.

**2026-08-06.** Found while answering "where is the collector at".

## What was wrong

Job 1 fixed the hotkey in **source**, committed it, and pushed it. **The two
binaries on disk were never rebuilt.**

```
collector-master.exe   built 18:07   NO hotkey fix
collector.exe          built 18:07   NO hotkey fix
```

Verified by behaviour, not by timestamp: neither exe's `--selftest` contained
the `-- hotkey (auto mode) --` group, which only exists after the fix.

**I had reported the live session as unblocked. It was not.** Running
`collector-master.exe --auto` at that moment would have had exactly the same
dead Ctrl+Alt+F9 as before, because `*.exe` is gitignored and a push does not
rebuild anything. Fixing source and declaring the operator unblocked are two
different claims, and I collapsed them.

## Fixed

```
go build -o collector.exe .                      # crew
go build -tags master -o collector-master.exe .  # master (Sleven)
```

Both now report:

```
[ok  ] --auto REGISTERS the hotkey (end to end)
selftest PASS
```

## Worth noting for later

Nothing in the repo rebuilds these on commit, so the same gap can reopen the
next time collector source changes. The `--ui` launcher job is a natural place
to close it - a launcher that shells out to a stale exe would show RUNNING while
running the wrong code, which is the same class of lie the launcher's own
"status from reality" rule exists to prevent.

Not implemented yet; flagged so it is a decision rather than an oversight.
