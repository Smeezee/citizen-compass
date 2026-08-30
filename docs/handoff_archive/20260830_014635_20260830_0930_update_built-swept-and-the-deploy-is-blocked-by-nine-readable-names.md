# Update — built and swept. My four controls are fixed. The deploy is blocked by nine names a visitor can read, and they are C1's.

**2026-08-30 14:30 UTC / 2026-08-30 09:30 local · Code (background session)**

## THE BUILD CARRIED EVERYTHING

    cmSummary     src 2  deploy 2      Hull armor    src 2  deploy 2
    unnamedTag    src 4  deploy 4      Hull armour   src 0  deploy 0
    comment strip: 1677 removed; every deployed .js and inline script parses
    Greycat 3, Grey's Market 3         <- names preserved, as instructed

## DRACO IS IN, AND NOT RUN IS GONE

    106 ok, 4 failed, 0 skipped, 0 NOT RUN, in 926s

`_verify_marker_mesh_distance.py` now runs and passes - 5,800 markers on 256
hulls. Installed `--no-save` into `checks/node_modules`; **`checks/package.json`
is byte-identical**, which was Sleven's constraint.

## FOUR OF MINE, AND THEY WERE ALL ONE DEFECT

**`_verify_column_split.mjs`** read `data-fixed` alone in TWO places and put
**716 ports on the wrong side fleet-wide** - every one a countermeasure sitting
exactly where it belongs. Its L4 section also sampled the first fixed port with
a part, which is now inside the summary and has no row: `indexOf` returned -1,
the "row" became the last character of the page, and three content assertions
failed against a correct page. **27 assertions, exit 0.**

**`_verify_panel_findable.mjs`** asserted the title contained `colour`. Sleven's
US-spelling instruction reached the copy and it went red. **A control that pins
the spelling of a word is asserting house style, not behaviour** - it now
accepts `colou?r`.

**THAT IS FIVE PLACES ACROSS THREE FILES.** C1 named two. `_verify_ship_page`
held four, `_verify_column_split` three more. The rule "a fixed port is
represented by its own row OR by a summary naming it" is now written out
identically in three files, **and that is the weakness**: the sixth copy is the
one that will be missed. Worth one shared helper, and I am not building it at
the end of a pass.

## THE DEPLOY IS REFUSED, AND IT IS RIGHT TO BE

    _verify_display_names.py   REFUSED - 9 name(s) a visitor can read

    truncated  6
      BMBRCK_S03_BEHR_Single_S03   shows 'CST-313 \'
      Turret_PDC_BEHR_G            shows 'MRX \'      game  MRX "Torrent"
    disagrees  3
      MRCK_S04_KRIG_S65_Stingray_Left   shows the raw class name

**Six names are truncated at a backslash.** `MRX "Torrent"` becomes `MRX \` -
which reads like an escaping bug in the name derivation, where a quoted name is
cut at the escaped quote. **C1's own control caught it**, which is the system
working, and it is C1's to fix: `build_loadout_data.py` is theirs as of today.

**I have not deployed.** Nine wrong names on a page whose claim is that its
numbers can be trusted is not something to ship past a red control.

`_verify_picker_deployed.mjs` is the fourth failure and is deployed-only -
expected until this ships.

## ANSWERS

**C1 claiming `build_loadout_data.py` is not wrong.** The ship page and its data
are theirs; a generator whose only consumer is C1's page should not have a
different writer.

**Q38 not touched.** Ping and we move `_WEAPONY` and `MARKABLE` together.

**Q44 recorded:** no fuzzy matching in the reader, Levenshtein out, exact
vocabulary hits only. Not started.

## AND ONE THING C1'S SPELLING PASS MISSED

Identifiers were correctly left alone - `id="armour"`, `_view.colour()`,
`data-colour`. **Five pieces of VISIBLE copy were not:**

    index.html    "Calm - muted colour, no motion, soft borders"
    index.html    "Turning this down helps if bright colours feel harsh"
    loadout.html  <th>vs. unarmoured</th>

C1's files. Reported, not edited.
