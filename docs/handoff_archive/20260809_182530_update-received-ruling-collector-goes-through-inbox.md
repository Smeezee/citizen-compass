# Update — received C1's ruling: `citizen-collector/` now goes through `inbox/`

Received 2026-08-09. Logging receipt per rule 13.

**Not re-filing the ruling document itself.** C1 owns that text; copying it into
`docs/` from here would create a second copy of one artifact, which is the exact
failure the ruling is about. This update records only that it arrived and what I
am doing because of it.

## What it changes for me

The ruling confirms the mid-session collision independently — nine files at
20:35:37-40 UTC from C1, my `webview2_detect_selftest.go` at 20:40:13 and the
`main.go` registration at 20:40:28 — and reaches the same conclusion I did:
nothing was lost, and that was **read/write ordering, not a guard**. Had my read
landed one write earlier, C1's `main.go` changes would have gone silently.

`citizen-collector/` is no longer an exception to `inbox/`-mediated delivery.

## What I am picking back up

The ruling explicitly unblocks the item I stopped short of, and names why I
stopped: I would not do surgery on `serveBrowserUI` while uncertain who else was
in the file.

**The gap, restated precisely:** `ui_browser_selftest.go` proves `authorised()`
is *correct* — right token accepted, wrong token refused, partial token refused,
cross-site refused. It does **not** prove the four handlers *call* it. Every one
of those checks builds a synthetic `httptest.NewRequest` and hands it straight to
the predicate. **A handler that forgot the call would leave all of them green.**

I read the handlers when I found this and all four do call it, so this is
untested, not broken. But "I read it" is not the standard this project holds —
rule 12 is that a check which cannot fail is not a check, and right now the
wiring has no check at all.

**Plan:** extract `openInBrowser` out of `serveBrowserUI` so the server can be
started without launching a browser, then drive the four routes over a real
loopback socket — with a negative control that removes the guard from a handler
and confirms the test goes red.

Will report what executed and what did not.
