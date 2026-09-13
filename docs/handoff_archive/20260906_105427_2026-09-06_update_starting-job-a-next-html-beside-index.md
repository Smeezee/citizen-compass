# Update - starting JOB A: next.html published beside index.html

Received `ORDER_put-the-new-front-page-up-beside-the-old-one-2026-09-06.md`.
Read Job B first as instructed, because A is disposable and B is not.

**Job A only.** Three lines:

    1. testing/_src/deploy_pages.py    PAGES += ('next.src.html', 'next.html')
    2. testing/_src/build_deploy.py    _SHIP_CONTENT_PAGES add 'next.html'
    3. nothing else

Both files are mine (OWNERS.md). `testing/_src/next.src.html` is on disk,
2,485,674 bytes, regenerated 10:50 - six bytes off the figure in the order, which
is a regeneration, not a discrepancy worth stopping for.

**Line 2 is the compliance one.** The page shows CIG ship artwork, so it must
carry the source and takedown notice. I am adding the page to the set that
RECEIVES that notice - I am not writing or editing the notice text, which is
rule 8 and Sleven's alone.

**If the build refuses over the missing `/* CC_DISC_CSS */` marker I stop and
report**, per the order. I will not add a marker to satisfy a guard.

Checks before any deploy: `next.html` present and permitted by
check_deploy_clean.py; **index.html byte-identical to the previous build**; the
trademark strip and takedown contact actually rendering on next.html; 253 cards.

Also arrived and NOT being actioned in this job:
- `ORDER_the-front-page-is-still-the-spreadsheet...` - the 47 wrong prices.
- `FINDING_the-5-percent-threshold-measures-the-sampler...` - C1 answered my
  open question: the 14 hulls are the sampling stride, not the render. She
  leaves one thing to me - why I counted 14 and she counts 50 - and says neither
  number should be quoted until that is resolved. Queued behind Job A.
