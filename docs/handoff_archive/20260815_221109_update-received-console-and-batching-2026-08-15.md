# Update: received three defects from the live session, plus the tray right-click

1. **The black box is a CONSOLE window** - subsystem 3 in both binaries. No build
   script ever passed `-H windowsgui`; three files carry comments saying it does.
2. **Sending is all-or-nothing**: 1.7 GB packaged, refused 413 by **Cloudflare**,
   not by our Worker. Notes (249 KB) are hostage to screenshots.
3. **Finish the WebView2 removal.**

Plus, reported directly: **right-clicking the tray icon does nothing.** I have a
diagnosis for that already - see below - and it is my own regression from
earlier tonight.

## The tray menu, diagnosed before the order arrived

I parented the tray's window to **HWND_MESSAGE** earlier tonight to kill what I
believed was the empty black box. A message-only window cannot own a popup menu:
it cannot take the foreground, and `TrackPopupMenu` needs an owner that can. So
the menu I added never had a chance to appear.

**And the black box was never that window** - it is the console, as this order
establishes from the PE header. So my fix addressed a real defect (a closable
stray window) while the reported symptom had a different cause entirely, exactly
as the order says.

Starting now.
