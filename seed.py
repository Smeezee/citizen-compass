"""Seed script for the Citizen Compass Phase 2 database.

Populates manufacturers, ships, dealers, ship_dealer_listings, and
pledge_links from the Phase 1 ship data. Safe to run more than once —
existing rows are matched on their natural key and updated in place
instead of being duplicated.

Usage:
    venv\\Scripts\\python.exe seed.py
    venv\\Scripts\\python.exe seed.py --patch 4.10

Each entry in SHIPS matches this shape (the format handed over from
the Phase 1 data source):

    {
        'manufacturer': 'Aegis Dynamics',
        'name': 'Avenger Stalker',
        'auec_price': 1508220,           # int or None
        'dealers': ['New Deal'],         # list[str], [] if none
        'notes': '',                     # str, '' if none
        'role': 'Fighter',
        'pledge_usd': 60.0,              # float or None
        'pledge_link': 'https://robertsspaceindustries.com/...',  # str or None
        'status': 'purchasable',         # 'purchasable' or 'pledge_only'
    }

DEALERS maps each dealer name used above to its station, as
"Dealer Name (Location)".

`status` is taken from the data as-is rather than re-derived, since a
handful of pledge-only ships (e.g. Basher, UTV) don't follow the
"Concept." / "Flight-ready, no dealer." notes-prefix pattern used
elsewhere.

Confidence defaults to "verified" for every row, except where the
notes themselves flag an unresolved discrepancy (two sources
disagree, a price needs rechecking, a dealer is an unconfirmed guess)
— those are stamped "low" instead. See CONFLICT_MARKERS below; the
run summary lists exactly which ships were downgraded and why so it
can be reviewed and overridden.
"""

import argparse
import re
from typing import Optional

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Dealer, Manufacturer, Patch, PledgeLink, Ship, ShipDealerListing

CONFLICT_MARKERS = (
    "unresolved",
    "not verified",
    "second source shows",
    "another source shows",
    "other source shows",
    "snapshot shows",
    "verify current price",
)

SHIPS = [
    {'manufacturer': 'Aegis Dynamics', 'name': 'Avenger Stalker', 'auec_price': 1508220, 'dealers': ['New Deal'], 'notes': '', 'role': 'Fighter', 'pledge_usd': 60.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/aegis-avenger/Avenger-Stalker', 'status': 'purchasable'},
    {'manufacturer': 'Aegis Dynamics', 'name': 'Avenger Titan', 'auec_price': 1290366, 'dealers': ['New Deal', "Teach's"], 'notes': '', 'role': 'Cargo', 'pledge_usd': 60.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/aegis-avenger/Avenger-Titan', 'status': 'purchasable'},
    {'manufacturer': 'Aegis Dynamics', 'name': 'Avenger Titan Renegade', 'auec_price': 1759590, 'dealers': ['New Deal'], 'notes': '', 'role': 'Cargo', 'pledge_usd': 75.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/aegis-avenger/Avenger-Titan-Renegade', 'status': 'purchasable'},
    {'manufacturer': 'Aegis Dynamics', 'name': 'Avenger Warlock', 'auec_price': 2136645, 'dealers': ['New Deal'], 'notes': '', 'role': 'Interdiction', 'pledge_usd': 85.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/aegis-avenger/Avenger-Warlock', 'status': 'purchasable'},
    {'manufacturer': 'Aegis Dynamics', 'name': 'Eclipse', 'auec_price': 7541100, 'dealers': ['New Deal'], 'notes': '', 'role': 'Bomber', 'pledge_usd': 300.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/eclipse/Eclipse', 'status': 'purchasable'},
    {'manufacturer': 'Aegis Dynamics', 'name': 'Gladius', 'auec_price': 2262330, 'dealers': ['New Deal', "Teach's"], 'notes': '', 'role': 'Fighter', 'pledge_usd': 90.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/gladius/Gladius', 'status': 'purchasable'},
    {'manufacturer': 'Aegis Dynamics', 'name': 'Gladius Valiant', 'auec_price': 2765070, 'dealers': ['New Deal'], 'notes': '', 'role': 'Racing', 'pledge_usd': 110.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/gladius/Gladius-Valiant', 'status': 'purchasable'},
    {'manufacturer': 'Aegis Dynamics', 'name': 'Hammerhead', 'auec_price': 34466568, 'dealers': ['New Deal'], 'notes': '', 'role': 'Capital/Multi-crew', 'pledge_usd': 725.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/hammerhead/Hammerhead', 'status': 'purchasable'},
    {'manufacturer': 'Aegis Dynamics', 'name': 'Reclaimer', 'auec_price': 30164400, 'dealers': ['New Deal', "Teach's"], 'notes': "Teach's version is a special loadout (***)", 'role': 'Salvage', 'pledge_usd': 400.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/reclaimer/Reclaimer', 'status': 'purchasable'},
    {'manufacturer': 'Aegis Dynamics', 'name': 'Redeemer', 'auec_price': 9803430, 'dealers': ['New Deal'], 'notes': '', 'role': 'Fighter', 'pledge_usd': 330.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/redeemer/Redeemer', 'status': 'purchasable'},
    {'manufacturer': 'Aegis Dynamics', 'name': 'Retaliator', 'auec_price': 7541100, 'dealers': ['New Deal'], 'notes': '', 'role': 'Multi-role', 'pledge_usd': 175.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/aegis-retaliator/Retaliator', 'status': 'purchasable'},
    {'manufacturer': 'Aegis Dynamics', 'name': 'Sabre', 'auec_price': 4273290, 'dealers': ['New Deal'], 'notes': '', 'role': 'Fighter', 'pledge_usd': 170.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/sabre/Sabre', 'status': 'purchasable'},
    {'manufacturer': 'Aegis Dynamics', 'name': 'Sabre Comet', 'auec_price': 4650345, 'dealers': ['New Deal'], 'notes': '', 'role': 'Fighter', 'pledge_usd': 185.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/sabre/Sabre-Comet', 'status': 'purchasable'},
    {'manufacturer': 'Aegis Dynamics', 'name': 'Sabre Firebird', 'auec_price': 5580414, 'dealers': ['New Deal'], 'notes': '', 'role': 'Fighter', 'pledge_usd': 185.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/sabre/Sabre-Firebird', 'status': 'purchasable'},
    {'manufacturer': 'Aegis Dynamics', 'name': 'Sabre Peregrine', 'auec_price': 3845961, 'dealers': ['New Deal'], 'notes': '', 'role': 'Racing', 'pledge_usd': 185.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/sabre/Sabre-Peregrine', 'status': 'purchasable'},
    {'manufacturer': 'Aegis Dynamics', 'name': 'Vanguard Harbinger', 'auec_price': 8200400, 'dealers': ['New Deal'], 'notes': '', 'role': 'Bomber', 'pledge_usd': 290.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/vanguard/Vanguard-Harbinger', 'status': 'purchasable'},
    {'manufacturer': 'Aegis Dynamics', 'name': 'Vanguard Hoplite', 'auec_price': 6645250, 'dealers': ['New Deal'], 'notes': '', 'role': 'Cargo', 'pledge_usd': 240.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/vanguard/Vanguard-Hoplite', 'status': 'purchasable'},
    {'manufacturer': 'Aegis Dynamics', 'name': 'Vanguard Sentinel', 'auec_price': 7776700, 'dealers': ['New Deal'], 'notes': '', 'role': 'Fighter', 'pledge_usd': 275.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/vanguard/Vanguard-Sentinel', 'status': 'purchasable'},
    {'manufacturer': 'Aegis Dynamics', 'name': 'Vanguard Warden', 'auec_price': 7354900, 'dealers': ['New Deal'], 'notes': '', 'role': 'Fighter', 'pledge_usd': 260.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/vanguard/Vanguard-Warden', 'status': 'purchasable'},
    {'manufacturer': 'Anvil Aerospace', 'name': 'Arrow', 'auec_price': 1984500, 'dealers': ['Astro Armada', "Teach's"], 'notes': '', 'role': 'Fighter', 'pledge_usd': 75.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/anvil-arrow/Arrow', 'status': 'purchasable'},
    {'manufacturer': 'Anvil Aerospace', 'name': 'Asgard', 'auec_price': 17860500, 'dealers': ['Astro Armada'], 'notes': '', 'role': 'Cargo', 'pledge_usd': 350.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/anvil-asgard/Asgard', 'status': 'purchasable'},
    {'manufacturer': 'Anvil Aerospace', 'name': 'Ballista', 'auec_price': 1407672, 'dealers': ['Astro Armada', 'New Deal'], 'notes': '', 'role': 'Ground Vehicle', 'pledge_usd': 140.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/anvil-ballista/Ballista', 'status': 'purchasable'},
    {'manufacturer': 'Anvil Aerospace', 'name': 'C8 Pisces', 'auec_price': 745290, 'dealers': ['Astro Armada'], 'notes': '', 'role': 'Exploration', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/anvil-pisces/C8-Pisces', 'status': 'purchasable'},
    {'manufacturer': 'Anvil Aerospace', 'name': 'C8R Pisces Rescue', 'auec_price': 555660, 'dealers': ['Astro Armada'], 'notes': '', 'role': 'Medical', 'pledge_usd': 65.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/anvil-pisces/C8R-Pisces', 'status': 'purchasable'},
    {'manufacturer': 'Anvil Aerospace', 'name': 'C8X Pisces Expedition', 'auec_price': 515970, 'dealers': ['Astro Armada'], 'notes': '', 'role': 'Exploration', 'pledge_usd': 45.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/anvil-pisces/C8X-Pisces-Expedition', 'status': 'purchasable'},
    {'manufacturer': 'Anvil Aerospace', 'name': 'Carrack', 'auec_price': 34398000, 'dealers': ['Astro Armada'], 'notes': '', 'role': 'Exploration', 'pledge_usd': 600.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/carrack/Carrack', 'status': 'purchasable'},
    {'manufacturer': 'Anvil Aerospace', 'name': 'Centurion', 'auec_price': 1106028, 'dealers': ['Astro Armada', 'New Deal'], 'notes': '', 'role': 'Ground Vehicle', 'pledge_usd': 110.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/centurion/Centurion', 'status': 'purchasable'},
    {'manufacturer': 'Anvil Aerospace', 'name': 'F7C Hornet Mk I', 'auec_price': 2910600, 'dealers': ['Astro Armada'], 'notes': '', 'role': 'Fighter', 'pledge_usd': 125.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/anvil-hornet/F7C-Hornet-Mk-I', 'status': 'purchasable'},
    {'manufacturer': 'Anvil Aerospace', 'name': 'F7C Hornet Mk II', 'auec_price': 4650345, 'dealers': ['Astro Armada', 'New Deal'], 'notes': '', 'role': 'Fighter', 'pledge_usd': 175.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/anvil-hornet-mkii/F7C-Hornet-Mk-II', 'status': 'purchasable'},
    {'manufacturer': 'Anvil Aerospace', 'name': 'F7C Hornet Wildfire Mk I', 'auec_price': 4630500, 'dealers': ['Astro Armada'], 'notes': '', 'role': 'Fighter', 'pledge_usd': 175.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/anvil-hornet/F7C-Hornet-Wildfire-Mk-I', 'status': 'purchasable'},
    {'manufacturer': 'Anvil Aerospace', 'name': 'F7C-M Super Hornet Mk I', 'auec_price': 4762800, 'dealers': ['Astro Armada'], 'notes': '', 'role': 'Fighter', 'pledge_usd': 180.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/anvil-hornet/F7C-M-Super-Hornet-Mk-I', 'status': 'purchasable'},
    {'manufacturer': 'Anvil Aerospace', 'name': 'F7C-R Hornet Tracker Mk I', 'auec_price': 3210480, 'dealers': ['Astro Armada'], 'notes': '', 'role': 'Exploration', 'pledge_usd': 150.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/anvil-hornet/F7C-R-Hornet-Tracker-Mk-I', 'status': 'purchasable'},
    {'manufacturer': 'Anvil Aerospace', 'name': 'F7C-R Hornet Tracker Mk II', 'auec_price': 4882858, 'dealers': ['New Deal'], 'notes': '', 'role': 'Exploration', 'pledge_usd': 185.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/anvil-hornet-mkii/F7C-R-Hornet-Tracker-Mk-II', 'status': 'purchasable'},
    {'manufacturer': 'Anvil Aerospace', 'name': 'F7C-S Hornet Ghost Mk I', 'auec_price': 3307500, 'dealers': ['Astro Armada'], 'notes': '', 'role': 'Fighter', 'pledge_usd': 140.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/anvil-hornet/F7C-S-Hornet-Ghost-Mk-I', 'status': 'purchasable'},
    {'manufacturer': 'Anvil Aerospace', 'name': 'F7C-S Hornet Ghost Mk II', 'auec_price': 5115370, 'dealers': ['New Deal'], 'notes': '', 'role': 'Fighter', 'pledge_usd': 185.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/anvil-hornet-mkii/F7C-S-Hornet-Ghost-Mk-II', 'status': 'purchasable'},
    {'manufacturer': 'Anvil Aerospace', 'name': 'Gladiator', 'auec_price': 4365900, 'dealers': ['Astro Armada'], 'notes': '', 'role': 'Bomber', 'pledge_usd': 165.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/anvil-gladiator/Gladiator', 'status': 'purchasable'},
    {'manufacturer': 'Anvil Aerospace', 'name': 'Hawk', 'auec_price': 2646000, 'dealers': ['Astro Armada'], 'notes': '', 'role': 'Fighter', 'pledge_usd': 100.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/hawk/Hawk', 'status': 'purchasable'},
    {'manufacturer': 'Anvil Aerospace', 'name': 'Hurricane', 'auec_price': 5556600, 'dealers': ['Astro Armada'], 'notes': '', 'role': 'Fighter', 'pledge_usd': 210.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/Standalone-Ships/Hurricane', 'status': 'purchasable'},
    {'manufacturer': 'Anvil Aerospace', 'name': 'Paladin', 'auec_price': 15876000, 'dealers': ['Astro Armada'], 'notes': '', 'role': 'Fighter', 'pledge_usd': 350.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/paladin/Paladin', 'status': 'purchasable'},
    {'manufacturer': 'Anvil Aerospace', 'name': 'Spartan', 'auec_price': 804384, 'dealers': ['Astro Armada', 'New Deal'], 'notes': '', 'role': 'Ground Vehicle', 'pledge_usd': 80.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/spartan/Spartan', 'status': 'purchasable'},
    {'manufacturer': 'Anvil Aerospace', 'name': 'Terrapin', 'auec_price': 5433120, 'dealers': ['Astro Armada', "Teach's"], 'notes': '', 'role': 'Exploration', 'pledge_usd': 220.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/terrapin/Terrapin', 'status': 'purchasable'},
    {'manufacturer': 'Anvil Aerospace', 'name': 'Terrapin Medic', 'auec_price': 5704770, 'dealers': ['Astro Armada'], 'notes': '', 'role': 'Medical', 'pledge_usd': 220.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/terrapin/Terrapin-Medic', 'status': 'purchasable'},
    {'manufacturer': 'Anvil Aerospace', 'name': 'Valkyrie', 'auec_price': 19845000, 'dealers': ['Astro Armada'], 'notes': '', 'role': 'Cargo', 'pledge_usd': 375.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/anvil-valkyrie/Valkyrie', 'status': 'purchasable'},
    {'manufacturer': 'Argo Astronautics', 'name': 'ATLS', 'auec_price': 71820, 'dealers': ['Astro Armada', 'Crusader Showroom', 'New Deal', "Teach's", 'Buy & Fly'], 'notes': '', 'role': 'Ground Vehicle', 'pledge_usd': 40.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/atls/ATLS', 'status': 'purchasable'},
    {'manufacturer': 'Argo Astronautics', 'name': 'ATLS GEO', 'auec_price': 86184, 'dealers': ['Astro Armada', 'Crusader Showroom', 'New Deal', "Teach's", 'Buy & Fly'], 'notes': '', 'role': 'Mining', 'pledge_usd': 45.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/atls/ATLS-GEO', 'status': 'purchasable'},
    {'manufacturer': 'Argo Astronautics', 'name': 'CSV-SM', 'auec_price': 359100, 'dealers': ['Crusader Showroom', 'New Deal', 'Buy & Fly'], 'notes': '', 'role': 'Cargo', 'pledge_usd': 45.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/csv/CSV-SM', 'status': 'purchasable'},
    {'manufacturer': 'Argo Astronautics', 'name': 'MOLE', 'auec_price': 8483738, 'dealers': ['New Deal', "Teach's"], 'notes': "Teach's version is a special loadout (***)", 'role': 'Mining', 'pledge_usd': 315.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/argo-mole/MOLE', 'status': 'purchasable'},
    {'manufacturer': 'Argo Astronautics', 'name': 'MOTH', 'auec_price': 8483738, 'dealers': ['New Deal'], 'notes': 'New addition in 4.9.0', 'role': 'Salvage', 'pledge_usd': 315.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/moth/MOTH', 'status': 'purchasable'},
    {'manufacturer': 'Argo Astronautics', 'name': 'MPUV Cargo', 'auec_price': 314213, 'dealers': ['New Deal'], 'notes': '', 'role': 'Cargo', 'pledge_usd': 35.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/argo/MPUV-Cargo', 'status': 'purchasable'},
    {'manufacturer': 'Argo Astronautics', 'name': 'MPUV Personnel', 'auec_price': 359100, 'dealers': ['New Deal'], 'notes': '', 'role': 'Cargo', 'pledge_usd': 40.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/argo/MPUV-Personnel', 'status': 'purchasable'},
    {'manufacturer': 'Argo Astronautics', 'name': 'MPUV Tractor', 'auec_price': 395010, 'dealers': ['New Deal', "Teach's"], 'notes': '', 'role': 'Cargo', 'pledge_usd': 40.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/argo/MPUV-Tractor', 'status': 'purchasable'},
    {'manufacturer': 'Argo Astronautics', 'name': 'RAFT', 'auec_price': 3366563, 'dealers': ['New Deal', "Teach's"], 'notes': '', 'role': 'Cargo', 'pledge_usd': 190.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/raft/RAFT', 'status': 'purchasable'},
    {'manufacturer': 'Argo Astronautics', 'name': 'SRV', 'auec_price': 3770550, 'dealers': ['New Deal', "Teach's"], 'notes': '', 'role': 'Search & Rescue', 'pledge_usd': 165.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/argo-srv/SRV', 'status': 'purchasable'},
    {'manufacturer': 'Banu (Souli)', 'name': 'Defender', 'auec_price': 6237000, 'dealers': ['Astro Armada'], 'notes': '', 'role': 'Fighter', 'pledge_usd': 220.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/defender/Defender', 'status': 'purchasable'},
    {'manufacturer': 'Consolidated Outland', 'name': 'HoverQuad', 'auec_price': 53865, 'dealers': ['Astro Armada', 'New Deal'], 'notes': '', 'role': 'Ground Vehicle', 'pledge_usd': 30.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/hoverquad/HoverQuad', 'status': 'purchasable'},
    {'manufacturer': 'Consolidated Outland', 'name': 'Mustang Alpha', 'auec_price': 610470, 'dealers': ['New Deal', "Teach's"], 'notes': '', 'role': 'Cargo', 'pledge_usd': 30.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/mustang/Mustang-Alpha', 'status': 'purchasable'},
    {'manufacturer': 'Consolidated Outland', 'name': 'Mustang Beta', 'auec_price': 622440, 'dealers': ['New Deal'], 'notes': '', 'role': 'Exploration', 'pledge_usd': 40.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/mustang/Mustang-Beta', 'status': 'purchasable'},
    {'manufacturer': 'Consolidated Outland', 'name': 'Mustang Delta', 'auec_price': 1228500, 'dealers': ['Astro Armada'], 'notes': '', 'role': 'Fighter', 'pledge_usd': 65.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/mustang/Mustang-Delta', 'status': 'purchasable'},
    {'manufacturer': 'Consolidated Outland', 'name': 'Mustang Gamma', 'auec_price': 1178100, 'dealers': ['Astro Armada'], 'notes': '', 'role': 'Racing', 'pledge_usd': 55.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/mustang/Mustang-Gamma', 'status': 'purchasable'},
    {'manufacturer': 'Consolidated Outland', 'name': 'Nomad', 'auec_price': 1436400, 'dealers': ['New Deal', "Teach's"], 'notes': "Teach's version is a special loadout (***)", 'role': 'Cargo', 'pledge_usd': 80.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/nomad/Nomad', 'status': 'purchasable'},
    {'manufacturer': 'Crusader Industries', 'name': 'A1 Spirit', 'auec_price': 4961250, 'dealers': ['Crusader Showroom'], 'notes': '', 'role': 'Bomber', 'pledge_usd': 200.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/spirit/A1-Spirit', 'status': 'purchasable'},
    {'manufacturer': 'Crusader Industries', 'name': 'A2 Hercules Starlifter', 'auec_price': 37800200, 'dealers': ['Crusader Showroom', "Teach's"], 'notes': '', 'role': 'Bomber', 'pledge_usd': 750.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/crusader-starlifter/A2-Hercules', 'status': 'purchasable'},
    {'manufacturer': 'Crusader Industries', 'name': 'Ares Inferno', 'auec_price': 4725000, 'dealers': ['Crusader Showroom'], 'notes': '', 'role': 'Fighter', 'pledge_usd': 250.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/crusader-ares/Ares-Inferno', 'status': 'purchasable'},
    {'manufacturer': 'Crusader Industries', 'name': 'Ares Ion', 'auec_price': 4725000, 'dealers': ['Crusader Showroom'], 'notes': '', 'role': 'Fighter', 'pledge_usd': 250.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/crusader-ares/Ares-Ion', 'status': 'purchasable'},
    {'manufacturer': 'Crusader Industries', 'name': 'C1 Spirit', 'auec_price': 3118500, 'dealers': ['Crusader Showroom'], 'notes': '', 'role': 'Cargo', 'pledge_usd': 125.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/spirit/C1-Spirit', 'status': 'purchasable'},
    {'manufacturer': 'Crusader Industries', 'name': 'C2 Hercules Starlifter', 'auec_price': 18900000, 'dealers': ['Astro Armada', 'Crusader Showroom'], 'notes': '', 'role': 'Cargo', 'pledge_usd': 400.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/crusader-starlifter/C2-Hercules', 'status': 'purchasable'},
    {'manufacturer': 'Crusader Industries', 'name': 'Intrepid', 'auec_price': 1173060, 'dealers': ['Astro Armada', 'Crusader Showroom', 'New Deal'], 'notes': '', 'role': 'Cargo', 'pledge_usd': 65.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/Standalone-Ships/Intrepid', 'status': 'purchasable'},
    {'manufacturer': 'Crusader Industries', 'name': 'M2 Hercules Starlifter', 'auec_price': 28009800, 'dealers': ['Crusader Showroom', 'New Deal'], 'notes': '', 'role': 'Cargo', 'pledge_usd': 520.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/crusader-starlifter/M2-Hercules', 'status': 'purchasable'},
    {'manufacturer': 'Crusader Industries', 'name': 'Mercury Star Runner', 'auec_price': 12285000, 'dealers': ['Crusader Showroom'], 'notes': '', 'role': 'Data', 'pledge_usd': 260.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/crusader-mercury-star-runner/Mercury', 'status': 'purchasable'},
    {'manufacturer': 'Drake Interplanetary', 'name': 'Buccaneer', 'auec_price': 1580040, 'dealers': ['New Deal', 'Buy & Fly'], 'notes': '', 'role': 'Fighter', 'pledge_usd': 110.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/drake-buccaneer/Buccaneer', 'status': 'purchasable'},
    {'manufacturer': 'Drake Interplanetary', 'name': 'Caterpillar', 'auec_price': 11850300, 'dealers': ['New Deal'], 'notes': '', 'role': 'Cargo', 'pledge_usd': 330.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/drake-caterpillar/Caterpillar', 'status': 'purchasable'},
    {'manufacturer': 'Drake Interplanetary', 'name': 'Clipper', 'auec_price': 3619728, 'dealers': ['New Deal', "Teach's", 'Buy & Fly'], 'notes': '', 'role': 'Multi-role', 'pledge_usd': 150.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/clipper/Clipper', 'status': 'purchasable'},
    {'manufacturer': 'Drake Interplanetary', 'name': 'Corsair', 'auec_price': 6224400, 'dealers': ['New Deal'], 'notes': '', 'role': 'Exploration', 'pledge_usd': 250.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/drake-corsair/Corsair', 'status': 'purchasable'},
    {'manufacturer': 'Drake Interplanetary', 'name': 'Cutlass Black', 'auec_price': 2010960, 'dealers': ['New Deal'], 'notes': '', 'role': 'Fighter', 'pledge_usd': 105.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/drake-cutlass/Cutlass-Black', 'status': 'purchasable'},
    {'manufacturer': 'Drake Interplanetary', 'name': 'Cutlass Blue', 'auec_price': 3519180, 'dealers': ['New Deal'], 'notes': '', 'role': 'Interdiction', 'pledge_usd': 155.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/drake-cutlass/Cutlass-Blue', 'status': 'purchasable'},
    {'manufacturer': 'Drake Interplanetary', 'name': 'Cutlass Red', 'auec_price': 2714796, 'dealers': ['New Deal', 'Buy & Fly'], 'notes': '', 'role': 'Medical', 'pledge_usd': 130.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/drake-cutlass/Cutlass-Red', 'status': 'purchasable'},
    {'manufacturer': 'Drake Interplanetary', 'name': 'Cutlass Steel', 'auec_price': 3797483, 'dealers': ['New Deal'], 'notes': '', 'role': 'Cargo', 'pledge_usd': 170.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/drake-cutlass/Cutlass-Steel', 'status': 'purchasable'},
    {'manufacturer': 'Drake Interplanetary', 'name': 'Cutter', 'auec_price': 603288, 'dealers': ['New Deal', "Teach's"], 'notes': '', 'role': 'Exploration', 'pledge_usd': 45.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/cutter/Cutter', 'status': 'purchasable'},
    {'manufacturer': 'Drake Interplanetary', 'name': 'Cutter Rambler', 'auec_price': 703836, 'dealers': ['New Deal'], 'notes': '', 'role': 'Exploration', 'pledge_usd': 55.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/cutter/Cutter-Rambler', 'status': 'purchasable'},
    {'manufacturer': 'Drake Interplanetary', 'name': 'Cutter Scout', 'auec_price': 670320, 'dealers': ['New Deal'], 'notes': '', 'role': 'Exploration', 'pledge_usd': 50.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/cutter/Cutter-Scout', 'status': 'purchasable'},
    {'manufacturer': 'Drake Interplanetary', 'name': 'Dragonfly', 'auec_price': 325584, 'dealers': ['New Deal', 'Buy & Fly'], 'notes': '', 'role': 'Racing', 'pledge_usd': 40.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/drake-dragonfly/Dragonfly-Black', 'status': 'purchasable'},
    {'manufacturer': 'Drake Interplanetary', 'name': 'Golem', 'auec_price': 1005480, 'dealers': ['New Deal', "Teach's", 'Buy & Fly'], 'notes': "Teach's version is a special loadout (***)", 'role': 'Mining', 'pledge_usd': 60.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/golem/Golem', 'status': 'purchasable'},
    {'manufacturer': 'Drake Interplanetary', 'name': 'Herald', 'auec_price': 1220940, 'dealers': ['New Deal'], 'notes': '', 'role': 'Data', 'pledge_usd': 90.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/herald/Herald', 'status': 'purchasable'},
    {'manufacturer': 'Drake Interplanetary', 'name': 'Mule', 'auec_price': 64638, 'dealers': ['New Deal', "Teach's"], 'notes': '', 'role': 'Cargo', 'pledge_usd': 45.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/mule/Mule', 'status': 'purchasable'},
    {'manufacturer': 'Drake Interplanetary', 'name': 'Vulture', 'auec_price': 2513700, 'dealers': ['New Deal', "Teach's", 'Buy & Fly'], 'notes': "Teach's version is a special loadout (***)", 'role': 'Salvage', 'pledge_usd': 175.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/drake-vulture/Vulture', 'status': 'purchasable'},
    {'manufacturer': 'Esperia', 'name': 'Blade', 'auec_price': 7796250, 'dealers': ['Astro Armada'], 'notes': '', 'role': 'Fighter', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/vanduul-blade/Blade', 'status': 'purchasable'},
    {'manufacturer': 'Esperia', 'name': 'Prowler', 'auec_price': 18711000, 'dealers': ['Astro Armada'], 'notes': '', 'role': 'Cargo', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/prowler/Prowler', 'status': 'purchasable'},
    {'manufacturer': 'Esperia', 'name': 'Prowler Utility', 'auec_price': 16839000, 'dealers': ['Astro Armada'], 'notes': '', 'role': 'Cargo', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/prowler/Prowler-Utility', 'status': 'purchasable'},
    {'manufacturer': 'Esperia', 'name': 'Stinger', 'auec_price': 8930250, 'dealers': ["Teach's"], 'notes': '', 'role': 'Fighter', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/stinger/Stinger', 'status': 'purchasable'},
    {'manufacturer': 'Esperia', 'name': 'Talon', 'auec_price': 3260250, 'dealers': ['Astro Armada'], 'notes': '', 'role': 'Fighter', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/talon/Talon', 'status': 'purchasable'},
    {'manufacturer': 'Esperia', 'name': 'Talon Shrike', 'auec_price': 3260250, 'dealers': ['Astro Armada'], 'notes': '', 'role': 'Fighter', 'pledge_usd': 115.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/talon/Talon-Shrike', 'status': 'purchasable'},
    {'manufacturer': 'Gatac Manufacture', 'name': 'Syulen', 'auec_price': 2082500, 'dealers': ['Astro Armada'], 'notes': '', 'role': 'Exploration', 'pledge_usd': 70.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/syulen/Syulen', 'status': 'purchasable'},
    {'manufacturer': "Grey's Market", 'name': 'Shiv', 'auec_price': 5556600, 'dealers': ["Teach's"], 'notes': '', 'role': 'Fighter', 'pledge_usd': 150.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/shiv/Shiv', 'status': 'purchasable'},
    {'manufacturer': 'Greycat Industrial', 'name': 'MDC', 'auec_price': 127575, 'dealers': ['New Deal', 'Buy & Fly'], 'notes': '', 'role': 'Ground Vehicle', 'pledge_usd': 50.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/mdc/MDC', 'status': 'purchasable'},
    {'manufacturer': 'Greycat Industrial', 'name': 'MTC', 'auec_price': 75600, 'dealers': ['New Deal', 'Buy & Fly'], 'notes': '', 'role': 'Ground Vehicle', 'pledge_usd': 50.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/mtc/MTC', 'status': 'purchasable'},
    {'manufacturer': 'Greycat Industrial', 'name': 'PTV', 'auec_price': 28350, 'dealers': ['Astro Armada', "Teach's"], 'notes': '', 'role': 'Ground Vehicle', 'pledge_usd': 15.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/ptv/PTV', 'status': 'purchasable'},
    {'manufacturer': 'Greycat Industrial', 'name': 'ROC', 'auec_price': 98753, 'dealers': ['New Deal', "Teach's"], 'notes': '', 'role': 'Mining', 'pledge_usd': 55.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/roc/ROC', 'status': 'purchasable'},
    {'manufacturer': 'Greycat Industrial', 'name': 'ROC-DS', 'auec_price': 134663, 'dealers': ['New Deal', "Teach's"], 'notes': '', 'role': 'Mining', 'pledge_usd': 75.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/roc/ROC-DS', 'status': 'purchasable'},
    {'manufacturer': 'Greycat Industrial', 'name': 'STV', 'auec_price': 75600, 'dealers': ['Astro Armada', 'Buy & Fly'], 'notes': '', 'role': 'Racing', 'pledge_usd': 40.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/stv/STV', 'status': 'purchasable'},
    {'manufacturer': 'Kruger Intergalactic', 'name': 'L-21 Wolf', 'auec_price': 2381400, 'dealers': ['Astro Armada'], 'notes': '', 'role': 'Fighter', 'pledge_usd': 100.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/wolf/L-21-Wolf', 'status': 'purchasable'},
    {'manufacturer': 'Kruger Intergalactic', 'name': 'P-52 Merlin', 'auec_price': 283500, 'dealers': ['Astro Armada'], 'notes': '', 'role': 'Fighter', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/p52-merlin/P-52-Merlin', 'status': 'purchasable'},
    {'manufacturer': 'Kruger Intergalactic', 'name': 'P-72 Archimedes', 'auec_price': 449820, 'dealers': ['Astro Armada'], 'notes': '', 'role': 'Racing', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/p72-archimedes/P-72-Archimedes', 'status': 'purchasable'},
    {'manufacturer': 'MISC', 'name': 'Fortune', 'auec_price': 1795500, 'dealers': ['New Deal', "Teach's", 'Buy & Fly'], 'notes': "Teach's version is a special loadout (***)", 'role': 'Salvage', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/fortune/Fortune', 'status': 'purchasable'},
    {'manufacturer': 'MISC', 'name': 'Freelancer', 'auec_price': 2962575, 'dealers': ['New Deal'], 'notes': '', 'role': 'Cargo', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/misc-freelancer/Freelancer', 'status': 'purchasable'},
    {'manufacturer': 'MISC', 'name': 'Freelancer DUR', 'auec_price': 3151103, 'dealers': ['New Deal', "Teach's"], 'notes': '', 'role': 'Exploration', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/misc-freelancer/Freelancer-DUR', 'status': 'purchasable'},
    {'manufacturer': 'MISC', 'name': 'Freelancer MAX', 'auec_price': 4039875, 'dealers': ['New Deal'], 'notes': '', 'role': 'Cargo', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/misc-freelancer/Freelancer-MAX', 'status': 'purchasable'},
    {'manufacturer': 'MISC', 'name': 'Freelancer MIS', 'auec_price': 4713188, 'dealers': ['New Deal'], 'notes': '', 'role': 'Fighter', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/misc-freelancer/Freelancer-MIS', 'status': 'purchasable'},
    {'manufacturer': 'MISC', 'name': 'Hull A', 'auec_price': 1615950, 'dealers': ['New Deal', "Teach's"], 'notes': '', 'role': 'Cargo', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/hull/Hull-A', 'status': 'purchasable'},
    {'manufacturer': 'MISC', 'name': 'Hull C', 'auec_price': 15710625, 'dealers': ['New Deal'], 'notes': '', 'role': 'Cargo', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/hull/Hull-C', 'status': 'purchasable'},
    {'manufacturer': 'MISC', 'name': 'Prospector', 'auec_price': 2783025, 'dealers': ['New Deal', 'Buy & Fly'], 'notes': '', 'role': 'Mining', 'pledge_usd': 155.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/misc-prospector/Prospector', 'status': 'purchasable'},
    {'manufacturer': 'MISC', 'name': 'Reliant Kore', 'auec_price': 1633905, 'dealers': ['New Deal', "Teach's"], 'notes': '', 'role': 'Cargo', 'pledge_usd': 65.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/reliant/Reliant-Kore', 'status': 'purchasable'},
    {'manufacturer': 'MISC', 'name': 'Reliant Mako', 'auec_price': 2388015, 'dealers': ['New Deal'], 'notes': '', 'role': 'Data', 'pledge_usd': 95.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/reliant/Reliant-Mako', 'status': 'purchasable'},
    {'manufacturer': 'MISC', 'name': 'Reliant Sen', 'auec_price': 2136645, 'dealers': ['New Deal'], 'notes': '', 'role': 'Data', 'pledge_usd': 85.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/reliant/Reliant-Sen', 'status': 'purchasable'},
    {'manufacturer': 'MISC', 'name': 'Reliant Tana', 'auec_price': 1885275, 'dealers': ['New Deal'], 'notes': '', 'role': 'Fighter', 'pledge_usd': 75.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/reliant/Reliant-Tana', 'status': 'purchasable'},
    {'manufacturer': 'MISC', 'name': 'Starfarer', 'auec_price': 13891500, 'dealers': ['New Deal', "Teach's"], 'notes': "Teach's version is a special loadout (***)", 'role': 'Refuel', 'pledge_usd': 300.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/misc-starfarer/Starfarer', 'status': 'purchasable'},
    {'manufacturer': 'MISC', 'name': 'Starfarer Gemini', 'auec_price': 14244300, 'dealers': ['New Deal'], 'notes': '', 'role': 'Refuel', 'pledge_usd': 340.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/misc-starfarer/Starfarer-Gemini', 'status': 'purchasable'},
    {'manufacturer': 'MISC', 'name': 'Starlancer MAX', 'auec_price': 8379000, 'dealers': ['Astro Armada', 'New Deal'], 'notes': '', 'role': 'Cargo', 'pledge_usd': 250.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/starlancer/Starlancer-MAX', 'status': 'purchasable'},
    {'manufacturer': 'MISC', 'name': 'Starlancer TAC', 'auec_price': 13381200, 'dealers': ['Astro Armada', 'New Deal'], 'notes': '', 'role': 'Fighter', 'pledge_usd': 375.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/starlancer/Starlancer-TAC', 'status': 'purchasable'},
    {'manufacturer': 'Mirai', 'name': 'Fury', 'auec_price': 691268, 'dealers': ['Astro Armada', 'New Deal'], 'notes': '', 'role': 'Fighter', 'pledge_usd': 55.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/fury/Fury', 'status': 'purchasable'},
    {'manufacturer': 'Mirai', 'name': 'Fury LX', 'auec_price': 824670, 'dealers': ['Astro Armada'], 'notes': '', 'role': 'Racing', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/fury/Fury-LX', 'status': 'purchasable'},
    {'manufacturer': 'Mirai', 'name': 'Fury MX', 'auec_price': 691268, 'dealers': ['New Deal'], 'notes': '', 'role': 'Bomber', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/fury/Fury-MX', 'status': 'purchasable'},
    {'manufacturer': 'Mirai', 'name': 'Guardian', 'auec_price': 6284250, 'dealers': ['Astro Armada', 'New Deal'], 'notes': '', 'role': 'Fighter', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/guardian/Guardian', 'status': 'purchasable'},
    {'manufacturer': 'Mirai', 'name': 'Guardian MX', 'auec_price': 7038360, 'dealers': ['Astro Armada', 'New Deal'], 'notes': '', 'role': 'Fighter', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/guardian/Guardian-MX', 'status': 'purchasable'},
    {'manufacturer': 'Mirai', 'name': 'Pulse', 'auec_price': 175959, 'dealers': ['Astro Armada', 'New Deal'], 'notes': '', 'role': 'Racing', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/mirai-pulse/Pulse', 'status': 'purchasable'},
    {'manufacturer': 'Mirai', 'name': 'Pulse LX', 'auec_price': 201096, 'dealers': ['New Deal'], 'notes': '', 'role': 'Racing', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/mirai-pulse/Pulse-LX', 'status': 'purchasable'},
    {'manufacturer': 'Mirai', 'name': 'Razor', 'auec_price': 1770363, 'dealers': ['New Deal'], 'notes': '', 'role': 'Racing', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/razor/Razor', 'status': 'purchasable'},
    {'manufacturer': 'Mirai', 'name': 'Razor EX', 'auec_price': 1669815, 'dealers': ['Astro Armada', 'New Deal'], 'notes': '', 'role': 'Fighter', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/razor/Razor-EX', 'status': 'purchasable'},
    {'manufacturer': 'Mirai', 'name': 'Razor LX', 'auec_price': 1831410, 'dealers': ['Astro Armada', 'New Deal'], 'notes': '', 'role': 'Racing', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/razor/Razor-LX', 'status': 'purchasable'},
    {'manufacturer': 'Origin Jumpworks', 'name': '100i', 'auec_price': 1089270, 'dealers': ['Astro Armada', 'New Deal'], 'notes': '', 'role': 'Exploration', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/origin-100/100i', 'status': 'purchasable'},
    {'manufacturer': 'Origin Jumpworks', 'name': '125a', 'auec_price': 1508220, 'dealers': ['New Deal'], 'notes': '', 'role': 'Fighter', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/origin-100/125a', 'status': 'purchasable'},
    {'manufacturer': 'Origin Jumpworks', 'name': '135c', 'auec_price': 1490580, 'dealers': ['Astro Armada'], 'notes': '', 'role': 'Cargo', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/origin-100/135c', 'status': 'purchasable'},
    {'manufacturer': 'Origin Jumpworks', 'name': '300i', 'auec_price': 1375920, 'dealers': ['Astro Armada'], 'notes': '', 'role': 'Multi-role', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/origin-300/300i', 'status': 'purchasable'},
    {'manufacturer': 'Origin Jumpworks', 'name': '315p', 'auec_price': 1490580, 'dealers': ['Astro Armada'], 'notes': '', 'role': 'Exploration', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/origin-300/315p', 'status': 'purchasable'},
    {'manufacturer': 'Origin Jumpworks', 'name': '325a', 'auec_price': 1852200, 'dealers': ['Astro Armada'], 'notes': '', 'role': 'Fighter', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/origin-300/325a', 'status': 'purchasable'},
    {'manufacturer': 'Origin Jumpworks', 'name': '350r', 'auec_price': 3748500, 'dealers': ['Astro Armada'], 'notes': '', 'role': 'Racing', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/origin-300/350r', 'status': 'purchasable'},
    {'manufacturer': 'Origin Jumpworks', 'name': '400i', 'auec_price': 8389063, 'dealers': ['Astro Armada', 'New Deal'], 'notes': '', 'role': 'Exploration', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/400i/400i', 'status': 'purchasable'},
    {'manufacturer': 'Origin Jumpworks', 'name': '600i Explorer', 'auec_price': 27231750, 'dealers': ['Astro Armada'], 'notes': '', 'role': 'Exploration', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/600i/600i-Explorer', 'status': 'purchasable'},
    {'manufacturer': 'Origin Jumpworks', 'name': '600i Touring', 'auec_price': 24938550, 'dealers': ['Astro Armada'], 'notes': '', 'role': 'Touring/Luxury', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/600i/600i-Touring', 'status': 'purchasable'},
    {'manufacturer': 'Origin Jumpworks', 'name': '85X', 'auec_price': 544635, 'dealers': ['New Deal'], 'notes': '', 'role': 'Touring/Luxury', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/85x/85X', 'status': 'purchasable'},
    {'manufacturer': 'Origin Jumpworks', 'name': '890 Jump', 'auec_price': 65356200, 'dealers': ['Astro Armada', 'New Deal'], 'notes': '', 'role': 'Touring/Luxury', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/890-jump/890-Jump', 'status': 'purchasable'},
    {'manufacturer': 'Origin Jumpworks', 'name': 'M50', 'auec_price': 1424430, 'dealers': ['Astro Armada', 'New Deal'], 'notes': '', 'role': 'Racing', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/origin-m50/M50', 'status': 'purchasable'},
    {'manufacturer': 'Origin Jumpworks', 'name': 'X1', 'auec_price': 125685, 'dealers': ['Astro Armada'], 'notes': '', 'role': 'Ground Vehicle', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/x1/X1', 'status': 'purchasable'},
    {'manufacturer': 'Origin Jumpworks', 'name': 'X1 Force', 'auec_price': 132300, 'dealers': ['Astro Armada', 'New Deal'], 'notes': '', 'role': 'Ground Vehicle', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/x1/X1-Force', 'status': 'purchasable'},
    {'manufacturer': 'Origin Jumpworks', 'name': 'X1 Velocity', 'auec_price': 113117, 'dealers': ['Astro Armada', 'New Deal'], 'notes': '', 'role': 'Racing', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/x1/X1-Velocity', 'status': 'purchasable'},
    {'manufacturer': 'Roberts Space Industries', 'name': 'Apollo Medivac', 'auec_price': 8295210, 'dealers': ["Teach's"], 'notes': 'New addition in 4.9.0', 'role': 'Medical', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/rsi-apollo/Apollo-Medivac', 'status': 'purchasable'},
    {'manufacturer': 'Roberts Space Industries', 'name': 'Apollo Triage', 'auec_price': 7541100, 'dealers': ["Teach's"], 'notes': 'New addition in 4.9.0', 'role': 'Medical', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/rsi-apollo/Apollo-Triage', 'status': 'purchasable'},
    {'manufacturer': 'Roberts Space Industries', 'name': 'Aurora CL', 'auec_price': 969570, 'dealers': ['New Deal', "Teach's"], 'notes': '', 'role': 'Cargo', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/rsi-aurora/Aurora-Mk-I-CL', 'status': 'purchasable'},
    {'manufacturer': 'Roberts Space Industries', 'name': 'Aurora ES', 'auec_price': 402192, 'dealers': ['New Deal', "Teach's"], 'notes': '', 'role': 'Exploration', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/rsi-aurora/Aurora-Mk-I-ES', 'status': 'purchasable'},
    {'manufacturer': 'Roberts Space Industries', 'name': 'Aurora LN', 'auec_price': 861840, 'dealers': ['New Deal'], 'notes': '', 'role': 'Fighter', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/rsi-aurora/Aurora-Mk-I-LN', 'status': 'purchasable'},
    {'manufacturer': 'Roberts Space Industries', 'name': 'Aurora LX', 'auec_price': 653562, 'dealers': ['New Deal'], 'notes': '', 'role': 'Exploration', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/rsi-aurora/Aurora-Mk-I-LX', 'status': 'purchasable'},
    {'manufacturer': 'Roberts Space Industries', 'name': 'Aurora MR', 'auec_price': 646380, 'dealers': ['New Deal'], 'notes': '', 'role': 'Fighter', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/rsi-aurora/Aurora-Mk-I-MR', 'status': 'purchasable'},
    {'manufacturer': 'Roberts Space Industries', 'name': 'Constellation Andromeda', 'auec_price': 9652608, 'dealers': ['New Deal'], 'notes': '', 'role': 'Cargo', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/rsi-constellation/Constellation-Andromeda', 'status': 'purchasable'},
    {'manufacturer': 'Roberts Space Industries', 'name': 'Constellation Aquila', 'auec_price': 11577384, 'dealers': ['New Deal'], 'notes': '', 'role': 'Exploration', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/rsi-constellation/Constellation-Aquila', 'status': 'purchasable'},
    {'manufacturer': 'Roberts Space Industries', 'name': 'Constellation Phoenix', 'auec_price': 14076720, 'dealers': ['New Deal'], 'notes': '', 'role': 'Touring/Luxury', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/rsi-constellation/Constellation-Phoenix', 'status': 'purchasable'},
    {'manufacturer': 'Roberts Space Industries', 'name': 'Constellation Taurus', 'auec_price': 7641650, 'dealers': ['New Deal', "Teach's"], 'notes': '', 'role': 'Cargo', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/rsi-constellation/Constellation-Taurus', 'status': 'purchasable'},
    {'manufacturer': 'Roberts Space Industries', 'name': 'Hermes', 'auec_price': 7110180, 'dealers': ["Teach's"], 'notes': '', 'role': 'Cargo', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/hermes/Hermes', 'status': 'purchasable'},
    {'manufacturer': 'Roberts Space Industries', 'name': 'Mantis', 'auec_price': 3231900, 'dealers': ['New Deal'], 'notes': '', 'role': 'Interdiction', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/rsi-mantis/Mantis', 'status': 'purchasable'},
    {'manufacturer': 'Roberts Space Industries', 'name': 'Meteor', 'auec_price': 4309200, 'dealers': ['New Deal'], 'notes': '', 'role': 'Fighter', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/rsi-meteor/Meteor', 'status': 'purchasable'},
    {'manufacturer': 'Roberts Space Industries', 'name': 'Perseus', 'auec_price': 39686023, 'dealers': ['Astro Armada'], 'notes': 'Price sourced from live terminal data - minor rounding vs earlier UEX figure, not a real discrepancy', 'role': 'Capital/Multi-crew', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/perseus/Perseus', 'status': 'purchasable'},
    {'manufacturer': 'Roberts Space Industries', 'name': 'Salvation', 'auec_price': 1185030, 'dealers': ["Teach's"], 'notes': '', 'role': 'Salvage', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/salvation/Salvation', 'status': 'purchasable'},
    {'manufacturer': 'Roberts Space Industries', 'name': 'Scorpius', 'auec_price': 5171040, 'dealers': ['New Deal'], 'notes': '', 'role': 'Fighter', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/scorpius/Scorpius', 'status': 'purchasable'},
    {'manufacturer': 'Roberts Space Industries', 'name': 'Ursa', 'auec_price': 107730, 'dealers': ['New Deal'], 'notes': '', 'role': 'Ground Vehicle', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/ursa/Ursa', 'status': 'purchasable'},
    {'manufacturer': 'Roberts Space Industries', 'name': 'Ursa Medivac', 'auec_price': 118503, 'dealers': ['New Deal', "Teach's"], 'notes': '', 'role': 'Medical', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/ursa/Ursa-Medivac', 'status': 'purchasable'},
    {'manufacturer': 'Roberts Space Industries', 'name': 'Zeus Mk II CL', 'auec_price': 6463800, 'dealers': ['New Deal'], 'notes': '', 'role': 'Cargo', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/zeus-mk-ii/Zeus-Mk-II-CL', 'status': 'purchasable'},
    {'manufacturer': 'Aopoa', 'name': 'Khartu-al', 'auec_price': 7229250, 'dealers': ['Astro Armada'], 'notes': '', 'role': 'Fighter', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/khartu/Khartu-Al', 'status': 'purchasable'},
    {'manufacturer': 'Aopoa', 'name': 'Nox', 'auec_price': 722925, 'dealers': ['Astro Armada'], 'notes': '', 'role': 'Racing', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/nox/Nox', 'status': 'purchasable'},
    {'manufacturer': 'Aopoa', 'name': "San'tok.yai", 'auec_price': 9355500, 'dealers': ['Astro Armada'], 'notes': 'Live sale confirmed at Astro Armada.', 'role': 'Fighter', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/aopoa-santokyai/Santoky-i', 'status': 'purchasable'},
    {'manufacturer': 'Tumbril Land Systems', 'name': 'Cyclone', 'auec_price': 98753, 'dealers': ['New Deal'], 'notes': 'Also buyable at 3 Pyro Buy & Fly outposts (Orbituary/Checkmate/Ruin Station) for 103,950 aUEC - Pyro runs a separate, slightly higher price tier', 'role': 'Ground Vehicle', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/cyclone/Cyclone', 'status': 'purchasable'},
    {'manufacturer': 'Tumbril Land Systems', 'name': 'Nova Tank', 'auec_price': 861840, 'dealers': ['New Deal'], 'notes': 'Also buyable at same 3 Pyro Buy & Fly outposts for 907,200 aUEC', 'role': 'Ground Vehicle', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/nova-tank/Nova', 'status': 'purchasable'},
    {'manufacturer': 'Roberts Space Industries', 'name': 'Lynx', 'auec_price': 129276, 'dealers': ['New Deal'], 'notes': '', 'role': 'Touring/Luxury', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/ursa/Lynx', 'status': 'purchasable'},
    {'manufacturer': 'Roberts Space Industries', 'name': 'Scorpius Antares', 'auec_price': 4955580, 'dealers': ['New Deal'], 'notes': '', 'role': 'Interdiction', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/scorpius/Scorpius-Antares', 'status': 'purchasable'},
    {'manufacturer': 'Roberts Space Industries', 'name': 'Zeus Mk II ES', 'auec_price': 4201470, 'dealers': ['New Deal'], 'notes': '', 'role': 'Exploration', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/zeus-mk-ii/Zeus-Mk-II-ES', 'status': 'purchasable'},
    {'manufacturer': 'Tumbril Land Systems', 'name': 'Cyclone AA', 'auec_price': 143640, 'dealers': ['New Deal'], 'notes': '', 'role': 'Ground Vehicle', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/cyclone/Cyclone-AA', 'status': 'purchasable'},
    {'manufacturer': 'Tumbril Land Systems', 'name': 'Cyclone MT', 'auec_price': 134663, 'dealers': ['New Deal'], 'notes': '', 'role': 'Ground Vehicle', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/cyclone/Cyclone-MT', 'status': 'purchasable'},
    {'manufacturer': 'Tumbril Land Systems', 'name': 'Cyclone RC', 'auec_price': 116708, 'dealers': ['New Deal'], 'notes': '', 'role': 'Racing', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/cyclone/Cyclone-RC', 'status': 'purchasable'},
    {'manufacturer': 'Tumbril Land Systems', 'name': 'Cyclone RN', 'auec_price': 116708, 'dealers': ['New Deal'], 'notes': '', 'role': 'Ground Vehicle', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/cyclone/Cyclone-RN', 'status': 'purchasable'},
    {'manufacturer': 'Tumbril Land Systems', 'name': 'Cyclone TR', 'auec_price': 116708, 'dealers': ['New Deal'], 'notes': '', 'role': 'Ground Vehicle', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/cyclone/Cyclone-TR', 'status': 'purchasable'},
    {'manufacturer': 'Tumbril Land Systems', 'name': 'Storm', 'auec_price': 430920, 'dealers': ['New Deal'], 'notes': '', 'role': 'Ground Vehicle', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/storm/Storm', 'status': 'purchasable'},
    {'manufacturer': 'Tumbril Land Systems', 'name': 'Storm AA', 'auec_price': 452466, 'dealers': ['New Deal'], 'notes': '', 'role': 'Ground Vehicle', 'pledge_usd': None, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/storm/Storm-AA', 'status': 'purchasable'},
    {'manufacturer': "Grey's Market", 'name': 'Basher', 'auec_price': None, 'dealers': [], 'notes': "New in 4.9.0. Pledge $110. In-game dealer not yet confirmed - Teach's is a guess, not verified.", 'role': 'Fighter', 'pledge_usd': 110.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/basher/Basher', 'status': 'pledge_only'},
    {'manufacturer': 'Drake Interplanetary', 'name': 'Kraken', 'auec_price': None, 'dealers': [], 'notes': 'Concept capital ship, see Development Progress tab. Pledge $1,650.', 'role': 'Capital/Multi-crew', 'pledge_usd': 1650.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/drake-kraken/Kraken', 'status': 'pledge_only'},
    {'manufacturer': 'Roberts Space Industries', 'name': 'Galaxy', 'auec_price': None, 'dealers': [], 'notes': 'Concept modular explorer. Pledge $380.', 'role': 'Multi-role', 'pledge_usd': 380.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/galaxy/Galaxy', 'status': 'pledge_only'},
    {'manufacturer': 'Anvil Aerospace', 'name': 'Liberator', 'auec_price': None, 'dealers': [], 'notes': 'Concept vehicle carrier. Pledge $575 - confirmed via UEX and independently verified.', 'role': 'Cargo', 'pledge_usd': 575.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/liberator/Liberator', 'status': 'pledge_only'},
    {'manufacturer': 'Consolidated Outland', 'name': 'Pioneer', 'auec_price': None, 'dealers': [], 'notes': 'Concept construction ship. Pledge $925 (UEX) - one other source shows $850, a real conflict, unresolved.', 'role': 'Multi-role', 'pledge_usd': 925.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/pioneer/Pioneer', 'status': 'pledge_only'},
    {'manufacturer': 'Argo Astronautics', 'name': 'CSV-FM', 'auec_price': None, 'dealers': [], 'notes': 'Concept cargo CSV variant. No reliable pledge price found.', 'role': 'Multi-role', 'pledge_usd': None, 'pledge_link': None, 'status': 'pledge_only'},
    {'manufacturer': 'Banu (Souli)', 'name': 'Merchantman', 'auec_price': None, 'dealers': [], 'notes': 'Long-standing concept cargo hauler. Pledge $650.', 'role': 'Cargo', 'pledge_usd': 650.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/merchantman/Merchantman', 'status': 'pledge_only'},
    {'manufacturer': 'Aegis Dynamics', 'name': 'Javelin', 'auec_price': None, 'dealers': [], 'notes': 'Concept destroyer. Pledge $3,000; older wiki snapshot shows $2,500.', 'role': 'Capital/Multi-crew', 'pledge_usd': 3000.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/aegis-javelin/Javelin', 'status': 'pledge_only'},
    {'manufacturer': 'Aegis Dynamics', 'name': 'Idris-M', 'auec_price': None, 'dealers': [], 'notes': 'Concept frigate/carrier variant. Pledge $1,000.', 'role': 'Capital/Multi-crew', 'pledge_usd': 1000.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/aegis-idris/Idris-M', 'status': 'pledge_only'},
    {'manufacturer': 'Aegis Dynamics', 'name': 'Idris-P', 'auec_price': None, 'dealers': [], 'notes': 'Concept frigate variant. Pledge $1,900 - confirmed via RSI Pledge Store and a second source.', 'role': 'Capital/Multi-crew', 'pledge_usd': 1900.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/aegis-idris/Idris-P', 'status': 'pledge_only'},
    {'manufacturer': 'Aegis Dynamics', 'name': 'Nautilus', 'auec_price': None, 'dealers': [], 'notes': 'Concept minelayer. Pledge $725.', 'role': 'Minelayer', 'pledge_usd': 725.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/aegis-nautilus/Nautilus', 'status': 'pledge_only'},
    {'manufacturer': 'Anvil Aerospace', 'name': 'Crucible', 'auec_price': None, 'dealers': [], 'notes': 'Concept repair ship. Pledge $350.', 'role': 'Support/Repair', 'pledge_usd': 350.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/crucible/Crucible', 'status': 'pledge_only'},
    {'manufacturer': 'Anvil Aerospace', 'name': 'Odin', 'auec_price': None, 'dealers': [], 'notes': "CIG's last planned concept sale. $5,000, invite-only Founders Club, May 2026 - sale now closed.", 'role': 'Capital/Multi-crew', 'pledge_usd': 5000.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/odin/Odin', 'status': 'pledge_only'},
    {'manufacturer': 'Roberts Space Industries', 'name': 'Orion', 'auec_price': None, 'dealers': [], 'notes': 'Concept mining ship. Pledge $650.', 'role': 'Mining', 'pledge_usd': 650.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/orion/Orion', 'status': 'pledge_only'},
    {'manufacturer': 'Aegis Dynamics', 'name': 'Vulcan', 'auec_price': None, 'dealers': [], 'notes': 'Concept refuel/repair ship. Pledge $200.', 'role': 'Support/Repair', 'pledge_usd': 200.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/vulcan/Vulcan', 'status': 'pledge_only'},
    {'manufacturer': 'Anvil Aerospace', 'name': 'Legionnaire', 'auec_price': None, 'dealers': [], 'notes': 'Concept FPS boarding ship. Pledge $120 - older snapshot, verify current price on the RSI Pledge Store.', 'role': 'Multi-role', 'pledge_usd': 120.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/legionnaire/Legionnaire', 'status': 'pledge_only'},
    {'manufacturer': 'MISC', 'name': 'Endeavor', 'auec_price': None, 'dealers': [], 'notes': 'Concept modular science/medical ship. Pledge $350.', 'role': 'Data', 'pledge_usd': 350.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/misc-endeavor/Endeavor', 'status': 'pledge_only'},
    {'manufacturer': 'Crusader Industries', 'name': 'Genesis Starliner', 'auec_price': None, 'dealers': [], 'notes': 'Concept passenger transport. Pledge $400.', 'role': 'Multi-role', 'pledge_usd': 400.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/starliner/Genesis', 'status': 'pledge_only'},
    {'manufacturer': 'MISC', 'name': 'Expanse', 'auec_price': None, 'dealers': [], 'notes': 'Concept refinery ship. Pledge $150.', 'role': 'Mining', 'pledge_usd': 150.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/expanse/Expanse', 'status': 'pledge_only'},
    {'manufacturer': 'MISC', 'name': 'Hull D', 'auec_price': None, 'dealers': [], 'notes': 'Concept cargo hauler. Pledge $550.', 'role': 'Cargo', 'pledge_usd': 550.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/hull/Hull-D', 'status': 'pledge_only'},
    {'manufacturer': 'MISC', 'name': 'Hull E', 'auec_price': None, 'dealers': [], 'notes': 'Concept cargo hauler, largest of the Hull line. Pledge $750.', 'role': 'Cargo', 'pledge_usd': 750.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/hull/Hull-E', 'status': 'pledge_only'},
    {'manufacturer': 'MISC', 'name': 'Odyssey', 'auec_price': None, 'dealers': [], 'notes': 'Concept exploration ship. Pledge $700.', 'role': 'Exploration', 'pledge_usd': 700.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/odyssey/Odyssey', 'status': 'pledge_only'},
    {'manufacturer': 'Drake Interplanetary', 'name': 'Kraken Privateer', 'auec_price': None, 'dealers': [], 'notes': 'Concept Kraken variant. Pledge $2,000.', 'role': 'Capital/Multi-crew', 'pledge_usd': 2000.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/drake-kraken/Kraken-Privateer', 'status': 'pledge_only'},
    {'manufacturer': 'Roberts Space Industries', 'name': 'Arrastra', 'auec_price': None, 'dealers': [], 'notes': 'Concept mining/refinery ship. Pledge $575.', 'role': 'Mining', 'pledge_usd': 575.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/arrastra/Arrastra', 'status': 'pledge_only'},
    {'manufacturer': 'Crusader Industries', 'name': 'E1 Spirit', 'auec_price': None, 'dealers': [], 'notes': 'Concept civilian Spirit-line variant. Pledge $150.', 'role': 'Multi-role', 'pledge_usd': 150.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/spirit/E1-Spirit', 'status': 'pledge_only'},
    {'manufacturer': 'Roberts Space Industries', 'name': 'Zeus Mk II MR', 'auec_price': None, 'dealers': [], 'notes': 'Concept military Zeus Mk II variant. Pledge $190.', 'role': 'Interdiction', 'pledge_usd': 190.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/zeus-mk-ii/Zeus-Mk-II-MR', 'status': 'pledge_only'},
    {'manufacturer': 'Tumbril Land Systems', 'name': 'Ranger CV', 'auec_price': None, 'dealers': [], 'notes': 'Concept Cyclone-family ground vehicle. Pledge $35.', 'role': 'Ground Vehicle', 'pledge_usd': 35.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/tumbril-ranger/Ranger-CV', 'status': 'pledge_only'},
    {'manufacturer': 'Tumbril Land Systems', 'name': 'Ranger RC', 'auec_price': None, 'dealers': [], 'notes': 'Concept Cyclone-family ground vehicle. Pledge $35.', 'role': 'Racing', 'pledge_usd': 35.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/tumbril-ranger/Ranger-RC', 'status': 'pledge_only'},
    {'manufacturer': 'Tumbril Land Systems', 'name': 'Ranger TR', 'auec_price': None, 'dealers': [], 'notes': 'Concept Cyclone-family ground vehicle. Pledge $40.', 'role': 'Ground Vehicle', 'pledge_usd': 40.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/tumbril-ranger/Ranger-TR', 'status': 'pledge_only'},
    {'manufacturer': 'MISC', 'name': 'Starlancer BLD', 'auec_price': None, 'dealers': [], 'notes': 'Concept construction variant of the Starlancer line. No pledge price yet - true concept, not even in the pledge store.', 'role': 'Multi-role', 'pledge_usd': None, 'pledge_link': None, 'status': 'pledge_only'},
    {'manufacturer': 'Roberts Space Industries', 'name': 'Aurora SE', 'auec_price': None, 'dealers': [], 'notes': 'Flight-ready, no dealer. Distinct Aurora variant. No in-game dealer confirmed.', 'role': 'Cargo', 'pledge_usd': 60.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/rsi-aurora/Aurora-Mk-I-SE', 'status': 'pledge_only'},
    {'manufacturer': 'Origin Jumpworks', 'name': 'G12', 'auec_price': None, 'dealers': [], 'notes': 'Flight-ready, no dealer. Touring ground vehicle, also bundled with the 600i Explorer/Executive. No in-game dealer confirmed.', 'role': 'Touring/Luxury', 'pledge_usd': 60.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/origin-g12/G12', 'status': 'pledge_only'},
    {'manufacturer': 'Origin Jumpworks', 'name': 'G12a', 'auec_price': None, 'dealers': [], 'notes': 'Flight-ready, no dealer. Recon ground vehicle variant. No in-game dealer confirmed.', 'role': 'Ground Vehicle', 'pledge_usd': 65.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/origin-g12/G12a', 'status': 'pledge_only'},
    {'manufacturer': 'Origin Jumpworks', 'name': 'G12r', 'auec_price': None, 'dealers': [], 'notes': 'Flight-ready, no dealer. Racing ground vehicle variant. No in-game dealer confirmed.', 'role': 'Racing', 'pledge_usd': 60.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/origin-g12/G12r', 'status': 'pledge_only'},
    {'manufacturer': 'Anvil Aerospace', 'name': 'F8C Lightning', 'auec_price': None, 'dealers': [], 'notes': 'Flight-ready, no dealer. Concierge-exclusive reward ($10,000+ lifetime spend) - not normally purchasable by most players. Included for completeness, not as a realistic buy target.', 'role': 'Fighter', 'pledge_usd': 300.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/lightning/F8C-Lightning', 'status': 'pledge_only'},
    {'manufacturer': 'MISC', 'name': 'RAPTOR', 'auec_price': None, 'dealers': [], 'notes': 'Flight-ready, no dealer. Referral-program reward only (50 referrals required) - not normally purchasable directly. Included for completeness, not as a realistic buy target.', 'role': 'Ground Vehicle', 'pledge_usd': 50.0, 'pledge_link': None, 'status': 'pledge_only'},
    {'manufacturer': 'Greycat Industrial', 'name': 'UTV', 'auec_price': None, 'dealers': [], 'notes': 'Not sold in-game anywhere. Pledge-only, $40 (a second source shows $42).', 'role': 'Ground Vehicle', 'pledge_usd': 40.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/utv/UTV', 'status': 'pledge_only'},
    {'manufacturer': 'Drake Interplanetary', 'name': 'Pitbull', 'auec_price': None, 'dealers': [], 'notes': 'Flight-ready, no dealer. Snub fighter. Pledge $55 - in-game dealer status unconfirmed.', 'role': 'Fighter', 'pledge_usd': 55.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/pitbull/Pitbull', 'status': 'pledge_only'},
    {'manufacturer': 'Drake Interplanetary', 'name': 'Ironclad', 'auec_price': None, 'dealers': [], 'notes': 'Flight-ready, no dealer. No in-game dealer confirmed.', 'role': 'Cargo', 'pledge_usd': 600.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/ironclad/Ironclad', 'status': 'pledge_only'},
    {'manufacturer': 'Drake Interplanetary', 'name': 'Ironclad Assault', 'auec_price': None, 'dealers': [], 'notes': 'Flight-ready, no dealer. Combat variant of the Ironclad. No in-game dealer confirmed yet.', 'role': 'Cargo', 'pledge_usd': 650.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/ironclad/Ironclad-Assault', 'status': 'pledge_only'},
    {'manufacturer': 'Aegis Dynamics', 'name': 'Tiburon', 'auec_price': None, 'dealers': [], 'notes': 'Flight-ready, no dealer. No in-game dealer confirmed.', 'role': 'Capital/Multi-crew', 'pledge_usd': 775.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/tiburon/Tiburon', 'status': 'pledge_only'},
    {'manufacturer': 'Roberts Space Industries', 'name': 'Polaris', 'auec_price': None, 'dealers': [], 'notes': 'Flight-ready, no dealer. Corvette-class capital ship. No in-game dealer confirmed.', 'role': 'Capital/Multi-crew', 'pledge_usd': 975.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/polaris/Polaris', 'status': 'pledge_only'},
    {'manufacturer': 'MISC', 'name': 'Hull B', 'auec_price': None, 'dealers': [], 'notes': 'Flight-ready, no dealer. No in-game dealer confirmed.', 'role': 'Cargo', 'pledge_usd': 280.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/hull/Hull-B', 'status': 'pledge_only'},
    {'manufacturer': 'Roberts Space Industries', 'name': 'Aurora Mk II', 'auec_price': None, 'dealers': [], 'notes': 'Flight-ready, no dealer. Confirmed real, alongside the existing Mk I line. Dealer status No in-game dealer confirmed.', 'role': 'Multi-role', 'pledge_usd': 45.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/aurora-mk-ii/Aurora-Mk-II', 'status': 'pledge_only'},
    {'manufacturer': 'Drake Interplanetary', 'name': 'Golem OX', 'auec_price': None, 'dealers': [], 'notes': 'Flight-ready, no dealer. Distinct cargo-focused variant of the Golem (64 SCU vs 32). Dealer status No in-game dealer confirmed.', 'role': 'Cargo', 'pledge_usd': 90.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/golem/Golem-OX', 'status': 'pledge_only'},
    {'manufacturer': 'Origin Jumpworks', 'name': 'M80', 'auec_price': None, 'dealers': [], 'notes': 'Flight-ready, no dealer. Heavy fighter. No in-game dealer confirmed.', 'role': 'Fighter', 'pledge_usd': 300.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/m80/M80', 'status': 'pledge_only'},
    {'manufacturer': 'MISC', 'name': 'Starlite', 'auec_price': None, 'dealers': [], 'notes': 'Flight-ready, no dealer. Light refuel ship. No in-game dealer confirmed.', 'role': 'Refuel', 'pledge_usd': 60.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/starlite/Starlite', 'status': 'pledge_only'},
    {'manufacturer': 'Gatac Manufacture', 'name': 'Tyilui', 'auec_price': None, 'dealers': [], 'notes': 'Flight-ready, no dealer. Carrier. No in-game dealer confirmed.', 'role': 'Capital/Multi-crew', 'pledge_usd': 425.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/tyilui/Tyilui', 'status': 'pledge_only'},
    {'manufacturer': 'Gatac Manufacture', 'name': 'Railen', 'auec_price': None, 'dealers': [], 'notes': 'Flight-ready, no dealer. Heavy freight. No in-game dealer confirmed.', 'role': 'Cargo', 'pledge_usd': 400.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/railen/Railen', 'status': 'pledge_only'},
    {'manufacturer': 'Kruger Intergalactic', 'name': 'L-22 Alpha Wolf', 'auec_price': None, 'dealers': [], 'notes': 'Flight-ready, no dealer. Upgraded L-21 Wolf variant. No in-game dealer confirmed.', 'role': 'Fighter', 'pledge_usd': 120.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/wolf/L-22-Alpha-Wolf', 'status': 'pledge_only'},
    {'manufacturer': 'Esperia', 'name': 'Glaive', 'auec_price': None, 'dealers': [], 'notes': 'Flight-ready, no dealer. Human-built Vanduul-derived fighter. Unlockable via 25 Vanduul Swarm waves in Arena Commander, or pledge. No in-game dealer confirmed.', 'role': 'Fighter', 'pledge_usd': 350.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/esperia-glaive/Glaive', 'status': 'pledge_only'},
    {'manufacturer': 'Esperia', 'name': 'Scythe', 'auec_price': None, 'dealers': [], 'notes': 'Flight-ready, no dealer. Referral-reward-gated (500 referrals), not normally pledge-purchasable. No in-game dealer confirmed.', 'role': 'Fighter', 'pledge_usd': 300.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/scythe/scythe', 'status': 'pledge_only'},
    {'manufacturer': 'Mirai', 'name': 'Guardian QI', 'auec_price': None, 'dealers': [], 'notes': 'Flight-ready, no dealer. Interdiction variant alongside Guardian/Guardian MX above. NOTE: also seen elsewhere as a temporary bug-workaround loaner for the Mantis - possibly both are true, unresolved.', 'role': 'Fighter', 'pledge_usd': 260.0, 'pledge_link': 'https://robertsspaceindustries.com/en/pledge/ships/guardian/Guardian-QI', 'status': 'pledge_only'},
]

DEALERS = [
    'Astro Armada (Area18)',
    'Crusader Showroom (Orison)',
    'New Deal (Lorville)',
    "Teach's (Levski)",
    'Buy & Fly (Ruin Station)',
]


def _parse_dealer_locations(entries: list[str]) -> dict[str, str]:
    locations = {}
    for entry in entries:
        match = re.match(r"^(.*) \(([^)]+)\)$", entry)
        if match:
            locations[match.group(1)] = match.group(2)
    return locations


DEALER_LOCATIONS = _parse_dealer_locations(DEALERS)


def has_conflict_marker(notes: str) -> bool:
    lowered = (notes or "").lower()
    return any(marker in lowered for marker in CONFLICT_MARKERS)


def get_or_create(session: Session, model, defaults: Optional[dict] = None, **kwargs):
    instance = session.query(model).filter_by(**kwargs).one_or_none()
    if instance is not None:
        for key, value in (defaults or {}).items():
            setattr(instance, key, value)
        return instance, False
    instance = model(**kwargs, **(defaults or {}))
    session.add(instance)
    session.flush()
    return instance, True


def seed(session: Session, patch_version: Optional[str]) -> None:
    patch_id = None
    if patch_version:
        patch, _ = get_or_create(session, Patch, version=patch_version)
        patch_id = patch.id

    stats = {
        "ships_created": 0,
        "ships_updated": 0,
        "purchasable": 0,
        "pledge_only": 0,
        "dealer_listings": 0,
        "pledge_links": 0,
    }
    flagged: list[tuple[str, str]] = []

    for row in SHIPS:
        manufacturer, _ = get_or_create(
            session,
            Manufacturer,
            name=row["manufacturer"],
            defaults={"last_verified_patch": patch_id, "confidence": "verified"},
        )

        stats[row["status"]] += 1

        conflicted = has_conflict_marker(row["notes"])
        if conflicted:
            flagged.append((row["name"], row["notes"]))

        ship, ship_created = get_or_create(
            session,
            Ship,
            name=row["name"],
            manufacturer_id=manufacturer.id,
            defaults={
                "role": row.get("role"),
                "notes": row.get("notes"),
                "status": row["status"],
                "last_verified_patch": patch_id,
                "confidence": "low" if conflicted else "verified",
                "verification_source": "Phase 1 migration",
            },
        )
        stats["ships_created" if ship_created else "ships_updated"] += 1

        for dealer_name in row.get("dealers") or []:
            dealer, _ = get_or_create(
                session,
                Dealer,
                name=dealer_name,
                defaults={
                    "location": DEALER_LOCATIONS.get(dealer_name),
                    "last_verified_patch": patch_id,
                    "confidence": "verified",
                },
            )
            get_or_create(
                session,
                ShipDealerListing,
                ship_id=ship.id,
                dealer_id=dealer.id,
                defaults={
                    "in_game_price_auec": row.get("auec_price"),
                    "last_verified_patch": patch_id,
                    "confidence": "verified",
                    "verification_source": "Phase 1 migration",
                },
            )
            stats["dealer_listings"] += 1

        if row.get("pledge_link"):
            get_or_create(
                session,
                PledgeLink,
                ship_id=ship.id,
                defaults={
                    "url": row["pledge_link"],
                    "price_usd": row.get("pledge_usd"),
                    "last_verified_patch": patch_id,
                    "confidence": "low" if conflicted else "verified",
                    "verification_source": "RSI Pledge Store",
                },
            )
            stats["pledge_links"] += 1

    session.commit()

    print(f"Ships created:                 {stats['ships_created']}")
    print(f"Ships updated:                 {stats['ships_updated']}")
    print(f"Confirmed purchasable:         {stats['purchasable']}")
    print(f"Pledge-only:                   {stats['pledge_only']}")
    print(f"Dealer listings written:       {stats['dealer_listings']}")
    print(f"Pledge links written:          {stats['pledge_links']}")

    if stats["purchasable"] != 179 or stats["pledge_only"] != 53:
        print(
            f"NOTE: handoff doc expects 179 purchasable / 53 pledge-only out of 232 ships; "
            f"this run saw {stats['purchasable']} / {stats['pledge_only']}. "
            "Double-check SHIPS before trusting the result."
        )

    if flagged:
        print(f"\n{len(flagged)} ship(s) stamped confidence=low (notes flag an unresolved conflict):")
        for name, notes in flagged:
            print(f"  - {name}: {notes}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Seed the Citizen Compass database from Phase 1 ship data."
    )
    parser.add_argument(
        "--patch",
        help="Current game patch version (e.g. 4.10) to stamp as last_verified_patch",
    )
    args = parser.parse_args()

    session = SessionLocal()
    try:
        seed(session, args.patch)
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
