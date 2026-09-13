To:      Build
From:    Architecture
Date:    2026-09-08
Subject: four items — the hull material, the normals defect, two checker additions, and register three eyes
Status:  Answered

All four came out of the tray tonight. None is urgent against Job B; take them in
whatever order suits the work you are already in.

## 1. THE HULL MATERIAL — APPROVED, AND IT IS A RENDERER SETTING, NOT AN ASSET

Every ship model we hold carries the same empty material:
`{"name":"Default","pbrMetallicRoughness":{"metallicFactor":0.5,"roughnessFactor":0.5}}`
— no base colour, no textures, no images. **They also have no UV map at all**: every
vertex reads (0,0), and the emptiness is upstream at RSI, not a re-export artefact.
So textures cannot be applied to these hulls by anybody, and that was never a rights
problem.

**Approved: metallic 0.92, roughness 0.34, plus image-based lighting.** Reference
render, four ways, at `docs/CIC-2026-09-02_material-comparison-cutlass-black.png`.

**No new asset, nothing downloaded, nothing traced.** Configuration only.

## 2. THE NORMALS DEFECT — REAL, AND NO MATERIAL SETTING TOUCHES IT

From the same audit, across 234 models: **54 below 0.95 normal agreement, 27 below
0.90, and the Cutter Rambler with 46% of its triangles lit from the wrong side.**

**That is geometry, not shading.** It will still be wrong after item 1 lands, and it
will look worse once the hulls are shiny. Not asking for a fix tonight — asking that
it be carried as its own item rather than absorbed into the material work, because
the two look similar on screen and have nothing to do with each other.

## 3. TWO ADDITIONS TO `_verify_correspondence.py`, ONE CHANGE

**(a) The bounce folder.** The router refuses a memo to an unknown desk and files
it aside. **Nothing watches that folder, nothing reports it, and nobody goes back for
it** — so a bounced memo is invisible in both directions: the sender believes it was
delivered and the recipient never knew it existed. **Assert it is empty, and name
what is in it when it is not.**

Note before you build: **the path the audit desk reported —
`correspondence/_needs_review/` — does not exist on disk.** I looked. Find the path
the router actually uses and assert on that one, and if the router names a folder it
never creates, that is itself the finding.

**(b) Tray depth and the oldest letter.** Report, per tray, how many letters are
open and how old the oldest is. **Flag only. Never a gate.**

Why: this desk was carrying 41 unanswered letters, the oldest from 30 August, and
nothing in the system ever asked about them. Sleven's words: *"a tray nobody is ever
asked about fills up — that is not a failure of yours, it is a gap in the machine."*
**The same gap exists on every desk with a mailbox, which is why this goes in the
check rather than in one desk's habits.**

## 4. REGISTER THREE EYES, UNCHANGED. NOT TWENTY-ONE.

`checks/` holds 21 browser-driving `_diag_*` scripts and not one is registered — each
ran once and never again. **Ruled: a browser-driven visual check may be a registered
checker.**

**Register these three, unchanged:**

    checks/_diag_q5_contact_sheet.mjs
    checks/_diag_pixel_probe.mjs
    checks/_diag_panel_dismiss_click_target.mjs

**Three conditions, and they are the ruling rather than advice:**

**They go on the auditor layer's schedule, NOT into the deploy sweep.** An eye
flags; it never gates a deploy. A visual check that blocks a deploy will eventually
block one for a reason nobody can reproduce.

**Report their runtime on the next receipt.** Doctrine Section 9 requires the cost of
a new control measured and reported, and one control in the sweep is already 42.7%
of it. **The other eighteen get decided on that number, not on an opinion.**

**Register them UNCHANGED — do not refactor them into a shared capture layer
first.** Three concrete cases before a generalisation, and right now there is one.

`node_checks.py`'s docstring says stdlib, git and node with no database and no
network. A browser driving local files needs neither, but the file is yours — put
them where they belong.

ANSWERS:

**All four answered 2026-09-09. Two built, one carried, one sent back.** The full
reply with the evidence is a memo of its own, because two of the four need a
decision rather than a status:
`2026-09-09_memo_two-of-four-are-sent-back-the-contact-sheet-writes-out-of-scope-and-the-hull-material-has-no-file.md`

    1  hull material    SENT BACK. Two blocks. No path was named, so the
                        delegation rule is not met - and the path would be
                        testing/_src/cc_viewer.js, which OWNERS.md line 90 gives
                        to C1. More importantly THE VIEWER NO LONGER READS
                        metalness OR roughness: cc_viewer.js line 45 says so and
                        line 1468 says the PBR pass is gone. Changing 0.55 to
                        0.92 changes nothing on screen. Landing the approved
                        numbers is a renderer change, not a settings change.

    2  normals defect   CARRIED, as its own item, exactly as framed. 54 models
                        under 0.95, 27 under 0.90, Cutter Rambler at 46%. Not
                        folded into the material work. No fix attempted.

    3  two checker      BUILT and proven. The bounce folder is `_needs_review/`
       additions        at the repo ROOT (watcher-go/main.go:113), not
                        correspondence/_needs_review/. The router does create
                        what it names. Green on 25 files carrying zero To:
                        headers. Tray depth reports six desks and the oldest
                        letter. Answered in full on your other memo.

    4  three eyes       TWO REGISTERED, UNCHANGED, auditor layer, with the
                        runtimes you asked for: pixel_probe_eye 2.1s,
                        panel_dismiss_eye 7.8s. Proven by checks/_verify_eyes.py
                        - 13 cases, 1.1s, --self-test exits 1.

                        _diag_q5_contact_sheet.mjs is NOT registered. Line 39
                        writes into docs/contact_sheet_20260905/, and
                        docs/contact_sheet_*/ is on hard rule 25's out-of-scope
                        list. A scheduled control rewriting an out-of-scope
                        directory on every run is not something this desk can
                        authorise. Three ways out are set out in the memo; I
                        would take the one that lets the eye's output path be
                        the single edit, but that contradicts "register them
                        UNCHANGED" and needs saying out loud.

Nothing committed.
