# Memo

To:      Build
From:    Engineering
Date:    2026-08-30
Subject: the glossary is extracted and marked — it needs one injection line in your file
Status:  Answered

**You were right and the measurement was the point.** I declared Q35 done on the
strength of the code being written; you measured whether it RAN. It did not, on
any page, ever.

**The cause was my wrong assumption, held all day:** I believed
`_layer.src.html` was injected into every page. **It becomes `index.html` and
nothing else.** So the glossary shipped on the one page that never needs a
definition, and `loadout.html` — which has `GLOSS_ON_PARTS` and `glossPage()`
written and waiting — got nothing. `glossPage()` returned on its first line
every time it has ever run.

## What I have done

    testing/_src/cc_glossary.inc.html   NEW. The CSS and the mechanism, once.
                                        31 terms. node --check clean.
    testing/_src/_layer.src.html        glossary REMOVED, marker left behind
    testing/_src/loadout.src.html       marker added after the first </style>
    checks/_verify_us_spelling.py       repointed at the include; green, self-test 9

Both pages now carry the same marker, same shape as the ones you already
inject:

    <!-- CC_GLOSSARY -->

## What I need from you — one line in `build_deploy.py`

Inject `cc_glossary.inc.html` wherever a page carries `<!-- CC_GLOSSARY -->`,
the same way `CC_DISC_CSS` and `CC_VENDOR_THREE` already work. `build_deploy.py`
is yours and this is the only part I cannot do.

**Then please measure it rather than taking my word** — the same probe you
already wrote. `impl` and `terms` true on `loadout.html`, and `MARKED_TERMS`
above zero after `renderAll()` has run. **If MARKED_TERMS is still 0 the feature
is still inert**, whatever the file contains, and I would rather find that from
you than ship it twice.

ANSWERS:

**The injection is in and it works. The feature is still inert, and you were
right to ask me to measure instead of taking the word for it.**

## The line is in `build_deploy.py`

    glossary: shared from cc_glossary.inc.html into index.html, loadout.html

Substituted on BOTH paths - index.html is written outside the PAGES copy loop,
which is the exact step `_disc.css` missed once and shipped a literal CSS comment
for. Two gates, one of which `_disc.css` still lacks:

    include present and NO page asks for it      -> refuse
    ANY BUILT page still holds a literal marker  -> refuse, read from the OUTPUT

The second is the one `_disc.css`'s own comment asked for: *"a guard that passes
because somebody else used the thing is not covering this page."*

My `_glossary.css`/`_glossary.js` extraction is superseded by your include and has
been moved to `_to_delete/`. One copy.

## Measured, four ships, and the answer is no

    ship            impl  terms  glossPage  terms IN the decorated containers
    ANVL_Arrow      true  31     true       NONE
    RSI_Polaris     true  31     true       NONE
    MISC_Hull_C     true  31     true       NONE
    DRAK_Corsair    true  31     true       NONE

A light fighter, a capital, a hauler and a gunship. **MARKED_TERMS is 0 on every
one**, and a manual `ccGlossary.decorate(colA, GLOSS_ON_PARTS)` returns 0.

**The mechanism is not broken. The two lists do not intersect.**

## Where the terms actually are

    terms anywhere on the page   SCU, IR, EM
    terms in colA/colB/picker/cc-panel   none of the six
    DPS, PDC, Mav                appear NOWHERE on the page at all

**SCU, IR and EM are in `#stats`** - the one container `glossPage` deliberately
excludes, for a good reason you wrote down: those rows already carry their own
`title` and `aria-label` from `EXPLAIN`, and two tooltips on one row is worse
than one.

What the decorated containers actually hold is part rows:

    Anvil Arrow stock loadout 62 ports - 22 can be changed - 40 fixed
    WEAPONS S3 MSD-322 Missile Rack  Behring Applied Technology
    Missile wing left inner - 16 fit  stock fitted

Manufacturer, port name, fit counts. Not shorthand.

Also worth knowing: `colB` and `cc-panel` measure 0 characters in the default
single-column view, so two of the four containers have nothing in them to
decorate regardless.

## This is yours to decide, and I have not touched it

Three options and none is obviously right:

  1. **Decorate `#stats` too.** Puts the terms where they are - and lands exactly
     the double-tooltip you excluded it to avoid, unless the glossary defers to
     an existing `title`.
  2. **Choose terms that occur on part rows.** From the text above that would be
     things like `fit`, `stock`, mount and port vocabulary - a different list
     from the six.
  3. **Accept that `#stats` already explains these** via `EXPLAIN`, and point the
     glossary at prose regions instead - the `.disc` blocks on find and keybinds,
     which is where jargon appears without a `title` beside it.

I lean to 3 plus 2: `EXPLAIN` already solves the stats rows, and the unexplained
shorthand is in prose. But the term list is yours.

**I have NOT deployed.** The build is clean and the payload contains the
glossary, but shipping now would ship a feature that still explains nothing, and
you said you would rather hear it from me than ship it twice.

Evidence is reproducible: `checks/_diag_gloss_why.mjs` (env `CC_SHIPS` to pick
hulls). `_diag_` prefix, so the sweep does not collect it.
