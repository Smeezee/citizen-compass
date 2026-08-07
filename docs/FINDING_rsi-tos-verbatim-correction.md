# FINDING — RSI ToS §XIII, verbatim. C2 has been stating this wrong.

    from    C2, 2026-08-06
    for     C1 -> Claude Code, and for Sleven's Historian planning
    source  https://robertsspaceindustries.com/en/tos  — retrieved 2026-08-06
    status  VERBATIM QUOTES. Not paraphrase. Read the quotes, not my summary.

**C2 has repeated a version of this clause in `claude/historian-vision-architecture.md`
and in conversation as "the fan-site grant does not apply if you charge a
subscription or access fee." That is a paraphrase, it is imprecise, and the
imprecision changes the business answer. Corrected here against the source.**

---

## 1. WHAT §XIII.D ACTUALLY SAYS

**Section XIII.D — "Personal and Fansite Use".**

**What is granted, verbatim:**

> "we may (in our sole discretion) grant you, on a non-exclusive and
> non-sublicensable basis, permission to reproduce and redistribute on your
> fansite to end users, certain RSI Services-related images, graphics or
> artwork (the "RSI Fansite Content")"

and

> "certain RSI trademarks and logos (the "RSI Marks")"

**The condition, verbatim:**

> "You may not use any of the RSI Fansite Content and/or RSI Marks on your
> fansite if you charge a subscription or access fee to access your fansite, or
> if you make arrangements to generate advertising or sponsor revenue (except in
> regards to game streaming as set forth below), unless you enter into a
> separate license agreement with us"

---

## 2. THE CORRECTION — three things C2 got wrong or blurred

**2.1 The restriction is on USING THEIR ART AND MARKS. It is not a ban on
charging.**

C2 said the *grant does not apply* if you charge. **What it actually says is you
may not use RSI Fansite Content and/or RSI Marks if you charge.** Those are
different statements.

**The practical difference is large.** A paid product that uses **no CIG images,
no CIG artwork and no CIG logos** is not restricted by this sentence at all,
because the sentence only governs the use of those things. **It does not grant
CIG any say over a subscription that carries none of their art.**

**2.2 Advertising and sponsorship are restricted on exactly the same footing as
a subscription.** C2 has never mentioned this half. The clause bars using the
content if you *"make arrangements to generate advertising or sponsor revenue"*
— **so an ad-supported free site is in the same position as a paid one.** That
is directly relevant: Citizen Compass is free, which people assume is
sufficient. **Free is not sufficient if it ever carries ads or a sponsor.**

**2.3 There is a named escape hatch, and C2 has never mentioned it.**

> "unless you enter into a separate license agreement with us"

**A separate licence is an explicit, contemplated path written into the terms.**
It is not a loophole and not a hope — it is the mechanism CIG themselves point
at. **Any monetisation conversation should start there rather than treating the
clause as a wall.**

---

## 3. AND IT CONFIRMS THE DESCRIPTION-RIGHTS HOLD

**The granted list is "images, graphics or artwork" plus "trademarks and logos."
Text is not in it.**

That confirms `claude/finding-description-rights-correction.md` from the primary
source rather than from a dead forum link. **The hold on `stdItem.DescriptionText`
and on the CIG keybind descriptions stands, and now it stands on a verbatim
quote.**

**Note the direction of the logic, because it cuts both ways:** CIG's written
text is not *granted* by §XIII.D, so publishing it is unlicensed regardless of
whether the site is free. **Being free does not fix the description question. It
never did.**

---

## 4. §XIII.E — VIDEO, WHICH IS A DIFFERENT AND MORE PERMISSIVE REGIME

**Section XIII.E — "Video Use (incl. Gameplay Streaming)".** Verbatim:

> "You may not charge users to view or access your videos, e.g. a paywall or
> mandatory charge, ticket, or subscription. You also may not sell or license
> videos containing RSI Content to others for a payment or compensation of any
> kind"

**But paid advertisement on streaming channels is explicitly contemplated**,
aligned to the video provider's own terms — which is the exception the §XIII.D
sentence refers to with *"except in regards to game streaming as set forth
below."*

**So the streamer-monetisation precedent C2 has cited is real, but it lives in a
different subsection with different rules and it does not transfer to a data
service.** Citing "streamers monetise" as support for a subscription data
product is not sound. **Delete that argument from the Historian planning.**

---

## 5. WHAT THIS MEANS FOR EACH PROJECT

**Citizen Compass — free, no ads, no sponsor.** Fully inside §XIII.D. **The two
live constraints are unchanged and both are about content, not money:**

    text          NOT granted. Descriptions stay held.
    images        granted - BUT the 4,805 images found in the wiki source are
                  hosted by cstone.space, a third party. CIG granting fansite
                  use of THEIR art says nothing about Cornerstone's copies.
                  Two separate permissions, and we have neither confirmed.

**Adding advertising or a sponsor to Citizen Compass would forfeit the Fan Kit
grant** unless a separate licence is in place. **That is a new constraint on the
record — it was never stated before.**

**AI Historian — subscription.** The workable reading, and it is narrower and
better than "you cannot charge":

    You can charge. What you cannot do while charging is use CIG's images,
    artwork, trademarks or logos - unless you sign a separate licence.

**So a subscription Historian that renders no CIG art and no CIG logos, and
whose answers are built from facts and numbers rather than CIG's prose, is not
addressed by this clause at all.** That is a real product shape, and it is close
to what `claude/ai-historian-design.md` already describes.

**The three things that would put it back inside the restriction:** shipping CIG
artwork, using RSI marks or logos in the branding, or reproducing CIG's written
descriptions.

---

## 6. NOT VERIFIED — read this before anyone acts on the above

- **C2 is not a lawyer and this is not legal advice.** It is a careful reading of
  a quoted document. **Rule 8 puts Fan Kit, trademark and legal text solely with
  Sleven.**
- **The quotes above are from the current live ToS as of 2026-08-06.** They have
  not been checked against any earlier version, and CIG revises these terms.
  **Anything built on this should re-check the source at the time it ships.**
- **"Facts and numbers are not copyrightable" is the assumption underneath the
  whole data side of both projects and it has never been examined.** It is
  broadly right in US law for raw data, and the boundary around a *selection and
  arrangement* of data is genuinely contested. **Nobody has looked at it.**
- **Whether §XIII.D applies at all is discretionary** — "we may (in our sole
  discretion) grant you". **The grant is permissive, not automatic.**
- **The separate-licence path in §2.3 has never been enquired about.** Sleven
  parked the RSI legal enquiry deliberately. **This finding does not unpark it;
  it just records that the path is named in the terms.**
