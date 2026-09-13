# Build update - the share card (shape A) is built and proven locally; the full sweep is running before deploy

**Code (Build), 2026-09-13. Clock read at 05:39:24.** On Owner's order (`..._build-now-static-discord-share-card-shape-a.md`), in Design's locked copy.

**DELEGATION, RECORDED AS OWNERS.md REQUIRES:**
- **The order:** Owner's, and it names `testing/_src/loadout.src.html` and states the change: Design's table of strings.
- **The file:** C1's, under `OWNERS.md`.
- **The write:** the ten tags Design listed. Nothing added and nothing else on the page touched.
- **`testing/_src/deploy_pages.py`:** one entry, `og-loadout.png`. `OWNERS.md` lists this file as "proposed for Code, not claimed by C1", and I declare that here the way C1 did on 09-04. **Architecture: please confirm the owner in `OWNERS.md`.**

**WHAT WAS BUILT:**
- **The markers:**
  - The tags carry `__CC_ORIGIN__` and `__CC_PATCH__`, and `build_deploy.py` (Code's) fills them.
  - **The origin** follows `--live`: the testing host now, the public host on a live payload. **The patch** is the snapshot manifest's own `LAST_VERIFIED_PATCH`. It reads 4.10 today, and it is never typed.
- **The image:**
  - `testing/_src/og-loadout.png`, 1200x630, drawn once, in the page's own colours and Design's words.
  - It has no ship, no one else's logo and no disclaimer wording: rule 8 text stays Sleven's.
- **The copy:** the build copies the image byte for byte through a new binary branch. The text path strips comments and would have corrupted it.
- **The canonical path** is `/loadout`. Measured on the host: `/loadout.html` redirects 307 to `/loadout`. **A plain fetch gets the `<head>` with no password gate,** which is what Discord's crawler does.
- **The control is `checks/_verify_share_card.py`** (new, Code's). It checks the BUILT page against Design's strings:
  - the absolute URLs on one origin
  - the image really in the payload and 1200x630
  - no leftover marker
  - **Proof:** 13 of 13 self-test cases and 7 of 7 mutations. The first run caught only 5 of 8, which exposed two weak plants and one crash path; all three are fixed.

**PROVEN LOCALLY:**
- **The build is ok** (venv, 17 s). The deploy guard says "safe to deploy".
- **The built `loadout.html`** carries the ten tags, with " · Patch 4.10" and absolute testing-origin URLs.
- **The image in `_deploy/`** is byte-identical to its source.
- **The control passes on the real payload.**

**IN FLIGHT:** the full sweep, started at 05:39, which the testing deploy requires. Then:
1. deploy
2. fetch the served head and image as a crawler
3. file the receipt

**Not performed by Build:** the Discord paste itself needs a Discord client. The served-bytes check is what Build can do.

**While the sweep runs:** the pre-push guard. It touches only `checks/` and `.git/hooks`, not the payload.
