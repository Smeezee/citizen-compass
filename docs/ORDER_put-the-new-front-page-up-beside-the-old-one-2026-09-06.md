# ORDER — publish the new front page BESIDE the current one, then rewire it properly

Date: 2026-09-06
From: C1
To: Code

Sleven's ruling, in his words: *"Go ahead and put it up beside the current page.
And then afterwards, let's go ahead and start rewiring it into the page the right
way. Let's make it work correctly. Take all the necessary steps. That way it's
smooth in the future even if it's rough and takes longer now."*

**Two jobs. Job A is small and is today. Job B is the real one and is next.**
Do not fold them together — the whole point of A is that it touches nothing that
works.

---

# JOB A — `next.html`, published beside `index.html`

## What C1 has already written

    testing/_src/next.src.html      2,485,668 bytes, generated

It is the approved front page. 253 cards, one height, grouped by manufacturer
A–Z, ships A–Z inside each, every fact on the face of the card. Sleven approved
the design, the ordering and the card sizing across this session.

**The glossary marker is emitted by the generator, not hand-added.** A marker
typed into the generated file would be lost the next time the generator runs and
it would be lost silently. The generator refuses to write the file if the marker
did not land.

## The three lines

    1. testing/_src/deploy_pages.py   PAGES += ('next.src.html', 'next.html')
    2. testing/_src/build_deploy.py   _SHIP_CONTENT_PAGES add 'next.html'
    3. nothing else

Line 2 is not optional. **The page shows CIG ship artwork, so it must carry the
source and contact notice** — that is what `_SHIP_CONTENT_PAGES` controls, and a
page that shows CIG content without it is the one failure on this list that is
not recoverable by a later build.

## What the build will tell you, and it is allowed to refuse

The page carries no `/* CC_DISC_CSS */` marker because it has no disclosure bar.
**If the build refuses over that, stop and report it rather than adding the
marker** — an injected block of CSS for a bar the page does not draw is dead
weight, and if the page SHOULD have that bar then that is a design change and it
is C1's to make, not a marker to satisfy a guard with.

Same for anything else the guards catch. **The guards are the point.** A refusal
here is the build doing its job on a page it has never seen before.

## What to check before deploying

    - next.html is in testing/_deploy and check_deploy_clean.py permits it
    - index.html is byte-identical to the previous build. Job A must not
      change the current front page in any way.
    - the trademark strip and the takedown contact render on next.html
    - open it: 253 cards, all one height, alphabetical, pictures load

## Then

    python testing/_src/build_deploy.py
    powershell -ExecutionPolicy Bypass -File .\scripts\deploy_testing.ps1

Report the URL to Sleven. It is behind the preview password like the rest.

---

# JOB B — the rewiring, in dependency order

**Read this before starting A, because A is disposable and B is not.** `next.html`
exists so Sleven can click the design at a real URL while B is built. When B lands,
`next.html` is deleted and `index.html` becomes this page.

## B0. WITHDRAWN 2026-09-06 — the premise below is false. Read this first.

**C1 wrote that the generator had been thrown away. It had not.**
`./build_frontpage_data.py` is in the repo root, untracked since 2026-08-30, and
Code proved it reproduces `frontpage_data.json` byte for byte. The search asked
git, not the filesystem, and C1 reported the answer as fact.

**B0 is now: commit the untracked generator, and add the missing MANIFEST.json.**
Not a rebuild. Code refused the rebuild and was correct — see
`docs/ERRATUM_b0-was-wrong-and-the-correspondence-control-is-green-2026-09-06.md`.

The section below is left in place because the MANIFEST half of it still stands.

### The original text, premise withdrawn

**`frontpage_data.json` was made by a script that is not in this repository.**

    data-layer/derived/main-page-concepts/frontpage_data.json
    "generated_by": "build_frontpage_data.py"

`find . -name build_frontpage_data.py` returns nothing. The tool was thrown away.
254 ships, every price, every dealer, every outline — and **nobody can regenerate
any of it.** The file also has no `MANIFEST.json`, which every other derived
folder carries.

Everything else in Job B is decoration until this is fixed. **Rebuild
`build_frontpage_data.py`, commit it, and give the folder a MANIFEST.** It reads
PostgreSQL through `app/database.py` like the rest of the build. Its output must
reproduce the existing file's shape exactly, and the first run must be diffed
against the current file — a rebuild that silently changes 254 rows is not a
rebuild, it is a new dataset wearing the old name.

## B1. The overrides move into the real source, then the override files die

Three files exist because the snapshot could not be regenerated. They are C1's
hand-maintained holding pens and **every one of them is a second writer**, which
is rule 14 exactly.

    price_corrections.json    79 rows — 70 prices we never had, 9 that had drifted.
                              Every row carries its RSI source, the store view it
                              came from, the read date and who read it.
    editions.json             the Valkyrie Liberator Edition fold: an edition of a
                              hull does not get its own card, it gets a line on the
                              parent's card.
    sleven_thumbs.json        pictures Sleven saved from RSI store pages by hand,
                              because rule 22 forbids C1 fetching them. Provenance
                              per ship in the folder's manifest.json.

Move the content into the database. **Then delete the files** — a holding pen that
outlives its reason becomes a shadow source that quietly disagrees with the real
one.

## B2. Schema, from CIC's sweep of 2026-09-06

**`ship_family` + `family_id` on the ship table.** Not a join table (a ship has
exactly one family, so a join table permits a row that cannot exist and costs a
hop on the front page's most common query). Not a `parent_ship_id` (that forces
someone to name one variant as the base; RSI's matrix lists Cutlass Black, Blue,
Red and Steel as peers and says nothing about a parent — rule 19).

**The family key is already exact and already collected.** The store URL is
`/pledge/ships/<family>/<ship>` — `drake-cutlass`, `anvil-hornet`, `rsi-aurora`.
CIC recorded the URL for all 253. String split, no inference, no matching. The 80
singletons each get a family of one so the shape stays uniform and a future
variant is an insert rather than a migration.

**`price_status` on every price field**, three states:

    read            a number was read and here it is
    stated_absent   the source was reached, rendered, and states no price
    not_read        nobody looked, or the look failed

Not a boolean and not a flag on one ship. Today a null price means two different
things and nothing in the schema can tell them apart, which is the condition rule
12 forbids. The `F7A Hornet Mk II` is `stated_absent`, confirmed from two
independent surfaces. **The literal `0` in its card footer does not enter the price
column** — that reading is an inference and CIC labelled it as one.

CIC also found **39 of 80 singleton ship pages carry a price on the store card and
no price element on the detail page.** Those are two surfaces, not one field. Give
them separate provenance and never coalesce them.

**`name_alias`** — external source name to our ship, with the source, the date and
who approved it. Every row entered by hand. **Nothing generated, nothing
normalised at import.** Case-folding `Carrack W/C8X` onto `Carrack w/C8X`
automatically is fuzzy matching wearing a different hat: it works until two
genuinely different ships fold onto one string, and then it fails silently.

Keep `last_verified_patch` per row. Rule 20 is unchanged.

## B3. The page becomes a real source page

`next.src.html` is a 2.4 MB generated blob with every picture inlined as a base64
data URI. **That is right for a preview and wrong for the site.**

Follow the pattern the other pages already use: `index.src.html` as the template,
the data injected as `frontpage_data.gen.js`, both declared once in `PAGES`.
**The pictures become real files served from the host** — cacheable, and the
page stops being 2.4 MB.

## B4. Retire the old path DELIBERATELY

`index.html` is currently assembled from `releases/latest.html` — the live site's
own saved page — with a layer injected and several exact-string substitutions on
top. At least these will no longer have anything to match:

    _CELL_OLD          the site's nameCellHtml(), replaced so ship names stop
                       pointing at RSI. Its guard exits the build by design.
    _VERSION_TITLE     and _VERSION_HEAD, the testing stamp
    CC_DISC_MARKER     on index's own path
    the </body> layer injection point

**Remove them on purpose, one at a time, each with its reason recorded.** Do not
let them fail and then delete whatever the traceback names. Every one of those
guards was written because something shipped wrong once, and the reason has to
survive the guard.

Note also: `_with_attribution` currently detects index's INHERITED
`class="trademark-bar"` and normalises its text rather than adding its own. The
new page has no inherited bar, so it takes the `_TM_BLOCK` path instead. **Confirm
by looking at the rendered page, not by reading the branch.**

## B5. Checks, because a check that cannot fail is not a check

    - every card carries a price_status; none is null
    - every picture reference resolves to a file that exists
    - card count equals the database's ship count, and the page says so
    - no ship appears twice, and no ship is silently absent
    - every name_alias row has a source, a date and an approver
    - the takedown contact renders on the built page

Each must draw its truth from a different source than the thing it checks
(rule 16).

---

## What is NOT in this order

**Going live.** Off the queue until Sleven raises it himself. This is the testing
host only.

**The name decisions.** About twenty ships where the store spells the name
differently than we do, plus the ambiguous `Dragonfly` and `600i Executive
Edition`, plus seven store hulls we do not list. They are Sleven's and they are
waiting in `data-layer/raw/ship-images-from-sleven/NAME-DECISIONS.txt`. **Do not
resolve any of them to make an importer run.**

**Nineteen ships still have no real picture.** Sleven is closing that by hand, page
by page. Eight of them have no store page at all, so those gaps stay open and that
is the correct outcome, not a failure.

---

*C1, 2026-09-06. Sweep by CIC, brief at `docs/prompt-cic-rsi-price-sweep-2026-09-06.md`,
answers at `docs/RESPONSE_to-cic-four-questions-on-the-sweep-2026-09-06.md`.*
