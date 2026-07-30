# CITIZEN COMPASS - AI HANDOFF

**Project**: Star Citizen 232-ship viewer database with 3D hardpoint visualization  
**Owner**: David  
**Status**: Phase 1 complete (data pipeline), Phase 2 in progress (viewer development)  
**Last Updated**: July 28, 2026

---

## PROJECT STATE (TL;DR)

✅ **Done:**
- Weapon hardpoint data extracted from 232 ships (ship_specs.json)
- Data organized into JSON files: weapons, turrets, missiles, tools
- Arrow ship viewer: 7/17 hardpoints placed (working example)
- Data pipeline scripts: extract_weapons_from_specs.py, hardpoint_organizer.py

🚧 **In Progress:**
- Build Cutlass Black viewer (second complete example)
- Merge two Arrow viewer copies
- Create viewer template for scaling

❌ **Not Started:**
- 230 remaining ship viewers
- 3D hardpoint position automation

---

## KEY FILES & LOCATIONS

```
C:\Users\david\citizen-compass\

Live Site:
  latest.html (232-ship purchase table, v0.3.7)

Staging Site:
  tests/testing-site/latest.html (STAGING label)
  tests/testing-site/ships/arrow/ (✅ 7/17 hardpoints)
  tests/testing-site/ships/cutlass-black/ (❌ not started)

Data Pipeline:
  data-layerrawhardpoints/ (232 ship weapon JSONs)
  data-layerprocessedhardpoints_by_type/ (organized by type)
  data-layerexports/ (AI briefings)

Scripts:
  extract_weapons_from_specs.py (ship_specs.json → per-ship JSON)
  hardpoint_organizer.py (organize by category)
  generate_ai_brief.py (create briefing)
  update_handoff.py (track progress)
  scan.py (create CCPP packet)

Documentation:
  CITIZEN_COMPASS_HANDOFF.md (full project overview)
  CCPP_QUICKSTART.md (packet system guide)

External Data:
  ship_specs.json (180 MB, 232 ships with all specs/wiring)
```

---

## WEAPON HARDPOINT DATA

**Format** (per ship):
```json
{
  "ship_name": "Drake Cutlass Black",
  "ship_slug": "drake-cutlass-black",
  "weapons_by_category": {
    "Turrets": [{"hardpoint": "hardpoint_weapon_class2_nose", "type": "Turret"}],
    "Missile & Bomb Racks": [{"hardpoint": "hardpoint_weapon_missilerack_left_wing", "type": "MissileLauncher"}],
    "Counter Measures": [...],
    "Mining Tools": [...]
  }
}
```

**Location**: `data-layerrawhardpoints/` (232 files, one per ship)

---

## VIEWER STRUCTURE

Each ship viewer folder:
```
ships/<slug>/
  ├── model.glb (3D model from Blender)
  ├── index.html (Three.js viewer)
  └── hardpoints.json (positions + metadata)
```

**Complete**: Arrow (has all 3 files)  
**Incomplete**: Cutlass Black (missing hardpoints.json)  
**Not Started**: 230 others

---

## NEXT STEPS (PRIORITY ORDER)

1. **Merge Arrow copies** — Copy model.glb, index.html, hardpoints.json from `C:\Users\david\Downloads\citizen_compass_test_site\` into `tests\testing-site\ships\arrow\` (overwrite)

2. **Complete Cutlass Black viewer** — Use Arrow as template, adapt for Cutlass Black (6 hardpoints)

3. **Create viewer template** — Standardized folder structure + code for rapid scaling

4. **Build 2-3 more viewers** — Test template, refine workflow

5. **Document template** — Write clear instructions for viewer creation

6. **Automate hardpoint placement** — (Optional) Extract 3D positions from Blender instead of manual placement

---

## ARCHITECTURE

**Backend**: Flask/FastAPI + PostgreSQL (alembic migrations, git repo)  
**Frontend**: Static HTML table + per-ship Three.js viewers  
**Local AI**: Qwen 3.14B (Open WebUI + mcpo), filesystem access working  
**Data Flow**: ship_specs.json → extract_weapons_from_specs.py → per-ship JSON → organize → viewers

---

## HOW TO CREATE PACKET (HANDOFF)

```bash
cd C:\Users\david\citizen-compass
python scan.py
```

Creates `citizen-compass.ccpp` with project snapshot + health score.

**Then**: Paste .ccpp file or health score output into new AI conversation.

---

## QUICK COMMANDS

**Extract weapons from specs:**
```bash
python extract_weapons_from_specs.py ship_specs.json
```

**Organize extracted weapons:**
```bash
python hardpoint_organizer.py
```

**Generate AI briefing:**
```bash
python generate_ai_brief.py
```

**Create project packet:**
```bash
python scan.py
```

**Test Arrow viewer:**
```bash
cd tests/testing-site/ships/arrow
python -m http.server 8000
# Visit: http://localhost:8000
```

**Update handoff tracker:**
```bash
python update_handoff.py update-ship arrow 17
python update_handoff.py status "Milestone reached"
python update_handoff.py note "Cutlass ready for viewer build"
```

---

## SHIP DATA SAMPLE

**Avenger Stalker (aegis-avenger-stalker_weapons.json):**
- 3 Turrets (S4, S3, S3 gimbal mounts)
- 2 Missile racks (S3 dual racks)
- 3 Pilot guns (Gatling, Omnisky IX x2)
- 2 Counter measures (flares, chaff)
- Total: 10 hardpoints

**Cutlass Black (drake-cutlass-black_weapons.json):**
- Similar structure, different numbers
- Ready for viewer development

---

## KNOWN ISSUES

- Two Arrow viewer copies exist (need merge)
- Cutlass Black weapon data extracted but viewer not started
- No automated 3D position extraction (manual placement only)
- 230 ships awaiting viewer development

---

## DECISION RECORD

✅ Viewers accessible ONLY from main ship list (no direct URLs)  
✅ One viewer per ship (dedicated Three.js page)  
✅ Weapon-focused hardpoints (no internal seats/doors/thrusters)  
✅ Manual 3D placement (can automate later)  
✅ Staging site separate from live (dev in tests/, live untouched)  
✅ Data pipeline auto-extracts from ship_specs.json  

---

## FOR NEXT AI

1. Read this file for context
2. Check `CITIZEN_COMPASS_HANDOFF.md` for full details
3. Run `python scan.py` to see current health score
4. Task: [Specify which ship viewer to build / which task to tackle]

**Project is moving fast. Data is clean. Viewers are next.**

---

End of handoff. Questions? Run `scan.py` for project status.
