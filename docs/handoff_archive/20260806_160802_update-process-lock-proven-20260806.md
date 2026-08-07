# Update: process lock now proven by refusal, both builds (2026-08-06)

All four ordered checks are in `--selftest` and pass on the crew AND master
builds. Nothing has been packaged or distributed.

New file `process_lock_selftest.go`; `main.go` and `winapi.go` amended.

## The condition is CREATED, not hoped for

The test builds a real top-level Win32 window, really titled **"Star Citizen"**,
really `WS_VISIBLE`, 400x300 so it clears the 200px filter — owned by the test
binary, which is not `StarCitizen.exe`. It is placed at -5000,-5000 so a
selftest does not flash a box over whatever you are doing; `IsWindowVisible`
tests the WS_VISIBLE *style*, not desktop bounds, so it still takes exactly the
path a real bystander window takes.

A test that waited for such a window to happen to exist would silently do
nothing on a quiet desktop and report a pass.

## The four checks

1. **POSITIVE CONTROL — refuses.** `findGameWindow(allowAny=false)` refuses the
   decoy, and the error **names the refused process** (`collector.exe` /
   `collector-master.exe`).
2. **NEGATIVE CONTROL — accepts.** Faked at the `isGameProcess` boundary only:
   `scProcessNames` is briefly pointed at the test binary's own exe name. **The
   gate itself is untouched and still runs** — same call, same path, same
   guard. A further check confirms the whitelist was restored afterwards, so no
   later check runs against a permanently widened list.
3. **SECOND GUARD, independently.** The inline `if` at the old `main.go:187` is
   now a named `finalWindowGuard(win, allowAny)`, called from exactly one place
   so no logic is duplicated. It is fed a crafted window (`claude.exe`) that
   "passed selection" and must refuse, naming it; must admit a genuine game
   window; and must stand aside under `--allow-any-window`.
4. **CREW VARIANT — cannot set it.** Asserts `flag.Lookup("allow-any-window")
   is nil` **and** the bench closure returns false. Master asserts the
   opposite, so the check cannot pass by accident in both.

Measured directly, not inferred:

- crew `--allow-any-window` -> `flag provided but not defined`, **exit 2**
- master `--allow-any-window` -> accepted, listed in `--help`
- master `--allow-any-window --auto` -> **exit 2**, combination refused

## My own test had the exact defect you warned about, inverted

Mutation testing found it. **Deleting layer 1 outright turned nothing red** —
layer 2 caught the decoy, `findGameWindow` still returned an error, and every
check still passed. "It refused" is true of both layers, so asking only "did it
refuse" proves *neither* individually. That is the same hole as testing layer 1
alone, pointing the other way.

Fixed by pinning the layer from the error wording — layer 1 says
`Refused N other process(es)`, layer 2 says `internal guard:` — and adding
**`lock: refusal came from LAYER 1, the process gate`**. That check fails the
moment layer 1 is removed.

## Every check seen to fail. Seven mutations, all caught:

| mutation | check that went red |
|---|---|
| layer 1 gate never refuses | `refusal came from LAYER 1` |
| refusal error stops naming the process | `refusal NAMES the refused process` |
| `finalWindowGuard` always allows | `second guard refuses a non-game window` |
| `isGameProcess` never matches | `NEGATIVE CONTROL accepts the real game process` |
| crew bench closure leaks `allowAny=true` | `CREW build cannot set allow-any-window` |
| crew build registers the flag | `CREW build cannot set allow-any-window` |
| master build loses the flag | `MASTER build does offer allow-any-window` |

Source restored from a pristine copy; both baselines re-confirmed exit 0.

One incidental proof: calling `registerBenchFlags()` a second time is harmless
in crew (it registers nothing) but panics the master build with
`flag redefined`. That panic is itself evidence the two variants genuinely
differ, so the second call is made only in the crew branch, with a comment
saying why.

## Full verbatim output — CREW

```
citizen-collector 0.1.0 (crew) selftest
  [ok  ] captures dir writable              ...
  [ok  ] blank detector rejects blank       every one of 4096 sampled pixels is rgb(0,0,0)
  [ok  ] blank detector accepts content     accepted as real content
  [ok  ] png encode                         ...
  [ok  ] win32 reachable                    primary display 1920x1080
  -- process lock --
  [ok  ] lock: decoy is a real visible 'Star Citizen' window title="Star Citizen" visible=true size=400x300 owner=collector.exe
  [ok  ] lock: POSITIVE CONTROL refuses a non-game 'Star Citizen' refused, error names collector.exe: true
  [ok  ] lock: refusal NAMES the refused process refused, error names collector.exe: true
  [ok  ] lock: refusal came from LAYER 1, the process gate the process gate refused it before any title was consulted
  [ok  ] lock: NEGATIVE CONTROL accepts the real game process accepted the window once its process counted as the game
  [ok  ] lock: whitelist restored after the fake scProcessNames=[starcitizen.exe]
  [ok  ] lock: second guard refuses a non-game window internal guard: selected a window from "claude.exe", which is not starcitizen.exe - refusing
  [ok  ] lock: second guard admits the game a genuine game window is not blocked by the guard
  [ok  ] lock: second guard defers to --allow-any-window master-only bypass still works, by design
  [ok  ] lock: CREW build cannot set allow-any-window flag registered=false benchAllow=false hint="" (all must be empty/false)
  -- auto mode --   (16 checks, see the Job 4 update)
  -- environment --
  [note] Game.log  ...LIVE\Game.log (776 lines, patch 4.9.188.23497)
selftest PASS   exit 0
```

## MASTER — identical except the last lock line

```
  [ok  ] lock: MASTER build does offer allow-any-window flag registered=true
selftest PASS   exit 0
```

**Which checks are new:** everything under `-- process lock --` (10 checks) and
everything under `-- auto mode --` (16 checks). The five above `-- process
lock --` are the pre-existing ones.

## Standing gap

The lock is proven against a decoy. It has **not** been exercised against a
real running Star Citizen — the game is not running, so the "accepts the actual
game" path is proven only via the `isGameProcess` boundary fake. Stating it
rather than implying coverage I do not have.
