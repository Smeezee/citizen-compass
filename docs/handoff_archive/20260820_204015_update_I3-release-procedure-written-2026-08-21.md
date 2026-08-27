# UPDATE — I3 DONE: the release procedure is written down

    from  Code, 2026-08-21
    item  I3
    sha   05f6a0c

`docs/RELEASING-THE-SITE.md`. Ten sections, written for somebody who is not the
person who has been doing this by hand: the two sites and three ways to tell
them apart, which command publishes which, what the deploy guard does and what
to do when it stops you, the run-through end to end, what only you can do before
the first live deploy, and what to check afterwards.

Two things in it worth your eye:

- **After the Cloudflare live site is up there will be two public URLs** until
  somebody takes `citizencompass.netlify.app` down by hand. Nothing in this repo
  can do that or check it, so it is a numbered manual step.
- **No custom domain**, deliberately, on either site. If `citizencompass.net` is
  ever bought, the apex belongs to the live worker and testing goes on
  `testing.<domain>`. Your call, not made here.

Section 6 (what changes when live flips) is filled in by I5.

Next: I4, one source of truth for the version number.
