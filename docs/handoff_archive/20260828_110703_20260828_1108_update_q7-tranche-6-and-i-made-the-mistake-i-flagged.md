# Update — Q7 tranche 6: 62 of 104 labelled. And I made the exact mistake I criticised C1 for two hours ago, so I fixed the gate that hid it from both of us.

**2026-08-28 11:08 local · Code (background session)**

    labelled     62  (26 INDEPENDENT, 36 UNPROVEN)     was 52
    unlabelled   42                                    was 51

Nine controls, the data / database / lifecycle family. **All nine green after
labelling.**

## I WROTE A MALFORMED LABEL, AND THE GATE TOLD ME THE WRONG THING

At 00:02 I wrote up C1 for this:

    RULE16: INDEPENDENT for the two assertions that matter

...and noted that the gate reporting it as "no RULE16 label" was "the one part
of this I would call a wart". Then, in this tranche, I wrote:

    RULE16: UNPROVEN, and closer than most - the ROWS are independent

**A comma where the separator belongs.** Same defect, same misleading message,
mine this time. Two people, two hours apart, both sent looking for a missing
label in a file that had one.

**So the wart is fixed rather than noted again.** The gate now distinguishes the
two:

    _verify_zz_probe_malformed.py: a RULE16 line is PRESENT but MALFORMED. It
    must read RULE16: <INDEPENDENT|UNPROVEN> - <reason>, with the separator.
    Got: RULE16: UNPROVEN, it imports snapshot_shape_check and reads its ...

**Proven by planting one.** A copy of a labelled control with the separator
swapped for a comma, named so the gate discovers it, produced exactly that line
and exit 1. The probe went to `_to_delete/probes-2026-08-28/`.

The comment at the site names both offenders, C1's and mine, because *"a reader
told there is no label goes looking for the wrong thing, and in both cases went
looking for it in a file that had one."*

## TWO INDEPENDENT, AND BOTH FOR THE SAME REASON: THEY LEAVE THE PROCESS

**`_verify_degraded_database.py`** starts the application **three times in three
real subprocesses**, each configured differently, and judges what each one does.
Nothing is imported and no internal flag is consulted. *A module asked whether
it thinks it is degraded could answer wrongly in exactly the situation this
exists to catch.*

**`_verify_preservation_inversion.py`** installs the guard on a real engine and
then asks **the database** whether the row survived. The inversion it is named
for is precisely the case where asking the code gives the wrong answer - a
delete refused for the wrong reason looks identical from the guard's side.

## SEVEN UNPROVEN, AND ONE OF THEM IS THE CLOSEST CALL SO FAR

`_verify_location_hierarchy_db.py` gets **"UNPROVEN - closer than most"**. Its
ROWS are independent: real locations out of the real database rather than
fixtures shaped to suit the resolver, which is the entire reason it exists
beside the unit control. But `resolve_path` is imported and asked, so the answer
is the code under test's own.

**Real input, self-reported verdict.** That pairing has come up enough tonight
to be worth a name.

The other six each name their own gap: `findings_store` round-trips through the
store itself; `fingerprint_history` writes and reads with the same module, though
it reads the FILE rather than the module's accessor, which is the better half of
a weak channel; `lifecycle`, `pull_and_clear` and `snapshot_shape` all import the
rule they judge.

## Where Q7 stands

    62 of 104 labelled       42 to go
    26 INDEPENDENT           36 UNPROVEN

The count moved from 103 to 104 because another control landed while I was
working - the sweep discovers rather than lists, so it will be swept without
anyone remembering it.

Nothing committed since `1a1b4b7`.
