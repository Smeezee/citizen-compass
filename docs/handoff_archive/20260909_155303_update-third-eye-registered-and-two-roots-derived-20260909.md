# Update — the third eye is registered, both hard-coded roots are gone, and OWNERS is green

**2026-09-09 15:56 CDT** (`date`, read immediately before writing).

Architecture accepted both send-backs and sent four items back. All four are
answered; three needed work.

## `_verify_owners.py` — GREEN, AND ARCHITECTURE COULD NOT RUN IT

They lost their shell to this machine and said plainly they would not claim a
green they had not seen. Ran it:

    83 owned path(s), 3 owner(s); NEXT.md enumerates 0 (must be 0)
    A. every owned path exists        passed
    B. no path is claimed twice       passed
    C. NEXT.md keeps no second copy   passed          exit 0

Both new rows resolve — `design/ANGLES.md` and `testing/_src/next.src.html`.

## THE CONTACT SHEET — OUT OF `docs/`, REGISTERED, PROVEN

    was  join(ROOT, "docs", "contact_sheet_20260905")
    now  join(ROOT, "checks", "_diag_output", "contact_sheet")

Architecture's ruling: *"register them UNCHANGED" governed what the eye READS,
not where it writes* — and independently of rule 25, a scheduled control should
never have been writing into `docs/`, which is a directory people write.

**`docs/contact_sheet_20260905/` is untouched and still there.** I have not been
near it.

`checks/_diag_output/` is gitignored with rule 21 named in the comment — every
frame in it is internal working material.

**Registered as `contact_sheet_eye` in `node_checks.py`.** Its wrapper splits the
four failure kinds by what they mean rather than lumping them:

    LOAD FAILED / EMPTY     a hull the site CANNOT DRAW      DEFECT
    INVISIBLE / OVERFLOW    framing, which belongs to the    WARNING
                            camera control - two controls
                            arguing over one number is how
                            one of them gets ignored
    page errors             WARNING
    ok 0 of 0               DEFECT - a sheet of nothing is the shape of
                            every silent success this project has found

## BOTH HARD-CODED ROOTS ARE GONE

    _diag_pixel_probe.mjs:4        ORDERED    C:/Users/david/citizen-compass
    _diag_q5_contact_sheet.mjs:37  NOT ordered - same defect, same file family

Both now derive the repo from the script's own location, the way
`tools/frontpage/build_next_frontpage.py` does. **The probe's readback is
byte-identical after the change** — `nonBlank 35906, pct 10.61%` — so it changed
where it looks for the repo and nothing else.

**The second one is an extension of the order and I have flagged it to
Architecture rather than slipping it in.** Their stated reason applied to it word
for word, and it was about to become a registered check, but inferring beyond
what was written is exactly what the delegation rule says is not delegation.

## ONE HOUR-LONG TRAP WORTH RECORDING

My first version of the contact sheet's new comment quoted the out-of-scope glob
literally — `docs/contact_sheet_` followed by star-slash. **In a `/* */` block
comment that closes the comment**, and the file stopped parsing on the next run.
The comment now says so in its own text, so the next person to quote that glob
into a `.mjs` finds out from the comment rather than from node.

## RULE 12 — 22 CASES NOW, ALL GREEN

`checks/_verify_eyes.py` grew nine cases for the third eye and covers all three
wrappers. `--self-test` exits 1. `_verify_rule16_labels.py` green.

**A full contact-sheet run is measuring now** — 256 hulls, past 96 as this is
filed. That number decides the other eighteen eyes, so it goes to Architecture as
soon as it lands.

## THE HULL MATERIAL IS WITHDRAWN

Architecture withdrew the order outright: *"it is a renderer decision, not a
settings decision, and I am not ordering a removed pass back without knowing why
it was removed."* Nothing asked of this desk. The normals defect stays on my list
as its own item.

**Nothing committed.**
