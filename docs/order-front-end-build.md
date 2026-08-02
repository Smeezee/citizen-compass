# ORDER — front end build, C1 to Code

Constructed by C1 from Claude-02's plan, 2026-08-02. **C2's plan is the input; this is the order.** Where they differ, this wins — the differences are corrections, and they are marked.

Read `docs/workorder-front-end-build-plan.md` for the reasoning, the demand research and the page designs. That work is good and stands. Read this first for what has changed since it was written.

Hard rule 13: `inbox/` update on intake, on each part completing, on any stop.

---

## CORRECTION 1 — the tab problem is real, C2's diagnosis of it is not

C2 reports the right-edge tabs were "wiped twice by rebuilds" and proposes the build re-emit them from a list.

**The LOADOUT tab was not wiped by a rebuild. C1 removed it deliberately, on Sleven's instruction, and a later write restored it.** Implementing 8a as written would make that removal impossible — the build would put it back after every rebuild, permanently overriding a decision the owner has already made twice.

**The underlying idea is still right.** Hand-patching tabs after every build is not workable. But the build must own a list that Sleven controls, not re-emit whatever happened to be in the file last.

### And the stack is broken right now — measured, not argued

Five tabs currently sit on the right edge:

```
#cc-tab      DISPLAY    44%
#cc-fb-tab   FEEDBACK   44% + 150px
#cc-kb-tab   KEYBINDS   44% + 290px
#cc-lo-tab   LOADOUT    44% + 430px
#cc-fi-tab   FIND       44% + 570px
```

On a 1920×1080 display, 44% is 475px. **FIND starts at 1045px on a 1080px-tall viewport — entirely off-screen. LOADOUT starts at 905px and is mostly off.** Two of five are unreachable on a standard monitor. It only fits at 1440p.

**So the tab work is not "make the build emit five tabs."** It is:

1. **Decide what belongs on the right edge at all.** DISPLAY and FEEDBACK are page-level tools and belong there. KEYBINDS, LOADOUT and FIND are *destinations* — they are pages, and pages belong in navigation, not in a floating stack that grows until it falls off the screen.
2. **Sleven has already ruled on LOADOUT: it goes on the ship page**, opening on the ship you are looking at. That is the pattern for destinations. FIND almost certainly belongs in the site's own nav alongside Ship Purchase Matrix and Sale Calendar.
3. **Whatever survives, the build owns it — from an explicit list with an explicit position for each**, so adding a sixth is a deliberate act with a layout consequence someone had to think about, rather than a silent append.

**Do not add tab emission until the layout question is answered.** Emitting a broken layout reliably is not an improvement. Report your recommendation; Sleven decides.

---

## CORRECTION 2 — 8b is already done, and needs one more entry

`build_deploy.py` already copies pages into `_deploy/` and already fails loudly on a missing source. C1 added it and proved it per rule 12 — deleted both outputs and confirmed they were restored, removed a source and confirmed **exit 1**.

Current list:

```python
PAGES = [
    ('keybinds.src.html', 'keybinds.html'),
    ('loadout.src.html',  'loadout.html'),
]
```

**Add `('find.src.html', 'find.html')`.** That is the whole of 8b that remains. Re-run the proof after adding it — the guard has only ever been exercised on two entries.

---

## CORRECTION 3 — the Blender finding is confirmed, not pending

C2's plan says the `Loadout` array was checked on one file and asks for confirmation across others.

**C1 confirmed it. Ten ships sampled across manufacturers, 10 of 10 carry the full schema:** Avenger Stalker 67 slots, Prowler Utility 103, Asgard 106, Constellation Taurus 115, Centurion 45, plus five more. 316 files total.

Treat it as established. Do not re-verify it.

---

## CORRECTION 4 — ship identity is already resolved

C2's plan does not mention it, and every page in Build A and Build B needs it.

`data-layer/ship_resolution.json` holds the cross-reference, built on Sleven's method — anchor on the 254 live ships as the trusted set, match outward into the 316 game files, classify the residue rather than discard it:

```
254   live ships
215   matched to a game file
  2   ambiguous
 37   no game file — 33 of them already flagged pledge_only by the site
  6   tier variants set aside
 95   game files not on the site (PARKED by Sleven — do not work on these)
```

**Use it. Do not re-derive it.** Two items remain: PostgreSQL's 232 is not in the table, and four ships say `purchasable` with no game file — 600i Explorer, Ares Inferno, Ares Ion, Nova Tank. Ares Inferno and Ion are expected to be in the game, so suspect a naming mismatch before concluding absence.

---

## THE DECISION C2'S PLAN FORCES, AND IT IS NOT YOURS TO TAKE

C2 states that Build B "finally forces the FastAPI backend to serve something public." `docs/workorder-loadout-real-data.md` recommends the opposite — static JSON alongside the page — and says explicitly not to take the FastAPI path without asking.

**Both positions are defensible and they are in direct conflict. Sleven decides. Do not resolve it by building.**

Put these numbers in front of him rather than an opinion:

- **Cloudflare Workers static assets caps at 20,000 files.** A page-per-item build across the item catalogue plus 823 shops plus 316 ships would exceed it. That is a hard ceiling, not a preference.
- But a static build does not have to be one file per item. A bundled index with client-side rendering stays well inside the cap and keeps the site's **zero-backend property** — which is the reason the live site has never had a runtime dependency and a deploy is a folder of files.
- FastAPI is more flexible and Railway already runs, powering nothing. The cost is that the site starts depending on a service being up, and there is currently no monitoring, no uptime history, and no fallback for when it is not.

**Report the trade-off. Recommend one. Wait.**

---

### RULED 2026-08-02: STATIC JSON. And the file-count argument reverses — record this.

**The item count depends entirely on which "items" is meant, and the two answers
fall on opposite sides of the cap:**

| meaning | items | + 823 shops + 316 ships | vs 20,000 cap |
|---|---:|---:|---|
| UEX **priced** items | 7,728 | **8,867** | comfortably inside |
| source 1 **game-file** items | 21,849 | **22,988** | **over** |

**"21,849" is real.** It is the recursive file count of `items/` in the
scunpacked-data snapshot — **identical in `20260731T041451Z` and
`20260801T204744Z`**, because both are upstream commit `4764726`. An earlier
claim that the current snapshot's `items/` is empty came from a non-recursive
glob; the files are nested. C2's error was conflating that game-file count with
UEX's 7,728 priced records — everything in the game files versus only what has
a price.

**The ruling does not rest on either number.** It rests on the live site having
no runtime dependency at all: a deploy is a folder of static files, and there is
currently no monitoring, no uptime history and no fallback for Railway being
down. Static preserves that. FastAPI remains open later without rework — this is
a "not yet", not a "no".

**Which is exactly why the decision should never have rested on the file count.**
Had it done so, it would have flipped on a definition.


---

## WHAT TO ACTUALLY DO, IN ORDER

**1. Add `find.src.html` to `PAGES` and re-prove the guard.** Small, unblocks nothing else being wrong.

**2. Report on the tab layout** per Correction 1. Recommendation only, no implementation.

**3. Put the backend decision in front of Sleven** with the numbers above.

**Stop there.** Builds A, B and C are all downstream of decisions 2 and 3, and starting any of them first means building on an answer nobody has given.

---

## Two things in C2's plan worth carrying forward without change

**The position.** "Plain answers, legibly presented, honest about how sure they are." The six rules under it are the best statement of what this site is that anyone has written down. Rule 4 in particular — every price shows its age and its source — is the one thing no competitor does and it follows directly from UEX being Tier C at ±100% on items.

**The empty-state requirement.** Zero of the UEX items have images. If a template needs a picture and a description to look finished, twenty thousand pages look broken. **Assert a page renders correctly with every optional field empty** before building twenty thousand of them.

---

## Unverified in C2's plan — flag, do not build on

- **"21,849 item files."** The snapshot's `items/` directory is empty; that count comes from somewhere else. Establish where before any page-count or file-count decision rests on it.
- **"90,121 labels."** Source 2's manifest records 63,375. Different sources may explain it. Confirm before quoting.

Neither blocks anything. Both would be embarrassing to discover after building on them.

---

## Boundaries

- Live site, `releases/latest.html`, `static/preview.html`, sealed snapshots untouched.
- No FastAPI work until Sleven rules.
- No tab emission until the layout question is answered.
- C1 is the only Cowork session authorized to write to the repository. If a file under `testing/` changes and it came from neither C1 nor you, that is a reportable anomaly.
