# Update — received rev 5 addendum: master build + crew package generator

**When:** 2026-08-05 (addendum is a C1 decision dated 2026-08-06)

Logging on arrival per hard rule 13. **Not started** — job 1 (the grabber) has
tonight's deadline and is still in flight, so this is recorded and queued, not
begun.

## What arrived

**Two builds from one source, via a build flag — not two projects.**

- `collector.exe` — crew build. Capture, read, export. Nothing else.
- `collector-master.exe` — Sleven only. The above plus calibration, zone tuning,
  the review pen, and *Generate crew package*.

**Generate crew package** — one button on the master, producing
`citizen-collector-<version>-<patch>.zip` containing the pre-compiled crew exe,
Sleven's calibrated `atlas\`, `names.dat`, `zones.json`, `profiles.json`,
`README.txt`, `CONSENT.txt`, `MANIFEST.txt`. **Generate assembles, it does not
compile** — neither the crew nor necessarily Sleven's machine will have Go on
the day.

**Must-not-ship list is an assertion, not a filter.** `.env`, tokens, keyed
URLs, Sleven's `install_id`/handle, any `captures\` content, the master build
itself, anything not on the list. Generate **refuses and reports** on a hit
rather than excluding quietly.

**Verify-after-generate** — rule 12 applied to distribution. Reopen the zip;
check every MANIFEST file present with matching SHA256; no file outside
MANIFEST; grep the archive for machine name, Windows username, `install_id`,
and any 32+ char hex/base64 run; run the crew exe `--selftest` and require
exit 0.

**Version stamping** — every package carries version + game patch; every
returned session file carries the package version that produced it.

## Effect on work already in flight

I am folding **two cheap parts in now**, because they are structural and get
expensive later:

1. **The build-flag split** (`//go:build master`) goes into the collector as it
   is being written, so the two-build shape exists from the first commit rather
   than being retrofitted.
2. **`--selftest`**, since the verify step depends on the crew exe having it.

## What I am NOT doing yet, and why

The package generator itself is **blocked on inputs that do not exist**. Job 1
is explicitly scoped "NO OCR. No atlas. No vocabulary. No zones." — so of the
seven payload files, only `names.dat` is buildable today (from the sealed UEX
snapshot, per the §4.4 note). `atlas\`, `zones.json` and `profiles.json` are all
downstream of calibration and the reading half, which is exactly what job 1's
legibility answer gates.

Building Generate now would mean a generator that asserts against a payload it
cannot assemble — and a verify step that passes because it never had anything to
check. That is the silent-success shape hard rule 12 exists to stop.

**Sequencing, unless Sleven says otherwise:** finish job 1 → jobs 2 and 3 (both
independent, both have real inputs on disk) → `names.dat` → the generator once
there is an atlas to put in it.

**Next:** back to job 1 — `main.go`, then build and actually run it.
