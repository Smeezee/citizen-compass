# RESEARCH — tools that let Claude watch the screen

**Filed 2026-09-11 by the Adjutant desk, first look only.** Sleven is sending the question to
Echo; Perplexity is also searching. Nothing installed.

## THE ANSWER: IT EXISTS

**screenpipe** — [github.com/screenpipe/screenpipe](https://github.com/screenpipe/screenpipe),
read 2026-09-11.

- Continuous capture of screen and audio, in its own words "creating a searchable,
  AI-powered memory": screenshots taken on events, paired with accessibility data, text
  read off the screen when needed, and speech transcribed locally.
- Stored locally in SQLite. "Nothing sent to external servers" by default.
- Windows 10/11 fully supported, with an .exe installer.
- Works as an MCP server, so Claude can query the recorded screen history.
- Source code free for personal, non-commercial use. The signed desktop app is a
  subscription: Standard $25/month, Pro $50/seat, Enterprise $150/seat. Prices read
  2026-09-11.
- Product analytics (PostHog) and crash reports (Sentry) are on by default and can be
  turned off.

**Simpler, on-demand screenshot servers also exist** — for example `claude-screen-mcp` and
`screen-capture-mcp` on GitHub. **Not verified beyond their search listings.**

## WHAT MATTERS BEFORE ANYONE INSTALLS ANYTHING

- **It records everything on screen, including passwords and private messages.** That
  is a security decision, not just a tool choice.
- **How it would reach Cowork:** the Cowork setup documents that MCP servers installed on
  the desktop are passed through to the session. None are configured today. Not tested
  with screenpipe.
- **It is not real-time watching either.** It builds a searchable history that Claude asks
  questions of. Whether that is fast enough for anything live is untested.
- **It overlaps the Looking Project**, which is a separate project by Sleven's standing
  ruling. Whether one replaces, feeds or is kept apart from the other is his call.
