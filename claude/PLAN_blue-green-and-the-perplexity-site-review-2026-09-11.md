# PLAN — blue-green deployment, and the Perplexity site review

**Filed 2026-09-11 by the Adjutant desk. Planning only. Nothing was changed on any site,
host, database or repository file.** Not committed: no Cowork desk can commit, which is
open in Architecture's record specification.

**His decisions that shape this plan, 2026-09-11:** Perplexity may be given the test
site's password. Run it blind first, cross-reference against what we already know, then
run it again for anything else. Planning and test documents get filed so what was tested
and what came back can be shown later.

---

# PART 1 — SHOULD CITIZEN COMPASS USE BLUE-GREEN DEPLOYMENT?

**Blue-green:** two complete copies of the site exist at once, visitors are switched from
the old one to the new one in a single step, and the old one stays ready so they can be
switched back.

## VERDICT

**Not now.** The part of blue-green that protects visitors already exists on both hosts
for free, because the site is static files. **The milestone that justifies real
blue-green is the first release where a visitor's request reaches a Citizen Compass
server or database while they are using the site.** Nothing does today.

## WHAT IS ACTUALLY RUNNING — FROM THE FILES, NOT FROM MEMOS

    public site    citizencompass.netlify.app. Netlify Drop, hand-uploaded, one HTML
                   file (releases/latest.html), v0.3.9.            LIVE.md
    testing site   Cloudflare Workers static assets, worker "citizencompasstesting",
                   `npx wrangler deploy` of testing/_deploy/.       testing/wrangler.toml,
                                                                    scripts/deploy_testing.ps1
    planned live   worker "citizencompass", same payload directory built with --live.
                   Never run; the worker did not exist on 2026-08-21.  wrangler.live.toml
    frontend       static HTML plus generated data files (*.gen.js). The pages read
                   files, not an API: "the page reads this file instead of calling an
                   API, because a page searching a dated snapshot needs a file and not
                   a server."                                        testing/_src/deploy_pages.py
    runtime calls  ONE, and it is not ours: the new front page fetches
                   open.er-api.com for the USD exchange rate.       testing/_deploy/next.html
    API            FastAPI exists (app/, Procfile: uvicorn app.main:app). No evidence
                   found that it is hosted or reachable by a visitor. Not proven
                   absent — no host configuration, and nothing in the pages calls it.
    database       PostgreSQL on Sleven's Windows machine, read at BUILD time only.
                   "The build is machine-bound and this is proven."  docs/CURRENT-STATE.md
                   Alembic migrations exist. Hard rule 3 bars destructive operations
                   outside the guarded test harness.                CLAUDE.md

## PROTECTION THAT ALREADY EXISTS

**Cloudflare Workers (the testing site, and the planned live site).**
- Every deploy is a version. Rollback "will immediately create a new deployment with the
  version specified", to any of the 100 most recent versions.
- Every version gets its own preview URL, and `wrangler versions upload` uploads a
  version without sending visitors to it. Preview URLs are public when enabled.
- Gradual deployments can split traffic between versions; static assets need version
  affinity or a visitor can get the page from one version and its files from another.
- Caveat in Cloudflare's own words: resources attached to the Worker "will not be
  changed during a rollback". Code rolls back; data does not.

**Netlify (the public site).**
- "Netlify versions all deploys", including Drop deploys, each at its own unique URL.
- Rollback is "Publish Deploy" on any earlier deploy, and "Rollbacks are instantaneous."

**The project's own gates.**
- A separate, password-gated testing site: a staging copy that visitors never see.
- The deploy scripts refuse a testing payload without the gate and stamp, and refuse a
  live payload with them, checked on the front-door page as well as index.html.
- The sweep gate refuses to upload anything the check suite has not passed, matched by
  payload fingerprint.
- `-WhatIf` dry runs, proven by behaviour rather than by the flag's own claim.
- Post-deploy verification from served bytes, not exit codes.

## WHAT BLUE-GREEN WOULD ADD

**For static files, almost nothing new.** Keeping the old version, switching at once and
switching back are all already there.

**One real gap, and it is small.** The live build is a rebuild with `--live`, so the
exact bytes that go public have never been looked at on a real URL before visitors get
them. **The cheap fix, when the live site moves to Cloudflare:** upload the `--live`
build as a version without deploying it, check it on its preview URL, then deploy that
same version. Same bytes checked, same bytes shipped, one-command rollback. That is
blue-green in substance with no new infrastructure. RECOMMENDATION, not ordered.

**Full blue-green with two running server stacks has nothing to protect today.** There
is no server.

## THE DATABASE RISKS, FOR WHEN A RUNTIME API ARRIVES

- **Shared database, two code versions.** During a switch, old and new code both use one
  schema. A migration that renames or drops something breaks the old version, and
  switching back cannot undo it. The code rolls back; the schema does not.
- **Separate databases.** Anything written during the switch lands on one side only, and
  the two copies disagree.
- **Data written after the switch.** Rolling back the code does not remove rows the new
  version wrote.
- **This project's rules make that stricter, not looser.** Destructive operations and
  `alembic downgrade` outside the guarded harness are barred, so any rollback has to be
  code-only. Every migration must therefore be additive first: add the new column, move
  the code over, remove the old column in a later release. That is usually called
  expand-and-contract.

## THE MILESTONE

**Blue-green becomes worth building at the first release where a visitor's request
reaches a Citizen Compass server or database.** Examples: FastAPI hosted publicly, or
visitor submissions stored in our own database.

**Not milestones:** moving the public site to Cloudflare, buying a domain, more traffic,
more pages. All of those stay static files.

**Worth adopting before the milestone, because it costs nothing now:** expand-and-
contract as the rule for every Alembic migration.

**One decision nearby.** The feedback feature Sleven wants back is JotForm, a third
party, which keeps the site static. A self-hosted feedback store would cross the
milestone. That is a design choice to make knowingly.

---

# PART 2 — THE PERPLEXITY SITE REVIEW

**SUPERSEDED IN PART, 2026-09-11 afternoon.** Echo reviewed the run design and Sleven held
it. The review now runs as five separate runs in a separate Comet profile, with no external
sites and a third label, UNVERIFIED. The answer key has been re-checked against the served,
rendered site. **Read `claude/ECHO_the-comet-plan-critique-and-the-refreshed-answer-key-2026-09-11.md`
before using anything below.** Blocked on the separate profile.

## WHAT IT IS FOR

A comparison of the public site and the updated testing site as a visitor meets them:
navigation problems, missing information, ship-page weaknesses, accessibility, broken
links, phone problems and visual inconsistency. **Rendered pages only. No repository.**

## STEP 0 — PROVE WHAT PERPLEXITY CAN SEE, BEFORE ANY REVIEW

**Why this comes first:** the new front page draws its 253 ship cards with JavaScript.
The raw file holds none of them. A tool that reads the file instead of the rendered page
will report the whole list missing, and every finding after that is noise.

**What Perplexity documents:** Comet Agent clicks buttons, fills forms and navigates;
Comet Assistant summarises and answers questions about open tabs. **Whether either sees
the rendered page, takes screenshots, or can emulate a phone width is not stated.** So it
is tested, not assumed:

    P1  enter the password and get past the gate on the testing site
    P2  report the ship count in the page header and name the first three
        maker headings in the list. A correct answer proves it sees the
        rendered page; the raw file contains neither.
    P3  open one ship card and report the ship page's heading
    P4  show the page at phone width, or say it cannot
    P5  produce a screenshot as evidence, or say it cannot

**UPDATE, same day: P1 is already met, by Sleven, not by the agent.** He set Comet as
his default browser on 2026-09-10, the sites are open in it, and he typed the password
himself. The page remembers the unlock in that browser, so the agent will see unlocked
pages. **That means P1 no longer tests the agent, and P2 is now the test that matters.**

**And one precaution, because of where it runs:** the agent is working inside Sleven's
everyday browser, where his other accounts are signed in. The run instructions tell it
to stay on the two Citizen Compass addresses and the external links it is checking, and
to take no action on any other site.

**P1 or P2 fails: stop.** The review cannot be trusted, and the fallback is Sleven
supplying screenshots, which is a decision for him then.
**P4 or P5 fails: the review can run,** but phone findings need screenshots from Sleven
and every finding's evidence has to be quoted text plus exact steps.

## SCOPE

    public site    https://citizencompass.netlify.app          its single page
    testing site   https://citizencompasstesting.citizencompass-contact.workers.dev
                   /          the new front page
                   /classic   the old front page, the closest match to the public site
                   /find
                   /keybinds
                   five ship pages, reached by clicking cards
    ship sample    the first card under five different category chips on the new
                   front page, chosen at run time so nobody hand-picks easy ones
    screen sizes   desktop about 1440 pixels wide; phone about 390 wide

**The same six tasks on both sites**, so the comparison is like for like:

    1  find a ship by name
    2  find where it can be bought in the game, and the price
    3  tell whether that price has been checked, and against which patch
    4  open that ship's details
    5  find how to report a problem or leave a note
    6  find the credits and the notice about CIG's material

## EVERY FINDING, IN THIS FORMAT

    ID           P-001 ...
    site, page   full URL
    screen       desktop or phone
    category     navigation / missing information / ship page / accessibility /
                 broken link / phone / visual inconsistency / first impression
    LABEL        CONFIRMED or OPINION
    severity     blocks the task / slows it / cosmetic
    evidence     for CONFIRMED: the steps to reproduce, plus the visible text
                 quoted exactly, a screenshot, or the link and what happened
                 when it was followed
                 for OPINION: what a first-time visitor would likely do, and why

**No evidence, no finding.** Broken links: the URL and what happened. Accessibility:
machine-checkable problems (contrast, unlabelled controls, keyboard focus) are
CONFIRMED; judgement about readability is OPINION.

## THE RUNS

**Run 1, blind.** No known-problem list. It reports what it sees.

**Cross-reference, filed.** Its findings matched against Code's front-page inventory
(`docs/FINDING_the-front-page-inventory-2026-09-11.md`) and the Q55 entries, in three
lists: found by both, found only by Perplexity, known and missed by Perplexity. **The
third list is the measure of how far its review can be trusted.**

**Run 2, briefed.** It is given the known list and asked only for what else it finds. It
must not restate a known item.

**Source code comes only after that,** one file per CONFIRMED finding that needs a
technical cause, under the curated export rules. Never for an OPINION.

## THE MINIMUM PERPLEXITY GETS

- The two addresses.
- The password, supplied by Sleven at run time. **It is not written in this document or
  any other file.** The lock is inside the page itself, not a login, so it is a courtesy
  lock and not a security boundary.
- One paragraph of purpose:

  > Citizen Compass is a free, non-commercial, fan-made reference for Star Citizen
  > players. Its job is to help a player find a ship, see where it can be bought in the
  > game and for how much, and judge how trustworthy that information is. Its tagline is
  > "Know where to buy, before you fly."

- The page list, screen sizes, six tasks and finding format above.

**Excluded completely:** the repository and all source code for runs 1 and 2,
correspondence, internal documents and findings, machine paths, account names, every
secret other than the page password, the Looking Project, and the known-problem list for
run 1.

## WHAT GETS FILED

Each run's product and date, the Step 0 results, Perplexity's findings verbatim, and the
cross-reference. Filed to disk and mirrored to the project, the same way as this plan.

## OPEN FOR SLEVEN

Nothing. **Product settled 2026-09-11: Comet**, already his default browser with both
sites open and unlocked.

---

## SOURCES

- [Cloudflare — Rollbacks](https://developers.cloudflare.com/workers/versions-and-deployments/rollbacks/)
- [Cloudflare — Preview URLs](https://developers.cloudflare.com/workers/versions-and-deployments/preview-urls/)
- [Cloudflare — Gradual rollouts with static assets](https://developers.cloudflare.com/workers/static-assets/routing/advanced/gradual-rollouts/)
- [Netlify — Manage deploys](https://docs.netlify.com/deploy/manage-deploys/manage-deploys-overview/)
- [Perplexity — Comet Assistant vs Comet Agent](https://www.perplexity.ai/comet/resources/articles/comet-assistant-vs-agent)
- Repository files named inline above, read 2026-09-11.
