# Update — sweep green with the new control; nothing queued

**2026-09-04 · Code**

    117 ok, 0 failed, 3 skipped, 0 NOT RUN, in 1058s
    _verify_inspector_nose.mjs   exit 0   5.9s   7 assertions

The new control integrates and costs six seconds - it is discovered by glob, so
it needed no listing anywhere.

## One thing I checked rather than assumed

The receipt's payload fingerprint moved from `27f6d133fd5c78e0` to
`446a772a82a87699` and **I had not rebuilt.** That is the shape of a stale
deploy, so I went and looked rather than filing a green sweep and stopping.

`testing/_deploy` was rewritten at 21:12:46-52, inside the sweep's own tail -
`_verify_deploy_drift.py` rebuilding into `_deploy` and restoring, which is what
that control does by design.

**The site is current.** Served `_inspect.html` is byte-identical to the local
payload, and all three deployed-only controls pass, including the one whose whole
job is this question: *"the served ship page is byte-identical to the one just
built"*.

## State

- Deployed: `8bddb786`, testing only. Live untouched.
- Everything I was asked for today is done and verified from served bytes.
- **Nothing queued.** No new orders since 18:37; inbox drained.

## Open, and none of it mine to decide

- the `see-through-ships` exception list - which ships stay see-through
- whether the 241 thumbnails are CIG assets at all (deregistered pending it;
  Part 2 renders our own and retires the question)
- the `cig-holoviewer` label on the 19 Fleetyards imports - C1 says not
  established either
- the glossary marks 0 of its 31 terms, and the control that measures it reports
  without failing
- the 85X renders as two crossed ships, broken as delivered
- 12 models the site cannot reach; four of them have unique geometry

## What actually bit today, in one line, because it was the same thing three times

**A green result that had not looked at anything.**

    the stub camera that always faced its target      239 hulls dark, 4 days
    the mark guard whose register had been emptied     I argued with the control
                                                       for an hour; it was right
    my own new control measuring the previous ship     5 green assertions over
                                                       one hull measured 5 times

None of the three was caught by an exit code. Each was caught by a number that
was too tidy - 826x-897x on every hull, "all carry it" on images byte-identical
to their unmarked originals, and two different ships framing at exactly -16.47.
