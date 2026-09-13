# Memo

To:      Owner
From:    Architecture
Subject: You were right. It is MCP, it runs on your own machine, and it closes the loop completely — Echo files her own work and you say one sentence.

**Design rewritten on disk: `claude/DESIGN_the-echo-loop-2026-09-12.md`. Nothing built.**

**Everything I proposed before this was built on an assumption nobody checked — that you
used ChatGPT in a browser. You don't. That killed the share link, the tab scrape and the
download, and you were right that there is something better in 2026.**

## WHAT IT IS

**OpenAI's own documentation says the ChatGPT DESKTOP APP supports MCP servers, including
ones that run as a local process on your machine, and that their tools can write.**

So: a small program on your PC that Echo can call. It hands her the open briefs and it
takes her finished answers and drops them into `inbox/`, where the watcher files them to
my tray.

    you say    "work the open briefs"
    Echo       reads them, works them, and FILES HER OWN ANSWER
    me         read it against the repository, rule, then do it or send to Code

**No clipboard, no browser, no share link, no web, no API key.** A local process started
by your own app and reachable by nothing else.

**Your action per round trip: one sentence.** Possibly one approval click per write,
depending on how the approval setting lands — I am not going to pretend that away until
it is seen.

## WHY THIS IS THE ANSWER AND NOT ANOTHER OPTION

**It needs no credentials.** That is what killed the API route twice: a local server has
no key, no endpoint and no public surface. **Rule 23 is not engaged at all.**

**It is not fragile.** Nothing depends on a page's layout, a tab being open, or a window
being focused.

**And it also fixes the inbound half** — the same server hands her the briefs, so that
side stops waiting on the GitHub push.

## THE BOUNDARY, WHICH IS MINE TO SET AND NOT NEGOTIABLE AT BUILD TIME

Handing an outside AI a write tool into your repository is a real thing to hand out.
**It gets bounded in the tool, not by asking her nicely:**

    writes   only into inbox/, only .md, never overwrites — refuses instead,
             a required memo header, a size cap
    reads    design/briefs/, docs/, claude/ and nothing else
    never    .env, correspondence/, _needs_review/, logs/, any credential file,
             anything outside the repository
    no       delete, move, rename or execute

**The worst she can then do is put a bad letter in a tray that a desk reads before
anything happens.** That is a risk this project already carries for every desk.

## THE ONE THING THAT GATES IT, AND IT IS THIRTY SECONDS IN YOUR APP

**Two sources disagree and I am not picking the convenient one.** OpenAI's own docs
describe the desktop app taking a LOCAL server. A secondary guide says custom MCP in
ChatGPT is remote-HTTPS only through a developer mode on the web, and flags an ambiguity
about whether **Plus** gets write tools at all.

**They are probably two different surfaces. I am not certain, and that uncertainty is
the entire gate.**

**Open the ChatGPT desktop app's settings and look for MCP, connectors or developer
tools. Tell me what it offers and whether it will take a local command.**

**If it takes a local server, it gets built and everything else I proposed tonight is
history. If it only takes a remote one, that is a public endpoint with authentication —
credentials, and it comes back to you as its own decision rather than being built
quietly. If it takes neither, the floor is a clipboard hotkey: you copy her answer in
the desktop app, one keypress files it. Two keystrokes, no web, and still better than
anything I proposed before you told me about the app.**

---

**THE QUESTION:**

1. What does the ChatGPT desktop app's settings offer for MCP — a local command, a
   remote URL, or nothing?

*C1, 2026-09-12. Nothing built.*
