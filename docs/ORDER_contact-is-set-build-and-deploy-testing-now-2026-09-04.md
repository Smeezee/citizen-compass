# ORDER — the takedown contact is set. Build and deploy TESTING now.

From: C1 (Cowork), 2026-09-04
For: Code

This supersedes the blocking half of
`ORDER_source-notice-is-on-build-and-deploy-testing-2026-09-04`. Everything else in
that order still stands — read it for what changed and what to verify.

## The block is cleared
Sleven supplied the address. `CC_TAKEDOWN_CONTACT` is now in `.env`.

    tagged assets : 499
    contact set   : True
    build would   : PROCEED

The address is `citizencompass.contact@gmail.com` and it is now recorded in
`docs/CURRENT-STATE.md` as well, because it had never been written down anywhere in
this repository — a session had to ask Sleven for it, and that must not happen twice.
It is not a secret; it is printed on every page that shows CIG content, by design.

## RUN

```
python testing/_src/build_deploy.py
```

```
powershell -ExecutionPolicy Bypass -File .\scripts\deploy_testing.ps1
```

## VERIFY AFTER, rather than assume
- `cc-src-note` present in `_inspect.html`, `loadout.html`, `index.html`, `holo.html`.
  Before this change it was **0 of 4**. If it is still 0, STOP and say so — that means
  a second condition nobody has found, and I would rather hear it than ship it.
- `node checks/_verify_hull_is_solid.mjs` green
- `python checks/_verify_no_leaked_comments.py` green
- `python testing/_src/check_deploy_clean.py` green

## Then tell Sleven
`https://citizencompasstesting.citizencompass-contact.workers.dev/_inspect.html`

**TESTING ONLY. Live is untouched.**
