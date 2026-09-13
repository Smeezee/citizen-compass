# Update — the phone stamp is fixed, deployed, and proven at phone width on the served page

**2026-09-11 14:52 CDT / 19:52 UTC.** Owner's 13:55 letter is closed.

## REPRODUCED FIRST, MY OWN WAY

He measured it through a same-origin iframe because Chrome refused to resize
the real window. **I reproduced it with a real mobile viewport instead, rather
than inherit a measurement I did not take** — and found the breakpoint he did
not have to:

    640px and above    #ver display:block   stamp visible
    560px and below    #ver display:none    stamp GONE

**The cause is the page's own rule:** `@media(max-width:560px){#top
span{display:none}}`. It hides the tagline and the version together on a phone,
deliberately — and my stamp was living inside `#ver`, so it went with them.

## THE FIX

**The stamp is now a SIBLING of `#ver`, not a child of it, and it carries its
own `display:inline` inline** — an inline style beats a stylesheet rule, so the
media query cannot take it away again. **The version text it used to sit inside
stays hidden on a phone, which is what that rule is there for.**

The whole declaration is injected by the build rather than added to the page's
stylesheet, **because that stylesheet is C1's and ships to the LIVE payload,
where this stamp must never appear at all.**

## PROVEN ON THE SERVED PAGE, NOT THE BUILD — WHICH IS WHAT HE ASKED FOR

    width   stamp box   stamp display   #ver display   in rendered text
     1510px  100x16      block           block          true
      900px  100x16      block           block          true
      640px  100x16      block           block          true
      560px  100x16      block           none           true
      500px  100x16      block           none           true
      390px  100x16      block           none           true
      360px  100x16      block           none           true
      320px  100x16      block           none           true

Eight widths, all PASS. **"Visible" means a real box AND the text present in the
rendered text of the page** — a computed style alone would call a zero-height
element visible.

**Two canaries, and they are the point:** at 390px the page's own
`#top span{display:none}` must still be IN FORCE, proven by `#ver` being hidden
there; and at 1510px it must not be. **If `#ver` were visible at 390px the media
query would not be applying, and the stamp surviving would prove nothing about
the rule it has to survive.** `checks/_diag_q55_stamp_widths.mjs`, which exits 2
rather than 1 if either canary fails.

## THE GUARD LEARNED THE THING THAT ACTUALLY MATTERS

`_verify_deploy_drift.py` now pins **`display:inline` by itself**, separately
from the rest of the style attribute, which is appearance.

**And that pin was proven by removing exactly that one declaration.** A stamp
stripped of `display:inline` is still in the bytes, still the right date, still
passes every byte-level check — and is invisible at 390px. **Drift reports it.**
Five plants in the rule 12 proof now, every one seen firing, and everything
restored byte for byte afterwards.

## STILL GREEN AFTER THE DEPLOY

    the four addresses (P1)   all four land, both canaries pass
    the front door (Q54)      gate, /classic, /next, 404 canary - all pass
    sweep                     129 green against this payload (3b1f09adb1222ff6)
                              0 failed, 0 not run
    drift                     16 passed, 0 failed

## WHAT THIS WAS, IN ONE LINE

**A check that passed while the thing it protects was defeated, one screen width
down.** Same shape as P24 itself and as the three found yesterday — and this one
was found by Sleven on a phone, not by any control. The control exists now.

*Code, 2026-09-11 14:52 CDT.*
