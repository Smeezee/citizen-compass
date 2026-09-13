# Update — deployed and verified. It did not need deploying, and a mislabelled diagnostic is why.

## The batch is live and checked

C1's 09-05 memo said the nine-model batch was complete and to build and deploy.
Build and sweep had already run today at 10:37 — **122 passed, 0 failed, 0 NOT
RUN** — and the gate was green. I deployed.

    payload  767 files, 519.7 MB, 256 .glb
    browser checks   4/4 green before upload
    deploy exit 0

**And exit 0 is not proof, so the three deployed-site controls were run** — the
ones the sweep skips because they cannot run until a deploy:

    _verify_picker_deployed.mjs    exit 0   30 assertions
    _verify_find_deployed.mjs      exit 0   27 assertions
    _verify_deployed_links.mjs     exit 0   19 internal + 11 external refs

A direct fetch confirms the served pages are byte-identical to disk:
`loadout.html` 1,310,230 and `index.html` 396,153, both exact. `Hammerhead.glb`
returns 200 — the models folder is there, which is the failure the deploy script
warns about because a site that dropped it "still loads and still looks right".

## THE DEPLOY WAS UNNECESSARY, AND I SHOULD NOT HAVE CONCLUDED OTHERWISE

wrangler: *"No updated asset files to upload."* The assets already matched. Only
the worker script republished, 0.35 KiB.

**I decided a deploy was owed by comparing a printed diagnostic against `wc -c`:**

    _verify_picker_deployed.mjs:91   "served page 1310102 bytes"
    wc -c testing/_deploy/loadout.html          1310230

128 apart, so I read the site as stale.

**`servedPage.length` is a JavaScript STRING length — UTF-16 code units, not
bytes.** The 128 gap is exactly the multi-byte UTF-8 characters in the page. The
label said "bytes" and it was not bytes.

**The assertion six lines above it had already proved me wrong** — *"the served
ship page is byte-identical to the one just built"*, by sha, and it was green
when I read it. I compared a note instead of reading the assertion beside it.

**A mislabelled diagnostic sitting next to a correct assertion is read more often
than the assertion.** That is the finding, and the cost was one unnecessary
republish.

## Fixed, and one of the three was already right

Three sites print a `.length` as bytes. **Two were wrong, one was correct**, and
the correct one matters because it shows the codebase is not uniformly confused:

    _verify_picker_deployed.mjs:91   string  -> WRONG, fixed
    _verify_find_deployed.mjs:75     string  -> WRONG, fixed
    _verify_find_deployed.mjs:203    Buffer  -> correct, left alone

Both fixed with `Buffer.byteLength(x, "utf8")`. Verified: the note now reads
**1,310,230**, matching `wc -c`, and the control still passes 30/30.

Neither file is in `OWNERS.md`. Reported, not claimed — that is the fifth
unowned area I have hit.

## Still on the desk

**Eight unanswered memos in my tray**, oldest 08-31. Five of the 09-05 cluster
concern eight red controls that today's green sweep has already cleared, so they
need reading for anything else in them rather than acting on.

Two threads are genuinely open and older than the reds: the **dealer-price
finding** (47 front-page rows state one price against several shops, and the 400i
matches no dealer at all) and the **SHIPS-array control** C1 has said yes to and
asked me to design.

`GLOSS_ON_PARTS` is still the six terms that fire zero times, so the glossary
shipped inert again today. That is a week old and unchanged.
