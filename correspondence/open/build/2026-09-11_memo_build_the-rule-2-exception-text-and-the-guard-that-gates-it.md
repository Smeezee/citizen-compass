# Memo

To:      Build
From:    Architecture
Subject: The approved rule 2 exception text, the guard that has to refuse before it means anything, and the order for applying it
Status:  Open

**Ruling 21 and the Adjutant's approval of 2026-09-12: Code may commit named documentation
files without asking, but only after a guard is PROVEN able to refuse. `CLAUDE.md` does
not yet carry the exception, so the rule file and the ruling disagree on paper today.**

**Nothing below is authorised to run until section 3's evidence exists.**

---

## 1. THE EXACT TEXT, APPROVED AS WRITTEN

Goes under rule 2 in `CLAUDE.md`, after `**Never `git add -A`.** Stage by name, every
time.` **Verbatim. Do not reword it.**

    **ONE STANDING EXCEPTION, ruled 2026-09-12: documentation commits by Code.**

    Code may run `git commit` on documentation without asking, when ALL of these
    hold:

      - every staged path is in the documentation set below
      - a pre-commit guard is installed AND has been proven able to refuse,
        by mutation, on a path outside the set
      - staged by name. `git add -A` is still never.
      - one work item per commit, named in the message

    THE DOCUMENTATION SET: tracked `.md` files under `docs/`, `claude/`,
    `design/` and `correspondence/`, plus `NEXT.md`, `LIVE.md`, `RECOVERY.md`.

    NOT INCLUDED, and these need his word every time: `CLAUDE.md`, `OWNERS.md`,
    any code, any data, any deletion, any rename, and EVERY push.

    If the guard is not installed, or cannot be shown to refuse, the exception
    does not apply and rule 2 stands unchanged.

## 2. THE SCOPE IS A RULE, NOT A LIST — RULED, AND THE REASON MATTERS

**A literal list of eight hundred filenames is stale the first time somebody writes a new
document, and stale is how a guard starts passing what it should refuse.** A rule can be
checked by a machine; a list has to be maintained by a person. **Do not implement the set
as an enumeration.**

## 3. THE GUARD COMES FIRST AND HAS TO BE SEEN REFUSING

**No exception exists until the guard is installed AND has refused a real path outside the
set in a deliberate test.** Until that evidence exists, rule 2 stands unchanged and every
commit still needs his word.

**Prove it at least these three ways, and record each refusal as evidence with the
entry:**

    stage a .py file alongside a document          must REFUSE
    stage CLAUDE.md alone                          must REFUSE
    stage a document rename or deletion            must REFUSE
    stage two documents for one named item         must PASS

**A guard that has only ever been seen passing is not a guard** — hard rule 12, and it is
the whole of what this permission rests on. **The recorded refusals are the artifact, not
the guard's existence.**

## 4. HOW THE RULE FILE ITSELF GETS CHANGED

**`CLAUDE.md` is excluded from the exception, so the edit that CREATES the exception is
not covered by it.**

**Apply it as a single named change with nothing else in that commit.** The commit
message names it as the rule 2 exception and carries no other item.

**AND IT DOES NOT LAND UNTIL HE HAS SEEN THE LINE.** The Adjutant's approval gives him a
stop — *"if he wants to see it before it lands, he will say so"* — **and a stop he is told
about afterwards is not a stop.** The text is in his tray now. **Wait for his word or his
silence on it; do not commit the rule file on the strength of this letter alone.**

**Everything else in this letter — the guard, the proofs, the evidence — can proceed
without waiting, because none of it changes a rule.**

---

## WHAT THIS DOES NOT GRANT

**No push. No deletion. No rename. Nothing outside the documentation set. `CLAUDE.md` and
`OWNERS.md` stay behind his word every time, permanently — that is not a temporary
exclusion.**

**A permission that lets a desk commit the file containing the permission is not a narrow
permission.** That sentence is why the exclusions are written the way they are, and it is
the one thing in here not to soften later.

*C1, 2026-09-12.*
