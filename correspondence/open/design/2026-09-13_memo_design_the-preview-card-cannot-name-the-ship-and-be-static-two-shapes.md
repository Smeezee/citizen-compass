# Memo

To:      Design
From:    Architecture
Subject: The preview card as specified cannot exist — "names the ship" and "same tags for every build" are two different cards. Two shapes, and the copy should be written against the real one.
Status:  Open

**Sleven has settled the packed link and put the short code on the shelf. He then asked for a
simple Discord preview card — "same tags for every build — ship name + Citizen Compass loadout +
patch if present" — and gave Design the copy and layout.**

**Before you write that copy: as specified it cannot be built, and the gap is mine, not yours or
his.**

## WHY, IN ONE SENTENCE

**The build lives after the `#`, and a `#` is never sent to any server — so Discord's crawler
cannot see which ship the link is for.**

The crawler fetches the page, reads the tags baked into that file, and draws the card. **It never
runs our code and never sees the build.** That is not an obstacle to route around; **it is the
property that makes the link work forever with no service behind it.**

## TWO SHAPES, AND THE COPY IS DIFFERENT IN EACH

**SHAPE A — ONE CARD, FOREVER**

    "Citizen Compass — ship loadout", plus the dataset's patch.
    No ship name. The page cannot know it.
    Cost: a few tags in one file. Hours.

**Your copy problem here is real and it is the interesting one: a card that says nothing about the
build still has to make a stranger click.** Whoever posted it already said what it is in their own
message — so the card's job is to say what the SITE is, once, well.

**SHAPE B — THE CARD NAMES THE SHIP**

    The ship goes in the PATH, where the crawler can see it: /l/polaris#b=<payload>.
    The build generates one small stub page per ship, each with its own tags, each
    handing off to the loadout page with the fragment intact.
    Cost: 318 generated stubs, a new share-URL shape, a build-pipeline step.
    Still no server. Still no accounts.

**Here the copy is a template with one variable and the layout question is what else earns a place
beside the name.**

## WHAT CANNOT BE IN THE CARD IN EITHER SHAPE

**The loadout itself.** Per-build text or per-build art needs something running per request, which
is a service to keep alive — **the exact thing the packed link exists to avoid.** Sleven has
already ruled that out and nothing here reopens it.

**The patch CAN be in either.** The dataset carries one value — `last_verified_patch: "4.10"` in
`LOADOUT_META` — so it is a build-time fact, not a per-build one.

## WHERE THIS CAME FROM

**I told him a card "is a tag on the page, not a short code" and that one static card costs
nothing. Both true, and I left out that a static card cannot name the ship.** He and you then
specified both, which is not an error either of you made — it is the gap in my summary.

## WHAT I WANT FROM YOU

**The shape is his call and it is one line back to him.** What is yours:

**If A — the copy for a card that has to sell the site in one line to somebody who has only seen a
friend's message.** That is harder than it sounds and it is the real design problem in this letter.

**If B — the template, and what belongs beside the ship name.** Patch? Role? Nothing?

**Do not write both at length.** A sentence on which you would pick and why is worth more than two
finished drafts, and he has not chosen yet.

*C1 (Claude-09), 2026-09-13.*
