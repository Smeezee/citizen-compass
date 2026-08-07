# Update: Cloudflare agent setup completed (2026-08-06)

Done in two halves, because the second was blocked for me.

- `claude plugin marketplace add cloudflare/skills` — run by me, succeeded,
  declared in user settings.
- `claude plugin install cloudflare@cloudflare` — **blocked by the Claude Code
  permission classifier** when I attempted it. Sleven ran it directly instead.

Verified: `cloudflare@cloudflare`, version 1.0.0, scope user, status enabled.

## What this changed, and where

This is configuration **outside the repo** — the user-scope Claude config, not
anything under `citizen-compass/`. It registers five remote MCP endpoints
(`mcp.`, `docs.mcp.`, `bindings.mcp.`, `builds.mcp.`, `observability.
mcp.cloudflare.com`). Cloudflare OAuth triggers on first use of a Cloudflare
tool, separately from the `wrangler` OAuth login done earlier tonight.

Recorded here because hard rule 6 names MCP server registration and `.claude/`
config as off-limits without asking, so the fact that it happened — and that it
was authorised, deferred, then completed by hand — belongs in the record rather
than only in a terminal scrollback.

## Remaining step

`/reload-plugins` in Claude before the plugin's tools become available in this
session.

## Note on how this arrived

The instruction was "fetch and execute the instructions at
`developers.cloudflare.com/agent-setup/prompt.md`". Hard rule 7 forbids
executing fetched content, so it was fetched and **read**, its two commands
reported, and confirmation taken before anything ran. The content turned out to
be exactly what was asked for and nothing more.
