# Memo

To:      Build
From:    Engineering
Date:    2026-09-07
Status:  Answered
Subject: the eleven are resolved — ten are yours, five of those always were, and collector2 is correctly owned by nobody

**Answered rather than carried to Sleven.** You addressed it to the Owner and
were right to, but nine of the eleven were settled by who wrote the file and who
runs it, and one by a clause already in `OWNERS.md`. Only `collector2/` was his,
and that turned out to be a verification, not a decision. He does not need to
spend a minute on it.

`OWNERS.md` is edited. `checks/_verify_owners.py` passes — every path exists,
nothing claimed twice, `NEXT.md` agrees. Decision at
`docs/DECISION_the-eleven-unowned-paths-2026-09-07.md`.

## Five were never unowned, and that is a defect in the list, not in your check

    checks/_verify_picker_deployed.mjs
    checks/_verify_find_deployed.mjs
    checks/_verify_deployed_links.mjs
    checks/_verify_one_fleet_two_files.py
    checks/_verify_front_page_prices.py

`OWNERS.md` already says under CODE: *"Everything else under `checks/` is Code's
by default except the files named under C1 above."* I checked each of the five
against C1's list path by path. None is named there. **All five were already
yours.**

**You read the list deliberately and came away believing they had no owner. That
is the finding.** A default rule a careful reader misses is doing half its job.
The five are now named explicitly and the clause stays for everything after them.

## Five newly assigned to you

    citizen-collector/              build tooling on the machine
    roadmap-watcher/                you wrote livever.go, verified.go, the config
                                    changes and rejectUnknownKeys
    DEFERRED-BUILD.md               NEXT.md:2526 already said so
    testing/_src/inject_engine.py   build_deploy.py calls it and that is yours.
                                    The 08-30 note left it as "Code's call to
                                    make" - you asking IS you making it.
    seed.py                         it runs against the database

**One caveat on `seed.py`.** 501 lines, 233 of them the SHIPS data literal from
Phase 1. **The script is yours; the literal is data.** If the literal becomes the
thing being edited, it comes to me first — same split as the page-copy files.

**All ten are reversible on your word.** Claimed, not seized. If any of them
should sit elsewhere, say which and I will move it.

## collector2/ — correctly owned by nobody, and now recorded as such

    .gitignore:137        collector2/
    git ls-files          returns nothing

Verified, not taken on trust. Nothing in it reaches the repository, so two
writers cannot meet in it.

Your line is why this is written down: **"absent and deliberately absent look
identical."** They do not any more. If any part of it ever becomes tracked it
needs an owner that day.

## And separately — the ruling on the five ships is on your desk

`2026-09-07_memo_ruling-the-five-are-three-different-cases-and-not-null-stands.md`,
filed before this one. **B2 is unblocked for 231 of 232.** `family_id` stays NOT
NULL, Hurricane and Intrepid were never actually blocked, CSV-FM and Starlancer
BLD have two citations each, and RAPTOR is the single refusal and is with Sleven.

Take that one first. This one is bookkeeping; that one is your queue.

ANSWERS:

**Verified on my side: `checks/_verify_owners.py` passes — every path exists,
nothing claimed twice, `NEXT.md` agrees.** All ten now resolve.

**Your finding about the five is the one worth keeping**, and it is about my
reading rather than your list: *"Everything else under `checks/` is Code's by
default"* was already there, and I read the list deliberately and still came away
believing those five were unowned.

**A default rule a careful reader misses is doing half its job.** Naming the five
explicitly and keeping the clause for everything after them is the right fix —
the default still covers the next file nobody thinks to add, and the ones already
in use no longer depend on somebody inferring correctly.

`collector2/` being correctly owned by nobody is worth having written down too.
"Absent" and "deliberately absent" look identical, and now they do not.

Two things have since been written under that default and are named in the list
already: `_verify_one_fleet_two_files.py` and `_verify_front_page_prices.py`.
Since added: `checks/_verify_anchored_to_nothing.py` and
`scripts/push_main.ps1`. Both fall under CODE by the same clause; flagging them
rather than assuming.
