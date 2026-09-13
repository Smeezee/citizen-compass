# Memo

To:      Build
From:    Owner
Subject: On a phone, the front door hides the testing stamp. P24's fix holds on desktop only.
Status:  Open

**Not urgent. Do not stop P1 for it.**

## WHAT WAS SEEN, ON THE SERVED SITE

Checked 2026-09-11 around 13:50 CDT, on the served `/next`, unlocked, rendered in Chrome:

    desktop, 1510 px wide    #ver visible: "v0.4.0 · 253 ships testing 2026-09-11"
    phone, 386 px wide       #ver computed display: none, size 0 x 0
                             its text is still in the page: "v0.4.0 · 253 ships
                             testing 2026-09-11"

The phone reading came from loading `/next` in a same-origin iframe 390 px wide, so the
page's own media rules applied at that width. Chrome refused to shrink the real window: it
reported the resize as done and the width stayed at 1510.

**So on a phone, the testing front door carries no visible testing marker.** That is the
exact condition P24 exists to prevent, at one screen width. Your guard reads the stamp out
of the bytes, where it is present, so the guard passes.

## WHAT I WANT

Treat it as P24's own unfinished edge, not a new feature. File it where it belongs, fix it
when P1 is done, and prove the fix at phone width on the served page, not from the build.
