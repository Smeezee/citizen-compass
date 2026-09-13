# Update — order received: the inspector page needs its source notice

**2026-09-04 · Code**

Received `docs/ORDER_the-inspector-missed-your-build-by-90-seconds-2026-09-04.md`
from C1. The earlier build ran ninety seconds before `_inspect.src.html` existed,
so Sleven opened the URL and got nothing. C1 has taken that one.

**Order names the file and states the change, so it is delegated** - and it is my
file anyway:

    testing/_src/build_deploy.py
      _SHIP_CONTENT_PAGES = {'index.html', 'loadout.html', 'holo.html'}
      -> add '_inspect.html'

**Why it matters and not just cosmetics:** the inspector displays 258 CIG ship
models. Without that line the page ships the trademark strip but NOT the source
and takedown notice, which is the exact thing that set exists to prevent.

Then build, sweep, deploy, verify, and give Sleven the URL.

**Watching for the same race rather than assuming it is over.**
`_inspect.src.html` was last written at 12:04:54 and it is now 12:10. The order I
am acting on exists because a build beat an edit by ninety seconds, so I will
re-check that the source has stopped moving immediately before the build rather
than trusting a file that was being edited three minutes ago.

Not touching `_inspect.src.html`, `deploy_pages.py`, `check_deploy_clean.py` or
`strip_comments.py` beyond the one line named above. C1 notes the last three have
no owner and proposes me; that is Sleven's to confirm, and I am not claiming
files by editing them.
