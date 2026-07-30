# AI Architect System — Status as of now

## What's confirmed working right now

| Piece | Status |
|---|---|
| Ollama | ✅ Running. Models: `qwen3.6:latest` (23GB), `qwen2.5-coder:14b` (9GB) |
| Docker Desktop | ✅ Installed and running |
| Open WebUI | ✅ Running at `http://localhost:3000`, logged in, on version 0.11.0 |
| Memories | ✅ Turned on (Admin → General) |
| Web Search | ✅ Turned on, using DDGS (DuckDuckGo) |
| Code Execution | ✅ Turned on, using Pyodide |
| Node.js | ✅ Installed (v24.18.0) |
| uv / uvx | ✅ Installed (v0.11.32) |
| kokoro-tts | ⚠️ Container is running, but voice playback gives a "Server Connection error" — unresolved, paused to focus on higher-priority steps |
| Filesystem tool (mcpo) | 🔄 In progress — this is the very next thing to finish |

## Where your actual files are

**Real project folder:** `C:\Users\david\citizen-compass`
- Contains a `releases` folder, a `static` folder, and a Python `venv` with `litellm` installed (a sign a backend API was already started by the other AI — not yet explored)

**Other copies found on your machine** (not the primary folder, just other locations the same/older files ended up):
- `C:\Users\david\Desktop\Citizen Compass\`
- `C:\Users\david\Desktop\done ships\`
- `C:\Users\david\Downloads\arrow_hardpoint_viewer\`
- `C:\Users\david\Downloads\citizen_compass_test_site\`

**Project folder we created for setup files:** `Documents\AI Architect System` — holds `docker-compose.yml` and (in progress) `mcpo-config.json`

## What you already have built (bigger than we first realized)

1. A ship reference table site ("Citizen Compass") — dark cyan/amber sci-fi theme, searchable table
2. A **working 3D hardpoint viewer prototype** for the Arrow ship — Three.js, loads the actual `model.glb`, clickable glowing markers, popup with equipment info, camera orbit/zoom. Note in it says **7 of 17 hardpoints placed**
3. A `hardpoints.json` data file with the naming/structure convention already established
4. A Python virtual environment with `litellm` — unexplored, possible early backend work

## The exact spot we're at right now

We're setting up the **filesystem tool** — the first real capability that lets your AI in Open WebUI actually read and write files in `C:\Users\david\citizen-compass`, instead of just talking about them.

**Immediate next step:** run this in PowerShell (from inside `Documents\AI Architect System`, with `mcpo-config.json` saved there):

```powershell
uvx mcpo --port 8100 --config mcpo-config.json
```

Then paste me what it prints — we confirm it started, then add it in Open WebUI under **Admin → Tools → Integrations → External Tool Servers** (Type: OpenAPI, URL: `http://localhost:8100`).

## After that, in order

1. **Finish filesystem tool** — confirm the AI can actually list/read files in your project folder
2. **Blender integration** (blender-mcp) — not started yet
3. **Coding worker** — VS Code + Cline, pointed at `qwen2.5-coder:14b` — not started yet
4. **Investigate the existing `litellm` venv** — see what the other AI already built before continuing
5. **Finish the hardpoint viewer** — 10 more hardpoints to place on the Arrow, then repeat for other ships
6. **Tailscale + phone access** — not started yet
7. **kokoro-tts voice fix** — parked, low priority
8. **Broker (web scraper) and Observer (video transcription) workers** — future, after the core system works

## Your persona

You've already written a solid system-prompt persona for the AI in Open WebUI ("Citizen Compass AI Core System Persona v2.1") — good safety rules and structure. One gap worth patching once things are calmer: it should explicitly say *"if a tool isn't connected, say so — don't describe hypothetical actions as if they happened,"* since we saw it draft a very convincing but entirely unbuilt architecture document earlier.
