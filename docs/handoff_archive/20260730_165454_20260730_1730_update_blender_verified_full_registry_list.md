# UPDATE — blender-mcp verified live, CC Hardpoint Tool summary given, full 26-item registry list produced (2026-07-30)

## 1 — blender-mcp: VERIFIED LIVE, real data returned

Session restart picked up the `blender` MCP server. Called two real tools against the actual running Blender session (not assumed from "Connected" status):

- `get_scene_info` returned real scene data: 3 objects (Cube at origin, Light, Camera), 2 materials — the Blender default startup scene.
- `get_viewport_screenshot` returned an actual rendered image matching that scene (cube + light + camera, default grey viewport with axis lines).

Bridge confirmed end-to-end: Claude can now read and (via `execute_code`, not yet used) drive the live Blender session.

## 2 — CC Hardpoint Tool: covers the placement/export job standalone

Re-confirmed by reading the full addon source (`citizen_compass_hardpoints.py`, Blender's local addons folder). It's a complete manual workflow: set ship name, pick from a 15-item hardpoint-type dropdown, place a tagged Empty at the 3D cursor, list/select/delete markers, Export/Import to JSON matching the project's exact hardpoints.json schema (name/type/label/position.x,y,z @ 4 decimals). This fully solves hardpoint placement + export with zero dependency on blender-mcp. blender-mcp adds a different capability (AI-driven scene inspection/control), not a replacement for this addon — still the user's call whether that layer is wanted now that the bridge works.

## 3 — Registry gap: full 26-name list reproduced live (not just the count)

Re-ran the DB-vs-registry comparison fresh against the real Postgres DB (232 ships) and the real `data-layer/ship_registry.json` (295 entries), reproducing last session's script logic rather than trusting the stored number. Got the same 62 DB-ships-with-no-exact-match, same ~36 naming-convention mismatches, same 26-count "no similar match" set. Named list:

600i Explorer, 85X, Ares Ion, Arrastra, Crucible, Endeavor, Expanse, G12, G12r, Galaxy, Hull D, Hull E, Kraken, Kraken Privateer, Legionnaire, Liberator, Merchantman, Nautilus, Odin, Odyssey, Orion, Pioneer, Ranger CV, Ranger RC, Ranger TR, Vulcan

Re-verified the known blind spot directly this time: grepped the registry for "Ares" + "Ion" and confirmed `Ares Star Fighter Ion` (and a variant) genuinely exist — so `Ares Ion` is a false negative from difflib's similarity cutoff, not a real gap. Reliable "genuinely no similar entry" count is 25, with that one caveat. Still recommending a manual pass against CIG's canonical ship list before treating any of these as confirmed real gaps rather than further naming mismatches.

## Nothing committed/pushed this round — investigation/verification only, one throwaway script in scratchpad (not in the repo).
