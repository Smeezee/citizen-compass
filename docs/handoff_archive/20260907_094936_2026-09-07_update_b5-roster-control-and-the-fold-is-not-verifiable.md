# Update - B5 second control written and PROVEN. And it turned up something real: a fold and a silent loss are the same observation today.

    checks/_verify_front_page_roster.py       RULE16: INDEPENDENT
    6 assertions, 0 failed   -   253 ships on the page, 254 in the source

## What it asserts

    1  no ship appears twice, and every card carries a name
    2  the page invents nothing - every ship on it is in the source data
    3  no ship is silently absent - every absence declared BY EXACT NAME,
       and no declaration outlives its reason
    4  the parent a ship was folded into actually SHOWS an edition line

## THE FINDING, and it is why assertion 3 needed a declaration at all

Sleven's fold ruling is working: the page shows 253 where the data holds 254,
and the missing one is `Valkyrie Liberator`, folded into `Valkyrie`. Correct.

**But the page records a fold as a DISPLAY LABEL on the parent and never the
name of the ship that was folded.** The Valkyrie carries
`ed: [{name: "Liberator Edition"}]`. It does not carry "Valkyrie Liberator".

So from the built page alone:

    a ship folded on purpose   looks like:  absent from the roster
    a ship dropped by a bug    looks like:  absent from the roster

**They are the same observation.** And recovering "Valkyrie Liberator" by joining
"Valkyrie" to "Liberator Edition" is a string concatenation dressed up as a fact
- rule 17. It happens to work for this one and fails silently the first time a
fold is named differently from its parent.

**So the absence is DECLARED by exact name in the control, with Sleven's ruling
cited**, and a declaration that stops firing is refused. That keeps it honest
today. **The durable fix is for the fold to carry the folded ship's own name** -
`ed: [{name: "Liberator Edition", of: "Valkyrie Liberator"}]` - after which the
declaration can be deleted and the check verifies the fold directly instead of
trusting a list. **That is C1's generator, so I am reporting it rather than
doing it.**

## Rule 12 - PROVEN, seven cases, against damaged COPIES

    ok   the undamaged copy passes - or nothing below counts            exit 0
    ok   one ship duplicated -> 'appears exactly once' fails            exit 1
    ok   a ship the data never had -> the page invents nothing fails    exit 1
    ok   an UNDECLARED ship removed -> a silent absence is caught       exit 1
    ok   the parent's edition line stripped -> the fold shows nothing   exit 1
    ok   a declared fold put BACK -> the stale declaration is refused   exit 1
    ok   the DATA block gone -> NOT PERFORMED (exit 2), never a pass    exit 2

`testing/_deploy` is never opened for writing - each case writes one mutated
page into the scratchpad - so there is no restore to interrupt.

## One implementation note worth keeping

The page's roster is read with `json.JSONDecoder().raw_decode`, which stops at
the end of the first complete JSON value. **My first attempt used a regex and it
swallowed the script that followed the DATA block** - it parsed, it just parsed
the wrong thing. `raw_decode` does not guess where the value ends.

## State

    124 checks, 0 unlabelled, 0 malformed rule-16 labels
    B5: 2 of 6 checks written; both proven
        remaining 4 all depend on B2's schema (price_status, name_alias) or on
        the database driving the page

Full sweep running. **Nothing shipped** - these are checks; the payload is
untouched and the site is unchanged since 19:59 last night.

## Open, unchanged

- The ragged card height is live, on Sleven's go-ahead. **Still worth C1
  levelling.**
- 241 unreferenced images - rule 5 list filed, nothing moved.
- B2 on five hand-entered families. B1 behind B2.
- `build_frontpage_data.py` untracked, needs Sleven (rule 2).
- Ownership gaps: `testing/_src/next.src.html`,
  `checks/_verify_broken_checker_end_to_end.py`.
