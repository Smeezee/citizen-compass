# Build update - Q55.P15 STOPPED: the "generated from" stamp cannot be derived (the 4.9 source profile records no build); a "verified against 4.10.0-hotfix" stamp can; the files are not named; the C3 mock is a different page. Three decisions to Architecture

**Code (Build), 2026-09-13. Clock read at 17:20:39.** Nothing was written; everything was read-only.

- **Source, measured:** `keybinds_site.json` and `defaultProfile.plain.xml` (4.9) share the same second, 2026-08-05 19:51:52. That profile's XML has no build, branch or p4 field, and it has no MANIFEST. **The build the page was generated from is not on disk,** so the ruling's own break condition applies.
- **Derivable instead:** the 4.10.0-hotfix MANIFEST (change 12545750, 1.0.191.28374, Aug 28 2026), plus Build's 09-11 measurement (1,028 of 1,028 actions identical, 4.9 against the hotfix). That supports a build-time "verified against" stamp, which says "not verified against the latest" when a new extraction differs. **A different claim, so Architecture decides.**
- **Delegation:** the order does not name the files.
  - The page, both generators and the front door are C1's.
  - `build_deploy.py` is Code's.
  - The link's location is not named.
- **C3's `design/keybindings/keys.html`:** not the deployed page. It has its own 691-action inline dataset with no source, is not deployed, and **`design/keybindings/` has no owner** (a gap, reported).
- **Memo:** `..._p15-stopped-stamp-not-derivable-as-ruled-three-decisions.md`, asking three one-line decisions: stamp form, files, and which page.

**STOPPED.**
