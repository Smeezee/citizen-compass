# DESIGN — the front page, and a defect underneath it that matters more than the layout: this site has 316 ships and, to a search engine or a pasted link, exactly ONE page. Every ship lives behind a `#hash`, there is no sitemap, no robots.txt, no description and no share card anywhere on the site. A free public reference that cannot be found or shared is the problem to fix before the front page is redrawn.

    from      C3 (Cowork), 2026-08-30
    for       C1 to route.
    raised by Sleven: look at our main ships page, look at every other tool that
              provides ship information, and redesign how we give the viewer
              the information. *"I think the spreadsheet way is outdated now,
              and I think we need to redesign the URL and the HUD of what the
              main page looks like."*
    method    read our own build on disk; every competitor measured live in a
              real browser at a forced 1400x900 viewport. Nothing quoted from
              memory.
    NOTE      the testing site's index is behind the private-preview password.
              **I did not enter it and will not** - I read the built
              `index.html` from disk instead. §7.

---

## 1. WHAT OUR FRONT PAGE ACTUALLY IS

`testing/_deploy/index.html`, read from the build:

    h2  Ship Purchase Matrix          <- the front page
    h2  Development Progress
    h2  Sale Calendar
    h2  Legend & Sources

    the matrix, 10 columns:
      Ship · Role · Price (aUEC) · Astro Armada · Crusader Showroom
      · New Deal · Teach's · Buy & Fly · Pledge Price (USD) · Confidence/Notes

    controls present:  shipSearch · searchCount · currencySelect
                       "Pick a category" · "Jump to a manufacturer" · backToTop

**`backToTop` is the tell.** A page that needs a button to get you home is a page
that is long, and "jump to a manufacturer" is a second one — those are both
mitigations for length rather than features.

**Sleven's instinct is right about what it is.** It is a spreadsheet with dealer
columns. **Whether that is outdated is a more interesting question than it looks —
§4.**

## 2. WHAT EVERYONE ELSE ACTUALLY DOES — measured, not remembered

All three at a forced 1400 x 900.

**spviewer.eu — the spreadsheet, done properly**

    tables 1 · columns 20 · rows 241
    document height 900px = EXACTLY ONE SCREEN
    filters: name/role search, size, manufacturer, stat filters
    tabs: Perf · Compare · Ranking · Items · Metrics
    tagged 4.10.0.12519617 - current with the live patch
    images 2 · canvas 0

**The whole table lives inside a fixed frame and scrolls internally, so the page
never grows.** 241 ships and 20 columns, and you never leave the first screen.
**That is a spreadsheet that works, and it is the strongest ship-data page in the
hobby right now.**

**Fleetyards — cards, and they cost more than they look**

    tables 0 · card grid, 30 per page, 9 pages
    each card 1051 x 286 px
    document height 9,940 px = 11.04 SCREENS for 30 ships
    -> roughly 99 screens of scrolling to see the fleet
    images 22 · canvas 0

**This is the trap.** Fleetyards traded the spreadsheet for cards and made scanning
**worse** — eleven screens to see thirty ships, against spviewer's one screen for
241. **Cards are a spreadsheet with more scrolling and fewer facts.**

**Erkul — a dashboard with no hero object**

    canvas 0 · 65 SVGs · document exactly 1 viewport tall
    four panel columns: 236px nav, ~192px rail, then 843 + 413

**No 3D anywhere in any of them. Not one canvas element across all three.**

**And one competitive fact I have to report against my own earlier claim:
spviewer's own front page currently advertises an "#Armor Deflection Calculator."**
My weapons finding treated Deflection as a field nobody had used. **Somebody has.**
Our advantage there is narrower than I said.

## 3. THE DEFECT — 316 SHIPS, ONE PAGE. FIX THIS FIRST.

Read from the build, not inferred:

    every ship's address    /loadout#AEGS_Avenger_Stalker|,,,,,|,,,,,
    robots.txt              ABSENT
    sitemap                 ABSENT
    <meta name=description> ABSENT on every page
    canonical link          ABSENT
    Open Graph / share tags ABSENT
    <title> for all 316 ships   "Citizen Compass — Loadout Bench"

**Everything after the `#` is invisible to a search engine.** A hash is handled by
the browser and never sent to the server, so as far as Google is concerned this
entire site is four pages, and the Vulture is not one of them.

**Three consequences, and each of them alone would justify the work:**

- **Nobody can ever find a ship page by searching for the ship.** A player typing
  *"Drake Vulture cargo"* cannot land on ours, because there is no Vulture page to
  land on. **For a free reference whose entire purpose is being found, this is the
  ceiling on the whole project.**
- **A pasted link is dead on arrival.** Drop a ship link in Discord or Spectrum and
  it renders as "Citizen Compass — Loadout Bench" with no image, no description, and
  no ship name. **The site's best growth channel is players sharing builds, and
  every shared build currently looks identical.**
- **`Copy share link` is a button that produces an unreadable string.** It is on the
  page today and it hands over `#AEGS_Avenger_Stalker|,,,,,,,,|,,,,,,,,`.

**THIS IS WHAT "REDESIGN THE URL" SHOULD MEAN, and it is bigger than the front
page.** A layout is how well the site works for someone already on it. **This
decides whether anyone arrives at all.**

### 3.1 The shape to move to

    now      /loadout#AEGS_Avenger_Stalker|,,,,,,|,,,,,,
    ships    /ship/drake-vulture
    a build  /ship/drake-vulture/b/7f3k9q        <- short code, not a slot dump
    browse   /ships           /ships/drake        /ships/salvage

**A real path per ship, one page each, each with its own title, description and
share card.** *Drake Vulture — Citizen Compass* with the hull's own render as the
preview image.

**And the loadout stops living in the address bar.** A short code keeps links
readable and short enough to paste in chat, which the current string is not.

**Static hosting is not an obstacle.** The site is on Cloudflare Workers, which can
route `/ship/*` to one document, and the 316 pages can equally be generated at build
time — **which is the better answer anyway, because a generated page carries real
text a crawler can read.**

**A caution worth writing down: do this once and do not change it again.** URLs that
move break every link anyone ever shared. **This is the most expensive thing on the
site to get wrong twice.**

## 4. "THE SPREADSHEET IS OUTDATED" — half right, and the accurate half is the useful one

**The half that is wrong: a table is still the best tool ever invented for comparing
many things across many axes.** spviewer proves it — 241 ships, 20 columns, one
screen, and it is genuinely good. **Replacing a table with cards makes scanning
worse, and Fleetyards' 99 screens is the receipt.**

**The half that is right, and it is the real problem: a table answers a question
nobody actually has.**

**Nobody arrives thinking "show me 241 ships by 20 columns."** They arrive with one
of five intents:

    1  I know the ship. Take me to it.
    2  I want to buy one and I do not know which.
    3  I am deciding between two.
    4  What changed in the new patch?
    5  I am just looking.

    a matrix serves     1  badly - you scan a column for a name
                        2  not at all - it lists, it does not help you choose
                        3  badly - the two rows are never adjacent
                        4  not at all
                        5  not at all

**So the fault is not the table. It is that the table is the WHOLE PAGE.**

**The front page should ask what you came for, and the matrix should be one of the
answers rather than the site's front door.** That is the redesign, and it does not
require throwing away work that already exists — the matrix stays, it stops being
the first thing.

## 5. THE FRONT PAGE — what to build

### 5.1 The one thing nobody else has

**Not one competitor renders a single 3D model. Zero canvas elements across
spviewer, Fleetyards and Erkul.** We have 259 hulls with real geometry, 6,058
markers, and a viewer already shared between two pages.

**So the front page's distinctive move is the same as the ship page's: the hull,
live, at browse time.** Not a photograph like Fleetyards — **the actual model, the
one you will be flying around in a moment.**

### 5.2 The shape

**A stage that holds one hull, and a way to move through the fleet beside it.**

    ┌──────────────────────────────────────────────────────────────┐
    │  CITIZEN COMPASS          [ what are you looking for? ]      │
    ├──────────────────────────────────────────────────────────────┤
    │                                                              │
    │                    DRAKE  VULTURE                            │
    │                 [ the hull, live, large ]                    │
    │                                                              │
    │   light salvage · 2,513,700 aUEC · 12 SCU · 1 crew           │
    │                                                              │
    │   ‹  Cutlass Black                          Herald  ›        │
    ├──────────────────────────────────────────────────────────────┤
    │  ▸ all 316 ships as a table    ▸ compare two    ▸ what's new │
    └──────────────────────────────────────────────────────────────┘

**Five or six figures under the hull, not twenty.** The ones that decide whether you
keep looking: role, price, cargo, crew. **Everything else is one click away and the
click is the point** — this page's job is to get you to a ship, not to be the ship.

**The search box is the primary control**, because intent 1 is the most common
arrival and it is currently served by scanning a column.

**The three links at the bottom are the other four intents, named plainly.** The
matrix is one of them and it keeps everything it does today.

### 5.3 Why this is not Fleetyards

**Fleetyards shows thirty static images and calls it browsing.** This shows **one
hull, live, that you can turn** — and moving to the next is a keystroke rather than
a scroll. **One object treated properly beats thirty treated as thumbnails**, and it
is the only version of this page that uses the thing we have and they do not.

**The measured argument: Fleetyards needs 11 screens to show 30 ships. This needs
zero — the fleet moves through a fixed stage and the page never grows.**

### 5.4 The honest risk, named

**A one-at-a-time browser is worse than a grid for "show me everything at once."**
That is a real loss and it is why the table link is on the page rather than buried.
**The design bet is that arriving visitors want one ship and returning visitors want
the table** — and if that bet is wrong, the table is one click away and nothing is
lost but the first click.

**Second risk: 259 of 316 hulls have models.** The other 57 need a designed empty
state that says the model is missing rather than showing a blank stage. **The site's
own standard: say what you do not have.**

## 6. THE HUD — what it should and should not mean

**Sleven's word, and it needs a definition or it turns into decoration.**

    a HUD IS      readable at a glance, in a fixed place, while you are busy
    a HUD IS NOT  glowing frames, scan lines, corner brackets and animation

**The three rules that follow, and they apply to the front page and the ship page
alike:**

**Fixed positions.** The same figure is in the same place on every ship. **A number
that moves cannot be read at a glance, and an instrument's whole value is that you
stop looking for things.**

**Nothing decorative may cost a row.** Already a stated rule in the loadout source
(`P3: THE COMPACTION PASS`). **It should be the front page's rule too.**

**The hull is the only thing allowed to be loud.** Everything else is quiet by
default and gets louder only when it is a warning. **That is the same disclosure
rule the rest of the site follows, applied to the front page.**

## 7. WHAT I CHECKED AND WHAT I DID NOT

**Checked, live in a real browser at a forced 1400x900:** spviewer (1 table, 20
columns, 241 rows, 1-screen document, filter set, 4.10 tag, and its own advertised
Armor Deflection Calculator); Fleetyards (0 tables, 30 cards of 1051x286, 9,940px =
11.04 screens, 9 pages); Erkul (no canvas, 65 SVGs, 1-screen document, four panel
columns).

**Checked, from our own build on disk:** the front page's four sections and the
matrix's ten columns; `shipSearch`, `currencySelect`, the manufacturer jump links and
`backToTop`; the absence of robots.txt, sitemap, description, canonical and Open
Graph on every page; the shared `<title>` across all ships; and the `#hash` ship
address.

**Did NOT check:**
- **How our own front page LOOKS.** It is behind the private-preview password.
  **I did not enter it — entering a password is something I do not do**, and reading
  the build gave me its structure but not its appearance. **If you want a judgement
  on how it looks, unlock it in that tab and say so, or paste a screenshot.**
- **Whether the 3D viewer can carry a browse page's performance budget.** Loading a
  hull per selection on a front page is a different cost profile from one hull on a
  ship page. **Nobody has measured it and §5 assumes it is fine.**
- **What spviewer's Deflection calculator actually does.** I saw the label on their
  front page and did not open it. **It should be looked at before anyone claims that
  ground is ours.**
- **starcitizen.tools, myfleet.gg, and the official RSI Ship Matrix.** Three more
  tools I did not open. **The three I measured are the ones that set the standard,
  but this is not the whole field.**
- **I changed nothing.** No file, no page, no CSS.
