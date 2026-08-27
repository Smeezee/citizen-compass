# Update — the collector is in git. 61 files, and one 32-byte file that nearly went with it.

Sleven: "yes go". Committed and pushed as **`6a4edbf`**, 61 files, 12,227
insertions. `origin/main` confirmed at that commit after a re-fetch.

## What this actually was

Not new work. **This directory was last committed 2026-08-07 00:41** and had
been carrying 51 changed or new Go files since — consent v2, the browser
fallback that took the package from 271 MB to 6.4 MB, shortcuts, the update
channel and `make-release.ps1`, the game-log miner, export and scrubbing,
contributor identity, watched keys, the resend fix, and the selftest suite
growing from ~190 checks to 386.

All of it working. All of it on one disk, with no copy anywhere else, for three
days.

**That is on me.** Every order today said in writing not to touch
`citizen-collector/`, and I followed each one correctly — but I noted "still
uncommitted, which is correct" three separate times as though that settled it.
Following the scope of an order is right; not flagging that three days of tested
work had no backup is not. Sleven had to ask.

## The part worth remembering: `collector-scrub-salt.bin`

A plain `git add citizen-collector/` would have committed **eight** files that
must never leave the machine. The worst is 32 bytes.

`scrub.go:46` on that file: *"The salt is random per install and never leaves
the machine."* Salting exists because an unsalted hash of a player handle is
reversible. **Committing those 32 bytes would have made every pseudonymised
name in every export reversible by anyone holding this repo** — a privacy
guarantee undone by a routine convenience command.

Also excluded: the contributor id (would make one person's exports attributable,
and hand every clone the same id), a human's timestamped consent record, three
runtime markers, machine-specific selftest output, and the 6 MB package that
`make-release.ps1` reproduces from a tag.

**Fixed structurally, not by remembering.** All eight are now in
`citizen-collector/.gitignore` with the reasoning written next to them, in the
same voice as the existing entries. Verified twice: `git check-ignore` on every
one before staging, and `git ls-tree` against **the pushed remote tree** after —
no salt, no id, no consent record. Checking the remote rather than the index
was deliberate; the index is what I intended, the remote is what happened.

## Committed with its failures named, not hidden

`--selftest` is **386 passing, 6 failing**, and the commit message says so:

- **sent-rows (2)** — seeds one transaction, then calls `BuildExport`, which
  mines the real machine's Star Citizen logs and finds 309. Passes only on a
  machine with no game installed, which is the opposite of the machines this is
  for. Another session's file.
- **staleness (4)** — an intermittent race, ~1 run in 5. Two of the four now
  report NOT PERFORMED rather than passing, because they compared a count
  against zero and went green precisely when the check above them failed.

## Still not done, unchanged by committing

- the staleness race — honest now, but unfixed
- **0.2.0 unpublished**, blocked on `gh` not installed. No collector can
  self-update until that is resolved.
- the browser fallback has still never executed on a machine without WebView2
- collector → database ingest does not exist; the Worker receives zips and
  nothing imports them
