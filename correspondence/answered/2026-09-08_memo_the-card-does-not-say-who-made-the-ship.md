# Memo

To:      Engineering
From:    Audit
Date:    2026-09-08
Subject: the new front page's cards do not carry the manufacturer, and scrolling loses it — Sleven hit this while gathering data
Status:  Answered

A feature request from Sleven for the new front page. Not urgent — it goes on
the queue behind the feature inventory — but it came from real use, not from
looking at the design.

**In his words:** there needs to be a way to tell what manufacturer makes the
ship from the card itself. It does not need to be big. There are times he is
partway down the page thinking *"what type of ship is this?"* and has to scroll
back up to find the manufacturer. It bit him while he was gathering information
earlier.

## Confirmed in the source, and the fix is display-only

`testing/_src/next.src.html`, `card()` at line 259. The card renders picture,
name, availability pill, role/career subtitle, the spec row, price, shop line,
editions and note. **The manufacturer is not on it.**

`render()` groups by `s.m` and emits the manufacturer once per group in an
`<h2>`. So the maker's name exists exactly once for a run of cards, and the
moment that header scrolls off the top, nothing on screen says who made
anything.

**The data is already on the card object.** `s.m` is present and is already used
for grouping and inside the search haystack in `match()`. So this is a display
change, not a data change — nothing upstream has to produce anything new.

## Two shapes, and the reason it is not obvious which

**A. Put it on the card.** Small, low emphasis — the sub line already carries
role or career and could carry the maker with it, or a quiet line above the
name. Costs a little card space, and the cards are one fixed height by ruling,
so whatever goes on has to fit inside that without changing the height.

Its real advantage is that it survives being seen out of group context. After a
search or a career filter, `render()` regroups the hits, and a person looking at
a single result should still be able to tell who made it.

**B. Make the group header stick while you scroll its group.** Nothing added to
the card, no space cost, and it answers the exact complaint — the maker stays on
screen the whole time you are inside that manufacturer's run.

It does not help when a card is looked at outside its group, and it is a scroll
behaviour that has to be checked at the defined viewport widths rather than just
on one screen.

**My read, not a decision:** A is the more robust of the two because the
grouping is not stable under filtering, and the two are not mutually exclusive.
The call is yours and Sleven's, not this desk's.

## One note on process

This changes what is rendered, so the UX doctrine's Section 39 applies — Level A
if it is text placed on the card with no layout change, Level B if the card
layout moves or if the sticky header is chosen, since that is presentation
behaviour at defined viewports. Worth being deliberate about: this is one of the
first items the doctrine governs, and how it is handled will be the example
everyone copies.

## What a good answer looks like

Which shape, and whether it waits behind the feature inventory or rides along
with it. It is small either way.

— Audit (C2)

---

ANSWERS:

**Architecture, 2026-09-08.**


**Shape A. The manufacturer goes on the card. Not the sticky header. Queued as Q60,
riding with Q55 rather than ahead of it.**

**Why not the sticky header, which is the cheaper of the two.** It answers the
question only while the visitor is inside that maker's group, and says nothing at all
the moment a search or a filter mixes makers together — **which is exactly when
somebody most needs to know who built the ship they are looking at.** It also does
nothing for the card as a unit: a card gets linked to, screenshotted, and read on its
own, and it should carry its own identity.

**A sticky header solves scrolling. It does not solve the card being incomplete.**
Those are different problems and only one of them was reported.

**It costs no new data and you proved that before asking.** `s.m` is already on the
card object, already used for the grouping, already in the `match()` haystack.
Display only.

**The fixed card height is a ruling and it stands.** It goes into the existing
role/career subtitle line rather than as a new line. Doctrine Section 39 Level A if
nothing moves; Level B the moment layout does.

**Riding with Q55, not ahead of it, as you proposed.** Sleven hit this while
gathering data, so it is real, but the feature inventory gates the front-page work
and a display fix does not jump that queue.
