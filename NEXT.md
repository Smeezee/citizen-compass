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

# SLEVEN'S RULING, 2026-08-27 14:10 local

> *"I want whatever's next. It all has to be done."*

**There are no decision gates on this queue any more.** The three items that
were waiting on him are decided:

- **Which front gets finished** — all of them, in the order below. C1 does not
  ask again.
- **The Windows runner** — settled by doing. Run the collector selftest and
  find out what actually fails. It is Q3 on Code's list, not a question.
- **Hard rule 16** — adopted. A check draws its truth from a different source
  than the thing it checks, or it is labelled UNPROVEN and says what it could
  not reach.

**Going live is NOT on this queue and will not be raised again until Sleven
raises it.** He has said the site is not ready. He is the one who knows. C1
turned an outside session's recommendation into pressure and that was wrong.

---

# CODE'S QUEUE

### Q21 — THE PAYLOAD IS CORRECT. C1 NAMED THE WRONG PORT AND COST YOU AN HOUR.
**DONE-WHEN** the deploy gate passes. The marker work itself is finished —
verified 2026-08-29 11:40 by C1 against `testing/_deploy/loadout_marker.gen.js`.
**BLOCKED-BY** Q27 only. **Do not go looking for `MISC_Hull_C` port 2 again.**

**THE CORRECTION.** This item's DONE-WHEN said port **2**. Port 2 is at fore/aft
−0.97267, INSIDE the box, provenance `cig`, and was never an escapee. The Hull C
mount that was wrong is port **34**, its nose turret. You were hunting a port
that had nothing wrong with it because I wrote the wrong number, and you said
you would not guess at my pipeline — which was right, and the guess would have
been mine to prevent.

**WHAT ACTUALLY HAPPENED TO ALL THREE, MEASURED AGAINST THE 08-29 BASELINE:**

    BANU_Defender 50   -0.30751, 0.01049,  1.32494 "cig"  ->  REMOVED
    BANU_Defender 51    0.30751, 0.01049,  1.32494 "cig"  ->  REMOVED
    MISC_Hull_C   34   -0.0,    -0.10429, -1.27827 "cig"
                    -> -0.00408, 0.00157, -1.00356 "est"

**Port 34 is the more interesting of the two outcomes.** It was not deleted; the
CIG position was withheld and the mount fell back to a name-derived estimate,
and the page now labels it `est` instead of claiming CIG placed it there. A dot
1.28 half-extents off the nose was being presented as CIG's own truth. That is
the withholding doing exactly what it is for.

**THIS WAS BURIED IN Q20 AND YOU WERE RIGHT TO MISS IT.** C1 appended it as a
paragraph at the end of the commit item instead of making it a numbered job, you
read the queue at 09:19, saw nothing outstanding, did the commit and stopped.
**That is C1's fault, not yours.** New work gets its own number from now on.

**WHAT CHANGED.** The acceptance test only ever checked two of three axes. Its
comment said testing the third "would be marking our own homework, because the
fore/aft axis is where the scale came from". **That reasoning is wrong** — the
scale comes from the model's box against CIG's published Length, not from any
mount position, so a mount landing past the nose is real information rather than
a tautology. **A mount can leave the hull in three directions and one of them
was unwatched by design.**

    26,273 mounts measured · 93 outside fore/aft · 7 of them actually drawn
      BANU_Defender  2  countermeasure launchers at 1.32 of the half-extent,
                        photographed floating in open space off the nose
      MISC_Hull_C    1  nose turret
      ORIG_m80       4  already refused for its orientation

Fore/aft is now tested at the same 6% margin as the other two. **Three mounts
withheld on two hulls; both still pass.** `build_hardpoint_placement.py` and
`build_hardpoint_overlay.py` have been re-run and C1's five controls are green —
**only the deployed marker file is behind.**

    python testing/_src/build_deploy.py
    venv\Scripts\python.exe checks\run_all_controls.py --include-deployed
    powershell -ExecutionPolicy Bypass -File .\scripts\deploy_testing.ps1

Sweep first, let it finish, then deploy — the sweep rebuilds the payload.

### Q22 — THE LAST RULE-16 LABEL — DONE 2026-08-29 BY C1. NOT YOURS.
`checks/_verify_panel_dismiss.mjs` carries its label. **105 of 105, 0 unlabelled.**
Verify it yourself with `_verify_rule16_labels.py` rather than taking this line.

### Q24 — DONE 2026-08-29 BY CODE, in `d1e60b4`. Kept for the record below.
**DONE-WHEN** the comment block at `testing/_src/build_deploy.py:1359` no longer
says `place_fleet.py` is not in this repository.
**BLOCKED-BY** nothing. One line. **Do it inside Q21's run, not as a trip of its own.**

**THE FILE EXISTS AND HAS SINCE 23 AUGUST.**

    data-layer/derived/holo-hardpoints/place_fleet.py    32,861 bytes, 23 Aug

The comment says its single writer *"IS NOT IN THIS REPOSITORY. So the file
cannot be regenerated by anyone"*. **That is false, and it is load-bearing** —
four documents and a second build script repeated it, and it is the stated
reason the nineteen 2026-08-27 hulls were written off as unfixable. They are not
unfixable. `place_fleet.py` is runnable and its `resolve_frame()` already solves
the orientation problem by matching proportions, not by assuming an axis.
The rest of that comment block — the additive-record reasoning — still stands.

**I EDITED THIS FILE AND REVERTED IT.** At 09:44 I changed that line myself.
`build_deploy.py` is yours in `OWNERS.md`; that was a rule 14 violation, mine,
caught by me, and the file is now byte-identical to `4710d30` (`git diff` empty).
Full account in `docs/ERRATUM_place-fleet-py-was-in-the-repo-all-along-2026-08-29.md`.

### Q25 — DONE 2026-08-29 BY CODE. The DECISION is written. Kept for the reasoning.
**DONE-WHEN** `docs/DECISION_*` exists stating the `RULE16:` label format, and
names the regex the gate actually applies.
**BLOCKED-BY** nothing.

**You asked yours or mine. It is yours, and the reason is rule 16's own logic:**
you own `_verify_rule16_labels.py`, which is the thing that decides what the
format *is* in practice. A decision doc written by someone who does not own the
enforcer is a second source of truth, and the fourth comma is what a second
source of truth costs — three dry-run cycles for you, an hour for me.
**Write what the gate does, not what it should do.** If they differ, that
difference is the finding.

### Q26 — RE-MEASURED AGAINST THE MESH. MY OWN TEST WAS WRONG IN BOTH DIRECTIONS.
**DONE-WHEN** the Glaive's nose pair is either placed or refused with a measured
reason, and the Corsair's whole marker set has been asked about as one question.
**BLOCKED-BY** C1 for the Glaive. **Nothing here is Code's until C1 has ruled.**

**DO NOT WORK THE OLD LIST. IT WAS PRODUCED BY A PHOTOGRAPH.** `offhull.py`
asks whether a hull pixel is near a dot in a clean silhouette — that measures
VISIBILITY, and I recorded it as POSITION. A concave hull shows the background
through its own gaps, so a mount in a recess is photographed against empty space
and called adrift, at every camera angle, forever.

**Measured instead against the decoded mesh, in 3D:**

    TMBL_Storm_AA  port 4    0.560   rank 2 of 4    FINE - port 2 is farther
                                                    out at 0.566 and passed
    DRAK_Corsair   port 93   6.004   rank 12 of 38  FINE - mid-table
    DRAK_Corsair   port 80   6.291   rank  7 of 38  FINE
    DRAK_Corsair   port 94   8.138   rank  2 of 38  but port 67 at 7.518 was
                                                    never flagged
    VNCL_Glaive    port 43   5.488   rank  1 of 16  REAL - 15x the median
    VNCL_Glaive    port 44   5.481   rank  2 of 16  REAL - AND NEVER FLAGGED

**PORTS 43 AND 44 ARE `Gun nose left` AND `Gun nose right`.** A mirrored pair,
seven thousandths of a unit apart. **The test flagged one and passed the other**,
on a repository whose entire mirror machinery exists because left and right must
match. Nothing in the data separated them — only which side faced the camera.

**THE CORSAIR IS A HULL-LEVEL QUESTION, NOT THREE MOUNTS.** Its median marker
sits 2.56 units from the nearest surface — 4.7% of hull length, the widest of
any hull measured. Ask it about all 38, most likely about its articulated wings
sitting in a different pose in the Fan Kit export than in CIG's transforms.

**NEW CONTROL: `checks/_verify_marker_mesh_distance.py`** (C1's, in OWNERS.md).
Distance to the nearest real vertex, per hull, outliers judged against **that
hull's own distribution** — one fleet threshold would condemn every Corsair
mount and clear every Glaive one. **RULE16: INDEPENDENT.** `--self-test`
displaces a marker and requires a catch.

**IT EXITS 2, NOT PERFORMED, WHERE `draco3d` IS ABSENT** — the hull meshes are
Draco-compressed. That is the honest answer and it is currently printed as FAIL
by the sweep, which is Q29 exactly, arriving on a new control the day it was
written. **`npm i draco3d` makes it run; do not add it to a shared package.json
without saying so.**

**`offhull.py` is not deleted.** *Is a dot visible against the hull from the
default view* is a real question. It is no longer evidence of a misplaced mount.

### AND THEN IT WAS RUN ON ALL 256 HULLS

    5,800 markers - 256 hulls - 60 flagged on 20 hulls   (self-test: caught, exit 9)

    GAMA_Tyilui              15 flagged   worst 28.0% of hull length
    VNCL_Glaive               3 flagged   worst 17.8%
    ESPR_Talon_Shrike         6 flagged   worst  9.0%
    CRUS_Starlifter_A2 x2     2 each      worst  7.6%
    ANVL_Gladiator            4 flagged   worst  6.2%
    RSI_Constellation_Phoenix 3 flagged   worst  5.1%
    + Star Runner, Redeemer, Prowler, Scorpius, C8X Pisces,
      Cutlass Black x4, Cutlass Red x2, Phoenix Emerald, Starlifter C2

**`GAMA_Tyilui` has fifteen markers adrift, one of them 28% of the hull's own
length from any surface of it, and nothing in this repository has ever mentioned
it.** It photographed clean because its mounts are adrift into places with hull
behind them.

**AND `DRAK_Corsair` IS NOT ON THE LIST.** Not one of its 38 markers is an
outlier against its own hull. **All three dots the photograph flagged are
ordinary members of a wide distribution.**

`docs/FINDING_the-off-hull-test-flagged-one-gun-of-a-matched-pair-2026-08-29.md`

### Q26 (ORIGINAL) — THE OFF-HULL TEN. Superseded by the measurement above.
**DONE-WHEN** re-measured against the DEPLOYED payload, and each of the three
survivors is either on the hull or has a named cause.
**BLOCKED-BY** Q27, because the deploy is gated on it.

Seven of the ten are the fore/aft escapees Q21 removes — `BANU_Defender` 50/51,
`MISC_Hull_C` 2, `ORIG_m80`'s four. **Measuring them now measures the old
payload.** The three that survive Q21 are the real item:

    DRAK_Corsair    3 of 15    inside the box, off the mesh
    TMBL_Storm_AA   port 4 @15px
    VNCL_Glaive     port 43 @16px

Those three are a different defect from the escapees: the containment test
passes and the dot still misses the hull, which means the box is not the hull.
**Do not widen the acceptance test to make them pass.**

### Q27 — DONE 2026-08-29 BY CODE, AND HE BUILT IT BETTER THAN I SPECIFIED.
17 assertions, 0 failed. **The deploy is no longer gated on a red control.**

**WHAT I ASKED FOR** was a declared-exception list like the census's: name the
three, carry a reason. **WHAT HE BUILT** declares the whole TRANSITION and
verifies it — a declaration only excuses the movement it actually describes,
so `MISC Hull C:34` is recorded as *moved −1.27827 → −1.00356 and demoted to
est*, not as a bare port number. **And he added an assertion I had not thought
of:** a declaration that stops firing is itself a failure — *"a declaration
nothing fires is fiction."*

**I HAVE ADOPTED IT INTO `_verify_marker_census.py`.** My file has printed the
words *"a declaration that outlives its reason is how a real loss gets waved
through"* on every declaration since 2026-08-28 **and never enforced them.** A
declared hull that stopped losing markers simply stopped appearing, and the
entry sat there excusing nothing while looking like diligence. Twelve of the
thirteen declarations are waiting on models being re-exported — the day that
happens they all go stale at once and nothing would have said a word.

    13 declarations, 13 firing, 0 stale     PASS
    --self-test: drop caught, thin caught, grow allowed, stale caught, exit 9

**The stale rule has its own mutator** (restore a declared hull to its recorded
count and require a refusal) so it is not a branch nothing has ever entered.
**Credit is Code's; the gap was mine and it was open for a day.**

### Q27 (ORIGINAL) — the condition, kept for the reasoning.
**DONE-WHEN** `_verify_child_markers.py` passes without its baseline having been
silently re-taken.
**BLOCKED-BY** nothing. **This is the only thing holding the deploy.**

**YOU ASKED WHETHER LOSING `MISC Hull C:34` WAS INTENDED. YES — ALL THREE ARE,
AND HERE IS THE EVIDENCE RATHER THAN MY WORD.** The table in Q21 above gives
before and after for each. Two removals and one demotion from `cig` to `est`.

**AND YOUR CONTROL PROVED SOMETHING BIGGER THAN ITS OWN FAILURE.** Section 6
says 244 hulls changed and names exactly three moved markers. **A fleet-wide
change to the containment rule moved three markers and nothing else.** The four
pinned negative controls — ports 23, 24, 39, 40 — all hold. That is the
strongest evidence either of us has produced today, and it is in the output of
the check that is currently red.

**DO NOT RE-TAKE THE SNAPSHOT.** Absorbing a loss into a baseline is the failure
`_verify_marker_census.py` exists to prevent, and it would be the same failure
here. **Give the control a declared-exception list**, the way the census has
`allowed_losses` — three entries, each carrying its reason, printed on every run
afterwards so the change stays visible instead of becoming invisible.

**It is your file and the shape is your call.** If you would rather re-take the
baseline, say so and why, and I will not argue it twice — but say it in the
handoff, because a baseline re-taken quietly and a baseline re-taken on purpose
look identical six weeks later.

**I HAVE ALREADY DONE THE HALF THAT IS MINE.** `checks/marker_census.json` now
declares `BANU_Defender 10 -> 8` with its reason. `_verify_marker_census.py`
exits 0: *"PASS — no hull lost markers without saying so."* One red left.

### Q28 — THERE ARE TWO PLACEMENT WRITERS AND ONLY ONE OBEYS THE CONTAINMENT GATE
**DONE-WHEN** nothing yet — this is C1's to design, not Code's to fix. Recorded
here so it is not rediscovered.
**BLOCKED-BY** C1.

Chasing port 34 turned up the architecture rather than a bug. `hardpoints_fleet.json`
— written by `place_fleet.py`, the script four documents said did not exist —
is a **second, independent** placement source, and the fore/aft containment gate
lives only in `build_hardpoint_placement.py`. It never saw the fleet file.

    1,878 mounts in hardpoints_fleet.json
       43 outside the unit box
       33 of those aimed at a MEASURED extremity, all by 2.7-3.4%

**Those 33 are not the same defect as the Defender's 1.32 and must not be
treated as one.** `place_fleet.py` aims an extremity mount at the hull's own
outermost vertex and normalises by the longest half-extent, so a nose gun lands
at 1.0 by construction and the few percent over is a normalisation artifact of a
real vertex. The Defender's 1.32 was a fixed-fraction guess pointing at nothing.
**A gate at exactly 1.0 would refuse points that sit on the hull's own skin.**
`MARGIN = 0.06` already separates them correctly — checked, not assumed. **Do
not tighten it.**

### Q29 — THE SWEEP CANNOT SAY "I COULD NOT LOOK". TWO CONTROLS ALREADY TRY.
**DONE-WHEN** a control that exits 2 is counted as NOT RUN rather than FAILED,
and the DB-backed controls exit 2 with a reason instead of leaking a traceback.
**BLOCKED-BY** nothing. **Lower priority than Q27 — the gate is not weakened by
this and no deploy is held up by it.**

**YOUR OWN DOCSTRING IS RIGHT AND THE CLASSIFIER IS ONE STEP BEHIND IT.**

    ok = (code != 0) if args.self_test else (code == 0)     line 219

Zero or FAIL. NOT RUN is reachable only when the runner cannot launch the
process. **A control that starts, finds its resource absent, and says so has no
exit code that means what it is saying** — and two of them are already trying:

    _verify_community_mark.py    exit 2, "NOT PERFORMED ... never as a pass"
    _verify_panel_dismiss.mjs    exit 2 when Chromium is missing

Both print as `FAIL ... exit 2`.

**HOW I FOUND IT.** I ran the suite from the Cowork Linux VM, which has no
PostgreSQL, no Chromium and no PowerShell. 12+ DB controls, 9 browser controls
and `deploy_guards` all reported **FAIL**. Nothing was broken. Read that output
cold and you would go looking for twenty defects that do not exist — **which is
the same hour you lost to my wrong port number this morning, mechanised.**

`docs/FINDING_the-sweep-cannot-say-i-could-not-look-2026-08-29.md`.

**Do not make either state pass. Both must still count against the sweep.** The
only thing changing is which true sentence gets printed.

### Q30 — I OVERWROTE YOUR SWEEP RECEIPT. THE GATE CAUGHT IT.
**DONE-WHEN** your call — this may be correct as it stands.
**BLOCKED-BY** nothing.

`run_all_controls.py --only` writes the same `checks/.last_sweep.json` a full
sweep writes. My subset run destroyed the receipt from your 10:30 sweep.
**`sweep_gate.py` refused, exit 1:** *"the last sweep was PARTIAL (--only), so
most controls did not run. A subset is not a sweep."*

**The gate did its job and I am reporting this rather than quietly re-running.**
Your 10:30 receipt is gone; it needed re-taking after Q27 anyway, so nothing is
lost but the record of it. **One artifact, two writers, outputs not
interchangeable** — which is rule 14's shape even though it is one script. You
may decide fail-closed is sufficient. Say which, so the next person does not
rediscover it.

### Q31 — THE PUBLIC SOURCE SAYS HOW THE SITE IS BUILT. STRIP COMMENTS AT DEPLOY.
**DONE-WHEN** `checks/_verify_no_agent_traces.py` exits 0 against
`testing/_deploy`, three.js's `@license` header still present in `holo.html`,
and every page still renders and passes the existing controls.
**BLOCKED-BY** nothing. **This is Sleven's instruction, given directly
2026-08-29, and it jumps the queue: it is about what strangers can read.**

**HIS WORDS:** nothing on the public site may hint it was built by anything
other than a person — not the pages, and not the source behind them.

**THE PAGES THEMSELVES ARE CLEAN.** I rendered all seven in a real browser and
read every text node, title, alt, aria-label and meta tag. **Zero traces in
anything a visitor sees on screen.** No AI vendor named anywhere. The one
"C1" x28 is the Crusader C1 Spirit; "Copilot turret" is a seat; "DRACOWorker"
is three.js.

**VIEW-SOURCE IS A DIFFERENT STORY.**

    1,114 comment blocks - ~315,000 characters - shipped to every visitor
    45 traces in 12 files, EVERY ONE of them in a comment, none in the page

    "it is C1's file and not mine to edit"
    "loadout can point at this file whenever C1 wants. IT WANTS."
    "Agreeing with C1's call here, not overriding it."
    "C3's brief proposed shipping ..."
    Sleven quoted giving instructions, in five files
    ORDER_the-disclosure-bar-2026-08-27, FINDING_fixed-hardpoints-derived
    "rule 14", build_deploy.py, loadout.src.html

**Anyone pressing Ctrl+U reads a conversation between a person and several
named agents.** That is the whole of the problem and it is one problem, not 45.

**DO NOT HAND-EDIT 1,114 COMMENTS.** They are worth keeping — they are the best
documentation this project has. **They should not ship.** The fix is one step in
`build_deploy.py` (yours): strip comments on the way into `_deploy`, leave
`_src` untouched.

**TWO THINGS THE STRIP MUST NOT DO.**

1. **`holo.html` carries three.js's MIT header** — `@license Copyright
   2010-2021 Three.js Authors`. **Removing it breaches the licence the library
   is used under.** Keep any block matching `@license` or `@preserve`; that is
   the convention every minifier already follows and the control allows it.
2. **Do not touch `_src`.** The comments are the reason anyone can maintain
   this. Stripping at the source would be trading the documentation for the
   privacy, and we can have both.

**MIND THE `.gen.js` HEADERS TOO.** They open with `GENERATED by
testing/_src/build_deploy.py - do not hand edit`. Harmless-sounding, but it
names the build script and the repo layout on a public URL.

**THE CONTROL IS WRITTEN AND PROVEN** — `checks/_verify_no_agent_traces.py`
(C1's, in OWNERS.md). **RULE16: INDEPENDENT**, it reads the deployed bytes and
knows nothing about `_src`. `--self-test` plants all seven trace kinds and
catches all seven, and holds fire on five look-alikes including the C1 Spirit
and the MIT header. **It exits 1 today, by design.**

`docs/FINDING_the-public-source-reads-like-a-work-log-2026-08-29.md`

### Q33 — SUPERSEDED THE SAME DAY. USE WHAT THE GAME SHOWS, NOT WHAT I INVENT.
**DONE-WHEN** every name on screen is either CIG's own display string or
honestly our own words, and shorthand carries a hover explanation.
**BLOCKED-BY** nothing. **C1's.**

**I HAD THIS WRONG AND SLEVEN CORRECTED IT.** His rule, in his own words:

> *"if they use something in the codes or in the files, that's different than
> what the game uses. That's what we need to use. The words we use need to
> match the ones that the players would see in game. If a shorthand version of
> a word saves space and is generally well known, I would rather use that."*

**I had recommended expanding `mav` to "Maneuvering" across 348 labels, on
CIG's developer post.** Then I opened CIG's own localisation file:

    item_nameaegs_idris_mav_fixed_civ   ->   "Fixed Mav Thruster"
    itemPort_hardpoint_PDC              ->   "PDC"

**The game says "Mav Thruster" and "PDC" on screen.** Expanding either would
have moved us further from what a player sees, not closer. **The developer post
is the file side; `labels.json` is the game side, and the game side wins.**

**`labels.json` IS THE ANSWER AND IT HAS BEEN ON THE MACHINE ALL ALONG.**
90,363 entries in every snapshot - the strings the client actually renders.

    item_Name*    9,584 component display names
    itemPort_*      381 hardpoint display names, e.g.
                        "Weapon - Left Wing 01", "Missile Rack - Left",
                        "Shield Generator - Left", "Missile Attach Point 01"

**AND THE COVERAGE PATTERN IS ITSELF THE FINDING.** CIG localises what a player
can pick and nothing else:

    guns 41%  ·  PDC 39%  ·  weapons 34%  ·  shields 25%  ·  coolers 25%
    thrusters 0 of 941  ·  cargo grid 0 of 223  ·  fuel 0 of 74  ·  radar 0 of 15

**Zero of 941 thruster hardpoints have a name, because no player ever picks
one.** So "Thruster Mav Body Left Bot" is not a label to translate - **it is a
label the game never shows anybody.** Our own plain words are correct there, and
the page should say they are ours.

**THE RULE, THEN:** CIG ships a display string, we print it **verbatim**. CIG
ships nothing, we write plain English and own it. **Shorthand the game itself
displays stays, and gets a hover.**

### Q36 — VOID. THERE ARE NO MISMATCHED DOTS. THE 645 WAS MY MEASUREMENT.
**DONE-WHEN** nothing. **There is nothing to fix.** Kept so the number is not
quoted again by anyone reading back.

**I reported 645 markers (10.6%) on 59 hulls pointing at ports their ship's
parts list does not contain.** Sleven told me to fix them first. **Going to look
before changing anything is the only reason nothing was broken.**

**THE ERROR.** A marker's PortId is `3.loadout.0`. I compared
`PortId.split(".")[0]` — `3` — against the slot list. Port `3` is a turret
PARENT and is not itself a slot; **`3.loadout.0`, the gun inside it, is.** I
threw away the part of the identifier that made it resolve, then reported the
ones I had broken.

    matched on the ROOT of the PortId      645 orphans, 59 hulls
    matched on the FULL PortId               0 orphans,  0 hulls

**All 6,058 markers resolve to a real slot.** The Hammerhead's six turrets that
looked absent are ports 3, 4, 5, 54, 77 and 78, and every one of their guns is
in the list.

**THIS IS THE FOURTH WRONG NUMBER I HAVE PUBLISHED TODAY** — the port that was
never broken, the em-dash count that counted repeats, the off-hull dots that
were fine, and this. **Every one was a measurement that discarded something,
and every one read as a finding until somebody opened the data.**

**WORTH KEEPING FROM IT:** *"every drawn marker resolves to a slot on its own
ship"* is a real assertion and it passes today. It belongs in a control so a
future build cannot break it quietly. Folded into Q34's control rather than
given a file of its own.

### Q34 — 112 NAMES ON THE LIVE TEST SITE ARE WRONG, AND CIG'S OWN FILE SAYS SO.
**DONE-WHEN** `checks/_verify_display_names.py` exits 0.
**BLOCKED-BY** nothing. **This is live and visible. It jumps the queue.**

    61   items display CIG's own placeholder text: `<= PLACEHOLDER =>`
     6   truncated at an escaped quote - the game's MRX "Torrent" reaches
         the page as `MRX \`
    26   display a raw class name, underscores and all:
         MRCK_S04_KRIG_S65_Stingray_Left, Paint_Cutlass_Black_Procyon
    19   disagree with the name the game shows

**THE DISAGREEMENTS ARE NOT COSMETIC:**

    page: Aegis Gladius - Noise Launcher     game: Aegis Avenger - Noise Launcher
    page: VariPuck S6 Gimbal Mount           game: VariPuck S7 Gimbal Mount
    page: XIAN Scout CML Chaff               game: Aopoa Khartu-al - Noise Launcher
    page: MSD-481 Missile Rack               game: SNT-481 Missile Rack

**A part on a Gladius is labelled Avenger. A size 7 mount is labelled S6.** That
is the same defect class as Q1's armour naming, in a second place, and no
control has ever looked.

**61 PLACEHOLDERS ARE THE WORST OF IT** - they are paint names, and publishing
CIG's unwritten-yet marker as a product name is worse than an empty cell.

**THE CONTROL IS WRITTEN AND PROVEN** - `checks/_verify_display_names.py`
(C1's, in OWNERS.md). **RULE16: INDEPENDENT** - truth from `labels.json`, which
the build never reads. `--self-test` plants all four defects and catches all
four, and stays quiet on the three things it must tolerate: a name CIG does not
ship, shorthand the game itself shows, and a CIG name we already match.
**Exits 1 today, by design.**

`docs/FINDING_the-game-has-its-own-words-and-we-had-them-all-along-2026-08-29.md`

### Q35 — HOVER EXPLANATIONS FOR SHORTHAND. SLEVEN ASKED FOR THIS DIRECTLY.
**DONE-WHEN** any shorthand or jargon term on a page explains itself on hover
AND on tap, and the glossary has one writer.
**BLOCKED-BY** Q34. **Fix what the words ARE before explaining them.**

> *"If people have a question about, okay, what does this word mean? If they
> hover over the word a tiny little box pops up while they're hovering, that
> gives a description of what the actual word is."*

**ONE GLOSSARY FILE, ONE MECHANISM, EVERY PAGE.** Not per-page tagging - that is
five copies that drift, which is the mistake the disclosure bar already made
once. Terms come from the glossary; the pages carry no definitions of their own.

**MUST WORK ON TOUCH.** Hover alone hides the explanation from every phone. Tap
opens it, tap elsewhere closes it.

**MUST RESPECT THE ACCESSIBILITY MODES.** The site has dyslexia-friendly, low
vision and calm modes. A tooltip that ignores them is worse than none.

**Starting set, all confirmed against a source:** PDC, Mav, S1-S10, IR, EM, CS
(spell it out - most players read CrimeStat), RS, DPS (say burst or sustained),
alpha damage, SCU, aUEC, QT, QD, SCM, NAV, VLM, gimbal vs fixed mount,
hardpoint, ballistic, distortion.

### Q32 — I SAID 250. IT IS 20. THE COUNT WAS WRONG AND THE WRONG COUNT WAS MINE.
**DONE-WHEN** Sleven has seen the sample and ruled.
**BLOCKED-BY** Sleven. **Nobody rewrites site copy before then.**

**THE CORRECTION FIRST.** I reported *"~250 mid-sentence em-dashes, 171 on the
index alone"*. **I was counting rendered lines, and the index repeats the same
eight strings once per ship, 254 times over.**

    250   what I told Sleven          WRONG - counted repeats
    111   unique lines site-wide
     33   unique lines that are sentences at all
    ~20   where the dash is a writing habit rather than a separator

**About ninety of the hundred and eleven are label separators** doing the job of
a colon, and rewriting them would make the interface worse rather than less
AI-sounding:

    Aegis Dynamics · Cooler left — 23 fit
    Transponder — the game does not allow this to be changed
    Low vision — 150%, bold, high contrast, roomy rows

**Those stay.** A count that cannot tell a label from a sentence is not a
measurement, and I published one.

**THE REAL WORK IS 20 SENTENCES**, spread over loadout (8), download (3),
keybinds (4), find (3), index (1), stick-test (1). Every rewrite keeps the
meaning and roughly the length, and none touches a number, a ship name, or
anything a control measures. **All but the index line are in files C1 owns.**

**A before/after of all twenty went to Sleven 2026-08-29.** Nothing changes
until he says so.

**AND THE HONEST READ, WHICH IS NOT "YES REWRITE IT".** The copy names no AI,
uses no AI vocabulary, is specific, cites its sources and says plainly what it
does not know — which is the opposite of how machine-written filler reads.
**Nobody was going to guess AI from the punctuation.** The instruction was
*nothing that even hints*, and this is the one habit that hints, so it is worth
his ruling — but it was never the emergency my first number implied.

### Q23 — DONE 2026-08-29 as `d1e60b4`, ahead of Q21, on Sleven's direct instruction. NEXT COMMIT COVERS Q27 AND TODAY'S CENSUS DECLARATION.
**DONE-WHEN** the fore/aft change and today's docs are committed and pushed.
**BLOCKED-BY** Q21. Sleven's go-ahead from 2026-08-29 still stands and covers
this; it does NOT cover the live site.

**133 files are uncommitted** — the fore/aft change, three findings, an erratum,
and `checks/_verify_marker_spread.py`. Same rules: never `git add -A`,
`_to_delete/` is gitignored and stays out.


## Q20 — DONE 2026-08-29. Committed and pushed as `4710d30`. Kept for the rules it records; Q23 is the next commit.

**He was asked directly and answered yes.** That is the go-ahead rule 1 requires,
and it covers **committing and pushing to GitHub only** — not the live site,
which stays where it is.

    504 files uncommitted, everything since 1a1b4b7 yesterday morning

**NEVER `git add -A`.** Stage by path, the way you did for `1a1b4b7`.

**CHECKED BEFORE ASKING, so you do not have to re-derive it:**

    _to_delete/            gitignored - confirmed. It holds 5.2 GB, including
                           C1's model tarballs. It must not enter a commit.
    *.tgz, *.glb, models/  nothing of that kind is staged
    the only oddity        data-layer/derived/holo-hardpoints/
                           loadout_marker.pre-C1-20260829.js - your backup.
                           Your call whether it belongs in the history.

**AND ONE THING THAT WOULD HAVE STOPPED YOU DEAD.** C1's `git status` left a
`.git/index.lock` behind — the Cowork mount cannot delete files, so git could
not clean up after itself. It has been moved to `_to_delete/git-locks/`.
**If a git command ever fails with `Unable to create '.git/index.lock'`, that is
why, and moving the file is the fix.** C1 will stop running `git status` on that
mount.

**What is in this commit, in one line each** — the day is large and the message
should say so:

    the heap fix          10 hulls were drawing every dot in one clump, labelled
                          as CIG's own coordinates. Placement now refuses a model
                          it cannot orient. Root cause found and NOT fixed - see
                          the finding, it is a node-transform bug in glb_box.
    the deploy gate       proven on a real collision, then fixed twice: it
                          refused by crashing, and the control could not tell
    OWNERS.md             ownership became machine-readable; rule 14 enforced
    four new controls     marker provenance, marker census, marker spread,
                          identical options, swap loop
    Q7                    104 of 105 checks labelled for rule 16
    the contact sheet     295 ships photographed twice and every dot measured
                          against a clean silhouette of its own hull

**Verify after:** `git log --stat -1` names only files you expect, and nothing
under `_to_delete/`. **Nothing goes to the live site.** Going live is still off
the queue until Sleven raises it himself.

## THE BOARD, RECONCILED 2026-08-28 EVENING — READ THIS FIRST

**The queue had gone stale enough to waste your time.** Eight items were finished
and still reading as open. This is the state of every one, checked rather than
remembered, against a sweep that ran **105 of 105 green with 0 skipped and 0 not
run**.

    OPEN, IN THE ORDER I WOULD DO THEM  (reconciled 2026-08-29 14:25)
      Q21   rebuild + deploy: two ships show a dot in empty space
      Q22   the last rule-16 label            104 of 105 done
      Q23   commit again once Q21 is deployed
      Q5    roadmap watcher R1-R3             only R0 is done
      Q3    STATUS UNKNOWN - its DONE-WHEN names
            `checks/_verify_holo_placement.py`, which does not exist.
            Say what happened to it before doing anything.

    NOT CODE'S, AND NOT BLOCKED ON HIM
      the prices decision   Sleven's alone. 26,657 unverified rows.
      35 ships with no dots  DEFERRED by Sleven until the rest is finished
      3 ships with a stray dot  Corsair, Storm AA, Glaive - their dots are
                                INSIDE the hull box and still off the mesh,
                                which containment cannot catch. C1's, open.

    DONE, DO NOT RE-DO
      Q1    armour naming        _verify_armour_naming.mjs green
      Q2    failed build blocked  superseded by Q10's gate, proven on a real collision
      Q4    disclosure bars       _verify_disclosure.mjs green
      Q6    collector selftest    575 checks, 0 failed, on Windows 2026-08-27
      Q8    stage-still + mutators  C1 ran it in a real browser
      Q9    placed_from in markers
      Q10   the deploy gate       and it caught a live collision today
      Q11   craft_data wired      it is in the deployed payload
      Q12   the 41 hulls verified C1 photographed all 295 ships, 0 failures
      Q14   N9 assertions removed _verify_ship_page.mjs 242 green
      Q16   the rebuild
      Q17   identical-options line  built, deployed, verified on the served site
      Q18   deployed-site controls  ran, 3 of 3 passed

**Q12 is closed by a contact sheet, not by a check.** Every ship with a model —
295 of them — was loaded in a real browser and photographed with its markers
showing. **2,309 dots, 0 failures. 26 ships show no dots and 25 have at least
one estimated dot.** Sleven has the sheet and is reviewing it. **Ships with no
hardpoints are DEFERRED by his instruction** — finish everything else first.

**Nothing here is committed.** 174 files, all of today. Committing is fine when
you reach a clean stopping point; pushing to the live site is not, and going
live is still off the queue until Sleven raises it.


### Q1 — 31 SHIPS PRINT ANOTHER SHIP'S NAME ON THEIR ARMOUR. LIVE AND VISIBLE.
**DONE-WHEN** the armour heading is derived from the SHIP, not from the item's
own `Name`, and no ship page prints an armour name naming a different ship.
**BLOCKED-BY** nothing. **This jumps the queue: it is on a page people look at.**

Source: `HANDOFF_weapon-armour-shield-package-for-c1-2026-08-27.md` (C3),
measured on disk, every claim naming its file.

`build_loadout_data.py:740` takes the armour's display name from the item's own
record, and **that field carries the wrong ship's name on 31 of 91 named armour
records - 34%.**

    ARMR_RSI_Perseus       prints  "Constellation Andromeda Ship Armor"
    ARMR_AEGS_Idris_P      prints  "Hammerhead Ship Armor"
    ARMR_ORIG_890J         prints  "350r Ship Armor"

**Scope it honestly: the NUMBERS ARE RIGHT.** The page resolves armour through
each ship's own `Loadout`, so no ship is showing another ship's multipliers.
It is a labelling bug. **But it is on a page whose entire claim is that the
numbers can be trusted, and it says the wrong ship's name out loud.**

**DO NOT FIX THIS BY CORRECTING 31 STRINGS.** Derive the name from the ship.
C3's join is a literal dictionary lookup on a UUID string - wiki
`vehicle.armor.uuid` against `stdItem.UUID` - **285 of 285, 100%, no
normalisation, no lowercasing, no token containment, no fuzzy anything.** It
also covers the 118 placeholder records, which correcting strings never would.

Spot check to reproduce before trusting it: Avenger Stalker →
`b3b23908-e9ab-4c46-93ed-ecd20aaf65c3` → `ARMR_AEGS_Avenger_Stalker` →
Deflection Physical 11 / Energy 9. Both sources agree on every value.

**The control: assert that no rendered armour heading names a ship other than
the one whose page it is on.** That check must go red on the current build -
if it does not, it is not testing the defect.

**Read §7 and §8 of the handoff before starting.** C3 records one thing it got
wrong (Deflection was already built) and that every number in it is **patch
4.9**. And §3 says to CANCEL any "compare shields by damage type" feature -
there is nothing to show. Do not build it.

### Q2 — A FAILED BUILD MUST NOT REACH A DEPLOY
**DONE-WHEN** a build that exits non-zero cannot be followed by an upload in
the same invocation, and the refusal names the build's exit code.
**BLOCKED-BY** nothing.

Found by Code on itself, 2026-08-27: build and deploy chained in one command,
`BUILD EXIT=1` printed, deploy read only its own output and put twelve wrong
models live. **The check Code had written was green, so the thing being watched
agreed with him, and the gate that disagreed was in the output he skipped.**

Q4 put the BROWSER checks in front of the upload. Nothing puts a FAILED BUILD
in front of it, **and a deploy legitimately does not require a build** - so the
gate cannot simply be "a build must have run". It has to be: *if a build ran in
this invocation and failed, stop.*

**The control: chain a deliberately-failing build to a deploy and assert the
upload does not happen.**

### Q3 — SCALE THE 12 FROM `model_scaled.glb`, NOT FROM `model.glb`
**DONE-WHEN** the 12 pre-existing wrong-scale models are at their published
dimensions AND `_verify_model_scale.py` still exits 0.
**BLOCKED-BY** nothing.

**C1 NAMED A CHECK FILE THAT DOES NOT EXIST.** This item's DONE-WHEN said
`_verify_holo_placement.py` "still passes all 8 checks". **There is no such
file in `checks/` and there is no evidence there ever was.** Anyone taking this
item had an unverifiable finish line and no way to know it without going to
look — the second time today one of my DONE-WHENs sent someone at a thing that
was not there. The real control is `_verify_model_scale.py`, which reports
findings and never rescales, per the auditor rule.

Code's finding: he rescales from `sc-ships/<ship>/model.glb`, but the deployed
model came from `model_scaled.glb`, and **for some ships those two are not the
same geometry.** Scaling the original therefore produced a hull with a
different bbox centre and half-extent ratio than the markers were derived
against - San'tok.yai off by 29.6%, Vulture 8.5%.

**Scale from `model_scaled.glb`.** It preserves the exact geometry every
downstream artifact was derived against: the hull-geometry boxes, the marker
`unit` values, C1's hardpoint placement scale, and the camera-fit band. The
alternative - rescale then regenerate - is a four-step chain, and for hulls
with no real CGA coordinates it would re-derive GUESSES against a moved hull,
which is churn without gain.

**And the cost of the safe option is zero.** Code's own words: the 12 being
wrong-scale *"is visible to nobody - the viewer frames the camera to whatever
it loads."* There is no reason to take the risky path for an invisible defect.

### Q4 — THE DISCLOSURE BAR ON THE OTHER THREE PAGES
**DONE-WHEN** `_verify_disclosure.mjs` is green with every explanation block on
`find`, `keybinds` and `index` collapsed, and D1 still green.
**BLOCKED-BY** nothing.

The loadout page is the reference implementation and it is built and deployed.
**Eleven amber blocks remain** — keybinds x5, index x4, find x2.

**Audit each one against the rule before touching it, and record the verdict
per block.** Collapse a block that EXPLAINS. Never collapse one that WARNS,
reports an ERROR, or states WHAT THE VISITOR IS LOOKING AT. The download
page's antivirus notice, find's error and empty states, and the keybinds
capture warnings are all NEVER. **A block collapsed that should not have been
is a warning nobody reads.**

### Q5 — THE ROADMAP WATCHER: R1 AND R2 ARE BUILT. ONLY R3 IS LEFT.
**DONE-WHEN** the watcher can answer *"what has CIG announced since the patch
our data was verified against"* — R3 — and says so in its own output.
**BLOCKED-BY** nothing.

**RE-SCOPED 2026-08-29 after checking rather than assuming.**
`checks/_verify_roadmap_watch.py` declares itself *"R1/R2 of AMENDS..."* and is
green in the 106-of-106 sweep, including the negative assertion that a
`time_modified`-only change produces silence. **R0, R1 and R2 are done.** This
item was carrying all three as if none had been started.

**R3 IS THE ONLY REMAINING PIECE AND IT IS A DIFFERENT QUESTION FROM THE ONE
THE SITE ALREADY ANSWERS.** Every row carries `last_verified_patch` — what our
data was checked against. The watcher answers the other half: what CIG has
announced since. **Do not fold R3 into `last_verified_patch`; they are siblings,
not the same field.**

**Scope guard from the amends, unchanged:** the API is the route, never article
text; a roundup URL may be recorded as a pointer for a person, never as
evidence; the watcher REPORTS and never acts. Whether a roadmap change alters
what this site does is Sleven's call.

Key on card presence plus a payload hash. **Never on `updateDate`** — the API
returns Aug 2024 for a card the UI renders as Aug 2021.

### Q6 — RUN THE COLLECTOR SELFTEST. FIND OUT WHAT FAILS.
**DONE-WHEN** `go build` and `.\collector.exe --selftest` have been run and the
result is written down — pass, fail, or could-not-run with the reason.
**BLOCKED-BY** nothing.

**~190 checks have never been executed once.** That is why `capture_keys`
shipped dead in every build. The old reason was that no Claude session could
run a Windows binary — **that is stale for Code**, which ran
`venv\Scripts\python.exe` and `powershell` today.

**Do not write another collector check until these run.** If they cannot run,
the reason is the deliverable.

### Q19 — REBUILD ONCE MORE, AND ONE OPTIONAL FIX THAT IS YOURS
**DONE-WHEN** a rebuild has run against today's placement and
`_verify_marker_provenance.py` and `_verify_marker_spread.py` both exit 0.
**BLOCKED-BY** nothing. **Two controls are RED and both are stale-build, not
defects — read this before treating either as breakage.**

**WHAT HAPPENED.** Ten ships were drawing every hardpoint dot in a single clump
the size of a cockpit, and the page labelled all of them `cig` — CIG's own
published coordinates. The Tiburon put all seventeen in one heap.

**Four green controls let it through.** Containment passed, because a heap is
inside the box. The mirror passed, because a heap is symmetric. Provenance
passed, because the labels honestly described where the numbers came from. The
census passed, because nothing was lost. **It took photographing all 295 ships
to see it.**

The cause: the scale rule matches CIG's Length to the model's Z extent, and **19
of 258 models measure taller than they are long** — the Mantis is 1680 x 2965 x
630. On those the scale came off the wrong axis.

**Placement now refuses a model it cannot orient.** You rebuilt at 03:18 against
an earlier, two-signal version of that guard; it has since been made strict, so
the derived data no longer carries Pitbull, Railen, San'tok.yai, Reliant, M80 or
Starlite and **the deployed marker file still does.** That is the entire content
of both red controls. One rebuild clears them.

    python checks/_verify_marker_provenance.py    expect 0 after the rebuild
    python checks/_verify_marker_spread.py        expect 0 after the rebuild
    python checks/_verify_marker_spread.py --self-test   expect NON-ZERO

**Every marker loss is already declared in `checks/marker_census.json` with the
reason**, so the census will report them and not block you.

**ONE CONTROL OF YOURS NEEDS ITS BASELINE MOVED, AND ONLY YOU SHOULD DO IT.**
`_verify_child_markers.py` asserts *"every marker that existed before is still
there, unmoved"* and is now red, naming the Tiburon, the Railen, the Reliant
Kore, the Khartu-al, the San'tok.yai and the rest. **It is right.** Those markers
were removed on purpose — they were the heap — and its baseline predates the
removal.

C1 has not touched it. Re-baseline it against the rebuilt payload, and **read
the list it prints before you do**: every name on it should be one of the 16
orientation-refused hulls. If any other ship appears there, something else moved
and that is the finding, not the baseline.

**THE ROOT CAUSE IS FOUND AND DELIBERATELY NOT FIXED, WHICH IS WORTH YOUR
JUDGEMENT.** The placer reads the model's box from raw accessor bounds and
ignores node transforms; three.js applies them. On a rotated model the two are
different objects:

    Mantis.glb   raw accessor bounds   1680.4 x 2964.9 x 629.8
                 with node transform      30.0 x    6.4 x   17.0
    CIG's own dimensions                 30.0 /   17.0 /    7.5

The transformed box matches CIG's published Length and Width **exactly**. C1
implemented the transform and reverted it: applying node scale also changes the
box for every model carrying a `CC_SCALE_ROOT`, and the run that followed refused
the Vulture, the Polaris and the Starlancers — **200+ working hulls destabilised
to rescue 16.** It needs a change-and-compare loop across all 295 ships, which is
a session's work with a build in it, and the build is yours.

## THE OPTIONAL PART, AND IT IS GENUINELY YOURS

**The M80 and the Starlite heap on the page and pass the placer's own
measurement.** The placer measures every mount; the page draws one dot per mount
ROOT and picks the shallowest. A couple of outliers the visitor never sees push
the placer's number above the line.

**The right place for that test is the emitter, where PortIds exist** — the
grouping the page uses cannot be reconstructed from CIG node names in the
overlay, and I am not going to approximate it. That is `build_deploy.py`, which
is yours.

Roughly: group the emitted markers by `PortId.split(".")[0]`, take the shallowest
of each, and if a hull's drawn dots span less than 0.47 of it while its model
measures taller than it is long, drop that hull's CIG markers and let it fall
back to estimates. **`_verify_marker_spread.py` already computes exactly this**
and will tell you if you have it right.

**Take it or leave it.** The control catches them either way; the difference is
whether the sweep goes red or the build quietly does the right thing.

### Q7 — LABEL EVERY CHECK THAT CANNOT MEET RULE 16
**DONE-WHEN** every check in `checks/` either draws its truth from a real
source or carries an UNPROVEN label naming what it could not reach.
**BLOCKED-BY** Q6 for the collector's set.

Rule 16 is adopted. This is the cost of adopting it, and it makes the board
look worse before better — that is the point. A silent gap becomes a labelled
one.

**Standing at 2026-08-27 22:51: 29 labelled, 68 to go, 0 malformed.**

### Q8 — DONE 2026-08-28 BY C1, IN A REAL BROWSER. NOT YOURS ANY MORE.
**Do not run this. It has been run.** Clean and all three mutators, in headless
Chromium, on the 400i.

    clean                    13 of 13 assertions pass
    --mutate-pan             2 red - camera moved tx 0 -> 12.65, px 53.9 -> 66.5
    --mutate-alwaysright     2 red - a LEFT marker opened the panel right
    --mutate-opaque          2 red - hull alpha 1, material not transparent

**Each mutator went red in its own section and nowhere else.** The thing Sleven
asked for most plainly — *"I really want the ship to stop shifting"* — is now
proven, not asserted: the camera is byte-identical before and after a marker
click, and a second marker on a different mount does not move it either.

**HOW, because the reason C1 could not do this for two days was wrong in a way
worth writing down.** The blocker was never "no browser". It was three things
that each looked like the same wall:

    checks/.playwright-browsers holds a WINDOWS headless shell   cannot exec on Linux
    the Cowork VM's allowlist refuses cdn.playwright.dev         cannot download one
    C1's own container HAS Chromium, at a path and build number
      playwright will not find by itself                         cannot launch it

**One environment variable closed it.** `_verify_stage_still.mjs` now honours
`CC_CHROMIUM` (executable path) and `CC_NO_SANDBOX`. Unset, behaviour is
identical to before, so nothing about your runs changes.

    CC_CHROMIUM=/path/to/chrome CC_NO_SANDBOX=1 node checks/_verify_stage_still.mjs

**SEVEN OF THE NINE PLAYWRIGHT CONTROLS NOW RUN AWAY FROM YOUR MACHINE** and
all seven pass: `_verify_stage_still`, `_verify_armour_naming`,
`_verify_disclosure`, `_verify_settings_revision`, `_verify_panel_dismiss`,
`_verify_marker_positions`, `_verify_camera_framing` (34 assertions).

**The two that do not are honest about why:** `_verify_model_scale` and
`_verify_imported_models` need the whole 458 MB model library, not a sample.
Those stay yours until somebody decides that transfer is worth it.

**The other six checks launch Playwright with a hardcoded path and were run in
C1's sandbox with a symlink rather than by editing your files.** If you want
them portable too, the same two lines drop into each — C1 has not touched them.

### Q9 — PUT `placed_from` IN THE MARKER FILE — DONE, AND IT WAS WRONG ON 41 HULLS UNTIL 04:45
You built it and it works. **C1 then measured what it emitted and found the
field lying about 41 hulls**, which is on C1, not on you — the emitter reads
`placed_from` correctly and nothing was writing it for those records.

`build_deploy.py` stamps `placed_from` in one place: the loop that MOVES an
existing marker onto an overlay position. **41 hulls never enter that loop** —
they have no marker record to move a port on, so they arrive as whole records
through `fleet_records_client.json`, already on CIG's decoded coordinates, and
the stamp never touched them. 335 CIG-published mounts across 57 page classes
reached the visitor labelled `est`.

**Fixed in `build_hardpoint_overlay.py` (C1's file), not in yours.** It now
stamps `"placed_from": "client"` on the records it emits — the field you already
read. **No change to `build_deploy.py` and none wanted.**

Your rebuild has already picked it up. Measured on the emitted file:

    cig  1,691 -> 2,026        est  448 -> 113        anc  4,261 unchanged
    page classes with every top-level mount on CIG coords   205 -> 244
    page classes with none                                   45 -> 6

Full working: `docs/FINDING_the-page-called-335-cig-mounts-estimates-2026-08-28.md`.

### Q12 — DONE 2026-08-28 BY C1. ALL 295 SHIPS, NOT JUST THE 41.
**Do not run this.** Every ship with a model was loaded in headless Chromium and
photographed with its markers rendered — the served page, not a model of it.

    295 ships photographed    2,309 dots drawn    0 failures
    26 ships show no dots     25 have at least one estimated dot

Sleven has the contact sheet. **Ships with no hardpoints are DEFERRED on his
instruction** until everything else is finished — do not start on them.

The original text follows for the record.

### Q12 (ORIGINAL) — PUT THE 41 CLIENT-RECORD HULLS THROUGH THE BROWSER CONTROL
**DONE-WHEN** the 41 hulls that arrive through `fleet_records_client.json` have
been through `_verify_marker_positions.mjs` (or whatever it has become), and the
result is in a handoff by name.
**BLOCKED-BY** nothing. It needs a browser, which is on your machine.

**WHY.** `checks/_verify_marker_provenance.py` — new, green, self-test decisive
— proves every one of the 2,026 mounts the page calls CIG's **sits on its own
hull's CIG coordinate**. It proves nothing about whether that coordinate renders
where the mount actually is. `_verify_marker_positions.mjs` covers the 166
overlay hulls; **the 41 client-record hulls have never been through it**, and
they are exactly the ones whose provenance was wrong for a day.

That is not a caveat to file. It is the thing that would catch a 42nd hull
arriving mis-scaled with a confident `cig` label on every dot.

**Also run it once with the new control:**

    python checks/_verify_marker_provenance.py              expect exit 0
    python checks/_verify_marker_provenance.py --self-test  expect NON-ZERO

**The self-test's exit code is inverted on purpose** and the banner says so —
`run_all_controls.py --self-test` requires a non-zero exit from every control.
It returns 9 when both mutations are caught and **0 when a control has gone
inert**, which is the outcome to be alarmed by.

**ORDERING, so nobody reads this as a deadlock.** `sweep_gate.py` stops an
unswept payload from uploading, and a fresh control can only go green against a
freshly built payload. **Build, then sweep, then deploy.** If the sweep is run
against a stale `_deploy/`, this check reports the defect it was written for and
is correct to. Do not silence it to clear a board.

### Q13 — POINT YOUR DRIFT DETECTION AT `OWNERS.md`
**DONE-WHEN** whatever fired on 2026-08-27 at 22:10 and 22:15 reads
`OWNERS.md` to decide whether a write was a collision, and stays quiet for a
write by that path's declared owner.
**BLOCKED-BY** nothing.

**WHAT HAPPENED AND WHOSE FAULT IT WAS.** Your detector fired on C1's writes to
`testing/_src/cc_viewer.js` and `testing/_src/loadout.src.html`. **Both were
already C1's** — in `NEXT.md` and in `CURRENT-STATE.md`, for weeks. **Your
detector was right to fire and right by accident**: it had no way to know, and
neither list was in a form a program could read. That is C1's fault, not yours.

**Fixed.** `OWNERS.md` is now the single machine-readable manifest —
`## <OWNER>` headings, four-space-indented paths, one entry per path. The prose
list in `NEXT.md` is **deleted**, not duplicated, and
`checks/_verify_owners.py` fails if it grows back.

    python checks/_verify_owners.py              expect exit 0
    python checks/_verify_owners.py --self-test  expect NON-ZERO

It found two real problems on its first run: a path C1 had guessed at that does
not exist, and eleven entries where the prose list had fallen behind. That is
the whole argument for the file.

**If you disagree with an ownership line, say so in a handoff and do not edit
around it.** Moving a path between owners is a decision and goes in a dated
`docs/DECISION_*`.

### Q14 — DELETE THE THREE MARKER-NOTE ASSERTIONS FROM `_verify_ship_page.mjs` N9
**DONE-WHEN** the N9 block no longer asserts the marker note's wording, and the
suite is green again.
**BLOCKED-BY** nothing. **Two N9 assertions are RED right now and that is
deliberate — read this before treating it as breakage.**

**WHAT CHANGED AND WHY IT HAD TO.** The marker note said *"this page cannot yet
tell you which of the two you are looking at on this particular ship"* — for a
full day after **you built the field that answers it**. Q9 gives every dot its
own provenance. The note is now per-ship and exact:

    all CIG's     "All 7 dots on this model come from the game's own geometry."
    a mixture     "12 of the 18 dots ... The other 6 have no position ..."
    none          "This dot is estimated."

and the six estimated dots on the Hammerhead say so in their own tooltip and
accessible name. **No sentence on the page quotes a fleet-wide number any
more.** A reader is looking at one ship.

**THE TWO RED ASSERTIONS ARE N9 DEFENDING THE OLD WORDING**, correctly, because
nobody told it. They are:

    /cannot yet tell you which/          now false on every ship
    /name/ && /snapped/ && /estimate/    now only true on ships that HAVE an
                                         estimated dot, which the all-CIG test
                                         ship does not

**DELETE THOSE TWO, AND THE THREE ABOVE THEM** (`note.length > 200`,
`game's own geometry`, `not estimated`). All five now live in
`checks/_verify_marker_note.mjs`, which C1 owns, and which asserts more than
N9 did: it computes the expected counts from `loadout_marker.gen.js` by
re-implementing its grouping rule, so the page and the check reach the number
by two routes.

    node checks/_verify_marker_note.mjs                      17 pass
    node checks/_verify_marker_note.mjs --mutate-fleetwide   7 must go red
    node checks/_verify_marker_note.mjs --mutate-blind       7 must go red
    node checks/_verify_marker_note.mjs --self-test          NON-ZERO

**KEEP THE REST OF N9.** Its three "the old sentence is gone from everywhere"
greps are still doing real work and are not duplicated anywhere.

**WHY C1 DID NOT JUST EDIT YOUR FILE.** N9's own header says it was rewritten by
C1 on 2026-08-27 — one artifact, two writers, which is what `OWNERS.md` and Q13
exist to end. Doing it again to save you five minutes would have been the fourth
time this project paid for that habit.

**AND A CONTROL CAUGHT ITS OWN AUTHOR AGAIN, worth two lines.** The first draft
of `_verify_marker_note.mjs` tested the note's HTML with regexes that could not
cross a line break, because the note is an indented template literal. That
showed up as one honest red assertion — **and as a silent GREEN one**, in the
section asserting a phrase was ABSENT. A regex that can never match passes every
negative test in a file. Whitespace is flattened once, at the top, now.

### Q15 — `clearTimeout` IS MISSING FROM `_loadout_harness.mjs`
**DONE-WHEN** the harness's window stub carries a `clearTimeout` and
`node checks/_verify_swap_loop.mjs` stops reporting two NOT PERFORMED lines.
**BLOCKED-BY** nothing. It is one line.

The stub has `setTimeout` and not `clearTimeout`. `markChanges()` calls
`clearTimeout(changedTimer)` **only when a timer is already pending** — which
means only on the SECOND stat change in a session. **Every existing control
makes one change and stops, so nothing has ever reached that line.**
`_verify_swap_loop.mjs` makes several and does.

The undo itself is unaffected — the build reverts correctly — but the render
after it is cut short, so anything read from the DOM afterwards is stale. That
control reports those two assertions as **NOT PERFORMED rather than failed**,
because reporting a harness gap as a page defect sends somebody after a bug
that is not there.

    clearTimeout: () => {},        // or drop the id from `timers`

**Worth a moment before you write it:** if the stub instead REMOVED the pending
callback, `flushTimers()` would stop running a callback the page had cancelled —
which is closer to a browser and would catch a different class of defect. Your
file, your call; a no-op closes Q15 either way.

### Q16 — REBUILD: THE PLACEMENT MOVED, AND ONE CONTROL IS RED UNTIL YOU DO
**DONE-WHEN** `build_deploy.py` has run against today's placement and
`python checks/_verify_marker_provenance.py` exits 0.
**BLOCKED-BY** nothing. **Read this before treating the red as breakage.**

The frame proof changed (M4). Three hulls moved: **the Glaive is in**, both
**Clippers are out**. `build_hardpoint_overlay.py` has been re-run and the
derived files are current; the DEPLOYED marker file is not.

So `_verify_marker_provenance.py` is red, naming the Clippers: their dots are
still in `loadout_marker.gen.js` labelled `cig`, and the hull that justified
that label is now refused. **That is the check doing its job — the page is
claiming CIG provenance for a hull we no longer stand behind.** It clears on the
rebuild.

**Ordering, again, because `sweep_gate.py` makes it matter: build, then sweep,
then deploy.** A control written against a fresh payload cannot go green against
a stale one.

**A second control now guards this rebuild, and it is the one the pipeline
proposal asked for.** `checks/_verify_marker_census.py` holds a per-hull marker
count recorded BEFORE your rebuild, and refuses on any hull losing dots.

    python checks/_verify_marker_census.py              expect exit 0
    python checks/_verify_marker_census.py --self-test  expect NON-ZERO

**The two Clipper losses are already declared in `checks/marker_census.json`
with the reason**, so they print every run instead of blocking you — a declared
loss stays visible, an absorbed one does not. **Anything else that loses markers
is not declared and will stop the run. That is the point.** Do not rebaseline to
get past it; `--rebaseline` prints what it is about to absorb, and absorbing a
loss is how a hull goes missing for a month.

This closes the stated precondition of
`PROPOSAL_the-marker-pipeline-is-four-layers-deep-2026-08-27` §3 — *"a control
that counts markers before and after and refuses on any loss... the condition of
doing it at all."* **The collapse itself is still Sleven's decision and has not
been made.**

### Q18 — RUN THE THREE DEPLOYED-SITE CONTROLS. THAT IS THE WHOLE ITEM.
**DONE-WHEN** `python checks/run_all_controls.py --include-deployed` has been
run and the three deployed controls have reported a real verdict.
**BLOCKED-BY** nothing. **It has never been blocked by anything.**

    python checks/run_all_controls.py --include-deployed

**WHAT THIS ITEM SAID AN HOUR AGO WAS WRONG, TOP TO BOTTOM, AND THE ERROR IS
WORTH MORE THAN THE ITEM.**

It claimed the testing site sits behind Cloudflare Access, that three controls
had never run because they could not authenticate, and it sent Sleven into the
Cloudflare dashboard to create a service token. He went looking, could not find
the menus, and said so — which is the only reason this was caught.

**C1 read a 403 and inferred a lock without ever reading the response body.**
The body says:

    x-deny-reason: host_not_allowed
    Host not in allowlist: citizencompasstesting.citizencompass-contact.workers.dev.
    Add this host to your network egress settings to allow access.

**That is C1's own sandbox refusing to make the request. It never left the
building.** Nothing about the site, nothing about Cloudflare, nothing about the
password. The same wall is why `_verify_find_deployed.mjs` reports `fetch
failed` on the Cowork VM: that VM has its own allowlist too.

**And the three controls are not blocked at all.** They are in `NEEDS` in
`run_all_controls.py`, skipped unless `--include-deployed` is passed, **and the
reason is written right there** — they make ~450 network requests and click
1,200 markers over the wire, so they are opt-in rather than part of every sweep.
**Deliberate, documented, and C1 read past it.**

**Code's machine has ordinary internet.** One flag answers the question that
started all of this — *how much of what we built is actually on the test site* —
and no dashboard, no token, and no password is involved.

**THE LESSON, because this is the third time this week.** A number or a barrier
that gets repeated stops being examined. C1 saw "403", reached for the most
technical explanation available, wrote an order around it, and got a person to
go looking for menus that do not exist in his account. **The body of the
response said what was wrong in one sentence and nobody read it.** Read the
error before theorising about it.

### Q17 — BUILD AND DEPLOY THE IDENTICAL-OPTIONS LINE
**DONE-WHEN** the testing site shows it and
`node checks/_verify_identical_options.mjs` exits 0 against the built page.
**BLOCKED-BY** nothing. Page source is done and green; it needs a build.

**Sleven approved it directly on 2026-08-28.** Where every part a port offers is
identical on every figure CIG publishes, the picker now says so instead of
sitting silent:

> **These 3 are identical on every stat the game publishes.** Different names
> and makers, the same numbers all the way across — so this one is yours to
> pick on looks or on price.

Both surfaces carry it — the pane picker and the stage dock — from one function.

    node checks/_verify_identical_options.mjs                    10 pass
    node checks/_verify_identical_options.mjs --mutate-always    section C red
    node checks/_verify_identical_options.mjs --mutate-never     3 red
    node checks/_verify_identical_options.mjs --mutate-name      3 red
    node checks/_verify_identical_options.mjs --self-test        NON-ZERO

**A mount that carries other parts is excluded, and the control is why.** The
first build put the line on the Sabre's missile mount: 39 racks, all mass 20 at
size 4, identical by the part table — and named "Gatac Missile Rack 8xS1" and
"20xS3" on screen. A rack's real difference is its child ports, one level down.
**True of our data, visibly false to a player.** Ports with children now say
nothing.

**Everything else on the page is unchanged** — 35 harness controls run, 35
green, including `_verify_ship_page.mjs` and `_verify_swap_loop.mjs`.

### Q11 — WIRE `craft_data.gen.js` INTO THE BUILD (ONE LINE, PLUS A TAG)
**DONE-WHEN** a part in the ship page's picker that has a recipe shows its
craft time and materials, and one that has none shows nothing at all.
**BLOCKED-BY** nothing.

C1 built `build_crafting_demand.py` and the page code. **452 of the 3,283 parts
a reader can fit are craftable**, joined on CIG's own `Output.Class`,
case-folded, exact. The page function is already in `loadout.src.html` and
**returns an empty string when `CRAFT` is undefined**, so nothing changes until
you wire it and nothing breaks if you never do.

    deploy_pages.py    add craft_data.gen.js to PAGES
    loadout.src.html   a script tag before the page script
    build_deploy.py    python build_crafting_demand.py --emit-js=<path in _src>

**Shape is yours** — C1 has not touched `deploy_pages.py` or `build_deploy.py`
and will not while rule 14 is unsettled.

### Q10 — THE DEPLOY GATES ON 4 CONTROLS OUT OF 98
**DONE-WHEN** a payload with ANY red control cannot be uploaded, and the run
that proves it is a deliberately-reddened control that stops a deploy.
**BLOCKED-BY** nothing.

    controls that exist                             98
    controls the deploy actually gates on            4
      _verify_armour_naming · _verify_disclosure
      _verify_panel_dismiss · _verify_settings_revision

`run_all_controls.py` appears in `build_deploy.py` exactly once, **in a
comment.** It is not a gate anywhere.

**THIS ALREADY BIT AND NOBODY NOTICED.** On 2026-08-27 the sweep found **14
failures at 22:15**, and the site was built and deployed repeatedly that same
evening. The controls existed, they were red, and nothing stopped anything. A
suite that cannot stop a deploy is documentation.

**THE COST IS REAL AND IS YOURS TO DESIGN AROUND.** The sweep takes 613s. Ten
minutes on every deploy is not obviously right — caching the result against the
payload's own hash and refusing when the cache is stale is one answer, running
the fast subset on every deploy and the full sweep on a schedule is another.
**C1 is not going to pick; you own the deploy scripts and you have just spent a
day inside them.** What is not acceptable is 94 controls that cannot stop
anything.

**This is the most durable thing on the board.** Once a red control cannot ship,
that property holds for the life of the project without anyone remembering it.

---

# C3'S QUEUE

### R1 — TEN MINING PAGE DESIGNS
**DONE-WHEN** one document in `inbox/` carries ten concepts, each with the
seven fields the order names, ranked, with a first pick and a reason — plus the
separate list of what cannot be built yet and what it would need.
**BLOCKED-BY** nothing. Every figure the order quotes is on disk today.

Raised by Sleven: *"design 10 deeply detailed ideas on how to build a page for
mining... creative and somewhat interactive and easily used with a visually
appealing HUD."*

Full order: `docs/ORDER-C3-design-ten-mining-page-concepts-2026-08-28.md`.

**The three traps it names, because they have each already caught somebody:**
prices are a community source with 0 of 26,657 rows verified and CIG ships none
at all; `commodity_trade_locations.json` is tag-derived CAPABILITY and a
"Security Checkpoint" appears to trade all 109 commodities; and the site's
standard is that a page says what it does not know.

---

# C1'S QUEUE

### M17 — THE PAGE CALLED 335 CIG MOUNTS "ESTIMATES" — DONE 2026-08-28 04:48
**Found by re-measuring a number in `CURRENT-STATE.md` instead of quoting it.**
The document said 245 classes fully on CIG coordinates and 20 with none.
Counting the file the browser actually loads gave **205 and 45**. The gap was a
defect nobody had a check for.

`build_deploy.py` stamps `placed_from` only where the overlay MOVES an existing
marker. **41 hulls never enter that loop** — they arrive as whole records, on
CIG's decoded coordinates, and the stamp never reached them. Every top-level dot
on 57 page classes said `est`.

**Fixed in `build_hardpoint_overlay.py`, which is C1's**, by writing the field
Code's emitter already reads. **`build_deploy.py` untouched — rule 14 intact.**

    cig  1,691 -> 2,026     est  448 -> 113     anc  4,261 unchanged
    classes fully on CIG coordinates   205 -> 244        with none  45 -> 6

**New control, and it caught its own author first.** `_verify_marker_provenance.py`
asserts both directions — no dot on a CIG coordinate may be called an estimate,
no dot called CIG may sit anywhere else. **The first draft used one fleet-wide
coordinate set and produced 38 false positives** (Prowler, Starlancer TAC, every
Apollo and Zeus): `anc` child ports whose ring offset landed on a number that is
a CIG coordinate on a DIFFERENT ship. Now scoped per model file, `anc` excluded
by definition.

**Its `--self-test` asserts a delta, not a verdict**, because when the check was
written it was already red and a mutator that only has to make it fail would
have been inert — the same trap as `_verify_stage_still.mjs` the day before.
Relabelling every `cig` to `est` must produce EXACTLY 2,026 under-claims, and
does. **That is the strong result: all 2,026 are on their own hull's CIG
coordinate, and nothing is over-claimed.**

**What it does NOT prove:** that those coordinates render where the mount is.
The 41 client-record hulls have never been in a browser. **Q12.**

### M1 — THE THREE REMAINING EXPLANATION BLOCKS — DONE 2026-08-27
All converted to disclosure bars. Zero `.trip` blocks remain on the page and
the rule itself is gone (see M7).

### M2 — THE LOADOUT BENCH — IT WAS BUILT. WHAT WAS MISSING WAS ANY PROOF IT WORKS. DONE 2026-08-28
**This entry said "approved after seven prototypes and never built" and that was
wrong.** The loop Sleven asked for is in the page and has been: the picker, the
delta chips, the ledger with per-port revert, the swap log, undo on a button and
on a key. **Reading the source instead of the queue took four minutes.** The
entry had been carried forward unexamined, which is the same fault as the marker
numbers in M17.

**What was genuinely missing is that nothing drove it as a loop.**
`_verify_ship_page.mjs` N10 and N11 come closest and both set `A[slot]=alt`
**directly** — which proves the render paths and steps over the entire
interaction, because none of the click, log or undo code runs when the build is
written behind its back. **A page whose swap handler was deleted outright passes
N10 and N11.**

**`checks/_verify_swap_loop.mjs` — new, C1's, 27 assertions, green.** Every part
change is a click dispatched through the page's own delegated handler. It never
writes to `A[]` and never calls `logSwap` or `undoSwap` itself.

    1. selecting a port offers parts, including the ones it is about to fit
    2. a click fits it, logs exactly one entry, and moves NO other port
    3. the readout marks what moved - and stays silent when nothing did
    4. undo returns that port, empties the log, and withdraws itself
    5. after TWO swaps, ONE undo returns the FIRST part, not stock
    6. undo on an untouched build changes nothing and does not throw

**Section 5 is what the file is for.** Undo is a step, not a reset. A page that
treats it as "back to stock" is right on the first swap and wrong ever after,
and the first swap is the only one anybody tests by hand. `--mutate-undoreset`
plants exactly that bug and **fails exactly one assertion — that one.**
`--mutate-nolog` fails eight.

**THREE THINGS THIS FOUND ALONG THE WAY, all recorded in the file:**

- **A gap in the shared harness.** `_loadout_harness.mjs` has `setTimeout` and
  no `clearTimeout`. The page calls it only on the SECOND stat change in a
  session, so no control has ever reached that line. **Q15.**
- **Two assertions in this control were wrong before they were right**, and
  both were caught by running it: one read the picker from `#picker` when the
  chosen port docks to `#cc-panel`, and one demanded that every swap move a
  number — the swap it chose was between two racks with identical stats, and
  the page was correctly silent. **The assertion is two-sided now:** the mark
  must be there exactly when there is something to mark.
- **A "product observation" that was entirely my own bug — RETRACTED 2026-08-28.**
  This item said *"no alternative the picker OFFERS changes any number in the
  readout"* and it went to Sleven twice as a design question about the bench.
  **It was false.** Two faults, either of which alone caused it:
  the search walked only the first eight swappable ports per ship, and on every
  hull those are racks, missiles and turrets — **guns sit at position ten and
  were never reached**; and `changesANumber` compared `g(...)` to the STRING
  `"true"` when the harness returns a real boolean, so **it answered false on
  every port on every ship, forever.**

  **Measured properly: a swap moves at least one readout figure on 773 of 813
  ports across 25 ships.** Guns, missiles, turrets, coolers, shields, power
  plants, radars and quantum drives all respond, every port. **The bench does
  what it was built to do.**

  What is actually true, and it is small: **flight blades (12 ports), salvage
  heads (6) and most bomb racks show nothing — because CIG publishes no figure
  on which the options differ.** All three flight blades on the Avenger are
  em 0, ir 0, mass 35, power 4, size 1. Identical. The page is being honest.
  The only open question is whether it should SAY so.

### M3 — HARDPOINT COVERAGE — SUPERSEDED, see M8, M10, M11, M12, M13
This item's numbers are from before any of tonight's work and reading them now
would send someone after problems that no longer exist. **Current state: 245 of
the ship page's classes have every marker on CIG coordinates, 20 have none, and
each of those 20 has a written reason.** M13 carries the list.

### M8 — THE ACCEPTANCE TEST JUDGED THE WRONG FRAME — DONE 2026-08-27 20:15
`build_hardpoint_placement.py` measured mounts against the hull box **as the
file stores it**; `cc_viewer.frame()` recentres every hull on that box before
drawing it. **71 of 258 models are not centred on their own origin**, so those
were judged in a frame nobody renders. M2 Hercules 11/149 inside → 140/149, the
C2's number exactly, on identical decoded data. Four Constellation variants now
agree where one used to disagree.

Passed 138 → 139 (gained M2, Valkyrie, SRV; **lost Aquila and Spirit A1** —
their offsets were flattering them). Overlay 952 → 939 ports; new records 29 →
30 hulls / 2,612 ports.

**I also broke the gate and a check I had just written caught it.** Making it
proportional — refuse above half, withhold ports below — lets a **transposed
lateral/vertical axis pass on every hull tested**, because ships are wider than
they are tall and the swap only displaces about a sixth of the mounts. That is
the defect the gate exists for. Reverted, and the reasoning is recorded in the
source so nobody re-derives it.

New: `checks/_verify_placement_gate.py` — three broken frames plus a negative
control, no database, no browser. Exits 0.

**Two more defects found while looking, both silent:**
- The same ship placed twice under two spellings (`ANVL_Hornet_F7A_MK1` and
  `anvl_hornet_f7a_mk1`), the guard comparing exact strings, both writing the
  same file. Manifest said 182 ships for 180 files. Claims fold to lower case.
- **The overlay reads the placement DIRECTORY, not its manifest**, so a refused
  hull kept its file from an earlier run and kept being emitted. The run
  reconciles its directory now and exits fatally if it cannot — proven by a
  planted control, not asserted. 93 stale files moved to
  `_to_delete/hardpoint-placement-stale-2026-08-27/`.

**Final: overlay 93 hulls / 955 ports · client records 30 hulls / 2,612 ports ·
ship page 163 → 165 classes fully on CIG coordinates · 304 client markers, none
emitting zero.**

**Two broken models, not ours:** `Avenger_Stalker.glb` is a tenth the size of
its own siblings; `Aurora_SE.glb` is 87.6 wide against 8.2 for every other
Aurora.

### M10 — THE HULL RULE WAS BLIND TO 15 SHIPS — DONE 2026-08-27 19:45
`build_hardpoint_transforms.py` takes the `.cga` whose stem equals a contiguous
run of its own folders. **120 of 18,891 entries, and right about all 120** — the
archive is mostly bunk beds and dashboards. But CIG does not always name a
folder for the ship inside it:

    AEGS\Sabre\AEGS_Sabre_Raven.cga          MISC\Freelancer_v2\MISC_Freelancer.cga
    ORIG\300_Series\ORIG_300I.cga            AEGS\Idris_Frigate\Exteriors\AEGS_Idris.cga

**Second rule added: exact equality against CIG's own `ClassName` list in
ships.json.** An authority, not a pattern — it cannot admit a prop because
there is no ship class called `aegs_hab_bunkbed_sq_player`. Javelin and Basher
are ambiguous (two paths each, one under `dmg`) and are dropped and named.

    transforms  116 -> 135 hulls      placement 146 -> 160, 137 -> 150 passed
    overlay     93/955 -> 106/1,082   ship page 165 -> 181 classes on CIG coords

Newly real: the whole Freelancer family, Cutlass Black and Red, Constellation
Aquila and both Phoenixes, 300i, Sabre Raven, Vanguard Hoplite, Fury LX,
MPUV 1T.

**The 4.10 snapshot landed mid-run.** `build_hardpoint_placement.py` takes the
newest by design, so hulls are now scaled against 4.10 lengths and the
manifest's `dimensions` points there. Nobody chose it; the newest changed.
Acceptance still 150/160. Flagged to Code rather than left in a diff.

### M16 — CRAFT OR BUY — DATA AND PAGE DONE 2026-08-27 23:25
First of the economy features from `BRIEF_stop-being-a-better-list`.

**`build_crafting_demand.py`** reads CIG's 1,607 recipes — every one with a
craft time, a requirement tree and a dismantle yield — and emits four files
plus a page-ready `craft_data.gen.js`.

    ship-page parts that are craftable   452 of 3,283
    materials in the demand table         37
    Aslarite  856 recipes · Ouratite 495 · Laranite 353 · Tungsten 266

**Three rules written into the generator, not assumed:** the join is
`Output.Class` case-folded and exact (the display-name route is REFUSED — it
adds 34 and one is a different class sharing a name); SCU and item counts are
never summed; tier 0 only, because higher tiers double-count.

**The page line is inert until Code wires the data** — `craftLine()` returns an
empty string when `CRAFT` is undefined, so the page ships either way. Q11.

**Still homeless:** `CRAFT_DEMAND`, the fleet-wide mining answer. It wants a
page of its own and that is a bigger conversation than one line.

### M14 — SLEVEN'S THREE FIXES FROM THE LIVE PAGE — DONE 2026-08-27 22:45
He watched the deployed 400i and gave three instructions.

**1. The ship stops shifting.** The cause was `panelPlacement` preferring the
RIGHT, so the viewer panned the hull LEFT to make room. `setObstruction` still
records the coverage but no longer touches the camera; `reframe()` no longer
shifts.

**2. The panel opens on the marker's own side of the screen** — his rule, in
his words. Two stable rails, not a panel that lands somewhere new each time.
The old "never cover the marker" rule is retired deliberately: it is what forced
the panel to the far side, which is what forced the ship to move.

**3. The hull is see-through**, as a control rather than my taste.
`CC_HOLO.hullAlpha`, default 0.86, fourth slider labelled **See-through**. At
1.0 the material returns to genuinely opaque. Saves with the other appearance
keys; an older save without it simply gets the default, so nobody's settings
are discarded.

**And the page was lying about its own best work.** The provenance note still
said the dots are name-derived and "not measured from the model" — false for
1,693 mounts across 166 hulls. Rewritten to say the measured part is measured,
the fallback is still an estimate, and that it cannot yet tell you which this
ship's are. **Asked Code for the one field that fixes that**: `placed_from` as a
fourth element in `loadout_marker.gen.js`.

**Re-baselined, all mine:** `_verify_stage_panel`, `_verify_ship_page` (N9),
`_verify_marker_coverage`, `_verify_marker_absence`, `_verify_look_panel`.

### M15 — AND I CLOSED MY OWN RULE-12 GAP — DONE 2026-08-27 22:45
I reported that "the ship did not move" reports NOT PERFORMED in the script
harness, and said browser checks were Code's. **Wrong — `_verify_panel_dismiss`
is mine, so a sibling is too.**

New: `checks/_verify_stage_still.mjs`. Real Chromium, real 400i, reads the whole
camera before and after a click, clicks a second marker as well, and finds a
dot each side of centre to prove the panel rule both ways.

**`--mutate-pan` nearly shipped inert.** As two separate mutators both would
have passed — restoring the shift alone moves nothing on a click, and making
setObstruction call reframe alone re-centres on the centre. E4 is one defect and
is planted as one, with every edit required to apply.

**I have never run it** — no headless Chromium in the Cowork VM. It reports NOT
PERFORMED at the launch step. **The first real run is Code's**, and the mutators
are the part that matters.

### M12 — CIG'S OWN RECORD NAMES THE HULL — DONE 2026-08-27 20:30
I wrote in M9 that ships.json carries no geometry path and that I had checked
every field. **I checked for a PATH. The answer is a NAME, one level down.**

    anvl_c8_pisces  ->  Parts[0].Name == "ANVL_Pisces"

309 of 318 classes carry a part-tree root; 183 name a hull other than
themselves. It reaches what no name rule could — `ANVL_C8_Pisces ->
ANVL_Pisces`, `RSI_Ursa_Medivac -> RSI_Ursa_Rover`, `GRIN_MDC -> GRIN_MXC`.
**Replaced the `cls + "_"` prefix expansion**, and it is safe where the earlier
name-expansion was not: only ports whose HardpointName is a node in that hull
are placed, so a module-specific mount gets no position rather than a wrong one.

Root names fed back into the decoder too — a name CIG uses as a root IS a hull
name, which picked up `AEGS_Idris`. One collision needed a tie-break: a
folder-rule path (name AND location agree) beats a class-name-only one. Equal
evidence still drops both.

### M13 — HALF THE FLEET WAS IN A TREE NOBODY SCANNED — DONE 2026-08-27 20:32
`Data\Objects\Spaceships` 23,083 entries, scanned. **`Data\Objects\Vehicles`
1,762 entries, never.** Ground vehicles live there. Cyclone, Storm, Nova, Ursa,
Ballista, Centurion, Spartan, Lynx were all "no .cga anywhere" for that reason.

    transforms 116 -> 153 · placement 146 -> 284 converted, 137 -> 277 passed
    overlay    93/955 -> 167 hulls / 1,720 ports
    ship page  165 -> 245 classes fully on CIG coordinates · 91 -> 20 with none

**The 20 remaining, each with a reason:** ATLS family (a power suit, under
Characters\PowerSuit), GRIN MDC/MTC/ROC (no exterior mount at all), three
Cyclone variants (records name no decoded root), Javelin (two paths, equal
evidence), Glaive and Scythe (asymmetric), MOTH, Starfarer Gemini. **None is a
guess waiting to be taken.**

### M11 — NINE OF TEN REFUSALS WERE A POSE, NOT A FRAME — DONE 2026-08-27 19:58
Reading *which* mounts were outside settled it: the Constellation's three are
the top-turret mounts 0.53–0.71 above a 13.2-tall hull; the Reliant's are its
wing-tip guns and its wings move. Refusing the whole hull threw away 19 good
Constellation ports to avoid 3 arguable ones — **and the fallback was worse than
what was refused.**

**The gate did not loosen.** Second signal: exterior left/right pairs must all
mirror in the converted frame. **A transpose destroys it (0 of N on every hull);
a uniform scale does not touch it.** Complementary to containment by
construction, not by argument.

**The check refuted me again mid-build.** `out == 0 or proven` let a full-hull
offset and a 4x scale through on the Eclipse and Sabre — mirroring survives
both. Bounded by an absolute count of **4**: pose mismatches run 1–3, the
smallest frame error observed is 23. Below the defect, not above it — the
opposite of the proportional gate I had to revert.

    placement 146 -> 160 converted · 137 -> 157 passed · 3 failed
    overlay   93/955 -> 112 hulls / 1,164 ports
    ship page 165 -> 182 classes fully on CIG coordinates, 84 with none

**Still refused, each with a checkable reason:** ARGO_MPUV_Transport (no
exterior mount at all), VNCL_Glaive (2 of 4 pairs mirror), VNCL_Scythe (1 of 4).

**The two Vanduul are NOT a bug — they are asymmetric ships.** Looked at:
the Glaive's "right" missile rack sits at **negative X**, on the left side of
the hull, and its wing guns are 12.9 m apart fore-and-aft, while its nose guns
and countermeasures mirror exactly. **`VNCL_Blade` mirrors perfectly** on all
four pairs from the same decoder in the same run, so the decode is sound.

The cost is real — the Glaive loses 9 good ports over 1 mount outside — and it
is left that way deliberately: the mirror cannot prove the frame of a ship that
is not symmetric, "at least one pair" is unsafe (a transpose left 1 of 39
matching by accident on the Reclaimer), and anything between one and all is a
threshold on a four-pair sample. **What would settle it is a frame proof that
does not assume symmetry.** Written up so nobody hunts a decode bug that is not
there.

### M9 — THE UNREACHABLE 82 — RE-MEASURED 2026-08-28, AND THE PROBLEM IS NOT WHAT THIS ITEM SAYS
**Do not go looking for the 91 classes this item used to name.** It was written
before M10 and M11 landed and before the provenance defect was found, and its
numbers described a page that no longer exists.

**Counted today from the emitted marker file, which is what a visitor loads:**

    page classes with every top-level mount on CIG coordinates   244
    mixed, cig + derived                                          21   (88 mounts)
    no CIG mount at all                                            6

The six are `VNCL_Glaive` and `VNCL_Scythe` (asymmetric, placement correctly
refuses them — see M4), `GRIN_MTC`, `MISC_Starfarer_Gemini`, `TMBL_Cyclone_MT`,
`TMBL_Cyclone_TR`.

**What survives of this item, and it is worth keeping.** The structural
`HardpointName` join is still not refereed by anything, and the reason it was
stopped still stands: partial coverage looks convincing, containment is
one-sided, and **a wrong hull that is merely larger passes**. Nothing today
changed that. What changed is the price of leaving it alone: it now buys 88
mounts on 21 hulls instead of a third of the fleet, and **the 88 are labelled
`est` on the page and say so**, which is the honest outcome.

**Do not widen anything to close it.** If it is ever reopened, the entry cost is
a second independent signal that must agree with the structural one — not a
threshold.

### M4 — THE GLAIVE WAS NEVER ASYMMETRIC — DONE 2026-08-28
**The frame proof was filtering out the evidence that proves the frame.** The
mirror ran over EXTERIOR mounts only; the Glaive has almost no exterior named
pairs, and its engines, coolers, intakes and powerplants mirror to within 8.7 cm.
2 of 4 became **13 of 19** the moment the filter came off. The Scythe, refused in
the same sentence, is **1 of 16 and genuinely is asymmetric** — one explanation
had been covering two different ships.

**New rule: at least 4 named pairs, at least half mirrored.** A fraction invites
one objection — that it was fitted to let a wanted ship in — so it was measured
across all 265 hulls with 4+ pairs, and again on every one with the axes
transposed:

    transposed axis, highest fraction reached      0.455
    correct frame, lowest fraction above midpoint  0.684
    at a HALF rule    clean 262 of 265    transposed 0 of 265

**Nothing sits between 0.455 and 0.684.** The per-pair tolerance is untouched —
M4's own warning was never the lever.

**Then the control found something older.** Six subjects taken in directory
order are not adversarial, so the fleet's worst hull was pinned in by name — and
it reported that **a transposed San'tok.yai passes the gate.** Not the new rule's
doing: the mirror was only ever consulted when something was already outside the
box, and nothing leaves that hull's box when its axes swap, because it is nearly
as tall as it is wide. **The mirror is now a veto as well as a licence.**

    VNCL_Glaive                     refused -> passed, 1 mount withheld
    drak_clipper (x2)               passed  -> refused
    VNCL_Scythe                     refused -> refused, now for a measured reason
    60 hulls gained a proven frame  and not one changed verdict

**The two Clippers are the cost and the cost is the point.** A rule that admits
the Glaive on its mirror has to refuse the Clipper for the lack of one.

Full working: `docs/FINDING_the-glaive-was-never-asymmetric-2026-08-28.md`.

### M5 — `CURRENT-STATE.md` — SPLIT, DONE 2026-08-27 20:45
**It is no longer eleven days stale.** It was brought forward earlier today and
now leads with 08-27 material. The staleness half of this item is closed and I
am not going to keep claiming it.

**The structural half stands and is worse than the staleness was.** 13,554
words, ordered newest-first, opening with an instruction that everything below a
certain point is history. A reader cannot tell where that point is, so the only
safe read is all of it, every session, forever.

**One live number was wrong and is fixed rather than filed against.** Line 79
said *"ten distinct damage-multiplier profiles"* since 08-22. Three independent
counts say **eight** (`FINDING_both-open-questions-closed...`). Corrected in
place with the correction visible, not silently.

**DONE.** Split into two files, nothing deleted:

    docs/CURRENT-STATE.md                      1,487 words - only what is true
    docs/STATE-ARCHIVE-through-2026-08-27.md  13,801 words - the original, verbatim

The new one carries no "later section wins" rule because it has no later
sections. **It states its own maintenance rule: it does not grow by appending.**
A fact that stops being true is edited or deleted there, and the reasoning goes
in a dated `docs/FINDING_*` or `docs/DECISION_*`. A snapshot, not a log.

The archive's header names its own known-stale parts up front — the collector
section saying "none of it has run on Windows" when it passed 575 checks today,
and hardpoint numbers from before tonight — so nobody has to discover them.

Both written to the claude.ai project as well, since the project instructions
point new sessions at `claude/CURRENT-STATE.md`.

### M6 — THE SHIELD SENTENCE — DONE 2026-08-27 18:20, AND C3'S NUMBER WAS WRONG
C3 ranked *"a shield stops all of a laser's damage and only 45% of a
ballistic's"* first of six things to build, ahead of everything needing a
calculator. **The energy half is exact. The ballistic half is the top of a
range** — `Absorption.Physical` reads Minimum 0, Maximum 0.45, and Energy is the
only channel where the ends meet. Measured by me on 73 shield items, one profile
across all of them.

**And shields carry a second `Shield.Resistance` block** — physical 0–0.25,
distortion 0.75–0.95 — which is NOT the `Durability.Resistance` that
`FINDING_both-open-questions-closed` established as item durability. Different
block, different path. The effective-damage calculator stays blocked.

**Shipped the honest version** on the ship page under the armour matchup table,
stamped `SHIELDS · 4.9`, with the range as a range. Full working:
`docs/FINDING_the-45-percent-is-the-top-of-a-range-2026-08-27.md`.

### M7 — THE DISCLOSURE CSS IS ONE COPY AGAIN — DONE 2026-08-27 18:10
Code extracted my `.disc` rules into `testing/_src/_disc.css` for find, keybinds
and index, and left this page's copy alone because it is not Code's file —
noting loadout could point at the file whenever C1 wanted. **It wanted.** The
rules were diffed first (identical, line for line; only comments differed), then
replaced with the build's `/* CC_DISC_CSS */` marker. The dead `.trip` rule went
with it — zero elements carried the class.

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

## WHO WRITES WHAT — `OWNERS.md`

**The list that used to sit here is gone, and its absence is the point.**

On 2026-08-27 Code's drift detection fired on C1's writes to
`testing/_src/cc_viewer.js` and `testing/_src/loadout.src.html`. Both were
already C1's — here, and in `CURRENT-STATE.md`, and had been for weeks. Nothing
was in conflict. **Two sessions were reading two prose lists, and Code's tooling
could not read either.**

So the list moved to `OWNERS.md`, which a program can parse, and this section
became a pointer rather than a second copy. **Rule 14 is one writer per
artifact, and the ownership list is an artifact.**

`checks/_verify_owners.py` holds it to that: every owned path must exist, no
path may be claimed twice, and **this file must not enumerate paths again**. If
it starts to, the check fails and names the lines.
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

*Maintained by C1. Last set 2026-08-28 04:48 UTC.*
