# PHASE 1: DATA FOUNDATION IMPLEMENTATION
## Based on Your Actual Files

**Date:** July 28, 2026  
**Status:** Ready to Build  
**Files Analyzed:** cutlass_black_hardpoints.json, index.html, HPs.blend

---

## WHAT YOU HAVE (Current State)

### 1. Hardpoint Data Format (JSON)
**File:** `cutlass_black_hardpoints.json`

**Structure:**
```json
{
  "ship_name": "cuttlass black",
  "ship_slug": "cuttlass_black",
  "hardpoints": [
    {
      "name": "hardpoint_missile_rack_missiles",
      "type": "missile_rack",
      "label": "Missiles",
      "position": {
        "x": 0.0378,
        "y": 22.1842,
        "z": -7.2337
      }
    },
    {
      "name": "hardpoint_weapon_gun_s3_ls",
      "type": "weapon_gun",
      "label": "S LS",
      "position": {"x": -6.2501, "y": 14.4718, "z": 1.5971}
    }
  ]
}
```

**What this tells us:**
- ✅ Hardpoint data is in JSON format (perfect)
- ✅ Each hardpoint has: name, type, label, position (x, y, z coordinates)
- ✅ Types include: `missile_rack`, `weapon_gun`, `weapon_turret`
- ✅ Positions are 3D coordinates (from Blender models)
- ⚠️ Only ONE ship file shown (Cutlass Black)

### 2. 3D Model File
**File:** `HPs.blend`
- This is a Blender file containing 3D ship models with hardpoint data
- The hardpoint positions in the JSON match coordinates from this Blender file

### 3. Website Display
**File:** `index.html`
- Citizen Compass website with searchable table interface
- Dark theme (cyberpunk aesthetic matching Star Citizen)
- Has legend for hardpoint types
- Has search controls
- Displays hardpoint data in organized table format

---

## CRITICAL QUESTIONS ANSWERED

### Q: Where is your raw data?
**A:** You have:
- Individual ship hardpoint JSON files (like `cutlass_black_hardpoints.json`)
- Blender file with 3D models and hardpoint positions
- HTML rendering of the data

### Q: How many ships do you have data for?
**A:** Based on files shown = **1 ship (Cutlass Black)** fully done, but your goal is **452+ ships**

### Q: What format is the data?
**A:** **JSON** ✅ (Perfect for AI and data processing)

### Q: Where do you want to centralize this?
**A:** We'll create a **Data Central** folder structure

---

## PHASE 1 IMPLEMENTATION PLAN

### STEP 1: Create Data Central Folder Structure

```
C:\Users\david\citizen-compass\data-layer\
│
├── raw/
│   ├── hardpoints/
│   │   ├── cutlass_black_hardpoints.json
│   │   ├── arrow_hardpoints.json
│   │   └── [all other ship hardpoints]
│   ├── ships/
│   │   ├── ships_manifest.json  (master list of all ships)
│   │   └── [ship specs]
│   ├── components/
│   │   └── components_manifest.json
│   └── blender/
│       ├── HPs.blend
│       └── [other model files]
│
├── processed/
│   ├── hardpoints_by_type.json
│   │   ├── weapons/
│   │   ├── turrets/
│   │   ├── missiles/
│   │   ├── guns/
│   │   └── components/
│   └── ship_hardpoint_matrix.json
│
└── exports/
    ├── AI_BRIEF_COMPACT.json
    └── AI_BRIEF_READABLE.md
```

**Why this structure:**
- `raw/` = your original data files (never modified)
- `processed/` = organized and categorized data
- `exports/` = the 5-minute AI briefing files

### STEP 2: Hardpoint Categorizer Script

I'll create a Python script that:

**Input:** Takes raw hardpoint JSON files  
**Process:** Reads the `type` field and categorizes:
- `missile_rack` → Missiles
- `weapon_gun` → Guns/Ballistic
- `weapon_turret` → Turrets
- `weapon_launcher` → Missiles
- Everything else → Components

**Output:** Creates organized JSON files:
```
processed/hardpoints_by_type/
├── weapons/
│   ├── gun_s3_ls.json
│   ├── gun_s3_lsb.json
│   └── [all other guns]
├── turrets/
│   ├── s3_turret.json
│   └── [all other turrets]
├── missiles/
│   └── [all missile hardpoints]
└── components/
    └── [all internal components]
```

### STEP 3: Ship Hardpoint Cross-Reference

Create a master matrix:
```json
{
  "cutlass_black": {
    "name": "Cutlass Black",
    "manufacturer": "Drake Interplanetary",
    "weapons": [
      {"name": "gun_s3_ls", "size": 3, "position": [-6.2501, 14.4718, 1.5971]},
      {"name": "gun_s3_lsb", "size": 3, "position": [-8.9397, 22.9537, -4.2935]}
    ],
    "turrets": [
      {"name": "s3_turret", "size": 3, "position": [-0.0279, 5.8662, 10.17]}
    ],
    "missiles": [
      {"name": "missile_rack", "size": 4, "position": [0.0378, 22.1842, -7.2337]}
    ],
    "total_hardpoints": 6,
    "verified": true,
    "last_updated": "2026-07-28"
  }
}
```

### STEP 4: AI Knowledge Export

Create the 5-minute briefing file:

**File:** `AI_BRIEF_COMPACT.json`

```json
{
  "briefing": {
    "version": "1.0",
    "generated": "2026-07-28",
    "project": "Citizen Compass",
    "mission": "Build complete Star Citizen ship viewer, hardpoint reference, and compatibility database"
  },
  "data_summary": {
    "total_ships": 452,
    "ships_with_hardpoints": 1,
    "total_hardpoints": 6,
    "by_category": {
      "weapons": 4,
      "turrets": 1,
      "missiles": 1,
      "components": 0
    }
  },
  "sample_ship": {
    "name": "Cutlass Black",
    "slug": "cutlass_black",
    "hardpoints_count": 6,
    "weapons": [
      {"position": "LS", "size": 3, "type": "gun"},
      {"position": "LSB", "size": 3, "type": "gun"},
      {"position": "RS", "size": 3, "type": "gun"},
      {"position": "RSB", "size": 3, "type": "gun"}
    ],
    "turrets": [
      {"position": "Top", "size": 3}
    ],
    "missiles": [
      {"quantity": "1 rack"}
    ]
  },
  "what_needs_work": [
    "Import hardpoint data for remaining 451 ships",
    "Cross-reference hardpoint types with in-game data",
    "Verify component compatibility",
    "Complete 3D models for all ships",
    "Add ship specifications (price, manufacturer, size, class)"
  ],
  "data_format": {
    "hardpoint_types": ["missile_rack", "weapon_gun", "weapon_turret", "weapon_launcher"],
    "position_format": {"x": "float", "y": "float", "z": "float"},
    "ship_fields": ["ship_name", "ship_slug", "hardpoints"]
  },
  "how_to_use": "This briefing contains everything needed to work on Citizen Compass. Each hardpoint has a name, type, label, and 3D position. Ships are organized by slug (cutlass_black, arrow, etc.)."
}
```

---

## WHAT I'LL BUILD FOR YOU (SPECIFIC CODE)

### 1. Hardpoint Organizer Script (`hardpoint_organizer.py`)

```python
import json
import os
from pathlib import Path

def categorize_hardpoint(hardpoint):
    """Categorize hardpoint by type"""
    hp_type = hardpoint.get('type', '').lower()
    
    if 'gun' in hp_type:
        return 'weapons'
    elif 'turret' in hp_type:
        return 'turrets'
    elif 'missile' in hp_type or 'launcher' in hp_type:
        return 'missiles'
    else:
        return 'components'

def process_ship_hardpoints(json_file):
    """Read ship hardpoints and organize by category"""
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    organized = {
        'ship_name': data['ship_name'],
        'ship_slug': data['ship_slug'],
        'categories': {
            'weapons': [],
            'turrets': [],
            'missiles': [],
            'components': []
        }
    }
    
    for hp in data['hardpoints']:
        category = categorize_hardpoint(hp)
        organized['categories'][category].append(hp)
    
    return organized

def main():
    raw_hardpoints_dir = 'data-layer/raw/hardpoints/'
    processed_dir = 'data-layer/processed/hardpoints_by_type/'
    
    # Process each ship file
    for json_file in Path(raw_hardpoints_dir).glob('*.json'):
        organized = process_ship_hardpoints(json_file)
        
        # Save organized version
        output_file = processed_dir + organized['ship_slug'] + '_organized.json'
        with open(output_file, 'w') as f:
            json.dump(organized, f, indent=2)
        
        print(f"✓ Processed {organized['ship_name']}")

if __name__ == '__main__':
    main()
```

### 2. AI Brief Generator (`generate_ai_brief.py`)

```python
import json
from pathlib import Path
from datetime import datetime

def generate_ai_brief():
    """Generate 5-minute AI briefing from processed data"""
    
    # Count data
    raw_dir = Path('data-layer/raw/hardpoints/')
    ships_processed = len(list(raw_dir.glob('*.json')))
    
    brief = {
        "briefing": {
            "version": "1.0",
            "generated": datetime.now().isoformat(),
            "project": "Citizen Compass",
            "mission": "Complete Star Citizen ship viewer and hardpoint database"
        },
        "data_summary": {
            "ships_with_hardpoints": ships_processed,
            "total_ships_target": 452
        },
        "what_needs_work": [
            f"Hardpoint data for {452 - ships_processed} remaining ships",
            "Cross-reference verification",
            "Component compatibility matrix"
        ]
    }
    
    # Save briefing
    with open('data-layer/exports/AI_BRIEF_COMPACT.json', 'w') as f:
        json.dump(brief, f, indent=2)
    
    print("✓ AI Brief generated")

if __name__ == '__main__':
    generate_ai_brief()
```

---

## WHAT HAPPENS WHEN YOU GIVE THIS TO A NEW AI

**You:** "Here's your briefing on Citizen Compass"  
**You:** [Pastes `AI_BRIEF_COMPACT.json` content]

**New AI reads:**
- ✅ Project name and mission
- ✅ 1 ship (Cutlass Black) fully mapped with 6 hardpoints
- ✅ 451 ships still need hardpoint data
- ✅ Data format (JSON with ship_name, ship_slug, hardpoints array)
- ✅ Hardpoint structure (name, type, label, position x/y/z)
- ✅ What work remains

**New AI can instantly:**
- Understand the data structure
- Write code to process more hardpoint files
- Validate incoming data
- Generate reports on progress
- Help complete the remaining ships

**Time to productivity:** 5 minutes or less ✅

---

## NEXT IMMEDIATE STEPS

### Step 1: Tell Me Where Your Files Are
**I need to know:**
1. Where are all your hardpoint JSON files stored?
   - `C:\Users\david\Desktop\Citizen Compass AI Brain\05 ships\` ?
   - Or another location?

2. How many hardpoint JSON files do you have?
   - Just Cutlass Black?
   - Or more scattered around?

3. Do you have a master ships list?
   - A file with all 452 ships and their metadata?

### Step 2: I'll Build the Scripts
Once I know where your files are, I'll create:
- ✅ `hardpoint_organizer.py` (auto-categorize everything)
- ✅ `generate_ai_brief.py` (creates 5-minute briefing)
- ✅ Folder structure (organize everything)

### Step 3: First Run
- You run the scripts
- All your hardpoint data gets organized
- The 5-minute briefing gets generated
- Ready to hand to any AI

---

## SUMMARY

**You have:**
- ✅ Hardpoint JSON format (perfect structure)
- ✅ 3D model file (Blender)
- ✅ Website display (HTML)
- ✅ 1 fully mapped ship (Cutlass Black)

**You need:**
- ❌ Centralized folder structure
- ❌ Hardpoint categorizer script
- ❌ AI briefing generator script
- ❌ All 451 remaining ships' hardpoint data

**I will build:**
- ✅ The folder structure
- ✅ The categorizer script (ready to run)
- ✅ The briefing generator (ready to run)
- ✅ Instructions for organizing your data

**Then you can:**
- ✅ Drop hardpoint files into `raw/hardpoints/`
- ✅ Run `hardpoint_organizer.py`
- ✅ Run `generate_ai_brief.py`
- ✅ Get a fresh briefing every time

**Ready?** Tell me where your hardpoint files are, and I'll build everything.

