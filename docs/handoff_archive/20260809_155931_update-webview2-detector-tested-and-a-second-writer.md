# Update — the fallback decision now has tests, and there is a SECOND WRITER in citizen-collector/

Continuing from the selftest re-run. Two things below; the second is the urgent one.

---

## 1. Item #3, the browser fallback — the decision behind it was untested

The handoff calls the browser fallback "the one path with zero real-world
evidence". Looking at why, the problem turned out to sit one level above the
fallback itself.

`ui_browser_selftest.go` is thorough — 20 checks covering the token, the
cross-site refusal, action parity across both transports, shim placement. But
**every one of them is downstream of `webview2Available()`, and that function
had no test at all, in either direction.**

If it could only ever return true, the fallback would be unreachable code and
all 20 of those checks would still pass — testing a page that is never served.
That is the SILENT SUCCESS shape at the level of a *decision* rather than an
assertion. And it is invisible here specifically because both machines this has
run on have WebView2 installed, so the answer on those machines is always yes
and the negative branch is never taken.

**Added `webview2_detect_selftest.go` — 9 checks, all passing.** The detector
reads only the filesystem and the environment, so both answers can be forced on
demand without a second machine:

- says **NO** when nothing is on disk and nothing is in the environment (the one
  that matters — it proves the fallback is reachable at all)
- an **uninstall leftover** (version folder present, `msedgewebview2.exe`
  removed) is not counted as installed — the wrong-direction failure
  `webview2_detect.go` calls out by name in its own comments
- POSITIVE CONTROL: a real engine **is** found — without this, everything above
  would pass equally well if the function were `return false`, which would send
  every machine to the browser
- a per-user (`LOCALAPPDATA`) install is found
- a non-version folder such as `Installer` is not mistaken for a runtime
- the pinned-folder override is refused when empty and accepted when populated
- and finally: **the same `exeDir` yields BOTH answers** — so a function
  ignoring its inputs cannot satisfy the pair whichever constant it returned

Registered *before* `runBrowserUISelftest` in `main.go`, because the browser
group is meaningless if this one is broken.

### Still open on item #3

**No end-to-end test over a real socket.** The existing auth checks build
synthetic `httptest.NewRequest` values and hand them to `b.authorised()`
directly. That proves the predicate is correct, but **not that the server
actually consults it** — a handler that forgot the call would leave every one of
those checks green. I read the handlers: all four *do* call it, so this is
currently fine. It is untested, not broken.

Testing it properly needs a small seam: `serveBrowserUI` calls `openInBrowser`
inline, so exercising the server from a test would launch a real browser tab.
Splitting "start the server" from "open the browser" would make the real socket
path testable. **Not done — that is shipped-code surgery and see §2.**

## 2. RULE 14: another session is writing citizen-collector/ right now

**Nine files were rewritten at 15:35 today, mid-session, by something that is
not me:**

```
export.go      gamelog_mine.go   scrub.go        sent_rows_selftest.go
ui.go          ui_actions.go     ui_state.go     upload.go
upload_selftest.go
```

`ui.go` read `2026-08-08 18:40` when I listed the directory at the start of this
session and reads `15:35` now. This is the fourth instance of the pattern rule 14
exists for, and the first one caught *while it was happening* rather than later
in a diff.

**No collision occurred.** My three files (`gamelog_selftest.go`, `main.go`,
`webview2_detect_selftest.go`) are intact, my staleness gate is still present,
and both registrations coexist in `main.go` — my edit was a read-modify-write of
current content, so their work was preserved rather than overwritten. That is
luck and sequencing, not a guard.

**I have stopped writing to anything in that set.**

### What that session's new test does, which someone should know

`sent_rows_selftest.go` (new, 15:35) **fails on this machine, consistently:**

```
[FAIL] sent-rows: first export carries the one pending row   rows=309 keys=309
[FAIL] sent-rows: confirming marks exactly the exported row  marked=309 err=<nil>
```

It seeds a temp store with exactly **1** transaction, then calls `BuildExport`.
`BuildExport` calls `MineAll`, and `MineAll` calls `MineTargets()`, which scans
real drive letters for a real Star Citizen install **and its `logbackups`**. So
the export carries the 1 seeded row plus 308 mined from this machine's actual
game logs.

The test's own comment says it deliberately bypasses `MineTargets` when seeding
the store "which scans real drive letters… and has nothing to find in a unit
test" — but `BuildExport` reaches it anyway, one call down.

I checked whether this was working-directory dependent by running the same
binary from two locations. **It is not** — identical `rows=309` both times. The
test is simply not hermetic: **it can only pass on a machine with no Star
Citizen installed**, which is precisely the opposite of the machines this
collector is built for.

**Reported, not fixed.** That file is another session's live work and touching
it is the exact collision rule 14 forbids.

## 3. The staleness fix proved itself in the wild

The gate added earlier today fired on its own during these runs — not in a
planted test:

```
[FAIL] staleness warns once per stall, not every poll
       NOT PERFORMED - no warning ever fired, so there is no count to hold steady
```

Before today those two lines read `[ok]` under exactly these conditions. The
flake is still ~1 in 5 and still unfixed, but it can no longer pass silently.

## Also noted, pre-existing, not acted on

`gofmt -l` flags 8 collector files: `export.go`, `gamelog_mine.go`, `merge.go`,
`package.go`, `startup_diag.go`, `trigger_value_selftest.go`, `ui.go`,
`winapi.go`. `merge.go` and `winapi.go` were not touched today, so this predates
both sessions — genuinely unformatted Go, not a line-ending artefact (checked).
Not reformatting: it is a bulk change across files another session is actively
editing.

## State

`go vet` clean, `go build` clean. My files are gofmt-clean. Nothing committed —
no go-ahead, per rule 2.

**Recommend somebody establishes which session owns `citizen-collector/` before
either of us writes there again.**
