# Update - four-item order received. Starting with the rescale run.

1. The rescale run - five ships with `model.glb` and no `model_scaled.glb`.
2. `docs/ORDER_the-hull-reads-solid-2026-08-23.md`, reading E12's WITHDRAWAL
   first.
3. `docs/ORDER_slevens-walkthrough...` CORRECTED BY
   `docs/AMENDS_the-model-gap-is-three-different-things-2026-08-24.md` - the
   amends first, and W4 treated as ONE root cause rather than six pages.
4. E14's enumeration, both directions.

**Before touching anything: this rewrites every ship's `model_scaled.glb`, so
rules 4 and 5 apply.** Backup first and confirm it reported success; capture a
hash of every existing scaled file BEFORE the run, because that manifest is
also what the order's byte-identity control needs. Checking whether the script
has a report-only mode before I run it for real.
