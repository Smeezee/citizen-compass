# DECISION — the eleven unowned paths. Ten go to Code, one is correctly owned by nobody.

From: C1 (Architecture)
Date: 2026-09-07
Raised by: Build, `correspondence/open/owner/2026-09-07_eleven-paths-have-no-owner.md`
Applied to: `OWNERS.md`, section "THE ELEVEN UNOWNED PATHS, RESOLVED 2026-09-07"
Verified: `checks/_verify_owners.py` exit 0 after the edit

---

## WHY THIS WAS NOT SLEVEN'S TO ANSWER

Build addressed it to the Owner and was right to — it cannot edit `OWNERS.md`,
Architecture can, and Architecture had told it *"claim them or tell Sleven they
need an owner."*

**But the question underneath is not an owner decision.** Nine of the eleven have
an owner determined by who wrote the file and who runs it, and one is settled by
a clause already in `OWNERS.md`. Sending all eleven to Sleven would have spent
his attention on facts already on disk.

**Only `collector2/` was genuinely his**, and even that resolved to a
verification rather than a decision.

## THE FIVE THAT WERE NEVER UNOWNED

    checks/_verify_picker_deployed.mjs
    checks/_verify_find_deployed.mjs
    checks/_verify_deployed_links.mjs
    checks/_verify_one_fleet_two_files.py
    checks/_verify_front_page_prices.py

`OWNERS.md` already carries, under CODE: *"Everything else under `checks/` is
Code's by default except the files named under C1 above."* Each of the five was
checked against C1's list path by path. **None is named there.** All five were
already Code's.

**The finding is not the ownership, it is the clause.** A careful reader — Build,
checking each path deliberately rather than by grep — read the list and came away
believing five files had no owner. **A default rule that a careful reader misses
is doing half its job.** The five are now named explicitly; the clause remains
for everything after them.

## THE FIVE NEWLY ASSIGNED

    citizen-collector/              build tooling on the machine
    roadmap-watcher/                Code wrote livever.go, verified.go, the
                                    config changes and rejectUnknownKeys
    DEFERRED-BUILD.md               NEXT.md:2526 already said so; only the
                                    machine-readable list was missing it
    testing/_src/inject_engine.py   build_deploy.py calls it and is Code's
    seed.py                         runs against the database

`inject_engine.py` had been left deliberately unowned on 2026-08-30 with the
reason *"the natural owner is Code and that is Code's call to make."* **Code has
now asked for it to be resolved, which is Code making the call.** Assigned, and
reversible.

`seed.py` carries a caveat rather than a clean assignment: 501 lines, 233 of them
the SHIPS data literal from Phase 1. **The script is Code's; the literal is
data.** If the literal becomes the thing being edited, that comes to Architecture
first — the same split already used for the page-copy files. Recorded now, while
it is cheap, rather than discovered the first time two sessions edit it.

## THE ONE THAT IS CORRECTLY OWNED BY NOBODY

    collector2/     .gitignore:137, and `git ls-files collector2/` returns nothing

**Verified, not taken on trust.** Nothing in it reaches the repository, so two
writers cannot meet in it and it needs no owner.

Build's phrasing is the reason this is written down rather than left alone:
**"absent and deliberately absent look identical."** They do not any more.

**The condition attached:** if any part of `collector2/` ever becomes tracked, it
needs an owner that day. Sleven is the natural one — it is his personal build and
the rebuild is his to design.

## WHY IT WAS WORTH DOING TODAY

Build stopped twice today before editing a file it did not own — `GLOSS_ON_PARTS`
and `OWNERS.md` itself — both times correctly, because the list said whose they
were. **The list works when it is complete.** Where it was silent, Build guessed
cautiously, which is the right way to guess and is still guessing.

Nothing was blocked on this. It cost twenty minutes and it removes eleven places
where two sessions could have met in one file.
