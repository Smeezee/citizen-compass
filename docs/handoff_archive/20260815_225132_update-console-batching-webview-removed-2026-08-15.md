# Update: all three done. `2e1589d` pushed, `33a9c6a` committed.

`selftest PASS - 529 checks, 0 failing.` Both binaries now **PE subsystem 2**.

## 1. The console

Both binaries were subsystem 3. Seven files said `-H windowsgui`; no build
command passed it. **The comment was the defect**, and my tray fix last night
made it look solved while addressing something else.

- `build.ps1` passes the flag and **reads the byte back** before reporting success.
- `make-release` **refuses** a non-2 binary. **Observed both ways:** a
  console-built binary was refused by name; the GUI build passed the same gate.
- Behavioural proof: the console build owns a visible **PseudoConsoleWindow**;
  the GUI build owns **no visible windows at all**.
- Every launch now logs whether a console is attached, so nobody has to trust a
  comment again.

**AttachConsole:** console.go's design is now finally in the situation it was
written for. It only attaches when started from a terminal, so a double-click
gets nothing - which is the intent. I have **not** driven it from a shell yet;
that is unverified and I am not claiming it.

## The tray right-click - my regression, found and fixed

Making the tray window **message-only** last night is why right-clicking did
nothing: such a window cannot take the foreground, and `TrackPopupMenu` needs an
owner that can. Now an ordinary window that is never shown, `WS_EX_TOOLWINDOW`.

**Not verified on screen by me** - your master build held the single-instance
lock all evening, so my launches yielded. It needs one right-click from you.

## 2. Sending

**The real limit is 100 MB**, Cloudflare free plan, from their own limits page -
which also names 413 as the response. It applies at the edge. **MAX_BYTES was
never the binding constraint.**

- **Notes first, alone.** 39,668 bytes, **confirmed in one second**, 308 rows
  marked sent. Verified in the bucket: 38.7 KB under your install id. **The
  first confirmed upload this project has ever had from your machine.**
- **Pictures in batches** of 48 MB (under both the 100 MB edge cap and our
  64 MB Worker ceiling). 700 frames plans to 35 batches, ~20 frames each.
- **Planned before anything is written** - no 1.7 GB package is ever created.
- **Zips removed** when finished with. A frame too big for any batch is *named*,
  not silently dropped.
- **Unchanged:** nothing is deleted the server has not confirmed. A failed batch
  leaves every frame where it was.

`-send-notes` added: hand over the 249 KB without the pictures.

**Your 3.94 GB of leftover packages** are in
`_to_delete/failed_export_packages_20260815/`. Moved, not deleted, per rule 1.
Every byte in them is still in `captures/`. Deleting that folder takes the
captures folder from 5.7 GB to 1.8 GB.

## 3. WebView2 is gone

Window, browser fallback, bridge timeout, parity check, escape hatch,
bundled-runtime machinery, and the dependency. Files moved to
`_to_delete/webview2_path_retired_20260815/`.

**One thing it nearly took with it.** `shortcut.go` relied on COM being
initialised as a side effect of `go-webview2`'s package init - its own comment
said so. Removing the import would have left every `CoCreateInstance` failing
with CO_E_NOTINITIALIZED, and the only symptom would have been a shortcut that
silently never appears on somebody's desktop, which people read as having
declined it. The program now initialises its own apartment.

Stale comments describing WebView2 as current behaviour were corrected rather
than left - that is the same failure mode as the windowsgui comments.

## Is uploading screenshots viable at all? My read: no, not as it stands.

One machine has 1.8 GB of frames after the leftovers came out; the bucket is
10 GB. **Two contributors with a normal backlog fill it.** Batching makes the
upload *possible* - it does not make it *affordable*.

The numbers: ~2.5 MB a frame, 653 frames from a few sessions. At 35 requests per
full backlog, R2's free tier (1M Class A ops/month) is fine on operations - the
constraint is purely storage, and storage is the thing that does not scale.

What I would actually do, in order of how much I believe in it:

1. **Read the frames on the machine that made them, and send numbers.** The
   pictures exist to have prices read off them. A price is bytes; a screenshot
   is megabytes. This is what the on-machine reader order was for, and it makes
   the storage question disappear rather than manage it.
2. **Send frames only when they carry something new** - a shop terminal, a
   price panel - rather than everything captured. Most frames are not evidence
   of anything.
3. **Pull and clear on a schedule.** `pull_and_clear.py` exists and works; the
   bucket becomes a queue rather than a store. This is the cheapest thing to do
   today and it does not need any new code.

**What I would not do** is raise the bucket size and carry on: it moves the wall
rather than removing it, and it puts a bill in front of you for storing pictures
whose value is a few hundred bytes each.

## Anything I think is wrong

Nothing in the order. One caution: `-send` now uploads the whole backlog in
batches, which on your machine is 1.8 GB and would put ~1.8 GB into a 10 GB
bucket in one go. **I deliberately did not run it.** Until the picture question
above is settled, `-send-notes` is the one to use.
