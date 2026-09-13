# Update — the inspector's one-line fix is in, and it cannot work yet. Reporting, not fixing.

**2026-09-04 · Code**

## Done as ordered

`testing/_src/build_deploy.py` - `'_inspect.html'` added to
`_SHIP_CONTENT_PAGES`, per
`ORDER_the-inspector-missed-your-build-by-90-seconds-2026-09-04`. Build ran
clean and produced `testing/_deploy/_inspect.html`, 1,154,755 bytes. The source
had stopped moving for three minutes before I built - I checked, because that
order exists precisely because a build beat an edit by ninety seconds.

## And the page still has no source notice. The line is necessary and not sufficient.

The built page is **1,154,730 bytes** of content, which is the order's own
"trademark only" simulation figure to the byte. Its "with source notice" figure
was 1,155,581. The notice is not there.

**Why, exactly:**

    build_deploy.py:315
      _SRC_BLOCK = _attr.source_notice(_contact) if _cig_count and _contact else None

    build_deploy.py:356
      if _ship_content and _SRC_BLOCK:
          _add = _SRC_BLOCK + "\n" + _add

`_SHIP_CONTENT_PAGES` controls `_ship_content`. It is the SECOND condition.
`_SRC_BLOCK` is `None`, so the branch cannot be reached whatever that set says.

`_cig_count` comes from `scripts/cig_assets.py: tagged_count()`, which reads
`data-layer/cig_assets.json`. **That file does not exist.** Nothing has ever been
registered as CIG-sourced, so the count is 0 and the build says so on every run:

    CIG-sourced assets registered: 0 - no source notice, and no contact
    needed until there is one

**So NO page on this site carries the source and takedown notice** - not the
inspector, not loadout.html, not index.html. I checked all three for it and the
result is the same on each. This is not new with the inspector and I did not
introduce it.

C1's simulation appended `source_notice()` by hand, which is why one line looked
sufficient. In the real build the block is never constructed.

Meanwhile `testing/_deploy/models/` holds **258 `.glb` files** - the exact count
the order gives for what the inspector displays.

## I am reporting this and not touching it

Hard rule 8: a gap in attribution or takedown wording is **reported, not fixed.**
Creating `data-layer/cig_assets.json`, or registering 258 models as CIG-sourced,
is an attribution decision and the notice text is Sleven's alone. I have not
created that file, registered anything, or edited any notice, and I am not
offering a view on what the right answer is.

**What is mechanically true, and all I am claiming:** the build has a working
source-notice mechanism that is switched off because its register is empty, and
the one-line change I was ordered to make will start working the moment that
register is not empty. My line is correct, it is in, and it is inert until then.

## The deploy question, which is C1's and Sleven's

The order's own words are *"Without this line it ships the trademark strip and
NOT the source and takedown notice"* - written as the thing to avoid. After my
change it still ships exactly that.

**The trademark strip IS present.** The testing site is behind the private-
preview password gate. And every other ship page on the site is already in this
same state, so the inspector would not be a new category.

Holding the deploy for a decision rather than shipping the thing the order named
as the failure. Say the word and it goes out in one command; the payload is
built and waiting.
