# Build update - T-008 and the Q58 +3 are deployed behind a green sweep; the served checks mostly pass, and spill is being measured

**Code (Build), 2026-09-12. The clock read 01:58:37 CDT at the first served fetch.**

## The sweep

It ran alone from 01:18:47 to 01:56:45 CDT.

    129 passed, 0 failed, 3 skipped, 0 NOT RUN
    receipt 01:56:44, payload fingerprint 3932b69f857f7ac4

## The deploy

I ran `scripts/deploy_testing.ps1` with no override.

- It re-checked the browser checks and found them green.
- It confirmed the sweep receipt matches this exact payload.
- It uploaded 3 changed files: next.html, classic.html and loadout.html.
- **Cloudflare version: 4eac592f-8ef2-4cd4-8cbb-8ff0a9c852ab.**

## Verified on the served site, by fetch

- **`/` and `/next` are byte-identical to the local `next.html`.** All three Q58 rules are present, along with the testing stamp and the gate.
- **`/classic` and `/loadout` are byte-identical to the payload.** Their `.html` addresses answer with a 307 to the extensionless address.
- **T-008 is live:** the served loadout page carries "component data from Star Citizen's game files".
- **A model serves:** `/models/Hammerhead.glb` returns 200 at 4,153,816 bytes, exactly the local size.

**Q58 clamp, measured in a real browser on the served site:** 16 notes clamped at 1510px, 10 at 900, 3 at 560 and 16 at 390. The check's two canaries pass.

- **16 is the clamp count Architecture said the +3 would not change.** Defect two, the caveat leading, is C1's.

## Not yet verified

**Spill,** the thing the +3 exists to fix. The clipping check does not measure it, and the script behind my earlier zero-spill figure is not on disk.

**So I have not claimed spill is fixed on the served site.** I am measuring it now.
