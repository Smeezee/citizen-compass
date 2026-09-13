# Update — the stamp is on the served front door, and the guard that missed it now watches it

**2026-09-11 12:50 CDT / 17:50 UTC. Deployed and verified from served bytes.**

## THE FIX IS LIVE

**A visitor at the front door now reads `v0.4.0 · 253 ships testing
2026-09-11`.** Read out of the rendered DOM in a browser, not off the build:

    served /        the stamp is present, and matches the guard's own
                    '>testing 20[0-9][0-9]-' pattern
    /               200   141,708   the new page
    /next           200   141,708
    /classic        200   396,153   the old page, still stamped in its title
    /find           200    31,387   untouched
    /keybinds       200    94,082   untouched
    Hammerhead.glb  200  4,153,816

**The front-door walk is green again** — 7 assertions and 2 canaries: the gate
is still the only thing a fresh visitor sees at `/`, `/classic` still serves the
old page and is still gated, and an address that does not exist is still not
mistaken for the front page.

**Q54's regression is closed.** From 03:12 to 12:49 today the served front door
carried no way to tell the testing site from the live one. It carries one now,
and the guard that let it through is the second half of this fix.

## THE DEPLOY FAILED ONCE, AND IT WAS MY MESS

**First attempt aborted: `wrangler exited -4082`, EBUSY on the npx cache.**
`npx` wanted to install wrangler 4.131.1 and could not rename a `miniflare`
directory because **my own `wrangler dev` runs from 01:33 and 01:38 were still
alive** — two npx parents, four node children and four `workerd` processes.

**I had killed the `workerd` processes earlier and not their parents**, so they
respawned and went on holding the cache. Killed properly this time, parents
first, and only the ones I started: PID 23496 (`_diag_serve_deploy.mjs`, from
2026-09-09) is not mine and was left alone.

**Nothing was uploaded by the failed attempt** — checked from outside before
retrying, not assumed from the error: served `/` was still 141,641 bytes with
zero stamps. **The script aborted where it should have.**

**The lesson is small and worth writing down:** a background dev server started
for a measurement is not finished with when its visible child is killed. I
should have shut those down when the fixture work ended at 01:40.

## WHAT WENT OUT

One file, `next.html`, 0.35 KiB. 526 already uploaded. Version ID
`4d223c19-a32f-4e16-a49d-cb67b1e6680c`.

Gates on the way: build receipt ok, **gate and stamp proven on `index.html` AND
on `next.html` (front door: next.html)**, deploy guard clean, 4 browser checks
green, **sweep 129 controls green against this exact payload (`40d01cead30bb93d`),
0 failed, 0 not run**, token scoped from `.env`.

## STATE

    P24             closed. Both halves: the stamp, and the guard's subject.
    Q54             up, and its one regression repaired.
    Q55             entries written and routed to C1; none implemented.
    committed       nothing. Hard rule 2 stands.
    wake system     untouched. The freeze holds.

**The next item is C1's to file** — the P-entries are in
`correspondence/open/architecture/`, and Group A's four can land without a new
decision from Sleven whenever he wants them.

*Code, 2026-09-11 12:50 CDT.*
