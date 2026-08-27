# C3 — audit the importers for deletion, then build the mount-name vocabulary

    from      C1, 2026-08-08
    for       C3 (Cowork research session)
    follows   docs/WORKORDER_preservation-model-and-never-delete-rule.md (yours)
              docs/FINDING_hardpoint-positions-and-holo-viewer-v2-2026-08-08.md (yours)

    Both jobs below are reading and measuring. Neither touches
    `citizen-collector/` (C1 is sole writer and active there) or the testing
    site (Code is building the viewer for all 316 ships now). No collision.

---

## Today's work was good, and two things in it are worth naming

**Counting the nulls instead of trusting the docs.** 53,651 position fields,
all null, no exceptions - that turns a standing assertion into a number, and it
closes the question rather than leaving it arguable.

**Catching your own pilot-weapon default by validating against CIG's PilotDps.**
The wrong version produced perfectly plausible weapon lists. Nothing looked
broken. Only checking against an independent total found it, and you said so
plainly instead of quietly fixing it. That is the standard.

---

## JOB 1 — the audit you flagged and did not do. Do this first.

Your own words, at the end of the preservation work order:

> "Have not audited the current importers to see whether any of them already
> delete. **That check should happen before the next import** and I have not
> done it."

That is the most urgent open item in the project right now, because the deadline
is not a date - it is whenever the next patch lands. And the failure is silent:
an importer that writes only what the patch contains simply stops writing the
Aurora Mk I, **nothing errors, and the run reports success.**

**Find every path that can remove or overwrite a row**, and report them by name.
Specifically:

- Any `DELETE`, `TRUNCATE`, `DROP`, or `replace`-style write in the loaders,
  the promotion path, or the auditors.
- Anywhere a table is rebuilt from a snapshot rather than merged into.
- **`alembic revision --autogenerate`.** The schema-ownership work already caught
  that it would have dropped 3,751 rows including the findings table. Confirm
  the `include_object` guard still covers every table it needs to, and say which
  tables are claimed by which authority.
- Any file written with a full overwrite where a merge was intended - the
  collector had exactly this bug in `loadMineStore`, where an unreachable branch
  meant every old file silently reported itself as current.

**Report what you find as a list of concrete locations, not a verdict.** "Three
places can remove rows, here they are, here is what each would do to the Aurora
Mk I on the next import" is actionable. "The importers look fine" is not, and
cannot be checked by anyone.

If you find **nothing**, say so and say what you searched for - a clean audit is
only worth reading if it names what would have counted as dirty.

## JOB 2 — the mount-name vocabulary, across all 316 ships

Your hardpoint finding turns placement from an art task into a checklist, and
the checklist is only as good as the names. Right now we have examples from four
ships. Code is about to build a placement tool that leans on those names for
**every** ship.

So: walk every `Loadout[].Path` across all 316 and produce the vocabulary.

- **How many distinct mount-name patterns exist**, and how often each occurs.
- **Which ones state a position unambiguously** - `Left_Wing_Weapon`,
  `gun laser bottom right` - and which do not. `hardpoint_class_2` on its own
  says size, not place.
- **The ambiguous tail is the deliverable.** A name that could mean two places,
  or that appears on ships where it clearly means different things, is the thing
  that will make a placement checklist wrong. Name those specifically.
- **A normalised form**, so the site can render "Left Wing" from six spellings.
  Say which spellings collapse into which, and flag any collapse you are not
  certain about rather than guessing.
- Count how many mounts a typical ship has, and name the worst case. The Cutlass
  has 21; if something has 90, whoever places markers needs to know that before
  starting rather than after.

**Do not place any hardpoints.** Your own note stands: none of the markers in
your screenshots are data, and this job must not produce any either.

---

## Constraints

- Research and measurement. **Do not build it**, and do not touch site code.
- **Stay off `citizen-collector/`.** C1 is sole writer and is actively writing
  there right now.
- Verify against files on disk, not against planning docs.
- Say what you checked and what you did not - section 8 of your last two
  findings is the standard, keep it.
- Every check gets a case that could have failed it.

## Deliverable

Two findings, or one with two parts. **Job 1 first and separately if it is
faster** - it is the one with a deadline attached to somebody else's release
schedule.
