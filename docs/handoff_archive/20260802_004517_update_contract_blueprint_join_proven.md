# FINDING — "where do I get this blueprint" is answerable from our own data

**From C2. 2026-08-02. Read-only. Nothing written to the repository.**

Tested in response to the question of whether to pull data from a community
crafting tool. **We do not need to.** The join works.

---

## THE TEST

`contracts/*.json` — 5,108 files in
`scunpacked-data/snapshots/20260801T204744Z/` — carry a `Blueprints` array that
nobody in this project had opened.

Structure, verbatim from `004f6931-271f-4774-8db1-ce7b86de6837.json`:

    "Blueprints": [
      {
        "Chance": 1,
        "PoolUUID": "9cf3799c-2347-46a6-bd65-203f8a426f79",
        "PoolContents": [
          { "ItemName": "Devastator \"Vastator\" Shotgun",
            "ItemUUID": "e5b42569-10da-40a5-a16f-497f5b84cf3c",
            "BlueprintUUID": "f2947ab8-56b3-43e6-9ef6-6301070a1846" },
          ...
        ]
      }
    ]

**This is a direct structured join, contract → blueprint, with a drop chance.**

## RESULTS — full scan of all 5,108 contract files

    contracts that award blueprints                     768
    distinct blueprints reachable via contracts         676
    blueprints carrying a RewardPools field             724
      ...of those, reachable from a real contract       676
      ...dangling (pool exists, no contract found)       48
    the "no default, no pool" group                     865
      ...reachable via contracts anyway                   0

`Chance` is 1 on almost every pool; a small number are 0.25.

**The 865 are confirmed sourceless.** Not an oversight in my earlier read — no
contract in the game files awards them. Saying "we don't know how you get this"
is now a verified statement rather than a hedge.

## WHAT EACH CONTRACT ALSO CARRIES

From the same files, no extra work: `DisplayTitle`, `MissionGiver`,
`MissionType`, `Faction`, `CalculatedReward`, `TimeToComplete`,
`ReputationGained`, `ReputationPrerequisite`, `Illegal`, `Shareable`,
`OnceOnly`, `Cooldown`, `Difficulty`, `AvailabilityLocations`,
`RequiredLocations`, `LocationPools` with resolved location names, and the full
mission text.

Mission givers seen in the scan: Headhunters, Shubin Interstellar, United
Wayfarers Club, Citizens for Prosperity, Foxwell Enforcement, Adagio Holdings,
Eckhart Security, Bit Zeros.

**That is the same dataset the community blueprint finder presents**, derived
independently from the game files we already hold, gated and sealed.

---

## WHY THIS SETTLES THE "PULL FROM A TOOL" QUESTION

**1. The thing we would take, we already have.** Recipes, quantities, quality
curves, and now sources. All four competing tools are built on the same
extracted game files.

**2. The thing we lack, they lack too.** Our blocker is commodity prices. Not one
of the four shows a price. Scraping them moves us zero distance on the only axis
where we are actually stuck.

**3. The only thing genuinely worth taking is the only thing it would be wrong to
take** — CmdrQuattro's grind-route planning. That is his original work: ordering
contracts, respecting reputation gates, inserting rep contracts to unlock tiers.
It is not in any game file. It is the reason his tool exists.

**4. Credit is not a licence.** Attribution answers a courtesy question, not a
permission question. It matters more here than usual for three reasons:

- The Historian is the **monetised** part of the plan. Using another fan's
  research inside a subscription product is a materially different act from
  citing it on a free reference page.
- CIG's 2026-07-28 confirmation reviewed a ship price table. It is a snapshot,
  not a licence, and it does not cover redistributing another fan site's data.
- **This project has already refused two sources on exactly these grounds.**
  Source 4 is self-blocked `blocked_missing_provenance`; source 5 is
  `not_directly_downloadable`. Both were correct calls. Taking a fifth source
  with weaker provenance than either would contradict a decision already on
  record.

**5. Provenance would break the pipeline's own rules.** Scraped tool output has
no manifest, no hash, no patch stamp, and no upstream we can re-verify against.
Every row on this site carries `last_verified_patch`. A scraped row could not.

---

## WHAT TO DO INSTEAD — in order

1. **Build the contract → blueprint index from the files we already have.**
   Proven above. Gives source, faction, payout, reputation gate, drop chance and
   location, with full provenance.
2. **Pull UEX commodity prices.** Still the one real blocker, still the one thing
   no competitor has. Legitimate route, token already active.
3. **Link out to CmdrQuattro for grind routing**, and say why. A reference site
   that points at the better tool for one specific job is more trustworthy, not
   less — and it is what the "one page per thing" rule implies when someone else
   owns that thing.
4. **Consider approaching them.** We will hold something all four lack: prices.
   A data exchange, or a mutual link, is a real proposition and costs nothing to
   ask. **This is a decision for Sleven, not a technical call.**

---

## UNCERTAIN, FLAGGED

- The 48 dangling pools — a pool referenced by a blueprint with no contract
  awarding it. Could be unimplemented content, could be a gap in the extraction.
  Not investigated.
- `Chance: 0.25` appeared on only 2 pools in the first third of the scan. I did
  not tabulate chance across the full set.
- Whether contract availability is patch-current. These are game files from
  2026-08-01; the game is on 4.9. Contract structures change between patches.
- I did not check any of the four tools' terms of use. If Sleven wants to pursue
  option 4, that should be read first — by a person, not by me.
