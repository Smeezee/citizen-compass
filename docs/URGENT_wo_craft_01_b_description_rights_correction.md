# CORRECTION — the item descriptions are not cleared, and I said they were

    id          WO-CRAFT-01-B
    raised by   C2, 2026-08-02, after CIC traced the permission to CIG's own documents
    for         C1 -> Claude Code — AFFECTS WORK POSSIBLY IN PROGRESS
    priority    read before implementing WO-CRAFT-01 §WO-1

---

## 1. WHAT I GOT WRONG

I called wiring in the 5,344 CIG-written item descriptions **"the highest-value
item in the project"** and **"the cheapest large improvement available
anywhere"**, in `claude/build-spec-descriptions-and-blueprint-index.md`,
`WO-CRAFT-01 §WO-1`, `claude/plan-build-a-static.md` and
`claude/finding-coverage-and-the-newbie-standard.md`.

**I never checked whether we are allowed to publish them.** I checked that they
existed, measured the coverage, and moved straight to page design.

That is the same failure I have now made repeatedly this week in a different
costume: reasoning from what the data allows instead of from the actual
constraint.

---

## 2. WHAT CIC ESTABLISHED — traced to CIG's own documents

**The wiki's claim does not survive tracing.** Star Citizen Wiki says CIG
"granted rights of reuse for their public Comm-Link art and text." Its only
citation is a **legacy RSI forum comment by a CIG staffer**, and **that URL is
now dead** — the forums were deprecated for Spectrum. The page was last edited
April 2023.

**CIG's actual published grant — RSI ToS §XIII.D "Personal and Fansite Use"**
(version issued 25 January 2018) permits reproducing:

> "certain RSI Services-related **images, graphics or artwork** … and certain
> RSI **trademarks and logos** … that RSI may expressly designate 'for fansite
> use'"

**The word "text" does not appear in the grant.**

**The baseline it sits under — §XIII.B:**

> "You may not sell, license, distribute, copy, modify, publicly perform or
> display, transmit, publish, edit, adapt, create derivative works from, or
> otherwise make unauthorized use of RSI Content without RSI's express written
> consent."

and "RSI Content" is expressly defined to include *"titles, objects, artifacts,
characters, character names, locations, location names, stories, story lines,
dialog, catch phrases."*

**The Fankit & Fandom FAQ lists the Fan Kit contents as art and media only** —
concept art, logos, screenshots, wallpapers, 3D models, fonts, audio. **No text.**
And it states directly:

> "simply re-posting or re-uploading content or material from the RSI Services
> is not permitted."

**Nothing granting verbatim reuse of item descriptions was found**, on the ToS,
the FAQ, the /fankit page, or a site-scoped search.

### And CIC caught something I had not even considered

**The game-file descriptions are outside the fan-site grant entirely.** The
5,344 come from the game client's data files, not from a web page. The fan-site
grant covers content RSI "expressly designates for fansite use" on the website.
Extracted client data was never designated anything. **It falls under §XIII.B,
which forbids publishing RSI text without written consent.**

So the store-page question and the game-file question are two different
questions, and **neither has a permission I can point to.**

---

## 3. MEASURED — how bad is it, exactly

**The `stdItem.DescriptionText` field is almost entirely creative prose.**
Classified all 5,344:

    pure prose        5,338   99.9%
    pure stat block       6    0.1%

Example: *"CDS's quest to create the ideal light armor continues with the FBL-8a.
This light armor will keep you fast on your feet with its strategic mix of
protective plating and reinforced nano-weave fabrics…"*

**That is marketing copy. It is the most protected kind of text there is, and
republishing it on 5,344 pages is exactly what §XIII.B describes.**

### But `labels.json` is a different and much better story

The `item_Desc_*` labels are **not** the same content. 5,793 entries:

    pure stat block   1,568   27.1%
    mixed             1,324   22.9%
    pure prose        2,901   50.1%

The stat-block and mixed entries carry a **structured factual header**:

    Manufacturer: Behring
    Item Type: Burst Generator
    Size: 4
    Damage Type: EMP

    (then, in "mixed" entries, a prose paragraph)

**2,892 items — 50% — have machine-readable facts we can extract.** Manufacturer,
item type, size, damage type, focus. **Facts are not copyrightable.** A table
built from them is our data presentation, not CIG's writing.

---

## 4. WHAT CHANGES IN WO-CRAFT-01 §WO-1

**The join is still worth building. What it feeds changes.**

    BEFORE   extract description -> display verbatim on the item page
    AFTER    extract description -> parse the factual header -> display OUR table
                                 -> discard the prose paragraph, do not publish it

**Concretely:**

- **Do not render `stdItem.DescriptionText` to a page.** Keep it in the derived
  file if useful for internal matching, but it does not reach a user.
- **Do parse the `labels.json` factual headers** — `Manufacturer:`,
  `Item Type:`, `Size:`, `Damage Type:`, `Focus:` — into real fields. 2,892
  items gain structured data this way.
- **Write our own one-line description from those facts.** *"A size 4 EMP burst
  generator from Behring."* That is ours, it is accurate, and it is more use to
  a new player than CIG's copy.
- **The 5,344 coverage figure stands as a data figure and falls as a display
  figure.** Do not quote 69% description coverage on any page or in any pitch
  until this is settled.

**Nothing else in WO-CRAFT-01 is affected.** WO-2 through WO-5 are unchanged —
blueprints, ingredients, contracts and prices are facts and numbers throughout.

---

## 5. THE SILVER LINING, AND IT IS REAL

**CIG's descriptions are marketing prose, not explanations.** *"CDS's quest to
create the ideal light armor continues"* tells a new player nothing about
whether to buy it.

The whole position is *plain answers, legibly presented, honest about how sure
they are* — and the four-question standard demands the page say **what a thing
is and what it does** in ordinary words. **CIG's copy does not do that.** Ours,
written from the facts, would do it better.

**The constraint pushes the product toward what it was supposed to be anyway.**
Writing 7,728 one-line descriptions from structured facts is a generation job
against real fields, not 7,728 acts of authorship.

---

## 6. WHAT I RECOMMEND — ask, and settle it permanently

**Sleven has a live contact at RSI legal who replied on 2026-07-28.** One
specific question closes this for good and costs an email. It also matters for
clause 2(k) anyway, because the site is materially changing.

Suggested text, deliberately narrow and easy to answer:

> Following your confirmation of 2026-07-28 regarding citizencompass.netlify.app,
> I would like to check one point before expanding the site.
>
> The site is a non-commercial fan reference. I would like to display, for each
> in-game item, the item's own in-game description text — the same wording a
> player sees in the game and on your store pages — alongside its price and the
> shops that stock it, with a clear notice that the text is CIG's and the site
> is unofficial.
>
> Is that permitted under the Fan Kit Agreement or the fan-site provisions of
> the Terms of Service? I am aware §XIII.D names images, graphics, artwork and
> marks, and I did not want to assume it extends to text.
>
> If it does not, I will write the descriptions in my own words from factual
> attributes instead, and no CIG text would appear on the site.

**Note what that last line does:** it tells them the site works either way, so
the easy answer is not a defensive "no."

**Until an answer arrives, proceed as though it is no.** That is the same
standard already applied to sources 4 and 5, and to CmdrQuattro's data.

---

## 7. NOT VERIFIED

- **The Fan Kit Agreement's full text.** It is gated behind the download/accept
  flow and was not retrieved. It may say something the ToS does not. **Worth
  reading before sending the email above** — Sleven has already accepted it, so
  he has a copy.
- **The game EULA**, which governs the client-data side. Not read.
- **Whether item *names* are affected.** §XIII.B names "titles" and "objects."
  Every fan site uses item names to identify things, and CIG confirmed
  compliance for a site full of ship names on 2026-07-28. **I am treating names
  as necessary identification, not reuse — but that is my reading, not a
  finding.**
- **Whether the labels.json factual headers are themselves considered creative
  selection.** A list of attributes is data; someone could argue the choice of
  attributes is editorial. I think that is weak, but I am not a lawyer and
  neither is CIC.
