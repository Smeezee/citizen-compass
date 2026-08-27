# Update — §5 and §6 built. The leak is closed three ways, and the fix for it also fixed a data-quality bug nobody had connected to it.

`gamelog.go`, `gamelog_mine.go`, `export.go`, new `leak_selftest.go`, new
`scripts/scrub_sidecars.py`. Builds, vets, formats clean.

## Where the leak stood when I measured it

C1 reported 364 of 450. **Current count on this disk: 401 of 449** - it has kept
growing, because it grows with every in-world capture.

```
sidecars:   449
clean:       48
leaking:    401
  location_candidates   401 file(s)
```

Uniform: every single one is the same field.

## Closed three ways, and the layering is deliberate

**1. The writer no longer produces it** - the parser fix below.
**2. The payload is gone from the struct** - it cannot be written even if the
parser fails.
**3. The export refuses any file that still carries one** - §6.

Layer 2 is the one I would argue for hardest. Unifying the paths closes the leak
*by making the parser succeed*, which means the leak returns the moment it
fails: a log starting mid-session, a future CIG rename, a capture before the
first terminal opens. **A payload that cannot leak is a property. A payload that
leaks only when something else breaks is a coincidence.**

## §6 - the guard, with the negative control that keeps it honest

Refusals are per file and name what was found, in the same shape as the existing
quarantine reasons. Checked on the sidecar's raw BYTES, not a parsed struct,
because the question is what would be SENT - a field this build has never heard
of still ships if it is in the file.

```
[ok] GUARD: a sidecar carrying a playerGEID is REFUSED
[ok] GUARD: and the refusal names the field
[ok] GUARD: a sidecar carrying location_candidates is REFUSED
[ok] GUARD: a sidecar quoting a raw log line is REFUSED
[ok] GUARD: a sidecar carrying an account handle is REFUSED
[ok] NEGATIVE CONTROL: a clean sidecar IS still sent
[ok] guard: exactly one frame of five was admitted
```

The negative control is what makes the other five mean anything - a guard that
refused everything would satisfy all of them.

**It is a refusal list, not an allow-list, and I have said so in the code rather
than letting the name flatter it.** A strict field allow-list applied to
sidecars written by older builds would refuse everything ever captured, and in
practice that means somebody switches the guard off. The raw-log-line rule is
the general case that catches a shape nobody has thought of.

## The renderer - and the parser I was told to reuse was wrong

The erratum says "the parser exists; this is a field, not a feature". The
DirectX half is exact. **The Vulkan half was `\bVulkan\b`**, and measuring it
against the archive:

```
logs with [VK] channel lines             79
logs with [VK] AND a D3D Adapter line     0
156 D3D + 79 VK = 235 = every log
```

A perfect partition - and the one log containing the *word* Vulkan beside a D3D
Adapter line has **zero** `[VK]` lines. It is a DirectX session whose GPU driver
printed `Driver Version (581.57.0.0) Vulkan API (1.4.312)` - the driver stating
what it supports, not what the game is using.

Tolerable noise in an aggregate count. **A wrong answer in a per-capture field**,
which is what the erratum asked me to create. So the matcher is now the `[VK]`
log channel, corrected at its one definition so the miner gets it too, with a
negative control asserting that exact driver line does not make a Vulkan
session.

## §5c - the 401 files: REPORT ONLY, waiting on Sleven

`scripts/scrub_sidecars.py`. Rule 5 - it touches hundreds of files, so it prints
exactly what it would change and stops. The dry run above is that output.

**Nothing has been written.** `--apply` takes a verified backup into
`_to_delete/sidecars_before_scrub_<stamp>/` first, checks every copy by size,
and refuses to rewrite anything if the backup is short (rule 4).

It removes `location_candidates` and **nothing else**. It does not go hunting
for identifiers inside other free-text fields - that is the name-detection
heuristic §5b rules out, and it would produce a scrubber everyone trusts and
nobody can verify. Anything still failing after the strip is reported and left
alone, with the export guard refusing it in the meantime.

**They are already contained**: §6 means none of these can leave the machine
regardless of whether they are ever scrubbed. This is tidying, not containment.

## Acceptance against the erratum's revised §6

```
1  no NEW sidecar carries an id or a raw line     PASS in test - needs a real session
2  in-world sidecar reports a non-null location   PASS
3  the 401 existing sidecars                      guard REFUSES them now;
                                                  scrub is dry-run and awaiting a yes
4  every game_log block names the renderer        PASS
5  Alt+F3 uses the existing burst                 DONE, shipped in 6dde2bd
```

Acceptance 1 says "verified by grepping a fresh folder after a real session, not
by reading code". **I cannot do that** - it needs the game played. What I have
is the same assertion against real log shapes carrying real identifiers, plus a
negative control proving those identifiers are findable when present.

Full `-selftest` running now; I will report its verdict rather than assume it.
