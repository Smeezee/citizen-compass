# UPDATE — blender-mcp still blocked (session restart needed), CC Hardpoint Tool discovered, full registry gap detail (2026-07-30)

## 1 - blender-mcp: cannot verify yet, root cause identified precisely

User connected on Blender's side ("Running on port 9876"). Tried three ways to invoke an actual blender-mcp tool from this session: ToolSearch for scene/object/screenshot tools (nothing), direct lookup of mcp__blender__* tool names (nothing), and `ListMcpResourcesTool(server="blender")` which returned an explicit error: server not found, available servers listed do not include blender.

Root cause: this running session has its own internal MCP server list separate from what `claude mcp list` (CLI) reports fresh from .claude.json. Since `blender` was registered mid-session via `claude mcp add`, this session never loaded it. Not a Blender-side problem - needs a session restart to pick up the newly-registered server before the bridge can actually be tested. Did not report success from the "Connected" status alone.

## 2 - Found: CC Hardpoint Tool addon, real and complete, predates this session

`citizen_compass_hardpoints.py` in Blender's local addons folder (AppData\Roaming\Blender Foundation\Blender\4.5\scripts\addons\), 12,955 bytes, file dated Jul 26 17:39 - four days before any Phase 1/2 work this session. Not tracked in the citizen-compass git repo, not mentioned in LATEST_HANDOFF.md or docs/ anywhere.

Read the full 347-line source. It's a complete, working manual hardpoint-placement tool: a "CC Hardpoints" panel lets you set a ship name, pick a hardpoint type from a 15-item dropdown, place a tagged Empty at the 3D cursor, list/select/delete placed markers, and Export/Import to JSON. The export schema is an exact field-for-field match to Arrow's real hardpoints.json (ship_name/ship_slug/hardpoints[].name,type,label,position.x,y,z at 4 decimal precision) - strong circumstantial evidence Arrow's file was made with this exact tool, though no git history or log trail proves it definitively.

This fully solves the "place markers -> export to our JSON format" workflow standalone, with zero dependency on blender-mcp. blender-mcp would only add something different - letting Claude read/drive the Blender scene programmatically - not a replacement for this addon. Flagged for the user to decide whether that AI-assisted layer is still wanted.

## 3 - Registry gap: full 62-item detail, not just count

Exact set comparison (100% reliable): 62 DB ships with no registry entry. Ran a similarity check against all registry names to separate real gaps from naming mismatches - this part is heuristic and has a demonstrated blind spot (see below).

~36 look like naming-convention mismatches, not real gaps: registry prefixes manufacturer name (Hull A -> MISC Hull A, Freelancer -> MISC Freelancer, Prospector -> MISC Prospector, Reliant Kore/Mako/Sen/Tana -> MISC Reliant *, Starfarer(+Gemini) -> MISC Starfarer*, Starlancer TAC/MAX -> MISC Starlancer*, Starlite/Fortune -> MISC *), registry adds "Mk I" to all 6 Aurora variants, "Ares Inferno" -> "Ares Star Fighter Inferno". One is a pure encoding artifact: DB has "San'tok.yai" (no macron), registry has "San'tok.yai" WITH macron on the a - literally the same ship, same root character that caused the original checker DEFECT bug, different symptom. ~13 more near-matches are probably spurious string-similarity noise (M50/M80, RAPTOR/RAFT, Genesis Starliner/Avenger Stalker, etc - different real ships).

26 had no similar registry entry at all by the similarity check - but caught the matcher missing at least one real alias: "Ares Ion" showed as no-match, yet "Ares Star Fighter Ion" genuinely exists in the registry (confirmed by direct grep). So this 26-count is an upper bound, not verified final - full list given to the user in-conversation with this caveat explicit. Recommended a manual pass against CIG's canonical ship list rather than trusting the automated similarity check as final.

## Nothing committed/pushed this round (no code changes made - this was investigation/verification only). Task 11 (blender-mcp live verification) stays pending, correctly not marked done.
