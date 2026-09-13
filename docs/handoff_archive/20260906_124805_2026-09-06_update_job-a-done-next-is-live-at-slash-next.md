# Update - JOB A IS DONE. `next.html` is live on testing at /next, verified byte for byte, and index.html is untouched.

    https://citizencompasstesting.citizencompass-contact.workers.dev/next

Behind the preview password like the rest. Version ID 65359fbe-4453-4197-93d3-a35a81eb529a.

## The sweep

    120 ok, 0 failed, 3 skipped, 0 NOT RUN, in 2238s
    receipt 2026-09-06T12:44:41   fingerprint e488b489c841d343   exit 0

`_verify_correspondence.py` green after C1's fix.
**`_verify_broken_checker_end_to_end.py` passed in the sweep this time** - second
confirmation that its earlier NOT RUN was my CPU contention and not a defect. I
ran nothing alongside this sweep.

No `-IgnoreSweep`. No rebuild before deploying: the payload was unchanged since
the 11:40 run, so the receipt applies to these exact bytes and the gate confirmed
it - *"120 control(s) green against this exact payload"*.

## Verified from SERVED BYTES

One file went up: `/next.html`, 524 already uploaded.

    /next                200, 2,496,384 bytes
    served sha256        115a6d2dece17571
    local  sha256        115a6d2dece17571     IDENTICAL

    cc-src-note          4   the source and takedown notice, in the served bytes
    not affiliated       1
    Cloud Imperium       9

    /  (the OLD front page)  fa0afd5e3eb095a8, byte-identical to local index.html
                             Job A changed nothing about the current front page.

## ONE THING I READ WRONG AND CHECKED RATHER THAN ASSUMED

`/next.html` returns **307**, and my first reading was that the password gate was
blocking it - which would have meant the page was unreachable and Job A had not
delivered the URL Sleven asked for.

It is not the gate. **The host strips `.html`:**

    /next.html      307 -> /next        /next   200
    /index.html     307 -> /            /       200
    /loadout.html   307 -> /loadout
    /holo.html      307 -> /holo

Every page behaves this way and always has. The correct URL is **`/next`**.
Worth writing down because "307" looked like a failure twice today and was
routing both times.

## Job A closed

    deploy_pages.py      ('next.src.html', 'next.html')
    build_deploy.py      _SHIP_CONTENT_PAGES += 'next.html'
    nothing else

    253 cards, one height (152px), 246 of 246 pictures, 18 manufacturer groups
    A-Z with ships A-Z inside each, no page errors, index.html untouched,
    trademark block and source/takedown notice both present.

**Nothing committed, nothing pushed** (rule 2). No `git add -A`.

## Job B, when it is queued

B0 is withdrawn by C1's erratum and is now two small things - commit her
untracked `build_frontpage_data.py`, and the missing `MANIFEST.json` in
`main-page-concepts/`. **Both are hers**, and the commit needs Sleven either way.

B1-B5 are unstarted and I have not touched them.
