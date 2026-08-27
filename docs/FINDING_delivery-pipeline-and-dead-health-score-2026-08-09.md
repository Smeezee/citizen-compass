# FINDING — the inbox pipeline silently drops code and never overwrites a corrected doc, two canonical documents are currently stale because of it, the malformed `data-layerrawhardpoints/` path is now load-bearing in real code, and the project health score has been structurally incapable of moving for as long as the Go port has existed.

    from      C3 (Cowork), 2026-08-09
    for       C1 + Sleven
    method    read logs/inbox_watcher.log, watcher-go/ccpp.go, watcher-go/classify.go,
              build_ship_component_schema.py, citizen-compass.ccpp, and the repo tree
              on the project machine. Every number below was read, not estimated.
    scope     C3 does not write outside inbox/ and data-layer/derived/. Nothing here
              has been fixed by me. This is a report and a recovery list.

---

## 1. THE HEADLINE — five files from today's work order never reached the repo

Work order 1 (`inbox/WORKORDER_swap-the-exporter-2026-08-09.md`) tells Code to install four
files. **None of them is where the order says.** From the watcher's own log:

    15:52:48  sc_export2.js      -> _needs_review\sc_export2.js      (unrecognized extension '.js')
    15:53:15  roundtrip.js       -> _needs_review\roundtrip.js       (unrecognized extension '.js')
    15:53:42  mutate.js          -> _needs_review\mutate.js          (unrecognized extension '.js')
    16:15:27  real_export.xml    -> _needs_review\real_export.xml    (unrecognized extension '.xml')
    16:15:53  real_export2.xml   -> _needs_review\real_export2.xml   (unrecognized extension '.xml')

**The work order is currently unexecutable.** C1's prompt for Code compounds it by stating
the fixtures are "now at `testing/_src/fixtures/real_export2.xml`" — they are not, and Code
following that prompt would find nothing there.

Two more from the same batch landed in odd places rather than being dropped:

    15:54:09  place_hardpoints.py -> citizen-compass\place_hardpoints.py      (repo ROOT)
    15:54:36  hardpoints.json     -> citizen-compass\data-layerrawhardpoints\ (malformed path, §4)

The four `.md` documents filed correctly. **The pipeline handles prose and loses code.**

## 2. The watcher never overwrites — so a correction never becomes canonical

The behaviour is deliberate and the log states it every time:

    doc (name collision, kept both — old file untouched)

Never destroying a file is the right instinct and I would not change it. But nothing tells
anyone a newer version exists, so **the stale copy keeps the canonical name and the
correction gets a timestamp suffix nobody opens.** Five occurrences on record; two are live
right now and both matter:

**`docs/CURRENT-STATE.md`** — 72,057 bytes, missing the entire build-pipeline section.
The current version is sitting in `docs/CURRENT-STATE__20260809162225.md` (74,027 bytes).
Confirmed by grep: the string `THE BUILD PIPELINE, READ AND WRITTEN DOWN` appears **zero**
times in the canonical file.

**`docs/RULING_reference-archive-collect-but-quarantine.md`** — still contains, at lines
31–33, the test-site / password-gate argument **Sleven explicitly instructed be dropped**.
I removed it and re-delivered on 2026-08-08 at 17:22; that corrected version has been
sitting in `RULING_..__20260808172218.md` ever since, unread, while the retracted argument
kept the canonical name for a full day.

**This is the failure mode that matters most.** A doc that is merely missing is obvious. A
doc that is confidently wrong, under the right filename, is not.

The claude.ai project copies of both are correct and current. It is the on-disk copies —
the ones Code reads — that are stale.

## 3. Where the routing rule actually bites

The classifier routes by extension and content shape. `.md` is understood. `.py` is a
"script". `.json` gets content-sniffed. **`.js` and `.xml` are understood as nothing**, and
`_needs_review/` is gitignored, so a dropped file is simultaneously out of the repo, out of
git, and out of sight.

The project's own convention already says work goes through `inbox/`. That convention is
sound for documents and silently broken for the code those documents describe.

## 4. The malformed path is not a spill — it is load-bearing

Three malformed directories exist at repo root, all missing separators:

    data-layerexports                        empty, 28 Jul
    data-layerprocessedhardpoints_by_type    empty, 28 Jul
    data-layerrawhardpoints                  185 MB, in active use

**`data-layer/raw/hardpoints/` does not exist.** The malformed folder is not a duplicate of
a correct one — it is the only place that data lives.

And it is referenced by name in working code. `build_ship_component_schema.py`, line 44:

    SHIP_SPECS_PATH = PROJECT_ROOT / "data-layerrawhardpoints" / "ship_specs.json"

The header comment documents the bad path as if it were the design. A copy of the same
script carries the same hardcode inside `.claude/worktrees/`.

The directory is in `.gitignore` at line 34, so `git status` cannot see it. `ship_specs.json`
is 185,305,277 bytes, dated 26 July, and `CURRENT-STATE.md` already records it as
**295 ships of scraped spec data — "do not bin it."**

**So this is no longer a cosmetic path bug. A typo has become an interface**, with a
185 MB dataset behind it and a script depending on it. That raises the cost of fixing it
and lowers the cost of leaving it, which is exactly how bad paths become permanent.

## 5. The health score cannot move, and has not been measuring anything

`LATEST_HANDOFF.md` has printed **35.0/100 three hundred times today**. It is not a plateau.
It is a constant, and all three components are broken independently.

**Data completeness — structurally pinned at 0.** `calculateScores()` in `watcher-go/ccpp.go`
looks for a data layer whose *name* contains "raw":

    for name, data := range p.Inventory.DataLayers {
        if strings.Contains(strings.ToLower(name), "raw") { dataFiles = data.FileCount; break }
    }
    p.Scores.DataCompleteness = minF(100, round1(float64(dataFiles)/232*100))

But the cataloguer registers **exactly one** layer, and it is called `data-layer`:

    catalogDataFolder(p, dataDir, "data-layer")

No name contains "raw", so `dataFiles` stays 0 and the score stays 0 — **regardless of the
data**. The packet currently reports that single layer holding **60,703 files and 10.4 GB**.
Ten gigabytes of real data scoring zero percent complete.

The same dead lookup empties the crossref: `data_files_by_category` is `{}` in the live
packet, where it should hold raw / processed / exports counts.

**Viewer progress — measured against a test fixture.** `shipsDir` is
`tests/testing-site/ships`, which holds **4 ships**. The packet reports
`ships_with_viewers: 2 of 4 = 50%`. The real catalogue is 316 ships and lives in `sc-ships/`.
The 50% is 2 of 4 in a scaffold folder.

**Documentation — pinned at 100 since the fifth document ever written.**
`min(100, len(docs)*20)`, and there are 759 markdown files. It has been maxed out for months
and can never say anything again.

The arithmetic confirms all three:

    0.0 x 0.40  +  50.0 x 0.50  +  100.0 x 0.10  =  35.0

**Every input is broken and the output looks like a plausible number.** That is the worst
shape a metric can take, and it is the same silent-success pattern this project has now
logged repeatedly. It should either be fixed or removed from the handoff — a number that
cannot move is worse than no number, because it invites people to read meaning into it.

My best guess, and it is a guess: the Python original counted per-layer folders and the Go
port flattened cataloguing to one entry without updating the scorer. `ccpp.py` lines 234–242
carry the same `/232` divisor with the comment "based on weapon hardpoint files", so the
divisor is probably stale too — the project is at 295–316 ships, not 232.

## 6. Recovery list — what needs moving, by hand, before Code can start

C1's lane, not mine. Nothing here is a code change:

    _needs_review\sc_export2.js     -> testing\_src\sc_export.js         (rename SCX2 -> SCX)
    _needs_review\roundtrip.js      -> testing\_src\roundtrip.js
    _needs_review\mutate.js         -> testing\_src\mutate.js
    _needs_review\real_export.xml   -> testing\_src\fixtures\real_export.xml
    _needs_review\real_export2.xml  -> testing\_src\fixtures\real_export2.xml

    docs\CURRENT-STATE__20260809162225.md                     -> becomes CURRENT-STATE.md
    docs\RULING_reference-archive-collect-but-quarantine__20260808172218.md
                                                              -> becomes the canonical RULING

    place_hardpoints.py   currently at repo root; belongs wherever derivation scripts live
    hardpoints.json       currently in the malformed folder; see §4 before moving anything

**Do not re-drop the code files into `inbox/`.** They will be routed to `_needs_review/`
again. This is the loop to break, not to repeat.

## 7. What I would do, and the alternatives

**On the pipeline.** Three options, and I would take the first.

*Teach the classifier the extensions it is missing* — `.js`, `.xml`, `.ts`, `.css` — with a
destination that is inside the repo and visible to git. Small, fixes the root cause, and
keeps one delivery path for everything. Against it: it is a change to a running service
that currently works for its main job.

*Stop sending code through `inbox/` and hand it over another way.* Cheapest today, and it
splits the delivery path in two, which is how the WO-UI-01 loss happened in the first place.
I would not.

*Leave it and remember.* Free, and it depends on every future session knowing a rule that
is written down in exactly one place. It has already failed once today.

**On collisions**, the fix is not to start overwriting. It is to make a collision **loud** —
one line in `LATEST_HANDOFF.md` naming the superseded file, so a stale canonical doc cannot
sit unnoticed for a day. Keep-both is right; keep-both-and-say-nothing is not.

**On the malformed path**, the honest options are to fix the generator and migrate — which
means touching a 185 MB file and a script that hardcodes the bad name — or to accept the
name as the interface and rename it deliberately so it stops looking like a bug. Doing
neither is the current state and is the one option with no upside. I lean to fixing it,
because a path that is a typo will be re-created by the next tool that gets it right.
**But `ship_specs.json` should not be moved by anyone who has not first confirmed nothing
else reads it** — I checked `.py`, `.go`, `.md` and `.json` under the repo and found only
`build_ship_component_schema.py` and its worktree copy, but my grep timed out twice against
the full tree over the device mount and I would not call that exhaustive.

**On the health score**, fix it or drop it. If it is fixed: name the data layers per folder
so the "raw" lookup finds something, point `shipsDir` at the real catalogue, replace the
documentation component with something that can vary, and revisit the 232 divisor. If that
is not worth the time — and it may not be — remove it from the handoff rather than keep
printing a number that has never described the project.

## 8. What I checked and what I did not

**Checked:** the full inbox watcher log, including every collision entry back to 2026-08-05;
the classifier's routing decisions for all nine files I delivered today; the presence and
contents of the three malformed directories; `git check-ignore` on each; the scoring
functions in `watcher-go/ccpp.go` against the live `citizen-compass.ccpp` packet, with the
arithmetic reproduced; `shipsDir` traced to its definition; `build_ship_component_schema.py`
line 44 read directly.

**Did NOT check:**
- **I have not fixed anything.** Every item in §6 is outside my lane.
- Whether the `.gitignore` entry for the malformed folder was a deliberate decision or a
  tidy-up. I can see the line; I cannot see the intent, and I am not going to guess at it.
- Whether anything outside `.py/.go/.md/.json` reads `ship_specs.json`. Two full-tree greps
  timed out over the device mount.
- The Python original's cataloguing, closely enough to be certain the Go port is where the
  score broke. §5's last paragraph is flagged as a guess for that reason.
- Whether `_needs_review/` holds other people's dropped work from before today. I only
  looked for my own five files.
