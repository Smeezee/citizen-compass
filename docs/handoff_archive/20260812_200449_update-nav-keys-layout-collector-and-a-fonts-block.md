# Update — §4/§5 done except the fonts, which rule 8 stops me doing. Two of these were "already built" and neither was.

`keybinds.src.html`, `stick-test.src.html`, `citizen-collector/{main,ui}.go`,
`build_deploy.py`. Built, all five gates green. **Not deployed.**

## The fonts are BLOCKED, and it is rule 8

§4 asks me to copy the five files into `testing/_deploy/fonts/` and **rewrite the
README that says "intentionally incomplete"**.

**I have not done either, and I am not going to without Sleven saying so
directly.** Rule 8: *"Never edit Fan Kit, trademark, licensing, or legal text...
If you find a gap or an error in one, report it — do not fix it."* Both halves
of this land squarely inside that:

- Placing the files in `_deploy/` is **redistributing third-party fonts** — a
  licensing act, not a copy step.
- The README is a licensing document. It discusses OFL 1.1, the redistribution
  decision, and it *cites rule 8 by name* as the reason it reports the
  requirement rather than satisfying it.

The order says the licence is closed, OFL 1.1, verified from the packages. I have
no reason to doubt that — but rule 8 says the call is **Sleven's alone**, and C1
is not Sleven. The go-ahead quoted at the top of the order is *"let's fix the
things that are broken, push a new build"*, which is not a licensing decision.
A rule beats a task instruction, so I stopped.

**Everything else is ready, and this is a two-minute job once he says yes:**

```
data-layer/derived/fonts-ofl/   ChakraPetch-SemiBold.woff2      9,968
                               Rajdhani-SemiBold.woff2        15,732
                               SairaCondensed-Bold.woff2      17,808
                               SairaCondensed-SemiBold.woff2  17,980
                               OFL.txt                        17,364
```

- `keybinds.src.html` **already declares all four `@font-face` rules** pointing
  at `fonts/<name>.woff2`, with `font-display:swap`.
- The scoping §4 asks for is **already correct**: chrome only — headings, tabs,
  section titles, buttons — and explicitly not the 691-row action table, with
  the reason written beside it (Saira Condensed is a condensed face, which is
  harder to read at low vision, and this page has no font switcher).
- `check_deploy_clean.py` already allows `fonts` in `DEFAULT_ALLOWED_DIRS`.
- The page falls back to the system stack and is completely readable today.

So: **copy five files, delete four sentences from the README.** I need a yes.

## "Two hits exist" — and both of them were the bug

§4 was right to say verify rather than assume. `End`, `Home`, `PageUp` and
`PageDown` **were being swallowed**, and the two greppable hits are *why*:
because `CODE['End']` resolves to a board key, the tester's keydown handler
reached its `e.preventDefault()`. Nothing had been built.

On a 691-row reference page with Capture **on by default**, that meant the only
way to reach the bottom was to turn Capture off — which silently stops the
sticks working. Two innocent decisions adding up to "nothing works", the same
shape as the search box.

Those four keys now behave as they do everywhere else, and are **still reported**
by the tester — showing what was pressed never needed `preventDefault`. **A
deliberate rebind still outranks scrolling**: if a cell is listening, the person
is binding End, not trying to reach the bottom of the page.

`_verify_navkeys.js` slices the real handler registrations out of the page and
asserts both halves, including that an ordinary key is *still* captured so the
tester has not been quietly disabled. Old behaviour swallows 4 of 4.

## The side-by-side layout on /stick-test could never have worked

`#devs` has had `grid-template-columns:repeat(auto-fit,minmax(420px,1fr))` since
Sleven asked for it — *"I wish I could have seen them side by side instead of
having to scroll."*

**`.wrap` caps the page at 780px. Two 420px columns need 854px plus the gap.**
`auto-fit` therefore collapsed straight back to one column at every screen size,
and the page looked exactly as it had before. The declaration was correct and the
container defeated it — nothing in the CSS looks wrong, which is why it survived.

The device grid now escapes the prose width instead of fighting it: 780px is a
good measure for reading and a bad one for comparing two sticks. Centred
breakout, so the page stays centred.

**`/keybinds` was already genuinely side-by-side** — I measured rather than
assumed: the board column is roughly 1240px at desktop width against
`minmax(330px,1fr)`, and the `.rowset` floor of 870px still leaves room for two
330px columns. No change needed there.

## The 128-button default is right, and now says why

Confirmed rather than adjusted. The default shows the first 40 of 128 with an
honest count of the rest, and any button above the cap appears the instant it is
pressed.

**"Hide unused buttons" must stay OFF by default, and there is a hard reason.**
"Unused" means *not pressed since the page loaded* — and at load, nothing has
been. Defaulting it on renders **zero buttons**. I asserted that rather than
argued it:

```
  PASS  turning "Hide unused buttons" ON before anything is pressed hides
        EVERY button - which is why it must not be the default
```

An empty grid reads as "the page cannot see my stick", which is the exact
complaint this part of the page exists to answer. The check is there so nobody
later "improves" the default.

## The collector was worse than the order describes

§4: move `OfferShortcuts` after the single-instance check so a launch that exits
does not rewrite the Desktop. Done — it now lives in `runUI`, after
`yieldToExistingInstance`.

**The second problem was not in the order.** `runUI`'s first act is to relaunch
itself so the bundled runtime is inherited from process creation, and the
relaunched child re-enters `main()` through the same branch. So `OfferShortcuts`
ran **twice on every ordinary double-click** — once in a process whose only job
was to spawn another. Moving it past both the relaunch and the instance check
fixes both: exactly one process offers, and it is the one that opens a window.

`main()` now passes the intent (`offerShortcuts`) instead of performing it —
"which mode may offer" stays where the modes are, "may this process act" goes
where that is known.

**`go vet` clean, `go build` clean.** **Not run, deliberately**: exercising it
writes a shortcut to the Desktop, which is both outside the repo (rule 6) and
the precise side effect under test. Verified by reading the call order, and I am
saying so rather than implying it was tested.

**Unrelated, reporting not fixing:** `ui.go` fails `gofmt` on a pre-existing
import-ordering issue (`sync` out of place) that predates my change. Seven other
files in `citizen-collector/` are also unformatted. Left alone — it is not this
order's business and would muddy the diff.

## Gates

```
_verify_slots.js     21/21   (+3 for the 128-button default)
_verify_conflict.js   7/7    mutant fails 2
_verify_poll.js      13/13   mutant fails 4
_verify_navkeys.js   10/10   old behaviour fails 4
roundtrip.js         ALL CHECKS PASSED
mutate.js            22/23   (M18, the documented survivor)
build + deploy guard clean
```

`_verify_navkeys.js` is registered as a build gate alongside the other three.

## Still outstanding from the master order

- **Fonts** — blocked above, needs one word from Sleven.
- **§4 holo fleet dataset (167 ships)** — not started. §1 and §2 of the holo
  work were finished at 17:22; the fleet swap is the remaining piece, with the
  `unit`-over-`pos_model` reasoning already worked out and recorded.
- **§8 commit / push / deploy** — everything above is sitting in the working
  tree.
