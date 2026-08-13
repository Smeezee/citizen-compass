package main

// gamelog_mine.go - turn Star Citizen's own logs into a dataset, every session,
// automatically.
//
// # WHY THIS IS IN THE COLLECTOR AND NOT A SCRIPT
//
// The archive dig on 2026-08-07 was a Python script run by hand against 233
// sessions. It found four transaction families, 183 priced items, 31 shops and
// two and a half years of history. Then it stopped, because a script someone
// has to remember to run is a dataset that stops growing the day they forget.
//
// This is that script, in Go, inside the program that is already watching the
// game. It runs on start and again when the game exits, so the data accrues
// whether or not anybody thinks about it.
//
// # THE ARCHIVE IS THE PART PEOPLE MISS
//
// Star Citizen does NOT overwrite Game.log. It renames the old one into a
// logbackups folder beside the install and starts a new one. Every log header
// says so:
//
//	BackupNameAttachment=" Build(12399239) 07 Aug 26 (17 18 42)"  -- used by backup system
//
// So a new install of this tool does not start from zero. It starts from
// however long that player has been playing.
//
// # WHAT IT WILL NOT DO
//
// It never emits a raw log line, never emits a "context" field for debugging,
// and never emits an identifier. Fields are ALLOW-LISTED by name: anything CIG
// adds in a future patch is dropped unless somebody adds it here deliberately.
// That is the difference between stripping and filtering, and it is the only
// version of this that is safe to put on somebody else's computer.

import (
	"bufio"
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"sort"
	"strings"
	"time"
)

// --- patterns --------------------------------------------------------------
//
// Matched on the PAYLOAD SHAPE, never on the emitting class name.
//
// CIG renamed CEntityComponentShopUIProvider to CEntityComponentShoppingProvider
// between 4.9 and 4.10 and added a currencyType field. A parser keyed on the
// class name would have gone silent and looked exactly like a player who did
// not go shopping. Keying on the payload caught the rename AND found three
// transaction families nobody knew existed.

var (
	reMineTS    = regexp.MustCompile(`^<([0-9T:.\-]+Z)>`)
	reMineClass = regexp.MustCompile(`<(CEntityComponent[A-Za-z]+)::([A-Za-z_]+)>`)

	// SShopBuyRequest            item purchase
	// SShopSellRequest           item sale
	// SShopCommodityBuyRequest   commodity purchase
	// SShopCommoditySellRequest  commodity sale
	reMineTxn   = regexp.MustCompile(`S(Shop(?:Commodity)?)(Buy|Sell)Request\s*-\s*(.*)`)
	reMineField = regexp.MustCompile(`([A-Za-z_]+)\[([^\]]*)\]`)

	reMineLocation = regexp.MustCompile(`requested inventory for Location\[([^\]]+)\]`)

	// The three below were written months ago, compiled the whole time, and were
	// connected to nothing that reached the dataset. gamelog.go used them for the
	// per-capture sidecar; nothing carried them into the export. Wiring them up
	// was the cheapest expansion available and Sleven picked it first.
	//
	// All three require a QUOTED value, for a reason established the hard way. A
	// looser separator class ([=:\s"]+) walked out of one field and into the next
	// on this real line:
	//
	//	taskname="ResolveSpawnLocation" state=eCVS_UnstowPlayer(14)
	//
	// and reported the player's location as "state". A pattern that cannot cross
	// a field boundary cannot invent a value out of two unrelated fields.
	//
	// These are UNVERIFIED patterns - no in-world sample has confirmed them - and
	// they say so in the dataset itself, per extractor, rather than only in a
	// document nobody opens.
	reMineObjectContainer = regexp.MustCompile(`(?i)\bobjectcontainer="([^"]+)"`)
	reMineSpawnLocation   = regexp.MustCompile(`(?i)\bspawn_?location="([^"]+)"`)
	// INVESTIGATED 2026-08-13 and its zero is now an expectation, not a
	// suspicion. Its sibling reMineLocation is Verified and fires constantly,
	// which made a permanent zero right beside it look like a stale pattern.
	// It is not stale - it is speculative. 1038 RequestLocationInventory lines
	// across 235 archived logs, and not one carries name=". There is no
	// evidence CIG has ever written this form here.
	//
	// Left in place deliberately: it costs one regex per matching line and
	// would catch the form if it ever appears. Do not "fix" it by loosening
	// the pattern - the quoted-value rule above is what stops a location being
	// invented out of two unrelated fields, and a looser version of THIS
	// pattern would match the player handle on the same line.
	reMineLocInvName = regexp.MustCompile(`RequestLocationInventory[^\n]*?\bname="([^"]+)"`)
	reMineQT         = regexp.MustCompile(`Successfully calculated route to (\S+).*?fuel estimate ([0-9.]+)`)
	reMineShip       = regexp.MustCompile(`\b((?:AEGS|ANVL|ARGO|BANU|CNOU|CRUS|DRAK|ESPR|GAMA|GRIN|` +
		`KRIG|MISC|MRAI|ORIG|RSI|TMBL|VNCL|XIAN|XNAA|GLSN|APAR)_[A-Za-z0-9_]+?)_\d{6,}`)
	reMineBuild = regexp.MustCompile(`Changelist:\s*(\d+)`)
	reMineRes   = regexp.MustCompile(`Change resolution:\s*(\d+x\d+)\s*\(([^)]+)\)`)
	reMineD3D   = regexp.MustCompile(`D3D Adapter: FeatureLevel = (.+)`)

	// THE [VK] LOG CHANNEL, NOT THE WORD "Vulkan".
	//
	// This was `\bVulkan\b`, which matches the GPU driver's own capability
	// line - "Driver Version (581.57.0.0) Vulkan API (1.4.312)" - that the
	// driver prints whether or not the game is using Vulkan. Measured across
	// the 235-log archive on 2026-08-13:
	//
	//     logs with [VK] channel lines             79
	//     logs with [VK] AND a D3D Adapter line     0
	//     156 D3D + 79 VK = 235 = every log
	//
	// A perfect partition, and the one log that contains the WORD Vulkan
	// alongside a D3D Adapter line has zero [VK] lines - a DirectX session the
	// old pattern would have reported as Vulkan.
	//
	// It matters more now than it did: this answer goes in every sidecar, where
	// it is a claim about a specific session rather than a count in an
	// aggregate.
	reMineVulkan = regexp.MustCompile(`\[VK\]`)

	// Entity ids hide INSIDE otherwise harmless names. A quantum destination
	// came out of the archive as "PartyMemberMarker_200179793657" - another
	// player's entity id wearing a label. The first audit passed because it
	// only looked for bare digit strings, so it could not fail on that case.
	// Every free-text name now goes through scrubIDs before it can be written.
	reMineEmbeddedID = regexp.MustCompile(`\d{6,}`)

	// EVERY LINE STATES WHICH SUBSYSTEM WROTE IT. This is the discovery layer.
	//
	//	... [Team_GameSec][Salvage]
	//	... [Team_CoreGameplayFeatures][Cargo]
	//	... [Team_CGP4][QuantumTravel]
	//
	// 117 distinct tags across Sleven's 227-session archive. This is how the
	// collector stops needing to know about playstyles in advance.
	reMineTeam = regexp.MustCompile(`\[(Team_[A-Za-z0-9]+)\]\[([A-Za-z0-9]+)\]`)

	// THE GAME EXPLAINS ITSELF, AND NOBODY WAS LISTENING.
	//
	//	Notification "Cargo Spindles: To load cargo onto the Hull series of
	//	ships, the cargo spindles must be extended."
	//	Notification "Salvage - Hull Scraping: The Salvage Beam strips vehicle
	//	hulls into Recycled Material Composite"
	//
	// 347 distinct notifications in one player's archive. This is CIG's own
	// answer to "how do I do this", written into the log the moment a player
	// meets the mechanic - which is exactly the question a newcomer asks and
	// exactly the thing no wiki keeps current.
	//
	// RIGHTS FLAG, and it is not a small one: this is CIG's prose. Collecting
	// it locally is one thing; PUBLISHING it is the same open question that has
	// WO-1's 5,344 item descriptions on hold - see
	// claude/finding-description-rights-correction.md. Gathered, marked, and
	// NOT publishable until Sleven settles that. Rule 8.
	reMineNotify = regexp.MustCompile(`Notification "([^"]{20,400})"`)

	// What the player is actually holding or wearing. The line also carries
	// Player[handle], which is why only the class name is taken.
	reMineAttach = regexp.MustCompile(`Attachment\[([A-Za-z0-9_]+?)(?:_\d{6,})?,`)

	// Mission payouts, already priced by the game.
	reMineAward = regexp.MustCompile(`Notification "Awarded (\d+) aUEC`)

	// Contract names - the mission catalogue, as encountered.
	reMineContract = regexp.MustCompile(`Notification "Contract Accepted:\s*([^"]{3,160}?):?\s*"`)

	// Line-shape normalisation for the discovery layer. See SubsystemGap.
	reMineShapeNum   = regexp.MustCompile(`\d+`)
	reMineShapeQuote = regexp.MustCompile(`'[^']*'|"[^"]*"|\[[^\]]*\]`)

	// MISSION TEMPLATES, OBSERVED RATHER THAN ESTIMATED.
	//
	//	contract: TheCollector_Intro
	//	contract: Shubin_RG_FPSMine_Stanton_Intro_1
	//	contract: CleanAir_DefendShip_Easy_2
	//
	// These are CIG's internal mission template names, written when a contract
	// is running. The project already holds a mission-template count from the
	// game files - 106 exact plus a 700-1,051 estimate whose spread is an open
	// question. This is the other half of that: templates people ACTUALLY meet,
	// which is how an estimate gets checked rather than argued about.
	reMineContractID = regexp.MustCompile(`\bcontract:\s*([A-Za-z0-9_]{3,80})`)

	// What a mission actually asks you to do.
	//
	//	Text=Salvage the ~mission(ship)]
	//	Text=Locate Claim #~mission(ClaimNumber) near ~mission(location).]
	//
	// The ~mission(...) markers are CIG's own placeholders, kept as-is: they say
	// which fields a template fills in, which is more useful than a resolved
	// string that only describes one instance. Same rights flag as the tips.
	reMineObjective = regexp.MustCompile(`Text=([^\]]{6,120})\]`)

	// Rock type AND rarity tier, by name: MineableRock_SurfaceLegendary_Quantainium.
	reMineRock = regexp.MustCompile(`\b(MineableRock_[A-Za-z0-9_]+?)_\d{6,}`)
)

// scrubIDs replaces any run of six or more digits with a marker.
func scrubIDs(s string) string { return reMineEmbeddedID.ReplaceAllString(s, "<id>") }

// THE GOVERNING RULE FOR EVERYTHING DERIVED FROM ANYTHING - Sleven, 2026-08-13
//
//	A frame may contain a name. Nothing DERIVED from a frame ever may.
//
// The screenshots themselves are internal-only and are never published, so a
// picture is allowed to show a handle. The moment anything is EXTRACTED from
// one - by OCR, by a reader, by anything - that extraction is data, and data
// goes through the discipline below: NAME THE FIELDS THAT MAY EXIST, DROP THE
// REST. Not a filter that removes what looks like a name; an allow-list that
// admits only what is known to be safe.
//
// This is written here rather than in a document because of when it will be
// needed. Nothing reads frame contents today - the collector is scoped "NO OCR,
// no atlas, no vocabulary" in three file headers - so there is no code to guard
// and a guard for a path that does not exist would be a check that has never
// seen its subject.
//
// The day somebody builds the reading half, the frame data will not look like
// log data, and writing "a quick scrubber for the OCR output" will feel like
// the reasonable thing to do. THAT is the second, weaker mechanism the decision
// forbids. Extend this map, or write another one in this shape. Do not write a
// filter.
//
// Why an allow-list and never detection: §5b of the log-first order settled it.
// Handles look like ordinary words, so any heuristic either misses real ones or
// eats legitimate shop and item names - and both failures are silent. This
// map has never leaked across 308 rows precisely because it never had to
// recognise anything.
//
// mineTxnKeep is the allow-list. A field not named here never reaches disk.
var mineTxnKeep = map[string]bool{
	"shopName": true, "kioskId": true, "client_price": true,
	"itemClassGUID": true, "itemName": true, "quantity": true,
	"currencyType": true, "amount": true, "resourceGUID": true,
}

// mineForbidden is belt AND braces: checked even for allow-listed names, so a
// future CIG field called "shopName" carrying a handle still cannot get out.
var mineForbidden = map[string]bool{
	"playerId": true, "shopId": true, "sessionId": true, "shardId": true,
	"nickname": true, "node_id": true, "playerGEID": true,
	"accountId": true, "geid": true,
}

// --- the shapes that reach disk --------------------------------------------

// MineTxn is one observed transaction. There is no player in it, by design.
type MineTxn struct {
	TS       string `json:"ts"`
	Side     string `json:"side"`   // buy | sell
	Market   string `json:"market"` // item | commodity
	Shop     string `json:"shopName,omitempty"`
	Kiosk    string `json:"kioskId,omitempty"`
	Item     string `json:"itemName,omitempty"`
	ItemGUID string `json:"itemClassGUID,omitempty"`
	Price    string `json:"client_price,omitempty"`
	Quantity string `json:"quantity,omitempty"`
	Currency string `json:"currencyType,omitempty"`
	Amount   string `json:"amount,omitempty"`
	Resource string `json:"resourceGUID,omitempty"`
	EmitBy   string `json:"emitted_by,omitempty"`
	Build    string `json:"build,omitempty"`
	Channel  string `json:"channel,omitempty"`
}

// key identifies a transaction for dedup across runs. The same log will be
// re-read every session - the archive does not change - so without this the
// dataset would grow by a full copy of itself every time the game closed.
func (t MineTxn) key() string {
	return strings.Join([]string{t.TS, t.Side, t.Market, t.Shop, t.Item, t.Price, t.Amount}, "|")
}

// MineRoute is a quantum destination and every fuel figure seen for it.
// Multiple values are REAL - cost varies by origin - so they are kept as a set
// rather than averaged into a single number that means nothing.
type MineRoute struct {
	Destination string    `json:"destination"`
	Fuel        []float64 `json:"fuel_estimates"`
}

// MineSchemaVersion is the shape of gamelog-dataset.json.
//
// # WHY A NUMBER AND NOT "WE WILL FIGURE IT OUT"
//
// The moment a second person runs this, two exports written by two different
// builds have to be merged by something that was not present when either was
// written. Inferring a file's shape from its contents works right up until an
// absent field is ambiguous between "this version did not collect it" and "this
// player did not do it" - which is exactly the ambiguity this whole tool is
// built to avoid everywhere else.
//
// Version 1 is implicit: it is any file written before this field existed, and
// is detected by the field's absence.
const MineSchemaVersion = 3

// errMineSchemaNewer means the file on disk was written by a NEWER build than
// this one. It is fatal to the run on purpose - see loadMineStore.
var errMineSchemaNewer = fmt.Errorf("dataset was written by a newer version of this tool")

// MineExtractor describes one reader and how much it found.
//
// # THIS IS THE SILENT-PARSER CANARY, IN THE DATA
//
// CIG renamed the shop class between 4.9 and 4.10. A parser keyed to the old
// name would have gone quiet and looked exactly like a player who did not go
// shopping. The defence elsewhere is to key on payload shape; the defence here
// is arithmetic - an extractor sitting at zero hits across sessions where it
// should have fired is a parser about to be discovered six months late.
//
// Verified says whether a real in-world sample ever confirmed the pattern.
// Carrying that flag in the FILE rather than in a document means somebody
// merging a stranger's export can tell a fact from a hint without having read
// anything this project wrote.
type MineExtractor struct {
	Name     string `json:"name"`
	Emits    string `json:"emits"`
	Verified bool   `json:"pattern_verified"`
	Hits     int    `json:"hits"`
	Note     string `json:"note,omitempty"`
}

// mineExtractorTable is the static description. Hits are merged in from the
// loaded file at save time.
var mineExtractorTable = []MineExtractor{
	{Name: "transaction", Emits: "transactions[]", Verified: true,
		Note: "matched on payload shape, not on the emitting class name"},
	{Name: "location_inventory", Emits: "locations{}", Verified: true,
		Note: `confirmed live in 4.10 - "requested inventory for Location[...]"`},
	{Name: "quantum_route", Emits: "quantum_routes{}", Verified: true,
		Note: "destination and fuel estimate, confirmed live in 4.10"},
	{Name: "ship_class", Emits: "ship_classes{}", Verified: true,
		Note: "manufacturer-prefixed class names; entity ids stripped"},
	{Name: "object_container", Emits: "object_containers{}", Verified: false,
		Note: "fires on BOARDING, so it reports the container the player entered - " +
			"usually their own ship. A data event, never a capture trigger."},
	{Name: "spawn_location", Emits: "spawn_locations{}", Verified: false,
		Note: "quoted value only; no in-world sample has confirmed this pattern"},
	{Name: "mission_template", Emits: "mission_templates_seen{}", Verified: true,
		Note: "CIG's internal template names, observed in play - the check on the " +
			"106-exact-plus-estimated count taken from the game files"},
	{Name: "mission_objective", Emits: "mission_objectives{}", Verified: true,
		Note: "objective text with CIG's ~mission(...) placeholders kept intact. " +
			"CIG PROSE - same rights hold as game_tip"},
	{Name: "game_tip", Emits: "game_tips{}", Verified: true,
		Note: "CIG's own instructional text. NOT PUBLISHABLE until the description-" +
			"rights question is settled - see finding-description-rights-correction.md"},
	{Name: "equipment", Emits: "equipment_seen{}", Verified: true,
		Note: "tool, weapon and armour classes observed in use; the player name on " +
			"the same line is never taken"},
	{Name: "mission_payout", Emits: "mission_payouts_auec{}", Verified: true,
		Note: "the game states the reward in aUEC"},
	{Name: "contract", Emits: "contracts_seen{}", Verified: true,
		Note: "contract titles as encountered"},
	{Name: "actor_death", Emits: "deaths{}", Verified: true,
		Note: "weapon, damage type, zone and player-or-NPC. Names are shape-checked " +
			"and replaced with <player> unless they look like a game asset"},
	{Name: "vehicle_destroyed", Emits: "vehicles_destroyed{}", Verified: true,
		Note: "ship class and zone"},
	{Name: "mineable_rock", Emits: "mineable_rocks{}", Verified: true,
		Note: "rock class name carries type and rarity tier, e.g. SurfaceLegendary_Quantainium"},
	{Name: "location_inventory_name", Emits: "locations{}", Verified: false,
		Note: `EXPECTED ZERO, MEASURED 2026-08-13. Speculative: the name="..." ` +
			`form has never appeared in this subsystem. Across 235 archived logs ` +
			`(2024-09 to 2025-11) there are 1038 RequestLocationInventory lines ` +
			`and NONE carry name=". 1029 match the verified Location[...] reader ` +
			`beside it; the other 9 are INVALID_LOCATION_ID, which is the game ` +
			`saying a place has no inventory and is correctly not a location. ` +
			`Kept because it costs one regex and would catch the form if CIG ever ` +
			`writes it - not because anything is waiting on it.`},
}

// SubsystemGap is one thing the game did that this tool cannot yet read.
// SubsystemGap is one thing the game did that this tool cannot yet read.
//
// # LINES IS A LIAR, AND IT COST A RECOMMENDATION
//
// The first version ranked gaps by line count. Cargo came top with 177,851
// lines, so it was named "the single biggest blind spot in the log" and queued
// as the next thing to build. Then somebody looked at the actual lines:
//
//	22,236  "...transitioning light state in current platform state: OpenIdle"
//	 3,352  "...stopping effects in current platform state: OpenIdle"
//	 2,692  "...Platform state changed to OpenIdle"
//
// It is a freight elevator turning its lights on and off. One fact, repeated
// twenty thousand times, ranked above everything else in the game because
// volume was mistaken for substance.
//
// So gaps now carry SHAPES: the number of DISTINCT line forms, counted after
// stripping numbers, ids and quoted values. A subsystem with 177,851 lines and
// 12 shapes is a machine repeating itself. One with 400 lines and 300 shapes is
// a seam worth mining. Both numbers are reported, because the ratio between
// them is the actual signal.
type SubsystemGap struct {
	Subsystem string `json:"subsystem"`
	Lines     int    `json:"lines"`
	Shapes    int    `json:"distinct_shapes"`
}

// lineShape reduces a line to its form: numbers, quoted strings and bracketed
// values all collapse, so twenty thousand elevator events become one shape.
func lineShape(s string) string {
	s = reMineShapeQuote.ReplaceAllString(s, "*")
	s = reMineShapeNum.ReplaceAllString(s, "#")
	if len(s) > 120 {
		s = s[:120]
	}
	return s
}

// coveredSubsystems names the tags an extractor actually reads. Everything else
// is reported as a gap. Deliberately short and honest - overstating coverage
// here would turn the discovery layer into decoration.
var coveredSubsystems = map[string]bool{
	"Transaction":   true, // shop buy/sell
	"QuantumTravel": true, // routes and fuel
}

// MineStore is the accumulated dataset. It is merged, never overwritten.
type MineStore struct {
	SchemaVersion int    `json:"schema_version"`
	Generated     string `json:"generated"`
	ToolVersion   string `json:"tool_version"`

	// Contributor identity. Empty is a legitimate state and is explained in
	// the export README rather than left as a blank field to be puzzled over.
	InstallID    string `json:"install_id,omitempty"`
	InstallSince string `json:"install_first_seen,omitempty"`

	Privacy      string               `json:"privacy"`
	SessionsSeen []string             `json:"sessions_seen"`
	Extractors   []MineExtractor      `json:"extractors"`
	Builds       map[string]int       `json:"builds"`
	ShopClasses  map[string]int       `json:"shop_class_names"`
	Locations    map[string]int       `json:"locations"`
	Ships        map[string]int       `json:"ship_classes"`
	Routes       map[string][]float64 `json:"quantum_routes"`

	// Wired in 2026-08-08. Both are UNVERIFIED-pattern output; see Extractors.
	ObjectContainers map[string]int `json:"object_containers"`
	SpawnLocations   map[string]int `json:"spawn_locations"`

	// Mineable rock class names, carrying type and rarity tier.
	Rocks map[string]int `json:"mineable_rocks"`

	// THE DISCOVERY LAYER - see reMineTeam.
	//
	// Subsystems counts every "[Team_X][Subsystem]" tag the game wrote.
	// Uncovered lists the ones no extractor reads yet, biggest first.
	//
	// # WHY THIS IS THE ANSWER TO "IT HAS TO WORK FOR EVERY PLAYSTYLE"
	//
	// Sleven: "people doing FPS combat, people doing mining, cargo, salvage,
	// bounty hunting - any of that needs to be accounted for."
	//
	// You cannot enumerate playstyles in advance, and trying is how a collector
	// ends up useful to exactly one person. His own archive proves it: he has
	// not been mining, so it holds 6 rock mentions and 167,471 cargo ones. A
	// miner's log would be the reverse. An FPS player's would light up tags
	// neither of them has ever produced.
	//
	// So the collector does not guess. It counts what the game says it was
	// doing, and REPORTS WHAT IT DOES NOT UNDERSTAND. When this ships to
	// somebody who does something nobody here has done, their export arrives
	// carrying a list of the subsystems we are blind to, ranked by how much
	// they happened. The roadmap writes itself out of other people's play
	// instead of out of a meeting.
	// Combat. See mineCombatLine - these carry no player names by construction.
	Deaths        map[string]int `json:"deaths"`
	VehicleLosses map[string]int `json:"vehicles_destroyed"`

	// The game's own explanatory text. CIG's prose - see reMineNotify's rights
	// flag. Collected, marked not-publishable.
	GameTips map[string]int `json:"game_tips_CIG_TEXT_NOT_PUBLISHABLE"`

	// Equipment observed in use: tools, weapons, armour, consumables.
	Equipment map[string]int `json:"equipment_seen"`

	// Mission payouts and the contracts that paid them.
	Payouts   map[string]int `json:"mission_payouts_auec"`
	Contracts map[string]int `json:"contracts_seen"`

	// Mission template names as encountered, and what they ask you to do.
	// Objective text is CIG's - same rights hold as the tips.
	MissionTemplates map[string]int `json:"mission_templates_seen"`
	Objectives       map[string]int `json:"mission_objectives_CIG_TEXT_NOT_PUBLISHABLE"`

	Subsystems map[string]int `json:"subsystems"`

	// shapes is the distinct-form set per subsystem, capped so a chatty
	// subsystem cannot grow this without bound. Not serialised - the counts
	// that matter are folded into Uncovered at save time.
	shapes    map[string]map[string]struct{}
	Uncovered []SubsystemGap `json:"subsystems_not_yet_read"`

	Txns []MineTxn `json:"transactions"`

	// SentTxnKeys is the dedup key of every transaction row a receiver has
	// confirmed getting a byte-for-byte copy of (see MarkTxnsSent). Only the
	// KEY survives - the row itself is removed from Txns entirely, which is
	// what stops every export after the first from carrying the whole
	// history again.
	//
	// Keeping the key and dropping the content is the whole trick. Dropping
	// the key too would "fix" the resend problem by making the row look
	// brand new the next time its log line is read - mineOneLog re-reads the
	// same archive forever (see MineAll's doc comment), and dedup only ever
	// looks at what CURRENTLY sits in Txns. So the key has to persist
	// somewhere Txns no longer holds it, permanently, or the next log scan
	// resurrects everything this dataset has ever sent.
	SentTxnKeys map[string]bool `json:"sent_txn_keys,omitempty"`

	// hits accumulates per-extractor counts during a run. Not serialised
	// directly - it is folded into Extractors at save time.
	hits map[string]int
}

// noteHit records that an extractor fired. Nil-safe so a store built by an
// older code path cannot panic here.
func (st *MineStore) noteHit(name string) {
	if st.hits == nil {
		st.hits = map[string]int{}
	}
	st.hits[name]++
}

const minePrivacyNote = "No player handle, playerId, shopId, session id, shard id, " +
	"account id or other player's name appears in this file. Fields are allow-listed " +
	"by name, so anything the game adds in a future patch is dropped rather than " +
	"emitted. Any run of six or more digits inside a name is replaced with <id>. " +
	"No raw log line is ever included. The install_id is 16 random bytes and is not " +
	"derived from you, your handle, your account or your hardware."

func newMineStore() *MineStore {
	return &MineStore{
		SchemaVersion:    MineSchemaVersion,
		ToolVersion:      Version,
		Privacy:          minePrivacyNote,
		Builds:           map[string]int{},
		ShopClasses:      map[string]int{},
		Locations:        map[string]int{},
		Ships:            map[string]int{},
		Routes:           map[string][]float64{},
		ObjectContainers: map[string]int{},
		SpawnLocations:   map[string]int{},
		Rocks:            map[string]int{},
		GameTips:         map[string]int{},
		MissionTemplates: map[string]int{},
		Objectives:       map[string]int{},
		Equipment:        map[string]int{},
		Payouts:          map[string]int{},
		Contracts:        map[string]int{},
		Deaths:           map[string]int{},
		VehicleLosses:    map[string]int{},
		Subsystems:       map[string]int{},
		SentTxnKeys:      map[string]bool{},
		shapes:           map[string]map[string]struct{}{},
		hits:             map[string]int{},
	}
}

// --- reading one log -------------------------------------------------------

// mineOneLog reads a single Game.log and folds it into the store.
//
// Encoding is stated (hard rule 15). Logs are UTF-8 with the occasional stray
// byte from a crash mid-write; Go's scanner tolerates that, and a bad byte must
// not truncate an otherwise good session.
// mineLineInto is the single definition of "what one log line contributes".
// Both the archive walk and the live tailer go through it, so the two can
// never drift into extracting different things from the same file.
func mineLineInto(st *MineStore, line, build, channel string) {

	if m := reMineBuild.FindStringSubmatch(line); m != nil {
		st.Builds[m[1]]++
	}
	if m := reMineRes.FindStringSubmatch(line); m != nil {
		// Renderer and window mode are stated in the log. This is the whole
		// of the diagnostic that cost two evenings of guessing about the
		// dead hotkey, available for free from a file already being read.
		st.ShopClasses["_display:"+scrubIDs(strings.TrimSpace(m[2]))]++
	}
	if m := reMineD3D.FindStringSubmatch(line); m != nil {
		st.ShopClasses["_renderer:"+strings.TrimSpace(m[1])]++
	} else if reMineVulkan.MatchString(line) {
		st.ShopClasses["_renderer:Vulkan"]++
	}

	var emitBy string
	if m := reMineClass.FindStringSubmatch(line); m != nil {
		emitBy = m[1]
		if strings.Contains(m[1], "Shop") {
			st.ShopClasses[m[1]+"::"+m[2]]++
		}
	}

	if m := reMineTxn.FindStringSubmatch(line); m != nil {
		fields := map[string]string{}
		for _, f := range reMineField.FindAllStringSubmatch(m[3], -1) {
			if mineTxnKeep[f[1]] && !mineForbidden[f[1]] {
				fields[f[1]] = f[2]
			}
		}
		if len(fields) > 0 {
			st.noteHit("transaction")
			ts := ""
			if t := reMineTS.FindStringSubmatch(line); t != nil {
				ts = t[1]
			}
			market := "item"
			if strings.HasSuffix(m[1], "Commodity") {
				market = "commodity"
			}
			st.Txns = append(st.Txns, MineTxn{
				TS: ts, Side: strings.ToLower(m[2]), Market: market,
				Shop:     scrubIDs(fields["shopName"]),
				Kiosk:    fields["kioskId"],
				Item:     scrubIDs(fields["itemName"]),
				ItemGUID: fields["itemClassGUID"],
				Price:    fields["client_price"],
				Quantity: fields["quantity"],
				Currency: fields["currencyType"],
				Amount:   fields["amount"],
				Resource: fields["resourceGUID"],
				EmitBy:   emitBy, Build: build, Channel: channel,
			})
		}
	}

	if m := reMineLocation.FindStringSubmatch(line); m != nil {
		st.Locations[scrubIDs(m[1])]++
		st.noteHit("location_inventory")
	}
	if m := reMineQT.FindStringSubmatch(line); m != nil {
		d := scrubIDs(m[1])
		var v float64
		fmt.Sscanf(m[2], "%g", &v)
		if !containsFloat(st.Routes[d], v) {
			st.Routes[d] = append(st.Routes[d], v)
		}
		st.noteHit("quantum_route")
	}
	for _, s := range reMineShip.FindAllStringSubmatch(line, -1) {
		st.Ships[s[1]]++
		st.noteHit("ship_class")
	}

	// --- the three that were compiled and connected to nothing ----------
	//
	// Every one of these goes through the SAME two guards as the verified
	// extractors, in this order:
	//
	//   plausibleLocation  rejects CryEngine state enums (eCVS_*) and the
	//                      known structural tokens - "state", "taskname",
	//                      "null" - that a pattern matching the wrong key
	//                      would otherwise report as a place.
	//   scrubIDs           replaces any run of 6+ digits. This is the guard
	//                      that the FIRST privacy audit missed: an object
	//                      container is very often a ship, and a ship in
	//                      this log looks like DRAK_Vulture_864140490741 -
	//                      an entity id wearing a name. The audit checked
	//                      bare digit strings, so it could not fail on that
	//                      case, and passing was not the same as being right.
	//
	// Order matters: reject first, then scrub. Scrubbing first would turn
	// eCVS_UnstowPlayer(14) into something plausibleLocation still rejects,
	// but would also mean the rejection list is comparing against a string
	// the log never contained.
	mineCombatLine(st, line)

	// --- missions -----------------------------------------------------------
	if m := reMineContractID.FindStringSubmatch(line); m != nil {
		st.MissionTemplates[m[1]]++
		st.noteHit("mission_template")
	}
	if m := reMineObjective.FindStringSubmatch(line); m != nil {
		v := strings.TrimSpace(m[1])
		// The game writes a placeholder before a template is populated. It is
		// not an objective, it is the absence of one, and counting it would put
		// a fake step in every mission's list.
		if v != "" && !strings.Contains(v, "UNINITIALIZED") {
			st.Objectives[scrubIDs(v)]++
			st.noteHit("mission_objective")
		}
	}

	// --- what the game says, and what the player is holding -----------------
	if m := reMineAward.FindStringSubmatch(line); m != nil {
		st.Payouts[m[1]]++
		st.noteHit("mission_payout")
	} else if m := reMineContract.FindStringSubmatch(line); m != nil {
		st.Contracts[scrubIDs(strings.TrimSpace(m[1]))]++
		st.noteHit("contract")
	} else if m := reMineNotify.FindStringSubmatch(line); m != nil {
		// Only tips - text that TEACHES. A notification naming a place or a
		// person is an event, not instruction, and the two are told apart by
		// the colon-then-sentence shape CIG uses for tips.
		txt := strings.TrimSpace(m[1])
		if i := strings.Index(txt, ": "); i > 0 && i < 40 && strings.HasSuffix(txt, ".") {
			st.GameTips[scrubIDs(txt)]++
			st.noteHit("game_tip")
		}
	}
	for _, a := range reMineAttach.FindAllStringSubmatch(line, -1) {
		if v := strings.TrimSpace(a[1]); len(v) > 2 {
			st.Equipment[v]++
			st.noteHit("equipment")
		}
	}

	// Discovery: what subsystem wrote this line, and did we read it?
	if m := reMineTeam.FindStringSubmatch(line); m != nil {
		st.Subsystems[m[2]]++
		if st.shapes == nil {
			st.shapes = map[string]map[string]struct{}{}
		}
		set := st.shapes[m[2]]
		if set == nil {
			set = map[string]struct{}{}
			st.shapes[m[2]] = set
		}
		// Capped: past 400 distinct forms a subsystem is already known to be
		// rich, and counting further only costs memory.
		if len(set) < 400 {
			set[lineShape(line)] = struct{}{}
		}
	}
	for _, r := range reMineRock.FindAllStringSubmatch(line, -1) {
		st.Rocks[r[1]]++
		st.noteHit("mineable_rock")
	}

	if m := reMineObjectContainer.FindStringSubmatch(line); m != nil {
		if v := strings.TrimSpace(m[1]); plausibleLocation(v) {
			st.ObjectContainers[scrubIDs(v)]++
			st.noteHit("object_container")
		}
	}
	if m := reMineSpawnLocation.FindStringSubmatch(line); m != nil {
		if v := strings.TrimSpace(m[1]); plausibleLocation(v) {
			st.SpawnLocations[scrubIDs(v)]++
			st.noteHit("spawn_location")
		}
	}
	if m := reMineLocInvName.FindStringSubmatch(line); m != nil {
		if v := strings.TrimSpace(m[1]); plausibleLocation(v) {
			st.Locations[scrubIDs(v)]++
			st.noteHit("location_inventory_name")
		}
	}
}

func mineOneLog(path string, st *MineStore) error {
	f, err := openSharedRead(path) // shared-read: the game may still hold it
	if err != nil {
		return err
	}
	defer f.Close()

	channel := "LIVE"
	lower := strings.ToLower(path)
	for _, c := range []string{"eptu", "tech-preview", "ptu"} {
		if strings.Contains(lower, string(filepath.Separator)+c+string(filepath.Separator)) {
			channel = strings.ToUpper(c)
			break
		}
	}

	var build string
	// Some Game.log lines are enormous (the OC hierarchy dump, cvar blocks).
	// bufio.Scanner's default 64KB limit would return an error mid-file and
	// silently end the read, so the buffer is raised and the error is checked.
	sc := bufio.NewScanner(f)
	sc.Buffer(make([]byte, 0, 256*1024), 8*1024*1024)
	for sc.Scan() {
		mineLineInto(st, sc.Text(), build, channel)
	}

	// The scanner's error is RETURNED, not discarded. A truncated read has to
	// be visible: a log that stopped early looks exactly like a short session.
	return sc.Err()
}

func containsFloat(xs []float64, v float64) bool {
	for _, x := range xs {
		if x == v {
			return true
		}
	}
	return false
}

// --- finding every log on the machine --------------------------------------

// MineTargets returns every Game.log worth reading: the live ones for each
// installed channel, plus every archived session in each channel's logbackups.
//
// This is what makes a fresh install useful on day one. On a machine that has
// been playing for two years, logbackups is two years of sessions.
// mineTargets is the injection point for the filesystem half of mining.
//
// It exists because a test that seeds its own store still had the real archive
// mined into it: BuildExport -> MineAll -> MineTargets() walks real drive
// letters, so the sent-rows checks found 309 rows where they had planted 1, and
// passed only on machines with no Star Citizen installed.
//
// Production always uses MineTargets. Only a selftest ever replaces it, and it
// restores it in a defer.
var mineTargets = MineTargets

func MineTargets() []string {
	var out []string
	seen := map[string]bool{}
	add := func(p string) {
		if p == "" || seen[p] {
			return
		}
		if _, err := os.Stat(p); err == nil {
			seen[p] = true
			out = append(out, p)
		}
	}

	var roots []string
	for _, drive := range []string{"C:", "D:", "E:", "F:"} {
		roots = append(roots,
			drive+`\Program Files\Roberts Space Industries\StarCitizen`,
			drive+`\Roberts Space Industries\StarCitizen`)
	}
	for _, r := range roots {
		for _, ch := range []string{"LIVE", "PTU", "EPTU", "TECH-PREVIEW"} {
			add(filepath.Join(r, ch, "Game.log"))
			backups := filepath.Join(r, ch, "logbackups")
			entries, err := os.ReadDir(backups)
			if err != nil {
				continue
			}
			for _, e := range entries {
				if !e.IsDir() && strings.EqualFold(filepath.Ext(e.Name()), ".log") {
					add(filepath.Join(backups, e.Name()))
				}
			}
		}
	}
	sort.Strings(out)
	return out
}

// --- the run ---------------------------------------------------------------

// MineAll reads every target and merges into the store on disk.
//
// It is idempotent: re-reading the same archive does not duplicate a single
// row, because transactions dedup on their own content. That matters because
// this runs on every game exit, forever, against a folder that mostly does not
// change.
func MineAll(outDir string, in Install, logf func(string, ...interface{})) (*MineStore, error) {
	if logf == nil {
		logf = func(string, ...interface{}) {}
	}
	st, err := loadMineStore(outDir)
	if err != nil {
		// A dataset from a NEWER build is not a broken file to be replaced. It
		// is a file this build must not touch. Returning here means nothing is
		// written, so the original survives intact.
		if errors.Is(err, errMineSchemaNewer) {
			logf("mine: STOPPING - %v", err)
			logf("mine: gamelog-dataset.json has been left exactly as it was. Update this " +
				"tool, or move that file aside if you meant to start over.")
			return nil, err
		}
		logf("mine: could not read existing dataset (%v) - starting a new one", err)
		st = newMineStore()
	}

	before := len(st.Txns)

	targets := mineTargets()
	fresh := 0
	failed := 0
	for _, p := range targets {
		if err := mineOneLog(p, st); err != nil {
			failed++
			logf("mine: %s could not be read: %v", filepath.Base(p), err)
			continue
		}
		fresh++
	}

	// Dedup in one pass at the end, preserving first-seen order - AND drop
	// anything a receiver has already confirmed. See dedupAgainstSent: this is
	// the one place that checks EVERY row just mined against EVERY row ever
	// marked sent, which is what stops a row from resurfacing just because the
	// archive that produced it is still sitting on disk being re-read every
	// session.
	var resurrected int
	st.Txns, resurrected = dedupAgainstSent(st.Txns, st.SentTxnKeys)
	if resurrected > 0 {
		logf("mine: %d already-sent row(s) seen again in the archive - not re-added, "+
			"your last confirmed send still covers them", resurrected)
	}

	st.SchemaVersion = MineSchemaVersion
	st.Generated = time.Now().UTC().Format(time.RFC3339)
	st.ToolVersion = Version
	st.Privacy = minePrivacyNote
	st.InstallID, st.InstallSince = in.ID, in.FirstSeen
	st.Extractors = buildExtractors(st)
	st.Uncovered = buildGaps(st)
	st.SessionsSeen = []string{fmt.Sprintf("%d logs read, %d unreadable", fresh, failed)}

	if err := saveMineStore(outDir, st); err != nil {
		return st, err
	}

	added := len(st.Txns) - before
	buys, sells := 0, 0
	for _, t := range st.Txns {
		if t.Side == "sell" {
			sells++
		} else {
			buys++
		}
	}
	// SAY WHAT CHANGED, INCLUDING WHEN NOTHING DID.
	//
	// "0 new" after a session is information: it means the player did not trade,
	// OR it means the parser has stopped matching because CIG renamed something.
	// Those look identical from the outside, which is why shop_class_names is
	// written alongside - a class that stops appearing in new builds is a
	// parser about to go quiet.
	logf("mine: %d logs read (%d unreadable), %d new rows, %d total (%d buy, %d sell), "+
		"%d locations, %d ships, %d quantum destinations, %d object containers, "+
		"%d spawn locations",
		fresh, failed, added, len(st.Txns), buys, sells,
		len(st.Locations), len(st.Ships), len(st.Routes),
		len(st.ObjectContainers), len(st.SpawnLocations))

	// NAME THE EXTRACTORS THAT FOUND NOTHING.
	//
	// This is the whole point of the extractor table. A silent parser and an
	// uneventful session produce identical output, and the difference only
	// becomes visible when somebody is told which readers were quiet. Saying it
	// every run means the day CIG renames something, the line that mattered was
	// already on screen rather than buried in a JSON file nobody opened.
	var quiet []string
	for _, e := range buildExtractors(st) {
		if e.Hits == 0 {
			quiet = append(quiet, e.Name)
		}
	}
	// THE COLLECTOR SAYS WHAT IT IS BLIND TO.
	if len(st.Uncovered) > 0 {
		var top []string
		for i, g := range st.Uncovered {
			if i == 5 {
				break
			}
			top = append(top, fmt.Sprintf("%s (%d shapes / %d lines)",
				g.Subsystem, g.Shapes, g.Lines))
		}
		logf("mine: the game used %d subsystems this archive; %d have an extractor. "+
			"Biggest gaps: %s", len(st.Subsystems),
			len(st.Subsystems)-len(st.Uncovered), strings.Join(top, ", "))
		logf("mine: that list is the to-do list, and it is ranked by what YOU actually " +
			"do in game. Somebody who mines or fights will produce a different one.")
	}
	if len(quiet) > 0 && fresh > 0 {
		logf("mine: these readers have never matched anything: %s. That is expected for "+
			"things you have not done - but if one covers something you KNOW you did, "+
			"its pattern has stopped matching.", strings.Join(quiet, ", "))
	}
	if added == 0 && fresh > 0 {
		logf("mine: nothing new this pass. That is normal after a session with no " +
			"trading - but if it stays 0 across sessions where you DID trade, check " +
			"gamelog-dataset.json's shop_class_names for a name that stopped appearing.")
	}
	return st, nil
}

// dedupAgainstSent removes exact-duplicate rows within txns AND any row whose
// key already appears in sent, preserving first-seen order.
//
// Split out from MineAll so it can be tested without touching the
// filesystem-scanning half of mining - MineTargets() walks real drive
// letters looking for a real game install, which a unit test has neither.
// This is the one function that actually decides whether a row survives, so
// it is also the one worth being able to call directly with a hand-built
// SentTxnKeys map and prove the resurrection case fails the way it is meant
// to.
//
// Returns the filtered slice and how many rows were dropped specifically
// because they were already sent, as opposed to being a plain in-run
// duplicate - "you traded twice" and "your last send already has this" are
// different facts, and folding them into one count would hide whichever one
// stopped being true.
func dedupAgainstSent(txns []MineTxn, sent map[string]bool) (out []MineTxn, alreadySent int) {
	out = txns[:0]
	seen := map[string]bool{}
	for _, t := range txns {
		k := t.key()
		if sent[k] {
			alreadySent++
			continue
		}
		if seen[k] {
			continue
		}
		seen[k] = true
		out = append(out, t)
	}
	return out, alreadySent
}

// txnKeys returns the dedup key of every row given, in order. BuildExport
// uses this to record exactly which rows a given zip claims to carry, so
// SendExport can tell MarkTxnsSent precisely what a receiver just confirmed -
// never "whatever the store holds right now", which could include a row
// mined in the gap between the zip being written and the receipt coming
// back.
func txnKeys(txns []MineTxn) []string {
	out := make([]string, 0, len(txns))
	for _, t := range txns {
		out = append(out, t.key())
	}
	return out
}

func mineStorePath(outDir string) string {
	return filepath.Join(outDir, "gamelog-dataset.json")
}

func loadMineStore(outDir string) (*MineStore, error) {
	p := mineStorePath(outDir)
	b, err := os.ReadFile(p)
	if err != nil {
		if os.IsNotExist(err) {
			return newMineStore(), nil
		}
		return nil, err
	}
	st := newMineStore()

	// ZEROED ON PURPOSE, AND THE SELFTEST IS WHY.
	//
	// newMineStore stamps the CURRENT version. Unmarshalling a file that has no
	// schema_version key leaves that stamp untouched, so the "absence means v1"
	// branch below could never be reached and the version check was decoration -
	// every old file would have reported itself as current. Nothing downstream
	// broke, which is exactly what made it hard to see.
	//
	// Found by runMineSchemaSelftest, not by reading this function.
	st.SchemaVersion = 0

	if err := json.Unmarshal(b, st); err != nil {
		return nil, err
	}

	// A file with no schema_version predates the field. That is version 1, not
	// a corrupt file, and it upgrades in place.
	if st.SchemaVersion == 0 {
		st.SchemaVersion = 1
	}

	// REFUSING TO PROCEED IS THE POINT.
	//
	// If a newer build wrote this file, this build does not know every field in
	// it. Unmarshalling drops what it does not recognise, and the very next save
	// would write the survivors back over the original - a silent, total loss of
	// whatever the newer version had collected, with a completed run and a
	// cheerful log line to go with it.
	//
	// So: stop. Do not load it, do not merge into it, and above all do not save
	// over it. The caller reports this and leaves the file exactly as it found
	// it. This costs one confusing evening if somebody downgrades; the
	// alternative costs a dataset.
	if st.SchemaVersion > MineSchemaVersion {
		return nil, fmt.Errorf("%w: file is schema v%d, this build understands v%d",
			errMineSchemaNewer, st.SchemaVersion, MineSchemaVersion)
	}

	if st.Builds == nil {
		st.Builds = map[string]int{}
	}
	if st.ShopClasses == nil {
		st.ShopClasses = map[string]int{}
	}
	if st.Locations == nil {
		st.Locations = map[string]int{}
	}
	if st.Ships == nil {
		st.Ships = map[string]int{}
	}
	if st.Routes == nil {
		st.Routes = map[string][]float64{}
	}
	if st.ObjectContainers == nil {
		st.ObjectContainers = map[string]int{}
	}
	if st.SpawnLocations == nil {
		st.SpawnLocations = map[string]int{}
	}
	if st.Rocks == nil {
		st.Rocks = map[string]int{}
	}
	if st.Subsystems == nil {
		st.Subsystems = map[string]int{}
	}
	if st.Deaths == nil {
		st.Deaths = map[string]int{}
	}
	if st.GameTips == nil {
		st.GameTips = map[string]int{}
	}
	if st.MissionTemplates == nil {
		st.MissionTemplates = map[string]int{}
	}
	if st.Objectives == nil {
		st.Objectives = map[string]int{}
	}
	if st.Equipment == nil {
		st.Equipment = map[string]int{}
	}
	if st.Payouts == nil {
		st.Payouts = map[string]int{}
	}
	if st.Contracts == nil {
		st.Contracts = map[string]int{}
	}
	if st.VehicleLosses == nil {
		st.VehicleLosses = map[string]int{}
	}
	if st.SentTxnKeys == nil {
		st.SentTxnKeys = map[string]bool{}
	}

	// Carry the previous run's per-extractor counts forward. Unknown names are
	// kept too: a file written by a newer build cannot reach here (the guard
	// above stops it), but a name retired from mineExtractorTable would
	// otherwise vanish from the record of what this dataset was built from.
	st.hits = map[string]int{}
	for _, e := range st.Extractors {
		st.hits[e.Name] += e.Hits
	}
	return st, nil
}

// buildExtractors folds accumulated hits into the described table, keeping any
// extractor name present in the file but absent from the table.
func buildExtractors(st *MineStore) []MineExtractor {
	out := make([]MineExtractor, 0, len(mineExtractorTable))
	named := map[string]bool{}
	for _, e := range mineExtractorTable {
		named[e.Name] = true
		e.Hits = st.hits[e.Name]
		out = append(out, e)
	}
	var retired []string
	for name := range st.hits {
		if !named[name] {
			retired = append(retired, name)
		}
	}
	sort.Strings(retired)
	for _, name := range retired {
		out = append(out, MineExtractor{
			Name: name, Emits: "(unknown)", Hits: st.hits[name],
			Note: "recorded by a build that described this extractor differently; " +
				"kept so the count is not silently lost",
		})
	}
	return out
}

// saveMineStore writes atomically. A half-written dataset that looks complete
// is worse than no dataset, and this file is appended to for years.
func saveMineStore(outDir string, st *MineStore) error {
	if err := os.MkdirAll(outDir, 0o755); err != nil {
		return err
	}
	b, err := json.MarshalIndent(st, "", "  ")
	if err != nil {
		return err
	}
	final := mineStorePath(outDir)
	tmp := final + ".tmp"
	if err := os.WriteFile(tmp, b, 0o644); err != nil {
		return err
	}
	return os.Rename(tmp, final)
}

// MarkTxnsSent is called ONLY after a receiver has confirmed a byte-for-byte
// copy of an export - the same rule SendExport already applies to
// screenshots (clearIncluded in upload.go), extended to cover the dataset
// rows those screenshots travel alongside.
//
// # WHY THE CONTENT LEAVES AND THE KEY STAYS
//
// Keeping the full row after it has been confirmed delivered would mean
// every export after the first carries the whole history again - that is
// the defect this function exists to fix. Dropping the key as well would
// "fix" it by making the row look brand new the next time its log line is
// read, since MineAll's dedup only ever looks at what CURRENTLY sits in
// Txns (see dedupAgainstSent).
//
// So the row's content leaves Txns and its key moves into SentTxnKeys,
// which every future MineAll run checks. The key is a handful of bytes; the
// row it once stood for might have carried a shop name and a price. That
// is the entire trade this function makes.
//
// Returns how many of the given keys were actually found and cleared - not
// len(keys) - because a key with no matching row in the CURRENT store is not
// an error. It means an earlier run already cleared it, which happens the
// moment somebody presses send twice before this function existed to stop
// it, or points a merge tool at the same export more than once.
func MarkTxnsSent(outDir string, keys []string, logf func(string, ...interface{})) (int, error) {
	if logf == nil {
		logf = func(string, ...interface{}) {}
	}
	if len(keys) == 0 {
		return 0, nil
	}
	st, err := loadMineStore(outDir)
	if err != nil {
		return 0, fmt.Errorf("could not reopen the dataset to mark rows sent: %w", err)
	}

	want := make(map[string]bool, len(keys))
	for _, k := range keys {
		want[k] = true
	}

	kept := st.Txns[:0]
	marked := 0
	for _, t := range st.Txns {
		k := t.key()
		if want[k] {
			st.SentTxnKeys[k] = true
			marked++
			continue
		}
		kept = append(kept, t)
	}
	st.Txns = kept

	if marked == 0 {
		// Not an error - see the doc comment - but worth a line, because it
		// happening on every send would mean the keys handed back from an
		// export and the store on disk have drifted apart from each other.
		logf("mine: confirmed send matched 0 row(s) in the current dataset - " +
			"they may already have been cleared by an earlier confirmed send")
		return 0, nil
	}
	if err := saveMineStore(outDir, st); err != nil {
		return marked, fmt.Errorf("rows were confirmed sent but the dataset could not be "+
			"saved (%w) - they will be included again next time, which repeats work but "+
			"never loses anything", err)
	}
	return marked, nil
}

// buildGaps ranks the subsystems the game used that no extractor reads.
//
// This is the collector's own to-do list, written by the game rather than by us,
// and re-ranked every time anybody runs it. On a miner's machine "Harvestable"
// rises; on a bounty hunter's, whatever combat writes does. Nobody has to
// predict that in advance, which is the point.
func buildGaps(st *MineStore) []SubsystemGap {
	var out []SubsystemGap
	for name, n := range st.Subsystems {
		if coveredSubsystems[name] {
			continue
		}
		out = append(out, SubsystemGap{
			Subsystem: name, Lines: n, Shapes: len(st.shapes[name])})
	}
	// RANKED BY DISTINCT SHAPES, not by volume - see the doc comment. Lines
	// break ties, and the name breaks those, so the file is stable between runs
	// and a diff shows real change rather than map ordering.
	sort.Slice(out, func(i, j int) bool {
		if out[i].Shapes != out[j].Shapes {
			return out[i].Shapes > out[j].Shapes
		}
		if out[i].Lines != out[j].Lines {
			return out[i].Lines > out[j].Lines
		}
		return out[i].Subsystem < out[j].Subsystem
	})
	if len(out) > 60 {
		out = out[:60]
	}
	return out
}

// --- live streaming --------------------------------------------------------

// MineLive folds a single line into the store as the game writes it.
//
// # THE TWO-READER PROBLEM THIS CLOSES
//
// mineOneLog opens a file and walks it. That is right for the archive - 227
// sessions that will never change - and wrong for the session happening now.
// During play the tailer was already reading every appended line to decide
// whether to take a picture, and discarding the content. So a transaction that
// took two seconds was not in the dataset until the game exited, and a process
// that died first recorded it late or never.
//
// This is the same extraction, driven by the tailer instead of by a file walk.
// One line in, all extractors run, dataset current.
//
// Build and channel are passed in rather than re-detected per line: the tailer
// already knows which install it is watching, and re-deriving it from every
// line would be both slower and less certain than being told.
func (st *MineStore) MineLive(line, build, channel string) {
	mineLineInto(st, line, build, channel)
}

// --- combat, death and destruction -----------------------------------------
//
// # THE PRIVACY PROBLEM HERE IS SHARPER THAN ANYWHERE ELSE
//
// A real line out of Sleven's archive:
//
//	<Actor Death> CActor::Kill: 'Jeri_Blade' [id] in zone 'OOC_Stanton_4_Microtech'
//	killed by 'unknown' [0] using 'unknown' [Class unknown] with damage type ...
//
// Three of those fields can hold ANOTHER PLAYER'S HANDLE. 'Jeri_Blade' is a
// person. The standing rule is that other players' names are stripped before
// the file exists, so a name-based allow-list is not enough - the field NAME is
// harmless, the field VALUE is the problem.
//
// So these extractors allow-list by SHAPE, not by field name:
//
//	NPC_Archetypes-Male-Human-...   emitted - a game asset, not a person
//	AEGS_Gladius_123456             emitted - a ship class
//	behr_rifle_ballistic_01         emitted - an item class
//	Jeri_Blade                      NOT emitted - replaced with a placeholder
//
// A value only travels if it looks like something CIG shipped. Anything else
// becomes "<player>" or "<unnamed>". FAIL CLOSED: an unrecognised shape is
// treated as a person, because the cost of being wrong in that direction is
// somebody else's handle in a public dataset.
//
// The valuable part survives intact - what weapon, what damage type, what ship
// class, which zone, player or NPC. Which is everything a combat dataset needs
// and none of who was there.

var (
	reMineDeath = regexp.MustCompile(
		`<Actor Death> CActor::Kill: '([^']*)' \[[^\]]*\] in zone '([^']*)' ` +
			`killed by '([^']*)' \[[^\]]*\] using '([^']*)' \[Class ([^\]]*)\]` +
			`(?:.*?with damage type '?([A-Za-z]+))?`)

	reMineVehDestroy = regexp.MustCompile(
		`<Vehicle Destruction> CVehicle::OnAdvanceDestroyLevel: Vehicle '([^']*)' ` +
			`\[[^\]]*\] in zone '([^']*)'`)

	// A value that looks like a game asset rather than a person: an NPC
	// archetype, a manufacturer-prefixed ship, or a lowercase item class with
	// underscores. Anchored, because a handle CONTAINING one of these would
	// otherwise pass.
)

// safeActor returns a value only if it is shaped like a game asset.
func safeActor(v, placeholder string) string {
	v = strings.TrimSpace(v)
	switch {
	case v == "" || strings.EqualFold(v, "unknown"):
		return "unknown"
	case reMineAssetish.MatchString(scrubIDs(v)) || reMineAssetish.MatchString(v):
		return scrubIDs(v)
	default:
		return placeholder
	}
}

// MineDeath is one death, with nobody in it.
type MineDeath struct {
	Zone       string `json:"zone"`
	Victim     string `json:"victim"`      // NPC archetype, or <player>
	Killer     string `json:"killer"`      // as above
	Weapon     string `json:"weapon"`      // item class, or <unnamed>
	Class      string `json:"class"`       // Player | unknown | NPC class
	DamageType string `json:"damage_type"` // ballistic, energy, ...
	Count      int    `json:"count"`
}

func (d MineDeath) key() string {
	return strings.Join([]string{d.Zone, d.Victim, d.Killer, d.Weapon, d.Class, d.DamageType}, "|")
}

func mineCombatLine(st *MineStore, line string) {
	if m := reMineDeath.FindStringSubmatch(line); m != nil {
		d := MineDeath{
			Zone: scrubIDs(strings.TrimSpace(m[2])),
			// RAW, deliberately - see scrub.go. Deciding at collection time is
			// deciding forever; the export decides instead, so a better rule can
			// be re-run over data already gathered.
			Victim:     scrubIDs(strings.TrimSpace(m[1])),
			Killer:     scrubIDs(strings.TrimSpace(m[3])),
			Weapon:     scrubIDs(strings.TrimSpace(m[4])),
			Class:      strings.TrimSpace(m[5]),
			DamageType: strings.TrimSpace(m[6]),
		}
		st.Deaths[d.key()]++
		st.noteHit("actor_death")
	}
	if m := reMineVehDestroy.FindStringSubmatch(line); m != nil {
		// The ship class is safe by construction - it is matched against the
		// manufacturer list - but it still goes through safeActor so there is
		// exactly one rule about what may travel, not two.
		v := scrubIDs(strings.TrimSpace(m[1])) + " @ " + scrubIDs(strings.TrimSpace(m[2]))
		st.VehicleLosses[v]++
		st.noteHit("vehicle_destroyed")
	}
}
