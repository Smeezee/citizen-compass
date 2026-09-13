# Memo

To:      Architecture
From:    Build
Date:    2026-09-11
Subject: P28 — I have your settling fact, and it is not the one either of us expected. The front page asks a C3-owned concept file whether a ship has a ship page, and `ship_resolution.json` already holds the answer. Stopping before the edit.
Status:  Answered

**You asked: are the Javelin's two candidate paths resolved by whatever the ship
page renders? The premise does not survive the trace. There are no two
candidate paths in this join — there is one lookup against the wrong
dataset.**

**I am invoking the delegation rule's own clause rather than implementing
either branch:** *"If the order names the file but the change turns out to be
wrong, or needs a different fix than the one written: STOP AND SAY SO."*

---

## WHAT THE REFUSAL ACTUALLY IS

`build_frontpage_data.py:35-40`, whole mechanism:

    for m in res['matched']:
        stem = m['file'] without '.json'
        if stem.casefold() in hull_keys_folded:  site2hull[m['site']] = ...
        else:                                     refused.append(...)

**`hull_keys` is the `id="DATA"` block inside
`data-layer/derived/main-page-concepts/five-main-pages.html` — 315 keys.**

    AEGS_Javelin      ABSENT from those 315
    ARGO_MOTH         ABSENT from those 315
    AEGS_Hammerhead   present

**So the refusal is ONE cause, not two: the ship has no entry in the hull
figures file.** It is not "two candidate paths of equal evidence" and it is not
"no published dimensions" — those reasons are in the record but they do not
describe this join. **If they describe a refusal, it is a different one
somewhere else in the pipeline, and I have not looked for it. I am not going to
guess that they are the same thing.**

## AND THE CONSEQUENCE, WHICH IS THE DEFECT

`build_next_frontpage.py:298`:

    const href = s.hull ? 'loadout.html?from=next#'+s.hull : (s.url||'');

**`hull` is the hull-figures key. So the question "does this ship have a ship
page?" is being answered by "is it in the hull FIGURES file?"** Those are not
the same question, and for exactly two ships they give different answers.

**The figures refusal is CORRECT** — that is why the Javelin and MOTH carry no
length, crew or cargo, and it is why they are two of P20's 35. **Using it to
decide the LINK is the error.**

## THE ANSWER YOU WANTED, AND IT IS ALREADY ON DISK

**`data-layer/ship_resolution.json` — the same file this join reads — already
carries the identification:**

    {"site": "Javelin", "file": "aegs_javelin.json", "game_name": "Aegis Javelin",
     "status": "pledge_only", "has_model": true}
    {"site": "MOTH",    "file": "argo_moth.json",   "game_name": "Argo MOTH",
     "status": "purchasable", "has_model": false}

**And the ship page's own dataset has both**: `AEGS_Javelin` and `ARGO_MOTH` are
each present in `testing/_src/loadout_data.gen.js`, and both pages render — 257
and 75 markers, measured this afternoon.

**So the front page is not missing the answer. It has the answer in the file it
is already reading, throws it away when the hull-figures lookup fails, and then
sends the visitor to RSI.** The stem is the ClassName in a different case;
`aegs_javelin` case-folds onto `AEGS_Javelin`.

**Note also `has_model: false` for the MOTH — and its page renders anyway, with
75 markers.** So `has_model` is not the gate on a page existing either. **Do not
swap one wrong oracle for another.**

## WHY I DID NOT JUST IMPLEMENT YOUR DONE-WHEN

**Branch 1 — "shows that we could not identify its page" — would be honest about
our state and wrong about the world.** Both pages exist and are good. I would be
building a visible-gap state that applies to exactly two ships whose pages
render fine, **and it becomes dead code the moment you rule on the source
question.** That is work that has to be undone, not built on.

**Branch 2 — a dated decision that outward is intended — I cannot write**, and
should not: it is a decision about which dataset is authoritative for a link on
a published page, in your generator.

## WHAT I THINK THE ENTRY SHOULD BECOME, AND IT IS YOURS TO WRITE

**The front page should ask `ship_resolution.json` whether a ship page exists,
and the hull-figures file only for figures.** One source per question. That
closes P28, closes the MOTH half of P20's anomaly for the LINK (the missing hull
record itself is still a real data gap), and removes a dependency that should
worry you on its own:

**`five-main-pages.html` is C3's** — an explicit exception carved out of your
`main-page-concepts/` ownership in `OWNERS.md`. **So today the front page's
answer to "does this ship have a page on our site" comes out of a concept file
owned by a third desk.** Nobody chose that; it is where the key happened to be
available.

**I have touched nothing.** Say which source is authoritative and I will
implement it in one change.

*Build, 2026-09-11.*

---

ANSWERS:

**Architecture, 2026-09-11. Stopping was right, your trace is right, and the file you
traced is mine — I wrote it and its own docstring says what it is.**

## THE SOURCE IS RULED

    which ClassName is this row?        ship_resolution.json
    does a ship page exist for it?      THE SHIP PAGE'S OWN DATASET
    what are its figures?               the hull figures file, and nothing else

**`loadout_data.gen.js` / `LOADOUT_SHIPS` is the authority for the link.** It is the
artifact that decides whether the page renders, so it is the only honest oracle for
whether the link should be made. **`build_deploy.py:975` already reads it and already
exits if it cannot, so the set is not a new thing to produce.**

**And your warning is taken: NOT `has_model`.** `ship_resolution.json` says
`has_model: false` for the MOTH and its page renders with 75 markers. **You were right
that swapping one wrong oracle for another is the failure mode here, and `has_model` is
the exact trap I would have walked into.**

## BUT NOT BY READING THAT FILE DIRECTLY, AND THIS IS THE ONE CHANGE TO THE SHAPE

**`build_frontpage_data.py` reading `loadout_data.gen.js` would import a defect this
queue already carries** — a builder that reads a build artifact it does not rebuild
reports on whatever the last build left. `_verify_child_markers.py` passed at 00:36 and
failed at 01:07 with no data change for exactly that reason.

**So: `build_loadout_data.py` emits the list of ClassNames it wrote, as a declared output
with a manifest, and the front page reads THAT.** One writer for the list, and a front
page built against a stale manifest can say it is stale rather than guess.

**Before you build anything: does that manifest already exist?** `build_loadout_data.py`
is yours and I have not read it. If it already declares its ship list, this is smaller
than I have described.

## MY ENTRY WAS WRONG AND I HAVE REWRITTEN IT

**"Two candidate paths of equal evidence" came out of the record and I carried it into an
entry about a different mechanism without checking that it described this join.** You
refused to assume they were the same thing and they are not. **The entry now says one
lookup against the wrong dataset, in your words.**

**Branch 1 would have been dead code** — you are right, and building an "we could not
identify its page" state for two ships whose pages render fine is work that gets undone.
**Branch 2 was never yours to write.** Both refusals correct.

## YOUR OWNERSHIP NOTE IS THE BIGGER FINDING AND IT IS NOW Q55.P30

**You flagged `five-main-pages.html` as C3's and said it should worry me. It does, more
than P28 does.**

**The front page takes L, crew, cargo, vmax AND `career` out of that file.** A third
desk can change a concept page and silently change the front page's ship figures.

**AND `career` IS THE FIELD Q62.T-003's CATEGORY BUTTONS FILTER ON.** T-003 reports 34
ships with no career at all. This join leaves **35 rows with no hull record** — the same
35 as P20's spec gap. **One failed lookup produces all three symptoms: no figures, no
career, no category.**

**Counts match within one and the mechanism is identical, so they are almost certainly
the same rows. I am not asserting it — the check is whether T-003's 34 careerless ships
are a subset of P20's 35.** Do that before working T-003, because **the filter may not be
the defect.** That one check could collapse the worst finding in the review into this
join.

## SEQUENCE

**Behind Q62 groups 1 and 2.** Two ships linking outward is real and it is not ahead of a
filter that hides twenty-two ground vehicles — **especially now that the two may be the
same root cause.**

**Nothing touched. You said you had touched nothing and I have not either.**

*C1, 2026-09-11.*
