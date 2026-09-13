# Update - B3 IS BUILT AND RENDERS. Sweep running. And a RULE 5 REPORT-ONLY list: 241 unreferenced images in _deploy.

## B3 - C1 authored it lean, I carried the pictures, it renders

She chose (b) - the generator - for the reason I gave for asking: my build quietly
undoing her output every time would have been two owners transforming one
artifact. `next.src.html` is 110,188 bytes and `_src/images/` holds 241 files
named by the SHA-256 of their own bytes.

**My side was one step**, in `build_deploy.py`, following how models and fonts
already live in `_deploy`:

    front page images: 241 in _deploy (241 copied this run, 0 already current)

`images` was already in `check_deploy_clean.py`'s `DEFAULT_ALLOWED_DIRS`, so **no
guard was widened.** Because the names ARE the content hash, a name that already
exists is the same picture - no stale file can hide under a matching name, and an
unchanged picture keeps its name so rebuilds do not churn the deploy.

    next.html   2,496,384 -> 120,898 bytes in _deploy

## The six lines C1 asked for, since she has no browser

Ran against the BUILT payload, not the prototype:

    253 cards render                     253
    every card is the same height        152px, 1 distinct
    every picture loads                  246 of 246
    manufacturer groups A-Z              18
    ships A-Z inside every manufacturer  ok
    no page errors                       0

**It renders. This is shippable.** Sweep running now; deploy after, if green.

## RULE 5 REPORT-ONLY - 241 unreferenced images. I have moved NOTHING.

`_deploy/images/` now holds **482** files: C1's 241, plus **241 human-named webps
that nothing references.**

Checked thoroughly before saying so - every file in the payload at any depth, plus
`static/`, `releases/` and `testing/_src/`:

    referenced by next.html            241  (all present, 0 missing)
    referenced anywhere in the payload 241
    referenced by _src / static / releases pages  241  (the same sha-named set)
    UNREFERENCED EVERYWHERE            241

They are leftovers from the earlier iteration that wrote named files straight into
`_deploy`. First eight:

        100i.webp
        125a.webp
        135c.webp
        300i.webp
        315p.webp
        325a.webp
        350r.webp
        400i.webp

    241 files, 3.96 MB

**Rule 5 says an operation touching more than ten files runs report-only first and
stops until Sleven has seen the list. This is that list and I have stopped.**

What I would do, on his word and not before: `mv` them to `_to_delete/` (rule 1 -
moved aside, never deleted). Two reasons beyond tidiness:

1. They are published today. The testing host is serving 2.3 MB of ship artwork
   that no page displays.
2. They are CIG-derived images we host and do not show. That is not a rule 8
   question about wording - it is just more published CIG content than the site
   has a reason for, and it is worth him deciding rather than me.

**Nothing about them blocks the deploy** - they were already being published
before today, so shipping now makes nothing worse.

## Still blocked, unchanged

B2 on Sleven's edition ruling. B1 behind B2. `build_frontpage_data.py` still
untracked and still needs his go-ahead to commit (rule 2).
