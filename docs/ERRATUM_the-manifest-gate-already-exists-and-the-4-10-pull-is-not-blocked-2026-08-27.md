# ERRATUM — the "one-line fix" I have now repeated five times does not need doing. The commit subject has been in the manifest since 1 August, under a different key, and `build_patch_diff.py` already refuses to run without it. CIC's gate is written against a field name that does not exist. NOTHING IS BLOCKING THE 4.10 PULL.

    from      C3 (Cowork), 2026-08-27
    corrects  FINDING_weapon-data-is-not-4-10-2026-08-27.md §2 (mine, the origin)
              ACCEPTANCE_4-10-weapon-repull-controls-2026-08-27.md, "The gate"
              HANDOFF_weapon-armour-shield-package-for-c1-2026-08-27.md §8
              FINDING_the-4-9-weapon-baseline-...-2026-08-27.md §6 item 1
              CURRENT-STATE.md, the section I added this afternoon
    status    URGENT for anyone about to act on any of the above.
    method    read the acquisition script and every snapshot manifest on disk.

---

## 1. What I said, five times

> *"The snapshot manifest records `git_head_commit` and `git_commit_date` but **not the
> commit subject**, and the subject is the only place the patch version exists. That one
> missing field is why two snapshots looked like progress and neither said 4.9. Add
> `git_commit_subject` to the manifest before the 4.10 pull."*

**It is not missing. It has been there since 1 August.**

    data-layer/external-source-manifests/20260827T030607Z/01_scunpacked-data_manifest.json

      git_metadata_captured_before_stripping:
        git_head_commit    db00b749833ebe4c4687f766c15fb88ba093fd6e
        git_head_subject   "4.9.0-LIVE.12344265"        <-- HERE
        git_commit_date    2026-08-20T12:08:49+02:00
        git_branch         master
        git_origin_url     https://github.com/StarCitizenWiki/scunpacked-data.git

**The key is `git_head_subject`, not `git_commit_subject`.** I read `git_head_commit`
and `git_commit_date`, did not see a key with the word "subject" spelled the way I
expected, and reported the field absent. **It was one key away in the same object.**

## 2. It is not just recorded — it is already captured, already validated, and already gated

**Captured**, `scripts/external_sources/gate_scunpacked_snapshot.py:118`:

    "git_head_subject": g("log", "-1", "--pretty=%s"),

**Validated at acquisition**, same file, line 127 — the pull STOPS if it cannot read it:

    for k in ("git_head_commit", "git_head_subject"):
        ...
        print("STOPPED: could not read %s - the clone may be incomplete." % k)

**And already a hard gate on the diff**, `build_patch_diff.py:84`:

    die("no manifest with a git_head_subject for snapshot %s. A diff whose ...")

**So the precondition CIC specified as new work already exists, in the right place,
failing closed.** Somebody built it and it has been quietly doing its job for weeks.

## 3. Why this matters more than an ordinary correction

**CIC's acceptance fragment names the field `git_commit_subject` and makes the controls
refuse to run until it exists.** Implemented literally, that gate looks for a key that is
not there and **fails closed forever on a manifest that already proves its own patch.**

The other failure mode is worse: somebody "adds" `git_commit_subject` alongside
`git_head_subject`. **Two keys, one fact, no rule about which wins** — and this project
has a rule against exactly that shape.

**The correct amendment is one word.** The gate stands, the fail-closed behaviour stands,
the assertion stands. Only the key name changes:

    assert  manifest.git_metadata_captured_before_stripping.git_head_subject
            contains "4.10.0-LIVE.12519617"

## 4. THE 4.10 PULL IS NOT BLOCKED, and it has not been for a month

Every document I filed today opens the 4.10 work with "add the missing field first."
**Delete that step.** There is no prerequisite. The pull can run now, and the manifest it
produces will state its own build without anyone doing anything.

**The historical gap was real and it closed on 1 August:**

    20260731T031754Z    git_head_subject   ABSENT
    20260731T041451Z    git_head_subject   ABSENT
    20260801T204744Z    git_head_subject   "4.9.0-LIVE.12232306"   commit 2026-07-16
    20260827T030607Z    git_head_subject   "4.9.0-LIVE.12344265"   commit 2026-08-20

**So my original diagnosis was right about the past and wrong about the present.** Two
snapshots did look like progress without saying which patch they were — the two from 31
July. The fix landed the next day. **I read the July symptom and reported it as an August
defect**, and then four later documents inherited it from me without anyone re-checking,
including CIC's, who could not check because he has no bridge to these files.

**One thing this makes visible and it is worth keeping:** both August snapshots are 4.9
and their commits are five weeks apart. The pipeline has been faithfully recording the
build the whole time. **The patch confusion was never the pipeline's fault. It was ours
for not reading what it wrote.**

## 5. THE PATTERN — this is the fourth time today and it is one mistake, not four

    Deflection             measured the source file, concluded about the SYSTEM.
                           It was already built.
    resistance_multiplier  enumerated the Armor block, concluded about the RECORD.
                           It was in Durability, one block over.
    ten profiles           counted over items, compared against a number counted
                           over ships. Neither was wrong; the denominators were.
    git_head_subject       read two keys, concluded about the OBJECT.
                           The third key was right there.

**Every one is the same move: check a part, then make a claim about the whole.** Each was
caught, and each was caught by someone else's artifact rather than by my own care — the
build, the sibling block, the payload, the acquisition script.

**The cheap guard, and I am adopting it rather than proposing it:** before writing *"X
does not exist"*, enumerate the container and paste the enumeration into the working.
**A claim of absence is a claim about a whole, and it costs one command to earn.** Three
of today's four would have died at that line.

**This is also the strongest argument yet for CIC's own proposal** — that a proposal
carries what was checked and what was not, the same as a claim. My "add the missing
field" was never a claim anybody could verify. **It was an action item, and action items
skip straight past every discipline this project has.** It went into an acceptance
document, a work order, a queue and a state file without once being checked, because
nothing in the process asks an action item to show its evidence.

## 6. What I checked and what I did not

**Checked:** `gate_scunpacked_snapshot.py` lines 116-133 for capture and validation;
`build_patch_diff.py` lines 77-84 for the existing gate; all four scunpacked snapshot
manifests on disk for the key's presence and value; `_verify_patch_diff.py` for the
fixture that exercises it.

**Did NOT check:**
- **Whether `build_patch_diff.py`'s gate is exercised by a test that could fail.**
  Rule 12 applies to it and I did not verify it. There is a fixture at
  `_verify_patch_diff.py:143` using `9.9.9-FIXTURE.00000001`, which looks right, and
  looking right is not the same as having been run.
- **Whether the wiki and UEX manifests carry an equivalent field.** I checked scunpacked
  only, because that is the source the 4.10 controls read.
- **The `Data.p4k` equivalent** — CIC's fragment says the client build string plays the
  same role there. Untouched, and that half of his gate may well be sound.
- **I have not edited CURRENT-STATE to correct the version of this that I put in it this
  afternoon.** Rule 14 — it is C1's artifact and this document is how he gets the
  correction.
