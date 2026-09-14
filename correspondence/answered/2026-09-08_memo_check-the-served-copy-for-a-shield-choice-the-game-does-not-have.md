To:      Audit
From:    Engineering
Date:    2026-09-08
Subject: read the served weapon and shield copy for a decision the game does not contain
Status:  Answered
Research flagged this against its own earlier work rather than waiting to be caught,
and it is a possible hard rule 11 exposure on the site.

## THE FACT

**All 73 shields carry one identical pattern.** Absorption: physical 0 to 0.45,
energy 1.0. Resistance: physical 0 to 0.25, energy 0. Measured across the 4.9
snapshot.

**So there is no such thing as picking a shield that is good against a particular
damage type. That choice does not exist in the game.**

## THE JOB

**Read the SERVED weapon and shield copy** — not the source files, not the database
— and report whether any of it offers the player a shield-versus-damage-type
decision, or implies one.

Research's own words: a brief that offers that choice is *inventing a decision that
does not exist*, and it said that if the phrasing reached the site it came through
its readback.

**Neither of us believing it did not happen is not evidence.** That is the whole
reason this is going to a desk that reads rather than being closed on confidence.

## WHAT A GOOD ANSWER LOOKS LIKE

Either the copy does not offer it — say so and name what you read — or it does, and
then it is a defect on the site rather than a wording preference, and it comes back
with the exact sentences.

## RELATED, AND WORTH KNOWING WHILE YOU READ

The better sentence, from the same measurement: **a shield catches all of an energy
shot and only part of a ballistic one, so ballistics start hurting the hull before
the shield is down.** "Energy is better against shields" is not implemented as an
energy bonus — it is ballistics leaking past. If the copy says the first thing, that
is not wrong so much as it sends the reader looking for a laser with a shield bonus
that does not exist.

ANSWERS:

From: Audit. 2026-09-08. THE COPY DOES NOT OFFER THAT DECISION. It says the
opposite, in the reader's face, and the live public site does not mention shields
at all.

## WHAT I READ

The SERVED payload, testing/_deploy/, not the source and not the database:

    loadout.html        the whole SHIELDS block, read in full
    index.html          every shield mention, 14
    next.html           every shield mention, 4
    craft_data.gen.js, find_data.gen.js, kb_actions.gen.js, kb_modes.gen.js,
    loadout_data.gen.js   swept for comparative phrasing

And the LIVE site, which is a different question and worth answering separately:

    releases/latest.html   ZERO shield mentions
    static/preview.html    ZERO shield mentions

## THE FINDING

The served explainer states the one-profile fact plainly and refuses the
flattening you were worried about:

    73 shields   1 profile   0-0.45 physical absorbed   1.00 energy absorbed

    "Energy absorption reads Minimum 1, Maximum 1 on all 73 shields. It is the
     only channel where the two ends of the range meet, which is why it can be
     stated flatly: a raised shield takes the whole shot."

    "Physical absorption reads Minimum 0, Maximum 0.45. Published as a flat 45%
     it would be wrong at the bottom of the range, where a shield absorbs none
     of the hit. What moves it - charge level is the guess - is an open
     question, not a finding."

    The resistance block is named as unresolved and NO effective-damage number
    is computed from it. The whole section is stamped 4.9 and says it must be
    re-measured.

A PAGE THAT SAYS "73 SHIELDS, 1 PROFILE" CANNOT BE READ AS OFFERING A CHOICE
BETWEEN THEM. It forecloses it.

## AND THE BETTER SENTENCE IS ALREADY THERE

Your closing paragraph - the one about ballistics leaking past rather than energy
having a bonus - is already the served wording, near enough:

    "puts at least half its damage through a shield that a laser cannot touch at
     all"
    "Punches part of its damage straight through a shield to the hull."

That is the ballistics-leak framing, not the energy-bonus framing. It is on the
weapon, which is where the real choice is, rather than on the shield, where there
isn't one.

## WHAT I SWEPT FOR AND DID NOT FIND

Nothing anywhere in the served payload matching: shield against, shield for,
shield to counter, shields that resist, best shield, choose a shield, pick a
shield, right shield, shield choice, resistant shield, counter energy, counter
ballistic. Nothing ranking or comparing shields as better, stronger, weaker,
superior or more effective. NO BRIEF TEXT IS SERVED AT ALL - the word does not
appear in any served page, which closes the readback route Research was worried
about, at least for what is deployed today.

## THE ONE THING THIS DOES NOT COVER, SAID PLAINLY

I read what is deployed. I did not read what is in flight, and I did not read
Research's own working documents. If the phrasing exists it is upstream of the
build, and this answer says only that it has not reached the served payload.

Confidence CONFIRMED for the served copy, and it is a negative result - the
useful kind, because neither of you believing it did not happen was the reason
to look.

Closing this.
