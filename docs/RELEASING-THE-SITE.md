# Releasing the site

    written  2026-08-21, I3 of
             docs/ORDER_the-public-site-needs-no-server-and-live-gets-a-deploy-script-2026-08-21.md
    for      anybody who is not the person who has been doing this by hand
    status   the live deploy path has NEVER BEEN RUN FOR REAL. See "Before the
             first live deploy" below - there is a thing only Sleven can do.

> **Why this document exists.** The live site was three weeks behind, and not
> because anything was broken. There was no button, and how to press it existed
> only in one person's head. That is the defect. A release procedure that lives
> in somebody's memory is a release procedure that stops when they are busy, and
> nobody else can tell whether it was followed.

---

## 1. There are two sites. Tell them apart before you touch either.

|                | **TESTING** | **LIVE** |
|---|---|---|
| URL | `citizencompasstesting.citizencompass-contact.workers.dev` | `citizencompass.citizencompass-contact.workers.dev` |
| Worker name | `citizencompasstesting` | `citizencompass` |
| Config | `testing/wrangler.toml` | `wrangler.live.toml` (repo root) |
| Command | `scripts/deploy_testing.ps1` | `scripts/deploy_live.ps1` |
| Password gate | **yes** — private preview | **no** — it is a public site |
| Version shown | `v0.4.0 testing <date>` | `v0.4.0` |
| Who it is for | Sleven, reviewing | everybody |

There is also **`citizencompass.netlify.app`**, which is where the live site
*is today*: hand-deployed on Netlify, frozen at **v0.3.9**. Nothing in this repo
can reach it, take it down, or update it. Sleven ruled on 2026-08-21 that the
live site moves to Cloudflare; until somebody retires the Netlify site by hand,
**both will be serving**, and that is the one thing this document cannot
automate away. See §7.

### How to tell which one you are looking at

Three ways, in order of how hard they are to get wrong:

1. **The URL.** `...testing.citizencompass-contact...` vs
   `citizencompass.citizencompass-contact...`. The worker name IS the
   subdomain.
2. **The password prompt.** Testing asks for one. Live must never ask.
3. **The version in the header.** Testing reads `v0.4.0 testing 2026-08-21`.
   Live reads `v0.4.0` with nothing after it.

> **The failure this is guarding against is not a crash.** A wrong worker name
> does not error - it creates a *second* site at a second URL and reports a
> completely successful deploy. This project has already done that once. Two
> URLs in circulation, both looking right, is how you end up unable to say
> which one anyone is actually using.

---

## 2. The two commands

Both are run from the repo root, and **both take `-WhatIf`. Use it first, every
time.**

```powershell
# publish the TESTING site
powershell -ExecutionPolicy Bypass -File .\scripts\deploy_testing.ps1 -WhatIf
powershell -ExecutionPolicy Bypass -File .\scripts\deploy_testing.ps1

# publish the LIVE site
powershell -ExecutionPolicy Bypass -File .\scripts\deploy_live.ps1 -WhatIf
powershell -ExecutionPolicy Bypass -File .\scripts\deploy_live.ps1
```

`-WhatIf` prints exactly what would be uploaded and where, and uploads nothing.
**Do not take its word for it.** Confirm from outside:

```bash
curl -s -o /dev/null -w '%{http_code}' https://citizencompass.citizencompass-contact.workers.dev/
```

A dry run that published nothing leaves that unchanged. Before the first real
live deploy it is `404`, because the worker does not exist.

---

## 3. Both sites are built from the same sources, by the same build

```powershell
# the TESTING payload - password gate, "testing <date>" stamp
python testing\_src\build_deploy.py

# the LIVE payload - neither
python testing\_src\build_deploy.py --live
```

Both write **`testing/_deploy`**. That is deliberate: what Sleven reviews on the
testing site has to be the same bytes that go live. Two build directories would
mean the thing reviewed and the thing shipped were never the same thing.

The consequence is that `_deploy` holds **one of the two payloads at a time**,
and which one depends on the last build. That is not left to memory:

- `deploy_live.ps1` **refuses** a payload carrying the password gate or the
  testing stamp.
- `deploy_testing.ps1` **refuses** a payload carrying neither.

Both check the *bytes about to be uploaded*, not which flag somebody thinks they
used. So a forgotten `--live` cannot reach the public site, and a remembered one
cannot leave the private preview open at the testing URL. The refusals are
exercised on every sweep by `checks/_verify_deploy_guards.py`.

**The build needs PostgreSQL.** It regenerates `find_data.gen.js` and
`hardpoint_data.gen.js` from the database and refuses to finish if it cannot.
That is on purpose: a build that skips its own data generation and still says
"safe to deploy" is a build that skips its own tests.

**The build also needs `node`**, for the behavioural gates it runs before
writing anything. Same reasoning.

---

## 4. What the deploy guard does, and why it will one day stop you

`testing/_src/check_deploy_clean.py` refuses to publish anything in `_deploy`
that is not on a declared list. **Whitelist, not blacklist**: a denylist would
have stopped the last surprise and silently permitted the next one.

It runs twice - once at the end of the build, and again inside each deploy
script immediately before upload. The second run is the one that matters,
because **a deploy does not require a build**. On 2026-08-06 a failed wrangler
run left a `.wrangler/` folder inside `_deploy`, and the next deploy published
`/.wrangler/cache/wrangler-account.json` to the internet. No build was involved,
so the build's copy of the guard never executed.

If it stops you, it will name the file. Then:

- if the file **does not belong**, move it out — `_to_delete/`, never `rm`
  (hard rule 1);
- if it **does belong**, add it to `PAGES` in `testing/_src/build_deploy.py`
  **and** to `DEFAULT_ALLOWED_FILES` in `check_deploy_clean.py`. Both. The build
  passes its own list in; the standalone guard keeps its own copy, and letting
  the two drift produces a standalone failure that flatly contradicts a clean
  build — worse than either alone.

It has already earned its keep: it refused `find_data.gen.js` the first time
that file appeared, which is exactly what it is for.

---

## 5. Releasing to live, start to finish

1. **Build the testing payload and deploy it.**
   ```powershell
   python testing\_src\build_deploy.py
   powershell -ExecutionPolicy Bypass -File .\scripts\deploy_testing.ps1 -WhatIf
   powershell -ExecutionPolicy Bypass -File .\scripts\deploy_testing.ps1
   ```
2. **Sleven reviews the testing site.** This is a ruling, not a courtesy
   (2026-08-21): nothing reaches live that he has not seen on testing.
3. **Tell him what is in it.** §6 of this document is the inventory of what a
   returning visitor would notice. Regenerate it if the release has moved on -
   approving a release you cannot describe is not approving anything.
4. **Rebuild as the live payload.**
   ```powershell
   python testing\_src\build_deploy.py --live
   ```
   Nothing changes except the gate and the stamp. If anything else changed
   between step 1 and here, you are shipping something he did not review.
5. **Dry run, and check it from outside.**
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\scripts\deploy_live.ps1 -WhatIf
   ```
   Read what it says it would publish: the worker name, the URL, the file count,
   the version. Then confirm nothing moved:
   ```bash
   curl -s -o /dev/null -w '%{http_code}' https://citizencompass.citizencompass-contact.workers.dev/
   ```
6. **Deploy.**
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\scripts\deploy_live.ps1
   ```
7. **Verify — exit code 0 is not proof it works.** §8.
8. **Rebuild the testing payload, so `_deploy` is left in its resting state.**
   ```powershell
   python testing\_src\build_deploy.py
   ```
   Not strictly required — `deploy_testing.ps1` would refuse a live payload
   anyway — but leaving `_deploy` as the live build means the next person hits a
   refusal instead of doing their work.

---

## 6. What changes when live flips

**Measured 2026-08-21 by fetching the live site and comparing it against the
built payload. If you are reading this much later, re-measure before quoting
any of it at anybody.**

### The short version

The live site is **one HTML page**. The payload is **a site**.

|  | **live now** (`citizencompass.netlify.app`) | **what would ship** (`testing/_deploy`) |
|---|---|---|
| Files served | 1 | **497** |
| Size | 205 KB | **350.8 MB** |
| Pages | `/` only | `/`, `/find`, `/keybinds`, `/loadout`, `/holo`, `/download`, `/stick-test` |
| 3D models | none | **235** `.glb`, 341.8 MB |
| Ship images | none | 241, 4.0 MB |
| Version | v0.3.9 | v0.4.0 |
| Needs a server | no | **no** — and that is new, see below |

### The base page has not changed at all

This is worth saying plainly, because it is the opposite of what "three weeks
behind" sounds like. `releases/latest.html` is **byte-identical to the page
being served live right now, except for the version string.** Two lines differ:
the `<title>` and the header. The ship matrix, all 254 ships, the 233 RSI links,
the text, the layout — identical.

Everything below is **added on top** of that page, or is a new page beside it.

### What a returning visitor would notice, in the order they would hit it

1. **Ship names in the matrix become clickable and open a detail panel.**
   Today a ship name is a link straight to its RSI page. After the flip it opens
   an in-page ship view, and **the RSI link is offered inside that view instead**.
   Anybody who has been clicking through to RSI will notice this immediately. It
   is the single most disruptive change in the release and it is not a bug.
2. **A 3D model viewer**, for the 235 hulls that have one. Ships that have one
   are marked with a `3D` badge in the matrix; ships that do not are not marked,
   and say so rather than showing an empty stage.
3. **A Loadout panel on the ship view**, listing that hull's real mounts —
   2,195 slots across 235 models, grouped by kind, with sizes and fitted items
   where the source states them. **New today (I1): this reads a generated file
   and no longer needs the API to be up.**
4. **A `FIND IT` tab**, floating on the page, opening `/find`: 7,932 items and
   commodities, 26,657 prices, 823 terminals, from two dated UEX snapshots.
   Every price row carries the snapshot it came from and UEX's own last-modified
   date. **This also needs no server.**
5. **A keybinds overlay** on the ship page, and a full `/keybinds` page behind
   it — a 691-action browser, an axis evidence table, and profile import/export.
6. **`/loadout`** — a component bench keyed on the game's class ids, knowing 316
   ships. 221 of the 254 ships in the matrix offer a link into it; the other 33
   correctly do not, because there is no bench data for them.
7. **`/holo`** — the hardpoint placement viewer.
8. **`/download`** — the public collector download page, which describes the
   SmartScreen warning before somebody meets it. Its two outbound links resolve
   (checked: the GitHub release redirects to `collector-v0.3.3` and returns 200).
9. **A HELP drawer** with the keybind troubleshooting walkthrough and the vendor
   support table.
10. **`/stick-test`** — a standalone gamepad diagnostic that shares no code with
    the rest of the site, deliberately.

### What is removed

Nothing. No page, no feature, and no data is taken away by this release.

### What is NOT in it

- **The password gate.** It is a testing-only thing and `deploy_live.ps1`
  refuses a payload carrying it.
- **The `testing <date>` stamp.** Same.
- **Any dependency on the API.** As of I1 the public site calls no server at
  all. `/find` and the hardpoint panel both read generated files. If Railway is
  down, nothing on the public site notices.

### The two things to tell Sleven before he approves

1. **Item 1 above.** Clicking a ship name stops going to RSI. If that is not
   wanted, it is a build change, not a deploy change, and it should be settled
   before the flip rather than after.
2. **350.8 MB and 497 files.** Cloudflare's limits are 20,000 files and 25 MiB
   per file, so both are comfortable — the largest single file is
   `Starfarer_Gemini.glb` at 5.22 MB. But this is the first time the public site
   has served anything but one HTML page.

---

## 7. Before the first live deploy — the thing only Sleven can do

**The live worker does not exist.**
`https://citizencompass.citizencompass-contact.workers.dev/` returns 404 as of
2026-08-21, checked rather than assumed. `scripts/deploy_live.ps1` has never
been run for real; it has only ever been dry-run.

Creating it is Sleven's, and so is the decision to publish. Two things follow:

1. **The first real `deploy_live.ps1` run creates the worker.** Cloudflare
   creates a worker on first deploy under that name. Do it with `-WhatIf` first
   and read every line of what it says it would publish.
2. **The Netlify site does not go away by itself.** After the Cloudflare live
   site is up and verified, `citizencompass.netlify.app` will still be serving
   v0.3.9, and there will be two public URLs for one project until somebody
   takes the Netlify one down by hand. That is a manual step, in the Netlify
   dashboard, and nothing in this repo can do it or check it.

**Also unresolved, deliberately:** there is no custom domain. Both sites are on
`*.workers.dev`. If `citizencompass.net` is ever bought, the apex belongs to the
live worker and the testing site belongs on `testing.<domain>`. Do not add a
route to either config before that decision is actually made.

---

## 8. After a live deploy — verify it, do not assume it

`wrangler` exiting 0 means the upload succeeded. It does not mean the site
works. Check all of these:

1. **The page serves.** Not a 404, not a Cloudflare placeholder.
2. **There is NO password prompt**, in a clean browser context (private window,
   no stored `ccGate`). A gate on the public site is the worst outcome this can
   have, and from the outside it looks like an outage rather than a mistake — so
   nobody will report it as one.
3. **The header says `v0.4.0` with nothing after it.** No `testing <date>`.
4. **A model serves.** `/models/Hammerhead.glb` returns 200 with a plausible
   byte count. A deploy that dropped the 235-model folder still loads and still
   looks completely right.
5. **`/find` fills, and the ship page's hardpoint panel fills.** Both read
   generated `.gen.js` files and neither needs a server. If either says it could
   not reach its data, a `.gen.js` did not ship.
6. **The other pages are there**: `/find`, `/keybinds`, `/loadout`, `/holo`,
   `/download`, `/stick-test`.
7. **The testing site is still there and still gated.** A deploy under the wrong
   name would have overwritten it, and it would still have reported success.

`checks/_verify_find_deployed.mjs` does the equivalent sweep against the testing
URL and is worth pointing at the live one once it exists.

---

## 9. Where things live

| What | Where |
|---|---|
| Page sources | `testing/_src/*.src.html` |
| The build | `testing/_src/build_deploy.py` |
| Built payload | `testing/_deploy/` (gitignored) |
| Deploy guard | `testing/_src/check_deploy_clean.py` |
| Deploy scripts | `scripts/deploy_testing.ps1`, `scripts/deploy_live.ps1` |
| Worker configs | `testing/wrangler.toml`, `wrangler.live.toml` |
| Generated data | `build_find_data.py`, `build_hardpoint_data.py`, `build_kb_actions.py` |
| The live page's source | `static/preview.html` -> `releases/latest.html` |
| Controls over all this | `checks/_verify_deploy_guards.py`, `checks/run_all_controls.py` |

**One writer per artifact** (hard rule 14). `testing/` is Claude Code's, and
nothing under it changes unless it arrived as an ordered edit. The `.gen.js`
files are written by their generators and by nothing else — do not hand-edit
one, the next build will overwrite it and the diff will look like a regression
nobody can explain.

---

## 10. If something goes wrong

- **A deploy script refuses.** Read the message; every refusal in both scripts
  names what it found and what to do. None of them is advisory.
- **A guard cannot run at all** (python missing, file moved). That is reported
  as *not checked* and refused. It is never reported as clean. Fix the cause;
  do not route around it.
- **The build refuses because the database is unreachable.** That is the
  intended behaviour. The alternative is shipping generated data nobody
  checked.
- **You deployed to the wrong URL.** Do not delete anything. Check both URLs,
  write down what each is serving, and tell Sleven. A second site at a second
  URL is recoverable; a panicked cleanup is how the record of what happened
  disappears.
