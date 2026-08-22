# ERRATUM — every ship name still opens RSI. N1 is not done, and its control could not have failed.

    from    C1, 2026-08-22
    for     Code
    status  DEFECT, live on the testing site right now. Sleven found it in the
              first ten seconds. **Fix this before anything else.**
    ledger  APPEND. This is a correction to N1, not a new feature.

---

## 0. THE SYMPTOM

Clicking a ship name on the index opens **robertsspaceindustries.com**, not the
ship page. **There is now no route to any ship page at all.** N1's whole purpose
is defeated and the site is worse than before the N-run.

## 1. THE CAUSE, located in source

`decorate()` rewrites the name cell **after** the site has already rendered it.
It finds the ship by reading the cell's own text:

    const label = td.textContent.trim();
    const ship  = CC_LOOKUP(label); if(!ship) return;   // <- silent bail

But `nameCellHtml()` (line 764) emits:

    <a class="buy-link" href="…robertsspaceindustries…">${name} &#128279;</a>

`&#128279;` is 🔗. **So `td.textContent.trim()` is `"Redeemer 🔗"`, not
`"Redeemer"`.** The lookup misses, `decorate()` returns, and the cell keeps the
RSI anchor it was born with.

**229 of 254 records carry a `pledge_url`**, so this is nearly every row. The
only names that work are the ~25 with no pledge link — which is why it looks
total.

## 2. THE REAL DEFECT IS THE ARCHITECTURE, NOT THE GLYPH

**Do not fix this by trimming the emoji.** That leaves a design where one writer
renders a cell and a second writer races to rewrite it, matched by display text —
and matching on display text is the exact thing this project banned two days ago
when 22 names turned out to be shared by 51 records.

**Fix it at source: `nameCellHtml()` emits the correct cell in the first place.**
It already has the record. It can decide there whether the ship has a page
(`LOADOUT_LINK`) and emit either the ship-page link or, for the 33 with no game
file, the RSI fallback with its explanation. **One writer, no observer, no
timers, no text matching.**
Then `decorate()` and its three timed re-runs (`decorate(); setTimeout(...,400);
setTimeout(...,1500)`) can go. **A function that has to be called three times at
guessed intervals is telling you it is in the wrong place.**

## 3. THE CONTROL THAT PASSED WHILE THIS WAS BROKEN — this is the part that matters

N12 reported: *"A SHIP NAME LANDS ON THE SHIP PAGE: `shipPageUrl` x3,
`loadout.html#`, and `cc-nobench` present."*

**Every one of those strings IS present. The feature still does not work.** The
control asserted that the CODE EXISTS. It never asserted that a name RESOLVES.
**It could not have failed** — Rule 12, and this project has logged this exact
shape seven times now.

C1 wrote that control requirement badly. The order said *"assert over every entry
point that exists"*, which grep satisfies. **It should have said: resolve a named
ship and check where it points.**

**THE REPLACEMENT CONTROL, and it must be behavioural:**
- Build the name cell for **`Aegis Redeemer`** through the real function with the
  real record, and assert the emitted href is **`loadout.html#AEGS_Redeemer`** and
  **contains no `robertsspaceindustries`**.
- **Negative half:** build it for **`Aegis Vulcan`** — no game file — and assert
  it DOES point at RSI with the explanation. Both halves, or neither is proven.
- **Then across the whole set:** every record with a `LOADOUT_LINK` entry emits a
  ship-page href; **assert the count equals the number of linked records** (221),
  not "at least one".
- **And drive the SERVED page**, as N12 did for the loadout page: run the served
  index's own scripts against the served data and count how many rendered name
  cells point at RSI. **Assert that number is 33, not 229.**

## 4. THEN AUDIT THE REST OF THE N-RUN FOR THE SAME SHAPE

**Every N control that asserted a string is present rather than a behaviour is
suspect.** Go back through N1–N12 and report which ones actually drove something
and which ones grepped. **Do not fix them all in this pass — list them**, and fix
any whose feature is provably broken.

## 5. WHAT MUST NOT HAPPEN

- **Do not fix this by stripping the emoji from the label.** §2.
- **Do not keep a post-render rewriter matched on display text.** §2.
- **Do not report this fixed on a string search.** §3.
- **Do not deploy the live site. Do not `git add -A`.**
- **Deploy to testing when done** — standing rule — and verify from the served
  bytes by counting RSI-pointing name cells.

## 6. REPORT

- The served count of name cells pointing at RSI, before and after.
- The §4 audit: which N controls drove something, which grepped.
- Anything here you think is wrong. **§2 is the part most worth arguing with** —
  if `nameCellHtml()` genuinely cannot see `LOADOUT_LINK` at render time, say so
  and propose where the single writer should live instead.
