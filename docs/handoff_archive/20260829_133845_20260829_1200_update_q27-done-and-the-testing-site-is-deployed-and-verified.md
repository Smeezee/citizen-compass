# Update — Q27 done with declared exceptions, the sweep is 106 of 106, and the testing site is deployed and verified on the served bytes.

**2026-08-29 12:00 local · Code (background session)**

## Q27 — DECLARED, NOT RE-BASELINED

Three exceptions in `_verify_child_markers.py`, each declaring the WHOLE
transition rather than just a port name, printed on every run:

    BANU_Defender 50   [-0.30751, 0.01049,  1.32494] cig  ->  REMOVED
    BANU_Defender 51   [ 0.30751, 0.01049,  1.32494] cig  ->  REMOVED
    MISC_Hull_C   34   [-0.0,    -0.10429, -1.27827] cig
                    -> [-0.00408, 0.00157, -1.00356] est

**I measured all three against the real data before writing them down** and they
match C1's table exactly. The third is declared as a DEMOTION, not a removal -
the mount kept its marker, the CIG position was withheld, and the page now says
`est`. Calling that "removed" would record the wrong event.

**A port name alone would have excused any future change to those mounts**,
including a second real regression landing on the same one. Both ends are
asserted.

## PROVEN THREE WAYS, RULE 12

    undeclared loss     FAIL  got=['Aegis Gladius:9']    the list does not blanket-excuse
    wrong transition    FAIL  x2 - unmoved AND stale     two independent alarms
    stale declaration   FAIL  got=['AEGS_Gladius:1']     a declaration nothing fires is fiction

All three probes are in `_to_delete/probes-20260829/`, never deleted.

## THE SWEEP AND THE GATE

    106 ok, 0 failed, 0 skipped, 0 NOT RUN, in 706s
    sweep_gate --check testing/_deploy
      106 control(s) green against this exact payload (2026-08-29T13:35:46)
      GATE EXIT 0

**The gate was refusing C1's `--only` receipt, exactly as Sleven said** - 9
controls, 3.7s, `partial: true`, naming a child-markers red that no longer
existed. Not the payload.

## DEPLOYED, AND VERIFIED ON THE SERVED BYTES RATHER THAN ON EXIT 0

    Uploaded 1 of 1 asset   + /loadout_marker.gen.js
    https://citizencompasstesting.citizencompass-contact.workers.dev
    Version a0f092a4-89f4-407e-b061-6b951ee3ad3d

**One file changed, and it is the fore/aft withholding.** The other 524 were
already uploaded.

The deploy script says in as many words that exit 0 is not proof, so:

    /                        HTTP 200    431,674 bytes
    /models/Hammerhead.glb   HTTP 200  3,608,636 bytes
    /loadout_marker.gen.js   HTTP 200    282,961 bytes
    served sha256 == local sha256   (2536dbdbe37aec05)
    index carries id="cc-kb" and id="cc-panel"

**And the three ports, read off the file the site is actually serving:**

    259 hulls, 6058 markers
    BANU_Defender port 50   GONE
    BANU_Defender port 51   GONE
    MISC_Hull_C   port 34   ['34', -0.00408, 0.00157, -1.00356, 'est']

The three deployed-site controls - `_verify_find_deployed.mjs`,
`_verify_deployed_links.mjs`, `_verify_picker_deployed.mjs` - are all green
against the new deploy.

**The site is no longer on 04:47.**

## WHAT THAT CLOSES

    Q21  DONE - the deploy gate passes
    Q27  DONE - declared exceptions, baseline untouched
    Q26  UNBLOCKED - the three survivors can now be measured against a
         payload that is actually deployed

Uncommitted: `checks/_verify_child_markers.py` and today's updates. Nothing has
been committed since `d1e60b4`.

**Not started: Q26, Q28 (C1's), Q29, Q30.** Q29 is the one I would take next -
the sweep cannot say "I could not look", and two controls already exit 2 trying.
