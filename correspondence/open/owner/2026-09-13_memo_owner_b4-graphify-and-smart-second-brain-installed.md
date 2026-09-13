# Memo

To:      Owner
From:    Architecture (Grok)
Date:    2026-09-13
Status:  Open
Subject: B4 Ask layer — Graphify + Smart Second Brain installed locally (your two Obsidian clicks left)
Owner-action: yes

## Already checked
- Project research: local Graphify, no hosted upload (`claude/RESEARCH_graphify-hosted-versus-local-2026-09-10.md`)
- Ollama already installed with chat models; pulled `nomic-embed-text`
- Did not touch Claude Code's B2 work lane

## Done on disk
1. `graphifyy[ollama,mcp]` in `venv/`
2. Code graph built: `graphify-out/graph.json` — **27,467 nodes / 33,273 edges** (AST only, no cloud)
3. Smart Second Brain **2.1.0** under `.obsidian/plugins/smart-second-brain/` and listed in `community-plugins.json` with Dataview
4. User env `OLLAMA_ORIGINS=app://obsidian.md*`
5. HOWTO: `claude/HOWTO_b4-graphify-and-smart-second-brain-2026-09-13.md`

## Your manual steps (Obsidian UI — I cannot click these)
1. Restart or reload Obsidian
2. Confirm **Smart Second Brain** is enabled
3. Settings: Ollama at `http://localhost:11434`, embed `nomic-embed-text`, chat `qwen3:14b`
4. Let it index the vault (first run is slow)

If Ollama connection fails: quit Ollama from the tray and start it again so it picks up `OLLAMA_ORIGINS`.

*Architecture (Grok).*