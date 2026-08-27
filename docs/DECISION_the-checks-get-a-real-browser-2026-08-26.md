# DECISION — the checks get a real browser

**2026-08-26 · Sleven's ruling · answers question 1 of
`docs/ORDER_the-camera-never-looked-at-the-ship-2026-08-26.md`**

---

## The ruling

**Option 1 is approved.** Playwright and a headless Chromium go on the build
machine, and the check suite gets a control that loads the real built page in a
real browser.

Option 2 — hand-modelling three.js behaviour into the stub camera — is **not**
taken. It stays on the record as rejected, not as a fallback to reach for
later, because the reason it was rejected does not expire: a test harness that
re-implements the engine can only ever be as correct as whoever wrote it that
day, and this outage is what that looks like when it is wrong.

## Why, in one line

Every viewer control passed for three days while every ship page on the site
was blank. Nothing in `checks/` renders. That is the hole, and only a real
browser closes it.

## Scope — what this authorises

- Installing `playwright` and its Chromium into the repo, under `checks/`.
- Adding real-browser controls to the sweep, starting with the camera-framing
  one specified as F3 in the order above.

## Scope — what it does NOT authorise

- No new runtime dependency on the **site**. This is test-only. Nothing
  Playwright touches is ever served to a visitor, and `_deploy/` never contains
  it, exactly like `testing/_src/package.json` already works today.
- No deploying the live site.
- No running the browser against anything but our own pages, local or the
  testing worker. It is not a scraper.

## Who does the install

**Code**, as part of F3, on the machine that builds the site. Sleven does not
need to run the install by hand; he has the steps in case Code is blocked.

## The standing rule this creates

**A control that cannot see what a visitor sees is not a control over what a
visitor sees.** From here, any claim about how a page LOOKS — the hull is
solid, the labels are placed, the ship is in frame, the colour is right —
must come from a real browser. Claims about arithmetic, data joins, file
contents and build output may keep using the stub harnesses, which are fast and
correct for that.
