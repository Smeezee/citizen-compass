# Citizen Compass Project Packet (CCPP) — Quick Start

## What Is This?

The **CCPP** is a self-contained archive application that scans your entire Citizen Compass project, auto-detects all files, validates everything, cross-references data, calculates health scores, and packs it all into a single **portable JSON file** you can pass between AIs, store, or backup.

Think of it like a **smart project snapshot** — drop it into any conversation and an AI instantly knows:
- How many ships have viewers (and which ones)
- How many weapon hardpoint files are extracted
- Overall project health (0-100 score)
- What's complete, what's in progress, what's missing

## Installation

Copy `ccpp.py` to your project root:
```
C:\Users\david\citizen-compass\ccpp.py
```

## Usage

### Create a Packet (First Time)

Scan your entire project and create the packet:

```bash
python ccpp.py create C:\Users\david\citizen-compass
```

This creates `citizen-compass.ccpp` with everything inside.

**Output:**
```
📁 Scanning: C:\Users\david\citizen-compass
✅ Packet saved: citizen-compass.ccpp

================================================================================
CITIZEN COMPASS PROJECT PACKET
================================================================================

📊 PROJECT HEALTH SCORE: 45.2/100

Breakdown:
  • Data Completeness: 68%
  • Viewer Progress: 4%
  • Documentation: 60%

📈 INVENTORY SUMMARY:
  • Ships (total): 232
  • Ships (viewers complete): 1
  • Viewer Progress: 0.4%
  • Data Files: 232
  • Scripts: 4
  • 3D Models: 2
  • Documentation: 3

🚢 SHIP VIEWERS STATUS:
  ✅ arrow: 17 hardpoints

  ⏳ In Progress: 231
     • cutlass-black: 2 files
     • ...
================================================================================
```

### Update an Existing Packet

You've made progress, viewers are done. Re-scan and update:

```bash
python ccpp.py update citizen-compass.ccpp
```

The packet re-scans the project, recalculates scores, and updates itself.

### Inspect a Packet

View what's inside without changing anything:

```bash
python ccpp.py inspect citizen-compass.ccpp
```

Shows the summary, scores, ship status, data inventory.

### Validate a Packet

Check integrity and creation date:

```bash
python ccpp.py validate citizen-compass.ccpp
```

### Extract a Packet

(Future feature) Unpack files from the packet back to disk.

## What's Inside a Packet?

A `.ccpp` file is just a JSON file. You can open it with any text editor:

```json
{
  "metadata": {
    "format": "CCPP-1.0",
    "project": "Citizen Compass",
    "created": "2026-07-28T22:30:45.123456",
    "updated": "2026-07-28T23:15:32.654321",
    "project_path": "C:\\Users\\david\\citizen-compass",
    "checksum": "a1b2c3d4e5f6"
  },
  "inventory": {
    "ships": {
      "arrow": {
        "slug": "arrow",
        "files": ["model.glb", "index.html", "hardpoints.json"],
        "hardpoints_count": 17,
        "viewer_complete": true,
        "model_size": 5242880
      }
    },
    "data_layers": {
      "data-layerrawhardpoints": {
        "file_count": 232,
        "total_size_mb": 15.3,
        "file_types": {".json": 232}
      }
    },
    "scripts": [
      {"name": "ccpp.py", "path": "...", "size": 12500}
    ]
  },
  "crossref": {
    "ships_with_viewers": 1,
    "ships_total": 232,
    "viewers_progress_pct": 0.4
  },
  "scores": {
    "data_completeness": 68.0,
    "viewer_progress": 0.4,
    "documentation": 60,
    "overall_health": 45.2
  }
}
```

## How to Use for AI Handoffs

### Option 1: Pass the Packet to Claude/GPT

1. Create packet: `python ccpp.py create C:\Users\david\citizen-compass`
2. Run inspect to see the summary
3. Paste **the entire .ccpp file contents** into a new AI conversation
4. Say: "Here's my Citizen Compass project state. What should I work on next?"

The AI instantly sees:
- ✅ 232 weapon hardpoint files extracted
- ✅ 1 complete viewer (Arrow)
- ✅ 231 ship viewers not started
- ✅ Overall health: 45.2%

### Option 2: Just Pass the Score Summary

If the file is too large, run:
```bash
python ccpp.py inspect citizen-compass.ccpp
```

Copy-paste the output (it's human-readable) into the AI conversation.

### Option 3: Attach in a Git Commit

Store the `.ccpp` file in your repo:
```bash
git add citizen-compass.ccpp
git commit -m "Project state snapshot: 45.2% health, 1/232 viewers complete"
```

Now every commit includes project state.

## Scoring System

The **overall health score (0-100)** is calculated as:

| Category | Weight | How It's Calculated |
|----------|--------|---------------------|
| **Data Completeness** | 40% | # weapon hardpoint files / 232 |
| **Viewer Progress** | 50% | # complete viewers / 232 |
| **Documentation** | 10% | # of .md files |

**Score Breakdown:**
- **0-20:** Data scattered, no pipeline set up
- **20-40:** Data pipeline built, viewers not started
- **40-60:** Data + some viewers, documentation improving
- **60-80:** Most viewers built, well documented
- **80-100:** Project nearly complete, all documented

## What It Auto-Detects

### Ships
- Folders in `tests/testing-site/ships/<slug>/`
- Files: `model.glb`, `index.html`, `hardpoints.json`
- Marks as "complete" only if all 3 files present

### Data Layers
- Any folder starting with `data-layer*`
- Counts files and calculates total size
- Categorizes by folder name (raw/processed/exports)

### Scripts
- All `.py` files in project root

### Models
- All `.blend` and `.glb` files recursively

### Documentation
- All `.md` files (like `CITIZEN_COMPASS_HANDOFF.md`)

### Cross-References
- Links ships to data files
- Calculates viewer completion %
- Builds data inventory by category

## Workflow Example

**Day 1:** Create packet
```bash
python ccpp.py create C:\Users\david\citizen-compass
# Health: 45.2% (1/232 viewers)
```

**Day 2:** You complete Cutlass Black viewer
```bash
python ccpp.py update citizen-compass.ccpp
# Health: 45.3% (2/232 viewers)
```

**Day 3:** You need a new AI to pick up the work
```bash
python ccpp.py inspect citizen-compass.ccpp
# Copy output, paste into new AI conversation
# AI sees exactly where you left off
```

## Future Enhancements

- `extract` command — Unpack specific files from packet
- Diff between two packets — See exactly what changed
- Archive mode — Compress the entire project + packet
- Progress tracking — Graph viewer completion over time
- AI integration — Packet formats a summary for Claude/GPT automatically

## Troubleshooting

**"Path not found"**
```bash
python ccpp.py create "C:\Users\david\citizen-compass"
# Use quotes if your path has spaces
```

**"No project path in packet"**
- You're trying to update an old packet format
- Create a fresh one: `python ccpp.py create <path>`

**File too large to send to AI**
- Run `python ccpp.py inspect citizen-compass.ccpp`
- Paste the human-readable output instead

---

**Next:** Create your first packet and see your project health score!
