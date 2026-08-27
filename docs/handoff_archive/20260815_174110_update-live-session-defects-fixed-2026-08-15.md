# Update: all four live-session defects fixed. Committed, not released.

`8ffe727`, 9 files, explicit paths. `selftest PASS - 551 checks, 0 failing.`

## 1. The dead window

**Both existing escape hatches were satisfied.** `webview2Available` said yes and
`NewWithOptions` returned a window, because **both look at the runtime BEFORE the
page runs**. Neither can see a bridge that fails afterwards - which is the state
he hit.

The page now calls `uiReady()` as its first act. No hello within 12 seconds ->
the window is scrapped and the browser transport takes over. A **third** route to
the browser, alongside "no runtime" and "window would not create".

**One correction to the order.** It says to fix the README because the browser
fallback is not "same buttons, same everything". **It is** - `browserPage()`
recreates every binding the window injects, and I added a check that reads both
lists out of the source and fails if they diverge (11 vs 11 today, with a
negative control so two empty sets cannot pass as parity). His problem was not
the browser fallback; it is that he never reached it. So that sentence stays, and
what I added is the **third state** the README never described: a window that
opens and does nothing, and what the program now does about it.

## 2. The empty black window - it was the tray's

`CreateWindowEx` was passed **parent 0**. That is not a hidden window, it is an
ordinary top-level one with no size and no content. And the loop breaks on
`WM_CLOSE`, which is how `Stop()` asks it to finish - so closing that stray box
took the whole collector with it, exactly as reported.

Parented to **HWND_MESSAGE**: invisible, not in Alt-Tab, impossible to close.

## 3. Sending without the window - the one that mattered

- **`collector.exe -send`** - packages and sends, no window needed.
- **Tray menu -> "Send my data now"** - because a flag still assumes somebody who
  can be told what to type, and he could not open a terminal.

**All three doors call one `SendNow`.** A second copy would drift into one door
clearing somebody's pictures and another not. The flag shows the **same consent
screen** - a command-line path around consent would be a silent way to upload
screenshots without the screen that says screenshots are uploaded.

The tray menu **resolves the destination when clicked**, not at startup, so an
address that arrived from the feed since the window opened is the one used.

## 4. The icon - three places, not one

- tray: was `IDI_APPLICATION`, Windows' generic glyph
- **the main window: had never been given an icon at all** - title bar, taskbar
  and Alt-Tab all showed the default. Found by enumerating, not by being told.
- shortcut: fixed earlier today

Both now extract index 0 from our own exe - a stable question, rather than a
resource id the toolchain picks.

## The runtime decision, and what I could not do

**I could not build the with-runtime package.** The payload is **gitignored on
purpose** (`WEBVIEW2_RUNTIME_PROVENANCE.md` is tracked, the 162 MB is not) and is
absent from this machine. That is *why* the only asset ever published was the
small one - and `make-release` mentioned it in a grey Note among green ticks.
It is now an unmissable warning.

**My answer on shipping it by default: no, and the reason changed today.** The
runtime existed to stop a machine without WebView2 getting a dead end. After this
commit such a machine gets a **working browser tab**, proven, with a parity check
keeping it equivalent. Making every contributor download 162 MB to protect a
minority is a bad trade over a Discord link. The with-runtime zip should still be
**published as an option** - it currently is not published at all, which is the
real gap, and it needs the payload back on this machine.

**If you disagree, it is one folder away:** restore `webview2-runtime/` beside the
exe and the release builds both packages with no code change.

## Not verified, and I am not claiming it

The bridge timeout path is **proven by construction and by unit checks**, not by
watching a real half-broken WebView2 - I do not have a machine in that state. The
tray menu and message-only window are likewise not observed on a live desktop by
me. What is proven: the deadline exists and is sane, the page calls hello, both
transports expose identical functions, and the no-runtime resolver refuses every
bad shape while still accepting a good one.

Not released. `main` is **2 commits ahead**.
