# Update — two guard letters closed, and the timezone stamp is held: `tzdata` is a real dependency and neither interpreter has it

Filed at the time in this file's archive name.

## CLOSED — two letters tonight's work discharged

    first-job-on-boot-the-two-halves-of-the-guard-disagree     ANSWERED
    amendment-the-guard-must-refuse-an-undeclared-key          ANSWERED

Both carry what proves them: the byte-identical rebuild, the six states run
against the built binary, and the red case that turned out to be a lying
instrument rather than an impossible state. **The tray is down to seven.**

## THE STAMP — ORDERED, MEASURED, AND NOT LANDED. HERE IS WHY.

`2026-09-10_memo_the-stamp-goes-local-...` asks for explicit `America/Chicago` at
`testing/_src/build_deploy.py:842`, with a loud refusal rather than any fallback,
and says: *"`zoneinfo` on Windows sometimes needs `tzdata` present — if that turns
out to be a real dependency, say so rather than working around it."*

**It is a real dependency, and it is missing everywhere that matters.**

    system python  3.11.3  C:\\Program Files (x86)\\Python311-32  ZoneInfoNotFoundError
    venv python    3.11.9                                        ZoneInfoNotFoundError
    zoneinfo.available_timezones()                               0 keys

**Zero.** Windows ships no IANA database at all, so `zoneinfo` has nothing to read
without the `tzdata` package, and neither interpreter has it.

**The one that matters is the SYSTEM python.** `scripts/deploy_testing.ps1` calls
bare `python` for `build_deploy.py` (lines 166, 205, 220) and only reaches
`venv\\Scripts\\python.exe` for `run_all_controls.py`. **So installing into the venv
alone would not fix the stamp, and would look like it had.**

### THE CODE IS WRITTEN AND ITS REFUSAL IS PROVEN

Run in isolation against the deploy's own interpreter, not landed:

    BUILD REFUSED: the testing stamp needs the America/Chicago time zone and
    this interpreter cannot resolve it (ZoneInfoNotFoundError: ...). Windows
    ships no IANA database, so zoneinfo needs the tzdata package present.
    Nothing was written. Falling back to UTC or to naive local time would stamp
    a wrong date with nothing saying so, which is the defect this refusal exists
    to prevent.

    exit 78

**The refusal branch works. The success branch is NOT PERFORMED** — it cannot be
exercised on this machine until the dependency exists, and reporting it as passing
would be exactly the silent success rule 12 is about.

### WHY IT IS NOT LANDED YET, WHICH IS THE ONE JUDGEMENT CALL HERE

**Landing it today would make every testing deploy refuse.** That is the ordered
behaviour working correctly, and it is still not a thing to do at midnight to a
deploy path that is currently fine. **The refusal is right; shipping the refusal
before the dependency is not.**

**What is needed is one install, and it is not mine to run:** `pip install tzdata`
into `C:\\Program Files (x86)\\Python311-32`. That is the system interpreter,
outside this repo, under **hard rule 6** — and a Program Files install will want
elevation, which is the other half of why it is being asked rather than done.

**Three ways out, and the choice is Sleven's:**

    1  install tzdata into the system python      one command, then this lands
                                                  and the success branch gets
                                                  proven the same night
    2  point the deploy at venv\\Scripts\\python    a bigger change than a stamp
                                                  line and not what was ordered
    3  vendor a tz file into the repo             no dependency, but a
                                                  third-party data file that
                                                  then needs its own upkeep

**I am not picking between them.** 1 is smallest and matches the order as written.

**Nothing about the UTC convention changes either way.** Stored, compared and
reconciled timestamps stay UTC. This is one rendered label read by one person, and
the comment explaining that goes in beside the line so the next session does not
"fix" it back — which the memo asked for and is the reason the original survived a
year.

## NEXT

The 42% control proposal, which is a memo and needs nothing installed. Then the
card mark.

Nothing committed.
