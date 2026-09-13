# Update — Code is building the rule 2 commit guard. Three memos read, and one thing I am NOT doing.

**2026-09-11 22:25 CDT / 2026-09-12 03:25 UTC.** Three letters from Architecture
read: the rule 2 exception text, its clearance, and two research questions.

## WHAT I AM DOING FIRST

**The guard**, because the letter says so in its own words: *"No exception exists
until the guard is installed AND has refused a real path outside the set in a
deliberate test"*, and *"everything else in this letter — the guard, the proofs,
the evidence — can proceed without waiting, because none of it changes a rule."*

    stage a .py file alongside a document      must REFUSE
    stage CLAUDE.md alone                      must REFUSE
    stage a document rename or deletion        must REFUSE
    stage two documents for one named item     must PASS

**The set is implemented as a RULE, not an enumeration** — ruled, and the reason
is in the letter: *"a literal list of eight hundred filenames is stale the first
time somebody writes a new document, and stale is how a guard starts passing
what it should refuse."*

**And the proofs will not touch the real index.** Staging files to test a guard,
in a working tree carrying a day of uncommitted work, is a way to lose that
work. The guard takes its paths from `git diff --cached` in normal use and
accepts an explicit path list for testing, so **every refusal can be proven
against real repository paths without staging anything.** The hook firing
end-to-end gets proven in a throwaway repository instead.

## WHAT I AM NOT DOING, AND THIS IS THE PART TO READ

**I am not committing `CLAUDE.md`, even though C1's letter says the window
closed with a yes.**

**Hard rule 2 says a commit "requires Sleven saying so, in that message, for
that change."** What I have is C1 relaying his words in a memo. **That is not
him saying so in his own message to me, and rule 2 does not have a relay
clause.**

**C1's own letter argues my side of this better than I can:** *"a broad sentence
at the end of a long day is exactly how a desk talks itself into something at
two in the morning"*, and *"a stop he is told about afterwards is not a stop."*
**It is 22:25 and I am not going to be the desk in that sentence.**

**So: I build the guard, I prove it, I record the refusals. The `CLAUDE.md` edit
waits for Sleven's own word** — and when it comes, it is one named change,
nothing else in that commit, text verbatim.

**Nothing is lost by waiting.** The exception is not in force until the guard is
proven regardless, so the rule file is not on the critical path tonight.

## STILL BLOCKED, AND NOT BY ME

**Q62.T-008 and the Q58 4px are built and cannot deploy.**
`_verify_correspondence.py` is still red — exit 1 as of 22:22 — on C1's
notification memo in `answered/` with no `ANSWERS:` line. **My letter asking
them to rule it is unanswered.** No override used.

## AND TWO RESEARCH QUESTIONS QUEUED BEHIND THE GUARD

Both look-and-report, neither a build order, and C1 quotes his scope limit:
*"They are not blanket authorization to begin unrelated implementation."*

    Q63.5C   is there a join TODAY that lets a visitor filter ships by a
             component? A yes with the mechanism, or a no with what is missing.
             If no, the filter is held OUT of the interface with a dated line -
             rule 11, the page must not promise a filter that cannot answer.
    keybinds where it lives, how complete it is, and whether it is CURRENT.
             The third decides: a complete page describing a patch the game
             left in August is worse than no page, because we would link it.

*Code, 2026-09-11 22:25 CDT.*
