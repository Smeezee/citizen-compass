# ANSWERED — image licensing. Research by CIC, 2026-08-06. With two things it did not connect.

    from    C2, 2026-08-06, recording CIC's research and analysing it
    for     C1 -> Claude Code
    closes  docs/FINDING_images-why-cstone-fails-and-the-four-options.md
    amends  docs/CORRECTION_extracted-textures-are-not-granted.md - confirmed
    sources robertsspaceindustries.com/fankit · /en/tos ·
            support.robertsspaceindustries.com/hc/en-us/articles/360006895793
            starcitizen.tools/Star_Citizen_Wiki:Copyrights · uexcorp.space/about/terms
            finder.cstone.space · developers.cloudflare.com/workers/platform/limits

---

## 1. THE HEADLINE — item icons do not exist in ANY licensed form, from anyone

**The Fan Kit contains no item artwork.** Its categories, verbatim from CIG's own
FAQ:

> "Concept art, Logos, Screenshots, Wallpapers (desktop and mobile), 3D Models,
> Artwork, Social media banners & icons, Fonts, Music and certain audio tracks."

**Ship-level and brand-level only. No item icon, component, or shop-kiosk
category exists.** Nothing in it maps to 7,728 priced items.

**And every other candidate inherits the same ToS rather than granting anything:**

    Cornerstone / finder.cstone.space   NO reuse grant anywhere. Confirmed by
                                        absence - no Terms, License or
                                        Attribution page exists. Footer asserts
                                        CIG ownership, which is the opposite of
                                        a grant.
    starcitizen.tools                   CC BY-SA covers WIKI-AUTHORED TEXT only.
                                        "All game content and materials are
                                        copyright of Cloud Imperium" is carved
                                        out. Per-file template routes users back
                                        to the RSI ToS.
    UEX                                 data platform. Its upload licence runs
                                        TO UEX, not to third parties.
    Erkul, sc-craft, star-crafting,
      sccraftlab                        not verified this session. Flagged, not
                                        guessed. None is expected to differ.

**There is no licensing shortcut through a third party. They all inherit
§XIII.D.**

---

## 2. THE FIND THAT MATTERS MOST — player screenshots ARE covered

**C2 said the fan ecosystem runs on "tolerance, and tolerance is not a licence."
That was too pessimistic. CIG has written it down.**

From the official Fandom FAQ, **"Non-Commercial → The Exception"**, verbatim:

> "Images, Videos and Live Streams of RSI IP which follow the guidance below
> ('Made by the Community Notices', 'Video Use, and Streaming', 'Third-Party
> Platform Advertising', 'Fan Sites', 'Fan Fiction' and 'Translation/ Fan
> Localization') for the purposes of sharing with the world (including contest
> submissions) **are generally exempt from needing written and express
> permission from RSI**."

**A player's own in-game screenshot is an image of RSI IP.** Provided the site
carries the unofficial notice, links to the official site, and runs no paywall
and no ad or sponsor revenue — **all of which Citizen Compass already does** —
it is inside the stated exemption.

**Two honest caveats CIC flagged and C2 endorses:**

- **The underlying artwork stays CIG's copyright.** This is permission to
  display, not a transfer.
- **§XIII.D permission is revocable at CIG's "sole discretion."**

**And one edge C2 adds that CIC did not name:** the exemption is written around
*"sharing with the world (including contest submissions)"* — the language of
community sharing. **Whether a systematic, curated image library attached to a
reference database reads as "sharing" is the honest edge of this clause.** It
probably does. It has not been tested. **Do not build 7,728 pages that break if
it does not.**

---

## 3. THE CONNECTION NOBODY MADE — the collector is already an image source

**`WO-COLLECT-01 rev 5 §4.11` already specifies saving a ~200×40 crop per row,
for provenance.**

**Those crops are player screenshots.** Sleven's own, taken in his own client,
of items on a shop shelf. **They fall under exactly the exemption in §2.**

**So the collector was already going to produce the only licensed per-item
imagery available to this project, and nobody noticed.**

**What follows, and it is cheap:**

- **Widen the crop.** A 200×40 strip proves a price row. **A crop that also
  takes the item's icon cell out of the kiosk gives a real per-item picture at
  no extra capture cost.** Decide this before the reader is built, because the
  crop geometry is set there.
- **It naturally produces the "500 correct images" over the "7,728
  questionable" ones** — you get pictures of the items people actually shop for,
  because those are the shelves someone stood in front of.
- **Provenance is already stamped** — patch, build, UTC, location, install id.
  **Better than any third-party image on the internet.**

**This is now a second, independent reason the collector is worth building, and
it survives the UEX commodity finding untouched.**

---

## 4. THE "ASK CIG" PATH IS CLOSED FOR NOW — verbatim

C2 has twice called a separate licence "the short path." **CIG's own FAQ says
otherwise:**

> "To request a Non-Commercial License please file a ticket with the Community
> Team via Support." … **"We are not currently offering any Non-Commercial
> licenses. No means no, please do not submit multiple requests for this type of
> license, not all requests will receive a response."**

Same "not currently offering" caveat on the Limited Commercial License route.

**Contacts, for the record:** Support ticket → Community Team;
`support@cloudimperiumgames.com`; formal notices to
`legal_notices@cloudimperiumgames.com`, 13420 Galleria Circle, Suite A-250,
Bee Cave, TX 78738.

**C2's "short path" framing was wrong and is withdrawn.** One polite ticket is
worth trying; **a roadmap must not depend on it.**

---

## 5. THE MANDATORY NOTICE — verify the live site carries it exactly

Required, verbatim:

> "This is an unofficial Star Citizen fan site, not affiliated with the Cloud
> Imperium group of companies. All content on this site not authored by its host
> or users are property of their respective owners."

**Citizen Compass has a compliance strip and it has been broken at least once
already** (`WO-TABS-01` flags that a bottom bar would cover the Fan Kit
disclaimer at `z-index:6`). **Check the live wording against the above
character-for-character, and check it is not obscured on mobile.** This is a
one-line job and it is a condition of everything else in this document.

---

## 6. FOR THE HISTORIAN — a harder line than the ToS sentence C2 analysed

**CIC surfaced this in passing and did not connect it. It is the most important
thing in the report for the Historian.**

From the same official FAQ, as a hard rule on fan sites:

> **"No content is allowed to be held behind paywalls / subscriptions / or other
> barrier to access."**

**That is blunter and broader than the §XIII.D sentence C2 analysed earlier
today.** C2's reading was: *you may charge, provided you use no CIG images,
artwork or marks.* **This line does not carve out art. It says content.**

**It does not settle the Historian question**, because it appears in fan-site
guidance and the boundary between a fan site and a separate paid product is the
same undefined thing as before. **But it is a second official statement pointing
the same direction, and it is more explicit than the first.**

**Filed to the Historian's parked legal page. Not actionable — the Historian is
years out — but it should not be discovered late.**

---

## 7. CLOUDFLARE — the remaining unknown, closed

**Verified, primary:** *"Number of Static Asset files per Worker version —
20,000 (Free) / 100,000 (Paid)"* and *"Individual Static Asset file size —
25 MiB / 25 MiB."*

Combined with the earlier finding that *"Requests to static assets are free and
unlimited"* and *"There is no additional cost for storing Assets"*:

    per-file size    25 MiB, both tiers - a non-constraint for icons
    bandwidth        not a constraint
    requests         not a constraint for static assets
    FILE COUNT       the only limit that bites. ~8,775 free headroom.

**The reframe that solves it: one file can hold many icons.**

**Sprite atlases.** ~1,024 icons on a grid plus one JSON coordinate map = **2
files instead of 1,024.** The whole set fits in roughly 16 files.

**Three real caveats, worth carrying:**

1. **Cache granularity is lost** — changing one icon re-downloads the atlas.
   **Group by stability**: rarely-changing sets in large atlases, volatile ones
   in small.
2. **Browser decode/texture memory** — keep atlases to a few thousand icons and
   a few MB, far under 25 MiB.
3. **CSS `background-position` is clumsy for responsive and HiDPI.** Prefer a
   JSON map with `object-fit`, or an SVG `<symbol>` sprite **if the icons were
   vector — ours are raster, so raster atlases are correct.**

**AVIF vs WebP:** AVIF for large atlases, where it wins clearly. **AVIF's
container overhead can lose to WebP below ~64 px**, so for any
individually-served small icon, test rather than assume. **Serve AVIF with a
WebP fallback via `<picture>`.** CIC declined to state a live browser-support
percentage rather than invent one — **verify at caniuse.com/avif before
shipping.**

**Hosting:** stay on Workers static assets and defeat the count with atlases.
**R2 is the pressure valve** — 10 GB free, zero egress, no per-object count
limit — served via a bound Worker with self-managed cache headers. **A separate
asset domain buys little and adds DNS and certificate surface.**

---

## 8. WHAT TO ACTUALLY DO

    1  verify the live compliance notice, character for character         §5
    2  do NOT chase item icons from any external source. They do not
       exist in licensed form and no third party can grant them.          §1
    3  widen the collector's crop to capture the item's icon cell.
       Decide before the reader is built.                                 §3
    4  Fan Kit for ships, manufacturers, concept art and brand assets.
       Download it and inventory what is actually inside - resolutions
       and formats are NOT published on the web and remain unknown.       §1
    5  atlas whatever we end up with. AVIF, WebP fallback, group by
       stability.                                                         §7
    6  one polite Support ticket if Sleven wants item art designated.
       Expect no reply. Do not plan around it.                            §4

---

## 9. NOT VERIFIED

- **Fan Kit internal resolutions and formats.** Not published; CIC did not
  download it, correctly, without Sleven's go-ahead. **Unknown until someone
  accepts the agreement and looks.**
- **Erkul, sc-craft.tools, star-crafting.com, sccraftlab.com terms.** Flagged by
  CIC as not personally verified rather than guessed. **Low value — none is
  expected to grant reuse — but the gap is real.**
- **Live AVIF browser support percentage.** CIC declined to state a figure it
  could not source. Correct call.
- **Whether a curated reference image library reads as "sharing with the
  world."** §2. The honest edge of the exemption, untested.
- **C2 and CIC are not lawyers. None of this is legal advice.** Hard rule 8 puts
  Fan Kit, trademark and legal text solely with Sleven.
