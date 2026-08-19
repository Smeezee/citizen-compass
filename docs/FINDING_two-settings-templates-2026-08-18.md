# FINDING — one settings file, two templates, and both of them were wrong in the same way

    found by  Code, 2026-08-18, while removing automatic capture (V1 §6)
    status    both cleaned. The DUPLICATION is not fixed and is the finding.
    rule      CLAUDE.md hard rule 14 - one writer per artifact, enforced by
              construction rather than by everyone remembering

---

## What is there

`collector-settings.txt` — the one file a non-technical person is invited to
edit — is written from **two separate hard-coded templates**:

    citizen-collector/auto.go      const settingsTemplate   (~90 lines)
    citizen-collector/package.go   the packaged copy        (~30 lines)

Neither is derived from the other. Neither is derived from the settings READER,
which is a third place the key names appear. Nothing checks that they agree.

## How it showed up

Removing automatic capture meant removing four settings: `interval_seconds`,
`capture_low_value`, `burst_seconds`, `burst_max_frames`. I cleaned the template
in `package.go`, rebuilt, and the new §6 check failed — because the OTHER
template still offered all four.

**A settings file written from that template would have switched automatic
capture back on**, on a build whose window says nothing captures on its own.
The check caught it. Nothing else would have: the two templates are never
compared, and the packaged one only appears in a release.

## Why this is the rule-14 shape and not a tidiness complaint

Hard rule 14 says a second writer must be made impossible rather than
discouraged, because "a rule that depends on several sessions remembering it is
a convention, not a guard". This is that, with a copy-paste instead of a second
program:

- the two templates drift silently — nothing reads both
- they drift in the direction of *stale* — the packaged one is the copy a crew
  member gets, and it is the one nobody edits while working
- the reader is a third copy of the same knowledge, so a key can be removed from
  both templates and still be honoured by the parser

The immediate danger is closed: the §6 check now reads the live template and
fails if it *sets* a removed key. But that check only knows about
`auto.go`'s copy and only about those four keys.

## What would actually close it

**One template, and the other place references it.** `package.go` should write
`settingsTemplate` rather than its own text — one constant, one writer, and the
packaged file becomes the same file by construction.

Then, if it is worth more: derive the reader's known keys and the template's
keys from one list, so a key that no code reads cannot be offered, and a key the
reader honours cannot be undocumented. That is the version that makes the next
removal safe rather than merely making this one correct.

**Not done in this pass.** It is a change to what a released package ships, on
the same day as a change to what the program does, and those two want separate
commits and separate proof.

## Where it is

    citizen-collector/auto.go       settingsTemplate
    citizen-collector/package.go    the packaged copy
    citizen-collector/no_auto_capture_selftest.go
                                    the check that caught the drift
