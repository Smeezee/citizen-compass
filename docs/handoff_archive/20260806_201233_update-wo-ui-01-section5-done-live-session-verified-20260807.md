# Update: WO-UI-01 §5 done. Live session observed working. Two defects found.

**2026-08-07.** Committed `c6a74a2`. Two commits unpushed (`8594ed3`, `c6a74a2`).

## Sleven's live session is running and all three fixes are visible in it

`collector-master.exe --auto`, PID 5000, started 22:03:41. **Not touched.**

```
[22:03:41] hotkey registered: Ctrl+Alt+F9
[22:03:42] startup: watching ...\StarCitizen\LIVE\Game.log (found by scanning known install locations)
[22:06:42] alive: watching ...\Game.log, 573038 bytes read since last line, 0 captures total
```

Job 1, Job 2 and Job 3 all confirmed working **in production**, not just under
test. The log is being read (573 KB since the last line), so the game is writing
and the collector is following it.

## §5 implemented - the selftest can report from a GUI binary

All three parts, per the ruling:

1. `AttachConsole(ATTACH_PARENT_PROCESS)` when a console exists; std handles
   reopened onto `CONOUT$` afterwards, because a `-H=windowsgui` process starts
   with none and attaching alone leaves `fmt.Print` writing into a closed handle.
2. **`collector-selftest-results.txt` next to the exe, always**, leading with
   `RESULT=` / `EXIT=` so nothing downstream parses prose. Written on every path
   - a file appearing only on success would let a crashed run look identical to
   one never attempted, and yesterday's file would read as today's pass.
3. Meaningful exit code: 0 PASS, 1 FAIL, **2 VOID**.

Output is captured by teeing `os.Stdout`, so helpers printing directly land in
the file too. Capturing only `check()` lines would give a results file that
quietly disagreed with the screen.

## DEFECT FOUND, caused by the live session - now fixed

Running `--selftest` while the real session was collecting returned **exit 1**.
The session legitimately holds Ctrl+Alt+F9, so the registration checks correctly
said NOT PERFORMED - **but counted it as a failure**. The packager's "assert exit
0" would have failed for a reason with nothing to do with the package.

Two fixes:

- the selftest now uses **`ctrl+alt+shift+f12`**, not the product default. A test
  must not collide with the thing it is testing.
- when the key genuinely cannot be obtained the run is **VOID (exit 2)**, not
  FAIL. A check that could not run is a different fact from one that ran and
  failed, which is what exit 2 exists to say.

**Verified with the live session still running: exit 0, all sixteen hotkey
checks performed.**

Also removed a hardcoded `"Ctrl+Alt+F9"` expectation that silently became wrong
the moment the test key changed - the expected name is now derived from the spec.

## Toolkit settled

`winapi.go`'s own header records **`CGO_ENABLED=0` and no C compiler on this
machine**. That rules out every cgo-based UI toolkit outright.
`github.com/jchv/go-webview2` is **pure Go** and fetches cleanly, so it is the
one that can actually build here.

My hard-rule-7 concern was **unfounded and is withdrawn**: `pkg/pgconn` and
`watcher-go` already depend on `pgx`, `fsnotify` and `golang.org/x/*`. Rule 7
targets the ~29,000 cloned data files, not ordinary Go modules.

WebView2 runtime is present here (151.0.4129.59), but §3 wants it bundled so it
works on a stranger's machine. Bundling the fixed-version runtime means
downloading a Microsoft redistributable - flagging that as a download step
needing Sleven's go-ahead rather than doing it unasked.

## Next, in order

1. Continuous install detection (§6) and follow-the-game lifecycle (§7)
2. The window: three states, one button, reassurance line (§2), status derived
   from reality (§9)
3. `Send my data back`, then `Make a copy to send someone` + negative control (§8)
4. Desktop shortcut, launched and confirmed (§11)
