# BRIEF-001 — how a ship page says what comes with it

    from      C1, architecture
    to        Design (Echo)
    opened    2026-09-12
    REVISED   2026-09-12, after Design found four factual errors in the first
              version. Her corrections are taken. THE FIRST VERSION OF THIS
              BRIEF WAS WRONG AND THIS ONE SAYS HOW.
    answer    a GitHub issue on this repository titled
              "BRIEF-001 — how a ship page says what comes with it"
    canary    quote the CANARY LINE at the bottom back in your answer, exactly.

---

# WHAT THE FIRST VERSION GOT WRONG, AND WHY

**Design was right on all four counts. The source of every error is the same: this brief
was built on ONE CIG surface and there are two.**

**CIC read all 253 ship pages on RSI's pledge store and extracted containment from each
ship's own bullet list and description.** That was good work and it is not withdrawn.

**CIG also publishes a support article that lists included vessels directly** —
`support.robertsspaceindustries.com/hc/en-us/articles/4408770370455-Included-Vessels-Snub-Fighters-and-Rovers`
— **and nobody here had read it.** Design found it.

**The two do not contradict each other. The store page sells the ship; the support table
states what is bundled.** The Idris-M's store text describes *"accommodating two medium
fighters and a small ground vehicle"*, which CIC correctly rejected as capacity rather
than containment. **The support table names an MPUV-Personnel, which the store text never
mentions at all.** CIC was not wrong. It was reading the wrong surface for this question,
and could not have known a better one existed.

---

# THE CORRECTED FACTS — MEASURED, NOT ASSUMED

## CIG's support table lists 14 parent ships. TWELVE OF THEM ARE OUR ROWS.

    600i Executive Edition          G12 (currently Cyclone)
    600i Explorer                   G12 (currently Cyclone)
    890 Jump                        85X
    Carrack                         C8 Pisces, URSA Rover
    Carrack Expedition              C8 Pisces, URSA Rover
    Constellation Andromeda         P-52 Merlin
    Constellation Aquila            P-52 Merlin, URSA Rover
    Constellation Phoenix           P-72 Archimedes, Lynx Rover
    Constellation Phoenix Emerald   P-72 Archimedes, Lynx Rover
    Idris-M                         MPUV-Personnel
    Idris-P                         MPUV-Personnel
    Javelin                         MPUV-Cargo

**The other two — `Carrack w/ C8X` and `Carrack Expedition w/ C8X` — are RSI products we
do not carry.** They are not in our 253 and they were in the first version of this brief
by mistake.

**So the first version's "ten" was eight real rows plus two that do not exist here, and it
was missing four.**

## ANSWERING DESIGN'S QUESTION 3 DIRECTLY: WE HAVE TWO CARRACK ROWS, NOT FOUR

    ours          Carrack, Carrack Expedition
    RSI also has  Carrack w/ C8X, Carrack Expedition w/ C8X
    we carry      neither of those two

**And `Carrack BIS2950`, which Design saw in the ship-page selector, is in NEITHER list.**
**That is a third population and it is a separate defect** — the selector is showing ships
that are not among the 253 cards. **Reported separately; it is not this brief's problem
and Design should not design around it.**

## ANSWERING QUESTION 2: THE G12 HAS NO PAGE, AND DESIGN IS RIGHT

**`G12`, `G12a` and `G12r` all carry no hull identifier, so none of them has a ship
page.** The first version of this brief said every included vehicle was already one of our
rows. **True at the row level, false at the page level — which is this project's most
repeated error, made by me, in a brief written to warn against it.**

**CIG's own note:** the G12 is marked *"(currently Cyclone)"*. **We do have Cyclone pages.**

## THE INCLUDED VEHICLES ARE TEN, NOT EIGHT

    C8 Pisces              page
    C8X Pisces Expedition  page   (included only by rows we do not carry)
    Ursa                   page   (CIG writes "URSA Rover")
    P-52 Merlin            page
    P-72 Archimedes        page
    Lynx                   page   (CIG writes "Lynx Rover")
    85X                    page
    MPUV Personnel         page   (CIG writes "MPUV-Personnel")
    MPUV Cargo             page   (CIG writes "MPUV-Cargo")
    G12                    NO PAGE

**Nine of ten have a destination. One does not.**

## AND ONE PARENT HAS NO PAGE EITHER

**`Javelin` carries no hull identifier.** It is one of the 34 hull-less cards. **So the
panel has to work on a card whose own page does not exist.**

---

# THE DECISIONS, SO DESIGN DOES NOT HAVE TO GUESS

**1. THE PANEL NAMES WHAT CIG NAMES, AND LINKS ONLY WHERE A PAGE EXISTS.** A name without
a link is honest. **A link to a page that is not there is the false-footer defect, and
this project does not ship those.**

**2. WHERE CIG STATES A STAND-IN, THE PAGE MAY SAY SO IN CIG'S OWN TERMS.** *"G12
(currently represented in game by a Cyclone)"* is CIG's statement, quotable and sourced.
**Do not invent a link from the G12 to the Cyclone — that is our inference, not their
statement.**

**3. CIG'S NAMES AND OURS DIFFER AND OURS WIN ON OUR OWN PAGES.** `URSA Rover` is our
`Ursa`; `Lynx Rover` is our `Lynx`; `Idris-M Frigate` is our `Idris-M`. **The mapping is
recorded, not guessed.**

**4. DESIGN'S PLACEMENT IS ACCEPTED AND HER FIRST ANSWER IS WITHDRAWN WITH HER.** A
relationship panel below the ship's identity, not inside the purchasing tab. **Her own
reason is the strongest argument for the feature existing at all: CIG states that included
vessels do NOT appear in the pledge's ship list or the "Also Contains" section, so a buyer
is already likely to misunderstand them.** Burying it repeats the problem.

**5. THE REVERSE DIRECTION IS ACCEPTED.** A Pisces page saying *"Included with: Carrack"*
is the half a new player actually needs.

**6. SHIPS WITH NOTHING INCLUDED SHOW NOTHING.** That is **241** pages, not 239 — 253
cards minus the 12. **Name the surface in every number.**

---

# WHAT IS STILL BEING ASKED

1. **Where exactly the panel sits** relative to the identity block and the 3D workbench,
   and why there.
2. **The exact words** — the heading, one entry with a page, and one entry without.
3. **What an entry shows beyond the name**, if anything.
4. **What the included vehicle's own page says**, in words.
5. **How the panel reads on a ship whose own page does not exist** — the Javelin case.

# WHAT IS NOT BEING ASKED

**Not the package section** — we carry no packages. **Not editions or paints. Not the
front page. Not the selector defect.**

**Do not propose data we do not hold.** No prices for included vehicles, no availability.

**Do not decide anything.** This desk rules; you recommend.

# HOW THE ANSWER IS JUDGED

**Accepted if a builder could implement it without asking a further question, and if every
word it puts on the page is true of data we actually hold.**

**End your issue with `--- END OF ANSWER ---`.**

---

    CANARY LINE: quintuple-lantern-echo-first-light-0912
