# OWNERS — one writer per artifact, in a form a program can read

    maintained by  C1
    why            rule 14 says: "one writer per artifact. When a second writer
                   is possible, make it impossible rather than discouraged."
                   Until 2026-08-28 the list lived in prose, in a section of
                   `NEXT.md` headed NOT CODE'S. Prose is discouragement.

**On 2026-08-27 at 22:10 and 22:15 Code's drift detection fired on C1's writes
to `testing/_src/cc_viewer.js` and `testing/_src/loadout.src.html`.** Both files
were already C1's, in `NEXT.md` and in the state document of the day, and had been for
weeks. **Nothing was actually in conflict.** Two sessions were reading two
different prose lists and one of them was reading a list Code's tooling could not
see at all.

That is the whole failure: **ownership was written down in a place programs do
not read.** This file is the place they do.

---

## THE RULE THIS FILE ENFORCES

A path appears **exactly once**. The session named beside it is the only one that
writes it. Anyone else who needs it changed **asks the owner** — through
`inbox/` for Code, through `NEXT.md` for C1 — and does not edit it, not even
"just this once", not even when the edit is obviously right.

**A path that is not in this file has no declared owner.** That is not
permission; it is a gap, and finding one is worth reporting.

---

## DELEGATION — when another session may write an owned file

**Ruled by C1, 2026-09-02, after Code stopped to ask. Stopping was correct.**

**An order that names the FILE and states the CHANGE is the owner delegating
that write.** Carry it out. You are the owner's hands, not a second writer, and
rule 14's failure mode — two writers who do not know about each other — does not
occur.

**What counts as delegation:**

    the order names the path
    and states the change, as a diff, a paste-in block, or precisely in prose

**What does NOT:**

    "fix the viewer"                    no file named
    "tidy that up while you are in there"   no change stated
    anything you infer, extend or improve beyond what was written
    a second file you noticed on the way

**If the order names the file but the change turns out to be wrong, or needs a
different fix than the one written: STOP AND SAY SO.** Delegation covers the
change described. It does not transfer ownership and it does not cover your
judgement about a better change.

**Record it in the update** — which order, which owner, which file. An owned file
changed by another session with no order named is the thing this rule exists to
catch.

**This does not loosen rule 14.** It states who the writer was. When C1 writes
the diff and Code applies it, C1 wrote the file.

## C1 — Cowork. The only Cowork session that writes repository ARTIFACTS.

**Corrected 2026-09-08.** This heading read *"the only Cowork session that
writes to the repository"*, which was true when written and is now wrong:
**C5, the audit desk, drops memos in `inbox/`.** That is a write, and the
watcher files them into `correspondence/`. What C2 does not do is write
artifacts, own paths, or edit an owned file. The distinction is the whole
difference and the old wording collapsed it.

**On the codename — SLEVEN RENAMED IT 2026-09-08.** The audit desk is **C5**,
not C2. It was proposed as C2 and the desk itself flagged the collision: `NEXT.md`
uses "C2" for the **C2 Hercules** (and a C2 Starlifter) and twice for an earlier
reviewer. **C5 collides with nothing.** A ship is never an owner, and now it
cannot be mistaken for one.

    NEXT.md
    LIVE.md
    OWNERS.md
    docs/UX_DOCTRINE.md
    docs/CURRENT-STATE.md
    docs/ARCHITECTURE_DECISIONS.md
    docs/NOTE_which-url-is-which-2026-08-02.md
    testing/_src/loadout.src.html
    testing/_src/next.src.html
    design/ANGLES.md
    testing/_src/cc_viewer.js
    checks/_verify_panel_dismiss.mjs
    checks/_verify_placement_gate.py
    checks/_verify_stage_still.mjs
    checks/_verify_marker_provenance.py
    checks/_verify_marker_note.mjs
    checks/_verify_swap_loop.mjs
    checks/_verify_marker_census.py
    checks/marker_census.json
    checks/_verify_child_markers.py
    checks/_fixtures_markers/
    checks/_verify_identical_options.mjs
    checks/_verify_marker_spread.py
    checks/_verify_drydock_scale.mjs
    checks/_verify_wall.mjs
    checks/_verify_frontpage_concepts.mjs
    build_ship_silhouettes.py
    build_frontpage_data.py
    build_ship_thumbs.py
    build_drydock_concept.py
    build_sky_three_ways.py
    tools/render_missing_ships.mjs
    data-layer/derived/ship-prices/
    data-layer/derived/ship-silhouettes/
    data-layer/derived/main-page-concepts/  (except five-main-pages.html,
                                             slipway.html, deck-sifter-yard.html — C3)
    decode_cga_nodes.py
    probe_ship_geometry.py
    extract_p4k_entry.py
    build_hardpoint_transforms.py
    build_hardpoint_placement.py
    checks/_verify_display_names.py
    checks/_verify_no_agent_traces.py
    checks/_verify_marker_mesh_distance.py
    checks/_dracopos.mjs
    build_loadout_data.py
    build_hardpoint_overlay.py
    testing/_src/_layer.src.html
    testing/_src/keybinds.src.html
    testing/_src/device_engine.js
    testing/_src/kb_overlay.inc.html
    checks/_verify_us_spelling.py
    checks/_verify_no_leaked_comments.py
    checks/_verify_hull_is_solid.mjs
    testing/_src/cc_glossary.inc.html
    testing/_src/_inspect.src.html
    cryxml.py
    testing/_tools/cc-uvfix-compress.cjs
    testing/_tools/verify_uvfix.cjs
    testing/_tools/survey_winding.cjs
    releases/latest.html
    static/preview.html
    testing/index.html                 CLAIMED BY C1 2026-09-11. Build found it had
                                       no owner while fixing Q57, and it is not a
                                       small file to leave unowned: it holds the
                                       SHIPS = [...] literal that build_frontpage_data.py
                                       reads, so it is the origin of the front page's
                                       ship facts. Last written 2026-08-02.
    correspondence/
    correspondence/README.md           CLAIMED BY C1 2026-09-13. The mail's doctrine - what a
                                       letter is, what its fields mean, how an answer returns.
                                       Build holds the watcher and the controls that enforce it;
                                       this desk holds the description. Found unowned by Build
                                       while wiring the owner-ask control, which needs the file
                                       to document `Owner-action:` before its cutoff can be set.
    checks/_verify_correspondence.py
    build_crafting_demand.py
    data-layer/derived/hardpoint-transforms/
    data-layer/derived/hardpoint-placement/
    data-layer/derived/holo-hardpoints/
    data-layer/derived/holo-hardpoints-align/
    data-layer/derived/crafting-demand/
    data-layer/derived/hull-geometry/
    build_kb_actions.py                CLAIMED BY C1 2026-09-12. Build found all
    build_keybind_modes.py             four unowned while answering ruling 13's
    extract_default_profile.py         keybinds question. The keybinds page and
    data-layer/processed/keybinds_site.json   its overlay were already C1's; the
                                       generators that feed them had no name on
                                       them. FIFTH gap found the same way - by a
                                       desk going to touch a file and finding
                                       nobody's name on it.
                                       AND A DEFECT TRAVELS WITH THE LAST ONE:
                                       nothing in the repository produces
                                       keybinds_site.json. 1,103 rows dated
                                       2026-08-05 with a hand-made link in the
                                       middle of the chain that cannot be re-run.
                                       Owning it does not fix that; it names who
                                       owns fixing it.

## GAPS FOUND 2026-09-04, PROPOSED FOR CODE — not claimed by C1

Three build-tooling files carry nobody's name. C1 proposes Code as owner and has
NOT claimed them. One of them C1 edited; that edit is declared here rather than
buried, and Code may reverse it.

**RULED 2026-09-13: all three are Code's, and they are now in the `## CODE` list above.** They
were proposed for Code on 2026-09-04 and nobody ever ruled it, so they sat as a proposal in a
prose section for nine days — invisible to the control that is supposed to find unowned paths.

**C1's one edit stays declared rather than buried.** `testing/_src/deploy_pages.py` gained one
entry to PAGES on 2026-09-04 — `('_inspect.src.html', '_inspect.html')`. Without it
`check_deploy_clean` REFUSES the deploy, proven by removing the line and re-running the guard.
Nothing else was touched. `check_deploy_clean.py` and `strip_comments.py` were not edited;
`strip_comments.py` behaved correctly in the 2026-09-04 glossary leak and the include was lying
to it. **Code may reverse any of it.**

## CODE — Claude Code, on the Windows machine.
claude/RECORD-AUDIT-DISPOSITIONS.md  B3 ledger; sole writer is record_repair (Code)

    testing/_src/build_deploy.py
    build_find_data.py
    testing/_src/_disc.css
    checks/run_all_controls.py
    checks/sweep_gate.py
    checks/file_checks.py
    scripts/deploy_testing.ps1
    scripts/deploy_live.ps1
    watcher-go/
    testing/_src/deploy_pages.py        RULED CODE'S 2026-09-13. Proposed for Code in the
                                        2026-09-04 gap note and never ruled until now. C1's
                                        2026-09-04 edit to it stands declared below.
    testing/_src/check_deploy_clean.py  RULED CODE'S 2026-09-13. Reads deploy_pages.
    testing/_src/strip_comments.py      RULED CODE'S 2026-09-13.
    checks/_verify_picker_deployed.mjs
    checks/_verify_find_deployed.mjs
    checks/_verify_deployed_links.mjs
    checks/_verify_one_fleet_two_files.py
    checks/_verify_front_page_prices.py
    citizen-collector/
    roadmap-watcher/
    DEFERRED-BUILD.md
    testing/_src/inject_engine.py
    seed.py

**Everything else under `checks/` is Code's by default** except the files named
under C1 above. Code wrote the suite; C1 contributes controls and names them here
when it does.

## A NOTE ON `build_loadout_data.py`, CLAIMED 2026-08-29

**It was unowned.** It writes `loadout_data.gen.js`, which is the ship page's
entire data layer, and neither C1 nor Code was named against it. That is the
second ownership gap found this week by the same route: going to change a file
and finding nobody's name on it.

**C1 claims it** because the ship page and its data are already C1's, and a
generator whose only consumer is C1's page should not have a different writer.
**Code is the one to say if that is wrong** - it is claimed, not seized, and
this note is the notification.

## A NOTE ON `data-layer/derived/holo-hardpoints/`, CLAIMED 2026-08-29

**It was unowned until Code reported it**, and it is the one directory where
rule 1 was not followed: `loadout_marker.pre-C1-20260828.js` was DELETED from
the working tree rather than moved to `_to_delete/`. Neither session can say
which of them did it. **That is the argument for the claim, not against it** —
an unowned directory is where that happens.

**C1 claims it, with a caveat that has to travel with it:** its main file,
`hardpoints_fleet.json`, has a single writer — `place_fleet.py`. **Nothing in
here is deleted; superseded files move to `_to_delete/` like everything else.**

**CORRECTION, 2026-09-05, C1.** The sentence that stood here said `place_fleet.py`
"is not in this repository." **It is** —
`data-layer/derived/holo-hardpoints/place_fleet.py`, inside the very directory
this note is about. Build found it by looking, which is how a wrong claim in an
ownership file gets caught: somebody needed the thing and went and read. The
claim on the directory is unaffected; what was wrong was the reason given for
the caveat.

`docs/PROPOSAL_the-marker-pipeline-is-four-layers-deep-2026-08-27.md` proposes
retiring the file to a named fallback. That decision is Sleven's and is not made.


## A NOTE ON `data-layer/derived/hull-geometry/`, CLAIMED 2026-09-05

**Build found it unowned — the seventh gap, and the first one sitting on a
critical path between two things that were already owned.** The chain is:

    the .glb files  ->  hull-geometry/  ->  place_fleet.py  ->  holo-hardpoints/

The models at the front are C1's. `holo-hardpoints/` at the back is C1's. The
stage in the middle had nobody's name on it, which is how it came to be three
days stale against the hulls it describes without either session noticing.

**C1 claims it.** Two owners at adjacent stages of one derivation is exactly the
failure rule 14 exists to prevent.

**STANDING DELEGATION, so Build never has to ask:** Build may regenerate
`hull-geometry/` into `_stage/` whenever a model changes, and hand over the
comparison. **Promotion into the committed directory is C1's**, because a wrong
promotion here puts markers on the wrong part of a ship and nothing downstream
would say so.

`testing/_src/decode_glb_points.js`, which does the decoding, is build tooling
and **Code is PROPOSED as owner** — not claimed by C1 — alongside the three
files proposed on 2026-09-04.

## A NOTE ON THE PAGE-COPY FILES, CLAIMED 2026-08-30 — AND ON WHAT I GOT WRONG

    testing/_src/_layer.src.html        injected into every page
    testing/_src/keybinds.src.html      the keybind tester
    testing/_src/device_engine.js       the device panel, one writer
    testing/_src/kb_overlay.inc.html    the overlay's copy of the same panel

**All four were unowned. That is the fourth gap found the same way in three
days: going to change a file and finding nobody's name on it.** Three of the
four were found by C1, which says the gap is systemic, not a run of bad luck.

**AND THE FIRST VERSION OF THIS NOTE, WRITTEN AN HOUR EARLIER, WAS WRONG.** It
said `_layer.src.html` and `keybinds.src.html` *"share code by copy"* and that
*"today's US-spelling pass had to be applied twice, by hand."* Both halves are
false and the truth is better: **`device_engine.js` is the single writer of the
device panel, and `inject_engine.py` copies it into both hosts on every build,
between fixed boundary markers, with a `node --check` gate that refuses to
inject code that does not parse.** Rule 14 was already satisfied here before
anyone claimed anything. I wrote a finding about duplication into a file whose
job is to record ownership, without reading the script that manages it.

**HOW IT SURFACED, WHICH IS THE ARGUMENT FOR THE CLAIM.** The hand edit to the
two hosts was silently reverted by a build - correctly, because the hosts are
generated in that region and the master had not changed. Nothing warned; the
edit simply stopped existing. **An unowned generated region is where that
happens**, and it is why the master is claimed here rather than the hosts alone.

**`testing/_src/inject_engine.py` IS STILL UNOWNED AND IS NOT CLAIMED HERE.**
It is build tooling, `build_deploy.py` calls it, and `build_deploy.py` is
Code's. **It is reported, not taken** - the natural owner is Code and that is
Code's call to make.

**Code is the one to say if any of these claims is wrong.** They are claimed,
not seized, and this note is the notification.

## A NOTE ON THE LIVE SITE'S TWO FILES, CLAIMED 2026-08-30 — AND THEY DISAGREE

    static/preview.html      286,228 bytes    the master, per CLAUDE.md
    releases/latest.html     205,362 bytes    the mirror, and the one PUBLISHED

**`CLAUDE.md` says the live site is served from `static/preview.html` mirrored
into `releases/latest.html`, by manual Netlify Drop.** The two are 80,866 bytes
and 33 diff lines apart. **The mirror is what the public gets, so on the live
site the master is not the master.**

They differ in exactly two places, and one of them is not a session's to settle:

    fonts    the MASTER embeds four faces as base64 and calls nothing.
             The MIRROR - the live file - @imports them from
             fonts.googleapis.com, so every visitor's browser contacts Google.
    legal    the MASTER carries an extra paragraph the live file does not:
             "This site is not endorsed by or affiliated with the Cloud
             Imperium or Roberts Space Industries group of companies..."

**THE LEGAL DIFFERENCE IS RULE 8 AND IS NOT TOUCHED.** The live file is not
bare - it carries its own unofficial-site disclaimer and a trademark bar. What
it does not carry is the master's SECOND paragraph. **Whether that paragraph
belongs on the public site is Sleven's decision alone**, and no session
reconciles it.

**BOTH FILES ARE CLAIMED SO THAT THE DIVERGENCE STOPS BEING ACCIDENTAL.** The
2026-08-30 patch-banner correction was applied to BOTH, identically, and the
diff is still 33 lines — deliberately. **Syncing them is a decision, not a
tidy-up, and it was not made here.**

**They were unowned, which is the fifth gap in three days.**

## A NOTE ON `correspondence/`, ADDED 2026-08-30 — THE SESSIONS WRITE TO EACH OTHER

`correspondence/open/<desk>/` holds memos waiting for a reply, and `correspondence/answered/`
holds the ones replied to and kept. **Written as a sentence rather than a diagram: a bare path
line inside a prose section reads as an ownership claim to the control, and this is a map.**

**Until 2026-08-30 a question from Code to C1 could only reach C1 by SLEVEN
reading a handoff, noticing the question inside it, and pasting it across.** He
was doing a postman's job between two sessions that both read this repository,
and he said so.

**MEMOS ARE ADDRESSED TO THE JOB, NEVER TO A CODENAME** — architecture, build,
research, audit, design, owner. **Corrected 2026-09-12: this said four and there
are six. Audit was added 2026-09-08 and design shortly after, and this line was
not.** The durable answer is that the names come off the trays on disk rather than
being typed here; until they do, a tray added without this line changing is a
finding. **`cic` is NOT one of them and never was** — it named an instrument, not
a job, and open-web work is addressed to `research`. Sleven's requirement: *"I'd prefer if we made it look like a
human is operating this. So that way, if I ever hand this off to somebody, they
know what to look at."* `C1` and `Code` mean nothing to a stranger; a tray with
a job on it means something immediately.

**EVERYTHING STILL GOES IN `inbox/`.** The watcher routes on the `To:` header —
`watcher-go/memo.go`, checked BEFORE handoff and update classification so a memo
whose subject contains "update" is not swallowed, which is the defect
`routing_prefix_test.go` already records. **C1 first built a separate `channel/`
folder to bypass the watcher and Sleven corrected it: a second sorting system
beside the one that works is how a project ends up with two of everything.**

`checks/_verify_correspondence.py` holds it: every memo addressed to a real
desk, every answered one carrying an answer, and **an open memo REPORTED, never
failed** — a control that went red on an unanswered question would teach
everyone to close questions rather than answer them.

**`watcher-go/` is Code's** — C1 wrote `memo.go` and `memo_test.go` to a design
Sleven asked for, and Code builds, tests and redeploys the watcher.

## SLEVEN — his alone, and not by convention.

    every legal, Fan Kit and trademark decision
    whether and when the site goes live
    attribution text and its placement

**No session edits these. Rule 8.**

---

## WHAT THIS FILE IS NOT

**It is not a lock.** Nothing stops a session writing to a path it does not own;
the filesystem has no idea who anyone is. What this file removes is the excuse —
after it, an unowned write is a decision somebody made against a list they could
have read, not a misunderstanding between two prose documents.

**It does not settle who SHOULD own something.** It records who does. Moving a
path between owners is a decision, it goes in a dated `docs/DECISION_*`, and this
file is edited to match afterwards.

---

## THE CHECK

`checks/_verify_owners.py` holds this file to its own rule: every path exists,
no path is claimed twice, and the prose list in `NEXT.md` agrees with it. If the
two disagree, **this file wins and `NEXT.md` is corrected**, because a program
can read this one.

— C1, 2026-08-28

---

## THE ELEVEN UNOWNED PATHS, RESOLVED 2026-09-07 — C1

Build filed `correspondence/open/owner/2026-09-07_eleven-paths-have-no-owner.md`
asking one line: are the Build-natural ones its own. **Ten of the eleven are, and
this is the edit that says so.** Decision recorded at
`docs/DECISION_the-eleven-unowned-paths-2026-09-07.md`.

**These are first assignments of paths nobody held, not moves between owners.**
Every one is reversible on Code's word — claimed, not seized, exactly as the
2026-08-30 note put it.

### Already Code's, and the list simply did not show it

**The five were `checks/_verify_picker_deployed.mjs`, `_verify_find_deployed.mjs`,
`_verify_deployed_links.mjs`, `_verify_one_fleet_two_files.py` and `_verify_front_page_prices.py`,
and they are now named in the `## CODE` list above.**

**The clause under CODE already covers these** — *"Everything else under
`checks/` is Code's by default except the files named under C1 above"* — and
none of the five is named under C1. Checked path by path, not by grep.

**That the clause did not answer the question for the person reading it is the
defect.** A default that a careful reader misses is doing half its job, so the
five are named here explicitly. The clause stays for everything after them.

### Newly assigned to Code

**Assigned to Code on 2026-09-07 and now carried in the `## CODE` list above, where a program
can read them:** `citizen-collector/` (build tooling on the machine); `roadmap-watcher/` (Code
wrote `livever.go`, `verified.go`, the config changes and `rejectUnknownKeys`); `DEFERRED-BUILD.md`
(`NEXT.md:2526` already said so; only the machine-readable list was missing it);
`testing/_src/inject_engine.py` (build tooling `build_deploy.py` calls, and `build_deploy.py` is
Code's — the 2026-08-30 note left it deliberately, Code asked for it to be resolved, and it is
reversible); and `seed.py` (it runs against the database, and the database is Code's execution
surface).

**One caveat on `seed.py`, because it is not purely a script.** 501 lines, of
which 233 are the SHIPS data literal handed over from Phase 1. **Ownership here
covers the script.** If the literal itself becomes the thing being edited, that
is a data decision and it comes to Architecture first — the same split already
used for the page-copy files.

## UNOWNED — nobody, and somebody checked

    collector2/

**Moved out of prose 2026-09-13 (Architecture / Grok covering C1).** Same facts as the old "Not owned by anybody" note: Sleven's personal build, gitignored, deliberately nobody. The section exists so the control can see "nobody, and somebody checked."


### Not owned by anybody, and that is correct

**`collector2/` is Sleven's personal build and is deliberately owned by nobody.** Gitignored
at `.gitignore:137`, zero tracked files, verified rather than assumed.

**Path now lives under `## UNOWNED` above (2026-09-13).** This paragraph stays as the human note.

**Its absence from this file is deliberate and is now recorded as such.** Build's
point is the right one: *"absent and deliberately absent look identical."* They
do not any more.

Nothing in `collector2/` reaches the repository, so no two writers can meet in
it. If that ever changes — if any part of it becomes tracked — it needs an owner
that day.

— C1, 2026-09-07

## A NOTE ON `docs/UX_DOCTRINE.md`, CLAIMED 2026-09-08

**Adopted by Sleven on 2026-09-08 at version 6.2**, after an assessment under
its own Section 43. Its STATUS block assigns technical interpretation and
maintenance to C1 and product direction, publication, rights and
acceptance/revision/retirement to Sleven, so the row above records what the
document itself already says.

**Section numbers are FROZEN.** Amend a section in place or append a new one at
the end. Do not renumber. If a renumber ever becomes unavoidable, the document
requires an explicit old-to-new mapping to be kept inside it so existing work
orders and evidence do not silently point at the wrong requirement.

**It creates no hard rules.** `CLAUDE.md` remains the only hard-rule list and
wins any conflict; where the doctrine disagrees with it, the doctrine is
corrected. **Do not create a second UX doctrine file** — the document says so
itself and this row is the enforcement point.

## A NOTE ON `testing/_src/next.src.html`, CLAIMED 2026-09-08

**Found by somebody tripping over it, which is the fifteenth time.** The audit desk
went looking for who owned the new front page and reported that the string `next`
does not appear in this file at all, while `testing/_src/next.src.html` had been
edited that morning.

It is claimed by C1 for the same reason `tools/frontpage/build_next_frontpage.py`
is: **this file is generated by that generator, and the generator is mine.** A
generated artifact whose generator has one owner cannot have a different one, or
the next person edits the file and the next build silently discards the edit. That
already happened once today — the drift control caught a regenerated
`next.src.html` landing four minutes after Code's build, and it was right to.

**The practical rule that follows:** nobody edits `testing/_src/next.src.html` by
hand, including me. Changes go into the generator and the file is rebuilt.

## A NOTE ON `design/ANGLES.md`, CLAIMED 2026-09-08 — AND ON THE EXCEPTION THAT MOVED WITH IT

> ## RESTORED 2026-09-12. THE WITHDRAWAL BELOW WAS WRONG AND THIS PARAGRAPH IS THE RULE.
>
> **`design/ANGLES.md` is additive-open again. Any desk may ADD a question, a
> pair or a standing rider — with an incident behind it, which is the file's own
> test. Nothing is removed without saying why. C1 owns the FRAME — the headings,
> the pointer, the structure — and owns every removal, and remains the named
> owner for rule 14 purposes.**
>
> **Why the withdrawal was wrong, because the error is more useful than the
> correction.** It reasoned about the METHOD, which Sleven moved out to
> `CCDesk-logs/ANGLES.md`, and concluded the exception was no longer needed
> here. **The method moved. The reason for the exception did not.** What stayed
> behind is *"the extra questions Citizen Compass asks"* and the standing riders,
> and every one of those is generated by a desk's own incident — Design's
> split-by-day rider, Audit's pairs section. **That content is exactly what
> invited every writer, and it never left the file.** "The method moved" was a
> proxy for "the reason moved", and it was not.
>
> **How it was found: by a desk acting, not by anyone reading.** Design wrote to
> the file on 2026-09-12 under its own first line — *"Any desk may add. Nothing
> is removed without saying why"* — which had said that for four days while this
> section said the opposite. **The file and this file disagreed in writing and
> both were being read.** That is the pair `OWNERS.md x the repository`, item 4
> on the pairs list in the very file it was about.
>
> **Design's writes of 2026-09-12 were lawful under the file's own rule and are
> lawful under this one. Nothing is undone.**

**HISTORICAL, AND SUPERSEDED BY THE BLOCK ABOVE — kept because the reasoning is
what went wrong.**

**It was briefly a declared exception to rule 14 and it is not one any more.**

On 2026-09-08 C1 ruled the sixty-angles method binding on every desk and declared
`design/ANGLES.md` a shared artifact — additive-only, every desk may write, C1 owns
the frame — because rule 14 is one writer per artifact and that file invited all of
them. **Sleven then moved the method itself out of this repository entirely**, to
`CCDesk-logs/ANGLES.md`, on the grounds that it is his method, it predates the site,
and more than one project uses it. He was right, and it makes the exception
unnecessary here.

**What is left in `design/ANGLES.md` is a pointer plus the questions specific to this
project.** That is an ordinary owned file with one writer, claimed by C1, and rule 14
applies to it normally.

**The shared-artifact exception went upstairs with the method.** `CCDesk-logs/` is not
this repository and this file does not govern it — the company copy carries its own
rule in its own first line: *anyone may add, nothing is removed without saying why.*
Recorded here so nobody finds the withdrawn exception in the history and applies it
to a file that no longer needs it.

