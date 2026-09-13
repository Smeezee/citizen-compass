# Memo

To:      Owner
From:    Architecture
Subject: That plugin is the answer. Official, OpenAI's own, write-capable — her work comes back as GitHub issues and we build almost nothing. Developer mode stays off.

**Ruled on disk: `claude/RULING_the-echo-loop-runs-on-github-issues-2026-09-12.md`.
Nothing built, nothing connected, nothing turned on.**

## THE LOOP

    you say    "work the open briefs"
    Echo       reads them from the repo, works them, and FILES HER ANSWER AS A
               GITHUB ISSUE
    a poller   turns new issues into letters in inbox/
    the watcher files them to my tray
    me         read against the repository, rule, then do it or send to Code

**One sentence from you per round trip. No clipboard, no link, no download, no paste, no
tunnel, no token.**

## THREE THINGS I AM RULING, AND THE THIRD IS THE IMPORTANT ONE

**ISSUES, NEVER PULL REQUESTS.** An issue is a letter; a pull request is a change.
Design produces designs and recommendations and does not execute — that is the desk's
charter and it maps exactly onto those two artifacts. **She never gets a path that writes
code.**

**NO CUSTOM CONNECTOR, AND DEVELOPER MODE STAYS OFF.** The page you sent says it plainly:
*prefer official servers hosted by the service providers themselves*, and avoid custom
ones unless you know and trust the application. **The connector I was about to design was
exactly the unverified case that warns against.** The official GitHub plugin is better by
their own standard and costs no build. **Leave that switch off.**

**AND ONE SENTENCE ON THAT PAGE CHANGES MY OWN SAFETY DESIGN:** *"It is possible for
write actions to occur even if the MCP server has tagged the action as read only."*

**So the limit I wrote earlier — write only into the inbox, never overwrite, no delete —
was enforcement by labelling, and that page says labelling is not enforcement.** I am
withdrawing it as a safeguard. **The real boundary is the GitHub authorisation itself:
which repositories the plugin is installed on and what it may do there.**

## SO THE INSTALL SCREEN IS THE PART TO READ SLOWLY

**When you connect it, GitHub will ask which repositories and which permissions.** Pick
the fewest repositories it will accept. **If it can be held to issues without commit
rights, hold it there** — that is the whole safety margin, and it is set once, by you, on
that screen.

## THE RISK THAT ACTUALLY APPLIES, SAID ONCE

**Echo reads the open web, and prompt injection is the first risk OpenAI names** —
instructions hidden in something she reads, aimed at making her take a write she was not
asked for.

**That is exactly why her answer comes back as an issue.** A poisoned issue is a bad
letter in a tray that I read before anything happens. A poisoned commit is not.

**And their page says the connected app receives whatever ChatGPT supplies** — the
plugin's own notice mentions chats and memories. **So nothing about rights, credentials
or the Fan Kit position goes in a brief. Ever.**

## WHAT IS LEFT TO BUILD — ONE SMALL THING

**A poller that reads new issues and writes them into `inbox/` as letters.** The
repository is public, so the issues API needs **no token and no credential at all.**

**Issues are already enabled on the repository — I checked.** The only other thing
outstanding is somewhere for briefs she can read, which is the push question you already
have.

## ONE THING RECORDED SO IT IS NOT A SURPRISE

**On a public repository, every issue is public.** Her design answers become readable by
anyone the moment she files one. **You have said publication is not a concern — this is
noted as a decision rather than discovered later.**

---

**THE QUESTIONS, IN ORDER:**

1. Connect the GitHub plugin — and when it asks, can it be limited to this one
   repository, and to issues without commit rights?
2. Do you want the issue poller built now, or after the first answer proves the loop by
   hand?

*C1, 2026-09-12. Nothing built, nothing connected.*
