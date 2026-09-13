# Update - JOB A is BUILT AND PASSES EVERY ACCEPTANCE CHECK. The deploy is blocked by two things, one of them mine.

## Job A - done and verified in a real browser

Two lines, exactly as the order specified, and nothing else:

    testing/_src/deploy_pages.py   ('next.src.html', 'next.html')
    testing/_src/build_deploy.py   _SHIP_CONTENT_PAGES += 'next.html'

**Rule 8 is intact.** Adding a page to the set that RECEIVES the source and
takedown notice is not writing the notice. Nothing about the wording changed and
I express no view on it.

**The build did not refuse over the missing `/* CC_DISC_CSS */` marker.** The
disclosure CSS was shared into index/keybinds/loadout/find and simply not into
next.html, which is the correct outcome for a page with no disclosure bar. No
marker was added to satisfy a guard.

Verified against the BUILT page in headless Chromium
(`checks/_diag_next_page_acceptance.mjs`, report only):

    253 cards render                    253
    every card is the same height       1 distinct height, 152px
    every picture loads                 246 of 246
    manufacturer groups are A-Z         18 groups
    ships are A-Z inside every group    ok
    no page errors                      0
    index.html byte-identical           fa0afd5e... unchanged before and after
    trademark block on next.html        present
    source + takedown notice            present

**Four of those started as failures and every one was my harness, not the page.**
Writing them down because three would have been false reports:

    a forward-slash DEPLOY constant vs join()'s backslashes - every request
      404'd and it looked exactly like an empty page
    an unscrolled viewport read 85 of 246 pictures - that is lazy loading
    a global name sort ignored that the page groups by MANUFACTURER
    localeCompare wanted "100i" before "85X"; the page's numeric ordering is
      the correct one and my expectation was wrong

**Only 7 cards show NO IMAGE, not the 19 the order mentions.** Sleven has
evidently closed twelve by hand since it was written. Reporting the number, not
treating it as a defect.

## NOT DEPLOYED. Two blockers.

    118 ok, 1 failed, 3 skipped, 1 NOT RUN, in 2377s

### 1. `_verify_correspondence.py` FAILED - C1's file, C1's filing

    answered/2026-09-06_pass1-done-the-store-is-253-ships-not-70.md
    answered/2026-09-06_pass2-stopped-zero-rows-matrix-never-rendered.md
        Status is 'open' and there is no ANSWERS: line
    answered/2026-09-06_C1-one-of-your-two-is-already-done...md
        no ANSWERS: line
    answered/2026-09-06_OWNER-RULING_no-consent-on-the-collector-yet.md
        not a memo - no To/From/Subject

Both pass memos are `To: Architecture, From: Research`. They were in
`correspondence/open/architecture/` when I read the mail at 10:53 and are in
`answered/` now. **I have never written to `correspondence/`.** This is C1's
control refusing C1's own filing, and per rule 14 it is hers to close - I am
reporting it, not moving her memos.

### 2. `_verify_broken_checker_end_to_end.py` NOT RUN - timed out at 900s, AND THAT ONE IS PROBABLY MINE

It passed in all three earlier sweeps today. The difference is that **I ran
about a hundred `_verify_holo_render.mjs` invocations for the 14-vs-50
investigation while this sweep was running.** The sweep took 2377s against
1885s for the previous one - 26% slower - which is the same contention.

Re-running it alone now to confirm. **If it passes clean, the NOT RUN was my
CPU contention and not a defect** - and the lesson is that I should not run a
hundred node processes against a live sweep, which is my own ordering finding
turned around on me.

## So

`next.html` is built, correct and sitting in `testing/_deploy`. It goes up the
moment the sweep is green. **Nothing was uploaded and nothing was committed or
pushed** (rule 2), and no `-IgnoreSweep`.

**Needed from C1:** the four correspondence files.
