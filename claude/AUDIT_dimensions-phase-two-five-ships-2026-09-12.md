# AUDIT - dimensions, phase two: the five ships with no figure from any local source

**Build (Code), 2026-09-12, 01:20 to 01:24 CDT.** Architecture ordered this in `2026-09-12_memo_build_phase-two-is-five-ships-and-two-bigger-jobs-go-first`, and its later STOP memo corrected the order.

**Source order, as ordered:** RSI first, then CIG publications, then game-file data, then maintained community datasets, and wikis last.

- **No conflict has been resolved by picking a number.**
- **Nothing in the repository was changed.** Fetched material sits in the session scratchpad, not in the repo, and its hashes are below.
- **Per-source rows:** `claude/AUDIT-2026-09-12-phase-two-dimensions.csv`

**RAPTOR is not on this list.** Architecture took it off, and it now stays as a joke card under Owner's 2026-09-07 ruling, which asks for no model and no dimensions.

## THE FIVE, IN ONE TABLE

    ship               RSI ship matrix        game data (snapshot)     Fleetyards            wiki (last)
    Odin               752 x 222 x 213        -- no ClassName          752 x 222 x 213       not read
    Genesis Starliner  85 x 80 x 25 "Genesis" -- none found            85 x 80 x 25 "Genesis" not read
    MOTH               0 x 0 x 0              0 x 0 x 0 (ARGO_MOTH)    45 x 25 x 15          not read
    CSV-FM             NOT PRESENT            NOT PRESENT              NOT PRESENT           5.44 x 4.13 x 2.81
    Starlancer BLD     NOT PRESENT            NOT PRESENT              NOT PRESENT           83 x 52 x 16

All figures are in metres and in each source's own order: length, beam or width, height.

**No source states a game patch for any of these figures.** The game data carries a snapshot id (20260827T225641Z), not a patch.

## SHIP BY SHIP

**Odin: SETTLED BY RSI, AND FLEETYARDS AGREES.**

- RSI's ship matrix has record id 317, name "Odin", length 752, beam 222, height 213, `in-concept`.
- The figure Architecture asked me to trace was never lost. It sits in `data-layer/derived/model-availability/scale_fix_report.json`: Fleetyards `anvl-odin`, 752.0 x 222.0 x 213.0, the target the model was scaled to on 2026-08-27. **`index.json` simply predates it.**
- **Two sources, the same figure.**
- **One caveat:** the Odin model was scaled to this very figure. So the model's box agreeing with it proves nothing (rule 16).

**Genesis Starliner: A FIGURE EXISTS, AND THE NAME JOIN DOES NOT.**

- RSI has id 91, name "Genesis", 85 x 80 x 25, `in-concept`, URL `/pledge/ships/starliner/Genesis`.
- Fleetyards has `crus-genesis`, name "Genesis", 85.0 x 80.0 x 25.0, updated 2026-08-22.
- **Both sources agree on the figure.**
- **Neither source uses our name.** Tying RSI's "Genesis" to our card "Genesis Starliner" is a name mapping, and Architecture has ordered the 28-name mapping from Research. **I have not applied it (rule 17).**

**MOTH: THE PRIMARY SOURCE IS ZERO, AND ONLY THE COMMUNITY HAS A MEASUREMENT.**

- RSI has id 311, "MOTH", length 0, beam 0, height 0, `flight-ready`.
- The game data has ARGO_MOTH at 0 x 0 x 0.
- Fleetyards has `argo-moth` at 45.0 x 25.0 x 15.0, updated 2026-09-09. The same figure appears in the 2026-08-27 local record.
- **Under Architecture's ruling a zero is absent, not a measurement.** So this is not a conflict between two numbers: it is one community figure and two blanks.
- **It is recorded as that, and not promoted to an RSI figure.**
- **Javelin has the same shape,** and it is not on this list: RSI and the game data both say 0 x 0 x 0, and Fleetyards (index.json) says 475 x 210 x 85.

**CSV-FM: ONLY A WIKI HAS A FIGURE, AND THE WIKI CITES NO SOURCE FOR IT.**

- RSI's ship matrix holds no CSV-FM. Its only CSV record is CSV-SM, id 281.
- The game data holds only ARGO_CSV_Cargo, named "Argo CSV-SM".
- A Fleetyards search for "CSV" returns only CSV-SM.
- starcitizen.tools, page "CSV-FM" (revision 373156, last edited 2026-07-14), gives length 5.44, width 4.13, height 2.81, and productionstate "In concept".
- **Its two references both cite CitizenCon 2954 for what the acronym means. Neither is cited for the dimensions.**
- **Observed, not concluded:** those three numbers match Fleetyards' CSV-SM (5.4 x 4.1 x 2.8) to one decimal place.

**Starlancer BLD: ONLY A WIKI HAS A FIGURE, AND IT IS THE STARLANCER MAX's.**

- RSI's ship matrix has MAX and TAC, and no BLD.
- The game data has MAX, TAC and two Wikelo specials, and no BLD.
- Fleetyards has MAX and TAC.
- starcitizen.tools, page "Starlancer BLD" (revision 376961, last edited 2026-08-19), gives length 83, width 52, height 16, and productionstate "In concept".
- **I followed its RSI citation to the end.** "Blast from the Past: Starlancer" (comm-link 12708, dated 1 October 2012) contains **no BLD mention and no dimensions.** The other reference is a CitizenCon video, which I could not read.
- **Observed, not concluded:** 83 x 52 x 16 is exactly RSI's figure for the Starlancer MAX.

## WHAT THIS MEANS FOR THE CARDS, AND IT IS NOT A DECISION

- **Odin has an RSI figure,** and it can carry it with its source.
- **Genesis Starliner has an RSI figure,** waiting on one name mapping.
- **MOTH has a community figure and two primary zeros.** Showing 45 m means showing a Fleetyards number, labelled as one. Architecture's ruling says every dimension carries its source.
- **CSV-FM and Starlancer BLD have wiki figures with no cited source,** and each matches a sibling ship. **Both are "in concept". The honest state today may be "not published".**

**Whether any of these reaches a card is Architecture's and Owner's call, under the source-label ruling.** This report records the figures and does not choose between them.

## PROVENANCE

    RSI ship matrix   https://robertsspaceindustries.com/ship-matrix/index
                      read 2026-09-12 01:20:33 CDT, HTTP 200, 5,011,257 bytes,
                      253 records, sha256 6556facb9eedfbfd...
    Fleetyards API    https://api.fleetyards.net/v1/models?q[nameCont]=<term>
                      terms Starlancer, CSV, Genesis, MOTH; read 01:21:13 CDT
                      sha256 8dad8499... 386dd408... 62fcd41b... 1159c95f...
    Fleetyards local  data-layer/derived/model-availability/scale_fix_report.json (2026-08-27)
    game data         data-layer/external-sources/scunpacked-data/snapshots/20260827T225641Z/ships.json
    wiki              https://starcitizen.tools/api.php (parse and revisions), read 01:21:54-01:22:11 CDT
    CIG comm-link     https://robertsspaceindustries.com/comm-link/spectrum-dispatch/12708-Blast-From-The-Past-Starlancer

**Rule 22 was kept:** nothing under `/media/` was fetched.

**Not done:** RSI's product pages for Odin, MOTH and Genesis returned only a title when fetched signed out. Architecture found the same. **The ship matrix is RSI's own data and is the RSI source used here.**

*Build (Code), 2026-09-12.*
