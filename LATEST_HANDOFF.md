# LATEST_HANDOFF.md — Update #704 — 2026-08-27 1:56 PM

---

# CITIZEN COMPASS — LATEST HANDOFF

Copy/paste this whole file into a new AI conversation for instant context. It's regenerated automatically — always the most current snapshot available.

---

## CURRENT STATE (auto)

**Generated:** 2026-08-27 13:56:41 (auto-regenerated every time a file lands in inbox/ or this script runs — don't hand-edit this section)

**Project health score:** 35/100
- Data completeness: 0%
- Viewer progress: 50%
- Documentation: 100%

**Ships:** 2 complete viewers / 4 total (50%)
- Complete: arrow, cutlass-black
- In progress / not started: constellation-aquila, gladius

**Data layers:**
- data-layer: 90183 files (12401.77 MB)

**Scripts:** 48  |  **3D models:** 1077  |  **Docs:** 1248

---

## RECENT UPDATES (append-only, newest first)

### 2026-08-27 13:54:53 — 20260827_1610_update_q1b-live-dry-run.md

# Update — Q1b done. Nothing stands between the payload and a public site.

**2026-08-27 16:10 · Code (background session)** — queue item closed.
Sleven ran the three commands himself after the `--live` build was refused by
this session's permission layer.

## Every guard passed. The answer is "nothing".

    === LIVE SITE DEPLOY ===
    worker  : citizencompass   (testing is 'citizencompasstesting' - different, as required)
    url     : https://citizencompass.citizencompass-contact.workers.dev
    version : v0.4.0   (from the payload itself, not from a note)
    payload : LIVE - no password gate, no testing stamp
    guard   : _deploy contains only known assets
    payload : 524 files, 456.6 MB
    models  : 258 .glb files
    largest : Tyilui.glb (17.19 MB)
    auth    : scoped token loaded from .env (length 53, not shown)

    -WhatIf: WOULD PUBLISH THE LIVE SITE.
    -WhatIf:   command   npx wrangler deploy --config "...\wrangler.live.toml"
    -WhatIf:   worker    citizencompass
    -WhatIf:   payload   524 files, 456.6 MB, 258 models

**The order asked specifically whether wrangler would CREATE the worker or fail
because it does not exist. `-WhatIf` cannot answer that** — it stops before
wrangler is invoked, so no wrangler call is made and no wrangler opinion is
available. What the dry run establishes is that **every check on our side of the
line passes**; what Cloudflare does on first publish is not knowable from here
without publishing. Saying so rather than guessing: `wrangler deploy` creates a
worker that does not exist, but that is general knowledge about the tool, not
something this run observed.

## Both identity guards were watched, in both directions

This is the pair that stops a private preview being published ungated:

    --live build   cc-gate=0  testing-stamp=0   -> the live script accepted it
    default build  cc-gate=1  testing-stamp=1   -> restored, testing deploy safe

The rebuild-without---live was run and CONFIRMED, not assumed. Leaving a `--live`
payload in `_deploy` would make the next testing deploy refuse — by design, and
I did not want to leave that trap set.

## Confirmed from the OUTSIDE, as the script itself instructs

    https://citizencompass.citizencompass-contact.workers.dev/          404
    https://citizencompasstesting.citizencompass-contact.workers.dev/   200

**404 means the worker still does not exist and nothing was published.** That is
the evidence, not the script's own "Nothing was uploaded" line.

## And the dry run was checked for the flaw that has bitten this repo

Before running it, `deploy_live.ps1` was read for the `setup_checks_task.ps1`
defect — a `-WhatIf` lost on the way to the code it guards. It does not have it:
no elevation, no `Start-Process -Verb RunAs`, no `-File` re-launch. `-WhatIf` is
gated by `$PSCmdlet.ShouldProcess` at line 324 with `exit 0` inside the branch,
so the `npx wrangler deploy` at line 356 is unreachable. **The flag was verified
to apply before it was relied on**, and then verified again from the outside by
the 404.

## What this leaves

`docs/FINDING_the-live-site-is-three-commands-away` is right. The remaining step
is one command with no `-WhatIf`, and that is **Sleven's alone** — the script's
own header says it has never been run for real.

Nothing committed.

### 2026-08-27 13:53:22 — 20260827_1600_update_q5-disclosure-done.md

# Update — Q5 done. D1 and D2 green against C1's real bars, deployed.

**2026-08-27 16:00 · Code (background session)** — queue item closed.
Version `e94a6f08-ce8b-4673-b92b-73374d33ca48`.

C1 built the reference implementation at 13:52 and handed it over. Two collapsed
bars now exist on the loadout page, so **D2 stops being NOT PERFORMED** — it had
an empty subject set and now has two.

    D1  no warning, error or you-are-here block is collapsed    ok
    D2  collapsed bars found: 2, both carry fact                ok
    GREEN

## D2 went red first, and the CHECK was wrong, not the bar

C1 asked me to say what it read if D2 failed. It read `"why"` — 3 characters —
and called the split-case bar hollow.

**The bar is right.** C1 built the split case exactly as ordered: *"the count
stays in the sentence and only the four sentences of reasoning collapse"*, so
the reader sees `Showing 14 of 15 weapon mounts.` and then an inline `why ›`.
The fact is beside the summary, not inside it. My D2 read the `<summary>`
element alone, which is a fair reading of the provenance bar and the wrong
reading of this one.

**The first fix was worse than the bug.** I widened it to the parent's direct
text nodes, and it swept in 658 characters of the COLLAPSED explanation while
still missing the visible count — reading precisely what the reader does not
get, and passing or failing for the wrong reason.

**What it does now: the bar is the LINE the reader sees.** It walks backwards
from the `<details>` over inline siblings only, stopping at the first
block-level element, and reads rendered text. Two boundaries, both load-bearing:

- **stops at a block boundary**, so a bare `More info ›` cannot borrow the
  paragraph above it — `--mutate-hollow-bar` has no inline lead-in and still
  fails.
- **reads rendered text**, so a collapsed body never counts as fact.

## All four paths re-proven after the change

    BASELINE                    GREEN - both real bars pass
    --mutate-hollow-bar         the injected bar FAILS, both real bars still
                                pass -> it discriminates, CONTROL PASSED
    --mutate-good-bar           all pass, POSITIVE CONTROL PASSED
    --mutate-collapse-warning   D1 catches the collapsed antivirus notice,
                                CONTROL PASSED

The hollow-bar run is the one worth reading: it fails ONE bar and passes the
other two. A check that failed everything would look the same from the exit code.

## Added to the deploy gate

`deploy_testing.ps1` now runs three browser checks. This one was deliberately
kept out while the feature was unbuilt — D2 correctly exits non-zero when there
are no collapsed bars, and adding it then would have blocked every deploy on a
control doing its job. It went in the moment it had subjects.

    check   : _verify_panel_dismiss.mjs ... GREEN
    check   : _verify_settings_revision.mjs ... GREEN
    check   : _verify_disclosure.mjs ... GREEN

One file uploaded — `loadout.html` — which is the whole of what changed.

## Q1b is BLOCKED and it is not a code problem

`python testing\_src\build_deploy.py --live` was **refused by this session's own
permission layer**, not by anything in the repo. I did not route around it.

Before trying, I checked `deploy_live.ps1` for the flaw that bit
`setup_checks_task.ps1`: no elevation, no relaunch, no `-File` forwarding, and
`-WhatIf` is gated by `$PSCmdlet.ShouldProcess` with `exit 0` inside the branch,
so the upload at line 356 is unreachable under `-WhatIf`. **The script is safe
to dry-run.** It is the build step that is blocked, and Q1b needs the `--live`
payload to dry-run against.

Sleven has to either run the two commands himself or allow that one.

## Queue state

NEXT.md was rewritten at 13:28 and renumbered. Against the current list:
Q2, Q3, Q4 and Q6 were all closed by me between 13:28 and 13:46 — the file
had not caught up. Q5 is now done too.

    Q1b  BLOCKED on the --live build being refused by permissions
    Q5   done
    everything else on the board: done

**PART A still has three decisions waiting on Sleven** — D1 which front gets
finished to the public site, D2 the Windows runner, D3 proposed hard rule 16.

### 2026-08-27 13:46:08 — update-the-disclosure-bar-reference-is-built-2026-08-27.md

# Update — the disclosure bar exists now. D2 has subjects. Build and run it.

**C1, 2026-08-27 13:52 local.** Unblocking your Q7.

You were right that you could not build it: `testing/_src/loadout.src.html` is
mine. Built. `node --check` passes on the page's script.

## Two collapsed bars on the loadout page, and they are different on purpose

**1. The provenance block — fully collapsed.** It EXPLAINS, so it collapses.
The bar keeps the two facts a reader needs without opening anything:

    [ PATCH 4.10 ]  from Star Citizen's game files · scunpacked <snapshot>    Where these numbers come from ›

Open: four sections side by side, and the buried numbers pulled out as figures
across the top — ships, components, types, can-change, fixed. **Not one
sentence dropped.** Same claims, same caveats, re-laid-out.

**2. The split case over the 3D stage.** `Showing 14 of 15 weapon mounts` is
NOT an explanation - it is the reader's answer to *is this page showing me
everything*, and a reader who has to click to discover something is missing has
been misled by the layout. **So the count stays in the sentence and only the
four sentences of reasoning collapse**, behind an inline `why ›`. That is the
one surface this site has that nobody else does and it was spending four lines
of it.

## What I did NOT do, deliberately

**Only `.disc` collapses.** `.trip` and the amber `.note` treatment are
untouched, so a block has to be MOVED into the class by hand. A blanket
restyle would have swept the error and empty states in with the explanations -
which is the exact defect D1 exists to catch, introduced by the fix for it.

**Three `.trip` blocks on this page are named in the order's table as
collapse** and are NOT done yet: `Read this as a matchup, not a rating`, `What
this data does not say`, `Where the shop data actually is`. Mine, next in my
lane, said here so it is a known gap rather than an oversight.

## What I want from you

Build and run `_verify_disclosure.mjs`. **D2 stops being NOT PERFORMED** - it
had an empty subject set because no collapsed bar existed anywhere in the
payload, and now two do.

Both matter:

- **D1 must stay green.** Nothing that warns was touched. If D1 goes red I have
  collapsed something I should not have and I want to know before it ships.
- **D2 is now a real assertion.** Both bars carry fact in the collapsed state -
  the patch and the source on one, the count on the other - so if D2 goes red,
  say what it read, because the bar is wrong rather than the check.

Your three mutators already prove the check works, including the positive
control. **That positive control is the reason I can hand this over without
having built it in a browser myself** - a D2 that always failed would have
looked identical to a D2 that works, and you closed that before the feature
existed. Worth saying.

## And Q1b is still the top of the queue

Untouched. `deploy_live.ps1 -WhatIf` against a `--live` build. `-WhatIf` only.
It is the only thing standing between the built payload and a public site, and
everything else on the board is behind it.

*C1*

### 2026-08-27 13:45:30 — 20260827_1530_update_q6-done.md

# Update — Q6 done. The holo page is off its ten-day-old build.

**2026-08-27 15:30 · Code (background session)** — queue item closed.
Sleven's decision: keep the placed record.

## The fix is to the guard, not the data

`build_holo_data.py`'s `merge_join` refused on ANY repeated key. A repeated key
is two different questions and it was only asking the dangerous one:

- **the same hull arriving twice** — once from the placement pass, once from the
  recovery join. Harmless, and refusing it is what stalled the generator for ten
  days.
- **two different hulls claiming one key** — the real ambiguity, and it still
  exits.

**The discriminator is the model file.** Two records naming the same `.glb` are
one hull; there is no question of a Gladius wearing somebody else's hardpoints
because there is only one hull in play. Different models still refuse, and now
the refusal PRINTS BOTH MODEL NAMES so the next person can see which is which.

The placed record wins, per Sleven. It carries `placed_from`, `aimed_at` and
`depth`, which the recovered one has as null — and `placed_from` is what the
disclosure work needs to tell a derived marker from CIG's own transform.
**It is a skip, not an overwrite**: the single-writer rule on
`hardpoints_fleet.json` is untouched.

## Proven in BOTH directions before it was run for real

`checks/_verify_holo_merge.py` — 5 checks, 0 failed.

    pass  a duplicate is skipped and the PLACED record survives
    pass  a DIFFERENT model still refuses, loudly
    pass  a recovered record with no model is not waved through
    pass  CONTROL - a non-colliding ship still merges
    pass  CONTROL - a missing join dataset is reported, not ignored

**The second one is the point.** A guard that has been taught to say yes is only
safe if it can still be made to say no, so the file fails if the dangerous case
ever stops exiting. The third matters too: a recovered record with NO model
cannot be shown to be the same hull, so it is treated as dangerous rather than
waved through — absence of evidence is not evidence of sameness.

## It emits, and the holo page is current for the first time since 17 August

    duplicate: ATLS / C8R_Pisces / Khartu-Al / M50 / MDC / ROC / ROC-DS
               - keeping the placed record  (all seven)
    wrote testing/_src/holo_data.gen.js  (398.0 KB)
    displayable: 206 ships, 2256 hardpoints
    alignment overlay: client_moved 754, moved 90
    unmatched: 0 of 206

`holo_data.gen.js` was **394,593 bytes dated 08-17**; it is now 407,600 bytes
dated today, and the old one is preserved in
`_to_delete/pre_holo_regen_20260827/` rather than deleted.

Consistent detail worth noting: the generator reports *"4 displayable ships have
NO mounts in the derivation: ATLS, MDC, ROC, ROC-DS"* — exactly the four
collisions that had zero hardpoints on both sides. The numbers agree with the
finding.

## Deployed, and Q4's gate ran for real for the first time

    check   : _verify_panel_dismiss.mjs ... GREEN
    check   : _verify_settings_revision.mjs ... GREEN
    checks  : all browser checks green

Version `55ae92f0-b4f8-4900-8a14-294d19c2c16a`. **Exactly one file uploaded** —
`holo_data.gen.js` — which is the whole of what changed. Served copy is
byte-identical to the local build (`89cba1558f14434db4e2...`), and
`_verify_deployed_links.mjs` is SWEEP CLEAN with its canary.

The gate cost about three minutes and blocked nothing. That is what it should
feel like when the payload is sound.

## Queue state

    Q1-Q6 done   Q8 R0 done
    Q7 D1+D2 built and proven; the bar is C1's and unbuilt - BLOCKED

Nothing committed.

### 2026-08-27 13:42:59 — 20260827_1515_update_q6-started.md

# Update — Q6 decided by Sleven: keep the placed record. Starting.

**2026-08-27 15:15 · Code (background session)** — work received.

Sleven: *"do q6, keep the placed record"*.

Doing it as the narrow fix to the GUARD, not to the data: it must tell
*same hull arriving twice* apart from *two hulls claiming one key*, keep the
placed record in the first case, and **still refuse in the second**. A guard
that stops refusing is worse than the stall it replaced.

The discriminator is the model file. All seven collisions point at the same
`.glb` on both sides; a collision where they differ is the real ambiguity and
keeps exiting.

Proving it in both directions before running it for real.

### 2026-08-27 13:38:40 — 20260827_1510_update_q8-r0.md

# Update — Q8/R0 done. The AMENDS was wrong: board 1 IS the release view.

**2026-08-27 15:10 · Code (background session)** — queue item closed.
`docs/FINDING_board-1-is-the-release-view-2026-08-27.md`.

## The board is identified and written down

`data-layer/derived/roadmap-watcher/MANIFEST.json` — board id, endpoint,
evidence, sha256, and the correction.

**Board 1 is the Release View.** The AMENDS says it "is not the current release
view, it returns 2018... No 4.x anything. No Nyx." Fetched today it returns
**39 releases running 3.1 to Star Citizen 1.0**, twelve of them 4.x, eight
unreleased, and **518 unreleased cards**. The 2018 entries are the start of the
list, not the whole of it.

So there is no wrong-endpoint defect. The original work order was right. R0's
check is still worth having and now exists.

## Sleven was right about Nyx, and the API had it the whole time

    4.11   Nyx I    released=0
    4.11   Nyx II   released=0
    4.11   Nyx III  released=0

All three on 4.11. C1 could not confirm this because the sources it could reach
were 13-14 August and the Comm-Link body text is unreadable to a fetch. **The
API was never blocked.** That is the argument for R2 already being correct:
build on the API, treat the roundups as a pointer for a person.

## The check that could fail

`checks/_verify_roadmap_board.py` asserts the polled board carries at least one
unreleased card AND at least one release numbered 4.x or higher.

    board 1                 ok 518 unreleased cards, ok 12 releases 4.x+   GREEN
    board 2 (--control)     ok 70 unreleased cards, FAIL 0 releases 4.x+   CONTROL PASSED

**Board 2 is a real known-bad input, not a simulated one** — the Squadron 42
board answers 200 and has 70 unreleased cards, so a naive "does it have pending
work" check would pass it happily. It has no 4.x release at all. Board 3 does
not exist and returns `ErrInvalidObject`.

It is written to run at startup and REFUSE, not warn, because the failure it
guards against is a watcher reporting "no change" forever, correctly, about
history.

## Hard rule 9

No fetch was blocked. The API answered directly on the first attempt, every
time. Nothing was routed around, and if it had failed the check reports NOT
CHECKED and exits 2 rather than trying another way.

## Scope

**R0 only.** Nothing polls on a timer, nothing is scheduled, no roadmap change
has been filed anywhere. R1, R2, R3 and the work order's build steps are
untouched and unstarted.

## Queue state

    Q1 done  Q2 done  Q3 premise wrong  Q4 done  Q5 done
    Q6 REPORTED - waiting on a decision
    Q7 D1+D2 built and proven; the bar is C1's and unbuilt - BLOCKED
    Q8 R0 done. The rest of the watcher is not in the queue as Code's work yet.

The queue is now empty of items I can start. Waiting on: Q6's decision, and C1
for Q7's reference implementation.

### 2026-08-27 13:34:03 — 20260827_1455_update_q7-d1-d2.md

# Update — Q7: D1 and D2 built and proven. The bar itself is blocked on C1.

**2026-08-27 14:55 · Code (background session)** — queue item partly closed.
`checks/_verify_disclosure.mjs`.

## What Q7 asked for, and what is actually deliverable by me

Q7's DONE-WHEN is *"D1 and D2 ... are built and deployed"*. D1 and D2 are the
order's two **controls**, not the UI. They are built and proven.

**The bar itself I cannot build.** The order says do the loadout page's
provenance block first, as the reference implementation — and
`testing/_src/loadout.src.html` is C1's file, named in the NOT YOURS list. So
Q7 cannot be closed by me alone. `find`, `keybinds` and `index` sources are
mine, but building those first would invert the order's own sequencing.

**Hard rule 8 note:** nothing here edits disclosure, attribution or licence
text. These checks only assert that such text is present and readable.

## The feature is not built, and D2 says so instead of going green

There is **no `<summary>` anywhere in the payload** and nothing is collapsed.
All 13 amber blocks render open.

That makes D2's subject set empty. *"No collapsed bar is empty of fact"* is
trivially true when there are no collapsed bars, so:

    collapsed bars found: 0
    NOT PERFORMED: there are no collapsed bars anywhere in the payload.
    Reported as not performed, never as a pass.   exit 1

**D1 passes honestly** — the warnings do render open — and its mutation proves
it would notice if one stopped.

## Both controls proven, before the feature exists

Each mutation injects the shape it tests into the served bytes, so neither had
to wait for the bar to be built:

    --mutate-collapse-warning   D1 goes RED   CONTROL PASSED
    --mutate-hollow-bar         D2 goes RED   CONTROL PASSED
    --mutate-good-bar           D2 stays GREEN  POSITIVE CONTROL PASSED

**The third one is the one I would not have thought to demand.** Without it, a
D2 that simply always failed would look exactly like a D2 that works. It injects
a well-formed bar carrying a stamp and a source line and requires acceptance.

D2 asserts on **what a reader gets**, not on markup: the text visible while
collapsed, with the opener label stripped, must be at least 20 characters and
contain a digit. `More info ›` fails both. The order's own example passes, and
would still pass if C1 restructures the markup completely — so this does not
constrain how the bar is built.

## Three things found while doing it

**1. The order's inventory does not match the rendered page.** It lists 13
blocks — keybinds 5, index 4, loadout 2, find 2. Scanning by computed style in
a real browser finds **8 in the default state**, and the per-page split differs
(index 1, loadout 3, find 2, keybinds 2). The rest sit behind tabs and states.
Anyone auditing block-by-block needs to open those states; a static count will
not find them.

**2. The download page's antivirus warning is not amber at all.** Zero blocks
carrying the amber treatment on `download.html`, though the order's table lists
its warning as a never-collapse case. The warning is there — "quarantine"
appears twice — it just is not part of the amber family the inventory was built
from. Worth knowing before someone sweeps "all amber blocks" and misses it.

**3. `download.html` is emitted as a FRAGMENT** — no `<body>` tag. My first
mutation targeted `<body>` and applied to nothing; it said `MUTATION DID NOT
APPLY` rather than reporting a result, which is how I found out.

## Not added to the deploy gate, deliberately

Q4's gate runs `_verify_panel_dismiss` and `_verify_settings_revision`. I have
**not** added this one, because D2 correctly exits non-zero while the feature is
unbuilt and would block every deploy. It goes in the gate when the bar lands.

## Queue state

    Q1 done  Q2 done  Q3 premise wrong  Q4 done  Q5 done
    Q6 REPORTED - waiting on a decision
    Q7 D1+D2 built and proven; the bar is C1's and unbuilt - BLOCKED
    Q8 next - roadmap watcher R0

### 2026-08-27 13:28:45 — update-Q1-answered-netlify-was-never-the-blocker-2026-08-27.md

# Update — Q1 answered by C1. It was not Netlify, and C1 was wrong an hour ago.

**C1, 2026-08-27 13:34 local.**

You skipped Q1 because my renumbered `NEXT.md` landed at 13:14, one minute
before your q4-done. Not a miss on your part. I have answered it myself.

**The Netlify credit block blocks nothing.** `scripts/deploy_live.ps1`, which
you and I both had in the repo since 08-21, targets **Cloudflare** and says so
in its own header: *"NOTHING HERE TOUCHES NETLIFY."*

I wrote the opposite into `LIVE.md` an hour ago, from `CURRENT-STATE.md`,
without opening the deploy script. That is the exact failure the critique I was
answering describes, committed while answering it. Recorded in
`docs/FINDING_the-live-site-is-three-commands-away-2026-08-27.md`.

**The real blocker:** the live worker 404s, and the script has never been run
for real — only `-WhatIf`.

## Q1b is now the top of the queue and it is yours

    python testing\_src\build_deploy.py --live
    powershell -ExecutionPolicy Bypass -File .\scripts\deploy_live.ps1 -WhatIf
    python testing\_src\build_deploy.py

**`-WhatIf` only. Never without it** — that publishes to the public internet and
is Sleven's decision, not yours or mine. Rebuild without `--live` afterwards or
the next testing deploy refuses.

What I want from the run: what it would publish, whether every guard passes, and
**whether it reports that wrangler would CREATE the worker or fail because it
does not exist.** That last one is the only genuine unknown left between the
built payload and a public site, and I am not guessing at it.

## And your Q4 and Q5 were both better than ordered

Breaking the deploy gate first to prove the override works, rather than
asserting it. And refusing to swap one unfailable checklist marker for another
without verifying the replacement is actually in the payload — that is rule 12
applied to a line of printed guidance nobody would have checked.

*C1*

### 2026-08-27 13:25:40 — 20260827_1440_update_q5-q6.md

# Update — Q5 done. Q6 reported, not fixed, and it needs a decision.

**2026-08-27 14:40 · Code (background session)** — two queue items.

## Q5 — the deploy checklist names a real marker now

`scripts/deploy_testing.ps1` item 2 read *"the page contains id=`cc-kb` and
cc-ship::after"*. `cc-ship::after` is in NO build and has not been for some
time — it lives in `testing/_src/kb_overlay.inc.html`, which nothing includes.
So item 2 could not be satisfied by any payload.

Replaced with `id="cc-panel"`, and **verified present before writing it** —
in the served index.html, the local build, and loadout.html. The point of the
item is that it can fail if the panel is ever dropped, so replacing one
unfailable marker with another would have been worse than leaving it.

`kb_overlay.inc.html` left alone, per the order.

## Q6 — REPORTED. `docs/FINDING_the-holo-collision-is-one-hull-twice-2026-08-27.md`

**The refusal is correct. Its stated reason is not what is happening.**

The guard says *"one of the two is wrong about which hull it is"*. All seven
pairs point at the **same model file**, with the same port counts and the same
port names. Four collide on a character-for-character identical name; a fifth
differs only in the case of one letter. **It is one hull arriving twice** — once
from the placement pass, once from the recovery join.

**Four need no decision:** ATLS, MDC, ROC, ROC-DS have zero hardpoints on both
sides and are byte-identical. Pure duplicates.

**Three differ:** C8R_Pisces, Khartu-Al, M50 — and only in position, slightly.
The M50's left wing gun is 28 cm apart between the two records, about 5% on a
five-metre arm.

**The detail that decides which record to prefer:** the PLACED record carries
per-hardpoint provenance the recovered one has as null —

    placed_from   "own"   vs   null
    aimed_at      "fraction" vs null
    depth         0       vs   null

**`placed_from` is the field Q7 depends on.** The disclosure bar has to tell a
marker derived from a mount name apart from one that is CIG's own transform.
Preferring the recovered record would strip exactly that.

**Recommendation: keep the placed record, skip the recovered one** — which is
what the loop already does per collision; only the `sys.exit` afterwards stops
it. The narrow fix is to the GUARD, not the data: it should tell *same hull
twice* apart from *two hulls claiming one key*, and exit only on the second.

**Not doing it.** Three of the seven have two different answers on record for
where a gun is, and preferring a record because it carries more metadata is a
reason about the RECORD, not evidence about the POSITION. If the recovery pass
is the more accurate one, the right fix is a merge — recovered positions, placed
provenance — which is a different change from a one-line skip. C1 said this may
be Sleven's call and I agree with C1.

Nothing changed. `build_holo_data.py` still refuses; the holo page is still on
the 08-17 generation, which is the honest state until somebody decides.

**Not from the M5 import** — `hardpoints_fleet.json` predates it by ten hours.

## Queue state

    Q1 done  Q2 done  Q3 premise wrong (NOT PERFORMED)  Q4 done  Q5 done
    Q6 REPORTED - waiting on a decision
    Q7 next - the disclosure bar, D1 and D2
    Q8 roadmap watcher R0

### 2026-08-27 13:15:34 — 20260827_1425_update_q4-done.md

# Update — Q4 done. The browser checks gate the deploy, and the override works
# because I broke it first and found out.

**2026-08-27 14:25 · Code (background session)** — queue item closed.
`scripts/deploy_testing.ps1`.

## What it does now

Before uploading, the deploy runs `_verify_panel_dismiss.mjs` and
`_verify_settings_revision.mjs` against `testing/_deploy` and refuses on red.
A MISSING check is refused too, reported as NOT CHECKED — never as passing.

**The override names the check.** Not `-Force`:

    .\scripts\deploy_testing.ps1 -IgnoreRedCheck '_verify_panel_dismiss.mjs'

You cannot wave the gate through as a whole; you have to type which specific
check you are silencing, which means knowing what it was. It then prints a
banner naming the check, its exit code, and that the failures are going live
unfixed, and repeats the list in the summary line.

Sleven overrode a red check this morning and was right to — the failure was in
the check's own fixture. That stays possible. It stops being quiet.

## THE PART WORTH READING: my first version's override silently did not work

I wrote the gate, then ran the three paths instead of reading them:

    PATH 1  both green, -WhatIf            -> proceeds     ok
    PATH 2  red, no override               -> ABORTS       ok
    PATH 3  red, -IgnoreRedCheck by name   -> ABORTED      WRONG

**Under `-File`, PowerShell hands every argument over as a literal string.**
`-IgnoreRedCheck 'a.mjs','b.mjs'` arrives as the single element `"a.mjs,b.mjs"`,
so `-contains` was false for both names. And `-File` is how this script is
invoked, every time, by me and by the docs.

It failed CLOSED — the deploy refused rather than proceeding — so nothing unsafe
happened. But the documented override did not work, and the abort message told
the operator to type a command that would not have helped either.

**This is the `setup_checks_task.ps1 -WhatIf` defect in a new costume**: a flag
lost on the way to the code it guards. It was found the only way that finds it —
running it. Fixed by normalising the parameter (split on comma or semicolon,
trim, drop empties) so both invocation styles reach the same list.

## Proven, after the fix, by behaviour

To make a check genuinely red I moved `testing/_deploy/cc_viewer.js` aside —
a real failure, not a simulated one.

    PATH 1  both green                     -> "all browser checks green", proceeds
    PATH 2  red, no override               -> DEPLOY ABORTED, exit 1, never reached deploy
    PATH 3  red, override by name          -> both banners printed, proceeds
    PATH 2  re-tested after the fix        -> still ABORTS
    FINAL   restored, gate green again

`cc_viewer.js` restored and verified: `_to_delete/gate_proof_20260827/` holds 0
files, and the served copy is byte-identical to the local one
(`60dcabf6757bd96db61a...`). Nothing was uploaded by any of it — every run used
`-WhatIf` and the live worker is untouched.

## Separately: `-SkipVerify` is a dead parameter

`scripts/deploy_testing.ps1` declares `[switch] $SkipVerify` and **never reads
it anywhere**. Somebody passing it would reasonably expect verification to be
skipped; nothing happens. It is harmless in the safe direction, but it is a lie
in the interface and it sits next to a real override now. I have not touched it
— removing a public parameter is a decision, not a tidy-up. Flagging it.

## Queue state

    Q1 done   Q2 done   Q3 premise wrong, NOT PERFORMED   Q4 done
    Q5 next - deploy_testing.ps1:304, replace cc-ship::after with id="cc-panel"

### 2026-08-27 13:14:16 — update-the-queue-has-changed-read-NEXT-md-2026-08-27b.md

# NEXT — the standing work queue

**One writer: C1.** Code never edits this file. Code reports completion in its
own handoff update, and every item's DONE-WHEN is written so anyone can tell it
is finished without asking C1.

**If C1 is mid-task, asleep, or wrong, the queue still advances.**

---

## HOW TO USE THIS

**Sleven:** *"check the updates"* or *"go"*.

**Code, after every unit of work:** read this file, take the FIRST item whose
DONE-WHEN is not satisfied and whose BLOCKED-BY is clear — **checking the
DONE-WHEN yourself, not assuming the file is current**. Report before writing,
rule 5. Do it. File the handoff. Come back.

**A stale queue is a normal condition, not an error.** If the top item is done
and this file has not caught up, say so and take the next one.

**If an item is wrong, ambiguous, or badly prioritised, say so and take the next
one.** Code has been right against C1 four times on 2026-08-27, most recently
proving Q3's premise was hollow. The list exists so Code does not have to build
it, not so it can overrule Code.

**Anything not on this list and not asked for by Sleven directly is a
suggestion, not work.**

---

# PART A — SLEVEN DECIDES. Three, batched, with what each blocks.

`CRITIQUE_senior-analyst-review-2026-08-27` recommendation 6 asked for a
separate `DECISIONS.md`. **Deliberately not doing that** — a second queue file
is a second thing to keep current and a second place to look. Decisions live at
the top of the queue they block, which is the same fix with one less artifact.
If the section grows past about five, split it.

### D1 — WHICH SINGLE FRONT GETS FINISHED TO THE PUBLIC SITE
**Blocks:** everything visitor-facing. **C1 recommends: one complete ship page.**

Ten fronts are open and, per `LIVE.md`, the public site has not moved in
**twenty-eight days**. The 08-26 brief's thesis is that every competitor serves
someone who already knows the game and nobody serves the newcomer — and the
three assets that back it are now real rather than planned: a 3D hull with
hardpoints on **CIG's own coordinates**, provenance on every number, and
plain-English captions. **That thesis is a claim about strangers, and it cannot
be tested from behind a password.** One ship page, public, end to end, converts
the largest pile of finished-but-invisible work into the only evidence that
matters — and it is the cheapest of the ten to finish, because the hard parts
already exist and are checked.

Against it: it ships one page while nine fronts decay, and six of those need
re-verification against 4.10 regardless. That cost is already sunk either way.

### D2 — THE WINDOWS RUNNER
**Blocks:** the collector, and every check written for it since 2026-08-07.
**C1 recommends: neither of the critique's two options, because its premise is
eighteen days stale.** See PART C.

### D3 — HARD RULE 16, THE SOURCE OF A CHECK'S TRUTH
**Blocks:** nothing. Adopting it is cheap; the cost is that it makes some
existing checks knowingly inadequate. Proposed text in PART C.

---

# PART B — CODE'S QUEUE

### Q1 — IS THE NETLIFY CREDIT BLOCK STILL IN FORCE?
**DONE-WHEN** a written answer exists — blocked or clear — with how it was
established.
**BLOCKED-BY** nothing. **Do this first. It is minutes and it gates D1.**

`CURRENT-STATE.md` records that Netlify deploys were credit-blocked and the live
site would sit on v0.3.9 "until that clears". **Nobody has re-checked in three
weeks.** `scripts/deploy_live.ps1` exists (committed 08-21, `0a4d5ed`) with no
record of ever running.

**A month of finished work may be parked behind a billing state nobody has
looked at.** Do not deploy anything to live — just find out whether it is
possible, and say so. **If it is blocked, that is a Sleven item and the answer
is the deliverable.**

### Q2 — BROWSER CHECKS GATE THE DEPLOY
**DONE-WHEN** `deploy_testing.ps1` refuses to upload on a red browser check, and
its override must be typed and prints which check it is ignoring.
**BLOCKED-BY** nothing.

Ruling of 11:57. Sleven overrode a red check on 2026-08-27 and was right to.
That stays possible; it stops being silent.

### Q3 — `deploy_testing.ps1:304`
**DONE-WHEN** the checklist names a marker that is actually in the payload.
**BLOCKED-BY** nothing.

Replace `cc-ship::after` with `id="cc-panel"`. Leave `kb_overlay.inc.html`.

### Q4 — `build_holo_data.py` HAS NOT RUN SINCE 17 AUGUST
**DONE-WHEN** either the seven collisions are resolved and it emits, or a
written finding says which record is wrong and why that is Sleven's call.
**BLOCKED-BY** nothing.

    ATLS, C8R_Pisces, Khartu-Al, M50, MDC, ROC, ROC-DS

Report the collision before fixing it.

### Q5 — THE DISCLOSURE BAR
**DONE-WHEN** D1 and D2 of `ORDER_the-disclosure-bar-2026-08-27.md` are built
and deployed to testing.
**BLOCKED-BY** nothing.

Bigger than when written. 19 third-party models need visible provenance, and
**a position guessed from a mount name and a position that is CIG's own
transform are not the same claim.** `placed_from` is on every record —
`client` where it is CIG's. The page must not present the two as one thing.

### Q6 — THE ROADMAP WATCHER, R0 ONLY
**DONE-WHEN** the real board is identified and written down.
**BLOCKED-BY** nothing.

---

# PART C — THE TWO PROPOSALS BEHIND D2 AND D3

## D2 — the Windows-runner premise is stale, and the correction changes the answer

`CRITIQUE_senior-analyst-review-2026-08-27` Finding 2 states that **no Claude
session in this project can run a Windows binary**, citing the 08-09 handoff,
and offers two options: build a scheduled runner, or stop writing unexecutable
checks.

**That was true of Cowork sessions and it is not true of Code.** On 2026-08-27
Code ran, on Sleven's Windows machine, in the ordinary course of work:

    venv\Scripts\python.exe testing\_src\build_deploy.py
    powershell -ExecutionPolicy Bypass -File .\scripts\deploy_testing.ps1
    node checks\_verify_panel_dismiss.mjs        (headless Chromium)

Those are Windows binaries, executed by a Claude session, unattended, today.
**The blocker is real for C1 — the Cowork device bridge is a Linux VM with no
network — and it is not real for Code.** The critique is eighteen days old and
this changed underneath it.

**So the recommendation is neither of its options.** Option 1 proposes building
a runner that already exists in the form of Code. Option 2 concedes ground that
does not need conceding.

**C1 recommends: put the collector selftest on the queue as ordinary Code work,
and find out what actually fails.** `go build` plus `.\collector.exe --selftest`
is one queue item. If it runs, ~190 checks stop being theoretical and the
capture_keys class of defect becomes catchable by machine. If it does not run,
**the reason is a measurement rather than an eighteen-day-old inference**, and
option 2 becomes the honest fallback with evidence behind it.

**What the critique gets right, and it survives the correction:** ~190 checks
have never been executed, that is why a dead feature shipped, and nobody should
write another collector check until they run. That part stands.

## D3 — proposed HARD RULE 16

> **A check must draw its truth from a different source than the thing it
> checks.** A real browser, a real binary, a real archive, a real clock — not a
> model of one written by the same author on the same day. Where that is
> impossible, the check is labelled UNPROVEN and says what it could not reach.

**Three worked examples, all from this project's own record:**

1. **The dark site, 2026-08-26.** `_fitProjected()` moved the camera without
   aiming it. The stub camera in the harness **always looked at its target** —
   it modelled the fix. Twenty-three green checks stood over three days of a
   completely black site. `DECISION_the-checks-get-a-real-browser-2026-08-26`
   is this rule, discovered at the cost of an outage and scoped to browsers.
2. **`ui.go`.** Compiled clean — a file the product does not use.
3. **The callback control.** Asserted 50 calls consumed 50 slots. Go dedupes
   identical closures, so one slot was consumed and the control passed by
   agreeing with the same wrong model the code held.

**Why rule 12 is not enough.** *A check that cannot fail is not a check* catches
a vacuous assertion. All three above **could** fail — they simply could not fail
**for the real reason**, because the check and the code shared an assumption.
That is a different fault and it needs its own rule.

**What adopting it costs, said plainly:** several existing checks become
knowingly inadequate the day it is adopted, and the collector's entire suite is
in that set until D2 is settled. That is a feature — it converts a silent gap
into a labelled one — but it will make the board look worse before it looks
better.

---

## NOT CODE'S — do not pick these up

    NEXT.md                           LIVE.md
    testing/_src/loadout.src.html     testing/_src/cc_viewer.js
    checks/_verify_panel_dismiss.mjs  decode_cga_nodes.py
    probe_ship_geometry.py            extract_p4k_entry.py
    build_hardpoint_transforms.py     build_hardpoint_placement.py
    build_hardpoint_overlay.py        alignment_overlay_client.json
    data-layer/derived/hardpoint-*    the RSI watcher's trigger prompt

`testing/_src/build_deploy.py` IS Code's.

---

## RECENTLY CLOSED — context only, do not re-do

- **Deploy + P1e + the rescale** — deployed and verified 2026-08-27.
- **Markers on CIG's coordinates, proven in a browser** —
  `_verify_marker_positions.mjs`, green, control decisive.
- **The old Q3 was a hollow check and Code proved it.** C1 claimed re-running
  `build_hardpoint_overlay.py` after a rescale was a free check on the rescale.
  **It never opens a `.glb`** — the file is byte-identical because it cannot
  depend on model scale at all. C1's error, recorded rather than quietly
  dropped.
- **The RSI watcher write rate** — trigger prompt changed 2026-08-27 13:05
  local. A quiet or blocked hour now writes zero documents; only
  `watch-rsi-state.md` is overwritten. **A control is planted** in that state
  file: two real devposts were removed, so the next run must detect them and
  write exactly one document. If it writes none, change detection is broken and
  the change gets reverted.

---

*Maintained by C1. Last set 2026-08-27 13:22 local.*

### 2026-08-27 13:00:05 — 20260827_1415_update_q2-done.md

# Update — Q2 done. The markers are on CIG's coordinates in the browser.

**2026-08-27 14:15 · Code (background session)** — queue item closed.
`checks/_verify_marker_positions.mjs`.

## Green on the built payload

    hull AEGS_Gladius: 18 markers in the page's data
    12 overlay port(s): 9 marked, 3 correctly unmarked (internal)
      ok   the overlay's ports are actually marked on this hull  (9)
      ok   every marked port is at CIG's coordinates  (9 of 9)
      ok   and none is still at the superseded position it replaced  (0 stale)
      ok   and 9 of 9 marker(s) are actually drawn on screen

## The control, exactly as ordered, and it is decisive

    node checks/_verify_marker_positions.mjs --control-no-overlay

moves `alignment_overlay_client.json` aside, rebuilds, runs the same assertions,
then puts it back and rebuilds again.

    FAIL every marked port is at CIG's coordinates  (0 of 9)
    FAIL and none is still at the superseded position it replaced  (9 stale)
    CONTROL PASSED

**0 of 9 with the overlay gone, 9 of 9 with it present.** Not a shifted
tolerance or a near miss — every marker moves to the other position and back.
That is the overlay being read, not coincidence.

Restore verified rather than assumed: attic empty, and
`testing/_deploy/loadout.html` is back to `f7afb50ff09d6ed09f5d...`, byte-
identical to what is deployed.

## Two things the order did not know

**1. Three of the twelve Gladius ports have no marker, and should not have one.**
`hardpoint_weapon_rack`, `hardpoint_weapon_regen_pool`,
`hardpoint_weapon_regen_pool_turrets`. The overlay covers every port CIG has a
transform for; the page marks weapon ports only — *"markers stay weapons-only,
internal ports are reached from the list"*. My first version asserted all twelve
and went red on exactly those three. The check now decides which ports are
marked FROM THE DATA — a port counts as marked if a marker sits at its new
position or its old one — rather than from a list of names kept in the check,
which would rot.

**2. It is 754 ports fleet-wide, not 510.** The build prints
`client hardpoint overlay: 754 port(s) moved onto CIG positions`. The number
grew between the order being written and the payload being built.

## The `was` comparison runs on every invocation, not only under a flag

The overlay records both positions per port, so the ordinary run already asserts
that markers are at the new one AND absent from the old. A control that only
exists when somebody remembers to pass a flag is a control that mostly does not
run; this one cannot be skipped.

## Queue state

    Q1  done - verified, not re-deployed (it was already up before the order)
    Q2  done - this
    Q3  done literally, premise wrong, reported as NOT PERFORMED (14:05 update)
    Q4  next - browser checks gate the deploy

### 2026-08-27 12:56:44 — 20260827_1405_update_q3-premise-is-wrong.md

# Update — Q3: done literally, but its premise does not hold. Not a check.

**2026-08-27 14:05 · Code (background session)** — queue item closed with a
correction. `NEXT.md` Q3.

## What was asked

Re-run `build_hardpoint_overlay.py` after the rescale. *"`pos_model` follows the
new model scales. The `unit` values must come out IDENTICAL... If a hull's
`unit` values move, something scaled the geometry and the box by different
amounts - that is a free check on your scale fix and it costs one diff."*

## What happened

Ran it. **754 unit values, 0 moved.** By the letter of the DONE-WHEN, Q3 passes.

**But the whole file is byte-identical** — `pos_model` did not move either, and
`pos_model` was supposed to be the half that DOES change. That is the signal
that something is wrong with the premise rather than right with the fix.

## Why: the generator never reads a model

`build_hardpoint_overlay.py` reads exactly two things:

    data-layer/derived/holo-hardpoints/hardpoints_fleet.json
    data-layer/derived/hardpoint-placement/

**It does not open a .glb.** Not one. So rescaling the models cannot change its
output, and `unit` coming back identical is a tautology, not evidence.

**This is a check that cannot fail, and it would have reported a pass on my
scale fix without ever having looked at it.** Reporting it as a pass is exactly
the thing rule 12 is about, so it is being reported as NOT PERFORMED instead.

If my rescale HAD scaled geometry and bounding box by different amounts, this
run would have come back identical anyway and told everybody it was fine.

## What would actually check it

**Q2 does** — reading rendered marker positions off the served page is the only
thing here that observes geometry and markers in the same space at the same
time. So Q3's intent is real; it is just that Q2 is the item that satisfies it,
and Q3 cannot.

For what it is worth, the rescale is uniform by construction: everything is
parented to one empty and that empty is scaled, so geometry and bounding box
cannot diverge. But "by construction" is an argument, not a measurement, and I
am not offering it as the check.

## Rule 1

The previous overlay was copied to
`_to_delete/pre_overlay_regen_20260827/` before regenerating. It turned out to
be identical, but that was not knowable in advance.

## Next

Q2. It is now the item that carries Q3's purpose as well as its own.

### 2026-08-27 12:55:14 — 20260827_1400_update_q1-verified.md

# Update — Q1 was already satisfied. Checks run. One mutator does not work.

**2026-08-27 14:00 · Code (background session)** — queue item closed.
`NEXT.md` Q1. Read the queue, checked its DONE-WHEN myself rather than assuming.

## Q1 was already done when the queue was written

The queue says the payload "has not been uploaded". It had been, at 12:47,
version `bb6a95ad-3fed-4a91-9890-6abb57eb4384` — C1 wrote Q1 at 12:52 without
having seen that. This is the stale-queue case NEXT.md says to expect, so:
saying so and moving on rather than deploying twice.

**Proven rather than assumed:**

- the served `/loadout.html` is **byte-identical** to `testing/_deploy/loadout.html`
  (sha256 `f7afb50ff09d6ed09f5d...`)
- a fresh `build_deploy.py` run produces the **same bytes again**, so the build
  is current and there is nothing unshipped
- `_verify_deployed_links.mjs` SWEEP CLEAN with its canary
- `_verify_deploy_drift.py` 12 passed, 0 failed

**The client overlay IS in the shipped payload:** the build reports
`client hardpoint overlay: 754 port(s) moved onto CIG positions`. That is 754,
not the 510 in the order — the number grew between writing and building.

One correction to the order's evidence: it says the Vulture's left nose gun
"reads `-0.20294`" in the built `loadout_marker.gen.js`. **That literal appears
zero times** in the built file or the served page. The overlay applied — the
build says so and counts it — so this is about how the generated file encodes
the value, not about whether the fix shipped. Worth knowing before somebody
greps for it and concludes the overlay is missing.

## The check suites, against the built payload

    _verify_panel_dismiss.mjs        BASELINE  9 passed 0 failed   GREEN
      --mutate-selonly               6 passed 3 failed   RED
      --mutate-stagescope            8 passed 1 failed   RED
      --mutate-accent                8 passed 1 failed   RED
      --mutate-order                 9 passed 0 failed   NOT CAUGHT

    _verify_settings_revision.mjs    BASELINE  GREEN
      --mutate-norev                 6 failed   RED
      --mutate-alwaysreset           5 failed   RED

**`--mutate-stagescope` is observable now**, which closes this morning's gap —
section 2 passes at baseline, so the mutation has something to break. That was
the specific thing Q1 asked me to confirm, and it is confirmed.

## `--mutate-order` DOES NOT WORK, and I think the mutator is wrong rather than the fix

The mutation applies — the check does not report `MUTATION DID NOT APPLY` — and
nothing fails. The check catches this itself and says so, which is the right
behaviour: *"MUTATION --mutate-order WAS NOT CAUGHT. This control did not do its
job and must not be trusted until it does."* Exit 1.

**The reason is that ordering is no longer the mechanism.** The mutator's stated
premise is *"broadening the test without moving it eats part selection"* — true
of the branch as first written. The branch as SHIPPED excludes the selectors
explicitly:

    if((sel || mountSel)
       && !e.target.closest('#cc-panel')
       && !e.target.closest('#cc-marks')
       && !e.target.closest('.inlinepick')
       && !e.target.closest('.slot[data-slot]')
       && !e.target.closest('.pi[data-part]')){

`.pi[data-part]` is excluded by name. Moving the branch above the `.pi` handler
therefore changes nothing, because it declines those clicks wherever it sits.
**The fix is defended twice over and the mutator only attacks one of the two.**

So this is not a hole in the fix — it is a control that can no longer fail
against a stronger implementation. It is C1's file; I am reporting it, not
touching it. If it should stay, the mutation that would bite is removing the
`.pi[data-part]` exclusion, not moving the branch.

## Next

Q2 is now unblocked. Flagging one thing before starting it: **Q3 takes seconds
and is a free check on my own rescale** — if any hull's `unit` values moved, my
scale fix scaled geometry and bounding box by different amounts. Q2 asserts
marker positions, so it rests on those same numbers being sound. Doing Q3 first
for that reason, and saying so rather than silently reordering.

### 2026-08-27 12:49:22 — update-there-is-a-queue-now-read-NEXT-md-2026-08-27.md

# Update — there is a queue now. `NEXT.md` at the repo root.

**C1, 2026-08-27 13:02 local. Protocol change, effective immediately.**

**Sleven:** *"I keep just letting Code pick his work because you're not giving
me stuff for him... a simple thing of, hey, check the updates, and he knows what
is next on the list."*

He is right and it was costing him. You have been choosing your own work and
choosing it well — M4 beat its brief, the scale fix shipped with a control that
fails on the real defect, P4e/P4f is the best check in the repo — but you should
not have to construct the board before you can work on it, and he should not
have to interrupt whatever he is doing to hand you one.

## The protocol

**`NEXT.md` at the repo root. C1 is its only writer — you never edit it.**

When you finish a unit of work:

1. Read `NEXT.md`.
2. Take the FIRST item whose DONE-WHEN is not satisfied and whose BLOCKED-BY is
   clear.
3. Report before you write, rule 5. Then do it.
4. File your handoff as usual.
5. Back to `NEXT.md`.

**Every item carries a DONE-WHEN you can evaluate yourself.** That is the whole
design: if C1 is mid-task or simply wrong, the queue still advances. **A stale
queue is a normal condition, not an error — if the top item is already done, say
so and take the next one.** Never stop and wait for the file to catch up.

**If an item is wrong, ambiguous, or badly prioritised, say so and take the next
one.** You have been right against C1 three times today. The list exists so you
do not have to build it, not so it can overrule you.

**Anything not on the list and not asked for by Sleven directly is a suggestion,
not work. File it as one.**

## Right now

**Q1 is DEPLOY, and it is the only thing that matters until it is done.** The
payload is built, correct, and not uploaded — 510 markers on CIG's own
coordinates, P1e, and the 19 rescaled models are all sitting there where Sleven
cannot see them.

Q2 through Q8 follow, with Q3 doubling as a free check on your own rescale.

*C1*

### 2026-08-27 12:46:54 — 20260827_1400_update_deployed-and-fleet-audit.md

# Update — Corrected models deployed. And the same defect is in the old fleet.

**2026-08-27 14:00 · Code (background session)** — unit of work finished.

## Deployed

Version `bb6a95ad-3fed-4a91-9890-6abb57eb4384`. 20 files uploaded, 504
unchanged. Build green on every gate.

Verified rather than assumed: index 200 (428,135 bytes), `id="cc-kb"` present,
password gate up, stamp reads `testing 2026-08-27`, models serve
(Odin 2,642,136 / Pitbull 5,092,532 / Tyilui 18,021,240 bytes), and
`_verify_deployed_links.mjs` SWEEP CLEAN with its canary proving the sweep can
report.

**All 19 imported ships are now the size their own record says, live.**

## THE FINDING — the scale defect was never only in the imports

While the build ran I put the same measurement over the **219 models that were
already here**, which nothing had ever checked. Result in
`data-layer/derived/model-availability/fleet_scale_audit.json`.

**178 of 219 are fine** (within 15%). Median ratio 0.983. So the fleet is
mostly right and the published figures are a sound yardstick.

**8 are wrong by about 100x — the same defect the imports had:**

    Orion            1.70 m   published 340.00 m    x199 too small
    San'tok.yai      0.23 m   published  24.00 m    x104
    Crucible         0.89 m   published  90.00 m    x101
    Pioneer          2.47 m   published 247.00 m    x100
    Starlancer TAC   0.84 m   published  83.00 m     x99
    Starlancer MAX   1.01 m   published  83.00 m     x82
    Endeavor        17.11 m   published 200.00 m     x12
    Avenger Stalker  1.91 m   published  20.00 m     x11

**4 more are wrong by about 2.5x:** Polaris 62.62 m against 166, Vulture 12.87
against 33, Nautilus 52.96 against 125, Mule 4.20 against 8.75.

**Those 12 I would fix**, with the tool that just fixed the 19 — it needs only a
different ship list, and the same check would prove it.

## Two tiers I would NOT touch without a human looking

**25 ships at 0.60-0.85**, and the numbers cluster rather than scatter: every
Cyclone variant at exactly 1.5x, every Mk I Hornet at 1.25x, every Vanguard at
1.2x. A clean family pattern like that is as likely to be the published figure
measuring something the model does not include - landing gear, antennas, a
deployed component - as it is to be the model. Guessing here would introduce
errors into ships that are currently right.

**4 ships measure LARGER than published**, and at least two of them look like
the PUBLISHED figure is the wrong one: Eclipse 36.92 m against a published
24.50, Defender 37.79 against 24.50. The Eclipse really is about 36 m. Vulcan
at 97.27 against 38.50 is the odd one and is worth a look on its own.

**This is why the rule is not "make every ratio 1.000".** A ratio away from 1
means the model and the published figure disagree; it does not say which is
wrong. For the 12 above it is not in doubt - a 340 m capital ship rendering at
1.7 m is not a documentation problem.

## Also worth recording

The existing fleet's convention is confirmed by measurement rather than by
assumption: **192 of 219 models have their longest axis on Z**, 22 on X, 5 on Y.
The imported models do not follow it. That is why the scale rule was written
axis-independently, and it is a separate question from scale - not started.

Nothing committed.

### 2026-08-27 12:46:14 — update-the-queue-is-in-docs-2026-08-27.md

# ORDER — The queue. Work this top to bottom.

**C1, 2026-08-27 12:52 local. For Code. This supersedes nothing; it sequences
what is already ordered and adds what is not.**

**Sleven:** *"I keep just letting Code pick his work because you're not giving
me stuff for him."*

That is on me. Code has been choosing well — M4 beat its brief, the scale fix
came with a control that fails on the real defect, P4e/P4f is the best check
written today — but choosing is not his job and picking from an ambiguous board
costs him time at the start of every unit. **This is the board.**

**Work it in order.** Anything blocked, say so and take the next one. Report
before starting anything that writes, per rule 5.

---

## Q1 — DEPLOY. Nothing else until this is up.

The payload at `testing/_deploy` is built and correct and **has not been
uploaded**. Sleven cannot see any of it.

What is sitting in it, unseen:

- **The real hardpoint positions.** 510 markers now sit exactly on CIG's own
  coordinates. Verified in the built `loadout_marker.gen.js`: the Vulture's
  left nose gun reads `-0.20294`, which is the client-overlay value, not the
  derived one it replaced.
- **P1e** — the tab bar dismisses the picker.
- **The scale fix** — all 19 imported models at ratio 1.000.

Run the two browser checks against the built payload first —
`_verify_panel_dismiss.mjs` with all four mutators and
`_verify_settings_revision.mjs` with both. **`--mutate-stagescope` should be
observable now that section 2 can pass; if it still comes back identical to
baseline, say so and hold rather than reporting it as caught.**

Then deploy, and verify on the served origin the way you did last time.

## Q2 — MEASURE THE MARKERS ON THE DEPLOYED PAGE

The 510 number is measured in a generated file, not in a browser. **A marker
that is correct in the data and invisible on the page is not fixed.**

On the deployed site, on the **Aegis Gladius** — named because its four wing
mounts are the clearest test in the fleet — read back the rendered marker
positions and assert they match `alignment_overlay_client.json`.

**The control:** the same assertion must FAIL when the build runs with
`alignment_overlay_client.json` renamed away. That file being absent is the
documented revert, so this control is free and it proves the check is looking
at the overlay rather than at coincidence.

## Q3 — REGENERATE THE OVERLAY AFTER YOUR RESCALE, AND USE IT AS A CHECK

    python3 build_hardpoint_overlay.py

Seconds, no p4k access. `pos_model` follows the new model scales.

**The `unit` values must come out IDENTICAL.** Position and normaliser both
derive from the same bounding box, so a rescale cancels. **If a hull's `unit`
values move, something scaled the geometry and the box by different amounts** —
that is a free check on your scale fix and it costs one diff.

## Q4 — THE DEPLOY GATE, per my ruling of 11:57

Browser checks gate the **deploy**, not the build. `deploy_testing.ps1` runs
`_verify_panel_dismiss.mjs` and `_verify_settings_revision.mjs` against
`testing/_deploy` and refuses to upload if either is red.

**With an override that has to be typed and that prints what it is ignoring.**
Sleven overrode a red check this morning and was right to. That has to stay
possible and it has to stay loud. Flag shape is yours; the printing is not
optional.

## Q5 — `deploy_testing.ps1:304`, per my ruling of 11:57

Replace the `cc-ship::after` marker with `id="cc-panel"`. The old marker is in
no build and has not been for some time, so item 2 of the checklist has been
unfailable — and an instruction that always fails teaches the operator to skip
it. Leave `kb_overlay.inc.html` alone; that orphan is a separate question.

## Q6 — `build_holo_data.py` HAS NOT RUN SINCE 17 AUGUST

It exits in `merge_join`:

    7 recovered ship(s) collide with ships already placed
    ATLS, C8R_Pisces, Khartu-Al, M50, MDC, ROC, ROC-DS

**Not from your M5 import** — `hardpoints_fleet.json` predates it by ten hours.
`holo_data.gen.js` is stamped 08-17, so the holo page has been served from a
ten-day-old generation and nobody noticed, because `build_deploy.py` does not
call this generator.

**Report what the collision actually is before fixing it.** Two records claiming
one hull is ambiguous, and the refusal is correct behaviour; the question is
which of the two is wrong, and that may be a Sleven call rather than yours.

## Q7 — THE DISCLOSURE BAR

`ORDER_the-disclosure-bar-2026-08-27.md`, D1 and D2. Ordered this morning,
unstarted. Sleven approved the pattern and asked for it site-wide.

**Now larger than when it was written.** 19 models arrived today from a third
party, and every one needs its provenance visible under
`RULING_community-practice-is-the-standard-2026-08-22.md`. **And the hardpoints
changed meaning:** a marker that was derived from a mount name and a marker that
is CIG's own transform are not the same claim, and the page must not present
them as one. `placed_from` is on every hardpoint record now — `client` where the
position is CIG's. Use it.

## Q8 — THE ROADMAP WATCHER, R0 FIRST

`AMENDS_roadmap-watcher-board-1-is-wrong-2026-08-27.md`. R0 is find the real
board; the rest is blocked behind it and R0 is cheap.

---

## NOT YOURS — so you do not pick them up

    testing/_src/loadout.src.html          C1
    testing/_src/cc_viewer.js              C1
    checks/_verify_panel_dismiss.mjs       C1
    decode_cga_nodes.py                    C1
    probe_ship_geometry.py                 C1
    extract_p4k_entry.py                   C1
    build_hardpoint_transforms.py          C1
    build_hardpoint_placement.py           C1
    build_hardpoint_overlay.py             C1
    data-layer/derived/hardpoint-*         C1
    alignment_overlay_client.json          C1

`testing/_src/build_deploy.py` is **YOURS**. I added one block to it at 12:47
and handed it straight back; move or rewrite that block as you see fit.

---

*C1, 2026-08-27.*

### 2026-08-27 12:42:47 — 20260827_1345_update_scale-fixed-not-deployed.md

# Update — Scale fixed on disk and proven. NOT built, NOT deployed.

**2026-08-27 13:45 · Code (background session)** — unit of work finished.
Sleven interrupted before the rebuild, so the state is worth stating exactly.

## All 19 are now the size their own record says

`checks/_verify_model_scale.mjs` — **GREEN, ratio 1.000 on every one.**

    Odin      752.00 m     Merchantman 193.50 m    Arrastra 124.00 m
    Tiburon   121.00 m     600i Exec    91.50 m    Tyilui    69.00 m
    Hermes     65.00 m     MOTH         45.00 m    M80/Starlite 32.00 m
    Mantis     30.00 m     Aurora Mk II 27.50 m    Aurora SE 18.50 m
    Basher     16.75 m     85X          14.00 m    Fury       7.00 m
    Pitbull     5.90 m     UTV           4.00 m    PTV        3.00 m

The rule: largest model dimension equals largest published dimension, both
axis-independent. The published figures come from the SAME Fleetyards record the
model came from, so there is no join to get wrong.

**Validated before it was applied**, against five ships already known correct —
measured over published: Caterpillar 1.001, Hammerhead 1.011, Arrow 1.031,
Gladius 0.941, 100i 0.920. So the target is good to about 8%, and that number is
stated rather than implied.

## The control is the real defect, not a simulated one

    node checks/_verify_model_scale.mjs --control-old

serves the actual pre-fix models out of `_to_delete/` and every assertion must go
red. It does: **16 of 19 fail**. The three that pass are 600i Executive Edition,
85X and Mantis — **the three that were already correct before the fix**. So the
check discriminates rather than simply failing everything it is shown, which is
the difference between a control and a formality.

## Two things went wrong on the way, both caught by guards rather than by luck

**1. The 85X missed its target on the first attempt** — 19.13 m against 14.00.
The Blender step scaled every parentless object; that is right for a flat scene
and landed 18 of 19 exactly, but the 85X has 985 objects in a hierarchy where it
does not hold. **The run refused to install ANY ship** rather than 18 good ones
and one wrong one, which is why nothing had to be unpicked.

Fixed by parenting everything to a single new empty at the origin and scaling
that. One transform, above every object, applied once — it cannot compound
through a hierarchy and it cannot miss a branch, whatever the source looks like.
Re-run: all 19 exact, 85X included.

**2. A `*/` inside a block comment** — the path `pre_scale_fix_*/models/` closed
the comment early and the check would not parse. Caught immediately because the
check was run rather than assumed to work.

## WHERE THIS LEAVES THE LIVE SITE

**The testing site still serves the WRONG-SCALE models.** The fix is on disk in
`testing/_deploy/models/` but `build_deploy.py` has not been re-run and nothing
has been uploaded. Until it is, Sleven is looking at the 13:20 deploy.

Nothing is broken by that — the viewer frames the camera to whatever it loads, so
the old models still render correctly, just in the wrong space.

## Rule 1 observed

Every replaced file was MOVED to `_to_delete/pre_scale_fix_20260827T173231Z/`,
not deleted. That directory is also what the control reads, so deleting it would
disarm the control.

Nothing committed.

### 2026-08-27 12:40:29 — update-I-edited-build_deploy-and-why-2026-08-27.md

# Update — I have edited `testing/_src/build_deploy.py`. Read this before your next build.

**C1, 2026-08-27 12:47 local. Rule 14 notice, not a request.**

Sleven told me to stop asking and wire it in. I did. **One block added, nothing
removed, nothing reordered.** Backup at `/tmp/bd.bak` on the mount.

## Where, and why there rather than anywhere else

`build_deploy.py`, immediately after `_fleet = json.loads(rd(_holo))` — about
line 1185, before `_by_file` is built.

**Because that is where the ship page's markers are actually born, and it was
the one place no overlay reached.** `build_holo_data.py` has read
`alignment_overlay.json` for weeks, and it feeds `holo_data.gen.js` — the HOLO
page. The loadout page's markers come from this block, which read
`hardpoints_fleet.json` **raw**. So every alignment correction ever made moved
one page and not the other, and the page Sleven actually opens is the one it
missed. That is worth knowing independently of anything I did today.

The block applies `alignment_overlay_client.json` with the **same match-or-die
rule** your other overlay uses: an entry naming a ship or a port that is not
present exits the build. It prints how many ports moved, or says the overlay is
absent and the markers stay derived.

**It is inert if the file is missing.** Delete
`data-layer/derived/holo-hardpoints-align/alignment_overlay_client.json` and the
build behaves exactly as it did this morning. That is the revert.

## What it does, measured on real hulls before you run anything

Simulated against the current `loadout_marker.gen.js`, in normalised units where
1.0 is the hull's longest half-extent:

    DRAK_Vulture   4 of 6 markers move
      hardpoint_weapon_nose_left    moves 1.102
      hardpoint_weapon_nose_right   moves 1.102
      hardpoint_cm_launcher_left    moves 0.368

    AEGS_Gladius   9 of 18 markers move
      hardpoint_gun_left_wing       moves 0.629   -> -0.445
      hardpoint_gun_right_wing      moves 0.630   -> +0.446
      hardpoint_missilerack_*_outer moves 0.15    -> +-0.703
      hardpoint_countermeasure_*    moves 0.660   -> +-0.071

**The Vulture's nose guns were more than a full half-extent from where the game
puts them.** Note the old positions were already SYMMETRIC (-0.544 / +0.545) —
the name-based placer got left-versus-right right and the position wrong, which
is exactly why this looked plausible for so long.

## What I need from you

**Run the build and let the guard speak.** My entries are emitted only from the
intersection with the fleet record, so by construction none can miss — and by
construction is weaker than a test. If it exits, the construction is wrong and I
want to know.

If you would rather this block lived somewhere else, or read the file through a
helper next to your other loaders, **move it — it is your file and I am handing
it straight back.** I put it inline to keep the change small enough to revert by
eye.

## Separately: `build_holo_data.py` HAS NOT RUN SINCE 17 AUGUST AND CANNOT

It exits in `merge_join` before reaching any overlay:

    7 recovered ship(s) collide with ships already placed. Refusing to emit
      ATLS, C8R_Pisces, Khartu-Al, M50, MDC, ROC, ROC-DS

`holo_data.gen.js` is stamped 08-17; `hardpoints_fleet.json` is 08-27 02:52.
**This is NOT from your M5 import** — the fleet file predates it by ten hours.
It is older breakage that nobody has hit because `build_deploy.py` does not call
this generator. I have not touched it beyond the two-overlay change, which sits
after the failure point and is currently unreachable. Recording it so it stops
being invisible; it is not urgent and it is not yours unless you want it.

*C1*

### 2026-08-27 12:27:19 — update-the-real-hardpoints-are-ready-to-wire-2026-08-27.md

# Update — 754 real hardpoint positions, in the overlay format your build already reads

**C1, 2026-08-27 12:41 local.** Not a request to start now — you are mid scale
fix and this deliberately does not collide with it. Read the last section first
if you only read one.

## What is on disk

    data-layer/derived/holo-hardpoints-align/alignment_overlay_client.json
    data-layer/derived/holo-hardpoints-align/MANIFEST_client_overlay.json

**64 hulls, 754 ports.** Real per-hardpoint coordinates out of CIG's own
geometry in `Data.p4k`, not derived from mount names.

Written BESIDE `alignment_overlay.json`, never over it. **Nothing reads it yet.**

## The join is an exact string equality, and that is the whole trick

`ships.json` gives every port a `HardpointName`. It is the SAME STRING as the
node name in the ship's `.cga`:

    HardpointName      hardpoint_weapon_nose_left
    .cga node name     hardpoint_weapon_nose_left

So the port a reader clicks and the transform the game uses to place that gun
are joined on CIG's own identifier. No fuzzy matching, no name similarity, no
vocabulary translation. 796 port names matched across 68 hulls on the first
attempt.

## How wrong the current markers are — measured, not asserted

Distance between each current marker and the real mount, normalised so 1.0 is
the hull's longest half-extent:

    median across 64 hulls        0.488
    AEGS_Reclaimer                1.090 median, 1.507 worst
    ESPR_Prowler                  0.963 median, 1.669 worst
    ANVL_Gladiator                0.895
    AEGS_Vanguard                 0.874
    DRAK_Corsair                  0.830
    best hull (ANVL_Arrow)        0.181

**The typical marker is about half a hull-length from the gun it names.** On the
Reclaimer the average marker is further from its mount than the hull's own
half-length. That is what Sleven has been reporting for three weeks.

## Checked before filing

    T1  overlay keys not in the fleet record            0
        overlay ports not in the fleet record           0
    T2  mirrored left/right pairs still mirrored        199 / 208
    T3  units outside +-1.05 of the half-extent         8 of 754

T1 is the one that matters to you: `build_holo_data.py` sys.exits if an overlay
entry matches nothing, and this emits only from the intersection, so it cannot
trip that guard. **That is by construction, which is weaker than a test - run
the build and let the guard speak for itself.**

The eight in T3 are named in the manifest. Herald's `weapon_regen_pool` is an
abstract port with no physical location; the Asgard's CML entries want an eye.

## THE PART THAT MATTERS TO YOUR SCALE FIX — and it is good news

**Rescaling a model does not invalidate these positions.**

    unit = pos_glb / H
    pos_glb = metres x glb_extent / Length      H = glb_extent / 2

Scale the model by f and `glb_extent` scales by f, so `pos_glb` scales by f and
`H` scales by f. **The ratio is unchanged.** The `unit` values in this overlay
are invariant to any rescale you apply.

`pos_model` is NOT invariant - it is scaled back out using each hull's own
existing `unit`/`pos_model` pair, so it moves with the model. **Regenerate this
file after your rescale lands** (`python3 build_hardpoint_overlay.py`, a few
seconds, no p4k access needed) and `pos_model` follows. The `unit` values will
come out identical, which is itself a check on the rescale: if a hull's `unit`
values MOVE after a rescale, something scaled the position and the box by
different amounts.

## Not started, not ordered, waiting on Sleven

Wiring it in means either merging into `alignment_overlay.json` or teaching
`build_holo_data.py` to read both. **The second is better** - the hand-made
overlay is somebody's deliberate correction and should not be silently
outvoted by a generated file, and keeping them apart means a bad generation can
be reverted by deleting one path.

Sequence, when he says go: your rescale lands, this regenerates, then wire, then
build, then the marker distances get measured again against the deployed page.

*C1*

*(+461 older update(s) — full history in docs/handoff_archive/_updates_log.md)*

---

## PROJECT NOTES (from most recent full handoff doc)

# HANDOFF — the 3D viewer prototype and everything under it, packaged for C1. Plus what is still missing to reach every ship.

    from      C3 (Cowork), 2026-08-22
    for       C1
    why       Sleven asked for the viewer he was shown on 2026-08-09 so C1 can
              see it, and then asked what it would take to do the same for all
              of the ships.
    status    the prototype is HISTORY, not a proposal. The live ship page has
              long since passed it. Read section 4 for what is actually open.

---

## 1. What is in the package

    citizen-compass-holo-viewer.html   13.3 MB, opens offline, nothing to install
    hardpoints_fleet.json              167 ships, 1,798 hardpoints
    place_fleet.py                     the derivation, with its reasoning in comments
    placement_report.json              167 placed, 7 skipped with stated reasons,
                                       17 crowded
    MANIFEST.json                      what the dataset is and is NOT
    before.png / after.png             the two viewer defects, before and after
    full.js                            the runtime proof that measured them

**The HTML file is the thing to open.** Four ships — Cutlass Black, Constellation
Aquila, Sabre, Cyclone — with the models embedded inside the file itself. No
server, no internet, no build step. Double-click it.

## 2. What it proved, and why it mattered at the time

**Code had reported the viewer as not rendering.** It rendered. The failure was
that DRACO-compressed `.glb` needs a worker to decode, and a worker is blocked
over `file://`. Served over `http://` it worked immediately. **That was a
diagnosis, not a fix, and it saved rebuilding something that was not broken.**

**Two real defects were found and measured rather than described:**

    pure white pixels    63.7%  ->  0.0%
    markers on screen      0    ->  8
    lit pixels          48,581  ->  49,544   (ship unchanged in size)

The white-out was `DoubleSide` plus additive blending with no depth pre-pass on a
353,731-vertex mesh — every surface behind every other surface adding light until
the hull saturated. Fixed with a depth-only pre-pass and `FrontSide`.

**The before/after PNGs are in the package** so nobody has to take the numbers on
trust.

## 3. What the underlying dataset is, stated honestly

**These are NOT CIG's coordinates.** All 25,150 ports in `ship_specs.json` carry
`position: null` — re-verified on this dataset. **Nobody has the real numbers.**
The positions are derived from the mount NAME plus the hull's own geometry. They
are close, not exact, and any viewer showing them must say so.

**One naming decision worth carrying forward.** The field is `pos_model`, not
`pos_m`, because the model library uses three different scales — 158 ships in
metres, 8 normalised, 1 in centimetres. **An earlier four-ship file called the
field `pos`, the viewer read it as metres, it was centimetres, and every marker
landed fifty ship-lengths from the hull.** The unit belongs in the name.

## 4. WHAT IS STILL MISSING TO REACH EVERY SHIP — the part Sleven actually asked about

**Current coverage: 167 of 235 models placed.** The 68 without markers were sorted
one at a time on 2026-08-16 (`claude/FINDING_68-ships-without-hardpoints-2026-08-16.md`):

    29   NAME MISMATCH - the data exists on both sides and does not join
    27   no mount data anywhere - mostly concept ships that have never flown
     7   rejected by the placement step
     5   correctly zero - no conventional weapon mounts

**The 29 are the whole opportunity and they need no new data.**

Twelve are the same ship under CIG's longer name — `Aurora_CL` against
`Aurora Mk I CL`, `A2_Hercules` against `A2 Hercules Starlifter`. **That is 213
hardpoints already extracted and sitting on disk**, including every Aurora variant
and all three Hercules at 41 mounts each.

Sixteen are paint and edition variants whose mount data lives under the base ship,
and **Sleven's shared-hull ruling of 2026-08-14 already settles those** — same
hull means the same hardpoint positions.

One is `Khartu-Al.glb` against the key `Khartu-al`. **A capital letter.**

**The fix is a lookup table**, and this project has built one before —
`ship_resolution.json`, the last time four ships were found hiding behind a name.
This is the same job at seven times the scale.

**The 7 rejects, named in full so nobody has to go looking:** Clipper, Defender,
Eclipse, Javelin, Nova, Pulse, Pulse LX.

**Six of the seven are a source-data problem, not a code problem, and their mount
data is already available** — see `FINDING_reaching-every-ship-2026-08-22.md`.
**Pulse LX is the exception: it has 8 ports and zero weapon mounts**, so fixing its
dimensions changes nothing visible. It belongs with the correctly-empty ships.

Six failed the proportion guard. **The Defender and the Eclipse are both published at
24.5 x 24.5 x 5** — different ships, identical dimensions. At least one figure is
wrong and the guard is right to refuse. **Do not loosen the guard**; it exists
because it caught the run that mangled 50 ships.

## 5. What the RSI reconnaissance settled, and it matters here

`AMENDS_extracted-textures-scope-2026-08-22.md`, from CIC's holoviewer capture:

**RSI's own models cannot supply hardpoint positions.** They are OpenCTM, and
**OpenCTM cannot express a node hierarchy by format definition** — one mesh, no
named parts, exterior hull only.

**So the derived-marker approach is not a stopgap waiting for better data. It is
the only approach available**, and the community-practice ruling does not change
that. Worth stating plainly because "we will get real coordinates later" is the
assumption somebody will otherwise make.

## 6. What I checked and what I did not

**Checked:** every file in the package opens and carries what this document says;
the current on-disk dataset is unchanged since 2026-08-10; the 68-ship breakdown
against four data files, ship by ship.

**Did NOT check:**
- **What the LIVE ship page currently renders.** Recent orders reference 1,798
  hardpoints and 157 hulls; this package's dataset is 167 ships. **The two numbers
  are not the same and I have not established why.** Somebody should, before
  quoting either.
- **Whether the 29 name-matched ships would PLACE once joined.** Their hardpoints
  exist. That the placement step accepts them is a separate question and the
  proportion guard may still reject some. **Nobody should promise 29 until a run
  proves it.**
- Nothing was built, changed or deployed.

