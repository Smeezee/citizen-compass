# Update - H run complete, all nine items DONE, pushed

Nine commits, `d17caba..67e441a`, pushed to origin/main.

| item | outcome |
|---|---|
| H1 generator | 188.7 KB gzipped, one file, ceiling enforced |
| H2 FIND reads the file | 56 assertions with the network genuinely blocked |
| H3 the banner | off, after a live fetch returned 26,657 rows |
| H4 say what is provable | 29 assertions, scanner proven on known-bad text |
| H5 download + checksum | downloaded from the deployed origin, hashed, matched |
| H6 build step | 21 assertions, both halves, negative half first |
| H7 protect by default | 45 assertions, inversion proven at the engine |
| H8 staleness flake + hang | 31.7% -> 0% over 2000 runs; the hang was something else entirely |
| H9 sweep | 36 controls, 36 ok, 0 skipped, 0 not run |

Nothing is BLOCKED. Two things deliberately not done, both yours to close:
the repo's collector binaries were **not rebuilt** (no release cut, nothing
installed), and the e2e harness's step-7 `alembic check` failure is
pre-existing and is a schema-authority call.

Report is in `docs/LEDGER_shop-price-layer-2026-08-19.md` under the H RUN
heading.
