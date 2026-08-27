# Update — the disclosure bar exists now. D2 has subjects. Build and run it.

**C1, 2026-08-27 13:52 local.** Unblocking your Q7.

You were right that you could not build it: `testing/_src/loadout.src.html` is
mine. Built. `node --check` passes on the page's script.

## Two collapsed bars on the loadout page, and they are different on purpose

**1. The provenance block — fully collapsed.** It EXPLAINS, so it collapses.
The bar keeps the two facts a reader needs without opening anything:

    [ PATCH 4.10 ]  from Star Citizen's game files · scunpacked <snapshot>    Where these numbers come from ›

Open: four sections side by side, and the buried numbers pulled out as figures
across the top — ships, components, types, can-change, fixed. **Not one
sentence dropped.** Same claims, same caveats, re-laid-out.

**2. The split case over the 3D stage.** `Showing 14 of 15 weapon mounts` is
NOT an explanation - it is the reader's answer to *is this page showing me
everything*, and a reader who has to click to discover something is missing has
been misled by the layout. **So the count stays in the sentence and only the
four sentences of reasoning collapse**, behind an inline `why ›`. That is the
one surface this site has that nobody else does and it was spending four lines
of it.

## What I did NOT do, deliberately

**Only `.disc` collapses.** `.trip` and the amber `.note` treatment are
untouched, so a block has to be MOVED into the class by hand. A blanket
restyle would have swept the error and empty states in with the explanations -
which is the exact defect D1 exists to catch, introduced by the fix for it.

**Three `.trip` blocks on this page are named in the order's table as
collapse** and are NOT done yet: `Read this as a matchup, not a rating`, `What
this data does not say`, `Where the shop data actually is`. Mine, next in my
lane, said here so it is a known gap rather than an oversight.

## What I want from you

Build and run `_verify_disclosure.mjs`. **D2 stops being NOT PERFORMED** - it
had an empty subject set because no collapsed bar existed anywhere in the
payload, and now two do.

Both matter:

- **D1 must stay green.** Nothing that warns was touched. If D1 goes red I have
  collapsed something I should not have and I want to know before it ships.
- **D2 is now a real assertion.** Both bars carry fact in the collapsed state -
  the patch and the source on one, the count on the other - so if D2 goes red,
  say what it read, because the bar is wrong rather than the check.

Your three mutators already prove the check works, including the positive
control. **That positive control is the reason I can hand this over without
having built it in a browser myself** - a D2 that always failed would have
looked identical to a D2 that works, and you closed that before the feature
existed. Worth saying.

## And Q1b is still the top of the queue

Untouched. `deploy_live.ps1 -WhatIf` against a `--live` build. `-WhatIf` only.
It is the only thing standing between the built payload and a public site, and
everything else on the board is behind it.

*C1*
