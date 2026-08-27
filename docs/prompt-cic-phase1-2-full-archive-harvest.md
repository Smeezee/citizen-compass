# CIC — Phase 1 + Phase 2 APPROVED. Full harvest, quarantined corpus.

    from      C3 (Cowork), 2026-08-08
    for       CIC, via Sleven
    approves  Phase 1 (capture index) and Phase 2 (content), per Sleven 2026-08-08
    governs   claude/RULING_reference-archive-collect-but-quarantine.md
    paste     Sleven: hand CIC everything from "=== BRIEF STARTS ===" down.

---

## Notes for Sleven before you paste

**One scaling judgement worth making now rather than at hour six.** CIC has proven the method
works — that was the point of Phase 0. But a browser agent fetching tens of thousands of URLs
one at a time is the wrong instrument for the *bulk* of a full scrape: it is slow, it is
fragile across a session boundary, and if it dies at 60% you may have nothing usable.

**So the brief is written to fail safely rather than to assume it will finish.** Phase 1 (the
index) is well within CIC's reach and produces the highest-value output on its own. Phase 2
(content) is ordered so that the most valuable material lands first and any stopping point
still leaves something coherent.

**The trigger to hand off is written into the brief:** if the index comes back above ~5,000
URLs to fetch, CIC reports the list and Code takes the bulk pull as a resumable script.
That is not a downgrade of CIC — discovery, verification and spot-checking are exactly what it
is good at, and a script cannot do those.

**The quarantine rules are in the brief as plain instructions**, not as a policy CIC has to
interpret. The one that matters: **the corpus goes in a folder outside the repo and nothing
from it is ever committed.**

---

=== BRIEF STARTS ===

# CIC — full historical harvest for Citizen Compass. Phase 1 and Phase 2 approved.

Sleven has approved both phases, including collecting CIG's page content. Read the storage
rules first — they are the part that must not be got wrong.

## STORAGE RULES — read before fetching anything

**1. Everything goes in `C:\Users\david\cc-reference\`.** Create it if it does not exist.

**2. Nothing goes anywhere inside `C:\Users\david\citizen-compass\`.** Not in a subfolder, not
temporarily, not "just while I sort it." That folder is a git repository, and anything that
lands there can end up committed permanently — removing it afterwards is not a delete, it is a
history rewrite. **Keep the two trees completely separate.**

**3. This corpus is reference material, not publishable content.** It exists so we can study
how CIG structured things. Nothing from it gets copied into the website. When you write
*findings*, keep doing exactly what you have been doing: facts in your own words with a source
citation, never CIG's prose. The corpus and your findings are different things with different
rules.

**4. Every stored file needs provenance** — see the manifest format below. A file with no
recorded source is unusable to us, so an unrecorded file is worse than a missing one.

## PHASE 1 — the capture index. Do this first, completely, before any content.

**This is the highest-value output and it stands alone.** Even if Phase 2 never happens, Phase 1
gives us the lifecycle data the preservation project actually needs.

Harvest the capture index for these path prefixes:

    /pledge/ships/
    /pledge/Paint/
    /pledge/Packages/
    /comm-link/
    /ship-matrix
    also try: /pledge/browse/  and the bare /pledge/ prefix, in case ships moved paths over the years

For every URL found, record: **full URL, first capture, last capture, number of captures, the
distinct content digests in order with the date each first appeared, and any capture where the
status code was 404 or 410.**

**Three fields do most of the work here, so use them deliberately:**

- **`digest` is a content hash.** Two captures with the same digest are byte-identical — the
  page did not change. **The dates where the digest changes are the dates the page actually
  changed.** That is a real edit history, derived without reading a single page.
- **`statuscode`** — the first 404 or 410 after a run of 200s is approximately when the page
  was removed. That is our retirement date.
- **first and last capture** bracket existence.

Save as `cc-reference/index/<prefix>.jsonl`, one JSON object per line.

**Report when done:** how many URLs per prefix, how many show a 404 transition, and the ten
oldest first-capture dates you found. **Then stop and tell us the total count before starting
Phase 2** — if it is above about 5,000 URLs needing content fetches, we will hand the bulk pull
to a script rather than have you do it by hand, and you will move to verification work instead.

## PHASE 2 — content. Only after Phase 1 reports.

### Fetch one copy per distinct version, not per capture

**This is the single most important efficiency rule.** A page captured 200 times with only 6
distinct digests needs **6 files, not 200.** You already have the digests from Phase 1. Fetch
one capture per distinct digest and skip the rest.

This is also the correct model for a historical archive: we want the *versions* of a page, not
redundant copies of the same version.

### Save raw, do not reformat

Save the page as it came. Do not convert to markdown, do not strip tags, do not tidy. We are
studying how it was built as much as what it said — layout and structure are part of what
Sleven wants to look at. Extraction can happen later from a faithful copy; it cannot happen
later from a cleaned one.

    cc-reference/content/<prefix>/<safe-filename>__<capture-timestamp>.html

### Be resumable — assume you will be interrupted

**Write the manifest line immediately after each file is saved, not in a batch at the end.** If
the session dies at item 4,000, everything before it must still be usable and the next run must
be able to see what is already done and skip it. **A harvest that has to start over is a harvest
that never finishes.**

Before fetching anything, check whether that exact file already exists and skip it if so.

### Be polite or get blocked

Pace yourself — roughly one request every second or two, no parallel hammering. If you start
getting errors or rate-limit responses, **stop and wait rather than retrying hard**. Getting
blocked mid-harvest costs far more than going slowly. If you get blocked anyway, report it and
stop; do not try to work around it.

### Priority order — so any stopping point still leaves something coherent

1. **Anything the index shows as removed** (404 transition). These are gone from the live web
   and are the entire reason for this project.
2. **Retired paints** — the ones under `/pledge/Paint/` with no live store URL.
3. **Aurora Mk I**, every variant and every version.
4. **Comm-Links 2013 → May 2024** — readable per your Phase 0b work, and the densest source of
   dates, announcements and patch notes.
5. **Ship pages, oldest first.** Early ones are readable; later ones are shells. Fetch the
   shells anyway — the URL and date still matter, the file is small, and we may find something
   in them later.
6. Everything else.

## DATA CLEANING — the junk you already found

You flagged these in Phase 0b. Handle them at collection, not later:

- **Strip tracking parameters** from URLs before using them as identifiers or filenames:
  `?_gl=`, `?fbclid=`, `?utm_*`, and anything similar. They are session junk, not part of the
  address.
- **Truncated URLs** (`...Flame-Pa..`) — record them in a separate `index/malformed.jsonl` with
  a note. **Do not guess the completion.**
- **Encoded stray characters baked into URLs** (`%20`, `%22`, `\n`) — same treatment: record,
  flag, do not repair by guessing.
- If two cleaned URLs collide after stripping, keep both and note the collision. Do not silently
  merge.

## MANIFEST FORMAT

`cc-reference/manifest.jsonl`, one line per stored file, written as you go:

    {"file":"content/comm-link/13124-12-Million__20201112033721.html",
     "source_url":"https://robertsspaceindustries.com/comm-link//13124-12-Million",
     "archive_url":"https://web.archive.org/web/20201112033721/https://...",
     "capture_date":"2020-11-12",
     "digest":"7OT7RQALET55X645B66BOFLKD2VVQGIT",
     "statuscode":"200",
     "bytes":22762,
     "usage":"reference-only",
     "collected":"2026-08-08"}

`"usage":"reference-only"` goes on every single line without exception. It is what stops a
future session from mistaking this corpus for publishable material.

## WHAT TO REPORT BACK

Not the content. A summary:

- Counts per prefix: URLs indexed, versions fetched, bytes stored.
- **How many URLs show a removal (404 transition), and the twenty most interesting** — the
  things that existed and no longer do. That list is the point of the whole exercise.
- Anything that failed, by name, with the reason.
- Anything that surprised you.

**And keep reporting facts the way you have been** — your findings are a publishable artifact
even though the corpus is not.

## STILL UNCHANGED

Nothing requiring a login. Nothing from Sleven's Hangar. If something looks like it needs an
account, skip it and note it.

=== BRIEF ENDS ===

---

## For Sleven, after CIC reports Phase 1

Two things worth deciding once the index count is in:

**If it is large, hand the bulk pull to Code as a script.** The trigger is written into the
brief at ~5,000. A resumable script doing this overnight is a better instrument than a browser
session, and it frees CIC for the thing only it can do — checking that what came back is real.

**The removal list is the deliverable to look at first.** "Here are 800 URLs that used to
return 200 and now return 404" is the closest thing to an answer to the question you actually
asked — what did Star Citizen used to have. Everything else is supporting material.

**Two checks still outstanding before collection starts**, and I have not done either: the
current contents of `.gitignore`, and exactly which paths `Backup-CitizenCompass.ps1` sweeps.
Both matter only if something ends up inside the repo tree by accident — which the storage
rules above are written to prevent, but the checks are cheap and worth doing.
