# Update — condition 8 can now fail, and it was proven by blinding it on purpose

Filed at the time in this file's archive name. **No spending. The wake was not
re-run.**

## WHAT WAS WRONG

`git status` cannot see a gitignored path, and `inbox/` — the one directory the
desk was told to write to — is gitignored. The first wake's condition-8 check
printed *"nothing changed"* and **could not have printed anything else.**

## WHAT IT DOES NOW

Two lists instead of one:

    WHAT CHANGED - TRACKED FILES (git)        git status + HEAD, as before
    WHAT CHANGED - IGNORED TREES              path, size and mtime for every file
                                              under inbox/, logs/, _to_delete/,
                                              _needs_review/, .claude/,
                                              _zip_archive/ - walked directly

**23,735 files manifested, in 8.4 seconds.**

**And it declares its own coverage every time** — Architecture's order that a
control walking a set must assert the set is COMPLETE. The output names what it
walked, what it pruned, and what it does not reach at all, with a reason on each.

## THE `_to_delete/` TRAP, WHICH I ONLY FOUND BY TIMING IT

`find _to_delete -type f | wc -l` said **2,095**. It is not 2,095. It holds

    _to_delete/mutate_holo/data-layer/external-sources/scunpacked-data/snapshots/...

a nested copy of the ~29,000-file snapshot tree, and the walk was still climbing
through **67,855 files at 25 seconds** when I cut it off. **The first dry run
after the fix hung and that is how it surfaced.**

So pruning is by **directory NAME at any depth**, not by path prefix — a prefix
list would have missed this one, because the copy is somewhere nobody would have
thought to name. And the walk has caps: **120,000 files or 45 seconds, and hitting
either marks the manifest INCOMPLETE and says so.** A truncated walk is never
allowed to look like a clean answer.

## PROVEN BY BLINDING IT, NOT BY READING IT

`--self-test` plants a file inside a walked tree and requires the detector to name
it — created, then modified, then gone. **It is moved to `_to_delete/`, never
deleted (rule 1), and that move is itself the third case.**

    normal      6 passed, 0 failed
    BLINDED     3 passed, 3 FAILED, exit 1
                "THIS CONTROL IS NOT TRUSTWORTHY"

The blinded run removes `_needs_review` from the walked list — **the same shape of
blindness the original had with `inbox/`** — and the self-test refuses to pass.

## AND THE SELF-TEST CAUGHT ITSELF DOING THE SAME THING

First time I blinded it, *"a file that GOES is seen as removed"* **still passed**.
It asserted `rel not in d`, which is trivially true when the tree is not walked at
all. **A check that cannot fail, inside the self-test written to catch checks that
cannot fail.** It now requires the file to have been PRESENT before and ABSENT
after, and it fails under blinding like the others.

**That is the whole reason for driving a control with bad input rather than
reading it.** I wrote that assertion believing it was one.

## ONE HONEST NARROWING, DECLARED

The watcher is live and writes to `logs/` continuously; its log grew mid-test and
failed the "nothing else changed" case for a reason unrelated to the detector.
**The SELF-TEST now ignores `logs/` for that one case, and only there.** The real
report excludes nothing — a desk that writes into `logs/` during a wake is still
named.

## WHERE CONDITION 8 STANDS

**Still NOT PERFORMED for the run that happened.** The control that would have
answered it did not exist at the time, and I am not converting a fixed control into
a retrospective pass for a run it never watched.

**It can be answered by the next wake, whenever you want one.** I have not re-run
it — that spends, and the go is yours.

## WHAT THE REPORT STILL CANNOT DO

**It cannot separate the desk's writes from the watcher's.** They run
concurrently. The report says so in its own output and points at
`logs/inbox_watcher.log` to tell them apart, rather than pretending.

Nothing committed.
