# ORDER — rebuild; the fix is in the source, the leak is still in the deploy

From: C1 (Cowork), 2026-09-04
For: Code

## What happened
Sleven sent a screenshot of the Anvil Carrack ship page on the testing site with
twelve lines of internal notes rendered as visible text, above the ship name.

`testing/_src/cc_glossary.inc.html` opened a comment on line 1 and on line 2 wrote
the marker it looks for IN FULL — the literal `CC_GLOSSARY` comment, angle brackets
and terminator included. HTML comments do not nest, and neither does
`strip_comments.py`, which closes on the first terminator exactly as a browser does.
So the stripper removed line 1 and half of line 2 and left the remaining twelve
lines, plus a dangling terminator, as page content.

`strip_comments.py` behaved correctly. The include was lying to it.

## What C1 changed
- `testing/_src/cc_glossary.inc.html` — the marker is now named in prose without its
  angle brackets, and the comment explains why. Previous file preserved at
  `_to_delete/cc_glossary.inc.html.pre_comment_fix_20260904T141327Z`.
- `checks/_verify_no_leaked_comments.py` — NEW control (see below).

Nothing else touched. Nothing committed, nothing pushed, nothing deployed.

## WHAT YOU NEED TO DO
Rebuild and redeploy testing. The source is fixed; the two DEPLOYED pages still
carry the leak and will until the build runs:

    testing/_deploy/index.html:1282
    testing/_deploy/loadout.html:888

Command, as usual:

```
python testing/_src/build_deploy.py
```

```
powershell -ExecutionPolicy Bypass -File .\scripts\deploy_testing.ps1
```

## The new control, and its rule-12 evidence
`checks/_verify_no_leaked_comments.py` walks every page source AND every deployed
page the way a browser does, and fails on three shapes: a nested `<!--` inside a
comment, an orphan `-->` with no comment open, and an unterminated comment. It masks
`<script>` and `<style>` bodies first, because comment rules do not apply in there.

**It was written against the first shape and passed the broken deployed page.** The
stripper had already removed the opener, so the artifact carried an ORPHAN
TERMINATOR, not a nested one — a different shape entirely. The check was rewritten
to catch that, and it is the shape that actually shipped. A control that only knows
how a defect looks in the source is not a control on what visitors get.

Measured, all four ways:

    broken source (the preserved copy)   2 defects  <- would have caught it
    deployed loadout.html                1 defect   <- catches what is live NOW
    fixed source                         0
    a clean page (find.html)             0          <- no false positive

**It exits 1 today, on purpose.** That is the deploy correctly refusing to call a
broken artifact clean. It goes green on your rebuild. If it is still red afterwards,
the build is reintroducing the defect and I want to know rather than have it
suppressed.

## Ownership gap
`testing/_src/cc_glossary.inc.html` and `testing/_src/strip_comments.py` are in
nobody's list in `OWNERS.md`. That is the fifth and sixth gap found the same way —
by going to change a file and finding no name on it. C1 claims the glossary include
(C1 moved it there on 2026-08-30). `strip_comments.py` is build tooling and the
natural owner is you; say so and I will write it in.
