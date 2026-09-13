# FINDING - what the other tools put on a ship card, looked at today, and one of our claims is wrong

**C1, 2026-09-06. Looked at the live sites myself in a real browser rather than
quoting the 2026-08-30 survey.** Fleetyards and Erkul only - spviewer needs an
approval I did not spend, and its shape is taken from our own record and labelled
as such.

---

## FLEETYARDS - the closest thing to what we are building

`fleetyards.net/ships`, read today. Their card carries **two facts**:

    ship name
    manufacturer

That is all. No price, no shop, no length, no crew, no cargo. **30 ships a page,
9 pages** to see the fleet. Their footer states patch `4.10.0-live.12519617`, so
their data is current - the thin card is a choice, not neglect.

Their pictures are excellent and are the reason the page works at all.

**Ours against theirs:** nine facts on the card against two, no pagination, and
the whole fleet on one page. **This gap is real and it is large.**

---

## ERKUL - AND THIS CORRECTS OUR OWN RECORD

Our survey said Erkul has *"prices everywhere, zero imagery"*. The imagery half
is right. **The rest undersold them.** Their Ship Finder card, read today:

    S1
    100i
    Origin Jumpworks
    Ship
    Exploration
    Starter / Pathfinder
    1 089 270 aUEC
    from New Deal - Lorville
    available
    2 shops

**They print the PLACE, not just the shop.** "New Deal - Lorville". We print
"at New Deal" and stop.

**That undercuts a claim this project has been making about itself.** We have
said our differentiator is picture plus price plus shop plus place in one card.
Erkul has price, shop, place, availability and a shop count in one card already.
**What is actually ours alone is the picture and the pledge price beside the
aUEC one** - which is narrower than what we have been telling ourselves.

**And we can close the place gap today at no cost.** `frontpage_data.json`
already carries every dealer's place and body:

    {"k":"New Deal","place":"Lorville","body":"Hurston","system":"stanton"}

The front page has been printing the shop and throwing the location away.

---

## WHAT IS STILL GENUINELY OURS, after correcting for the above

1. **The picture and the price in the same frame.** Erkul has no images at all;
   Fleetyards has images and no prices. Nobody has both.
2. **Both currencies together** - aUEC and the pledge store price on one card.
3. **The price SPREAD.** Nobody prints that a Vulture is 264,600 aUEC dearer at
   Teach's than at New Deal. Erkul says "2 shops" and shows the cheapest.
   **This is the tagline made literal and it is unclaimed.**
4. **Concept and pledge-only ships present and labelled.** Erkul's finder
   returned nothing for the Liberator, the Orion and the Hull D - three for
   three, from our own record, not re-checked today.
5. **Manufacturer grouping with real counts.** Erkul, Fleetyards and CStone are
   flat alphabetical.
6. **`last_verified_patch`.** CStone stamps a date. A date does not expire when
   the game changes; a patch number does.

## WHAT THEY DO BETTER AND WE SHOULD TAKE

    place as well as shop            Erkul   - we hold the data and drop it
    a shop count on the card         Erkul   - "2 shops" is a useful signal
    a freshness stamp on the price   Fleetyards prints how old the price is
    links out to other tools         Fleetyards links to Erkul, SPViewer, Ship
                                     Matrix from every ship. Ours links nowhere.

## The honest summary

**We are not building something nobody has built. We are building a card that
carries more than anyone else's while staying readable, and the only wholly
unclaimed ideas on it are the price spread and the picture-plus-price pairing.**
That is a smaller claim than this project has been making and it is the true one.

C1, 2026-09-06. Nothing built from this.
