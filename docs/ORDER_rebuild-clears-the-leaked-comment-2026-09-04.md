# ORDER — rebuild and deploy testing. Two things ride on it.

From: C1 (Cowork), 2026-09-04
For: Code
Sleven has said go.

## RUN THESE

```
python testing/_src/build_deploy.py
```

```
powershell -ExecutionPolicy Bypass -File .\scripts\deploy_testing.ps1
```

Then tell Sleven the URL is live:
`https://citizencompasstesting.citizencompass-contact.workers.dev/_inspect.html`

---

## 1. A COMMENT LEAK IS ON THE TESTING SITE RIGHT NOW

Sleven sent a screenshot of the Anvil Carrack ship page with twelve lines of
internal notes rendered as visible text above the ship name.

`testing/_src/cc_glossary.inc.html` opened a comment on line 1 and on line 2 wrote
the marker it looks for IN FULL, terminator included. HTML comments do not nest,
and neither does `strip_comments.py`, which closes on the first terminator exactly
as a browser does. It removed line 1 and half of line 2 and left the rest — plus a
dangling terminator — as page content.

**`strip_comments.py` behaved correctly. The include was lying to it. Do not
"fix" the stripper.**

Still leaking until you rebuild:

    testing/_deploy/index.html:1282
    testing/_deploy/loadout.html:888

### New control: `checks/_verify_no_leaked_comments.py` (C1)
Walks every page source AND every deployed page the way a browser does. Fails on a
nested `<!--`, an orphan `-->`, or an unterminated comment. Masks `<script>` and
`<style>` bodies first, because comment rules do not apply in there.

**Rule 12 evidence — and the reason it was rewritten once.** The first version
looked only for the nested opener. It passed the broken deployed page, because by
then the stripper had already removed the opener and what shipped was an ORPHAN
TERMINATOR — a different shape. A control that only knows how a defect looks in the
SOURCE is not a control on what visitors get.

    broken source (preserved copy)   2 defects   would have caught it
    deployed loadout.html            1 defect    catches what is live now
    fixed source                     0
    find.html (clean page)           0           no false positive

**It exits 1 today on purpose** and goes green on your rebuild. If it is still red
afterwards the build is reintroducing the defect — tell me, do not suppress it.

---

## 2. THE SHIP INSPECTOR NEEDS TO BE SERVED

Sleven wants to walk all 258 hulls and mark the broken ones, and he asked for a URL
rather than a command to run. It cannot be a local file: a page opened from disk
cannot fetch 258 `.glb` beside it, and the Linux VM a Cowork session gets cannot
host anything his browser can reach. The testing site already serves `models/`, so
that is where it belongs.

`testing/_src/_inspect.src.html` (C1, 1.17 MB) — 258 hulls one at a time, orbit and
zoom, Next / Prev, mark-as-broken with reason chips, a Solid vs See-through toggle,
progress that survives a reload, and a Report button that prints the list. Carries
its own three.js, GLTFLoader, DRACOLoader and Draco decoder inline, the same way
`loadout.html` does, so it shares no code with the site and cannot be broken by it.
Loads models from `models/` relatively.

Tested end to end in a real browser: first load, next/prev, jump to ship 201,
mark-broken, reason chips, side toggle, report output. Zero page errors.

### The one change this needed, and it is in YOUR area
`testing/_src/deploy_pages.py` — **one line added to PAGES**:

    ('_inspect.src.html', '_inspect.html'),

placed beside `stick-test.src.html`, which is the existing precedent for a
copied-verbatim page that shares no code with the site.

**Without it your deploy REFUSES.** Proven by removing the line and re-running the
guard:

    DEPLOY REFUSED - unexpected file would be PUBLISHED: _inspect.html

With it: `deploy guard: _deploy contains only known assets - safe to deploy`.

`deploy_pages.py` has no owner in `OWNERS.md`. C1 did not claim it — the edit is
declared in a new GAPS section there and you may reverse it. Same for
`check_deploy_clean.py` and `strip_comments.py`, neither of which C1 touched.

It is an internal tool on a password-gated host, on purpose. Deleting that one line
stops it being served and nothing else depends on it.
