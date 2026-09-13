# Memo

To:      Owner
From:    Architecture
Subject: WITHDRAWN — my MCP answer was wrong. The page I read is Codex documentation, not ChatGPT's. Do not go looking for that menu.

**Correction filed on disk at the top of `claude/DESIGN_the-echo-loop-2026-09-12.md`.
Nothing was built, so nothing has to be undone.**

## WHAT I GOT WRONG

I quoted *"The ChatGPT desktop app, Codex CLI, and IDE extension support MCP servers"*
and told you that was your app. **It is not. That page is CODEX documentation** — its
breadcrumb is *Codex › Configuration › MCP*, its opening line is *"Give Codex access to
third-party tools"*, and it stores its settings at `~/.codex/config.toml`. **The sentence
I quoted ends "...and share MCP configuration for the same Codex host."**

**"The ChatGPT desktop app" there means the CODEX desktop app.** I read the sentence and
not the page, which is the primary-source-read-halfway failure this desk is warned about
in its own boot prompt. **You were one message from hunting for a menu that probably is
not there.**

## WHAT IS ACTUALLY TRUE, AS BEST I CAN ESTABLISH

**Custom MCP in consumer ChatGPT looks like: a developer mode, remote HTTPS servers only,
and web rather than mobile** — with an open question about whether Plus gets write tools
at all. **A local program started by your ChatGPT app is probably not on the table.**

**OpenAI's own help page puts connectors at Settings → Apps**, with a Plugins Directory,
and names the Apps SDK as the way to package an MCP-backed app. **It does not say which
plans, and it does not say whether the desktop app has it.**

## WHAT THAT PROMOTES, AND IT IS THE THING I CALLED THE FLOOR

**The clipboard hotkey is now the leading answer**, because it needs nothing from OpenAI
at all: you copy her answer in the app, one keypress writes it into `inbox/`, the watcher
files it to my tray.

**No web, no connector, no developer mode, no credentials, no plan dependency — and no
vendor can remove it.** Two keystrokes per round trip. **It also works identically if you
switch from ChatGPT to something else next year**, which none of the other routes do.

## ONE MEASURED THING, AND ONE QUESTION BEHIND IT

**I could not find a ChatGPT desktop application on your PC.** Four names tried —
`ChatGPT`, `OpenAI ChatGPT`, `ChatGPT Desktop`, `OpenAI`. The only near match offered was
**`ChatGPT Classic`**, which is the shape of a browser shortcut, not a standalone program.

**That is evidence, not proof** — the lookup may simply not see Microsoft Store apps. But
if what you are using is a web app in a window, the browser routes I withdrew come back,
and that changes the answer again.

---

**THE QUESTIONS, IN ORDER:**

1. In the ChatGPT app, open Settings and tell me what sections you see — is there an
   **Apps** or **Connectors** section, and does it mention adding your own?
2. Where did you install it from — the Microsoft Store, OpenAI's own download, or is it a
   shortcut that opens in a browser window?

*C1, 2026-09-12. Nothing built, nothing changed.*
