# HOWTO — B4 Ask layer: Graphify + Smart Second Brain (local)

Filed 2026-09-13 by Architecture (Grok). Nothing leaves the machine.

## What each one is (plain)

- **Obsidian** = the window into your markdown vault (already running).
- **Smart Second Brain** = Obsidian plugin: search by meaning + topic graph + optional chat. Uses **Ollama** on this PC.
- **Graphify** = code index. Lets an AI ask questions about Python/Go structure. Separate from Obsidian.

## Done for you

1. `graphifyy[ollama,mcp]` installed in project `venv/`
2. Ollama model `nomic-embed-text` pulled (embeddings). Chat models already present: `qwen3:14b`, `qwen2.5-coder:14b`
3. Plugin files at `.obsidian/plugins/smart-second-brain/` (v2.1.0)
4. Enabled in `.obsidian/community-plugins.json` alongside Dataview
5. User env `OLLAMA_ORIGINS=app://obsidian.md*` set (restart Ollama / Obsidian if the plugin cannot reach Ollama)
6. `graphify-out/` gitignored

## Your two clicks in Obsidian

1. Restart Obsidian (or reload) so it sees the new plugin.
2. Settings → Community plugins → confirm **Smart Second Brain** is on.
3. Open Smart Second Brain settings: provider **Ollama**, base URL `http://localhost:11434`, embedding model **nomic-embed-text**, chat model **qwen3:14b** (or coder). Run its Test if offered.
4. Start indexing when it asks — first pass can take a while on this vault.

## Graphify (code half)

```
venv\Scripts\graphify.exe update .
venv\Scripts\python.exe -m graphify.serve graphify-out\graph.json
```

Code-only rebuild needs no cloud model. Document-half with Ollama is optional later and still local.

## Boundaries (Architecture)

- No hosted Graphify upload.
- Plugin does not replace correspondence trays — it reads the vault; trays stay the record for decisions.
- B1 `_links/` still feeds Obsidian’s native graph for path citations.

*Architecture (Grok).*

---

## Living map

Hub: [[claude/HIGHLIGHTS_mail-backlog-keep-surface-2026-09-13]] · [[GRAPH-LIVING-MAP]] · [[OWNER-NOW]]
