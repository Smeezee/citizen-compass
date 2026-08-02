# UPDATE — Phase 2 Blender/MCP setup: 3 of 5 steps done and verified, 1 genuinely blocked on you (2026-07-30)

## 1 — Blender: installed, verified by actually running it

Blender 4.5.4 LTS confirmed at `C:\Program Files\Blender Foundation\Blender 4.5\blender.exe`, build date 2025-10-28. Ran `blender.exe --version` directly and got real output back, not just a folder check.

## 2 — uv/uvx: already installed, no action needed

Found at `C:\Users\david\.local\bin\uv.exe` / `uvx.exe` (the official installer's default location) - `uv 0.11.32 (2026-07-23 build)`. Ran `--version` on both to confirm they actually execute. Confirmed on PATH in both bash and PowerShell via `where`/`where.exe`. Nothing to install.

## 3 — blender-mcp addon + registration: done

- Downloaded `addon.py` from github.com/ahujasid/blender-mcp (raw main branch), saved to `C:\Users\david\blender-mcp-setup\addon.py` (122,557 bytes, 2,883 lines). Confirmed real content: `bl_info` shows name "Blender MCP", version 1.2, requires Blender >= 3.0.0 (our 4.5.4 is fine).
- Registered with Claude Code: `claude mcp add blender uvx blender-mcp` succeeded, wrote to `C:\Users\david\.claude.json`.
- `claude mcp list` now shows `blender: uvx blender-mcp - Connected`.

**Important precision point, not glossed over:** that "Connected" status is only the stdio handshake between Claude Code and the `uvx blender-mcp` process itself - it does NOT mean it's bridged to a running Blender session yet. I checked for actual blender-mcp tools (scene inspection, object info, etc.) in this session and found none exposed. That's expected until the addon is enabled in Blender and "Connect to Claude" is clicked on your end - and possibly needs a session restart on my end to pick up the newly registered server's tools even after that. I have not claimed this works end-to-end because I have not verified it end-to-end.

**GUI steps for you (I gave the exact click sequence in-conversation, repeating here for the record):**
1. Blender -> Edit -> Preferences -> Add-ons tab
2. Click the dropdown arrow (Blender 4.2+ replaced the old "Install..." button) -> "Install from Disk..."
3. Select `C:\Users\david\blender-mcp-setup\addon.py`
4. Enable the "Blender MCP" checkbox in the add-ons list
5. In the 3D viewport, press N -> BlenderMCP tab -> "Connect to Claude"

Flagged honestly: unlike everything else in this audit, I have no GUI access to Blender, so this click sequence is based on accurate knowledge of the Blender 4.2+ addon UI, not something I watched happen. If anything's slightly off once you're actually in the Preferences window, that's why.

## 4 — Connection verification: BLOCKED, correctly not claimed as done

Cannot proceed until you've done the GUI steps above. Once you have, I'll need to actually invoke a blender-mcp tool (scene inspection at minimum, screenshot if available) and report exactly what comes back - real object data or nothing - rather than assuming it works from the "Connected" MCP status alone.

## 5 — Hardpoint-placement workflow: pieces confirmed to exist, nothing built (as instructed)

- GLB import: native Blender operator (`bpy.ops.import_scene.gltf`), and blender-mcp's own addon already calls this internally in several places - so once the bridge is live, GLB import is available through MCP itself.
- Placing marker/Empty objects at hardpoint locations: native Blender Python API (`bpy.ops.object.empty_add`), standard and well-established.
- Exporting positions into this project's hardpoints.json format: PARTIAL. blender-mcp exposes `get_scene_info`/`get_object_info` to read real object data back out, but there is no existing script anywhere in this repo that formats that into the project's exact schema (name/type/label/position.x,y,z, matching Arrow's file). That's genuinely new code, not yet written.
- Also confirmed: the addon exposes an `execute_code` method (arbitrary Python execution in a live Blender session) - this is the capability your standing instruction about "no execution against a real, unsaved file without asking first" refers to. Confirmed it exists. Not used.

## Net status: Phase 2 steps 1-3 and 5 done and verified for real. Step 4 is the one genuinely waiting on you - install/enable the addon and click Connect, then let me know and I'll verify the live bridge for real rather than assume it from the MCP registration alone.
