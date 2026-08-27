# Update: received four defects from a live session on Sleven's machine

Capture is working - 26 captures, hotkey burst confirmed "via polling". He is at
a shop terminal and **cannot send anything, because the window is dead.**

1. **The UI is dead and looks alive.** No bundled runtime -> fell back to a
   browser, where `w.Bind` has no meaning, so `state()` never returns and every
   button does nothing. NOT a network hang: `httpClient()` already has a 15s
   timeout, so a stuck "Checking for updates..." cannot be a slow fetch.
2. **Two windows, one empty and black.** Closing it kills the collector.
3. **No way to send without the UI.** The one that matters most - a broken
   window means a contributor cannot contribute, and cannot be talked through it
   on the phone either.
4. **The tray icon is the generic default.** Same family as today's shortcut
   icon bug, in a second place. Check every place this program supplies an icon.

Starting now. Not committed, not released.
