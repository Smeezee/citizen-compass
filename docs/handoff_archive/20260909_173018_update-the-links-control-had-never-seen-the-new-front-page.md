# Update — the link control has been printing SWEEP CLEAN without ever fetching the new front page

**Filed 2026-09-09 17:23 CDT.**

Architecture asked one narrow question about Q49: can
`_verify_deployed_links.mjs` resolve `loadout.html?from=next`. **It can. Checking
found something worse.**

## `next.html` WAS NOT IN THE CONTROL'S PAGE LIST

    const SHIPPED_PAGES = ["/", "/find", "/keybinds", "/loadout", "/holo",
                           "/download", "/stick-test"];

**Typed, and stale since `next.html` shipped on 2026-08-30.** For ten days the
control printed **SWEEP CLEAN** while never fetching the page Sleven is being
pointed at, and never checking one of its links.

**Nothing said so.** The only floor assertion in that file covers `<script src>`
data files; there was no equivalent for pages. **A check that cannot fail, inside
a control whose entire purpose is to be believed.** `OWNERS.md` line 393 makes it
Code's, so I fixed it.

## THE FIX

The page list is now **derived from `deploy_pages.py`** — the one place that
decides what is published, and the same file `publishedOutputs()` already read
for the data-file floor.

    / /download /find /holo /keybinds /loadout /next /stick-test
    (not swept: _inspect.html)

`_inspect.html` is excluded **by name with its reason beside it** — private
throwaway, hard rule 25, fleet walk finished 2026-09-04. An exclusion on the
record rather than an oversight that looks like one.

**An unreadable `deploy_pages.py` FAILS LOUDLY** instead of quietly falling back
to the list that went stale. Proved by running the control from a copy with no
`deploy_pages.py` beside it — the FAIL fired.

    before   13 internal references across  4 pages, plus  9 external
    after    19 internal references across 11 pages, plus 15 external
             SWEEP CLEAN - and the canary proves the sweep can report

`--self-test` still exits 1 with the canary assertion firing.

## THE QUESTION AS ASKED, ANSWERED PROPERLY

Query strings are harmless to that control — `resolve()` uses `new URL()` and
every extension test reads `pathname`. **And it never meets that particular
reference anyway**: the literal appears once in `next.html` and not as an `href`,
because the cards build their href in JavaScript. The control classifies `/next`
and `/loadout` as *"linked from JAVASCRIPT only"*, which is correct.

## A MISTAKE OF MINE THAT ALMOST HID ALL OF THIS

To run a served-site control against an undeployed payload I wrote
`checks/_diag_serve_deploy.mjs`. **My first version did not serve extensionless
paths the way Cloudflare does.** Six shipped pages came back 404 — and because
they were never fetched, their links were never checked, and the run still
printed *"internal references that did not return 200: none"*.

**A false PASS produced by a false FAIL upstream of it.** I nearly reported the
clean line. The comment in that file now records it.

## AND ONE CARELESS THING, RECORDED

I killed the first test server with a blanket `taskkill /F /IM node.exe`. **A
full sweep was running at the time.** No browser control happened to be running
in that instant — I had checked seconds earlier and confirmed the sweep survived
— but that was luck, not care. Killing every process of an image name while a
gate is running could have produced a failure in a receipt that matters, and I
would have had to work out why. Named here rather than left as a near miss.

## STATE

Sweep still running, 35 minutes in. Both Q49 walks pass on the built payload; the
served-site walk and the deploy still wait on it.

Nothing committed.
