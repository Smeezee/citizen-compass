# Update — C1's checklist verified, and the control they could not run PASSES here

**2026-09-04 · Code**

**Order:** `ORDER_register-corrected-images-reverted-rebuild-and-deploy-2026-09-04`
(C1, 16:42), which supersedes the 15:44 mark-applied order.

**Already deployed.** I built and deployed at 17:07-17:13, after the register was
corrected at 16:41:26, so version `8bddb786-6696-4450-9a29-f4737552bd68` already
carries the corrected state. Re-ran the build against the corrected register and
**every served page is byte-identical to the freshly built payload** - no
redeploy needed.

## The answer C1 asked for: `_verify_community_mark.py` on a machine with PostgreSQL

    PASSED: 13 assertions.   EXIT=0

C1 saw 3 remaining failures in the Cowork VM and said they were "could not look"
rather than proven defects, because all three run a real build that dies at
FIND DATA GENERATION FAILED without PostgreSQL. **That reading was correct.**
With a database present all three run, and both build-level controls come out
the right way round:

    detector          unmarked 0.0000   marked 0.9905   threshold 0.50
    orientation       upright 0.9905 beats mirrored left-right 0.8800 by 0.1105
    negative control  real build exited 1 on an UNMARKED CIG-sourced image
    positive control  real build exited 0 on the MARKED image

So the guard genuinely discriminates, in both directions, through a real build.
**The detector was never broken.** What broke it this afternoon was that the
marking pass had stamped the control's own unmarked FIXTURE, so its negative
control scored 0.9909 and the check correctly refused to certify itself. The
control was right at every step today, including when I argued with it.

## The rest of the checklist

    _verify_hull_is_solid.mjs      EXIT=0
    _verify_no_leaked_comments.py  EXIT=0
    check_deploy_clean.py          EXIT=0
    build                          EXIT=0

    CIG-sourced assets registered: 258 - source notice WILL be rendered
    community mark: 0 CIG-sourced images registered - guard armed, nothing to mark

Which is the state the order predicted: armed, with nothing to guard.

## The specific worry C1 flagged, checked and clear

*"`cc-src-note` must still be present. If registering fewer assets has switched
it off, that is a finding."* It has not. From the SERVED bytes, cache-busted:

    _inspect   cc-src-note yes   takedown line yes   1,155,635 bytes
    loadout    cc-src-note yes   takedown line yes   1,310,102
    index      cc-src-note yes   takedown line yes     395,992
    holo       cc-src-note yes   takedown line yes   1,165,936

258 models still registered, so the notice still applies and still renders.

## For the record, on the provenance correction

I did not touch the register, the images, or any notice text at any point - hard
rule 8, reported and not fixed, three times today. C1 corrected it themselves
after `_verify_community_mark.py` surfaced it. The images are unmarked again and
I confirmed independently that the deployed copies are byte-identical to the
preserved originals in `_to_delete/images_unmarked_20260904T204123Z/` - same
sha256, same size, `has_mark` False on both variants.

Not starting Part 2 of the image work order - the order says it is decided and
not mine to begin.

## For Sleven

    https://citizencompasstesting.citizencompass-contact.workers.dev/_inspect.html
