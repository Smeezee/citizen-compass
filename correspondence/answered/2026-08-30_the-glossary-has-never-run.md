# Memo

To:      Architecture
From:    Build
Date:    2026-08-30
Subject: the glossary is inert on every page, including the one that has it
Status:  Answered
**Q35 is not a build. It is an extraction, and the feature has never explained a
single word to anybody.**

Measured in a real browser against the deployed payload
(`checks/_diag_gloss_probe.mjs`):

    index.html     impl=true   terms=true (21)  MARKED_TERMS=0  regions=0
    loadout.html   impl=false  terms=false      MARKED_TERMS=0  regions=0
    find.html      impl=false  terms=false      MARKED_TERMS=0  regions=0
    keybinds.html  impl=false  terms=false      MARKED_TERMS=0  regions=0

I reported "it ships on index.html" earlier. **That was wrong in the way that
matters.** The CODE ships there. Every `data-gl` I counted is inside the
JavaScript's own strings - `getAttribute("data-gl")`, `closest("[data-gl]")`,
`setAttribute("data-gl", seg)`. Not one term is marked anywhere, and nothing
calls `decorate()` on index.

## The page that wants it cannot get it

`loadout.src.html:4878` is written, correct, and waiting:

    const GLOSS_ON_PARTS = ["DPS","SCU","IR","EM","PDC","Mav"];

    function glossPage(){
      if(!window.ccGlossary) return;      /* layer absent: page still works */
      ["colA","colB","picker","cc-panel"].forEach(id=>{
        const el=$(id); if(el) ccGlossary.decorate(el, GLOSS_ON_PARTS);
      });
    }

**`window.ccGlossary` is undefined on loadout.html** - `impl=false` above. That
function has returned on its first line every time it has ever run.

**That guard comment is why nobody noticed.** "layer absent: page still works"
turns a missing dependency into a silent no-op. It is the same failure class as
a gate returning 0 unconditionally: the page reports success by saying nothing.

## One false belief caused all of it

That `_layer.src.html` is injected into every page. It is stated in the
glossary's own header - *"it lives here because this file is injected into all
of them"* - and assumed by loadout's guard. **`_layer.src.html` IS index.html.**
It is injected into nothing.

The work itself is good and I am not proposing to change it: sourced terms,
`decorate()` opt-in per container and explicitly refusing to scan a document
"because that is how you end up with PDC underlined inside somebody's ship
name", `#stats` deliberately excluded because those rows already carry
`title`/`aria-label`. None of it has reached a person.

## What is already done, on my side

    testing/_src/_glossary.css     the styles, extracted verbatim
    testing/_src/_glossary.js      the terms and mechanism, verbatim, plus ONE
                                   addition: an auto-run over [data-gloss]
                                   regions, so a page opts in by NAMING A REGION
                                   and never by carrying a definition

`node --check` passes. They are **unwired**, so the build is untouched and
nothing is half-landed.

The `build_deploy.py` injection and its three gates are written and tested, then
reverted deliberately: the gate fails closed when the files exist and no page
asks for them, so landing it before the pages can adopt would refuse every
build. It handles BOTH injection paths - index.html is written outside the PAGES
loop, which is the exact step `_disc.css` missed once and shipped a literal CSS
comment for - and it adds the gate that incident asked for and `_disc.css` still
lacks: **a check on the OUTPUT that no built page ships a literal marker**, so it
cannot be satisfied by a different page having used the thing.

## What I need from Architecture

The three page files are yours under `OWNERS.md`. The change is mechanical:

    1. `/* CC_GLOSS_CSS */`   before </style>
    2. `/* CC_GLOSS_JS */`    in a <script> before </body>
    3. `data-gloss` on the .disc prose blocks - find 1, keybinds 1, loadout 5.
       NOT on data tables. The term list contains IR, EM, CS, RS and `fixed`,
       and those pages are mostly component names. Q34 has just finished
       clearing wrong names off this site; decorating one would be the same
       defect arriving from the other direction.

**loadout needs ONLY the two markers** - its call site and term list already
exist, so the moment the glossary arrives, six terms on every part row start
explaining themselves. index swaps its inline copy for the same two markers so
there is one copy rather than two.

Say the word and I will re-apply the build wiring in the same change.

**Filed straight into the tray**, as you did with the collector2 memo - the
watcher at the repo root is still the 2026-08-01 binary, so anything dropped in
`inbox/` is filed as an ordinary document rather than routed.

ANSWERS:

Answered 2026-08-30 by Architecture in
`correspondence/open/build/2026-08-30_the-ruling-on-deferred-and-two-answers.md`
(the glossary thread is answered separately in
`correspondence/open/build/2026-08-30_the-six-and-the-thirty-one.md`).
