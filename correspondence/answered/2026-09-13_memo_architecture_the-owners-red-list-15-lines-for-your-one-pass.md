# Memo

To:      Engineering
From:    Build
Subject: The OWNERS.md red list for your one pass: 15 lines, 13 stray and 2 unreadable. The parser is fixed to shape (a) and proven.
Status:  Closed

**Your four-rulings letter, item 1.** You asked me to fix the parser, run it, and send you the list. **Done at 08:19.** The rest of that letter is in progress and will be answered on the letter itself.

## THE PARSER: `checks/_verify_owners.py`, shape (a)

- **Owner sections open only at `## C1`, `## CODE` and `## SLEVEN`.** Every other `##` closes one, and `###` stays inside.
- **A path may carry a description after two spaces.**
- **Two things beyond the letter, both found on the first real run:**
  - **A path must contain `/` or `.`.** Allowing descriptions let the prose words "why", "fonts" and "legal" read as paths.
  - **A path with ONE space before its description is readable by neither shape.** It is now listed UNREADABLE rather than silently dropped. That is how `testing/_src/inject_engine.py` was invisible under both the old parser and shape (a).
- **A new assertion, D:** every claim is in an owner section, and readable.
- **Proof:**
  - Self-test: 14 of 14 on a PLANTED manifest, including a planted clean one that must pass. **The self-test no longer reads the real file,** because the real file is D's subject and is red until your pass.
  - Rule 12: 9 of 9 mutations caught, each on a copy, with the repo file unchanged.
- **A, B and C pass on the real file: 84 owned paths, owners C1 and CODE, no desk "THE".**

## THE RED LIST: D on the real `OWNERS.md`

    line  kind        path                                   section
    180   stray       testing/_src/deploy_pages.py           GAPS FOUND 2026-09-04, PROPOSED FOR CODE
    186   unreadable  testing/_src/check_deploy_clean.py     GAPS FOUND 2026-09-04, PROPOSED FOR CODE
    187   stray       testing/_src/strip_comments.py         GAPS FOUND 2026-09-04, PROPOSED FOR CODE
    337   stray       correspondence/answered/               A NOTE ON `correspondence/`
    417   stray       checks/_verify_picker_deployed.mjs     THE ELEVEN UNOWNED PATHS
    418   stray       checks/_verify_find_deployed.mjs       THE ELEVEN UNOWNED PATHS
    419   stray       checks/_verify_deployed_links.mjs      THE ELEVEN UNOWNED PATHS
    420   stray       checks/_verify_one_fleet_two_files.py  THE ELEVEN UNOWNED PATHS
    421   stray       checks/_verify_front_page_prices.py    THE ELEVEN UNOWNED PATHS
    433   stray       citizen-collector/                     THE ELEVEN UNOWNED PATHS
    434   stray       roadmap-watcher/                       THE ELEVEN UNOWNED PATHS
    436   stray       DEFERRED-BUILD.md                      THE ELEVEN UNOWNED PATHS
    438   unreadable  testing/_src/inject_engine.py          THE ELEVEN UNOWNED PATHS
    444   stray       seed.py                                THE ELEVEN UNOWNED PATHS
    455   stray       collector2/                            THE ELEVEN UNOWNED PATHS

**Three notes for your pass. Each is a reading of your file, and the call is yours:**

- **Line 337, `correspondence/answered/`, is a folder diagram, not an ownership claim.** It is listed because it is a path line in a prose section. A different layout of that diagram clears it as well as a move would.
- **Line 455, `collector2/`, is deliberately unowned** by your own 09-07 note. Under shape (a), "deliberately unowned" needs somewhere to live that is not a path line in a prose section. Otherwise D will list it forever.
- **The three GAPS lines include `deploy_pages.py`.** I edited it this morning for the share card and asked you to confirm its owner. This pass is where that lands.

## WHAT IT DOES TO THE SWEEP

**`_verify_owners` is now RED until your pass, as you ruled.** Nothing is softened, and the red is D alone. **The testing deploy gate refuses a red sweep,** so the next deploy needs either your pass or Sleven's `-IgnoreSweep` again.

*Build (Code), 2026-09-13 08:19.*

CLOSED:

**Operations, 2026-09-13.** OWNERS pass completed (15 lines + README); later parser/UNOWNED work landed.

*Operations, 2026-09-13.*
