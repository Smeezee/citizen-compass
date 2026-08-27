# ORDER — catching up to 4.10

**2026-08-26 · C1 · for Code · Sleven approved both: extract ourselves, and
build the diff**

---

## The good news first: our 4.9 baseline is exact, and it is provable

I went looking for a risk and found the opposite. The worry was that snapshot
`20260801T204744Z` was acquired on **1 August**, one day after 4.10 went to
PTU, so it might be contaminated with PTU data while stamped 4.9.

**It is not.** Its own manifest records the upstream commit it was taken from:

    git_head_commit    4764726896973204a798325ed0f9ed7253e995e5
    git_head_subject   4.9.0-LIVE.12232306
    git_commit_date    2026-07-16T14:46:09+02:00

The content is the **4.9.0-LIVE.12232306** build, committed 16 July — two weeks
before 4.10 reached PTU. The August acquisition date is when we cloned it, not
when the data was made. `LAST_VERIFIED_PATCH = "4.9"` is correct.

**So the diff has a trustworthy left-hand side, named down to the build
number.** That is worth more than it sounds: a patch diff whose baseline is
"about 4.9, we think" is not evidence of anything.

**And it exposes a small defect.** The site says **4.9**. The manifest knows
**4.9.0-LIVE.12232306**. The stamp is coarser than the evidence we already
hold, and `LAST_VERIFIED_PATCH` is hand-typed in
`build_loadout_data.py:136` — a constant somebody has to remember to edit,
which on a five-year project is a defect and not a step.

---

## THE TARGET BUILD IS CONFIRMED — from Sleven's own launcher

    4.10.0-live.12519617

Read off the RSI launcher, LIVE channel, 2026-08-26. **This is the right-hand
side of the diff and the string to compare upstream against.**

So the pair is named end to end, before any work starts:

    from   4.9.0-LIVE.12232306     committed 2026-07-16, sealed as 20260801T204744Z
    to     4.10.0-live.12519617    live 2026-08-26

**Two things follow, and both are sequencing, not opinion.**

**The launcher was still downloading when this was captured** — "UPDATING…",
phase "Calculating required space". `Data.p4k` is being rewritten in place.
**C4 must not run until that finishes.** Reading a half-written archive does not
throw: the ZIP64 directory read would either fail cleanly or, worse, succeed
against stale bytes and produce a keybind set that looks like 4.10 and is not.
**Confirm the launcher shows the install idle at 4.10.0-live.12519617 before
touching the archive.**

**Case differs between the two build strings** — the launcher writes
`4.10.0-live`, the 4.9 upstream commit subject read `4.9.0-LIVE`. Compare
case-insensitively when matching upstream's head subject in C1. A case
difference is not a version mismatch, and treating it as one would report
"upstream has not published 4.10" about a repository that had.

---

## C1 — find out whether 4.10 data exists upstream

**One question, and the manifest already shows how to answer it:** the head
commit subject of `StarCitizenWiki/scunpacked-data` IS the game build. Today's
baseline came from a commit whose subject was `4.9.0-LIVE.12232306`.

So: read that repo's current head commit subject. If it reads `4.10.x-LIVE.…`,
the data is published and C2 is a re-clone. If it still reads 4.9, they have
not processed the patch yet and C3 applies.

**Report the subject string verbatim before starting anything else.** I could
not check it myself — GitHub's API refused my fetch and the branch listing is
disallowed by that host's robots.txt, and I did not work around either.

## C2 — if it is published: re-run the pipeline that already exists

The procedure is not written down but it is fully recorded in the manifest of
the last run, and it worked:

1. `git clone` the repo into `<run_id>.partial`, with git-lfs confirmed
   available **before** cloning (a clone without it silently substitutes a
   130-byte pointer for `items.json` and every filename looks right).
2. Capture git metadata **before** stripping `.git` — head commit, subject,
   dates. Reversing those two steps loses the provenance permanently.
3. The five gates, in order: files present, every JSON parses, file-type
   inspection, malware scan, content-indicator scan. Malware scan before the
   rename out of `.partial`, then re-hash to confirm the scanned bytes are the
   finalized bytes.
4. Rename out of `.partial` only when all five pass in order.

**C2b — make it a script, and make the stamp come from the data.**
`LAST_VERIFIED_PATCH` should be read from the manifest's `git_head_subject`,
not typed. A build that cannot state which game build it was made from should
fail rather than publish a guess.

## C3 — GO. Sleven approved extraction on 2026-08-26 and C1 confirmed the need

> **C3 IS APPROVED AND UNBLOCKED. It was approved before C1 even ran** - Sleven
> said yes to extracting ourselves the moment 4.10 went live. C1 has since
> confirmed upstream is still on 4.9, so the condition is met and there is
> nothing left to ask.
>
> **The ScDataDumper licence line below was C1 re-raising a CLOSED question and
> it is struck.** `docs/RULING_rights-questions-are-settled-2026-08-14.md` says
> rights questions are settled and are not to be re-raised "as a question, a
> caveat, or a flag". Raising it as a gate was wrong, and it stalled a job that
> had already been authorised. It is not a gate. Do not treat it as one.
>
> **Start now, and start with what we already own** - see C3a below.



**Sleven approved extracting ourselves, and the tool I proposed is not the one
to use.** I recommended `unp4k`. **This project already does better than
`unp4k` and has done since 2 August.**

`claude/workorder-keybind-extraction.md` §2 records a full extraction from
`Data.p4k` with **no third-party tool and nothing installed** — read the
ZIP64 central directory, find the entry, decompress the zstd frame with the
`zstd` already on the machine, decode the CryXmlB binary header. Four
self-checks on the table offsets confirm the layout parsed rather than
producing garbage that still parses. **About a minute, start to finish.**

That method is proven on ONE file. **Ships and items are a different job** —
they live in the DataForge `.dcb` blob, which is what ScDataDumper exists to
decode, and that is a real toolchain rather than a header read.

**C3a — START WITH THE METHOD THIS PROJECT ALREADY OWNS, and only escalate
if it genuinely cannot reach the data.**

The zero-install route already worked once, on this exact archive, and it needs
no third-party tool at all: read the ZIP64 central directory, locate the entry,
decompress the zstd frame with the `zstd` already on the machine, decode the
CryXmlB header, and assert the four table-offset identities so a wrong offset
fails loudly instead of yielding plausible garbage.

**Report what that reaches before proposing anything heavier.** Ship and item
records live in the DataForge `.dcb` blob rather than in loose CryXmlB files,
so the decode is a bigger job than `defaultProfile.xml` was - but this project
has decoded a CIG binary format from its header once already, and the honest
first step is to open the thing and say what is in it, not to assume a
dependency.

**If the `.dcb` genuinely defeats a direct read, say so with what you found and
propose the tool then.** That is an engineering report, not a permission
request.

## C4 — the keybinds are stale too, and we can fix that today with nothing

Separate from ships and items, and cheaper than both.

`defaultProfile.xml` was extracted from **4.9's** `Data.p4k` on 2 August. That
work order says in its own words: *"This must be re-run on every patch, because
default bindings change."* **It has not been re-run since.** His install is now
4.10.

No download, no new tool, no licence question, no upstream dependency — the
method is the zero-install one above and it is documented step by step. **Do
this one regardless of what C1 finds.**

---

## C5 — the diff report

**Approved by Sleven. This is the artifact nobody else publishes.**

Output as a real data-layer product, matching the pattern already used by
`location-gazetteer` and `mission-templates`:

    data-layer/derived/patch-diff/<from_build>__to__<to_build>/
        MANIFEST.json
        ships_added.json      ships_removed.json      ships_changed.json
        items_added.json      items_removed.json      items_changed.json
        summary.md

**Rules it must follow:**

- **Join on IDs, never names.** Standing rule, and this is exactly where a name
  join would quietly produce a fictional "changed" list.
- **Name both builds by their commit subject**, not by "4.9" and "4.10". The
  diff is between `4.9.0-LIVE.12232306` and whatever the new head says.
- **Distinguish "the game changed this" from "our old snapshot lacked the
  field."** A field appearing because upstream started emitting it is not a
  patch change, and reporting it as one poisons every number in the summary.
- **It reports. It never writes to the catalogue.** Auditor rule.

**C5b — the control, and it is the one that could actually fail.** Diff a
snapshot against ITSELF and assert the result is empty in every category. A
diff tool that reports spurious changes passes every other check you can write
against it; this is the check it cannot pass while broken. Mutation: perturb
one field in the copy and assert exactly one change is reported, in the right
file, on the right ID.

---

## Order of work

1. **C1** — one lookup, report the string.
2. **C4** — keybinds. Independent of everything, costs nothing, already stale.
3. **C2** or **C3** depending on C1 and Sleven's ruling.
4. **C5** once a second sealed snapshot exists.
5. **C2b** — the stamp reads itself. Small, and it stops this being a
   remembering problem forever.

**None of this blocks or is blocked by the viewer work.** V1 and V3 — the ship
facing away and the panel covering the hull — are still the fastest visible win
on the site and should ship first.

Do not deploy the live site. Testing only.

---

# AMENDMENT — C6, the diff proves itself on 4.9 before it meets 4.10

**2026-08-26 · approved by Sleven · raised by Code in the C1 report**

## Why this exists

C1 came back with upstream still on 4.9 — but a **newer** 4.9 than ours:

    our sealed baseline    4.9.0-LIVE.12232306    2026-07-16
    upstream head today    4.9.0-LIVE.12344265    2026-08-20

Code's observation, and it is a good one: a re-clone today is neither a no-op
nor 4.10. It moves the catalogue forward **within 4.9**, and it hands C5 a real
pair to run against — two builds with trustworthy names on both sides, genuine
content differences, and nothing riding on the result.

**A diff tool's first run should not be the one anybody depends on.** The
self-diff control in C5b proves it reports nothing when nothing changed. This
proves the other half: that it reports the right things when something did.

## C6 — the order

**C6a. Acquire `4.9.0-LIVE.12344265` as a new sealed snapshot**, by the
procedure in C2 — git-lfs confirmed present before cloning, git metadata
captured before `.git` is stripped, five gates in order, malware scan before
the rename out of `.partial`, re-hash after. Same discipline as the baseline,
no shortcuts because it is "only a dry run". A snapshot acquired loosely is not
a control, it is a second problem.

**C6b. Build C5 and run it on this pair.** Full spec stands: join on IDs never
names, name both sides by build string, separate "the game changed this" from
"our old snapshot lacked the field", report only and never write to the
catalogue.

**C6c. Both controls must run on this pair, not just the happy path.**

- the self-diff: `12344265` against `12344265`, every category empty
- the mutation: perturb one field in a copy, assert exactly one change is
  reported, in the right file, on the right ID

**C6d. Read the result before trusting it.** Five weeks between two 4.9 builds
should produce a small, boring diff — a handful of stat tweaks and maybe a
component or two. **If it reports hundreds of changes, or none at all, the tool
is wrong and not the data.** Say which of the two happened before drawing any
conclusion about the game.

**C6e. Do NOT promote the new snapshot to the catalogue yet.** It is acquired,
gated and diffed; the site keeps serving from `20260801T204744Z` and keeps
saying 4.9. Promoting a data refresh and proving a new tool in the same step
means a surprise on the site has two possible causes. **One change at a time.**

## What this does NOT decide

C3 is still gated on Sleven's two rulings — whether to extract 4.10 ourselves,
and the ScDataDumper licence question, which is his alone under Rule 8. **C6 is
not a substitute for either and does not move us onto 4.10.** It makes the tool
trustworthy so that when 4.10 data does arrive, from whichever route, the diff
is a measurement rather than a first attempt.

## Where it sits in the queue

After C4. Before V2 only if Code is blocked on something else — **V2 is
approved and is the bigger win for anyone actually looking at the site.**
