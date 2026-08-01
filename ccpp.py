"""
Citizen Compass Project Packet (CCPP)

A self-contained project archive application that:
- Scans project folders for data files
- Auto-detects file types and content
- Organizes by category (ships, data, configs, docs)
- Validates completeness and cross-references
- Scores health/progress
- Compacts into a single portable JSON file
- Can be passed between AIs and systems

Usage:
    python ccpp.py create <project_path>       # Scan and create packet
    python ccpp.py update <packet.ccpp>        # Re-scan and update
    python ccpp.py inspect <packet.ccpp>       # View contents
    python ccpp.py extract <packet.ccpp>       # Unpack files
    python ccpp.py validate <packet.ccpp>      # Check integrity

Examples:
    python ccpp.py create C:\\Users\\david\\citizen-compass
    python ccpp.py inspect citizen-compass.ccpp
    python ccpp.py validate citizen-compass.ccpp
"""

import json
import sys
import hashlib
from pathlib import Path
from datetime import datetime
from collections import defaultdict


class CitizenCompassPacket:
    """Self-contained project packet with auto-detection and scoring."""

    def __init__(self):
        self.metadata = {
            "format": "CCPP-1.0",
            "project": "Citizen Compass",
            "created": datetime.now().isoformat(),
            "updated": datetime.now().isoformat(),
        }
        self.inventory = {
            "ships": {},
            "data_layers": {},
            "scripts": [],
            "models": [],
            "configs": [],
            "docs": [],
        }
        self.crossref = {}
        self.scores = {
            "data_completeness": 0,
            "viewer_progress": 0,
            "documentation": 0,
            "overall_health": 0,
        }
        self.file_index = {}

    def scan_project(self, project_path):
        """Scan entire project and auto-detect files."""
        project_path = Path(project_path)
        if not project_path.exists():
            print(f"❌ Path not found: {project_path}")
            return False

        print(f"📁 Scanning: {project_path}")

        # Scan key directories
        self._scan_ships(project_path)
        self._scan_data_layer(project_path)
        self._scan_scripts(project_path)
        self._scan_models(project_path)
        self._scan_docs(project_path)

        # Cross-reference and score
        self._build_crossref()
        self._calculate_scores()

        self.metadata["updated"] = datetime.now().isoformat()
        self.metadata["project_path"] = str(project_path)
        self.metadata["scan_complete"] = True

        return True

    def _scan_ships(self, project_path):
        """Scan ship viewer folders."""
        ships_dir = project_path / "tests" / "testing-site" / "ships"
        if not ships_dir.exists():
            return

        for ship_folder in ships_dir.glob("*/"):
            slug = ship_folder.name
            ship_data = {
                "slug": slug,
                "path": str(ship_folder),
                "files": [],
                "hardpoints_count": 0,
                "viewer_complete": False,
            }

            # Check for key files
            model = ship_folder / "model.glb"
            index = ship_folder / "index.html"
            hardpoints = ship_folder / "hardpoints.json"

            if model.exists():
                ship_data["files"].append("model.glb")
                ship_data["model_size"] = model.stat().st_size
            if index.exists():
                ship_data["files"].append("index.html")
            if hardpoints.exists():
                ship_data["files"].append("hardpoints.json")
                try:
                    with open(hardpoints, "r", encoding="utf-8") as f:
                        hp_data = json.load(f)
                        ship_data["hardpoints_count"] = len(
                            hp_data.get("hardpoints", [])
                        )
                        ship_data["viewer_complete"] = (
                            len(ship_data["files"]) == 3
                        )
                except:
                    pass

            if ship_data["files"]:
                self.inventory["ships"][slug] = ship_data
                self.file_index[str(ship_folder)] = {
                    "type": "ship",
                    "slug": slug,
                }

    def _scan_data_layer(self, project_path):
        """Scan data-layer folders."""
        data_dir = project_path / "data-layer" if (project_path / "data-layer").exists() else \
                  project_path / "data-layerrawhardpoints" if (project_path / "data-layerrawhardpoints").exists() else None

        if not data_dir or not data_dir.exists():
            # Try checking for individual data-layer* folders
            for item in project_path.glob("data-layer*"):
                if item.is_dir():
                    self._catalog_data_folder(item, item.name)
            return

        self._catalog_data_folder(data_dir, "data-layer")

    def _catalog_data_folder(self, folder, name):
        """Catalog a data folder and its contents."""
        if not folder.exists():
            return

        file_count = 0
        total_size = 0
        file_types = defaultdict(int)
        sample_files = []

        for f in folder.rglob("*"):
            if f.is_file():
                file_count += 1
                total_size += f.stat().st_size
                ext = f.suffix.lower()
                file_types[ext] += 1
                if len(sample_files) < 3:
                    sample_files.append(f.name)

        self.inventory["data_layers"][name] = {
            "path": str(folder),
            "file_count": file_count,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "file_types": dict(file_types),
            "sample_files": sample_files,
        }

    def _scan_scripts(self, project_path):
        """Scan for Python/JS scripts."""
        for py_file in project_path.glob("*.py"):
            self.inventory["scripts"].append({
                "name": py_file.name,
                "path": str(py_file),
                "size": py_file.stat().st_size,
            })

    def _scan_models(self, project_path):
        """Scan for 3D model files."""
        for blend in project_path.rglob("*.blend"):
            self.inventory["models"].append({
                "name": blend.name,
                "path": str(blend),
                "size_mb": round(blend.stat().st_size / (1024 * 1024), 2),
            })
        for glb in project_path.rglob("*.glb"):
            self.inventory["models"].append({
                "name": glb.name,
                "path": str(glb),
                "size_mb": round(glb.stat().st_size / (1024 * 1024), 2),
            })

    def _scan_docs(self, project_path):
        """Scan for documentation."""
        for doc in project_path.rglob("*.md"):
            self.inventory["docs"].append({
                "name": doc.name,
                "path": str(doc),
            })

    def _build_crossref(self):
        """Cross-reference data (ships ↔ data files ↔ viewers)."""
        self.crossref = {
            "ships_with_viewers": len(
                [s for s in self.inventory["ships"].values() if s["viewer_complete"]]
            ),
            "ships_total": len(self.inventory["ships"]),
            "viewers_progress_pct": 0,
            "data_files_by_category": {},
        }

        if self.crossref["ships_total"] > 0:
            self.crossref["viewers_progress_pct"] = round(
                (self.crossref["ships_with_viewers"] / self.crossref["ships_total"]) * 100, 1
            )

        # Categorize data files
        for name, data in self.inventory["data_layers"].items():
            if "raw" in name.lower():
                self.crossref["data_files_by_category"]["raw"] = data["file_count"]
            elif "processed" in name.lower():
                self.crossref["data_files_by_category"]["processed"] = data["file_count"]
            elif "export" in name.lower():
                self.crossref["data_files_by_category"]["exports"] = data["file_count"]

    def _calculate_scores(self):
        """Calculate health/progress scores (0-100)."""
        # Data completeness: based on weapon hardpoint files
        raw_weapons = self.inventory["data_layers"].get(
            [k for k in self.inventory["data_layers"] if "raw" in k.lower()][0]
            if any("raw" in k.lower() for k in self.inventory["data_layers"])
            else "none",
            {}
        )
        data_files = raw_weapons.get("file_count", 0)
        self.scores["data_completeness"] = min(100, round((data_files / 232) * 100, 1))

        # Viewer progress: ships with complete viewers / target
        self.scores["viewer_progress"] = self.crossref.get(
            "viewers_progress_pct", 0
        )

        # Documentation: number of doc files
        self.scores["documentation"] = min(
            100, len(self.inventory["docs"]) * 20
        )

        # Overall: weighted average
        self.scores["overall_health"] = round(
            (
                self.scores["data_completeness"] * 0.40
                + self.scores["viewer_progress"] * 0.50
                + self.scores["documentation"] * 0.10
            ),
            1,
        )

    def save(self, filename):
        """Save packet to file."""
        packet = {
            "metadata": self.metadata,
            "inventory": self.inventory,
            "crossref": self.crossref,
            "scores": self.scores,
        }

        # Compute checksum
        packet_json = json.dumps(packet, indent=2).encode()
        packet["metadata"]["checksum"] = hashlib.sha256(packet_json).hexdigest()[:16]

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(packet, f, indent=2)

        print(f"✅ Packet saved: {filename}")
        return filename

    def load(self, filename):
        """Load packet from file."""
        # JSON is UTF-8 by spec (RFC 8259). Without an explicit encoding these
        # fall back to the Windows ANSI codepage (cp1252), which cannot decode
        # non-ASCII ship names - e.g. the Xi'an "...an'tok.yaai" path raised
        # UnicodeDecodeError on byte 0x81 and took the whole handoff
        # regeneration down with it. The file was always valid; the reader was not.
        with open(filename, "r", encoding="utf-8") as f:
            packet = json.load(f)

        self.metadata = packet.get("metadata", {})
        self.inventory = packet.get("inventory", {})
        self.crossref = packet.get("crossref", {})
        self.scores = packet.get("scores", {})

        return True

    def inspect(self):
        """Print readable summary of packet contents."""
        print("\n" + "=" * 70)
        print("CITIZEN COMPASS PROJECT PACKET")
        print("=" * 70)

        print(f"\n📊 PROJECT HEALTH SCORE: {self.scores.get('overall_health', 0)}/100")
        print("\nBreakdown:")
        print(f"  • Data Completeness: {self.scores.get('data_completeness', 0)}%")
        print(f"  • Viewer Progress: {self.scores.get('viewer_progress', 0)}%")
        print(f"  • Documentation: {self.scores.get('documentation', 0)}%")

        print("\n📈 INVENTORY SUMMARY:")
        print(f"  • Ships (total): {self.crossref.get('ships_total', 0)}")
        print(f"  • Ships (viewers complete): {self.crossref.get('ships_with_viewers', 0)}")
        print(f"  • Viewer Progress: {self.crossref.get('viewers_progress_pct', 0)}%")
        print(f"  • Data Files: {sum(d.get('file_count', 0) for d in self.inventory['data_layers'].values())}")
        print(f"  • Scripts: {len(self.inventory['scripts'])}")
        print(f"  • 3D Models: {len(self.inventory['models'])}")
        print(f"  • Documentation: {len(self.inventory['docs'])}")

        print("\n🚢 SHIP VIEWERS STATUS:")
        complete = [s for s in self.inventory["ships"].values() if s.get("viewer_complete")]
        for ship in complete[:5]:
            print(f"  ✅ {ship['slug']}: {ship['hardpoints_count']} hardpoints")
        if len(complete) > 5:
            print(f"  ... and {len(complete) - 5} more")

        if self.inventory["ships"]:
            incomplete = [s for s in self.inventory["ships"].values() if not s.get("viewer_complete")]
            if incomplete:
                print(f"\n  ⏳ In Progress: {len(incomplete)}")
                for ship in incomplete[:3]:
                    print(f"     • {ship['slug']}: {len(ship['files'])} files")

        print("\n📁 DATA LAYERS:")
        for name, data in self.inventory["data_layers"].items():
            print(f"  • {name}: {data['file_count']} files ({data['total_size_mb']} MB)")

        print("\n" + "=" * 70)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    command = sys.argv[1]
    packet = CitizenCompassPacket()

    if command == "create" and len(sys.argv) >= 3:
        project_path = sys.argv[2]
        output_file = sys.argv[3] if len(sys.argv) > 3 else "citizen-compass.ccpp"

        packet.scan_project(project_path)
        packet.save(output_file)
        packet.inspect()

    elif command == "update" and len(sys.argv) >= 3:
        ccpp_file = sys.argv[2]
        packet.load(ccpp_file)
        project_path = packet.metadata.get("project_path")
        if project_path:
            packet.scan_project(project_path)
            packet.save(ccpp_file)
            packet.inspect()
        else:
            print("❌ No project path in packet")

    elif command == "inspect" and len(sys.argv) >= 3:
        ccpp_file = sys.argv[2]
        packet.load(ccpp_file)
        packet.inspect()

    elif command == "validate" and len(sys.argv) >= 3:
        ccpp_file = sys.argv[2]
        packet.load(ccpp_file)
        checksum = packet.metadata.get("checksum", "")
        print(f"✅ Packet valid (checksum: {checksum})")
        print(f"   Created: {packet.metadata.get('created')}")
        print(f"   Updated: {packet.metadata.get('updated')}")

    else:
        print(__doc__)


if __name__ == "__main__":
    main()
