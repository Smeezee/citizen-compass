# Update — Q54 IS UP. The front door serves the new page, confirmed from served bytes.

**2026-09-11 03:12 CDT / 08:12 UTC. Deployed, then verified — exit 0 is not
proof and the script says so itself.**

## CONFIRMED FROM THE SERVED ORIGIN, NOT FROM THE BUILD

    /            200   141,641   the new page          <- the front door
    /next        200   141,641   the same page
    /classic     200   396,153   the old page          <- its stated address
    /index.html  307 -> /        Cloudflare's own html_handling
    /find        200    31,387   untouched
    /keybinds    200    94,082   untouched
    models/Hammerhead.glb  200  4,153,816 bytes

**`/` SERVES the new page with a 200.** Not a redirect — the address bar stays at
`/`. Only two files went up, `next.html` and `classic.html`: `_redirects` is
parsed by Cloudflare rather than served as an asset, so the only proof the rule
took effect is the 200 above, which is why it was checked rather than assumed.

**In a real browser, against the live origin** —
`checks/_diag_q54_front_door.mjs`, 7 assertions and 2 canaries, all green:

    /          fresh profile    the gate, and the gate is the ONLY visible
                                top-level element
    /          unlocked         the new page, 253 cards, 0 table rows
    /classic   fresh profile    gated too
    /classic   unlocked         the old page, 272 rows, and its overlay,
                                keybinds board, help tab and back-to-top all
                                present
    /next      unlocked         the new page, unchanged
    a bad URL  404              and NOT reported as the new page

**Q54's DONE-WHEN is met in full:** the front door serves the new page, the old
page is reachable at a stated address, and both are confirmed from served bytes.

## THE FOOTER, ON THE LIVE SITE

> *"aUEC prices are community-reported and dated — **not verified in game**.
> Verification is incomplete: most ships on this page do not yet show the patch
> they were checked against."*

**And the invented RAPTOR sentence is gone from the served bytes** — `grep`
count 0 where it was 1 an hour ago. The trademark strip is byte-for-byte what it
was. **Nothing was done about the confidence notes: still Q55.**

## THE GATES THAT HAD TO PASS, AND DID

    build receipt   ok (03:10:11)
    payload sanity  password gate present, testing stamp present
    deploy guard    only known assets
    browser checks  4 green
    sweep           129 controls green against THIS payload (f311de02b8650a5d)
                    0 failed, 0 not run
    token           scoped, from .env, length only

**The dry run was verified from outside before the real one.** `-WhatIf` said
"Nothing was uploaded"; `/classic` still 404'd and `/` still served 396,153
bytes, so the flag was proved by behaviour rather than by its own claim — which
is what hard rule 12 asks of a safety switch, and this repo has been bitten by a
`-WhatIf` that did not apply.

## THE ARCHIVE ENTRY IS WRITTEN

`docs/FINDING_where-the-automation-stands-at-the-freeze-2026-09-11.md`. One
entry, written to stand alone, everything read off the machine rather than out
of a memo. It carries two corrections to the letters that ordered it:

**1. The running watcher is NOT the binary in `watcher-go/`.** The scheduled
task runs `C:\Users\david\citizen-compass\inbox_watcher.exe` — PID 19112,
sha256 `F9D983B2…`, 5,770,752 bytes, 2026-09-10 15:14. `watcher-go\inbox_watcher.exe`
is a different, older build: `1EBBCDBE…`, 5,761,024 bytes, 2026-09-07 23:31.
**A restart that rebuilds in `watcher-go/` and assumes the new binary is live
will be wrong.**

**2. The five `switch_off` refusals are entries 9 to 13, not the last five.**
C1's letter says the last five entries are those refusals; the last three are
`wake_start`, `wake_end` and `wake_usage` for the authorised probe. **The
substance holds — the launcher does refuse with the switch off, five separate
times — but the letter's own point was to verify from the log rather than from a
memo, so the log is quoted as it reads.**

**And one of C1's facts is now sourced properly rather than repeated.** The
`Edit(...)`-governs-`Write` finding is real, but the probe JSON it cited
contains no command line at all — it carries `permission_denials`, `modelUsage`
and the result. So the flags come from `scripts/wake_desk.py:68` and `:172` and
the denials from the JSON. **Both halves confirmed, neither taken on trust.**
C1's 0.527 figure for the probe checks out against the log: `total_cost_usd`
0.52735.

**The switch is absent**, confirmed by listing `C:\Users\david\.cc-control\` —
the directory exists and is empty.

## WHAT I DID NOT DO

**Nothing in the wake system was touched.** No step C, no doorbell, no
activation, no brakes. `MAX_BUDGET_USD` was NOT adjusted, per C1's instruction
to re-derive it from real tokens when the freeze lifts. The archive entry
records that its margin claim is wrong and leaves the number alone.

**Nothing committed.** The working tree holds tonight's changes:
`tools/frontpage/build_next_frontpage.py`, `testing/_src/build_deploy.py`,
`testing/_src/deploy_pages.py`, `checks/_verify_deploy_drift.py`,
`checks/_verify_correspondence.py`, the regenerated `next.src.html` and
`the-index.html`, six new files in `checks/`, and two new `docs/` findings.
**Hard rule 2 — a commit needs his go-ahead in the message that asks for it.**

*Code, 2026-09-11 03:12 CDT.*
