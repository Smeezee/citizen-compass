# CIC — RSI official ship roles, all 253 ships

**Read 2026-09-12 from RSI's own pledge store. Nothing from a wiki, tracker or aggregator.
Nothing under `/media/`. No contact with CIG.**

RSI publishes an official role for every ship on the store, on the ship card itself, in its
own element (`a-shipCardInformation__type-text`). Both store views swept alphabetically
(`sortField=name&sortDirection=asc`) and reconciled by name against the 253-row Pass 1
list: **253 of 253, 0 blanks, 0 missing, 0 extra, 0 disagreements between the two views.**

**Roles are recorded verbatim and are NOT normalised.** Three things in RSI's vocabulary
will bite an importer and are left exactly as RSI writes them:

- `Transporter` (35) and `Transport` (6) are both used. Different strings.
- `Multi-Role` (7) and `Multi-role` (3) are both used. Case differs.
- `Starter / Starter / Light Freight` (Intrepid) and `Destroyer / Destroyer` (Javelin)
  repeat their own category as the role.

**Any grouping of those is a decision and it is not Research's.**

**88 distinct role strings. 233 ships carry two segments, 20 carry three.**
First-segment categories: Combat 108, Transporter 35, Exploration 33, Industrial 20, Competition 17, Support 13, Ground 9, Multi-Role 7, Transport 6, Multi-role 3, Starter 1, Destroyer 1

`segments` is the role split on `/` with whitespace trimmed — a convenience, not a new
claim. `store_view` records which of the two store views the row was read from in Pass 1.

## The data

```json
[
 {
  "name": "100i",
  "official_role_verbatim": "Exploration / Starter / Pathfinder",
  "segments": [
   "Exploration",
   "Starter",
   "Pathfinder"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/origin-100/100i",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "125a",
  "official_role_verbatim": "Combat / Light Fighter",
  "segments": [
   "Combat",
   "Light Fighter"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/origin-100/125a",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "135c",
  "official_role_verbatim": "Transporter / Light Freight",
  "segments": [
   "Transporter",
   "Light Freight"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/origin-100/135c",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "300i",
  "official_role_verbatim": "Exploration / Luxury Touring",
  "segments": [
   "Exploration",
   "Luxury Touring"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/origin-300/300i",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "315p",
  "official_role_verbatim": "Exploration / Pathfinder",
  "segments": [
   "Exploration",
   "Pathfinder"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/origin-300/315p",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "325a",
  "official_role_verbatim": "Combat / Interceptor",
  "segments": [
   "Combat",
   "Interceptor"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/origin-300/325a",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "350r",
  "official_role_verbatim": "Competition / Racing",
  "segments": [
   "Competition",
   "Racing"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/origin-300/350r",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "400i",
  "official_role_verbatim": "Exploration / Expedition",
  "segments": [
   "Exploration",
   "Expedition"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/400i/400i",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "600i Explorer",
  "official_role_verbatim": "Exploration / Expedition",
  "segments": [
   "Exploration",
   "Expedition"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/600i/600i-Explorer",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "600i Touring",
  "official_role_verbatim": "Exploration / Luxury Touring",
  "segments": [
   "Exploration",
   "Luxury Touring"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/600i/600i-Touring",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "85X",
  "official_role_verbatim": "Exploration / Touring",
  "segments": [
   "Exploration",
   "Touring"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/85x/85X",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "890 Jump",
  "official_role_verbatim": "Exploration / Luxury Touring",
  "segments": [
   "Exploration",
   "Luxury Touring"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/890-jump/890-Jump",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "A1 Spirit",
  "official_role_verbatim": "Combat / Bomber",
  "segments": [
   "Combat",
   "Bomber"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/spirit/A1-Spirit",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "A2 Hercules",
  "official_role_verbatim": "Combat / Heavy Bomber",
  "segments": [
   "Combat",
   "Heavy Bomber"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/crusader-starlifter/A2-Hercules",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Anvil Ballista Dunestalker",
  "official_role_verbatim": "Combat / Military",
  "segments": [
   "Combat",
   "Military"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/anvil-ballista/Anvil-Ballista-Dunestalker",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Anvil Ballista Snowblind",
  "official_role_verbatim": "Combat / Military",
  "segments": [
   "Combat",
   "Military"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/anvil-ballista/Anvil-Ballista-Snowblind",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Apollo Medivac",
  "official_role_verbatim": "Support / Medical",
  "segments": [
   "Support",
   "Medical"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/rsi-apollo/Apollo-Medivac",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Apollo Triage",
  "official_role_verbatim": "Support / Medical",
  "segments": [
   "Support",
   "Medical"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/rsi-apollo/Apollo-Triage",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Ares Inferno",
  "official_role_verbatim": "Combat / Heavy Fighter",
  "segments": [
   "Combat",
   "Heavy Fighter"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/crusader-ares/Ares-Inferno",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Ares Ion",
  "official_role_verbatim": "Combat / Heavy Fighter",
  "segments": [
   "Combat",
   "Heavy Fighter"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/crusader-ares/Ares-Ion",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Argo Mole Carbon Edition",
  "official_role_verbatim": "Industrial / Medium Mining",
  "segments": [
   "Industrial",
   "Medium Mining"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/argo-mole/Argo-Mole-Carbon-Edition",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Argo Mole Talus Edition",
  "official_role_verbatim": "Industrial / Medium Mining",
  "segments": [
   "Industrial",
   "Medium Mining"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/argo-mole/Argo-Mole-Talus-Edition",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Arrastra",
  "official_role_verbatim": "Industrial / Mining / Refining",
  "segments": [
   "Industrial",
   "Mining",
   "Refining"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/arrastra/Arrastra",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Arrow",
  "official_role_verbatim": "Combat / Light Fighter",
  "segments": [
   "Combat",
   "Light Fighter"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/anvil-arrow/Arrow",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "Asgard",
  "official_role_verbatim": "Combat / Dropship",
  "segments": [
   "Combat",
   "Dropship"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/anvil-asgard/Asgard",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "ATLS",
  "official_role_verbatim": "Ground / Cargo",
  "segments": [
   "Ground",
   "Cargo"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/atls/ATLS",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "ATLS GEO",
  "official_role_verbatim": "Ground / Mining",
  "segments": [
   "Ground",
   "Mining"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/atls/ATLS-GEO",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "Aurora Mk I CL",
  "official_role_verbatim": "Transporter / Light Freight",
  "segments": [
   "Transporter",
   "Light Freight"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/rsi-aurora/Aurora-Mk-I-CL",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "Aurora Mk I ES",
  "official_role_verbatim": "Multi-Role / Starter / Pathfinder",
  "segments": [
   "Multi-Role",
   "Starter",
   "Pathfinder"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/rsi-aurora/Aurora-Mk-I-ES",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "Aurora Mk I LN",
  "official_role_verbatim": "Combat / Light Fighter",
  "segments": [
   "Combat",
   "Light Fighter"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/rsi-aurora/Aurora-Mk-I-LN",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "Aurora Mk I LX",
  "official_role_verbatim": "Exploration / Pathfinder",
  "segments": [
   "Exploration",
   "Pathfinder"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/rsi-aurora/Aurora-Mk-I-LX",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "Aurora Mk I MR",
  "official_role_verbatim": "Combat / Light Fighter",
  "segments": [
   "Combat",
   "Light Fighter"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/rsi-aurora/Aurora-Mk-I-MR",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "Aurora Mk I SE",
  "official_role_verbatim": "Combat / Light Fighter",
  "segments": [
   "Combat",
   "Light Fighter"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/rsi-aurora/Aurora-Mk-I-SE",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Aurora Mk II",
  "official_role_verbatim": "Multi-Role / Starter / Light Fighter",
  "segments": [
   "Multi-Role",
   "Starter",
   "Light Fighter"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/aurora-mk-ii/Aurora-Mk-II",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "Avenger Stalker",
  "official_role_verbatim": "Combat / Interceptor",
  "segments": [
   "Combat",
   "Interceptor"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/aegis-avenger/Avenger-Stalker",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "Avenger Titan",
  "official_role_verbatim": "Transporter / Light Freight",
  "segments": [
   "Transporter",
   "Light Freight"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/aegis-avenger/Avenger-Titan",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "Avenger Titan Renegade",
  "official_role_verbatim": "Transporter / Light Freight",
  "segments": [
   "Transporter",
   "Light Freight"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/aegis-avenger/Avenger-Titan-Renegade",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Avenger Warlock",
  "official_role_verbatim": "Combat / Interdiction",
  "segments": [
   "Combat",
   "Interdiction"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/aegis-avenger/Avenger-Warlock",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Ballista",
  "official_role_verbatim": "Combat / Anti-Air",
  "segments": [
   "Combat",
   "Anti-Air"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/anvil-ballista/Ballista",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "Basher",
  "official_role_verbatim": "Combat / Light Fighter",
  "segments": [
   "Combat",
   "Light Fighter"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/basher/Basher",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Blade",
  "official_role_verbatim": "Combat / Light Fighter",
  "segments": [
   "Combat",
   "Light Fighter"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/vanduul-blade/Blade",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Buccaneer",
  "official_role_verbatim": "Combat / Light Fighter",
  "segments": [
   "Combat",
   "Light Fighter"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/drake-buccaneer/Buccaneer",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "C1 Spirit",
  "official_role_verbatim": "Transporter / Light Freight",
  "segments": [
   "Transporter",
   "Light Freight"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/spirit/C1-Spirit",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "C2 Hercules",
  "official_role_verbatim": "Transporter / Medium Freight",
  "segments": [
   "Transporter",
   "Medium Freight"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/crusader-starlifter/C2-Hercules",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "C8 Pisces",
  "official_role_verbatim": "Exploration / Pathfinder",
  "segments": [
   "Exploration",
   "Pathfinder"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/anvil-pisces/C8-Pisces",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "C8R Pisces",
  "official_role_verbatim": "Support / Medical",
  "segments": [
   "Support",
   "Medical"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/anvil-pisces/C8R-Pisces",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "C8X Pisces Expedition",
  "official_role_verbatim": "Exploration / Pathfinder",
  "segments": [
   "Exploration",
   "Pathfinder"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/anvil-pisces/C8X-Pisces-Expedition",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "Carrack",
  "official_role_verbatim": "Exploration / Expedition",
  "segments": [
   "Exploration",
   "Expedition"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/carrack/Carrack",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "Carrack Expedition",
  "official_role_verbatim": "Exploration / Expedition",
  "segments": [
   "Exploration",
   "Expedition"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/carrack/Carrack-Expedition",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Carrack Expedition w/C8X",
  "official_role_verbatim": "Exploration / Expedition",
  "segments": [
   "Exploration",
   "Expedition"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/carrack/Carrack-Expedition-W-C8X",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Carrack w/C8X",
  "official_role_verbatim": "Exploration / Expedition",
  "segments": [
   "Exploration",
   "Expedition"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/carrack/Carrack-W-C8X",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Caterpillar",
  "official_role_verbatim": "Transporter / Medium Freight",
  "segments": [
   "Transporter",
   "Medium Freight"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/drake-caterpillar/Caterpillar",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Centurion",
  "official_role_verbatim": "Combat / Anti-Air",
  "segments": [
   "Combat",
   "Anti-Air"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/centurion/Centurion",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "Clipper",
  "official_role_verbatim": "Exploration / Generalist",
  "segments": [
   "Exploration",
   "Generalist"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/clipper/Clipper",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Constellation Andromeda",
  "official_role_verbatim": "Multi-Role / Medium Freight / Gun Ship",
  "segments": [
   "Multi-Role",
   "Medium Freight",
   "Gun Ship"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/rsi-constellation/Constellation-Andromeda",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "Constellation Aquila",
  "official_role_verbatim": "Exploration / Expedition",
  "segments": [
   "Exploration",
   "Expedition"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/rsi-constellation/Constellation-Aquila",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "Constellation Phoenix",
  "official_role_verbatim": "Exploration / Luxury Touring",
  "segments": [
   "Exploration",
   "Luxury Touring"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/rsi-constellation/Constellation-Phoenix",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Constellation Phoenix Emerald",
  "official_role_verbatim": "Exploration / Luxury Touring",
  "segments": [
   "Exploration",
   "Luxury Touring"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/rsi-constellation/Constellation-Phoenix-Emerald",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Constellation Taurus",
  "official_role_verbatim": "Transporter / Medium Freight",
  "segments": [
   "Transporter",
   "Medium Freight"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/rsi-constellation/Constellation-Taurus",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "Corsair",
  "official_role_verbatim": "Exploration / Expedition",
  "segments": [
   "Exploration",
   "Expedition"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/drake-corsair/Corsair",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Crucible",
  "official_role_verbatim": "Support / Heavy Repair",
  "segments": [
   "Support",
   "Heavy Repair"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/crucible/Crucible",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "CSV-SM",
  "official_role_verbatim": "Transporter / Light Freight",
  "segments": [
   "Transporter",
   "Light Freight"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/csv/CSV-SM",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Cutlass Black",
  "official_role_verbatim": "Multi-Role / Light Freight / Medium Fighter",
  "segments": [
   "Multi-Role",
   "Light Freight",
   "Medium Fighter"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/drake-cutlass/Cutlass-Black",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "Cutlass Blue",
  "official_role_verbatim": "Combat / Interdiction",
  "segments": [
   "Combat",
   "Interdiction"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/drake-cutlass/Cutlass-Blue",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Cutlass Red",
  "official_role_verbatim": "Support / Medical",
  "segments": [
   "Support",
   "Medical"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/drake-cutlass/Cutlass-Red",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Cutlass Steel",
  "official_role_verbatim": "Combat / Dropship",
  "segments": [
   "Combat",
   "Dropship"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/drake-cutlass/Cutlass-Steel",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Cutter",
  "official_role_verbatim": "Exploration / Starter / Pathfinder",
  "segments": [
   "Exploration",
   "Starter",
   "Pathfinder"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/cutter/Cutter",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "Cutter Rambler",
  "official_role_verbatim": "Exploration / Expedition",
  "segments": [
   "Exploration",
   "Expedition"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/cutter/Cutter-Rambler",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Cutter Scout",
  "official_role_verbatim": "Exploration / Pathfinder",
  "segments": [
   "Exploration",
   "Pathfinder"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/cutter/Cutter-Scout",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Cyclone",
  "official_role_verbatim": "Combat / Passenger",
  "segments": [
   "Combat",
   "Passenger"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/cyclone/Cyclone",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "Cyclone AA",
  "official_role_verbatim": "Combat / Anti-Air",
  "segments": [
   "Combat",
   "Anti-Air"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/cyclone/Cyclone-AA",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Cyclone MT",
  "official_role_verbatim": "Combat / Anti-Air",
  "segments": [
   "Combat",
   "Anti-Air"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/cyclone/Cyclone-MT",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Cyclone RC",
  "official_role_verbatim": "Competition / Racing",
  "segments": [
   "Competition",
   "Racing"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/cyclone/Cyclone-RC",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Cyclone RN",
  "official_role_verbatim": "Exploration / Pathfinder",
  "segments": [
   "Exploration",
   "Pathfinder"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/cyclone/Cyclone-RN",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "Cyclone TR",
  "official_role_verbatim": "Combat / Anti-Vehicle",
  "segments": [
   "Combat",
   "Anti-Vehicle"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/cyclone/Cyclone-TR",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Defender",
  "official_role_verbatim": "Combat / Light Fighter",
  "segments": [
   "Combat",
   "Light Fighter"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/defender/Defender",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Dragonfly Black",
  "official_role_verbatim": "Competition / Racing",
  "segments": [
   "Competition",
   "Racing"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/drake-dragonfly/Dragonfly-Black",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "Dragonfly Yellowjacket",
  "official_role_verbatim": "Competition / Racing",
  "segments": [
   "Competition",
   "Racing"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/drake-dragonfly/Dragonfly-Yellowjacket",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "E1 Spirit",
  "official_role_verbatim": "Transporter / Passenger",
  "segments": [
   "Transporter",
   "Passenger"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/spirit/E1-Spirit",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Eclipse",
  "official_role_verbatim": "Combat / Stealth Bomber",
  "segments": [
   "Combat",
   "Stealth Bomber"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/eclipse/Eclipse",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Endeavor",
  "official_role_verbatim": "Industrial / Heavy Science",
  "segments": [
   "Industrial",
   "Heavy Science"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/misc-endeavor/Endeavor",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Expanse",
  "official_role_verbatim": "Industrial / Refinery",
  "segments": [
   "Industrial",
   "Refinery"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/expanse/Expanse",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "F7A Hornet Mk I",
  "official_role_verbatim": "Combat / Medium Fighter",
  "segments": [
   "Combat",
   "Medium Fighter"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/anvil-hornet/F7A-Hornet-Mk-I",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "F7A Hornet Mk II",
  "official_role_verbatim": "Combat / Medium Fighter",
  "segments": [
   "Combat",
   "Medium Fighter"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/anvil-hornet-mkii/F7A-Hornet-Mk-II",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "F7C Hornet Mk I",
  "official_role_verbatim": "Combat / Medium Fighter",
  "segments": [
   "Combat",
   "Medium Fighter"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/anvil-hornet/F7C-Hornet-Mk-I",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "F7C Hornet Mk II",
  "official_role_verbatim": "Combat / Medium Fighter",
  "segments": [
   "Combat",
   "Medium Fighter"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/anvil-hornet-mkii/F7C-Hornet-Mk-II",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "F7C Hornet Wildfire Mk I",
  "official_role_verbatim": "Combat / Medium Fighter",
  "segments": [
   "Combat",
   "Medium Fighter"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/anvil-hornet/F7C-Hornet-Wildfire-Mk-I",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "F7C-M Super Hornet Heartseeker Mk I",
  "official_role_verbatim": "Combat / Medium Fighter",
  "segments": [
   "Combat",
   "Medium Fighter"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/anvil-hornet/F7C-M-Super-Hornet-Heartseeker-Mk-I",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "F7C-M Super Hornet Mk I",
  "official_role_verbatim": "Combat / Medium Fighter",
  "segments": [
   "Combat",
   "Medium Fighter"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/anvil-hornet/F7C-M-Super-Hornet-Mk-I",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "F7C-M Super Hornet Mk II",
  "official_role_verbatim": "Combat / Medium Fighter",
  "segments": [
   "Combat",
   "Medium Fighter"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/anvil-hornet-mkii/F7C-M-Super-Hornet-Mk-II",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "F7C-R Hornet Tracker Mk I",
  "official_role_verbatim": "Exploration / Pathfinder",
  "segments": [
   "Exploration",
   "Pathfinder"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/anvil-hornet/F7C-R-Hornet-Tracker-Mk-I",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "F7C-R Hornet Tracker Mk II",
  "official_role_verbatim": "Combat / Pathfinder",
  "segments": [
   "Combat",
   "Pathfinder"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/anvil-hornet-mkii/F7C-R-Hornet-Tracker-Mk-II",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "F7C-S Hornet Ghost Mk I",
  "official_role_verbatim": "Combat / Stealth Fighter",
  "segments": [
   "Combat",
   "Stealth Fighter"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/anvil-hornet/F7C-S-Hornet-Ghost-Mk-I",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "F7C-S Hornet Ghost Mk II",
  "official_role_verbatim": "Combat / Stealth Fighter",
  "segments": [
   "Combat",
   "Stealth Fighter"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/anvil-hornet-mkii/F7C-S-Hornet-Ghost-Mk-II",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "F8C Lightning",
  "official_role_verbatim": "Combat / Heavy Fighter",
  "segments": [
   "Combat",
   "Heavy Fighter"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/lightning/F8C-Lightning",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "F8C Lightning Executive Edition",
  "official_role_verbatim": "Combat / Heavy Fighter",
  "segments": [
   "Combat",
   "Heavy Fighter"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/lightning/F8C-Lightning-Executive-Edition",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Fortune",
  "official_role_verbatim": "Industrial / Light Salvage",
  "segments": [
   "Industrial",
   "Light Salvage"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/fortune/Fortune",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Freelancer",
  "official_role_verbatim": "Transporter / Light Freight",
  "segments": [
   "Transporter",
   "Light Freight"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/misc-freelancer/Freelancer",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "Freelancer DUR",
  "official_role_verbatim": "Exploration / Expedition",
  "segments": [
   "Exploration",
   "Expedition"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/misc-freelancer/Freelancer-DUR",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "Freelancer MAX",
  "official_role_verbatim": "Transporter / Medium Freight",
  "segments": [
   "Transporter",
   "Medium Freight"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/misc-freelancer/Freelancer-MAX",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "Freelancer MIS",
  "official_role_verbatim": "Combat / Gunship",
  "segments": [
   "Combat",
   "Gunship"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/misc-freelancer/Freelancer-MIS",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Fury",
  "official_role_verbatim": "Combat / Snub Fighter",
  "segments": [
   "Combat",
   "Snub Fighter"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/fury/Fury",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Fury LX",
  "official_role_verbatim": "Competition / Racing",
  "segments": [
   "Competition",
   "Racing"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/fury/Fury-LX",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Fury MX",
  "official_role_verbatim": "Combat / Snub Fighter",
  "segments": [
   "Combat",
   "Snub Fighter"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/fury/Fury-MX",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "G12",
  "official_role_verbatim": "Ground / Touring",
  "segments": [
   "Ground",
   "Touring"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/origin-g12/G12",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "G12a",
  "official_role_verbatim": "Ground / Military",
  "segments": [
   "Ground",
   "Military"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/origin-g12/G12a",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "G12r",
  "official_role_verbatim": "Competition / Racing",
  "segments": [
   "Competition",
   "Racing"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/origin-g12/G12r",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Galaxy",
  "official_role_verbatim": "Multi-role / Modular",
  "segments": [
   "Multi-role",
   "Modular"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/galaxy/Galaxy",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Genesis",
  "official_role_verbatim": "Transport / Passenger",
  "segments": [
   "Transport",
   "Passenger"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/starliner/Genesis",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Gladiator",
  "official_role_verbatim": "Combat / Bomber",
  "segments": [
   "Combat",
   "Bomber"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/anvil-gladiator/Gladiator",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Gladius",
  "official_role_verbatim": "Combat / Light Fighter",
  "segments": [
   "Combat",
   "Light Fighter"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/gladius/Gladius",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "Gladius Pirate Edition",
  "official_role_verbatim": "Combat / Light Fighter",
  "segments": [
   "Combat",
   "Light Fighter"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/gladius/Gladius-Pirate-Edition",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Gladius Valiant",
  "official_role_verbatim": "Combat / Light Fighter",
  "segments": [
   "Combat",
   "Light Fighter"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/gladius/Gladius-Valiant",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Glaive",
  "official_role_verbatim": "Combat / Medium Fighter",
  "segments": [
   "Combat",
   "Medium Fighter"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/esperia-glaive/Glaive",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Golem",
  "official_role_verbatim": "Industrial / Starter / Light Mining",
  "segments": [
   "Industrial",
   "Starter",
   "Light Mining"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/golem/Golem",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "Golem OX",
  "official_role_verbatim": "Industrial / Light Freight",
  "segments": [
   "Industrial",
   "Light Freight"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/golem/Golem-OX",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "Guardian",
  "official_role_verbatim": "Combat / Heavy Fighter",
  "segments": [
   "Combat",
   "Heavy Fighter"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/guardian/Guardian",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Guardian MX",
  "official_role_verbatim": "Combat / Heavy Fighter",
  "segments": [
   "Combat",
   "Heavy Fighter"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/guardian/Guardian-MX",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Guardian QI",
  "official_role_verbatim": "Combat / Interdiction",
  "segments": [
   "Combat",
   "Interdiction"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/guardian/Guardian-QI",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Hammerhead",
  "official_role_verbatim": "Combat / Heavy Gunship",
  "segments": [
   "Combat",
   "Heavy Gunship"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/hammerhead/Hammerhead",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Hawk",
  "official_role_verbatim": "Combat / Light Fighter",
  "segments": [
   "Combat",
   "Light Fighter"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/hawk/Hawk",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Herald",
  "official_role_verbatim": "Transporter / Medium Data",
  "segments": [
   "Transporter",
   "Medium Data"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/herald/Herald",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Hermes",
  "official_role_verbatim": "Transporter / Medium Freight",
  "segments": [
   "Transporter",
   "Medium Freight"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/hermes/Hermes",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "HoverQuad",
  "official_role_verbatim": "Exploration / Passenger",
  "segments": [
   "Exploration",
   "Passenger"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/hoverquad/HoverQuad",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Hull A",
  "official_role_verbatim": "Transporter / Light Freight",
  "segments": [
   "Transporter",
   "Light Freight"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/hull/Hull-A",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "Hull B",
  "official_role_verbatim": "Transporter / Medium Freight",
  "segments": [
   "Transporter",
   "Medium Freight"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/hull/Hull-B",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Hull C",
  "official_role_verbatim": "Transporter / Heavy Freight",
  "segments": [
   "Transporter",
   "Heavy Freight"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/hull/Hull-C",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Hull D",
  "official_role_verbatim": "Transport / Heavy Freight",
  "segments": [
   "Transport",
   "Heavy Freight"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/hull/Hull-D",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Hull E",
  "official_role_verbatim": "Transport / Heavy Freight",
  "segments": [
   "Transport",
   "Heavy Freight"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/hull/Hull-E",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Hurricane",
  "official_role_verbatim": "Combat / Heavy Fighter",
  "segments": [
   "Combat",
   "Heavy Fighter"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/hurricane/Hurricane",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Idris-M",
  "official_role_verbatim": "Combat / Frigate",
  "segments": [
   "Combat",
   "Frigate"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/aegis-idris/Idris-M",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Idris-P",
  "official_role_verbatim": "Combat / Frigate",
  "segments": [
   "Combat",
   "Frigate"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/aegis-idris/Idris-P",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Intrepid",
  "official_role_verbatim": "Starter / Starter / Light Freight",
  "segments": [
   "Starter",
   "Starter",
   "Light Freight"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/intrepid/Intrepid",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "Ironclad",
  "official_role_verbatim": "Transporter / Heavy Freight",
  "segments": [
   "Transporter",
   "Heavy Freight"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/ironclad/Ironclad",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Ironclad Assault",
  "official_role_verbatim": "Combat / Heavy Dropship",
  "segments": [
   "Combat",
   "Heavy Dropship"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/ironclad/Ironclad-Assault",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Javelin",
  "official_role_verbatim": "Destroyer / Destroyer",
  "segments": [
   "Destroyer",
   "Destroyer"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/aegis-javelin/Javelin",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Khartu-Al",
  "official_role_verbatim": "Combat / Light Fighter",
  "segments": [
   "Combat",
   "Light Fighter"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/khartu/Khartu-Al",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Kraken",
  "official_role_verbatim": "Industrial / Multi-Role / Light Carrier",
  "segments": [
   "Industrial",
   "Multi-Role",
   "Light Carrier"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/drake-kraken/Kraken",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Kraken Privateer",
  "official_role_verbatim": "Industrial / Multi-Role / Light Carrier",
  "segments": [
   "Industrial",
   "Multi-Role",
   "Light Carrier"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/drake-kraken/Kraken-Privateer",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "L-21 Wolf",
  "official_role_verbatim": "Combat / Light Fighter",
  "segments": [
   "Combat",
   "Light Fighter"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/wolf/L-21-Wolf",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "L-22 Alpha Wolf",
  "official_role_verbatim": "Combat / Light Fighter",
  "segments": [
   "Combat",
   "Light Fighter"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/wolf/L-22-Alpha-Wolf",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "Legionnaire",
  "official_role_verbatim": "Combat / Boarding",
  "segments": [
   "Combat",
   "Boarding"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/legionnaire/Legionnaire",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Liberator",
  "official_role_verbatim": "Transport / Light Carrier",
  "segments": [
   "Transport",
   "Light Carrier"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/liberator/Liberator",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Lynx",
  "official_role_verbatim": "Transporter / Luxury Touring",
  "segments": [
   "Transporter",
   "Luxury Touring"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/ursa/Lynx",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "M2 Hercules",
  "official_role_verbatim": "Transporter / Medium Freight",
  "segments": [
   "Transporter",
   "Medium Freight"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/crusader-starlifter/M2-Hercules",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "M50",
  "official_role_verbatim": "Competition / Racing",
  "segments": [
   "Competition",
   "Racing"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/origin-m50/M50",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "M80",
  "official_role_verbatim": "Combat / Heavy Fighter",
  "segments": [
   "Combat",
   "Heavy Fighter"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/m80/M80",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Mantis",
  "official_role_verbatim": "Combat / Interdiction",
  "segments": [
   "Combat",
   "Interdiction"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/rsi-mantis/Mantis",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "MDC",
  "official_role_verbatim": "Ground / Anti-Air",
  "segments": [
   "Ground",
   "Anti-Air"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/mdc/MDC",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Merchantman",
  "official_role_verbatim": "Transport / Heavy Freight",
  "segments": [
   "Transport",
   "Heavy Freight"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/merchantman/Merchantman",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Mercury",
  "official_role_verbatim": "Transporter / Medium Freight",
  "segments": [
   "Transporter",
   "Medium Freight"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/crusader-mercury-star-runner/Mercury",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Meteor",
  "official_role_verbatim": "Combat / Medium Fighter",
  "segments": [
   "Combat",
   "Medium Fighter"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/rsi-meteor/Meteor",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "MOLE",
  "official_role_verbatim": "Industrial / Medium Mining",
  "segments": [
   "Industrial",
   "Medium Mining"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/argo-mole/MOLE",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "MOTH",
  "official_role_verbatim": "Industrial / Medium Salvage",
  "segments": [
   "Industrial",
   "Medium Salvage"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/moth/MOTH",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "MPUV Cargo",
  "official_role_verbatim": "Transporter / Light Freight",
  "segments": [
   "Transporter",
   "Light Freight"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/argo/MPUV-Cargo",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "MPUV Personnel",
  "official_role_verbatim": "Transporter / Passenger",
  "segments": [
   "Transporter",
   "Passenger"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/argo/MPUV-Personnel",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "MPUV Tractor",
  "official_role_verbatim": "Transporter / Light Freight",
  "segments": [
   "Transporter",
   "Light Freight"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/argo/MPUV-Tractor",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "MTC",
  "official_role_verbatim": "Ground / Passenger",
  "segments": [
   "Ground",
   "Passenger"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/mtc/MTC",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Mule",
  "official_role_verbatim": "Transporter / Light Freight",
  "segments": [
   "Transporter",
   "Light Freight"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/mule/Mule",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "Mustang Alpha",
  "official_role_verbatim": "Multi-Role / Starter / Light Freight",
  "segments": [
   "Multi-Role",
   "Starter",
   "Light Freight"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/mustang/Mustang-Alpha",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "Mustang Alpha Vindicator",
  "official_role_verbatim": "Multi-Role / Starter / Light Freight",
  "segments": [
   "Multi-Role",
   "Starter",
   "Light Freight"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/mustang/Mustang-Alpha-Vindicator",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Mustang Beta",
  "official_role_verbatim": "Exploration / Pathfinder",
  "segments": [
   "Exploration",
   "Pathfinder"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/mustang/Mustang-Beta",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "Mustang Delta",
  "official_role_verbatim": "Combat / Light Fighter",
  "segments": [
   "Combat",
   "Light Fighter"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/mustang/Mustang-Delta",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Mustang Gamma",
  "official_role_verbatim": "Competition / Racing",
  "segments": [
   "Competition",
   "Racing"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/mustang/Mustang-Gamma",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "Mustang Omega",
  "official_role_verbatim": "Competition / Racing",
  "segments": [
   "Competition",
   "Racing"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/mustang/Mustang-Omega",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Nautilus",
  "official_role_verbatim": "Combat / Minelayer",
  "segments": [
   "Combat",
   "Minelayer"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/aegis-nautilus/Nautilus",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Nautilus Solstice Edition",
  "official_role_verbatim": "Combat / Minelayer",
  "segments": [
   "Combat",
   "Minelayer"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/aegis-nautilus/Nautilus-Solstice-Edition",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Nomad",
  "official_role_verbatim": "Transporter / Starter / Light Freight",
  "segments": [
   "Transporter",
   "Starter",
   "Light Freight"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/nomad/Nomad",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "Nova",
  "official_role_verbatim": "Combat / Heavy Tank",
  "segments": [
   "Combat",
   "Heavy Tank"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/nova-tank/Nova",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Nox",
  "official_role_verbatim": "Competition / Racing",
  "segments": [
   "Competition",
   "Racing"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/nox/Nox",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Nox Kue",
  "official_role_verbatim": "Competition / Racing",
  "segments": [
   "Competition",
   "Racing"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/nox/Nox-Kue",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Odin",
  "official_role_verbatim": "Combat / Battlecruiser",
  "segments": [
   "Combat",
   "Battlecruiser"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/odin/Odin",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Odyssey",
  "official_role_verbatim": "Exploration / Expedition",
  "segments": [
   "Exploration",
   "Expedition"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/odyssey/Odyssey",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Orion",
  "official_role_verbatim": "Industrial / Heavy Mining",
  "segments": [
   "Industrial",
   "Heavy Mining"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/orion/Orion",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "P-52 Merlin",
  "official_role_verbatim": "Combat / Snub Fighter",
  "segments": [
   "Combat",
   "Snub Fighter"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/p52-merlin/P-52-Merlin",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "P-72 Archimedes",
  "official_role_verbatim": "Competition / Racing",
  "segments": [
   "Competition",
   "Racing"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/p72-archimedes/P-72-Archimedes",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "P-72 Archimedes Emerald",
  "official_role_verbatim": "Competition / Racing",
  "segments": [
   "Competition",
   "Racing"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/p72-archimedes/P-72-Archimedes-Emerald",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Paladin",
  "official_role_verbatim": "Combat / Gunship",
  "segments": [
   "Combat",
   "Gunship"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/paladin/Paladin",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Perseus",
  "official_role_verbatim": "Combat / Heavy Gunship",
  "segments": [
   "Combat",
   "Heavy Gunship"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/perseus/Perseus",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Pioneer",
  "official_role_verbatim": "Multi-role / Heavy Construction",
  "segments": [
   "Multi-role",
   "Heavy Construction"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/pioneer/Pioneer",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Pitbull",
  "official_role_verbatim": "Combat / Snub Fighter",
  "segments": [
   "Combat",
   "Snub Fighter"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/pitbull/Pitbull",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Polaris",
  "official_role_verbatim": "Combat / Corvette",
  "segments": [
   "Combat",
   "Corvette"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/polaris/Polaris",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Prospector",
  "official_role_verbatim": "Industrial / Light Mining",
  "segments": [
   "Industrial",
   "Light Mining"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/misc-prospector/Prospector",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "Prowler",
  "official_role_verbatim": "Combat / Dropship",
  "segments": [
   "Combat",
   "Dropship"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/prowler/Prowler",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Prowler Utility",
  "official_role_verbatim": "Transporter / Light Freight",
  "segments": [
   "Transporter",
   "Light Freight"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/prowler/Prowler-Utility",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "PTV",
  "official_role_verbatim": "Transporter / Passenger",
  "segments": [
   "Transporter",
   "Passenger"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/ptv/PTV",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "Pulse",
  "official_role_verbatim": "Combat / Pathfinder",
  "segments": [
   "Combat",
   "Pathfinder"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/mirai-pulse/Pulse",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "Pulse LX",
  "official_role_verbatim": "Combat / Racing",
  "segments": [
   "Combat",
   "Racing"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/mirai-pulse/Pulse-LX",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "RAFT",
  "official_role_verbatim": "Transporter / Medium Freight",
  "segments": [
   "Transporter",
   "Medium Freight"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/raft/RAFT",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Railen",
  "official_role_verbatim": "Transporter / Medium Freight",
  "segments": [
   "Transporter",
   "Medium Freight"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/railen/Railen",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Ranger CV",
  "official_role_verbatim": "Ground / Touring",
  "segments": [
   "Ground",
   "Touring"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/tumbril-ranger/Ranger-CV",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Ranger RC",
  "official_role_verbatim": "Ground / Racing",
  "segments": [
   "Ground",
   "Racing"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/tumbril-ranger/Ranger-RC",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Ranger TR",
  "official_role_verbatim": "Ground / Combat",
  "segments": [
   "Ground",
   "Combat"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/tumbril-ranger/Ranger-TR",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Razor",
  "official_role_verbatim": "Competition / Racing",
  "segments": [
   "Competition",
   "Racing"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/razor/Razor",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Razor EX",
  "official_role_verbatim": "Combat / Stealth Fighter",
  "segments": [
   "Combat",
   "Stealth Fighter"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/razor/Razor-EX",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Razor LX",
  "official_role_verbatim": "Competition / Racing",
  "segments": [
   "Competition",
   "Racing"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/razor/Razor-LX",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Reclaimer",
  "official_role_verbatim": "Industrial / Heavy Salvage",
  "segments": [
   "Industrial",
   "Heavy Salvage"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/reclaimer/Reclaimer",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Redeemer",
  "official_role_verbatim": "Combat / Gunship",
  "segments": [
   "Combat",
   "Gunship"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/redeemer/Redeemer",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Reliant Kore",
  "official_role_verbatim": "Transporter / Starter / Light Freight",
  "segments": [
   "Transporter",
   "Starter",
   "Light Freight"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/reliant/Reliant-Kore",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "Reliant Mako",
  "official_role_verbatim": "Support / Reporting",
  "segments": [
   "Support",
   "Reporting"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/reliant/Reliant-Mako",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Reliant Sen",
  "official_role_verbatim": "Industrial / Light Science",
  "segments": [
   "Industrial",
   "Light Science"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/reliant/Reliant-Sen",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Reliant Tana",
  "official_role_verbatim": "Combat / Light Fighter",
  "segments": [
   "Combat",
   "Light Fighter"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/reliant/Reliant-Tana",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Retaliator",
  "official_role_verbatim": "Combat / Modular",
  "segments": [
   "Combat",
   "Modular"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/aegis-retaliator/Retaliator",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "ROC",
  "official_role_verbatim": "Industrial / Light Mining",
  "segments": [
   "Industrial",
   "Light Mining"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/roc/ROC",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "ROC-DS",
  "official_role_verbatim": "Industrial / Light Mining",
  "segments": [
   "Industrial",
   "Light Mining"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/roc/ROC-DS",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "S-65 Stingray",
  "official_role_verbatim": "Combat / Medium Fighter",
  "segments": [
   "Combat",
   "Medium Fighter"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/s-65-stingray/S-65-Stingray",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "Sabre",
  "official_role_verbatim": "Combat / Stealth Fighter",
  "segments": [
   "Combat",
   "Stealth Fighter"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/sabre/Sabre",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Sabre Comet",
  "official_role_verbatim": "Combat / Stealth Fighter",
  "segments": [
   "Combat",
   "Stealth Fighter"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/sabre/Sabre-Comet",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Sabre Firebird",
  "official_role_verbatim": "Combat / Stealth Fighter",
  "segments": [
   "Combat",
   "Stealth Fighter"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/sabre/Sabre-Firebird",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Sabre Peregrine",
  "official_role_verbatim": "Competition / Racing",
  "segments": [
   "Competition",
   "Racing"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/sabre/Sabre-Peregrine",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Sabre Raven",
  "official_role_verbatim": "Combat / Interdiction",
  "segments": [
   "Combat",
   "Interdiction"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/sabre/Sabre-Raven",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Salvation",
  "official_role_verbatim": "Industrial / Starter / Light Salvage",
  "segments": [
   "Industrial",
   "Starter",
   "Light Salvage"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/salvation/Salvation",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "San'tok.y\u0101i",
  "official_role_verbatim": "Combat / Medium Fighter",
  "segments": [
   "Combat",
   "Medium Fighter"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/aopoa-santokyai/Santoky-i",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Scorpius",
  "official_role_verbatim": "Combat / Heavy Fighter",
  "segments": [
   "Combat",
   "Heavy Fighter"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/scorpius/Scorpius",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Scorpius Antares",
  "official_role_verbatim": "Combat / Heavy Fighter",
  "segments": [
   "Combat",
   "Heavy Fighter"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/scorpius/Scorpius-Antares",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Scythe",
  "official_role_verbatim": "Combat / Medium Fighter",
  "segments": [
   "Combat",
   "Medium Fighter"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/scythe/Scythe",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Shiv",
  "official_role_verbatim": "Combat / Heavy Fighter",
  "segments": [
   "Combat",
   "Heavy Fighter"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/shiv/Shiv",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Spartan",
  "official_role_verbatim": "Combat / Passenger",
  "segments": [
   "Combat",
   "Passenger"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/spartan/Spartan",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "SRV",
  "official_role_verbatim": "Support / Recovery",
  "segments": [
   "Support",
   "Recovery"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/argo-srv/SRV",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Starfarer",
  "official_role_verbatim": "Support / Heavy Refueling",
  "segments": [
   "Support",
   "Heavy Refueling"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/misc-starfarer/Starfarer",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Starfarer Gemini",
  "official_role_verbatim": "Support / Heavy Refueling",
  "segments": [
   "Support",
   "Heavy Refueling"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/misc-starfarer/Starfarer-Gemini",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Starlancer MAX",
  "official_role_verbatim": "Transport / Medium Freight",
  "segments": [
   "Transport",
   "Medium Freight"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/starlancer/Starlancer-MAX",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Starlancer TAC",
  "official_role_verbatim": "Combat / Gunship",
  "segments": [
   "Combat",
   "Gunship"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/starlancer/Starlancer-TAC",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Starlite",
  "official_role_verbatim": "Support / Light Refueling",
  "segments": [
   "Support",
   "Light Refueling"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/starlite/Starlite",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Stinger",
  "official_role_verbatim": "Combat / Heavy Fighter",
  "segments": [
   "Combat",
   "Heavy Fighter"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/stinger/Stinger",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Storm",
  "official_role_verbatim": "Combat / Light Tank",
  "segments": [
   "Combat",
   "Light Tank"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/storm/Storm",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Storm AA",
  "official_role_verbatim": "Combat / Light Tank",
  "segments": [
   "Combat",
   "Light Tank"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/storm/Storm-AA",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "STV",
  "official_role_verbatim": "Transporter / Passenger",
  "segments": [
   "Transporter",
   "Passenger"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/stv/STV",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "Syulen",
  "official_role_verbatim": "Multi-Role / Starter / Pathfinder",
  "segments": [
   "Multi-Role",
   "Starter",
   "Pathfinder"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/syulen/Syulen",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "Talon",
  "official_role_verbatim": "Combat / Light Fighter",
  "segments": [
   "Combat",
   "Light Fighter"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/talon/Talon",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Talon Shrike",
  "official_role_verbatim": "Combat / Light Fighter",
  "segments": [
   "Combat",
   "Light Fighter"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/talon/Talon-Shrike",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Terrapin",
  "official_role_verbatim": "Support / Pathfinder",
  "segments": [
   "Support",
   "Pathfinder"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/terrapin/Terrapin",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "Terrapin Medic",
  "official_role_verbatim": "Support / Medical",
  "segments": [
   "Support",
   "Medical"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/terrapin/Terrapin-Medic",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Tiburon",
  "official_role_verbatim": "Combat / Heavy Gunship",
  "segments": [
   "Combat",
   "Heavy Gunship"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/tiburon/Tiburon",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Tyilui",
  "official_role_verbatim": "Transporter / Snub Carrier",
  "segments": [
   "Transporter",
   "Snub Carrier"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/tyilui/Tyilui",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Ursa",
  "official_role_verbatim": "Exploration / Pathfinder",
  "segments": [
   "Exploration",
   "Pathfinder"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/ursa/Ursa",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "Ursa Fortuna",
  "official_role_verbatim": "Exploration / Pathfinder",
  "segments": [
   "Exploration",
   "Pathfinder"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/ursa/Ursa-Fortuna",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Ursa Medivac",
  "official_role_verbatim": "Support / Medical",
  "segments": [
   "Support",
   "Medical"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/ursa/Ursa-Medivac",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "UTV",
  "official_role_verbatim": "Transporter / Passenger",
  "segments": [
   "Transporter",
   "Passenger"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/utv/UTV",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "Valkyrie",
  "official_role_verbatim": "Combat / Dropship",
  "segments": [
   "Combat",
   "Dropship"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/anvil-valkyrie/Valkyrie",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Valkyrie Liberator Edition",
  "official_role_verbatim": "Combat / Dropship",
  "segments": [
   "Combat",
   "Dropship"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/anvil-valkyrie/Valkyrie-Liberator-Edition",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Vanguard Harbinger",
  "official_role_verbatim": "Combat / Heavy Fighter / Bomber",
  "segments": [
   "Combat",
   "Heavy Fighter",
   "Bomber"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/vanguard/Vanguard-Harbinger",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Vanguard Hoplite",
  "official_role_verbatim": "Combat / Dropship",
  "segments": [
   "Combat",
   "Dropship"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/vanguard/Vanguard-Hoplite",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Vanguard Sentinel",
  "official_role_verbatim": "Combat / Heavy Fighter / Bomber",
  "segments": [
   "Combat",
   "Heavy Fighter",
   "Bomber"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/vanguard/Vanguard-Sentinel",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Vanguard Warden",
  "official_role_verbatim": "Combat / Heavy Fighter",
  "segments": [
   "Combat",
   "Heavy Fighter"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/vanguard/Vanguard-Warden",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Vulcan",
  "official_role_verbatim": "Multi-role / Medium Repair / Medium Refuel",
  "segments": [
   "Multi-role",
   "Medium Repair",
   "Medium Refuel"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/vulcan/Vulcan",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Vulture",
  "official_role_verbatim": "Industrial / Light Salvage",
  "segments": [
   "Industrial",
   "Light Salvage"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/drake-vulture/Vulture",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "X1",
  "official_role_verbatim": "Exploration / Passenger",
  "segments": [
   "Exploration",
   "Passenger"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/x1/X1",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "X1 Force",
  "official_role_verbatim": "Combat / Passenger",
  "segments": [
   "Combat",
   "Passenger"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/x1/X1-Force",
  "store_view": "sale=true",
  "read_on": "2026-09-12"
 },
 {
  "name": "X1 Velocity",
  "official_role_verbatim": "Competition / Racing",
  "segments": [
   "Competition",
   "Racing"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/x1/X1-Velocity",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Zeus Mk II CL",
  "official_role_verbatim": "Transporter / Medium Freight",
  "segments": [
   "Transporter",
   "Medium Freight"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/zeus-mk-ii/Zeus-Mk-II-CL",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Zeus Mk II ES",
  "official_role_verbatim": "Exploration / Expedition",
  "segments": [
   "Exploration",
   "Expedition"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/zeus-mk-ii/Zeus-Mk-II-ES",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 },
 {
  "name": "Zeus Mk II MR",
  "official_role_verbatim": "Combat / Interdiction",
  "segments": [
   "Combat",
   "Interdiction"
  ],
  "url": "https://robertsspaceindustries.com/pledge/ships/zeus-mk-ii/Zeus-Mk-II-MR",
  "store_view": "sale=false",
  "read_on": "2026-09-12"
 }
]
```

*CIC, 2026-09-12. Re-filed to disk 2026-09-12 after Architecture reported the path empty;
rows are the original sweep output, not reconstructed.*
