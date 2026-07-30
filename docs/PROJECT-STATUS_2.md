# AI Architect System — Status as of now

## What's confirmed working right now

| Piece | Status |
|---|---|
| Ollama | ✅ Running. Models: `qwen3:14b` (manager, ~9GB) and `qwen2.5-coder:14b` (coding worker, ~9GB). `qwen3.6:latest` (23GB) was removed — it didn't fit in 12GB VRAM and caused 30-40 min response times |
| Docker Desktop | ✅ Installed, running, set to start on login |
| Open WebUI | ✅ Running at `http://localhost:3000`, logged in, version 0.11.0 |
| Memories | ✅ Turned on |
| Web Search | ✅ Turned on, using DDGS (DuckDuckGo) |
| Code Execution | ✅ Turned on, using Pyodide |
| Node.js | ✅ Installed (v24.18.0) |
| uv / uvx | ✅ Installed (v0.11.32) |
| kokoro-tts | ⚠️ Container running, voice playback still gives a connection error — parked, low priority |
| Filesystem tool (mcpo) | ✅ Working when run manually. Root cause of earlier "AI can't see files" confusion: the PowerShell window running mcpo got closed during other troubleshooting, silently killing the connection. Currently mid-setup of a Scheduled Task so it starts automatically at login instead of needing a manual window — that task creation just failed once (`Get-ScheduledTask` came back empty, meaning `Register-ScheduledTask` didn't actually run/succeed) and is being redone |
| AI Persona | ✅ Updated to v2.2 — added a Tool Honesty Protocol, reasoning-mode guidance, and a "Not Yet Built" section so the persona stops implying things exist that don't |

## Where your actual files are

**Real project folder:** `C:\Users\david\citizen-compass`
- Contains a `releases` folder, a `static` folder, and a Python `venv` with `litellm` installed (a sign a backend API was already started by the other AI — still not explored)

**Other copies found on your machine** (older/duplicate locations, not primary):
- `C:\Users\david\Desktop\Citizen Compass\`
- `C:\Users\david\Desktop\done ships\`
- `C:\Users\david\Downloads\arrow_hardpoint_viewer\`
- `C:\Users\david\Downloads\citizen_compass_test_site\`

**Setup files folder:** `Documents\AI Architect System` — holds `docker-compose.yml`, `mcpo-config.json`, and (in progress) `start-mcpo.ps1`

## What you already have built

1. A ship reference table site ("Citizen Compass") — dark cyan/amber sci-fi theme, searchable table
2. A **working 3D hardpoint viewer prototype** for the Arrow ship — Three.js, loads the actual `model.glb`, clickable glowing markers, popup with equipment info, camera orbit/zoom. 7 of 17 hardpoints placed
3. A `hardpoints.json` data file with the naming/structure convention already established
4. A Python virtual environment with `litellm` — unexplored, possible early backend work

## The exact spot we're at right now

Setting up a Windows Scheduled Task so `mcpo` (the filesystem tool) starts automatically and silently at login, instead of needing a PowerShell window kept open by hand. The first attempt to register the task didn't take — `Register-ScheduledTask` needs to be re-run and its output actually checked for errors this time.

**Immediate next step:** run `Get-ScheduledTask -TaskName "MCPO Filesystem Tool" -ErrorAction SilentlyContinue` to confirm it's really missing, then re-run the `Register-ScheduledTask` block and read the full output (including any red error text) this time.

Once that's solid: retest the filesystem tool from a fresh chat with `qwen3:14b` — ask it to list the contents of `citizen-compass` and confirm real folder names come back, not a fabricated or empty answer.

## After that, in order

1. **Get mcpo auto-starting reliably** (see above)
2. **Confirm filesystem tool end-to-end** with a clean test
3. **Blender integration** (blender-mcp) — not started
4. **Coding worker workflow** — VS Code + Cline pointed at `qwen2.5-coder:14b` — not started
5. **Investigate the existing `litellm` venv** — see what the other AI already built before continuing
6. **Finish the hardpoint viewer** — 10 more hardpoints on the Arrow, then repeat for other ships
7. **Tailscale + phone access** — not started
8. **kokoro-tts voice fix** — parked, low priority
9. **Broker (web scraper) and Observer (video transcription) workers** — future, after the core system works

## Lessons banked so far (worth remembering)

- **Model size vs. VRAM matters enormously.** A model that doesn't fully fit in VRAM doesn't just run "a bit slower" — partial CPU offload can turn seconds into tens of minutes. Stay under ~10-11GB per model on this 12GB card.
- **A connected tool can silently disconnect** if the process serving it (mcpo, in this case) gets closed — Open WebUI won't necessarily surface a clear error, the AI just quietly falls back to whatever built-in tool sounds closest.
- **The AI will confidently write very convincing content for things that were never built or run**, unless explicitly told not to (this is what the Tool Honesty Protocol in the persona now addresses).
