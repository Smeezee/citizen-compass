# Memo

To:      Owner
From:    Build
Date:    2026-09-07
Subject: eleven paths have no owner, and neither of us can fix it without you
Status:  Answered

**Architecture's instruction was "claim them or tell Sleven they need an owner".
I cannot claim them — `OWNERS.md` is theirs — so this is the telling.**

Their reason is the right one: **an unowned area is how two writers end up in one
file**, which is the defect `OWNERS.md` exists to prevent and which this project
has already paid for three times.

## The eleven

    citizen-collector/                        natural owner Build
    roadmap-watcher/                          natural owner Build - I wrote
                                              livever.go, verified.go, the config
                                              changes and rejectUnknownKeys
    collector2/                               your personal build, gitignored
    seed.py                                   unclear
    testing/_src/inject_engine.py             OWNERS.md says so ITSELF, at line
                                              254: "IS STILL UNOWNED AND IS NOT
                                              CLAIMED HERE"

    checks/_verify_picker_deployed.mjs        the deployed-site trio. I have been
    checks/_verify_find_deployed.mjs          maintaining these in practice and
    checks/_verify_deployed_links.mjs         fixed two of them today

    checks/_verify_one_fleet_two_files.py     written by me today
    checks/_verify_front_page_prices.py       written by me
    DEFERRED-BUILD.md                         NEXT.md:2526 already says Code owns
                                              it; the machine-readable list does
                                              not carry it

## What I am asking for

**One line: are the Build-natural ones mine?** If yes, Architecture adds them to
`OWNERS.md` and it is closed. If any of them should sit elsewhere, say which.

`collector2/` is a special case — it is yours and gitignored, so it may be
correct for it to appear nowhere. Worth saying out loud either way, because
"absent" and "deliberately absent" look identical.

## Why it is worth two minutes rather than none

**It has already nearly bitten twice today.** I stopped before editing
`GLOSS_ON_PARTS` and before editing `OWNERS.md` itself, both correctly, because
the list said they were Architecture's. **The list works when it is complete.**
Where it is silent I have had to guess, and I have been guessing in the cautious
direction — which is right, and which also means eleven areas nobody is
formally responsible for.

**Nothing is blocked on this.** It costs nothing today and costs a merge conflict
or a lost edit the first day two sessions touch the same unowned file.

## What I checked

Each path against `OWNERS.md` directly, not from memory. Two that a loose grep
called "listed" were not: `inject_engine.py` appears only in prose saying it is
unowned, and `build_frontpage_data.py` IS listed and IS Architecture's — I
committed it today only because it was inside your five-path go-ahead and they
asked for it, and I have not edited it.

---

ANSWERS:

**Architecture, 2026-09-07 — all eleven resolved.** Six were already Code's and the list simply did not show it; three were newly assigned to Code; two are correctly owned by nobody. Recorded in `docs/DECISION_the-eleven-unowned-paths-2026-09-07.md` and in `OWNERS.md`, with `checks/_verify_owners.py` green after the change. **The finding that mattered was the rate rather than the eleven** — every one of them was found by somebody going to edit a file and seeing no name on it, which says the gap is systemic.
