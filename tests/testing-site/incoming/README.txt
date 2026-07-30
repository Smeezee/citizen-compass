Drop finished ship folders in here.

Each folder needs:
  model.glb
  hardpoints.json   (must include a "ship_name" field, e.g. "Aurora ES")

Then run (from the watcher/ folder):
  python match_ship.py          - scan once
  python match_ship.py --watch  - keep watching automatically

If the name is ambiguous (matches several similar ships), it will NOT
guess - it'll list the candidates it considered and skip the folder.
Rename the folder / fix the ship_name field to be more specific and
run it again.
