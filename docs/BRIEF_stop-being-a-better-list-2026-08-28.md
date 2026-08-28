# BRIEF — every Star Citizen tool is a list. The data on this machine answers QUESTIONS, and that is the whole opportunity. Here is what we can build that nothing else can, what we should stop competing on, and the order I would do it in.

    from      C1 (Cowork), 2026-08-27 evening
    for       Sleven
    question  "what can we do with this info and how do we use it to build
              the best SC tool on the internet"
    basis     measured today, on this machine, not researched or assumed

---

## 0. THE ONE-LINE VERSION

**Stop trying to be a better list. Be the only tool that answers a question.**

Every reference site shows a weapon's DPS. **None of them can tell you where that
weapon sits on your hull, what it will actually do to the ship in front of you,
or whether you should build it instead of buying it.** All three are answerable
from data already on this machine, and two of them come from files nobody else
opens.

---

## 1. WHY WE CAN DO THIS AND A SCUNPACKED-ONLY TOOL CANNOT

Everyone building an SC tool reads the same JSON export. **Today this project
went a layer deeper and read `Data.p4k` itself** — the game archive — and
decoded CIG's own geometry:

    153 hulls decoded out of the archive
    284 ships placed against their own models
    245 classes with EVERY weapon marker on CIG's real mount coordinates

That is not a better list. That is a dataset that did not exist this morning and
does not exist anywhere else, because it required writing a decoder for CIG's
`#ivo` container rather than downloading somebody's JSON.

**That is the pattern to repeat: the moat is one layer below where everyone
else stops.**

## 2. THE FOUR QUESTIONS WE CAN ANSWER AND NOBODY ELSE CAN

### 2a. "Where is this gun on my ship?" — BUILT, live on testing

245 ships, markers on CIG's own transforms, joined by CIG's own `HardpointName`.
The median existing guess was **half a hull-length** from the real mount. This is
already the strongest thing on the site and it is ours alone.

### 2b. "What will this weapon do to THAT ship?" — one open question away

The chain is entirely in CIG's data: weapon damage by channel → shield
absorption → armour multiplier → hull. **Every shield in the game is identical**
and no fan tool says so. Energy is stopped completely; ballistics get at least
half through.

**Blocked on one measurement** — whether a shield's `Absorption` and
`Resistance` stack. That is a client question, not a data one, and it is the
single highest-value unknown in the project.

### 2c. "Should I build this or buy it?" — 1,607 recipes, untouched

    1,607 crafting recipes, every one with a craft time, a requirement tree
          and a dismantle yield
    1,599 of them must be EARNED - only 8 are available by default
      732 tied to a named reward pool, so "where do I get this blueprint"
          is answerable
       96 make ship weapons · 75 power plants · 74 coolers · 62 shields
          · 60 radars · 57 quantum drives

Joined to items by **UUID**. No name matching anywhere.

### 2d. "What should I go mine?" — nobody has this and it is one query

Counting how many recipes demand each material:

    Aslarite         856 recipes        Iron             258
    Ouratite         495                Agricium         194
    Laranite         353                Taranite         145
    Tungsten         266                Stileron         141

**That is a demand ranking for the entire crafting economy, derived from CIG's
own recipes.** A miner deciding what to fill a hold with has nothing that tells
them this. It is one pass over a file we already have.

Pair it with the **30 raw-to-refined pairs CIG states outright** — `Agricium
(Ore) -> Agricium` — and the chain reads: *this rock becomes this metal, which
856 recipes need.*

---

## 3. WHAT WE SHOULD STOP COMPETING ON, AND WHY THAT IS A STRENGTH

**Prices.** Measured today: CIG's entire export contains **no prices at all** —
the only cost-like fields in every file are `AmmoCost` and `CostPerBullet`.
There is nothing to be authoritative from.

Price sites win on **crowdsourcing networks**, which take years and a community.
We have 26,657 price rows from UEX and **zero of them verified**, and no way to
verify them, because the game files do not contain the answer.

**So do not be a price site.** Show the prices, label them as community-reported
and dated, and put the effort where the game files ARE the truth. **"We only
state what the game states"** is a stronger position than a worse copy of
somebody else's price feed — and it is a position no crowdsourced tool can take.

---

## 4. THE ORDER I WOULD BUILD IN, AND WHY THIS ORDER

**FIRST — the mining demand table and the refine chain.** One pass over files we
hold, no join risk, no open questions, and it answers a question every mining
player asks before every run. **Cheapest real feature left in the data.**

**SECOND — craft or buy.** The recipes carry time, ingredients and dismantle
yield. Even without trustworthy prices it answers *"can I even make this, what
does it need, and how long"* — which nothing else does.

**THIRD — settle the shield stacking question**, then build effective damage.
It is the most valuable feature in the project and the only thing between us and
it is one measurement. **Do not build it before that measurement.**

**FOURTH — the hardpoint viewer's remaining 20 ships**, and only where the data
allows. Most of the 20 cannot be reached and that is written down.

**NOT YET — contracts and factions.** 5,120 contract files and 74 factions,
completely unread. Real material, but a separate product surface and the three
above are worth more per hour.

---

## 5. THE RISK, STATED PLAINLY

**The failure mode is building four half-features instead of one finished one.**
The site already carries a shop layer nobody has verified and a 3D viewer that
took weeks. Every item in §4 is a real feature with real depth, and doing all of
them badly would be worse than doing the first two properly.

**And nothing here changes the standing rule:** the site does not go live until
Sleven says so, and the prices question in §3 is a labelling decision he owns,
not an engineering task anyone can close.

---

## 6. QUESTIONS

1. **Do we build the mining demand table and refine chain next** (§4 FIRST), or
   is there something you want ahead of it?
2. **On prices** (§3) — publish them labelled as community-reported and dated,
   or leave them off the public site entirely?
3. **The shield stacking question** (§2b) — do you want to settle it in-game, or
   should C3 keep digging at the data first?

---

*C1, 2026-08-27. Everything above is a measurement taken on this machine today,
not a claim about what other tools do.*
