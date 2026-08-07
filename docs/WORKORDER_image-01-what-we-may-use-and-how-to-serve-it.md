# WORK ORDER — images: what we may use, and how to serve it

    id      WO-IMAGE-01
    from    C2, 2026-08-06
    for     C1 -> Claude Code
    rests   docs/ANSWERED_image-licensing-cic-research-and-analysis.md
    on      docs/CORRECTION_extracted-textures-are-not-granted.md
            docs/FINDING_rsi-tos-verbatim-correction.md
    repo    C2 wrote nothing except inbox/*.md

**The image question is answered. Item icons do not exist in licensed form from
any source. What we CAN use is narrower than hoped and more useful than
expected. This order turns that into work.**

**[C1] Items 1 and 2 are the ones with a clock on them. Everything else can
queue behind the collector.**

---

## 1. VERIFY THE COMPLIANCE NOTICE — do this first, it is a condition of everything

**Every permission this project relies on is conditioned on the fan-site rules
being followed. The notice is one of them.**

**Required wording, verbatim from CIG's own FAQ:**

> "This is an unofficial Star Citizen fan site, not affiliated with the Cloud
> Imperium group of companies. All content on this site not authored by its host
> or users are property of their respective owners."

**Three checks, all assertable:**

    a  the live site's strip matches the above CHARACTER FOR CHARACTER
    b  it is visible and not obscured - desktop AND mobile
    c  a link to the official RSI site is present

**`WO-TABS-01` already flags the hazard:** the Fan Kit disclaimer is a fixed bar
at `z-index:6` while the tabs sit at `z-index:100002, bottom:10px`. **A bottom
tab bar covers it. It has been broken once already.**

**This is a ten-minute job and it gates the legitimacy of every image and every
piece of CIG content on the site. Do it before anything else in this order.**

---

## 2. WIDEN THE COLLECTOR'S CROP — decide before the reader is built

**`WO-COLLECT-01 rev 5 §4.11` specifies a ~200×40 crop per row, for provenance.**

**Those crops are player screenshots — Sleven's own, from his own client — and
CIG's FAQ exempts images of RSI IP shared on a compliant fan site from needing
express permission.** They are therefore **the only licensed per-item imagery
this project can obtain.**

**Change: the crop must also capture the item's icon cell from the kiosk row,
not just the name-and-price strip.**

    why now      crop geometry is set when the reader is built. Retrofitting
                 means re-capturing everything.
    cost         near zero. Same frame, wider rectangle.
    what it      real pictures of the items people actually shop for, because
    buys         those are the shelves somebody stood in front of. It
                 self-selects for value in a way a bulk dump never would.
    provenance   already stamped - patch, build, UTC, location, install id.
                 Better than any image on the internet.

**[C1] The exact geometry cannot be specified until Sleven's in-game test shows
what a kiosk row looks like. Do not guess it. Make the crop rectangle a config
value and set it from the first real frames.**

**Store the icon crop as a SEPARATE file from the provenance strip.** They have
different lifetimes: the strip is evidence for review and can be discarded after
approval; the icon is a published asset.

---

## 3. THE FAN KIT — download it and inventory what is actually inside

**Confirmed: the Fan Kit contains no item artwork.** Its categories, verbatim
from CIG's FAQ:

> "Concept art, Logos, Screenshots, Wallpapers (desktop and mobile), 3D Models,
> Artwork, Social media banners & icons, Fonts, Music and certain audio tracks."

**It is still the only unambiguously licensed source we have, and it covers
ships, manufacturers and brand assets — which is most of what the site's
chrome needs.**

    where        https://robertsspaceindustries.com/fankit
    gate         no registration. "Your download will start after accepting"
                 the Fan Kit Agreement.
    unknown      resolutions and formats are NOT published anywhere on the web.
                 Nobody knows what is actually in the archive.

**[C1] Accepting an agreement on Sleven's behalf is his call, not Code's.
Confirm with him before downloading. Then inventory it: every asset, category,
resolution, format, and file size, written to a manifest.**

**Do not commit Fan Kit assets into the repo until §5's budget decision is
made** — a naive drop could blow the file count in one commit.

---

## 4. THE HARD RULE — do not chase item icons anywhere

**Recorded so no future session re-opens it:**

    Data.p4k textures      OUT. Copyrighted expression, not the designated set.
                           The grant covers "CERTAIN... images... that RSI may
                           expressly designate 'for fansite use'". A texture in
                           the shipped archive was never designated.
    .cga / .cgf models     OUT. Same reason. A model is expression as a texture is.
    cstone.space           OUT. No reuse grant exists - Cornerstone has no
                           Terms, License or Attribution page at all. Also
                           technically unusable: 3440x1440 lossless PNGs with
                           no thumbnail variant.
    starcitizen.tools      OUT for game imagery. Its CC BY-SA covers
                           WIKI-AUTHORED TEXT; "all game content and materials"
                           is carved out as CIG copyright and each file's
                           template routes back to the RSI ToS.
    UEX                    no image grant to third parties. Its upload licence
                           runs TO UEX.
    asking CIG             documented but stated closed: "We are not currently
                           offering any Non-Commercial licenses. No means no."
                           One polite ticket is fine. A roadmap must not
                           depend on it.

**The line that governs this project, and it should go into the standing rules:**

> **FACTUAL data extracted from game files** — names, stats, prices,
> coordinates, recipes, fuel rates — is what the site runs on.
> **CREATIVE assets extracted from game files** — textures, icons, models,
> artwork, and CIG's written descriptions — are not ours to take.

**We were already holding CIG's description text for exactly this reason.
Holding the text and taking the pictures was inconsistent.**

---

## 5. DELIVERY — the file-count budget decides the shape

**Cloudflare Workers limits, verified primary:**

    static asset files per Worker version   20,000 free / 100,000 paid
    individual asset file size              25 MiB, BOTH tiers
    requests to static assets               "free and unlimited"
    storage of assets                       "no additional cost"

**So bandwidth, request volume and per-file size are all NON-constraints.**
**File count is the only limit that bites. Current use ~11,225. Headroom
~8,775.**

**The reframe: one file can hold many images.**

**Sprite atlases.** ~1,024 icons on a grid plus one JSON coordinate map is
**2 files instead of 1,024.**

**Three caveats to carry, all real:**

1. **Cache granularity is lost** — changing one icon re-downloads the atlas.
   **Group by stability**: rarely-changing sets in large atlases, volatile ones
   in small.
2. **Browser decode and texture memory** — keep atlases to a few thousand icons
   and a few MB, far under the 25 MiB cap.
3. **CSS `background-position` is clumsy for responsive and HiDPI.** Prefer a
   JSON coordinate map with `object-fit`. **An SVG `<symbol>` sprite would be
   right for vector icons — ours are raster, so raster atlases are correct.**

**Format: AVIF with a WebP fallback via `<picture>`.** AVIF wins clearly on
large atlases. **AVIF container overhead can lose to WebP below ~64 px**, so for
any individually-served small image, measure rather than assume.

**Hosting: stay on Workers static assets and defeat the count with atlases.**
**R2 is the pressure valve** — 10 GB free, zero egress, no per-object count
limit — served through a bound Worker with self-managed cache headers. **A
separate asset domain buys little and adds DNS and certificate surface.**

**Every `<img>` carries `loading="lazy"`, `decoding="async"` and explicit
`width`/`height`.** Never ship one size and scale it in CSS.

---

## 6. ACCEPTANCE

    compliance notice      matches the required text character for character,
                           visible on desktop and mobile, not overlapped
    official link          present
    collector crop         icon cell captured, stored separately from the
                           provenance strip, rectangle is a config value
    Fan Kit                downloaded only with Sleven's go-ahead, and
                           inventoried to a manifest
    extracted assets       ZERO textures or models from Data.p4k in the repo
    file count             stays under 20,000 with headroom, and the number is
                           reported after any image commit
    atlases                grouped by stability, each well under 25 MiB
    images                 AVIF with WebP fallback, lazy, with intrinsic size

---

## 7. NOT VERIFIED

- **Fan Kit internal resolutions and formats.** Not published. Unknown until
  someone accepts the agreement and looks. §3.
- **Whether a curated reference image library reads as "sharing with the
  world."** CIG's exemption is written around sharing, including contest
  submissions. **A systematic per-item library is the honest edge of that
  clause. It probably qualifies. It is untested. Do not build thousands of pages
  that break if it does not.**
- **Live AVIF browser-support percentage.** CIC declined to state a figure it
  could not source. **Verify at caniuse.com/avif before shipping.**
- **Erkul, sc-craft.tools, star-crafting.com, sccraftlab.com terms.** Not
  verified. None is expected to grant reuse. Gap is real but low value.
- **Whether the collector's kiosk crop will actually contain a usable icon.**
  **Depends entirely on what the kiosk UI looks like, which nobody has captured
  yet.** §2 may turn out to be impossible. **The in-game test settles it.**
- **C2 and CIC are not lawyers. None of this is legal advice.** Hard rule 8 puts
  Fan Kit, trademark and legal text solely with Sleven.
