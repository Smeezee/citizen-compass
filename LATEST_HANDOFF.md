# LATEST_HANDOFF.md — Update #867 — 2026-08-30 3:13 AM

---

# CITIZEN COMPASS — LATEST HANDOFF

Copy/paste this whole file into a new AI conversation for instant context. It's regenerated automatically — always the most current snapshot available.

---

## CURRENT STATE (auto)

**Generated:** 2026-08-30 03:13:31 (auto-regenerated every time a file lands in inbox/ or this script runs — don't hand-edit this section)

**Project health score:** 35/100
- Data completeness: 0%
- Viewer progress: 50%
- Documentation: 100%

**Ships:** 2 complete viewers / 4 total (50%)
- Complete: arrow, cutlass-black
- In progress / not started: constellation-aquila, gladius

**Data layers:**
- data-layer: 119498 files (13787.21 MB)

**Scripts:** 53  |  **3D models:** 1147  |  **Docs:** 1433

---

## RECENT UPDATES (append-only, newest first)

### 2026-08-30 03:12:47 — 20260830_0335_update_committed-b9de329-and-the-4-10-header-is-ahead-of-the-data.md

# Update — pushed `b9de329`. And the live-site header now claims 4.10 while the data still says 4.9.

**2026-08-30 08:35 UTC / 2026-08-30 03:35 local · Code (background session)**

    b9de329   35 files changed, 3,075 insertions, 488 deletions
    6b1837f..b9de329      local == remote      tree clean
    no _to_delete, no node_modules, no .exe, no editability_patches

## THE ONE THING TO READ IF YOU READ NOTHING ELSE

    releases/latest.html   Live 4.10.0 "Siege of Orison"   <- C1, today
    static/preview.html    same
    loadout_data.gen.js    last_verified_patch "4.9"       <- unchanged

**The header claim is ahead of the numbers.** Q46's DONE-WHEN is
`build_loadout_data.py` pinned to `20260827T225641Z` / `last_verified_patch
4.10`, it is **BLOCKED-BY Sleven's go-ahead**, and C1 records that they have not
flipped it.

**Committing published nothing** - the live site goes out by manual Netlify
Drop from `releases/latest.html`, not from git. **But that file is the live
payload's source**, and if it were dropped as it stands the site would tell a
visitor its numbers are verified against 4.10 when every one of them was checked
against 4.9.

**I have not touched it.** It is C1's file, the version flip is Q46, and Q46 is
Sleven's call. Recording it here because a mismatch that lives quietly in a
tracked file is exactly the kind of thing that gets discovered after a drop
rather than before one.

## WHAT WENT IN

    Q45 first slice   pairstore.go + pairstore_selftest.go, //go:build master,
                      proven absent from the crew binary by symbol and string
    Q42               answered, nothing changed - 299 transactions found
    the checksum fix  the find page now publishes the hash of what it SERVES
    the sixth copy    _verify_picker_deployed.mjs, found after shipping

## STILL OPEN

**The website needs one clean sweep and a redeploy.** The last sweep measured a
moving tree - eight `_src` files changed under it - and C1 has since changed more
of them plus the two live-site files. **Nothing is wrong with the served site**;
it is the local payload that has moved ahead of the last clean measurement.

**Q45's next slice** needs a caller. Today the only thing that feeds `StorePair`
is the selftest, which is what the order asked for.

### 2026-08-30 03:10:15 — 20260830_0320_update_q45-is-master-only-and-proven-absent-from-crew.md

# Update — Q45 is master-only, and the crew binary is proven not to contain it. Symbols and strings, both directions.

**2026-08-30 08:20 UTC / 2026-08-30 03:20 local · Code (background session)**

Sleven's ruling applied: `//go:build master` on both files, `pairs/` written by
the master build only, and **absent from the crew binary rather than compiled
and disabled.**

## THE PROOF, BOTH DIRECTIONS

    go tool nm            crew   master
      StorePair              0      2
      NewPairStore           0      1
      ContextAllowed         0      2
      runPairStoreSelftest   0      2
      pairContextAllowed     0      1

    strings only this store would put in a binary
      pairs.jsonl                    0      1
      item_inspect                   0      1
      ground_prompt                  0      1
      "is not on the recorded list"  0      1

    crew   11,747,840 bytes
    master 11,788,288 bytes

**Measured in both directions on purpose.** A search that came back zero for
both builds would prove only that I was looking in the wrong place; the master
column is what makes the crew column mean something.

    crew   --selftest  exit 0
    master --selftest  exit 0

## HOW IT IS WIRED, AND WHAT IT DID NOT FORK

The call site left shared `main.go` and went behind `runVariantSelftests`,
**defined in both variant files** - the pattern `masterOnlyCommands()` and
`registerBenchFlags()` already use. Real in `variant_master.go`, empty in
`variant_crew.go` with the reason written at the site.

**Nothing was forked.** Capture, logging, the send path and the scrub layer are
untouched and remain one implementation each. The only shared file that changed
is `main.go`, by six lines, and it now names a hook rather than a feature.

## ONE THING I AM FLAGGING RATHER THAN DECIDING

`package.go`'s `packageExcluded` still carries `"pairs"`, and `package.go` is
shared - so the literal string `pairs` appears in the crew binary twice.

**It is not the pair store**, and every symbol and distinctive string of the
store is absent. But the ruling says *"must not contain it at all"*, so the
question is whether a defensive exclusion entry counts.

**My read: it should stay.** It costs nothing, it is documentation of a decision
in the place someone will look, and if a crew binary ever packaged a folder that
a master build had written, that entry is what keeps `pairs/` out of the zip.
**Removing it would make the crew build safer in appearance and less safe in
behaviour.** If that reading is wrong, say so and it comes out in one line.

## STILL PENDING

The website's find-checksum and picker fixes are built and uncommitted, waiting
on one clean sweep - the last one measured a moving tree while C1 edited eight
`_src` files mid-run.

### 2026-08-30 03:04:28 — 20260830_0300_update_q45-first-slice-built.md

# Update — Q45 first slice is built. The store records from five named contexts and refuses everything else, out loud.

**2026-08-30 08:00 UTC / 2026-08-30 03:00 local · Code (background session)**

    new   citizen-collector/pairstore.go
    new   citizen-collector/pairstore_selftest.go
    edit  citizen-collector/package.go     pairs/ excluded from the crew package
    edit  citizen-collector/main.go        6 lines, registering the selftest

## C1'S CORRECTION WAS RIGHT AND I BUILT TO IT

`scrub_policy.go` is **not wired to this**. It governs the fields of `MineStore`,
a struct built from the game log; it has no view of a pixel. **No chat-region
exclusion was built**, because none exists and inventing one here would have
been the same mistake in a new file.

**What was taken is the INVERSION.** A pair is recorded only from a named
screen context; anything else is refused and the refusal is written down:

    inventory · item_inspect · ground_prompt · hud_target · shop_kiosk

**The default is refusal.** A context nobody has thought of yet cannot leak in
by being unanticipated, which is the failure a blocklist has and an allowlist
does not.

## TWELVE ASSERTIONS, AND THE NEGATIVE CONTROLS ARE THE POINT

    [ok] pair from a named context is recorded
    [ok] the same pair twice collapses to ONE entry            1 entr(ies)
    [ok] a second VIEW attaches to the existing entry          1 entr(ies), 2 view(s)
    [ok] a different label is a different entry - the key is not the context
    [ok] an UNLISTED context is refused, not stored            stored=false
    [ok] and the store says WHICH context it refused           map[chat_window:1]
    [ok] half a pair is refused - no label, or no view
    [ok] a re-opened store reads what the first one wrote
    [ok] the index is APPEND-ONLY - earlier bytes are unchanged  1422 -> 1688 bytes
    [ok] a truncated final line survives - the log before it still reads
    [ok] every named context is on the allowlist               5 contexts
    [ok] and an unnamed one is not, with a reason

**Three of those exist only to stop a weaker implementation passing.** "A
different label is a different entry" fails anything keyed on context alone.
"The index is APPEND-ONLY, proven by bytes" is the only one a store that
rewrote its index would fail - every other assertion would still pass. And the
truncated-line case is what stops a crash mid-write from costing every pair
before it.

## THE FAILURE I SAW WAS MY OWN INVOCATION

`go run .` builds a CONSOLE binary, so `CONSOLE: this binary is a GUI build`
correctly reported subsystem 3. **Built the way the release builds it -
`-ldflags "-H windowsgui"` - the whole selftest exits 0.** The check was right
and I was holding it wrong.

## WHAT IS DELIBERATELY ABSENT

No recognition, no classifier, no matching, no OCR. No capture trigger, no
hotkey, no send path. The store is fed through `StorePair` and **today the only
caller is the selftest**, which is what the order asked for.

`pairs/` is local and now sits in `packageExcluded` beside `captures` with its
reason written down: *"your screenshots, cut up - same reason as captures"*.

## AND THE LINE THAT IS SLEVEN'S, UNTOUCHED

The consent text says *"Your chat. Chat is never sampled, at all."* Chat drawn
inside the Star Citizen window is inside a picture of that window, and Q45 makes
those pictures longer-lived. **C1 marked that as Sleven's to rule on and I have
not acted on it.** The store's allowlist means no pair is recorded from a chat
context - but that is a narrower claim than the consent line makes, and the gap
is the product promise, not the code.

## STILL PENDING ON THE WEBSITE

The find-checksum fix and the picker fix are built and uncommitted. **The sweep
that would clear them measured a moving tree** - C1 edited eight `_src` files
mid-run - so it needs one clean sweep before a redeploy. The site as served is
correct and verified; only the published checksum on the find page is stale, and
that is the thing the fix corrects.

### 2026-08-30 02:39:14 — 20260830_0245_update_deployed-then-a-sweep-measured-a-moving-tree.md

# Update — deployed and verified, then found a defect I had shipped. And the sweep after it measured a moving tree, so its nine failures are void.

**2026-08-30 07:45 UTC / 2026-08-30 02:45 local · Code (background session)**

## THE DEPLOY WENT OUT AND IS VERIFIED ON SERVED BYTES

    109 ok, 0 NOT RUN     GATE EXIT 0     20 files uploaded
    Version 8a200ac3-096e-4c6c-9a70-8bb04d40fbcf

    /                      HTTP 200    392,871 bytes
    /models/Hammerhead.glb HTTP 200  3,608,636 bytes
    PLACEHOLDER              0
    Unknown Manufacturer - 1 0
    4.99-CONTROL             0
    Torrent                  3   <- was truncated to 'MRX \'

C1's 107 corrected names, the US spelling, the countermeasure summary and the
1,450-part manufacturer fix are all live.

## THEN THE DEPLOYED-SITE CONTROL CAUGHT SOMETHING I SHIPPED

**The find page was publishing a checksum for a file it does not serve.**
`build_find_data.py` hashes the `_src` data file; **Q31's comment strip removes
1,169 bytes on the way into `_deploy`**, so the page told a visitor their
correct download was corrupt.

    the downloaded file hashes to exactly what the page claims   FAIL
    and its byte count matches too    991988 vs 993157

**That is mine, from yesterday, on the one page whose claim is that its numbers
can be trusted.** Not fixed by exempting the file from the strip - its header
names `build_find_data.py` on a public URL, which is the trace Q31 removes. **The
checksum moved instead**, because it is a promise about the bytes a person
downloads:

    find checksum: recomputed over the SERVED bytes (991988, ac431efc)

The drift control then flagged it as an undeclared transform, correctly, so it
is **declared by VERIFICATION rather than exemption**: it re-derives the hash
from what `_deploy` actually serves and requires the published figures to match.
A stale or hand-edited checksum still fails. 14 passed, 0 failed.

**And the sixth copy of the row-counting rule was where I said it would be.**
`_verify_picker_deployed.mjs`, found by the DEPLOYED control after shipping
rather than by the sweep. I wrote *"the sixth copy is the one that will be
missed"* and then missed it.

## THE SWEEP AFTER THAT IS NOT A MEASUREMENT

    101 ok, 9 failed          <- do not act on this

**C1 edited eight `_src` files during the run** - `device_engine.js`,
`download.src.html`, `kb_overlay.inc.html`, `keybinds.src.html`,
`stick-test.src.html`, `_layer.src.html`, `find.src.html`, `loadout.src.html` -
and added `checks/_verify_us_spelling.py` at **02:30:19**, eight minutes before
the receipt at 02:38:17.

**So the sweep read a `_deploy` built from a `_src` that no longer existed**, and
one of its nine failures is simply the new control having no RULE16 label yet:

    _verify_us_spelling.py: a NEW check with no RULE16 label

**I am not chasing the other eight.** Three controls disagreed with themselves in
both directions on 2026-08-28 for exactly this reason, and the lesson recorded
then was that it is one measurement taken during a write, not several defects.

**THIS IS THE THIRD TIME.** 08-28: C1 regenerated `data-layer/` mid-sweep. 08-29:
I edited `checks/` mid-sweep. Today: C1 edited `_src/` mid-sweep. **The sweep has
no lock and rule 14's own words apply - a rule that depends on everyone
remembering it is a convention, not a guard.** I closed the one perturbation I
owned, the drift control's rebuild. **The other two are still open by design.**

## WHAT I AM DOING

Rebuilding from the `_src` that exists now, sweeping once, and deploying only if
that sweep is clean. **If C1 is still editing, this will happen again**, and the
next honest step is not a fourth sweep - it is a way for a sweep to refuse to
start, or to declare itself void, when its inputs move underneath it.

### 2026-08-30 01:54:54 — 20260830_1000_update_q42-the-premise-is-wrong-the-miner-finds-299.md

# Update — Q42: the miner is not broken. It finds 299 transactions across all four families, and the regex needed no change.

**2026-08-30 15:00 UTC / 2026-08-30 10:00 local · Code (background session)**

**The order's premise does not survive the measurement, and the order is what
made that visible: *"run the miner over the FULL archive - 243 files, 208 MB,
not one session."* Run that way, transactions is not zero.**

    archive: 244 file(s), 208.3 MB

    extractor              verified   hits
    transaction            true       299
    location_inventory     true       1041
    quantum_route          true       339
    ship_class             true       23648
    mission_template       true       2115
    mission_objective      true       7670
    game_tip               true       3383
    equipment              true       16876
    mission_payout         true       312
    contract               true       948
    actor_death            true       121
    vehicle_destroyed      true       11
    mineable_rock          true       20
    object_container       false      0
    spawn_location         false      0
    location_inventory_name false     0

## AGAINST THE PYTHON DIG, WHICH IS THE ONLY HONEST COMPARISON

    Python 2026-08-07        item 286   commodity 10    233 sessions
    Go today                 item 289   commodity 10    244 files

    family commodity buy      1
    family commodity sell     9
    family item buy         279
    family item sell         10

**All four transaction families the header names are present.** Commodity
matches exactly at 10. Item is 289 against 286 - three more, which is what a
larger archive read eleven files later should look like, not a discrepancy.

## SO NOTHING IS CHANGED, AND THAT IS THE DELIVERABLE

**I did not touch `reMineTxn`.** The order said not to before a failing line was
in front of me. **There is no failing line, because there is no failure** - and
changing a working pattern on the strength of a wrong premise is exactly what
the instruction was protecting against.

**The `transactions: 0` was real but it was measuring one session.** A single
Game.log from a player who did not shop that session contains no
`SShopBuyRequest`, and zero is the correct answer to that question. The
extractor's `Verified: true` is also correct: the pattern is confirmed by 299
live samples.

**The two zeros that remain are the two UNVERIFIED patterns**, plus
`location_inventory_name`, which the file already documents as speculative -
1038 RequestLocationInventory lines across the archive and not one carrying
`name="`. **Every zero in that table is a zero the file already predicted.**

## AND ONE FIGURE IN THE HEADER IS STALE

    header says   240 SECONDS over the real archive
    measured      35.1 seconds, 244 files, 208.3 MB

**The reasoning around it still stands** - it is unbounded work proportional to
how much someone has played, and isolating it from the selftest was right. But
the number a future reader would plan against is off by a factor of seven.
`gamelog_mine.go` is not in `OWNERS.md`; I am reporting the figure rather than
editing someone's file to correct a comment.

## THE DIAGNOSTIC

`citizen-collector/zz_q42_archive_test.go`. A test file, so it never reaches the
shipped binary; gated behind `CC_Q42=1`, so nobody reads 208 MB of somebody's
play history by accident - which is the header's own complaint about the
selftest that did exactly that; and it writes to `t.TempDir()`. It reports the
program's own per-extractor accounting via `buildExtractors`, not a second count
written by me.

    CC_Q42=1 go test -run Q42 -v -timeout 40m

### 2026-08-30 01:52:03 — 20260830_0945_update_q42-taken.md

# Update — pushed `6b1837f`. Taking Q42: the miner reports zero transactions while declaring the extractor Verified.

**2026-08-30 14:45 UTC / 2026-08-30 09:45 local · Code (background session)**

    6b1837f   14 files changed      bd4cac2..6b1837f      tree clean
    no _to_delete, no node_modules, no editability_patches in the commit

A stale `.git/index.lock` from 01:20 blocked staging - C1's Cowork mount cannot
delete files, exactly as `NEXT.md` records. **Confirmed no git process was
running**, then moved it to `_to_delete/git-locks/`.

## Q42, AND THE NUMBER I AM MEASURING AGAINST

The Python dig's own manifest is on disk and gives me the target rather than a
remembered figure:

    data-layer/derived/gamelog-mining/MANIFEST.json
      sessions_read      233
      item_txn_rows      286
      commodity_txn_rows  10
      parse_errors         0

The archive is where the header says: **243 files, 209 MB**, at
`Program Files/Roberts Space Industries/StarCitizen/LIVE/logbackups`. Read only -
rule 6 is about writing outside the repo, and I am not writing there.

The pattern under suspicion, and I am **not touching it** until a failing line is
in front of me:

    reMineTxn = S(Shop(?:Commodity)?)(Buy|Sell)Request\s*-\s*(.*)

Its extractor declares `Verified: true`. **A verified extractor reporting zero
is either a broken pattern or a false declaration, and both are worth more than
the transactions.**

## EXPECTATIONS SET BEFORE RUNNING

The header records **240s over the real archive against 61ms isolated**, and
that the gap was once misdiagnosed as a flaky test. **It is unbounded work, not
a flake.** I am budgeting minutes and will not kill it for being slow - killing
long runs is how I lost a payload copy yesterday.

### 2026-08-30 01:46:35 — 20260830_0930_update_built-swept-and-the-deploy-is-blocked-by-nine-readable-names.md

# Update — built and swept. My four controls are fixed. The deploy is blocked by nine names a visitor can read, and they are C1's.

**2026-08-30 14:30 UTC / 2026-08-30 09:30 local · Code (background session)**

## THE BUILD CARRIED EVERYTHING

    cmSummary     src 2  deploy 2      Hull armor    src 2  deploy 2
    unnamedTag    src 4  deploy 4      Hull armour   src 0  deploy 0
    comment strip: 1677 removed; every deployed .js and inline script parses
    Greycat 3, Grey's Market 3         <- names preserved, as instructed

## DRACO IS IN, AND NOT RUN IS GONE

    106 ok, 4 failed, 0 skipped, 0 NOT RUN, in 926s

`_verify_marker_mesh_distance.py` now runs and passes - 5,800 markers on 256
hulls. Installed `--no-save` into `checks/node_modules`; **`checks/package.json`
is byte-identical**, which was Sleven's constraint.

## FOUR OF MINE, AND THEY WERE ALL ONE DEFECT

**`_verify_column_split.mjs`** read `data-fixed` alone in TWO places and put
**716 ports on the wrong side fleet-wide** - every one a countermeasure sitting
exactly where it belongs. Its L4 section also sampled the first fixed port with
a part, which is now inside the summary and has no row: `indexOf` returned -1,
the "row" became the last character of the page, and three content assertions
failed against a correct page. **27 assertions, exit 0.**

**`_verify_panel_findable.mjs`** asserted the title contained `colour`. Sleven's
US-spelling instruction reached the copy and it went red. **A control that pins
the spelling of a word is asserting house style, not behaviour** - it now
accepts `colou?r`.

**THAT IS FIVE PLACES ACROSS THREE FILES.** C1 named two. `_verify_ship_page`
held four, `_verify_column_split` three more. The rule "a fixed port is
represented by its own row OR by a summary naming it" is now written out
identically in three files, **and that is the weakness**: the sixth copy is the
one that will be missed. Worth one shared helper, and I am not building it at
the end of a pass.

## THE DEPLOY IS REFUSED, AND IT IS RIGHT TO BE

    _verify_display_names.py   REFUSED - 9 name(s) a visitor can read

    truncated  6
      BMBRCK_S03_BEHR_Single_S03   shows 'CST-313 \'
      Turret_PDC_BEHR_G            shows 'MRX \'      game  MRX "Torrent"
    disagrees  3
      MRCK_S04_KRIG_S65_Stingray_Left   shows the raw class name

**Six names are truncated at a backslash.** `MRX "Torrent"` becomes `MRX \` -
which reads like an escaping bug in the name derivation, where a quoted name is
cut at the escaped quote. **C1's own control caught it**, which is the system
working, and it is C1's to fix: `build_loadout_data.py` is theirs as of today.

**I have not deployed.** Nine wrong names on a page whose claim is that its
numbers can be trusted is not something to ship past a red control.

`_verify_picker_deployed.mjs` is the fourth failure and is deployed-only -
expected until this ships.

## ANSWERS

**C1 claiming `build_loadout_data.py` is not wrong.** The ship page and its data
are theirs; a generator whose only consumer is C1's page should not have a
different writer.

**Q38 not touched.** Ping and we move `_WEAPONY` and `MARKABLE` together.

**Q44 recorded:** no fuzzy matching in the reader, Levenshtein out, exact
vocabulary hits only. Not started.

## AND ONE THING C1'S SPELLING PASS MISSED

Identifiers were correctly left alone - `id="armour"`, `_view.colour()`,
`data-colour`. **Five pieces of VISIBLE copy were not:**

    index.html    "Calm - muted colour, no motion, soft borders"
    index.html    "Turning this down helps if bright colours feel harsh"
    loadout.html  <th>vs. unarmoured</th>

C1's files. Reported, not edited.

### 2026-08-30 01:25:35 — 20260830_0900_update_build-sweep-deploy-taken.md

# Update — build, sweep, deploy, commit. Taking it, and installing draco3d because the gate cannot pass without it.

**2026-08-30 14:00 UTC / 2026-08-30 09:00 local · Code (background session)**

C1's work is all in `_src` and none of it is on the site: 107 corrected item
names, US spelling, the countermeasure summary, and the "Unknown Manufacturer -
1" fix on 1,450 parts.

## THE ONE DECISION THIS FORCES

**The deploy gate refuses today on `_verify_marker_mesh_distance.py` being NOT
RUN**, because draco3d is absent. A NOT RUN counts against the sweep and never
as a pass - that is my own Q29 work and I am not going to walk around it.

**So deploying requires installing draco3d.** Sleven offered it conditionally on
2026-08-29 - *"npm i draco3d if you want it live; don't add it to a shared
package.json without saying so"* - and has now instructed a deploy. **I am
treating the instruction plus the offer as the authorisation**, which is more
than I was willing to act on when it was the offer alone.

**Installed with `--no-save` into `checks/node_modules`.** There is no repo-root
`package.json`; the only one is `checks/package.json`, which is the shared file
he named. `--no-save` makes the control runnable and **leaves that manifest
untouched**, which is the constraint kept rather than worked around.

**Rule 7 says downloaded code is data and is not to be imported or run.** This
is an exception granted by Sleven, the same way Playwright was - and Playwright
got a dated `docs/DECISION_*` for it. **This deserves one too**, and it is C1's
control rather than mine, so I am recording the fact here and not writing the
decision unasked.

## ORDER, AND WHY

    1  install draco3d      so the control can run at all
    2  build                carry _src into _deploy
    3  full sweep           one sweep, not two - a subset would only write a
                            partial receipt and could not open the gate
    4  sweep_gate --check   ask, do not assume
    5  deploy               only if it passes
    6  commit and push

## OWNERSHIP

**C1 claims `build_loadout_data.py` and asked me to say if that is wrong. It is
not wrong.** The ship page and its data are already C1's, and a generator whose
only consumer is C1's page should not have a different writer. Recorded here
because they asked in writing and deserve an answer in writing.

## Q38 IS NOT IN THIS PASS

Agreed and understood: my `_WEAPONY` and C1's `MARKABLE` change together or not
at all, and five controls check that they agree. **I will ping when I take it.**

### 2026-08-30 00:56:53 — 20260830_0320_update_committed-and-pushed-bd4cac2.md

# Update — committed and pushed as `bd4cac2`. Q37 and Q39 in history; tree clean.

**2026-08-30 08:20 UTC / 2026-08-30 03:20 local · Code (background session)**

    bd4cac2   18 files changed, 1,639 insertions, 367 deletions
    7cda543..bd4cac2  main -> main
    local == remote == bd4cac2      git status --porcelain   0 entries

## Verified after, not assumed

- **`_to_delete/` contributed 0 files**, and **`editability_patches.json` is not
  in the commit** - checked for both by name in the index before and in
  `git log -1 --name-only` after. The leftover plant did not enter history.
- No path outside the eight expected roots.
- Push confirmed by fetch and hash comparison.

## THE ONE JUDGEMENT CALL, REVERSED FROM LAST TIME

`testing/_src/loadout.src.html` is IN this commit. **I excluded it from
`7cda543` because no sweep had seen it.** It is included now because my Q37 fix
asserts on the markup it introduces - `data-cm-ports` and the `cm-summary` row -
so committing the control without the page would leave a control that cannot
pass. **They were verified together** by `_verify_ship_page` (237 assertions)
and `_verify_loadout_fitment`, both exit 0. **A full sweep still has not run
over it**, and that is in the commit message rather than left to be discovered.

## WHERE THINGS STAND

    Q37, Q39     done
    Q3           dry run done, list ready, NOT written - wants a verified
                 backup (rule 4) and an answer on Mule/STV sharing one stated
                 dimension triple
    Q38          not started - my _WEAPONY and C1's MARKABLE must move in the
                 same breath, 602 markers, two owners
    the deploy   still refused: _verify_marker_mesh_distance.py is NOT RUN
                 without draco3d. That is the only blocker left that is not
                 mine, and it is a one-line install away whenever Sleven says.

## OPEN AND MINE, AND IT IS THE ONE I WOULD TAKE FIRST

**`_verify_loadout_fitment.py` can leave a planted value in
`data-layer/editability_patches.json`** and therefore in the shipped data layer.
Cause not established - I guessed twice and could show neither. Until it is
fixed, **anything that builds after a sweep should check that file is absent
first.**

### 2026-08-30 00:52:48 — 20260830_0310_update_correcting-my-own-diagnosis-of-the-leftover-plant.md

# Correction — I gave a confident cause for the leftover plant twice and neither is established. Here is only what I can show.

**2026-08-30 08:10 UTC / 2026-08-30 03:10 local · Code (background session)**

Twenty minutes ago I filed that `_verify_loadout_fitment.py`'s plant survived
because *"a `finally` does not run when the process is killed"*. Then I said it
**leaks on every run**. **I have not established either.**

## WHAT IS ACTUALLY MEASURED

    the file        data-layer/editability_patches.json
    its content     {"AEGS_Avenger_Stalker|...missilerack_right_wing":
                     "4.99-CONTROL"}
    who writes it   _verify_loadout_fitment.py, and nothing else.
                    build_loadout_data.py only READS it, lines 1282-1283, and
                    C1's change today does not touch those lines.
    where it got to testing/_src/loadout_data.gen.js - the ship page's data
                    layer - and NOT testing/_deploy, and NOT the served site.
    now             absent from all three. Verified after regenerating.

**A build would have carried it.** That part I stand behind and it is why this
was worth stopping for: a visitor would have seen `4.99-CONTROL` as a version on
an Avenger Stalker's missile rack.

## WHAT I COULD NOT REPRODUCE CLEANLY

    run A   file absent before -> exit 0 -> file PRESENT after, plant in gen.js
    run B   file absent before -> exit 1 -> file absent after
    run C   file absent before -> exit 1 -> file PRESENT after

**Three runs, three outcomes, from the same starting state.** That is not a
mechanism I can name, and naming one anyway is what I did twice tonight. The
control also has more than one plant section and I have only read one of them.

## WHY I AM STOPPING RATHER THAN CHASING IT

It is 03:10. The control mutates a real data file and re-runs a generator that
C1 claimed today, and I have already twice asserted a cause I could not show.
**A third guess would be worse than the defect.**

**The tree is clean** - no plant file, `4.99-CONTROL` in neither `_src` nor
`_deploy`, and `loadout_data.gen.js` differs from HEAD by three lines that are
C1's livery and display-name work, not mine.

**The item for whoever takes it**, and it is mine: `_verify_loadout_fitment.py`
can leave a planted value in `data-layer/editability_patches.json` and therefore
in the shipped data layer. Reproduce by running it repeatedly from a clean
state and watching that path. **Until it is fixed, anything that builds after a
sweep should check that file is absent first.**

## Q39 AND Q37 ARE UNAFFECTED AND STILL DONE

Both were verified after the plant was cleared:
`_verify_loadout_fitment.py` and `_verify_ship_page.mjs` (237 assertions) both
exit 0 on a clean tree.

### 2026-08-30 00:50:44 — 20260830_0300_update_q39-q37-done-and-a-control-left-a-fake-value-in-the-data-layer.md

# Update — Q39 and Q37 done. And a control's own planted test value was sitting in the ship page's data layer, one build away from shipping.

**2026-08-30 08:00 UTC / 2026-08-30 03:00 local · Code (background session)**

## THE THING THAT MATTERS MOST IS NOT EITHER QUEUE ITEM

`data-layer/editability_patches.json` turned up as a new untracked file. **I
assumed it was C1's. It was not.**

    { "AEGS_Avenger_Stalker|hardpoint_weapon_missilerack_right_wing": "4.99-CONTROL" }

**`4.99-CONTROL` is `_verify_loadout_fitment.py`'s own planted test value.** The
control plants an override, regenerates, asserts it reached the page, then in a
`finally` removes it and regenerates again. **A `finally` does not run when the
process is killed** - and I killed sweeps twice yesterday. The plant survived.

**It was IN `testing/_src/loadout_data.gen.js`** - the ship page's entire data
layer - **and not in `_deploy` and not on the served site. One build would have
carried it.** A visitor would have seen a version of `4.99-CONTROL` on an
Avenger Stalker's missile rack.

Moved to `_to_delete/leftover-plant-20260830/`, regenerated, plant gone,
`_verify_loadout_fitment.py` exits 0.

**THIS IS THE THIRD TIME TODAY THE SAME DEFECT HAS APPEARED**: exception-safe
cleanup that is not kill-safe. I fixed it in my drift control yesterday with a
pending marker; `_verify_loadout_fitment.py` has it too and I have NOT fixed it
there yet. **That is the real item, and it is bigger than either of C1's.**

## Q39 - DONE

`un` allowed alongside `n`, `m`, `ev`, `tags`, **and deliberately still a narrow
allowlist**. Reading any unrecognised key as a stat is what made this fire at
all. The reason `un` exists is recorded at the site: 61 liveries had no name in
the game files and the page was printing CIG's `<= PLACEHOLDER =>` marker.

## Q37 - DONE, AND IT FOUND SOMETHING WHILE BEING FIXED

Rows became a bad proxy the moment one row could stand for several ports.
**Not relaxed - pointed at what was actually wanted:**

    every fixed port is REPRESENTED - by its own row or by a summary naming it
    and Specs claims no port that is NOT fixed          <- new
    and the two sum to every one of the 57 ports

**The new over-claim guard earned itself immediately.** It flagged
`cm-summary` - the summary row's own identifier, which is not a port - and that
sentinel is exactly why the sum read 37 of 57 instead of 36. A guard added on
principle caught a real miscount within a minute of existing.

**Four places counted rows, not two.** C1 named two; the column-split section
and the editability-flip test did the same thing, and the flip test also picked
the FIRST fixed port, which can now live inside a summary. All four now use one
definition of "represented", so the next fold cannot make three of them wrong
and one right.

    _verify_ship_page.mjs   237 assertions, exit 0

## ALSO

**C1 claims `build_loadout_data.py` in `OWNERS.md`** and says explicitly that
Code is the one to object. **No objection** - the ship page and its data are
C1's, and a generator whose only consumer is C1's page should not have a
different writer. The gap was real and closing it is right.

**Their display-names fix works:** the regeneration reports `agree 275,
disagree 0`, where it was 19 disagreements. Q34's Avenger-showing-GLADIUS is
gone.

**Q38 is not started.** It needs my `_WEAPONY` and C1's `MARKABLE` to change in
the same breath, and C1 has said they will move the moment I do. That is a
coordination I want to do awake, not at 03:00.

Uncommitted: `checks/_verify_loadout_fitment.py`,
`checks/_verify_ship_page.mjs`, `scripts/fix_model_scale.py`, and C1's files.

### 2026-08-30 00:26:12 — 20260830_0240_update_q3-dry-run-done-not-writing-tonight.md

# Update — Q3's dry run is done and the list is ready. I am not writing tonight, and three things need answering first.

**2026-08-30 07:40 UTC / 2026-08-30 02:40 local · Code (background session)**

## THE DRY RUN, WHICH IS RULE 5's REQUIREMENT AND IS NOW SATISFIED

    source: model_scaled.glb per ship        <- Q3's whole point
    7 ships, 14 files, every one MOVED ASIDE to _to_delete/, nothing deleted
    Nothing written. Re-run with --write to proceed.

`scripts/fix_model_scale.py` already did the right things: dry run by default,
`--source scaled`, and move-aside rather than delete. Nothing new had to be
built to do this safely.

## A FLAG THAT TOLD THE TRUTH AND A MESSAGE THAT DID NOT

The dry run printed **`would import each sc-ships/<folder>/model.glb`** no
matter what `--source` was set to, while the header two lines above said
`model_scaled.glb`.

**The flag itself is applied correctly** - `src_name = "model.glb" if
args.source == "raw" else "model_scaled.glb"` - so this was a lying message and
not a lost switch. **It is still a defect, and a pointed one: Q3 exists BECAUSE
these ships were once scaled from the wrong file.** A dry run that names the
wrong source is how somebody approves exactly that a second time.

It now prints the real source and the per-ship path with an exists/MISSING
verdict, so the claim can be checked instead of trusted.

## FOUR THINGS FOUND BEFORE ANY MUTATION

**1. Nine model files, not twelve.** Fourteen findings, nine distinct `.glb`s -
variants share models. **Twelve reconciles with nothing on disk.**

**2. Four of the nine do not map to a folder by their deployed name.** The build
derives `Starlancer_TAC.glb` from a folder called `Starlancer TAC`, and
`San_tok.y_i.glb` from `San'tok.yāi`. **A naive from-list keyed on the deployed
name would have found four MISSING folders and either failed or skipped them
silently.** All nine were resolved by reversing the build's own name rule, and
every folder and `model_scaled.glb` was asserted present before the list was
written.

**3. Drake Mule and Greycat STV share one stated triple** - `[8.8, 6.0, 3.5]` -
between two different vehicles. **Both are EXCLUDED from the list.** At least
one of those published figures is wrong, and scaling a hull to bad data makes
the hull wrong while making the auditor go quiet about it.

**4. The DONE-WHEN cannot fail.** *"`_verify_model_scale.py` still exits 0"* -
it exits 0 right now with 24 findings, because it is a findings-only auditor
that flags and never fails. **The finish line I will hold to instead: the seven
files measure inside the band and their rows leave the auditor's SCALE section.**

## AND RULE 15's OWN EXAMPLE BIT A THROWAWAY DIAGNOSTIC

    UnicodeEncodeError: 'charmap' codec can't encode 'ā'

Printing `San'tok.yāi` to a cp1252 stdout. **Rule 15 names that exact ship as
the reason the rule exists**, and says a one-off diagnostic has hit it before.
It has now hit it again. Fixed with `sys.stdout.reconfigure`, the way the
repo's other scripts do it.

## WHAT I AM NOT DOING TONIGHT

**Not running `--write`.** It is an irreversible binary mutation of seven ship
models and **rule 4 wants a verified backup first** - `Backup-CitizenCompass.ps1`
run and its output CONFIRMED, not merely started. That is worth doing awake.

The list is saved and the command is one line when it is time:

    venv/Scripts/python.exe scripts/fix_model_scale.py --source scaled
        --from-list <the list> --write

Uncommitted: `scripts/fix_model_scale.py` (the dry-run message).
**`scripts/fix_model_scale.py` has no declared owner in `OWNERS.md`** - a gap,
and C1's to close.

### 2026-08-30 00:23:54 — 20260830_0225_update_taking-q3-dry-run-first.md

# Update — Q3 taken. No updates from C1. Dry run first, and three things do not add up before anything is written.

**2026-08-30 07:25 UTC / 2026-08-30 02:25 local · Code (background session)**

Checked: **C1 has changed nothing since `7cda543`.** Their `loadout.src.html`
edit is still uncommitted and still unswept - deliberately left in the working
tree, as recorded in that commit.

**Q3 is the first open item that is mine and unblocked.**

## THE TOOL ALREADY DOES THE RIGHT THING

`scripts/fix_model_scale.py` needs no Blender import of its own, is **DRY RUN by
default**, moves the previous files aside rather than deleting them, and takes
**`--source scaled`** - which is precisely what Q3 asks for. Nothing new has to
be written to do this safely.

## THREE THINGS THAT DO NOT ADD UP, BEFORE ANY MUTATION

**1. Q3 says twelve. The auditor reports fourteen findings across NINE distinct
model files.**

    Starlancer_TAC.glb   Starlancer_MAX.glb   San_tok.y_i.glb
    Avenger_Stalker.glb  Clipper.glb          Polaris.glb
    Vulture.glb          Mule.glb             STV.glb

Variants share models, which is where the extra rows come from. **Twelve is not
a number I can reconcile with anything on disk**, and a mutation list that
disagrees with its own order is exactly the thing to stop on.

**2. Drake Mule and Greycat STV are BOTH stated [8.8, 6.0, 3.5].**

    Drake Mule    model [4.2, 3.0, 2.7]   stated [8.8, 6.0, 3.5]  = 0.48x
    Greycat STV   model [4.2, 2.7, 2.0]   stated [8.8, 6.0, 3.5]  = 0.48x

Two different vehicles with identical published dimensions. **One of those
stated figures is probably wrong, and scaling a model to a wrong published
dimension makes the model wrong** - it would move a hull to match bad data and
the auditor would then report it as correct. This needs looking at before either
is touched.

**3. RSI Polaris appears twice, identically.** Two ship records sharing one
model and one name. Harmless to the rescale, but it means the "count of
findings" is not a count of ships.

## AND THE DONE-WHEN CANNOT FAIL

    "AND `_verify_model_scale.py` still exits 0"

**It exits 0 right now, with 24 findings.** It is a findings-only auditor - it
flags and never fails - so that clause is satisfied no matter what I do to the
models, including breaking them. C1 replaced a DONE-WHEN naming a file that did
not exist with one naming a control that cannot fail. **The honest finish line
is: the nine files measure within the band, and their rows disappear from the
auditor's SCALE section.** That is what I will hold myself to.

## WHAT HAPPENS NEXT, IN ORDER

    1  dry run, report-only, and show the list          <- rule 5
    2  Backup-CitizenCompass.ps1, output CONFIRMED      <- rule 4
    3  only then --write, and only for files whose
       published dimensions are not themselves in doubt

**Nothing is written tonight without that backup being verified**, and the Mule
and STV are not touched until somebody says which of the two stated figures is
right.

### 2026-08-30 00:17:36 — 20260830_0210_update_drift-control-fixed-deploy-blocked-by-c1s-two.md

# Update — the drift control is fixed and proven. The deploy is now blocked by two controls that are both C1's, and one of them is finding a real, visible defect.

**2026-08-30 07:10 UTC / 2026-08-30 02:10 local · Code (background session)**

## THE FIX, AND WHY THE SECOND ATTEMPT WORKED

I measured instead of guessing, and there were two causes, not one:

    keybinds.html / loadout.html   diverged exactly at /* CC_DISC_CSS */
    find.src.html                  is CRLF; its output is LF

**The injection markers are themselves comments.** `<!-- CC_VENDOR_THREE -->`
and `/* CC_DISC_CSS */` - so stripping the source deletes the anchors the
segmentation is built on, and every page diverges at the first one. Stripping
the SEGMENTS instead fails differently: a segment can begin inside a `<script>`
block and the stripper then reads JavaScript as markup, which is why
`loadout.html` and its 437 template literals was the page that broke last night.

**Protect the markers, strip the whole document exactly as the build does, put
the markers back.** Plus the disclosure gap now compares against
`strip_css(_disc.css)`, because the CSS is substituted in and the page stripped
after.

    14 passed, 0 failed        --self-test exit 1

## IT IS A RECONCILIATION, NOT AN EXEMPTION, AND I PROVED THAT

Only the `_src` side is stripped, so a comment HAND-ADDED to `_deploy` still
has nothing to match against:

    planted a comment at the end of _deploy/download.html
      FAIL every copied file in _deploy is its _src source byte for byte
      FAIL and so is every copied file (moved: download.html)

Two independent assertions. `download.html` restored byte-identical. Section 5's
existing plants still pass through the new comparison, so the detection path is
whole.

**Declared honestly:** the control now imports the build's own stripper, so a
change to the STRIPPER passes here unremarked - the same trade
`attribution.TRADEMARK_HTML` already makes. `_verify_comment_strip.py` is what
closes it, by proving the stripper against node rather than against itself.

## THE SWEEP

    107 ok, 2 failed, 0 skipped, 1 NOT RUN, in 782s

    _verify_display_names.py        FAILED     C1's, OWNERS.md line 55
    _verify_marker_mesh_distance.py NOT RUN    C1's, line 57, needs draco3d
    _verify_picker_deployed.mjs     deployed-only, expected until this ships

**Everything of mine is green**, including the two guards I repaired and the
drift control.

## AND C1'S CONTROL IS FINDING SOMETHING REAL

    19 parts show a name that disagrees with the game's

    AEGS_Avenger_CML_Chaff   shows "Aegis Gladius - Noise Launcher"
                             game  "Aegis Avenger - Noise Launcher"
    ANVL_F7A_CML_Chaff       shows "Anvil Noise Launcher"
                             game  "Anvil Hornet F7A - Noise Launcher"

**An Avenger part is printing GLADIUS on the page.** That is the same shape as
Q1 - 31 ships printing another ship's name on their armour - on a page whose
whole claim is that the numbers can be trusted. It is C1's control and C1's
pipeline, and I am reporting it rather than touching it.

## THE DEPLOY IS STILL BLOCKED AND I HAVE NOT DEPLOYED

    GATE EXIT 1

Both blockers are C1's. **Nothing of mine stands between the payload and the
site any more**, and I am not weakening the gate to get past somebody else's
finding - least of all one that is right.

Uncommitted: `checks/_verify_deploy_drift.py`.

### 2026-08-29 23:59:20 — 20260830_0140_update_q31-is-built-and-the-deploy-is-blocked-by-my-own-control.md

# Update — Q31's strip is done and proven. The deploy is BLOCKED by my own drift control, correctly, and I stopped trying to reconcile it rather than keep making it worse.

**2026-08-30 06:40 UTC / 2026-08-30 01:40 local · Code (background session)**

## WHAT IS DONE AND PROVEN

    _verify_no_agent_traces.py   PASS, exit 0
    _verify_comment_strip.py     21 assertions, exit 0; --self-test exit 1
    comment strip: 1672 removed; every deployed .js and inline script parses
    browser controls             camera framing, panel dismiss, hull solid,
                                 disclosure, armour naming - all green
    @license                     survived
    comments in _src / _deploy   165 / 0

## THE SWEEP FOUND FOUR THINGS AND I FIXED THREE

    104 ok, 4 failed, 0 skipped, 1 NOT RUN, in 831s

**_verify_find_page.mjs and _verify_shared_viewer.mjs** both carried a guard
reading *"the comment stripper works"* - each required the SHIPPED page to
contain a particular comment and then checked their own regex had removed it.
**They were testing the fixture as much as the stripper, and Q31 took the
fixture away.** Both now prove their stripper on a LOCAL fixture and also assert
the stripped code is not empty, which the old form never did. Green.

**_verify_find_page.mjs also required `GENERATED by build_find_data.py` in the
DEPLOYED data file** - the exact class of trace Q31 removes. **Two requirements
in direct conflict, and the instruction wins.** The claim moved to `_src`, where
the header still is, plus a new assertion that the deployed copy does NOT name
it. Green.

**_verify_picker_deployed.mjs** is a deployed-site control comparing served
against local; the served site is the pre-strip payload, so it is expected and
the gate already counts it as deployed-only.

## THE FOURTH IS MINE AND I STOPPED

**`_verify_deploy_drift.py` is red because the comment strip is a transform it
does not know about**, and that is the control doing its job. Section 3 holds
every copied file byte-for-byte against `_src` outside declared injections; the
strip makes all of them differ.

**I tried to reconcile it and made it worse.** Applying the build's own strip to
the `_src` side got the `.js` and `.gen.js` files clean and left one page
failing. Switching to a whole-document strip with protected markers - because
the markers ARE comments, so segmenting first hands the stripper a fragment that
can begin inside a `<script>` - took it from one failing page to four.

**So I stopped.** The working copy is preserved at
`_to_delete/drift-wip-20260830/` and the control is restored to its committed
state. **Reconciling it by accretion at 01:40 is how a guard ends up with a hole
in it**, and this is the control that makes an unauthorised write to `_deploy`
loud.

**What I think the answer is, for whoever picks it up:** section 4 already
proves the payload by REBUILDING and comparing, and it passes. Section 3's
byte-comparison against `_src` is what the strip complicates. Whether section 3
should compare against a stripped source, or whether the rebuild in section 4
now makes it redundant, is a design question and wants a clear head.

## THE DEPLOY IS BLOCKED AND I DID NOT DEPLOY

    sweep_gate --check testing/_deploy   EXIT 1

Sleven asked for sweep, deploy, commit and push. **The sweep refused the deploy
and I am not going around it.** The served site stays on the pre-strip payload,
which is the safe direction: nothing about it is wrong, it just still carries
its comments.

### 2026-08-29 23:34:38 — 20260830_0110_update_q31-comments-no-longer-ship.md

# Update — Q31 done. 1,672 comments stop at the door, `_src` keeps every one of them, and the strip is proven by node rather than by itself.

**2026-08-30 05:10 UTC / 2026-08-30 00:10 local · Code (background session)**

    _verify_no_agent_traces.py   PASS - nothing in the published payload says
                                 how it was built.   exit 0
    comment strip: 1672 comment(s) removed on the way into _deploy;
                   every deployed .js and inline script still parses
    @license in holo.html        1, survived
    comments in _src / _deploy   165 / 0

## THE RISK WAS NEVER THE TRACES

`_verify_no_agent_traces.py` asks whether the words are gone. **It would be
perfectly happy with a strip that also deleted a line of code, because a broken
page contains no traces either.** So the work was a scanner with the same states
the language has, not a regular expression:

    "http://example.com"     a // inside a string is not a comment
    /a[/]b/                  a regex literal containing a slash
    `x${ a /* gone */ }y`    a comment inside a template EXPRESSION is a comment
    `keep // this`           the same text inside template TEXT is not
    a / b // gone            division, then a real comment

**437 template literals in `loadout.html` alone**, so this was not hypothetical.
`testing/_src/strip_comments.py`, proven by `checks/_verify_comment_strip.py` -
**21 assertions, including every real `.js` in `_src` handed to `node --check`,
which shares no code or assumption with the scanner.**

## AND THE BUILD REFUSES RATHER THAN SHIPPING A BROKEN PAGE

Every deployed `.js` and every inline script is parsed AFTER the strip. Proven
by planting a stripper that ignores string literals:

    BUILD FAILED: the comment strip left JavaScript that does not parse.
    Nothing has been uploaded.
      loadout_model.gen.js: ...loadout_model.gen.js:23

**That is the failure mode this had to have**, and it is the one the traces
control cannot see.

## FIVE WRITE PATHS, INCLUDING THE ONE THAT WOULD HAVE LEAKED

Everything entering `_deploy` goes through one function. **The byte-for-byte
copy path was the interesting one**: a page needing no substitution was copied
verbatim, which would have been the single route comments still shipped by while
everything else looked clean.

## WHAT I DID NOT DO

**Nothing was hand-edited and `_src` keeps all 165 of its comments.** The nine
`_src` files that changed are the build regenerating its own `.gen.js` data, as
every build does - not the strip. The `GENERATED by testing/_src/build_deploy.py`
header is still in `_src` and gone from `_deploy`, which is the right way round.

**The browser controls pass on the stripped payload** - camera framing, panel
dismiss, hull solid, disclosure, armour naming, all green. That is the check
that the pages still WORK, as opposed to still parsing.

## ONE THING I LOOSENED, AND I WANT IT ON THE RECORD

`_check_inline_js` refused any page with zero inline scripts. Correct for the
two source pages it was written for; wrong for `download.html`, which
legitimately has none, and it failed my first build. **I added
`require_any=False` for the post-strip pass only** - the source-page rule is
untouched. A check that cries wolf at a page that is exactly as it should be is
how checks get switched off.

## NEW FILES, AND ONE THING FOR C1

    testing/_src/strip_comments.py       mine
    checks/_verify_comment_strip.py      mine, RULE16 INDEPENDENT

**Neither is in `OWNERS.md`, which C1 maintains.** They are mine by the default
clause under `checks/` and by having written them, but the manifest should say
so - that is C1's edit to make, not mine.

**Not deployed.** The payload is built and clean; a deploy needs a full sweep
first and Sleven's word.

### 2026-08-29 23:24:22 — 20260830_0050_update_taking-q31.md

# Update — Q31 taken. The strip is a text transform on shipped code, so the hazard is the strip itself, not the traces.

**2026-08-30 04:50 UTC / 2026-08-29 23:50 local · Code (background session)**

Checked for updates. **C1 added Q31 and rewrote Q32 since `1cf4987`.** Q32 is
BLOCKED-BY Sleven and nobody rewrites copy before he rules. **Q31 is unblocked,
is Sleven's direct instruction, and the fix is in `build_deploy.py` - mine.**

## VERIFIED MYSELF BEFORE STARTING

    _verify_no_agent_traces.py              exit 1   (red today, by design)
    _verify_no_agent_traces.py --self-test  exit 9
      "DETECTION PROVEN - every planted trace is caught and no safe string is
       flagged - but the real payload is not clean yet"
    holo.html @license occurrences           1       (three.js MIT - must survive)
    loadout_marker.gen.js opens with         "GENERATED by testing/_src/build_deploy.py"

## THE ACTUAL RISK, AND IT IS NOT THE TRACES

**Stripping comments from shipped HTML and JavaScript is a text transform on
working code, and the naive version breaks pages silently.** What a regex gets
wrong:

    "http://..." inside a string          `//` is not a comment
    a regex literal containing /* or //   not a comment either
    <!-- --> inside a <script> block      markup rules do not apply there
    an unterminated /* in one file        eats the rest of the file

**A page that loses a stylesheet or a script and still renders is exactly the
failure this project keeps finding**, and it would ship looking fine. So the
strip has to be proven by BEHAVIOUR, not by the traces control going green:
the traces control only asks whether the words are gone.

## HOW I WILL PROVE IT, BEFORE I WRITE IT

    1  every stripped file still PARSES - node --check for JS, and the build
       already runs node --check on inline scripts, which I will not weaken
    2  the existing browser controls still pass against the stripped payload -
       they load the real pages in a real browser
    3  @license and @preserve survive, asserted per file rather than assumed
    4  _src is byte-identical afterwards - the strip happens on the way INTO
       _deploy and nowhere else
    5  a deliberately-unstripped payload still makes the traces control fail,
       so a strip that silently did nothing cannot read as success

**Nothing gets hand-edited.** 1,114 comment blocks are the best documentation
this project has and they stay in `_src`.

## AND ONE THING I WILL CHECK RATHER THAN ASSUME

The `.gen.js` headers name the build script. **Those are written by
`build_deploy.py` itself**, so for those the honest fix may be to write a
different header rather than to strip one - a generated file saying nothing
about where it came from is fine; a generated file that lies is not. I will look
before deciding.

### 2026-08-29 23:03:47 — 20260830_0040_update_committed-and-pushed-1cf4987.md

# Update — committed and pushed as `1cf4987`. Q30 is in history; tree clean.

**2026-08-30 04:40 UTC / 2026-08-29 23:40 local · Code (background session)**

Sleven said commit and push, in this session, for this change. Rule 2 satisfied.

    1cf4987   9 files changed, 640 insertions, 306 deletions
    162231e..1cf4987  main -> main
    local HEAD == origin/main == 1cf4987
    git status --porcelain    0 entries

## Verified after, not assumed

- **`_to_delete/` contributed 0 files**, and **no receipt entered history** -
  checked for both in the index before and in `git log -1 --name-only` after.
  The new `.last_sweep_partial.json` is ignored by the line added in this same
  commit, so it never had a chance to.
- **No path outside the four expected roots.** Filtered; empty.
- **The push landed** - fetch and hash comparison.

## THE DAY, IN FIVE COMMITS

    4710d30   the heap fix, the deploy gate, 295 ships photographed
    d1e60b4   the drift control stops writing to what it audits
    85e1d3b   three markers declared rather than forgotten, and deployed
    162231e   the sweep can say "I could not look", and the clock stops
              being a false red
    1cf4987   a subset run can no longer erase a sweep

**Four of the five are the same defect in different clothes**: something wrote
where it should only have read, or reported a state it had not actually
established. That is worth saying out loud rather than counting as five separate
wins.

## WHAT IS OPEN, AND NONE OF IT IS BLOCKED ON ME

    Q3    scale the 12 from model_scaled.glb, not model.glb - open, mine,
          older than today
    Q5    R3 of the roadmap watcher - open, mine
    Q28   two placement writers and one containment gate - C1's to design
    Q26   C1's mesh distance. The Glaive pair is C1's ruling.

    the served site   still one UTC date stamp behind local. The drift control
                      is honest about it now; they still do not match.
    the deploy gate   refuses today on _verify_marker_mesh_distance.py being
                      NOT RUN, which is correct and is not a defect.
    draco3d           not installed. Asked properly; rule 7 says downloaded
                      code is data, and a conditional offer is not the
                      authorisation.

**Next, unless told otherwise: Q3.** It is the older of the two open items and
its DONE-WHEN now names a control that exists.

### 2026-08-29 23:02:03 — 20260830_0030_update_q30-done-a-subset-can-no-longer-erase-a-sweep.md

# Update — Q30 done. A subset run can no longer erase a sweep, and the message that hid it for a day now names the path it actually wrote.

**2026-08-30 04:30 UTC / 2026-08-29 23:30 local · Code (background session)**

My call, made and built rather than restated: **fail-closed was not sufficient.**

    a full sweep   -> checks/.last_sweep.json          unchanged
    --only         -> checks/.last_sweep_partial.json
    --self-test    -> checks/.last_sweep_partial.json

**Self-test goes with it** because it inverts every expectation, so it is not a
sweep of the payload either - and until today a self-test run also took a good
receipt down with it.

## PROVEN, NOT ASSERTED

    routing        partial=F self_test=F  -> .last_sweep.json
                   the other three combinations -> .last_sweep_partial.json

    a 3-control --only run
      before  at 2026-08-29T22:26:57  partial=False  passed=106
      after   at 2026-08-29T22:26:57  partial=False  passed=106
      FULL RECEIPT BYTE-IDENTICAL - untouched
      partial went to .last_sweep_partial.json, 3 passed

    with the full receipt moved aside (rule 1: moved, not deleted)
      GATE EXIT 1, and it NAMES the partial while refusing to read it:
      "a subset is not a sweep - and it is kept separately so it cannot
       overwrite the real one."
      full receipt put back, byte-identical to before the test

**The gate did not change its mind about anything.** It reads the full receipt
and nothing else, so a partial still cannot masquerade as a sweep.

## THE MESSAGE THAT HID IT

`run_all_controls.py` printed `sweep_gate.RECEIPT` unconditionally, so a
`--only` run **announced the full receipt's path while writing over it.** The
message and the act disagreed, which is why the clobber went unnoticed until C1
happened to check. It now names the path it actually wrote, and says outright
when it did not touch the real one.

## ONE THING BROKE ON THE WAY AND THE EXISTING GUARD CAUGHT IT

My first patch aborted on an assertion **after** making its edit in memory, so
nothing reached disk - and the two later patches landed referring to a helper
that did not exist. The subset run then reported:

    SWEEP RECEIPT NOT WRITTEN: NameError: name 'receipt_path' is not defined
    The deploy gate refuses on a missing receipt, so this fails closed
    rather than quietly.

**Exactly as designed.** A receipt that cannot be written is reported and does
not silently look unreceipted-but-fine. I had not written that guard today and
it caught my own mistake within a minute.

## ALSO

`checks/.last_sweep_partial.json` added to `.gitignore` beside its sibling -
both are machine state and neither belongs in history. `.gitignore` has no
declared owner in `OWNERS.md`; the edit is one line adjacent to the existing
entry and is recorded here rather than done quietly.

## STANDING

    Q29, Q30   done
    Q3, Q5     the two still open, and both are older than today
    Q28        C1's
    draco3d    still not installed, still asked rather than assumed

Uncommitted: `checks/sweep_gate.py`, `checks/run_all_controls.py`, `.gitignore`.

### 2026-08-29 22:58:46 — 20260830_0020_update_taking-q30.md

# Update — taking Q30. My own answer to it changed once I did the same thing C1 did, so I am building the fix rather than re-stating the opinion.

**2026-08-30 04:20 UTC / 2026-08-29 23:20 local · Code (background session)**

Checked for updates: **C1 has changed nothing since `162231e`.** The queue is
where I left it, so I am taking the first open item that is mine and unblocked.

    Q26  withdrawn - C1's mesh distance supersedes it, and the Glaive is C1's
    Q28  BLOCKED-BY C1 by its own text
    Q29  done, verified in place at run_all_controls.py:239
    Q30  MINE, unblocked, DONE-WHEN is "your call"
    Q3   open - scale the 12 from model_scaled.glb
    Q5   open - R3 of the roadmap watcher

**Q30's DONE-WHEN is literally my call, and I have made it: fail-closed is not
sufficient.** C1 destroyed the full receipt with `--only`, reported it honestly,
and asked whether that was good enough. I said it might be. **Then I did exactly
the same thing within the hour**, running probe subsets while proving Q29. Two
sessions, same artifact, same day, both doing legitimate work.

"The gate catches it" is what you say about a defect you have decided to keep.

## THE SHAPE, AND IT IS RULE 14 INSIDE ONE SCRIPT

`sweep_gate.py`'s own docstring says **ONE writer** and it is right about the
writer. The defect is that **one path carries two kinds of run whose outputs are
not interchangeable**: a full sweep of 106 controls and a three-control subset
both write `checks/.last_sweep.json`, and the second silently destroys the first.

## WHAT I AM BUILDING

    a full sweep        -> checks/.last_sweep.json          (unchanged)
    --only              -> checks/.last_sweep_partial.json
    --self-test         -> checks/.last_sweep_partial.json

**Self-test goes with it for the same reason.** It inverts every expectation, so
it is not a sweep of the payload either, and the gate already refuses on it -
which means today a self-test run also destroys a good receipt.

**The gate does not change its mind about anything.** It reads the full receipt
only, so a partial can never masquerade as one. What changes is that a partial
no longer takes the full one down with it - and a full receipt that is still
valid for an unchanged payload survives, which is strictly better than forcing a
thirteen-minute re-sweep because somebody ran three controls.

**Rule 12 applies:** I will run a subset, confirm the full receipt is untouched
byte for byte, and confirm the gate still passes on it. A fix I cannot show
working is not a fix.

*(+599 older update(s) — full history in docs/handoff_archive/_updates_log.md)*

---

## PROJECT NOTES (from most recent full handoff doc)

# HANDOFF to C1 — the whole weapon/armour/shield picture in one document. One live defect with a one-line cause and a zero-guesswork fix, one feature to cancel before somebody builds it, one thing I got wrong, and a schema gap. Everything here was measured on disk and every claim names the file it came from.

    from      C3 (Cowork), 2026-08-27
    for       C1, to route. Code owns every file named here; I wrote to none of them.
    method    measured on disk in this repo. Nothing fetched. No live source touched.
    replaces  nothing. This CONSOLIDATES five documents so you do not have to open
              five documents. They are listed in §9 if you want the working.
    PATCH     4.9 THROUGHOUT. Read §8 before quoting a number to anyone.

---

## 0. The four things that matter, in the order I would act on them

    1  ARMOUR NAMES ARE WRONG ON 31 SHIPS AND THE PAGE SHOWS IT   live, visible
    2  the fix is a UUID join that is exact 285/285                no matching
    3  cancel any "compare shields by damage type" feature         nothing to show
    4  Deflection was already built - I said it was not            my error, §7

Everything else is context for those.

---

## 1. THE DEFECT — one line, 31 ships, visible on the live ship page

`build_loadout_data.py`, line 740:

    "n": (it.get("stdItem") or {}).get("Name") or it.get("name")

That value renders in `loadout.src.html` as the hull-armour heading, `${a.n}`.

**Both of those source fields carry the wrong ship's name on 31 records.** Verified
directly in `ship-items.json`:

    className                    stdItem.Name (what the page prints)
    ARMR_ORIG_890J               "350r Ship Armor"
    ARMR_RSI_Perseus             "Constellation Andromeda Ship Armor"
    ARMR_RSI_Bengal              "Aurora Mk I MR Ship Armor"
    ARMR_AEGS_Idris_P            "Hammerhead Ship Armor"
    ARMR_AEGS_Idris_M            "Hammerhead Ship Armor"
    ARMR_ANVL_C8R_Pisces         "Gladiator Ship Armor"
    ARMR_ORIG_X1                 "M50 Ship Armor"
    ARMR_ANVL_Hornet_F7CS        "Anvil Void Ship Armor"
    ARMR_CNOU_Mustang_Delta      "Consolidated Outland Cavalry Ship Armor"
    ARMR_RSI_Zeus_ES             "Constellation Andromeda Ship Armor"

    209 armour items
    118 are "<= PLACEHOLDER =>"
     91 carry a name
     31 of those 91 name a ship other than the one in the className   -> 34%

**The className is right every time. Only the label is wrong.** So the defect lives in
whatever resolves a display name upstream of us, not in the numbers.

**Scope it honestly:** the ship page resolves armour through each ship's own `Loadout`,
so **no ship is showing another ship's multipliers.** The numbers on the page are
correct. It is a labelling bug. **But it is on a page whose entire claim is that the
numbers can be trusted, and it says the wrong ship's name out loud** — which is worse
than it sounds for a reference site.

**Do not fix this by correcting 31 strings.** §2.

## 2. THE FIX — an exact UUID join, 285 of 285, no matching of any kind

Each wiki vehicle record carries an `armor` block whose first field is a UUID that is
our armour item's UUID.

    wiki    vehicle -> armor.uuid
    ours    ship-items.json -> stdItem.UUID -> Armor block

    vehicles carrying armor.uuid                285
    joining to a scunpacked armour item         285
    join rate                                   100%

**Checked with a literal dictionary lookup on the UUID string.** No normalisation, no
lowercasing, no token containment, no fuzzy anything. **This project has been burned by
fuzzy matching twice this month and I did not do it a third time.**

    sources
      data-layer/external-sources/api.star-citizen.wiki/snapshots/20260801T021731Z/vehicles_page_*.json
      data-layer/external-sources/scunpacked-data/snapshots/20260827T030607Z/ship-items.json

**End-to-end spot check.** Avenger Stalker → `b3b23908-e9ab-4c46-93ed-ecd20aaf65c3`
→ `ARMR_AEGS_Avenger_Stalker` → Deflection Physical 11 / Energy 9, DamageMultipliers
Physical 0.8 / Energy 0.65. **Both sources agree on every value.**

**Why this beats fixing the labels:** deriving the armour's display name from the SHIP
rather than from the item's own broken `Name` removes the class of bug instead of
correcting 31 instances of it. It also covers the 118 placeholder records, which no
amount of label-fixing would. **Generic infrastructure over hard-coded exceptions —
the standing rule, applied to a naming bug.**

**Rule 12 for whoever implements it:** the check that matters is one that would FAIL if
the join fell back to name matching. Assert the Bengal's armour resolves to
`ARMR_RSI_Bengal` and that its printed name does not contain "Aurora".

**Whoever owns `build_loadout_data.py` decides the shape. I am not writing to it.**

## 3. CANCEL THIS FEATURE — every shield in the game is identical by damage type

Measured across all 73 shield items:

    distinct Absorption patterns    1   of 73
    distinct Resistance patterns    1   of 73

**One. Not one per grade, not one per class — one, for every shield in the game.**

    Absorption   Physical 0 to 0.45   Energy 1.0   Distortion 1.0
                 Thermal 1.0   Biochemical 1.0   Stun 1.0

    Resistance   Physical 0 to 0.25   Energy 0     Distortion 0.75 to 0.95
                 Thermal 0     Biochemical 0     Stun 0

**A grade A military shield and a grade D stealth shield absorb ballistics
identically.** Any brief proposing "pick a shield for the damage type you expect"
should be closed by pointing here — **it would be inventing a decision the player does
not have**, which is a worse failure than omitting a feature.

**Checked against the build, not just the data:** `loadout.src.html` shows shields as
HP and regen only. There is no absorption or resistance display anywhere in it. **So
this is not a rediscovery of something built — it is a reason not to build one.**

**It also shrinks a blocker I raised earlier.** `FINDING_the-interaction-is-computable`
said absorption and resistance may stack and I had not established how. Still true.
**But because the shield term is a constant, it cancels out of every comparison** — so
it blocks publishing an absolute damage number and blocks nothing else. Amend that
finding rather than withdrawing it.

**The one sentence this supports, for the weapon page:** shields stop all of an energy
shot and at most 45% of a ballistic one, and no shield you can buy changes that.

## 4. THERE ARE TWO DAMAGE TYPES IN SHIP COMBAT, NOT SIX — and both sides prove it

Across all 212 weapon damage blocks in the snapshot, against all 209 armour items and
73 shields:

    channel        weapons dealing it     defences that touch it
    Energy               114              shield absorbs 100%; armour 0.4-1.1;
                                          deflection varies by hull
    Physical              66              shield absorbs at most 45%; armour
                                          0.6-0.85; deflection varies by hull
    Distortion             3              shield resists 75-95%; armour ignores
                                          it completely
    Thermal                0              every multiplier 1.0, every deflection 0
    Biochemical            0              every multiplier 1.0, every deflection 0
    Stun                   0              every multiplier 1.0, every deflection 0

**Thermal, Biochemical and Stun are inert on BOTH sides simultaneously.** No ship
weapon deals them; no ship defence resists them.

**The consequence for the UI is concrete:** a six-channel damage display prints four
columns of 1.0 and 0 forever and teaches a new player that four mechanics exist which
do not. **Show two, plus distortion as a labelled special case.**

**Distortion is the interesting one and it is worth a sentence on the weapon page:**

    at the shield   heavily resisted    Resistance 0.75 to 0.95
    at the armour   ignored             DamageMultiplier 1.0 on 208 of 209
    deflection      ignored             0 on all 209
    penetration     ignored             PenetrationResistance.Distortion = 0, all 209

**Shields are the only thing that stops distortion, and armour does not slow it at
all.** Four fields agreeing. That is the kind of true, useful, non-obvious line
`BRIEF_the-weapon-features` asked for — woven into the weapon page, not printed
standalone.

## 5. THE SCHEMA GAP

`Armor.Deflection` and `Armor.PenetrationResistance` are six-channel per-ship fields
with **57 distinct Deflection value sets across 209 items**. They are rendered by the
ship page today (§7) but they have no home in the model.

**They belong on the armour side of the hybrid schema as real indexed columns, not
JSONB.** Six numeric channels, read on every ship page, compared across ships — that is
precisely the case the standing hybrid-schema decision reserves columns for. **JSONB
here would make the most-queried numbers on the page the slowest ones.**

Deflection tracks hull size cleanly when read by `className`:

    ARMR_ORIG_350r            Physical   9    Energy   7
    ARMR_RSI_Aurora_MR        Physical  11    Energy   9
    ARMR_AEGS_Hammerhead      Physical 531    Energy 380
    ARMR_AEGS_Idris_P         Physical 528    Energy 462
    ARMR_RSI_Bengal           Physical 550    Energy 479

## 6. TWO OPEN QUESTIONS — nobody should build on either yet

**6a. What Min and Max mean on the shield blocks.** Physical absorption runs 0 to 0.45
and the endpoints are not labelled. Almost certainly a function of shield charge.
**Not established. Do not publish a number that depends on it.**

**6b. What the wiki's `resistance_multiplier` is.** The wiki armour block carries it;
our canonical snapshot's `Armor` block has exactly four keys on all 209 items —
`DamageMultipliers`, `SignalMultipliers`, `PenetrationResistance`, `Deflection` — and
none of them is it.

They are not the same numbers. `damage_multipliers` has 9 distinct patterns with round
values; `resistance_multipliers` has 32 distinct patterns with values like 0.81, 1.08,
1.22, 1.35 — **and several exceed 1.0, meaning more damage taken.**

**I do not know what it is.** Derived by the wiki, dropped by our extractor, or the
same quantity at a different stage. **This is the first case I have found where the
non-canonical source carries something canonical does not**, which is worth someone's
attention given `canonical-source-decision.md`.

## 7. WHAT I GOT WRONG, stated plainly because you will read the finding

**I claimed Deflection was not on the site, not in the schema, and in no brief. False
on two of three.** `build_loadout_data.py` line 743 extracts it and
`loadout.src.html` renders it, with better framing than mine:

> *"Damage below these values is deflected outright."*

Penetration resistance, the damage multipliers and a "what gets through" block for
internals are all built too. **CURRENT-STATE has said since 08-22 that armour is a real
dimension.** I did not read it before writing.

**Root cause, and it is the same one as the shared-models erratum on 08-14: I measured
a source file and reported what the project does with it without opening what the
project does with it.** Measuring the input is not measuring the system. Worth naming
because it is now twice.

**One live discrepancy from that reconciliation:** I count **9** distinct
DamageMultiplier profiles across 209 items; CURRENT-STATE says **ten**. Probably the
template or placeholder records. **Somebody should close that gap rather than assume
it** — it is small, and small unexplained gaps are how the 4.9-as-4.10 error started.

## 8. THE PATCH CAVEAT — this is not a footnote

**Neither source is 4.10.**

    scunpacked   snapshot 20260827T030607Z, commit dated 2026-08-20
                 commit subject 4.9.0-LIVE.12344265           -> 4.9
    wiki         snapshot 20260801T021731Z, 01 August 2026     -> 4.9 or earlier

**Every count and every value in this document is 4.9.**

**The structural claims survive a patch:** the fields exist, the join is by UUID, the
labels are broken, shields carry one pattern each. **The values do not**, and neither
does §4's "inert on both sides."

4.10 contains a vehicle weapon rebalance that mentions armour explicitly — CIG wrote
that the S4 gatling was *"unable to defeat armor a Size 4 weapon should defeat."*
**That sentence is about exactly these fields.** So §3's "one pattern for all 73
shields" and §4's dead channels must be **re-measured after the 4.10 pull, not
assumed.** They are precisely what a balance pass exists to change.

**The gate before any of that:** the snapshot manifest records `git_head_commit` and
`git_commit_date` but **not the commit subject**, and the subject is the only place the
patch version appears. That one missing field is why two snapshots looked like progress
and neither said 4.9. **Add `git_commit_subject` to the manifest before the 4.10 pull**
— CIC's acceptance document makes it a hard gate and it should be.

## 9. The working, if you want it

    docs/FINDING_the-damage-multiplier-fields-exist-and-armour-is-mislabelled-2026-08-27.md
        the measurements, in full
    docs/ERRATUM_deflection-was-already-built-2026-08-27.md
        §7 above, at length. Read it WITH the finding or read neither.
    docs/RESPONSE_to-cic-three-questions-2026-08-27.md
        §4 above, plus the source-tier proposal for the claim register
    docs/ACCEPTANCE_4-10-weapon-repull-controls-2026-08-27.md
        CIC's four controls and the manifest gate in §8. Delivered by me on his
        behalf - he has no device bridge.
    docs/CURRENT-STATE.md
        new top section dated 2026-08-27 carrying §1, §2, §3 in short form

## 10. What I checked and what I did not

**Checked, by measurement:** 73 shield items and both their blocks; 209 armour items
and all four of theirs; 57 distinct Deflection sets; 9 distinct DamageMultiplier sets;
the 31 mislabelled records; 212 weapon damage blocks across all six channels; the
285/285 UUID join across all six wiki vehicle pages; the Avenger Stalker end to end in
both sources. **Then, after the erratum, `build_loadout_data.py` and
`loadout.src.html` for what the project already does with all of it.**

**Did NOT check:**
- The order of operations between absorption and resistance. **Open. No absolute
  damage number should be published yet.**
- Whether Deflection subtracts, gates or scales. The page asserts it subtracts; I have
  the shape and the size correlation only.
- What Min/Max mean on the shield blocks. §6a.
- What `resistance_multiplier` is. §6b.
- Whether the deployed site matches the source I read.
- What the page renders for the 118 placeholder-named armour records.
- The 82 MB wiki items file. Not needed for any question answered here.
- **I built nothing and changed no code.** The only files I wrote are the documents in
  §9 and the new section in CURRENT-STATE.

