# PROMPT FOR CODE — Sleven's go-ahead: stage, commit, push, and deploy the test site. citizen-compass only.

    from    C1, 2026-08-09
    for     Code
    basis   Sleven, verbatim: "have code push everything... finish any of the things that
              are done and can go live... let's push. I would like to do some testing.
              I'd like to test the keybinding stuff. I would like to test the 3D viewer."
    scope   citizen-compass / testing/_src only. citizen-collector is untouched by this —
              that directory's own work (the browser-socket selftest) is independent and
              goes through inbox/ under the new ruling; nothing here changes that.

    This is the explicit go-ahead this project has required all along: "nothing commits or
    pushes without Sleven's go-ahead." He just gave it, for exactly this batch of work —
    order 1 (exporter), 2A pass 1 (wiring + stick identity), 2A pass 2 (action browser),
    2B (holo viewer). All four are built, guard-clean, and browser-verified per your own
    handoffs. Nothing else is authorized by this go-ahead — see §3.

---

## 1. Stage precisely what these four orders touched. Not `git add -A`.

The standing caution in `CURRENT-STATE.md` still applies: ~50 tracked files show CRLF/LF
churn unrelated to any of this. Confirmed via `git status` just now — the working tree
has a long list of modified files outside `testing/` and outside today's `.py` generators
(`alembic/`, `app/`, `checks/`, `data-layer/derived/...`, etc.). **None of that goes in.**

What I can see from here, cross-check against your own knowledge of what you built and
correct if anything's missing or shouldn't be here:

    modified:
      testing/_src/_layer.src.html
      testing/_src/build_deploy.py
      testing/_src/check_deploy_clean.py
      testing/_src/device_engine.js
      testing/_src/kb_modes.gen.js
      testing/_src/keybinds.src.html
      testing/_src/sc_export.js
      build_keybind_modes.py

    deleted:
      testing/_src/test_sc_export.js

    new:
      testing/_src/fixtures/           (real_export.xml, real_export2.xml)
      testing/_src/holo.src.html
      testing/_src/holo_data.gen.js
      testing/_src/kb_actions.gen.js
      testing/_src/mutate.js
      testing/_src/package.json
      testing/_src/package-lock.json
      testing/_src/patch_device_identity.py
      testing/_src/roundtrip.js
      build_holo_data.py
      build_kb_actions.py

**Two files I couldn't classify — decide and say which way you went:**
`testing/_src/_modelfolders.txt` and `testing/_src/_scunpacked_names.json` show as
untracked. If they're artifacts of this work, stage them; if they're stale scratch files
unrelated to today, leave them out and note that you did.

`place_hardpoints.py` (repo root, untracked) predates today's four orders — it's the
2026-08-08/09 hardpoint-derivation script 2B depends on but didn't create. Your call
whether it belongs in this commit or a separate one; either is defensible, just say which.

## 2. Build once more, clean, right before committing

`python testing/_src/build_deploy.py` — confirm it still completes with the deploy guard
passing on a fresh checkout state, not just against whatever's sitting in `_deploy/` from
earlier today. Cheap, and it's exactly the kind of thing that's caught real bugs today
already (the injection-ordering defect).

## 3. Commit, scoped, one message describing all four orders

No `git add -A`. Stage exactly the list from §1 (as corrected). One commit is fine — these
four orders landed together and describe one coherent change (the keybind builder going
from verify-only to a working import/export/browse/3D-viewer tool). Message should say
what changed and, briefly, what's still known-incomplete (fonts, 2-of-4 model coverage) so
the commit message itself does't overclaim — same discipline as the handoffs.

**Do not include citizen-collector/ in this commit.** Separate directory, separate
lifecycle, not part of this go-ahead.

## 4. Push to `origin/main`

Standard push, no force. This is the first push since `ba25d9c` (2026-08-07) — confirm
the local branch is actually tracking and up to date with `origin/main` before pushing,
in case anything landed upstream in the meantime (unlikely, but check rather than assume).

## 5. Deploy the test site

```
powershell -ExecutionPolicy Bypass -File .\scripts\deploy_testing.ps1
```

Only after the push succeeds. This is the step this project has a documented history of
silently failing in a specific way — `wrangler pages deploy` publishing to a second URL
while reporting success, "seen five times" per `CURRENT-STATE.md`. The deploy script
exists specifically to avoid that; use it, not a raw `wrangler` invocation.

**Verify the deploy actually landed, don't just trust exit 0.** The password gate only
covers HTML, so you can check static assets are live without needing it — fetch
`sc_export.js`, `kb_actions.gen.js`, `holo_data.gen.js`, and one model
(`models/Sabre.glb`) from the live testing URL and confirm they respond and roughly match
the local `_deploy/` byte sizes. That's a real check the deploy published the right
content, not just that the command exited cleanly.

## 6. What NOT to do — this go-ahead is scoped

- **Do not fetch or add the font files.** Still an open licensing decision, still Sleven's
  alone. The page works correctly with the fallback stack right now; that's fine to ship
  as-is. (Separately, C1 may follow up on this directly — don't preempt it.)
- **Do not guess the Cutlass Black / Aquila model match.** `MANUAL_MATCHES` stays empty
  until Sleven confirms the BIS 2949 edition is airframe-identical. Ship with 2 of 4 ships
  displayable and the other two honestly labeled, exactly as already built.
- **Do not write the 35 missing section descriptions.** Still no source data; still
  correctly left empty.
- **Do not touch citizen-collector/.**

## 7. Report back

A handoff in the same shape as today's others: what got staged (final list), the commit
hash, confirmation the push landed on `origin/main`, and the live-asset verification from
§5 — concretely, not "deploy succeeded."

---

Sleven wants to test the keybind page and the 3D viewer as soon as this is live. Treat
that as the priority — get it shipped correctly, then report, rather than polishing
anything beyond what's already built.
