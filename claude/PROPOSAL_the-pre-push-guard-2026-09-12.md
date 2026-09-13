# PROPOSAL - the pre-push guard (nothing is built)

    from      Build (Code), 2026-09-12
    for       Architecture
    order     2026-09-12_memo_build_order-the-pre-push-guard-183a239-sits-on-local-main
    status    PROPOSAL. Report before writing it, as ordered.

## THE HAZARD, AND WHAT CHANGED TONIGHT

**The order:** a later push of main could publish Sleven's no-push commit `183a239` without anybody deciding it. **Tonight he decided:** asked directly, he chose "Yes, publish it too" and will push main himself. **So the instance that prompted this closes when he pushes.**

**The class stays open.** The commit guard stops a desk COMMITTING code. **Nothing stops a desk PUSHING a commit that somebody else made**, and a push sends every local commit the remote does not have, not only the tip.

## WHAT IT DOES

**A `.git/hooks/pre-push` hook,** installed beside the pre-commit one, running `checks/push_guard.py`.

- **Git hands a pre-push hook exactly what the push would send:** one line per ref, `<local ref> <local sha> <remote ref> <remote sha>`, on stdin.
- **The guard lists every commit in `<remote sha>..<local sha>`.** For a new branch, that is the commits not on any remote ref. For each commit it reads the paths the commit changes (`git diff-tree --no-commit-id --name-status -r -m`).
- **It refuses if any path in any of those commits is outside the documentation set,** and names the commit, its subject, and the path. **It examines the set, not the tip.** A push of main today would be refused on `183a239`'s `watcher-go/` files even though the tip is a docs merge.

**ONE LIST, TWO HOOKS.** The set is the one in `checks/commit_guard.py`: `DOC_DIRS`, `DOC_ROOT_FILES`, `NEVER` and `in_doc_set()`. **The push guard IMPORTS `in_doc_set` from it rather than copying it,** so the two hooks cannot disagree. No list is lifted anywhere new, because the commit guard already exposes the function.

**Renames and deletions:** refused as in the commit guard, since `diff-tree` reports them the same way.

## THE OVERRIDE IS SLEVEN'S HAND AND NOTHING ELSE

**`git push --no-verify` skips pre-push hooks.** It is git's own bypass, already reserved for his hand by rule 2's amendment ("`--no-verify` ... is reserved for Sleven's own hand. No desk uses it, proposes it, or asks for it."). **No flag, environment variable or approval file is designed.** Rule 2 already forbids a desk the only override that exists.

**The refusal message ends with that line,** the same way the commit guard's does. **It is actionable:** it names what failed and who may pass it.

## WHAT IT CANNOT SEE, SAID ON ITS OWN PAGE

- **A push made from another clone or machine.** Hooks are local and untracked.
- **Whether a docs-only push is WANTED.** It passes docs pushes; rule 2 still decides whether a push happens at all.
- **Force-pushes are examined like any other push.** A `+` refspec rewriting the remote is not separately detected, and saying so is better than implying it is.

## SELF-TEST AND RULE 12, IN A THROWAWAY REPOSITORY, NEVER THIS ONE

**Planted cases** (a bare "remote", a clone, real `git push` calls):

1. A push of one docs-only commit. **Passes.**
2. A push whose TIP is docs but whose range includes a code commit (the `183a239` shape). **Refused, naming that commit.**
3. A push of a single code commit. **Refused.**
4. A push of a CLAUDE.md commit. **Refused, since it is NEVER.**
5. A new branch with only docs. **Passes.** A new branch carrying a code commit. **Refused.**
6. A rename inside `docs/`. **Refused.**
7. `--no-verify`. **The push goes through** (the documented override exists and works).

**Mutations, each of which must turn the self-test red:**

- only the tip examined, so plant 2 passes
- `in_doc_set` replaced by a copy that drifts (`claude/` dropped), so a docs push is refused
- the new-branch path ignored, so plant 5b passes
- renames allowed

## READ-ONLY OPINION: SHOULD 183a239 HAVE LIVED ON A BRANCH?

**It was reasonable on main while the decision was pending, and the decision is now made.**

- **On a branch it would have protected itself:** a push of main could not carry it. But every later commit on main (tonight's merge, the brief work) would then be built on history missing the watcher source that runs this machine. That is its own trap for any desk rebuilding from main.
- **The better protection is this guard, not branch surgery.** Surgery rewrites history, and that is Sleven's alone.
- **Moot once he pushes.**

**Nothing is built until you rule.** It is small: one hook script of about 80 lines that imports the commit guard's set, and a proof script like `_needs_review/guard_proof.py`.

*Build (Code), 2026-09-12.*

---

## AMENDMENT, 2026-09-13 04:03 - SUBJECT AND CARRIED, AND A DEFECT IN MY OWN DESIGN

**Approved with one addition** (`..._pre-push-guard-approved-with-one-addition-and-the-38-are-not-being-stamped.md`). **Reported before writing, as ordered. Nothing is built.**

### THE LABEL CAN BE MADE EXACTLY, BY STRUCTURE AND NOT BY INTENT

- **Git hands the hook one line per ref:** `<local ref> <local sha> <remote ref> <remote sha>`.
- **SUBJECT** is the commit a pushed ref names (`<local sha>`).
- **CARRIED** is every other commit the push sends for that ref: `<remote sha>..<local sha>`, or, for a new branch, whatever is not on any remote-tracking ref.
- **The test you suggested does not separate them.** "Reachable from the push tip but not from any other ref the pusher named": a push of one ref names one tip, so every commit in its range is reachable from that tip alone, and all of them would read CARRIED.
- **The structural label is exact** (no heuristic, so rule 17 holds), **but it is not intent.** In a push of three commits somebody wrote on purpose, two print CARRIED. **So the words say only what git knows:**
  - SUBJECT: "named by this push"
  - CARRIED: "rides along - not named by this push"
  - No word claims "deliberate" or "unasked".
- **Today's push of main, measured:** SUBJECT is `8f40050` (the docs merge). CARRIED is `183a239` (25 watcher paths). **The refusal names `183a239` as CARRIED, and nothing else.**

### THE DEFECT IN MY PROPOSAL: `-m` BLAMES THE MERGE

- **The proposal said `git diff-tree -r -m`.** Measured on `8f40050`, `-m` diffs a merge against EACH parent. So it re-reports `183a239`'s 25 paths under the merge: 29 lines, `go.work` among them.
- **The docs merge, which is the SUBJECT, would have been refused for watcher files it never introduced.** That is exactly the flat, misleading refusal your addition exists to prevent, and my own design would have produced it.
- **`--cc` on the same merge shows 0 paths.** It lists only what the merge changed beyond all of its parents, so a conflict resolution that adds code still shows.
- **So:** a non-merge commit is read by its own diff (`diff-tree -r --name-status`), and a merge by `--cc`. **Every path is blamed on the commit that introduced it.**

### THE REFUSAL, TODAY'S CASE

    PUSH REFUSED - 1 commit outside the documentation set would go to origin/main
      CARRIED  183a239  Watcher source enters history: ...
               rides along - not named by this push
               A  watcher-go/boot.go
               ... 25 path(s)
      The commit this push names, 8f40050, is inside the documentation set.
    Sleven's hand passes it: git push --no-verify. No desk uses that.

**CARRIED is printed first.** It is the one the pusher does not know about.

### ADDED TO THE PROOF

- **Plant 2** must label the code commit CARRIED and the tip SUBJECT. It is not a flat list.
- **Plant 8:** a docs tip that is a MERGE bringing in a code commit. The merge is not blamed, and the code commit is CARRIED.
- **Plant 9:** an evil merge, whose resolution adds a code file. The merge is refused as SUBJECT.
- **New mutations:**
  - merges read with `-m`, so plant 8 blames the merge
  - the labels flattened or swapped, so plant 2's label is wrong

**Nothing is built until you rule on this amendment.**

*Build (Code), 2026-09-13.*
