# Update — collector2 rebuilt after C1's -from; probe retired; moving to Q35

C1 changed `main.go` and `read_gamelog.go`. Rebuilt, vet clean, **30/30 green,
exits 9.**

**Both my fixes survived C1's edit to the same file** — checked rather than
assumed, since `read_gamelog.go` had two writers today: the `itemName`→`item`
mapping is present and the `identifying`/`scrubIDs` scrub is intact (9 hits).

**`-from` reproduces my probe exactly**, over the same 243 archived logs:

    read 243 log file(s) from ...\LIVE\logbackups
       recorded 601 observation(s)      (312 payout + 289 shop_transaction)
       asked    10 question(s)

`-derive` → 238 facts. `-questions` → 8 distinct open questions, all commodity
`ResourceContainer` lines identified by `resourceGUID` with no item name, and all
of them reading `playerId[<removed>] shopId[<removed>]`. The scrub is visible in
real output, not just in a test.

`collector2/zz_archive_probe_test.go` is **retired to `_to_delete/`** — `-from`
does the job as one command. Moved, not deleted, per rule 1.

C1 is building screen reading next, in collector2 only. No overlap with the site
work, so rule 14 is clear.

**Next: Q35.** Q34's DONE-WHEN is verified satisfied (control exits 0, self-test
exits 9, and it reads labels from the snapshot the payload's own header names, so
it is not passing on stale truth). That unblocks Q35.

**Q35's shape, before writing it — rule 5.** Following the `_disc.css` precedent
exactly, because Q35 names the disclosure bar as the drift it must not repeat:

    testing/_src/_glossary.json   the terms. ONE writer, one file.
    testing/_src/_glossary.css    injected at /* CC_GLOSS_CSS */
    testing/_src/_glossary.js     injected at /* CC_GLOSS_JS */
    build_deploy.py               injects both, and FAILS CLOSED when the file
                                  exists and no page asked for it - the same
                                  gate _disc_used already has
    checks/_verify_glossary.mjs   RULE16, in a real browser: hover shows, tap
                                  shows, tap-elsewhere closes, Escape closes

**THE ONE RISK, NAMED BEFORE I BUILD IT.** The starting set includes `IR`, `EM`,
`RS`, `CS` and `S1`-`S10`. Auto-wrapping two-letter tokens across pages full of
component and ship names is the SAME defect class Q34 just cleared — `MRX \` and
`VariPuck S6` were exactly that. So the matcher will be:

  - whole-token only, case-sensitive for acronyms
  - never inside `input`, `textarea`, `code`, `script`, `option`, or an existing
    glossary node
  - a container ALLOWLIST rather than the whole document, plus an explicit
    `data-noglossary` opt-out for any subtree that turns out to be name-dense
  - proven by a control that plants a ship name containing a term and asserts
    it is NOT wrapped

If that cannot be made safe on the loadout page, the honest answer is to scope
the glossary to prose regions and say so, rather than decorate a name.
