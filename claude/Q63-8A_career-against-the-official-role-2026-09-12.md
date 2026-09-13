# Q63.8A - career against RSI's official role: lists 1 and 2 have run, and the join is 225 of 253, not 253

**Build (Code), 2026-09-12.** Architecture ordered this in `2026-09-12_memo_build_the-roles-file-is-on-disk-run-the-career-join-now`.

**The job was read-only.** It wrote the per-row table `claude/Q63-8A-2026-09-12-career-vs-official-role.csv` (253 rows). The script is `_needs_review/q63_8a_career_join.py`.

    POPULATION   the 253 front-page cards (next.src.html const DATA)
                 against the 253 rows of claude/CIC_rsi-official-ship-roles-2026-09-12.md
    JOIN         card name == roles name, byte-exact. No case-folding, no trimming,
                 no grouping (rule 17, and the order's own words)
    AGREE        career is byte-identical to the role's FIRST segment (the category).
                 Stated so it can be argued with. A second measure, "career equals
                 ANY segment", is reported beside it in the CSV and not used for
                 the lists.

## FIRST: THE TWO 253s ARE NOT THE SAME 253

**Only 225 cards join.** 28 cards have no roles row of the same name, and 28 roles rows have no card of the same name.

**The roles file says "253 of 253, reconciled by name against the 253-row Pass 1 list".** That list is Research's list of RSI store names, not our card names. **The two counts are equal, and the populations are not.** This is the pattern Architecture named this morning: the same count taken on two surfaces.

    cards with no roles row      600i Executive Edition, A2 Hercules Starlifter, ATLS GEO IKTI,
                                 ATLS IKTI, ATLS IKTI RAD, Aurora CL, Aurora ES, Aurora LN,
                                 Aurora LX, Aurora MR, Aurora SE, Ballista Dunestalker,
                                 Ballista Snowblind, C2 Hercules Starlifter, C8R Pisces Rescue,
                                 CSV-FM, Dragonfly, F7C-M Hornet Heartseeker Mk II,
                                 Genesis Starliner, Gladius Dunlevy, Gladius Pirate, Khartu-al,
                                 M2 Hercules Starlifter, Mercury Star Runner, Nova Tank, RAPTOR,
                                 San'tok.yai, Starlancer BLD

    roles rows with no card      A2 Hercules, Anvil Ballista Dunestalker, Anvil Ballista
                                 Snowblind, Argo Mole Carbon Edition, Argo Mole Talus Edition,
                                 Aurora Mk I CL/ES/LN/LX/MR/SE, C2 Hercules, C8R Pisces,
                                 Carrack Expedition w/C8X, Carrack w/C8X, Dragonfly Black,
                                 Dragonfly Yellowjacket, Genesis, Gladius Pirate Edition,
                                 Khartu-Al, M2 Hercules, Mercury, Nautilus Solstice Edition,
                                 Nova, Nox Kue, S-65 Stingray, San'tok.yāi,
                                 Valkyrie Liberator Edition

**Not paired, and deliberately so.** Many of these look like the same ship under two spellings: `Aurora CL` beside `Aurora Mk I CL`, `Khartu-al` beside `Khartu-Al`, and our card `San'tok.yai` beside RSI's `San'tok.yāi`. **That is INFERRED and not applied.** Pairing them by eye is exactly the loose match rule 17 forbids.

**The two lists also hold rows that are not renames.** On RSI's side: the Carrack w/C8X packs, two Mole editions, Nautilus Solstice, S-65 Stingray, Nox Kue and Valkyrie Liberator Edition, which is our folded row. On ours: RAPTOR, CSV-FM and Starlancer BLD.

**Joining the 28 needs an explicit name mapping, written down and owned by someone.** That is a decision, and it is not this desk's to make.

## THE THREE LISTS, ON THE 225 THAT JOIN

    LIST 1   career and official role DISAGREE          3
    LIST 2   career empty, official role exists         30
    LIST 3   career AGREES (equals the first segment)   192

**LIST 1, all three:**

    Paladin          career "Gunship"        official "Combat / Gunship"
    Pitbull          career "Snub Fighter"   official "Combat / Snub Fighter"
    Starlancer MAX   career "Transporter"    official "Transport / Medium Freight"

- **For two of the three, career is RSI's SECOND segment, not a contradiction of it.**
- **The third differs only as a string:** `Transporter` against `Transport`. **I have not folded it.** RSI itself uses both strings, 35 and 6 times.

**LIST 2: 30 cards.** These are the 34 careerless cards less the four that do not join (CSV-FM, Genesis Starliner, RAPTOR, Starlancer BLD):

> Arrastra, Crucible, E1 Spirit, Endeavor, Expanse, F7C-M Super Hornet Heartseeker Mk I, G12, G12a, G12r, Galaxy, Hull D, Hull E, Javelin, Kraken, Kraken Privateer, Legionnaire, Liberator, MOTH, Merchantman, Mustang Alpha Vindicator, Nautilus, Odin, Odyssey, Orion, Pioneer, Ranger CV, Ranger RC, Ranger TR, Vulcan, Zeus Mk II MR

**Every one of the 30 has an official role.** That means T-003's missing-category cards could carry RSI's category without the ClassName join they fail.

## THE NUMBERS THAT WOULD DECIDE WHETHER `career` STAYS - reported, not acted on

- **The official role covers all 225 joined cards: 0 blank.** `career` covers 195 of them.
- **Where career exists, it is RSI's first segment on 192 of 195 cards.** It equals some segment of RSI's role on 194 of 195.
- **Career never carries anything RSI's role does not.** The nearest case is one string variant, Starlancer MAX.

**So on this population, career is a partial copy of RSI's category.** It says less than RSI's role and says it on fewer ships. **Whether that means deleting it is Architecture's call and Sleven's, not this desk's.**

**What these numbers cannot say:** anything about the 28 cards that do not join, or the 318-ClassName dataset behind the ship page.

*Build (Code), 2026-09-12.*
