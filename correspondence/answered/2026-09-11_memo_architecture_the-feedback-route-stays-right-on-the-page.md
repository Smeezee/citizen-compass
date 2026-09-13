# Memo

To:      Architecture
From:    Owner
Subject: The feedback route comes back, right on the page. That one is decided.
Status:  Closed

## MY WORDS

> "The feature for being able to leave comments or notes when it's broken. We had it
> through JotForm. That needs to get figured out, because that's missing. I want to
> have that permanently, or at least for a while, right on the page."

Those are my exact words. Everything below is how to carry them out.

## WHAT IS DECIDED

**Keep.** Of the Q55 keep-or-drop items, the feedback route is not a question any more.
It comes back on the new front page, and it sits **on the page**, not behind a link.

**Already a requirement, from the same round of feedback:** it clears after each note
so one person can send several without reloading.

## WHAT IS NOT DECIDED, AND IS YOURS TO BRING ME

**How.** JotForm again, embedded on the page, or something else. Bring me the
recommendation with its cost.

Two facts to weigh:

- The old route was a link out to JotForm and it got zero submissions, checked by me
  directly. Where it sits on the page matters as much as whether it exists.
- A third-party form keeps the site as plain files. Storing notes in our own database
  would be the first time a visitor's request reaches our own server, and
  `claude/PLAN_blue-green-and-the-perplexity-site-review-2026-09-11.md` names that as
  the point where deployment has to change. Choose it knowingly if you choose it.

Nothing gets built until I have seen the recommendation.

---

ANSWERS:

**Architecture, 2026-09-11. The recommendation, its cost, and one thing about your
evidence you should hear before you pick.**

---

## THE RECOMMENDATION IN ONE LINE

**A plain HTML form written into the page — no iframe, no third-party script — posting
to an address that is a single configuration value per deploy target.**

**Start with the testing site's own Worker as that address. Netlify Forms for the live
site when it is refreshed. Not our database, not yet.**

## WHY THE FORM ITSELF IS NOT THE QUESTION

**"Right on the page" and "JotForm" are close to incompatible, and that is the part
worth saying plainly.** JotForm on the page means an iframe: a third-party frame loading
on every visit, styled by somebody else, and a privacy surface on a site that currently
ships as plain files with no outside calls. **It would satisfy the words and not the
intent.**

**A plain `<form>` is about fifteen lines and it looks like the rest of the page.** The
visitor sees a box and a button where they are already standing. **That is what removes
the three decisions the old route asked for** — notice a link, accept leaving the site,
wait for somebody else's page to load.

**So the form is settled. Only its destination is a real choice.**

## THE THREE DESTINATIONS, WITH WHAT EACH COSTS

**1. THE TESTING SITE'S OWN WORKER — my recommendation for now.**
The testing site is *served by* a Cloudflare Worker. It is already our server for that
site, so accepting a POST there is not a new class of thing. **Cost: one route and a
store, small.**
**One constraint that is not negotiable and I am naming it before anybody trips over
it:** the collector's Worker and R2 bucket are under a standing rule — no public bucket,
no list, read or delete route. **Feedback does not go in that bucket and does not add
routes to that Worker.** It gets its own, or this option is off.

**2. NETLIFY FORMS — my recommendation for the live site, later.**
The live site is static on Netlify. Netlify Forms is a `netlify` attribute on a plain
form tag; their build parses the HTML at deploy and handles the rest. **No server, no
JavaScript, no third party beyond the host we already use.** For a static site this is
as close to free as the problem gets.
**Two cautions, both real.** Detection happens at DEPLOY time, and the live site goes up
by manual Netlify Drop — **I have not proved that a Drop deploy runs form detection, and
a form that silently does not register looks exactly like a form that works.** And the
included submission allowance depends on which plan the account is on; **that is a
one-minute look in your own Netlify dashboard and I am not going to quote you a number I
have not seen on your account.**

**3. OUR OWN DATABASE — not now, and deliberately.**
This is the deployment change you named, and it should be chosen for its own reasons on
its own day, not arrive as a side effect of adding a comment box.

## WHY TWO ADDRESSES IS NOT TWO SYSTEMS

**The form markup is the same everywhere. The destination is one value, set where the
gate and the version stamp are already set per target.** The deploy scripts already
differ per site; this adds one line to each, not a second code path.

**The alternative — one address for both — means the public live site posting to a
Worker we run.** That is cleaner on paper and it is the deployment change again, wearing
a smaller hat.

## WHAT MUST HAPPEN WHATEVER YOU PICK

**Submit one test note and confirm it arrived, before this is called done.** Not the
form rendering, not a 200 — **the note, read back from wherever it lands.** Every option
above can fail silently and look perfect while doing it.

---

## AND ONE THING ABOUT THE ZERO, BECAUSE YOU ARE USING IT AS EVIDENCE

**You concluded from zero submissions that placement is the problem. I think you are
right, and the zero is not what makes you right.**

**The site is password-gated and its visitors are a handful of people you invited.** A
population that small produces zero submissions whether the form is buried behind a link
or sitting in the middle of the page in red. **The zero is consistent with your reading
and it is equally consistent with nobody having had anything to report.** It is not
evidence either way.

**What makes your reading right is the shape of the old route** — a link out, to a
third-party page, on a site people are browsing rather than filling in forms. Three
decisions before a visitor types a word. **That argument stands on its own and does not
need the zero.**

**The consequence is the part that matters: you will not be able to tell whether the new
one works either.** Submissions will stay near zero on a gated site regardless. **So the
success test cannot be "we got notes."** It is the test-note proof above, and after
that, whether a note arrives the first time something actually breaks in front of
somebody.

**Nothing is built. Waiting on your pick.**

*C1, 2026-09-11.*

## QUESTIONS

1. Destination for now: the testing site's own Worker, or something else?
2. Do you want me to specify the Netlify Forms route for the live site now, or leave it
   until the live site is actually refreshed?

---

**Owner, 2026-09-11. Read. Closed.** Destination settled. Your second question, whether to specify Netlify Forms for the live site now, is moot: the live site is replaced whole rather than refreshed. Placement and wording went to research and came back; they are in their own letter.
