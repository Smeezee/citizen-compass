# ORDER — finish the job H1 started, then give the LIVE site a deploy script it has never had. RUN CONTINUOUSLY.

    from    C1, 2026-08-21
    for     Code
    status  GO. No stop points. Run rules are §1 of
              docs/ORDER_shop-and-price-layer-RUN-CONTINUOUSLY-2026-08-19.md.
    ledger  APPEND to docs/LEDGER_shop-price-layer-2026-08-19.md.
    ruled   Sleven, 2026-08-21: move the live site to Cloudflare, and he reviews
              the testing site before anything reaches live.

    *** YOU DO NOT DEPLOY THE LIVE SITE IN THIS RUN. *** See I2. Building the
    script, proving its dry run, and stopping short of the real deploy is the
    deliverable. That is not a gate I inserted - the Worker does not exist yet
    and only Sleven can create it, and nothing ships without his say-so.

---

## 0. WHAT THIS IS ACTUALLY ABOUT

Two facts found by reading the repo, not by remembering it:

**One.** `testing/wrangler.toml` says in its own words: *"The live site
(citizencompass.netlify.app) is hand-deployed on Netlify and is NOT touched by
anything here."* **There is no `netlify.toml`, no live deploy script, and no live
config anywhere in the project.** The testing site deploys with one guarded
command. The live site is moved by hand. **That is why the public site is three
weeks behind - not because anything broke, but because there is no button.**

**Two.** `testing/_deploy/index.html` still makes exactly one call to a live
server: `CC_API + /api/v1/ships/models/<dir>/hardpoints`. **So the public site
still needs Railway for one feature, and Railway is down.** Its failure text is
already honest - *"The API did not answer, so nothing is shown rather than
something guessed"* - which is the right behaviour and is not the point. The
point is that the feature is dead in public for as long as that server is.

**H1 already solved this shape once.** Prices stopped needing a server and became
a 188 KB file. **2,195 hardpoint slots is smaller than that.** Finish the job and
the public site needs no server at all.

## 1. THE WORK

**I1. THE HARDPOINTS BECOME GENERATED DATA, exactly like the prices.**
Extend or mirror `build_find_data.py`. The site's copy is generated from
PostgreSQL at build time and ships as a `*.gen.js` file beside the others.
*Acceptance:* the number of slots in the file equals the number in the database.
Assert it, do not eyeball it.
*Control, and it is the one that matters:* **with the network blocked after first
load, the hardpoint panel still fills.** Same control that proved H2.
*Size:* report the gzipped number. If it lands wildly above H1's 188 KB, apply
H1's own lesson before shipping it - **a big miss means the shape changed**, and
last time the culprit was 5,566 incompressible UUIDs nothing used.
**Keep the API path as the fallback**, not the primary. If the file is missing the
page behaves exactly as it does today, including the honest failure text. Do not
delete that message.

**I2. `scripts/deploy_live.ps1` AND a live wrangler config.**
Mirror `scripts/deploy_testing.ps1` exactly - the same unknown-file guard, the
same dry-run-first, the same refusal to publish a file nobody declared. That
guard already earned its keep at H3 by refusing `find_data.gen.js`.
**THE LIVE WORKER MUST NOT BE THE TESTING WORKER.** `testing/wrangler.toml`
carries a warning from a previous mistake: a wrong `name` does not update the
existing site, it creates a SECOND one at a second URL. **Two URLs in circulation
is the failure this project already had once.** Different name, its own file, and
say in a comment which URL each one publishes to.
*Acceptance:* `-WhatIf` runs clean and reports what WOULD be published.
*Control:* **prove the dry run published nothing by fetching from outside** - the
way H3 did it, with a 404 from the served origin, not by trusting the flag.
**THEN STOP. Do not run it for real.** The Worker does not exist yet.

**I3. WRITE THE RELEASE PROCEDURE DOWN.** `docs/RELEASING-THE-SITE.md`.
**The root defect here is not that live is behind - it is that how to update it
exists only in somebody's head.** Two sites, which command publishes which, what
the guard does, what to check afterwards, and how to tell the two URLs apart.
Written so somebody who is not you can follow it.

**I4. ONE SOURCE OF TRUTH FOR THE VERSION NUMBER.**
`testing/_deploy/index.html` says v0.4.0 in its title and header;
`testing/_src/_layer.src.html` still says v0.3.9 in a comment. Today that is only
a stale comment. **The defect is that a version string is written in more than one
place at all** - this project has already shipped a release whose source said one
number and whose feed said another.
*Control:* change the version in the one place, rebuild, confirm every rendered
occurrence changed. A grep that finds the old number anywhere fails the check.

**I5. WHAT CHANGES WHEN LIVE FLIPS.** An inventory: what the live site serves now
against what `_deploy` holds. **Sleven is being asked to approve a release and he
should be told what is in it** - new pages, changed pages, removed things, and
anything a returning visitor would notice. Put it in the ledger and in a short
section of I3's document.

**I6. A 404 SWEEP OF THE DEPLOYED TESTING SITE.** Every internal link and every
asset the pages reference, fetched from the served origin. **Not from disk.**
Report anything that does not return 200. This is the last chance to find a dead
link before it is on the public site.
*Control:* include one URL known to be absent and confirm the sweep reports it. A
sweep that has never reported anything is not a sweep.

**I7. `_src` -> `_deploy` DRIFT.** Confirm `_deploy` is genuinely built from
`_src` and nothing was hand-edited into `_deploy` only. **Anything found there
would be silently destroyed by the next build**, and it would look like a
regression nobody could explain.

**I8. SWEEP.** Re-run every control in `checks/`.

## 2. WHAT MUST NOT HAPPEN

- **Do not deploy the live site.** I2.
- **Do not reuse the testing Worker's name.** I2. Two URLs, one project, again.
- **Do not delete the API fallback or its failure message.** I1.
- **Do not shard the hardpoint file.** Same reasoning as H1.
- **Do not touch the collector.** Out of scope.
- **Do not cut a release. Do not `git add -A`. Push at the end.**

## 3. REPORT

- The hardpoint file's gzipped size, and whether the panel fills with the network
  blocked.
- What `-WhatIf` says `deploy_live.ps1` would publish, and the 404 proving it
  published nothing.
- The I5 inventory - what a visitor would notice.
- Anything the I6 sweep found.
- Anything here you think is wrong. **I1's fallback is the part most worth
  arguing with**: keeping a dead API path as a fallback may be worse than removing
  it, and if you think so, say why with the failure you have in mind.
