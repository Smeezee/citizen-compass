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
| Filesystem tool (mcpo) | ✅ Running and connected in Open WebUI, pointed at `C:\Users\david\citizen-compass`. Confirming the AI can actually read files as of this handoff. |

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

The filesystem tool is running and connected. We just asked the AI in chat to list real files in `citizen-compass` to confirm it actually works end-to-end (not just configured) — that check was still running as of this handoff. Note for next time: the first real tool call after connecting a new server can be slow — that's normal, not a sign of a problem.

**Immediate next step:** open that same chat and check whether it actually listed real folder names (`releases`, `static`, `venv`, etc.) instead of a made-up answer. If yes, Part 7 is fully done.

## After that, in order

1. **Confirm filesystem tool** (see above — likely finished by the time you read this)
2. **Blender integration** (blender-mcp) — not started yet
3. **Coding worker** — VS Code + Cline, pointed at `qwen2.5-coder:14b` — not started yet
4. **Investigate the existing `litellm` venv** — see what the other AI already built before continuing
5. **Finish the hardpoint viewer** — 10 more hardpoints to place on the Arrow, then repeat for other ships
6. **Tailscale + phone access** — not started yet
7. **kokoro-tts voice fix** — parked, low priority
8. **Broker (web scraper) and Observer (video transcription) workers** — future, after the core system works

## Your persona

You've already written a solid system-prompt persona for the AI in Open WebUI ("Citizen Compass AI Core System Persona v2.1") — good safety rules and structure. One gap worth patching once things are calmer: it should explicitly say *"if a tool isn't connected, say so — don't describe hypothetical actions as if they happened,"* since we saw it draft a very convincing but entirely unbuilt architecture document earlier.
