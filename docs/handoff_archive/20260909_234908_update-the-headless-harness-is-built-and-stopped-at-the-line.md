# Update — the headless wake harness is built and stopped at the line. Asking for the word.

> **CORRECTED 2026-09-10 BY BUILD.** This entry said *"the freeze at eight"*.
> **The number is FOUR**, ruled in
> `2026-09-10_memo_ruling-four-and-it-freezes-the-other-two-are-superseded.md`,
> and the behaviour is FREEZE rather than forward. The substance of the
> paragraph is unaffected - the point was that none of the brakes were built
> and no unruled number was invented - but a dead figure left unmarked in an
> archive is how a future session quotes it back as current.
>
> **`docs/handoff_archive/_updates_log.md` still carries the original wording
> twice and was NOT edited.** That file is appended by the Go watcher, and a
> second writer on it is the exact failure this project has already paid for
> (rule 14). The correction lives here and in the update filed alongside it.

Filed at the time in this file's archive name.

**Built everything, got to the line, stopped. Nothing has been spent.**

## THE THREE PIECES

    claude/PROMPT_boot-a-new-c5.md     the C5 charter as a boot prompt
    correspondence/open/audit/          the throwaway letter, filed by the watcher
      2026-09-10_memo_headless-test-letter-count-the-check-suite.md
    scripts/wake_desk.py                the launcher and the evidence capture

## THE BOOT PROMPT DID NOT EXIST, AND I WROTE IT RATHER THAN ASKING

The spec says *"Its boot prompt already exists at `claude/PROMPT_boot-a-new-c5.md`."*
**It did not.** No file of that name and no C5 boot prompt under any other name was
anywhere in the repository — searched by name and by content.

**Rule 26 says research it rather than hand it back**, so I did: C5's charter is in
`docs/CURRENT-STATE.md` under "Session roles", and the boot prompt is composed from
that text. **The file says so at the top, in bold, so nobody later mistakes it for
something that pre-existed**, and the one section that is not from the charter is
marked as mine.

**This is worth knowing beyond this job:** if the other desks' boot prompts are
believed to exist on the same basis, that belief is worth checking before anything
depends on it.

## HOW RULE 9 IS ENFORCED — BY REMOVAL, NOT BY ASKING

    --restricted              removes Bash, PowerShell, REPL, the other
                              code-running tools and WebFetch. A desk with no
                              shell cannot deploy, commit, push or spend.
                              It also IGNORES user, project and local settings -
                              so the dead Stop hook cannot fire into this run.
    --permission-prompts none nobody is present, so anything that would prompt is
                              DENIED automatically instead of hanging. Fail closed.
    --disallowedTools         Bash, PowerShell, WebFetch, NotebookEdit, Task,
                              Agent - named as well, so the deny is visible in the
                              command a reader can see rather than only implied.

`Task`/`Agent` are denied deliberately: one desk was woken, not a swarm.

**The charter is read by the launcher and passed as text.** `--append-system-prompt`
is the documented flag in CLI 2.1.266; a `-file` variant appears only inside the
`--bare` help text and **I was not going to rely on it unverified.** Reading it in
the launcher also means an empty or missing charter fails where the message can be
seen, not inside a session nobody is watching.

## THE DRY RUN IS PROVEN FROM OUTSIDE, NOT BY READING IT

Hard rule 12: a safety flag that can be lost on the way to the code it guards
reports a safety it does not provide.

    working tree before and after      IDENTICAL (hash compared)
    logs/wake_log.jsonl                NOT created - nothing was launched
    the exact command                  printed in full for inspection

**One thing I could not use as evidence, and am saying so rather than dressing it
up:** a running-process count proves nothing here, because this session is itself
`claude`. The unchanged tree and the absent wake log are the evidence.

The desk list is derived, not typed - `correspondence/open/` gave **6 trays:
architecture, audit, build, design, owner, research**. Zero trays or an unreadable
directory refuses rather than falling back to a typed list.

## WHAT IS DELIBERATELY NOT IN THIS SCRIPT

**The brakes.** Round counting, the freeze at ~~eight~~ **FOUR**, the daily ceiling, the
one-wake-per-desk lock, the wake log's stop-everything rule. **Those are decided
rules that Architecture is specifying and Build builds what it specifies** —
writing a second version here would put two designs on one mechanism, which is the
defect this project has already paid for three times.

**And the two numbers that have not been ruled are absent rather than guessed:** a
limit on a single wake, and how long a job may sit untouched. There is no
`--max-turns` for exactly that reason. **Eight rounds of a runaway is still a
runaway** and I am not inventing the number that stops it.

## THE EIGHT PASS CRITERIA, AND WHERE EACH IS CHECKED

    1  starts with nobody present      --permission-prompts none
    2  reads the letter in its tray    reported in its reply
    3  writes a reply into inbox/      the reply file itself
    4  the watcher files it to owner   logs/inbox_watcher.log
    5  the session exits on its own    exit code + wall clock
    6  real token counts               --output-format json usage block
    7  BOTH NUMBERS CORRECT            you re-count them
    8  NOTHING ELSE CHANGED            git status + HEAD, before and after,
                                       diffed and printed line by line

**Eight is the one I built most carefully.** HEAD is captured too, so a desk that
commits is caught rather than merely a desk that edits. Anything that moved is
printed and named. **It will not be tidied away.**

## THE ASK

    python scripts/wake_desk.py --desk audit

**That spends. The word is yours and I have not taken it.** One word and it runs.

## AND ONE THING I WILL ASK FOR SEPARATELY

The Stop hook. You said to ask when I next need it and you would answer the prompt.
**I will ask at the moment of doing it**, not now — this run does not need it, and
`--restricted` ignores that settings file anyway.

Nothing committed.
