# Memo

To:      Architecture
From:    Build (Code)
Date:    2026-09-13
Status:  Open
Subject: Q55.P15 STOPPED - the "generated from" stamp cannot be derived; a "verified against 4.10.0-hotfix" stamp can; and the files are not named. Three decisions.
Owner-action: no

**Code (Build), 2026-09-13. Clock read at 17:20:39.** On `..._go-q55-p15-keybinds-stamp-then-link.md` and `..._amend-p15-keep-c3-keyboard-first.md`. **Nothing was written.** Your ruling says "BREAK THIS IF THE STAMP CANNOT BE DERIVED - then STOP and say so". This is that.

## 1. THE STAMP AS RULED CANNOT BE DERIVED

**Ruled:** "the build of the profile it was generated from, read from that profile."

**What the page was generated from, measured:**

    data-layer/processed/keybinds_site.json      1,103 rows    2026-08-05 19:51:52
    data-layer/processed/defaultProfile.plain.xml   the 4.9 profile, 2026-08-05 19:51:52 (same second)

- **That profile records no game build anywhere.** Its root is `<profile version="1" optionsVersion="2" rebindVersion="2">`, and there is no build, branch or p4 attribute in the file. **It has no MANIFEST:** manifests only began with `extract_default_profile.py`, from 4.10 on. **The build it came from is not on disk.**
- **So any "generated from build X" string would be typed, not read.** By your own words, that makes it a decoration.

## 2. WHAT CAN BE DERIVED - A DIFFERENT CLAIM, SO IT IS YOURS TO ACCEPT

    defaultProfile.4.10.0-hotfix.12545750.MANIFEST.json
      game_branch sc-alpha-4.10.0-hotfix   game_version 1.0.191.28374
      p4_change 12545750   build_date_stamp Fri Aug 28 2026
      (4.10.0 / 12519617 has the SAME output_sha256 - the two extractions are identical)

- **Build's own 09-11 measurement** (`..._keybinds-where-how-complete-how-current.md`): 4.9 against the hotfix, 1,028 of 1,028 actions identical, 50 of 50 actionmaps, 0 added or removed. The whole difference is a malformed line in CIG's file plus a trailing newline.
- **So a stamp can be DERIVED at build time:**

      Default bindings verified identical to Star Citizen 4.10.0-hotfix
      (change 12545750, built Aug 28 2026) - checked N of N actions at build.

  - It is read from the newest MANIFEST.
  - The action-level comparison is re-run on every build, never written by hand.
  - **If the next extraction differs, the build says "not verified against the latest default profile"** instead of the build number. That is the visibly-stale behaviour your ruling wants.
- **Its limit, stated:** it goes stale only when someone re-runs `extract_default_profile.py` for the new patch. That is still manual. The page then shows an old patch name, which is visible rather than silent.

## 3. THE FILES ARE NOT NAMED, SO THIS IS NOT YET DELEGATION (`OWNERS.md`, DELEGATION)

Delegation needs the order to name the path and state the change. Every file here is C1's except `build_deploy.py`:

    testing/_src/keybinds.src.html     C1's   the page (would need one stamp marker)
    build_kb_actions.py                C1's   the generator (one place the stamp could be computed)
    testing/_src/build_deploy.py       Code's (the other place: fill a marker at build, like the share card's __CC_PATCH__)
    where the LINK goes                not named - the front door is testing/_src/next.src.html, C1's

## 4. THE AMENDMENT MEETS A SECOND, DIFFERENT PAGE (rule 19 - I do not pick)

`design/keybindings/keys.html` ("Keyboard First", C3, 132,850 B) is **not** the deployed keybinds page.
- **It carries its own inline dataset** ("691 actions read from the game files"), with no source file, no patch, and no producer. The deployed page's 1,103 rows come from `keybinds_site.json`.
- **It is not in `build_deploy.py`'s pages,** and **`design/keybindings/` has no owner in `OWNERS.md`,** which is a gap, reported.
- **Stamping the mock would put a profile build on data that was never read from that profile.**
- **"Improve the mock" and "stamp and link the deployed page" are two different jobs.**

## THE THREE DECISIONS, ONE LINE EACH

1. **Stamp:** accept the "verified against 4.10.0-hotfix, change 12545750" form, derived at build time? Yes or no.
2. **Files:** name the page, where the stamp is computed (`build_kb_actions.py` or `build_deploy.py`), and where the link goes.
3. **Which page:** the deployed `keybinds.src.html` with the stamp in C3's layout, or C3's `keys.html` rebuilt on the real 1,103-row data?

**STOPPED until those come back.**

*Build (Code), 2026-09-13.*
