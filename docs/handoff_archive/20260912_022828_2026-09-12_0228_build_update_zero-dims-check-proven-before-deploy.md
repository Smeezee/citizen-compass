# Build update - the check for the zero-dimension fix is proven able to fail, before the deploy

**Code (Build), 2026-09-12. Run at 02:26:52 CDT against the served site, before deploying.**

**The check:** `_needs_review/served_zero_dims.mjs`. It opens `loadout#<ClassName>` on the served site and reads the Specs rows.

**Before the deploy it reports the defect,** as it must:

    AEGS_Javelin        Length 0 m, Width 0 m, Height 0 m
    ARGO_MOTH           Length 0 m, Width 0 m, Height 0 m
    DRAK_Cutlass_Black  Length 37.5 m, Width 26.5 m, Height 11.5 m   (canary PASS)
    exit 1 - DIMENSION ROWS PRESENT on AEGS_Javelin, ARGO_MOTH

**So the check can see the "0 m" rows and can fail (rule 12).**

**After the deploy, the same run must say "NO DIMENSION ROWS on Javelin or MOTH" and exit 0,** with the Cutlass still at 37.5.

**In flight:** the solo sweep, started 02:25 CDT. It deploys only if it is green.
