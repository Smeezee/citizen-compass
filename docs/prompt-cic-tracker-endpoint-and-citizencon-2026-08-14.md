# BRIEF FOR CIC — two jobs. One is five minutes and unblocks an automated watcher. The other is the last transcript surface worth reading.

    from      C3 (Cowork), 2026-08-14
    for       CIC
    follows   your Constellation sweep, which closed that question three ways.
              Nothing here revisits it.

---

## JOB 1 — find the address the Progress Tracker fetches its data from

**Five minutes, and it decides whether a tripwire can be automated or not.**

We want the watcher to notice if a "Constellation" card ever appears on the
Progress Tracker. The watcher is a Go program that downloads pages — and the
Progress Tracker arrives nearly empty and is filled in by JavaScript, so a plain
download sees a blank shell. You proved that page is readable **with a browser**;
the question is whether it is readable **without one**.

It has to fetch its data from somewhere. Find where.

**What to do:** open `robertsspaceindustries.com/roadmap/progress-tracker/deliverables`
with the network panel recording. Reload. Look at what the page requests.

**What to report:**

    the request URL(s) that carry the deliverables data
    the method — GET or POST
    if POST, the request body (roadmap tools are often GraphQL, so this matters)
    the response format, and a small sample of the JSON shape
    any headers that look required — auth token, CSRF, referer, cookie
    whether the same request works in a fresh tab with no session

**That last one is the deciding question.** If it needs a logged-in session or a
CSRF token, a headless watcher is much harder and we should know now rather than
after somebody builds it.

**Finding it commits us to nothing.** Do NOT set anything up to poll it, and do
not hammer it — one page load is the whole job. **Whether we may call an
undocumented endpoint on a schedule is Sleven's decision, not ours** (rule 8, and
this project already has an open RSI permissions question that is his to clear).
Report the address; he decides whether it gets used.

**If the request turns out to need auth or is otherwise not reachable without a
browser, say so plainly.** That is a genuinely useful answer — it tells us the
tripwire needs a browsing session and is not free, which changes how it gets
scoped.

---

## JOB 2 — CitizenCon ship panels, for the four names only

You asked whether to keep going on transcripts. **Not for the Constellation** —
you closed that, and a fourth negative adds nothing.

**But CitizenCon ship panels are worth reading for a different reason:** they are
where CIG shows **unannounced silhouettes** — ships with no name attached yet.
That is the one remaining public surface where an unrevealed 2027+ ship could
appear, and it is the only place the four unresolved names could still be hiding.

    Drake Marauder    Origin M60    RSI Skylark    GATAC Hyun

**Read: CitizenCon 2955 and 2956 ship panels and keynotes.** Search the captions
for those four names, and — more usefully — for **unnamed or teased ships**:
silhouette reveals, "we're not saying what this is yet", concept art with no
name, manufacturer teases without a ship name.

**What matters is not whether the names appear.** It is: **how many unrevealed
ships has CIG shown without naming, and from which manufacturers?** If CIG has
silhouettes out for ships nobody can name, that is the honest home for these four
— and it is a real finding either way.

Two things already established that bound this, so you do not redo them:

- CIG's 2026 manufacturer list, from the ship-talk episode you already read, had
  Anvil, Kruger and Greycat slots still unfilled as of your check
- Drake has exactly **one** announced-but-unreleased ship (Kraken Privateer,
  2019) and Origin has **zero** — so neither name maps onto a known backlog item

---

## Standing rules, unchanged

No leak aggregators, as sources or as leads. Player posts on Spectrum are not
official even though they sit on CIG's domain. Attribute every claim to a URL
with its tier. **"I looked and there is nothing" remains a full answer** — you
have already demonstrated that better than most positives would have.

## What I checked and what I did not

**Checked:** that CIG publishes no documented public API for the roadmap or
progress tracker — searched for one and read the wiki's Roadmap page, which
describes the tool and its history and says nothing about programmatic access.
The roadmap was built by Turbulent.

**Did NOT check:** the endpoint itself. WebFetch cannot see it — the page returns
metadata only, and a POST-based API is out of reach for the tools I have. **That
is precisely why this is yours.** I am not guessing at the URL; I would rather you
read the real one than confirm a shape I invented.
