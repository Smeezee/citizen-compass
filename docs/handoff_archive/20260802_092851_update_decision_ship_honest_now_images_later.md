# DECISION — foundation first, images later, honesty as the standing constraint

**Ruled by Sleven, 2026-08-02. Recorded by C2. Planning only, nothing built.**

---

## THE RULING

1. **Foundation first.** The data is gathered. The job now is putting it where
   people can use it — not waiting for a better version.
2. **Images are a later, separate workstream.** Sleven will capture in-game
   screenshots of items, weapons, gear, locations and routes himself. It is
   legwork, it is attainable, and it does not gate anything.
3. **Ship what we have, presented as well as it can be presented.**
4. **The constraint: never misrepresent what the information is.** Partial is
   fine. Dressed-up is not.

Point 4 is the extension of rule 4 (*every price shows its age and its source*)
from prices to the whole site. **Rule 4 says how sure we are about a number.
This says how sure we are about a page.**

---

## WHY THIS IS THE RIGHT CALL, AND NOT JUST AN ACCEPTABLE ONE

**Only 136 items of 7,728 — 1.8% — have nothing beyond a name and a category.**
69% can say what a thing is; 36% can say where to buy it; 98.2% can say
something more than a name.

Waiting for images would hold back a site that can already answer more than any
competitor for the categories people actually search.

**And the images, when they come, will have better provenance than anything else
on the site.** The ship models came from a Hugging Face pack whose author's
redistribution rights are unestablished. UEX's 394 shop screenshots are
community-uploaded with unknown licensing. **Screenshots Sleven takes himself
have none of those questions** — known capturer, known patch, no third-party
redistribution. That makes the later workstream cleaner than the shortcut would
have been.

---

## PER-DOORWAY COVERAGE — measured, all 7,728

This was flagged as unknown in the Build A plan. 69% was the average; the split
matters more.

| doorway | items | with description | with price |
|---|---:|---:|---:|
| Clothing | 1,809 | **87%** | 58% |
| Food, drink & meds | 170 | **85%** | 69% |
| Ship parts | 758 | 74% | 63% |
| Suits & armour | 2,565 | 71% | 32% |
| Weapons & ammo | 558 | **50%** | **28%** |
| Tools & equipment | 111 | **50%** | **94%** |
| *(no doorway)* Liveries | 1,099 | 72% | 2% |
| *(no doorway)* Decorations | 77 | 52% | 19% |
| *(no doorway)* Miscellaneous | 334 | 19% | 12% |
| *(no doorway)* Commodities | 175 | **0%** | **0%** |

**No doorway is catastrophically thin — the worst is 50%.** The eight-doorway
structure survives the data.

Three things worth acting on:

- **Weapons & ammo is the weakest doorway** — 50% description, 28% priced — and
  it is a high-demand category. It will look thinnest exactly where people look
  hardest. **It is also the strongest candidate for the first screenshot batch.**
- **Tools & equipment is inverted** — 94% priced but only 50% described. It
  answers *"where do I buy it"* almost perfectly and *"what is it"* poorly. That
  is a different page emphasis, not a worse page.
- **Commodities is 0% and 0%.** Nothing at all. Confirms it gets no doorway, and
  is a second argument for pulling UEX commodity prices.

---

## THE ENGINEERING CONSEQUENCE — build the slot now, fill it later

Images being a later workstream is only cheap **if the data model expects them
today.** Retrofitting a media layer into 7,728 rendered pages is expensive;
declaring the field now costs nothing.

**Add to the item record in the Build A data contract, nullable from day one:**

    img       relative path, or null
    img_src   'sleven' | 'rsi_store' | 'uex' | null
    img_patch patch the screenshot was taken in
    img_date  capture date

`img_src` matters because the three sources have **different permission
stories** and a future question about one must not force a review of all of
them. `img_patch` matters because a screenshot of a 4.9 item is wrong by 4.12
and nothing else on the page would say so.

**The rendering rule from the coverage work still holds:** a null image produces
**no visible gap** — no placeholder box, no grey silhouette, no "image coming
soon." The layout is designed imageless and images are added *into* it, not
reserved *within* it.

---

## CAPTURE PROTOCOL — worth agreeing before the first batch, not after

The legwork is the expensive part. These are the things that are free at capture
time and unrecoverable afterwards.

1. **Record the patch version with every batch.** A folder per patch —
   `shots/4.9/` — is enough. Without it every image silently rots and nothing on
   the page can flag it.
2. **Name by UUID, not by display name.** `28c76343-8da9-495a-9339-3d5de02e6c3c.jpg`,
   not `venture-helmet-white.jpg`. Display names change between patches and
   collide — "Full Set" exists twice, "Container" exists twice. **UUIDs are the
   join key everywhere else on the site and they do not move.**
3. **One item, one frame, consistent framing.** A gear page with fifteen
   differently-lit, differently-cropped shots looks worse than no images at all.
   Same angle, same background, same distance — a shop inspection view is
   probably the most repeatable.
4. **Capture the shop, not just the item, when you are already there.** 394 of
   479 shops have a UEX screenshot of unknown licence. Our own would replace
   those cleanly, and a shop photo answers *"what does this place look like so I
   can find it"* — which nothing currently does.
5. **Start with Weapons & ammo.** Weakest doorway, high demand, and the 461
   price-without-description items are the group where a picture carries the most
   information.
6. **Do not capture liveries.** 1,099 items, 2% priced, no doorway. It is the
   largest category and the least worth the walking.

---

## WHAT THIS DOES NOT CHANGE

Nothing in `claude/plan-build-a-static.md` or `WO-CRAFT-01`. The four-question
standard, the no-visible-gap rule, and the doorway structure were all designed
imageless. **This ruling confirms the plan rather than altering it** — which is
the useful thing about having designed for the constraint before deciding to
accept it.

---

## NOT VERIFIED

- **Whether the 461 price-without-description items overlap the 1,387 carrying an
  RSI store link.** Still not computed. If they do, that group has a cheap
  legitimate image source before any screenshot is taken.
- **Whether RSI store images may be hotlinked or copied at all** under the Fan
  Kit position. Not researched.
- **What the 136 truly-bare items are.** Some are likely placeholder or debug
  records that should not get a page rather than a photograph.
