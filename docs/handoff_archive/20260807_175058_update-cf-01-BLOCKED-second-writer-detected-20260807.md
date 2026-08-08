# Update — CF-01 STOPPED before writing: a second session is already on it (2026-08-07)

**I have written nothing to `citizen-collector/`. Stopping and asking, per hard
rule 14 and the "if you are unsure, it does apply" clause.**

## What I found

I read the work order, then went to start job 1 (the crash). The fix was already
there.

`citizen-collector/winapi.go` at `HEAD` still carries the broken shape — a fresh
`syscall.NewCallback` per call. The **working tree** carries the corrected
one-callback-per-process version, uncommitted, with a comment block quoting the
same 14m2s/14m4s/14m4s/14m0s field evidence the work order does.

Eight source files were written in a single batch at **17:48:44–17:48:45**. I
filed my "work order received" update at 17:48:56. So that write landed roughly
ten seconds before I logged that I was starting, and I did not do it —
everything I touched this session was under `testing/` and `data-layer/`.

`tasklist` shows **nine `claude.exe` processes running.**

## State of the four jobs as it currently stands in the working tree

| job | state | evidence |
|---|---|---|
| 1. crash — `too many callback functions` | **done** | one package-level `enumCallback`, mutex-guarded `enumFn`, `runCallbackLeakSelftest` registered in `main.go` |
| 2. interval — 60s, unit change | **done** | `IntervalSeconds`, `defaultIntervalSeconds = 60`, `resolveIntervalSeconds` handles legacy `interval_minutes` and logs the conversion, `interval:%ds` tag, two selftests registered |
| 3. hotkey §2b — polling, edge-detect, dedup, tagging | **done** | `pollHotkey`, `GetAsyncKeyState` wired in `winapi.go`, `hotkey press received (%s, via %s)`, `runHotkeyEdgeSelftest` + `runHotkeyDedupSelftest` registered |
| 3. hotkey §2a — log renderer / window flags / elevation | **not built** | no `Game.log` renderer parse, no elevation check, no window style/rect/topmost logging anywhere |
| 4. tray indicator (option A) | **not built** | no `Shell_NotifyIcon` / `NOTIFYICONDATA` anywhere |

So the other session appears to be working the list in C1's stated order and is
somewhere around §2a / job 4 right now.

## Why I stopped instead of picking up §2a and the tray

Rule 14 names this exact defect, and its two prior instances both cost real
work — including a concurrent session rewriting `_layer.src.html` mid-verification
twice in one evening, once silently deleting a keybinds overlay and a compliance
strip.

§2a lands in `hotkey.go` / `auto.go` / `main.go` / `winapi.go`. Those are four of
the eight files the other session wrote ninety seconds ago. Two writers on those
files is not a merge conflict I would see — it is a last-write-wins clobber of
work that is not committed anywhere and therefore cannot be recovered.

The tray icon (job 4) is genuinely independent and would be safe in a new file,
**but** it still needs a wire-in point in `main.go`, which is contended.

## What I need from Sleven

One of:

1. **Stand down** — the other session finishes CF-01, and I stay off
   `citizen-collector/` entirely.
2. **Take over** — the other session is stopped first, and I verify what is
   there (build + full selftest run, including the required negative controls)
   then finish §2a and job 4.
3. **Split on a hard boundary** — I take job 4 only, in new files, and hand back
   the one-line `main.go` wire-in for whoever owns that file to apply.

Not proceeding on a guess. Nothing committed, nothing pushed, nothing written.
