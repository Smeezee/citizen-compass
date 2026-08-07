# AMENDS WO-IMAGE-01 — every published image must carry a CIG logo. And that fights the atlas plan.

    from    C2, 2026-08-07, recording CIC research round 2
    for     C1 -> Claude Code
    amends  docs/WORKORDER_image-01-what-we-may-use-and-how-to-serve-it.md §5
    source  support.robertsspaceindustries.com/hc/en-us/articles/360006895793
            robertsspaceindustries.com/en/tos · caniuse.com · retrieved 2026-08-06

---

## 1. THE NEW REQUIREMENT — nobody knew about this

**From the FAQ's "Made by the Community" Notices section, verbatim:**

> "One of these logos should be included, along with the trademark notice
> indicated in the Fan Kit materials, **in the corner of all imagery at no less
> than 50% opacity and of a legible size.**"

**Every published image must carry:**

    a "Made By The Community" logo        from the Fan Kit
    plus the trademark notice             wording is in the Fan Kit
    in the corner
    at >= 50% opacity
    at a legible size

**This is the only explicit image rule CIG publishes, and WO-IMAGE-01 was
written without it.**

**It makes the Fan Kit download a BLOCKING dependency, not a nice-to-have.** The
logo files and the exact trademark string exist only inside the kit. **We cannot
correctly mark a single image until someone accepts the agreement and retrieves
them.** §3 of WO-IMAGE-01 just became the critical path.

---

## 2. AND IT FIGHTS THE ATLAS PLAN — C2 spotted this, CIC did not

**WO-IMAGE-01 §5 recommends sprite atlases of ~1,024 small icons to stay inside
the file-count budget. Squared against §1 above, that plan has a problem.**

**"A legible size" and a 64-pixel icon are incompatible.** A logo legible in the
corner of a 64 px thumbnail does not exist. **Either the icon is unusable or the
mark is not legible, and the rule says legible.**

**Three ways this could resolve, and C2 cannot pick between them from the text:**

    a  the rule applies to the IMAGE AS DISPLAYED at a size where a mark can be
       legible - i.e. detail views carry it, thumbnails are covered by the
       page's site-wide notice
    b  thumbnails are not "imagery" in the sense meant, and the rule targets
       shared/downloadable images
    c  the rule applies to everything, in which case per-item thumbnails are
       not viable at small sizes and the design changes

**This is a real design fork and it is unresolved.** **[C1] Do not build the
atlas pipeline until it is settled.** The cheapest resolution is to look at what
the Fan Kit's own documentation says about applying the mark — **another reason
the download is now blocking.**

**Note the interaction with §XIII.D**, which prohibits *"reproduce, modify,
translate or create derivative works of the RSI Fansite Content"* — **while the
Made-by-the-Community rule requires overlaying a logo onto imagery.** CIC's
read, which C2 endorses: display-oriented adaptation for a fan site is
contemplated. **Minimal alteration plus the required overlay is the safe
posture.**

---

## 3. THE FULL FAN-SITE CHECKLIST — verbatim, and now complete

**From the FAQ's "Fan Sites" section:**

> "Fan sites must include this notice (whether an org domain, fan site, blog,
> social media page, or other similar page):
> **'This is an unofficial Star Citizen fan site, not affiliated with the Cloud
> Imperium group of companies. All content on this site not authored by its host
> or users are property of their respective owners.'**
> This notice must be placed where it is **open, obvious, and can be readily
> seen by any visitor to the page. It should not be 'hidden' in any way (i.e.
> printed in a smaller font than other notices, or tucked away in an obscure
> place).** …
> Your site must also **include a link to the official site** so that anyone who
> wishes to find it can easily do so.
> You must also **refrain from using any of the following official brands and
> marks in your site URL (domain): 'Star Citizen', 'Roberts Space Industries',
> 'Cloud Imperium', 'Turbulent', and 'Squadron 42'.**
> Also, you must **not use the name of any in-game entities in your site URL**,
> (i.e. ship manufacturers)…"

**The checklist, all assertable:**

    1  notice present, verbatim, character for character
    2  open, obvious, readily seen - NOT a smaller font than other notices,
       NOT tucked away. A persistent footer on every page is the safe reading.
    3  a link to the official RSI site, easy to find
    4  domain free of the five brand strings AND of in-game entity names
    5  no paywall, no ads, no sponsor revenue
    6  the logo + trademark mark on imagery - §1

**Item 2 is stricter than the project understood.** *"Not printed in a smaller
font than other notices"* is a concrete, testable rule and **the compliance
strip should be checked against it, not just for presence.**

**Item 4: `citizencompass.netlify.app` PASSES.** "Citizen" alone is not on the
list — "Star Citizen" as a phrase is — and "Compass" is not an in-game entity.
**Carry this forward: any future custom domain must be re-checked against the
same five strings and against manufacturer names.**

---

## 4. A DANGLING REFERENCE IN CIG'S OWN DOCUMENT

**The exemption names six guidance sections. One of them does not exist.**

CIC pulled the FAQ's complete heading list: Foreword/Terms, Attribution and
Credit, "Made by the Community" Notices, Video Use and Streaming, Fan Kit, Fan
Sites, Fan Fiction, Translation and Fan Localization, Fan Film/Machinima Policy,
Bar Citizen.

**There is no "Third-Party Platform Advertising" section**, though the exemption
sentence points at one. **Its rules live in "Video Use and Streaming" and ToS
§XIII.D**, both already quoted on file.

**Recorded so nobody hunts for a section that is not there.**

---

## 5. Q9 IS A DEAD END — the wiki's permission table does not help

The named contributors are Aelanna Tesla, Mr Hasgaha, The Damn Shames and
Rellim (in-game screenshots, 2016–2017) plus a Ben Lesnick / CIG grant for
Comm-Link art and text.

**Three reasons it fails:**

- **The grants are scoped.** Wording is consistently *"grants permission to use
  his work **on /r/starcitizen**"* — a specific place, not a public licence.
- **The evidence is gone.** `forums.robertsspaceindustries.com` **no longer
  resolves** (NXDOMAIN) since CIG moved to Spectrum, so the Aelanna and Lesnick
  permalinks are dead. The reddit links are decade-old deep comment links.
- **The one verifiable grant is a screenshot of a conversation**, uploaded to
  the wiki under CC0 by an editor. **Proof of permission, not a published
  licence.**

**Verdict: no broad, transferable licence found. Do not build on it.**

**The one narrow thread left:** those contributors' Flickr accounts still exist.
**If any has since set a Creative Commons licence on their photos, those
specific photos are independently usable.** Per-photographer, per-photo — not a
table-wide grant. **Low priority.**

---

## 6. FORMAT NUMBERS — the figure C2 flagged as unverified, now sourced

**caniuse.com / StatCounter GlobalStats, June 2026 dataset, retrieved
2026-08-06:**

    AVIF   93.40% + 0.02% partial = 93.42%   "Baseline - widely available"
    WebP   96.07% + 0.08% partial = 96.16%

**Holdouts:** WebP's ~3.8% is legacy and edge browsers. AVIF's ~6.6% sits in
older Safari on iOS, older Samsung Internet, KaiOS, and older UC/QQ/Baidu
builds.

**Recommendation unchanged and now evidenced: AVIF with a WebP fallback via
`<picture>`.** The AVIF holdout population overwhelmingly supports WebP, so the
pair covers effectively everyone.

---

## 7. THE FOUR REMAINING SITES — closed, none grants reuse

    erkul.games          standard fansite disclaimer. The TOOL is CC BY-NC-ND
                         4.0 - that is the code, not the imagery, and ND would
                         bar derivatives anyway. No image grant.
    sc-craft.tools       disclaimer only. No Terms or License page.
    star-crafting.com    "Community tool - not affiliated..." No image grant.
    sccraftlab.com       standard disclaimer plus trademark notice. No grant.

**The Q4 gap is now closed. Every candidate source has been checked and none
grants image reuse.**

---

## 8. WHAT CHANGES IN WO-IMAGE-01

    §3 Fan Kit      promoted from "inventory it" to BLOCKING. The logo files
                    and trademark string gate every published image.
                    Needs Sleven's go-ahead to accept the agreement.
    §5 delivery     the atlas plan is NOT cleared to build. §2 above must be
                    settled first.
    §1 notice       the check is stricter than written - add the
                    "not a smaller font than other notices" test and the
                    official-site link.
    NEW             every published image carries the logo + trademark mark.
                    Bake it at generation time, not in CSS - a CSS overlay
                    disappears the moment an image is saved or hotlinked.

---

## 9. NOT VERIFIED

- **The exact trademark-notice string and the logo files.** Inside the Fan Kit,
  not downloaded. **The one open dependency before any image can be marked.**
- **How the marking rule applies to thumbnails.** §2. **A real design fork.**
- **Whether a systematic image library reads as "sharing with the world."**
  CIC's read, labelled as interpretation: a curated, self-captured,
  properly-noticed, non-commercial library **most likely** sits inside the
  exemption — and CIG says nothing about scale, volume or databases anywhere.
  **The strongest argument in our favour is that the Fan Sites section
  contemplates fan sites as ongoing reference destinations and imposes
  conditions rather than a scale cap.** Accept as known residual risk.
- **Whether any wiki contributor's Flickr now carries a CC licence.** §5.
- **C2 and CIC are not lawyers. Hard rule 8.**
