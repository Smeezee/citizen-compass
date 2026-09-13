# RESEARCH — Echo on editions, packages and paints

**Returned 2026-09-12 by Echo, from the brief at
`claude/ECHO_variants-packages-and-paints-on-a-ship-page-2026-09-12.md`. Assessed by the
Adjutant desk. Her report follows in full, unchanged.**

## ASSESSMENT

**She accepted the plan and corrected its shape in the first line, which is the useful
part.** Sleven's framing was one list of "shapes". Echo's: three different relationships
that must not share a list.

    an EDITION or PAINT   the same ship, cosmetically changed  -> folds into the ship page
    a TRUE VARIANT        a different machine                  -> keeps its own card
    a PACKAGE             several ships sold together          -> its own labelled section

**That matches Sleven's own edition rule rather than replacing it, and it adds the piece he
had not settled: a package gets a heading of its own, "Packages containing this ship", with
the exact contents listed and each one linked to its own page.**

## THE TWO CORRECTIONS THAT CHANGE WHAT WE WOULD HAVE BUILT

**1. The store link cannot be the identity of an edition.** Our own count said 24 rows have
no link and they are mostly the edition rows. Echo's answer is that each edition holds a
local record with a verification status — verified with a date, not located, or retired —
and the link is dated evidence attached to it. **That means the feature can ship before the
24 links are found, which is the difference between a design that waits and one that does
not.**

**2. Do not call the section "buy" or "available".** We do not track package prices or
availability, and a label implying we do is the footer defect again. Her wording: "Official
editions", "Packages containing this ship", "Official RSI page", and one line saying the
package price is not tracked.

## WHAT SHE ANSWERS FOR SLEVEN'S THREE OPEN QUESTIONS

1. **Which ship carries the line** — every ship in the package carries it, because the
   section is about this ship's relationships, and the Pisces owner learns their ship comes
   in a Carrack bundle.
2. **Whether it shows a price** — no. Name, contents, internal links, an official link when
   verified, and a stated line that we do not track the price.
3. **Where the words stay findable** — the edition and package names become searchable child
   terms on the canonical ship, and the result says WHY it matched: "Matched package:
   Carrack Expedition". **Never keep a fake duplicate card just to keep a word searchable.**

## THE PAINT ANSWER, AND ONE THING THE DESK ADDS TO IT

**Paint records exist in community-extracted game data** — `StarCitizenWiki/scunpacked-data`
carries `Ship.Paints` item records naming their ship tags and a palette id. **What does not
exist is a rights-cleared, browser-ready texture set**, and a palette id is not a picture.

**The desk's addition, from our own record:** we are already consuming that dataset. The
ship page's own badge cites `scunpacked snapshot 20260827T225641Z` for component data. **So
the paint records are already within reach of a pipeline we run — which makes this a rights
and fidelity question rather than an access question.**

Her order stands and is the right one: names and links now, an official image only if the
terms clearly cover that exact asset, then a one-ship one-paint technical proof scored
against an official reference, and only then anything across the catalogue.

## THE RIGHTS FLAG, AND IT IS SLEVEN'S ALONE

**Two things she raises under RSI's own Fankit and Fandom FAQ, updated 2026-09-02:**

- **Fan Kit permission does not automatically cover material extracted from the game.** The
  FAQ separates the two, and says no permission is given to post RSI content to other sites
  for download. **Linking is the low-risk route because we redistribute nothing.**
- **The FAQ says fan content should not sit behind a paywall, subscription "or other barrier
  to access" — and our preview is password-gated.** She does not claim this breaks the
  policy; she flags that the wording is ambiguous about a temporary private development
  preview.

**Hard rule 8 puts every word of this with Sleven. It is reported, not acted on.**

## WHAT IS NOT ANSWERED

No measurement of any of this on a reference catalogue rather than a store — her evidence is
Google's product-variant documentation, Schema.org, and Baymard's usability testing, and
Baymard sells UX research, which she says plainly. **The interaction itself stays a
hypothesis until somebody watches a person use it**, which is the task test Sleven has
already declined for now.

## ROUTED

To Architecture:
`memo_architecture_echo-on-editions-packages-and-paints-and-the-three-answers.md`.

---

## ECHO'S REPORT, AS DELIVERED

# Citizen Compass — ship editions, packages, and paints

**Research date:** 2026-09-12  
**Purpose:** Decide how Citizen Compass should represent cosmetic editions, true variants, multi-ship packages, search results, and paint previews.  
**Labels:** **ESTABLISHED** = supported directly by evidence; **RECOMMENDATION** = design judgment based on that evidence; **FORECAST** = expected outcome that still needs testing.

## Direct conclusion

**RECOMMENDATION — Do not put editions, packages, and true variants into one generic “shapes” list.** They describe three different relationships:

- **Edition / paint:** the same ship, cosmetically changed. Fold it into the base ship page.
- **True variant:** a mechanically or functionally different ship. Keep its own card and page, then cross-link it to the family.
- **Package:** a purchase containing multiple ships or vehicles. It is not a version of any one ship. Show it in a separately labeled **Packages containing this ship** section and list every included item.

The plan is workable after that correction. One canonical page per real ship is the right foundation. Cosmetic editions should not inflate the ship count. Packages should remain searchable without masquerading as extra ships.

## The two flaws to fix before building

### 1. The official-store link cannot be the identity of an edition

**ESTABLISHED — Citizen Compass machine count, 2026-09-12:** 24 of 253 current rows have no official-store link, and many are precisely the editions that the proposed feature would depend on.

**RECOMMENDATION:** Each edition or package needs a stable local record even when the RSI link is missing, temporarily unavailable, or retired. Treat the external link as optional evidence with a status, not as the record itself:

- **Official page verified** — show the link and the date checked.
- **Official page not located** — keep the name and description, but do not invent a URL.
- **Official page retired/unavailable** — use only when that state has actually been verified.

This allows the design to work on day one instead of waiting for all 24 links.

### 2. “Purchasable shapes” promises information the site will not maintain

**ESTABLISHED — Baymard Institute, 2022 and 2024:** in ecommerce testing, unclear price and bundle contents caused uncertainty and forced people to bounce between pages. Baymard sells UX research and audit products, so it is an interested commercial source, but these claims are described as findings from moderated usability testing.

> “Users often can’t tell exactly what’s included in sets or bundles from the product list.”

> “Including contents and quantities directly in the list item helps users quickly assess if a set meets their needs without additional clicks.”

Source: [Baymard, “Always Include Contents and Quantities in the List Item for Sets and Bundles,” 2024-10-08](https://baymard.com/blog/include-contents-quantities-list-item-sets-bundles)

**RECOMMENDATION:** Do not label the section “Buy,” “Available packages,” or “Purchasable shapes” unless Citizen Compass also tracks current availability. Use factual labels such as **Official editions** and **Packages containing this ship**. If package prices are intentionally out of scope, say **Package price not tracked by Citizen Compass** once at the section level. The link label should be **Official RSI page**, not **Buy**.

## Question one — presentation

### A. Cosmetic editions: one product family, not separate ships

**ESTABLISHED — Google Search Central, accessed 2026-09-12:** Google’s official product-variant model groups products that vary by qualities such as color, material, or pattern under a `ProductGroup`. It separates common family information from variant-specific information and calls the single-page nested form the “most compact and natural representation.” Google is not selling a help widget; this is its official search documentation.

> “To help Google better understand which products are variations of the same parent product, use the ProductGroup class … to group such variants together.”

> “A common title and description are specified at the ProductGroup level. Variant-specific titles and descriptions are specified at the Product level.”

Source: [Google Search Central, “Product variant structured data,” accessed 2026-09-12](https://developers.google.com/search/docs/appearance/structured-data/product-variants)

**ESTABLISHED — Schema.org, accessed 2026-09-12:** `ProductGroup` is defined as products that vary only in well-described ways such as size, color, or material. The group is a shared template; the actual variants carry their differences.

> “A ProductGroup represents a group of Products that vary only in certain well-described ways.”

Source: [Schema.org, `ProductGroup`, accessed 2026-09-12](https://schema.org/ProductGroup)

**ESTABLISHED — Baymard Institute, 2021:** its ecommerce usability research recommends combining product variations into one list item rather than flooding the product list with near-duplicates. Baymard sells UX research and audits.

Source: [Baymard, “Combine Variations of Products into One List Item,” 2021-09-07](https://baymard.com/blog/combine-variations-one-list-item)

**RECOMMENDATION:** Fold cosmetic editions into the base ship. Give every edition a visible text name and an explicit type such as **Cosmetic edition**, **Paint**, or **Trim edition**. Do not rely on a paint swatch alone.

**ESTABLISHED — W3C, updated 2025-09-16:** WCAG 2.2 says color cannot be the only means of distinguishing information.

> “Use information in addition to color, such as shape or text, to convey meaning.”

Source: [W3C, Understanding WCAG 2.2 Success Criterion 1.4.1, 2025-09-16](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html)

### B. True variants: separate ship pages, visibly related

**RECOMMENDATION:** A Cutlass Red and Cutlass Black should retain separate cards and pages because their capability differs. Each page should include a **Related variants** section linking the other real variants. The family relationship should never replace each variant’s own role, equipment, dimensions, price, or shop data.

**FORECAST:** This preserves fast comparison for players searching by role while stopping cosmetic editions from inflating the catalogue. Verify it through a usability test containing both an edition query and a true-variant query.

### C. Packages: their own relationship, not a fourth ship

**ESTABLISHED — Baymard Institute, 2024:** people struggle when bundle contents and quantities are not explicit; listing them reduces uncertainty and extra navigation. Baymard is an interested commercial research vendor.

> “Sites should ensure that the exact contents of the set or bundle — including their quantities — are listed somewhere in the list item.”

Source: [Baymard, “Always Include Contents and Quantities in the List Item for Sets and Bundles,” 2024-10-08](https://baymard.com/blog/include-contents-quantities-list-item-sets-bundles)

**RECOMMENDATION:** Use a separate heading: **Packages containing this ship**. Each package entry should show:

- package name;
- the label **Multi-ship package**;
- exact contents and quantities;
- internal links to every included ship or vehicle page;
- an optional verified **Official RSI page** link;
- **Package price not tracked by Citizen Compass**.

For example, the Carrack page may state that Carrack Expedition is a multi-ship package containing a Carrack, Pisces, and Ursa. The Pisces and Ursa names should lead to their own pages. It must not appear as another Carrack variant or increase the ship count.

### D. Where it should sit

**RECOMMENDATION:** Near the ship name, show a small factual summary only when relevant: **2 editions · appears in 1 package · 3 related variants**. The full information should appear in clearly labeled sections on the same page:

1. **Related variants** — other mechanically distinct ships in the family.
2. **Editions and paints** — cosmetic versions of this exact ship.
3. **Packages containing this ship** — bundles in which this ship appears.

Do not hide the only indication behind a control that a visitor must guess exists. Collapsing a long section is reasonable, but its heading and count should remain visible.

**FORECAST:** This placement should let casual visitors ignore the extra detail while letting a person seeking a named edition find it quickly. It needs direct testing because the product research comes from retail sites, while Citizen Compass is a reference catalogue rather than a store.

### E. Search after cards are folded

**ESTABLISHED — Google Search Central, accessed 2026-09-12:** single-page variant groups can give each variant a distinct URL or parameter while retaining one canonical family page. Google recommends one canonical URL for the overall group on a single-page site.

Source: [Google Search Central, “Product variant structured data,” accessed 2026-09-12](https://developers.google.com/search/docs/appearance/structured-data/product-variants)

**RECOMMENDATION:** Index every edition name, package name, old name, and official name as searchable child terms attached to the canonical ship record.

- Search **Gladius Pirate** → return the **Gladius** card with the line **Matched edition: Gladius Pirate** and open or highlight the Editions section.
- Search **Carrack Expedition** → return the **Carrack** card with **Matched package: Carrack Expedition** and open or highlight the Packages section.
- Search **Cutlass Red** → return the separate **Cutlass Red** card because it is a real variant.

Give edition and package rows stable deep links or fragments so a search result can land on the exact match. Do not preserve fake duplicate ship cards merely to keep the words searchable.

**FORECAST:** The “matched edition/package” explanation is important. Without it, a visitor who typed Carrack Expedition and sees only Carrack may reasonably assume search ignored part of the query.

## Question two — paint on the 3D model

### What exists

**ESTABLISHED — public game-data extraction, checked 2026-09-12:** Star Citizen’s game files contain structured paint-item records. The maintained `StarCitizenWiki/scunpacked-data` repository includes an `items/` collection and individual paint JSON records. A checked record identifies itself as `Ship.Paints`, names required ship tags, and references a palette by ID. The repository says its contents are game-file data produced by a loader.

Sources:

- [StarCitizenWiki/scunpacked-data repository](https://github.com/StarCitizenWiki/scunpacked-data)
- [Example extracted paint record](https://github.com/StarCitizenWiki/scunpacked-data/blob/f45ee0159780acc67578ac0b006a6d37aade6884/items/paint_135c.json)

**ESTABLISHED — StarCitizenWiki/scunpacked, archived 2026-03-22:** the older loader documentation says it extracts XML and other data from `Data.p4k` and converts item and ship records to JSON. The loader repository is archived and points development elsewhere. This is community tooling, not a CIG-published API.

> “This is a .NET Core application which parses XML data extracted from the Star Citizen game files and produces a set of JSON files.”

Source: [StarCitizenWiki/scunpacked repository](https://github.com/StarCitizenWiki/scunpacked)

**ESTABLISHED — no official public paint API found:** CIG’s official public sources and support documentation located in this review do not publish a documented API that supplies web-ready paint textures, material files, or a supported “apply paint to model” operation.

**ESTABLISHED — no turnkey maintained community paint-render package verified:** the maintained community data proves that paint entities and palette references exist. It does not, by itself, provide a browser-ready texture set or reproduce Star Citizen’s material/shader system. No maintained source was verified that promises complete, rights-cleared, directly applicable paint materials for arbitrary web models.

### What that means technically

**RECOMMENDATION:** Do not treat a paint as a hex color. A correct 3D reproduction may require the exact model version, UV layout, material slots, palette records, textures, decals, finishes, wear settings, and shader behavior. A palette identifier proves a relationship exists; it does not prove that Citizen Compass can accurately render it.

**FORECAST:** Applying authentic paints to the current models may be possible for some ships if the models and material data came from compatible game builds. It is not yet shown to be possible across 217 models, and model-version drift could make the result wrong even when the code runs successfully.

### Safe presentation order

**RECOMMENDATION:** Use this order:

1. **Now:** edition name, plain description, verification status, and official RSI link when verified.
2. **Next:** an official image thumbnail only if the applicable CIG terms or written permission clearly allow that exact asset and use.
3. **Later:** a one-ship, one-paint technical proof using a rights-cleared source, scored visually against an official reference.
4. **Only after that proof:** consider extending model paints across the catalogue.

Do not publish a hand-tinted model as the official paint. Citizen Compass’s existing “do not guess” discipline makes a labeled approximation a poor fit. A color swatch may supplement a name, but it cannot faithfully represent patterns, markings, metallic finishes, or multi-material liveries.

## Rights and Fan Kit limits

**ESTABLISHED — RSI Fankit and Fandom FAQ, updated 2026-09-02:** RSI allows fan sites subject to its rules. The page requires a visible unofficial-site notice and a link to the official site. It says Fan Kit assets may be used under the Fan Kit Agreement and Terms of Service, and lists screenshots and 3D models among Fan Kit materials.

> “The Fan Kit contains official assets and materials that you are welcome to use … provided you agree to the Fan Kit Agreement and follow all applicable rules.”

> “RSI allows fan sites. Fan sites must include this notice … ‘This is an unofficial Star Citizen fan site…’”

Source: [RSI, “Star Citizen Fankit and Fandom FAQ,” updated 2026-09-02](https://support.robertsspaceindustries.com/hc/en-us/articles/360006895793-Star-Citizen-Fankit-and-Fandom-FAQ)

**ESTABLISHED:** The same FAQ distinguishes Fan Kit materials from material extracted from the game. It does not state that technical access to `Data.p4k` grants permission to redistribute extracted textures, palettes, or models. It also states that no permission is given to post RSI content to 3D-modelling or other content websites for download by others.

**RECOMMENDATION:** Do not assume the Fan Kit’s permission automatically covers extracted paint assets. Before copying an RSI product image or embedding extracted paint/material files, confirm that the exact source and use are covered by the agreement Sleven has accepted or by written CIG permission. Linking to the official page is the lowest-risk route because Citizen Compass does not redistribute the artwork.

**RECOMMENDATION:** The current password-protected preview deserves a narrow legal check before external testing. The FAQ says content should not be held behind a paywall, subscription, “or other barrier to access.” It is unclear from the public page whether a temporary private development preview is intended to fall within that language. This report does not claim that it violates the policy; it flags the ambiguity.

## Final decision package

### Adopt now

**RECOMMENDATION:**

1. One card and canonical page per real ship.
2. Cosmetic editions fold into **Editions and paints** on the base ship page.
3. Mechanically or functionally different variants retain separate cards and pages.
4. Packages appear under **Packages containing this ship**, never as ships or variants.
5. Package rows list exact contents and internal links; package prices are explicitly not tracked.
6. Every folded name remains searchable and explains why the canonical ship matched.
7. External RSI links are optional, verified, dated evidence—not the identity of the record.
8. Begin with text and links. Do not block the information design on paint rendering.

### Research or verify before building the paint layer

**RECOMMENDATION:**

1. Confirm the official full name and classification of every suspected edition.
2. Verify the 24 missing official links; record “not located” rather than guessing.
3. Identify the exact source and game build of Citizen Compass’s 217 models.
4. Test one model and one paint for technical compatibility.
5. Obtain a rights answer specifically covering any copied store images or extracted paint/material data.
6. Compare the result against an official reference image before calling it accurate.

### Confidence

**ESTABLISHED:** The information architecture recommendation is supported by official product-group conventions and usability evidence on product variants and bundles.

**FORECAST:** The exact interaction—summary line, expanded section, and search-match wording—should work well but remains a project-specific design hypothesis until tested on Citizen Compass.

**ESTABLISHED:** Paint metadata exists in community-extracted game data.

**ESTABLISHED:** A complete, maintained, rights-cleared, browser-ready paint dataset was not found in this review.

**FORECAST:** Authentic model paints are technically plausible, but they are a later research-and-rights project, not a feature ready to build from the data currently established.

