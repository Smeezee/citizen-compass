package main

// scrub_policy.go - every field is excluded unless it has been cleared.
//
// ===========================================================================
// WHY THE OLD SHAPE WAS THE REAL DEFECT
// ===========================================================================
//
// ScrubForExport was a hand-written walk over four things: Deaths, Locations,
// Txns, VehicleLosses. MineStore has 28 fields. The other 24 were not decided
// about - they were simply not mentioned, which is not the same as being safe.
//
// That is opt-in protection, and opt-in protection has one failure mode: the
// NEXT field. Somebody adds a collection that carries a name, does not think
// about the scrubber, and it leaks by default. That is exactly how `deaths`
// happened - it was added after the allow-list existed and never went through
// it.
//
// So it is inverted. Every field must carry a policy here. A field with no
// policy is NOT exported at all, and the export says so out loud. Adding a
// field therefore fails closed: the worst case is a missing collection that
// somebody notices, rather than a stranger's handle that nobody does.
//
// scrub_policy_selftest.go walks MineStore by reflection and fails if any field
// is missing a policy, so the gap is caught before a release rather than by a
// person reading a dataset months later.

// fieldPolicy is what the export does with one field.
type fieldPolicy int

const (
	// policyUnclassified is the ZERO VALUE and means "not decided about".
	// A field that lands here is dropped from the export and reported.
	policyUnclassified fieldPolicy = iota

	// policyCleared: this field cannot carry a person's name. Every entry is
	// game vocabulary, a count, or something this program generated itself.
	policyCleared

	// policyKeyed: the map's KEYS are pipe-separated records with name-bearing
	// positions. Handled by the existing per-field walks.
	policyKeyed

	// policyProse: free text that may MENTION a person - a bounty naming its
	// target. Token-scanned rather than replaced wholesale, or the sentence is
	// destroyed along with the name.
	policyProse
)

// mineFieldPolicy carries one entry per MineStore field.
//
// EVERY ENTRY HAS A REASON, because "cleared" is a claim about somebody's
// privacy and a bare map would make it look like bookkeeping.
var mineFieldPolicy = map[string]fieldPolicy{
	// --- header: generated here, nothing observed -------------------------
	"SchemaVersion": policyCleared, // an integer this program writes
	"Generated":     policyCleared, // a timestamp
	"ToolVersion":   policyCleared, // this build's version string
	"InstallID":     policyCleared, // 16 random bytes, not derived from anybody
	"InstallSince":  policyCleared, // a timestamp
	"Privacy":       policyCleared, // this program's own sentence about itself

	// --- game vocabulary: CIG's names for CIG's things ---------------------
	"SessionsSeen":     policyCleared, // session counts and build ids
	"Extractors":       policyCleared, // the names of our own readers
	"Builds":           policyCleared, // game build numbers
	"ShopClasses":      policyCleared, // shop class names, already id-scrubbed
	"Ships":            policyCleared, // ship class names - AEGS_Sabre and kin
	"Routes":           policyCleared, // quantum destinations
	"ObjectContainers": policyCleared, // interior/exterior container names
	"SpawnLocations":   policyCleared, // spawn point names
	"Rocks":            policyCleared, // mineable rock types
	"Equipment":        policyCleared, // item class names
	"Payouts":          policyCleared, // integers
	"MissionTemplates": policyCleared, // CIG mission template ids
	"Subsystems":       policyCleared, // the game's own subsystem names
	"Uncovered":        policyCleared, // subsystem names we have no reader for
	"Locations":        policyKeyed,   // location names, walked already

	// --- the ones that carry people ---------------------------------------
	"Deaths":        policyKeyed, // Zone|Victim|Killer|Weapon|Class|DamageType
	"VehicleLosses": policyKeyed, // the same shape of risk

	// --- free text that can NAME somebody ---------------------------------
	//
	// A PvP bounty names its target. Neither of these has ever been scrubbed,
	// and neither has ever been checked - they were simply not in the walk.
	"Contracts":  policyProse, // "Adagio Holdings in Need of Salvagers" ... or a handle
	"Objectives": policyProse, // "Eliminate <somebody>"
	"GameTips":   policyProse, // CIG's own tips; scanned because it costs nothing

	// --- transactions ------------------------------------------------------
	"Txns": policyKeyed, // shop and item names, walked already

	// SentTxnKeys is REMOVED from the export entirely rather than scrubbed.
	// It is this machine's dedup bookkeeping, it is of no use to anybody else,
	// and its keys are built from shop and item names. There is a check that it
	// is absent from the exported JSON.
	"SentTxnKeys": policyCleared,
}

// unclassifiedMineFields returns the fields with no policy.
//
// Used by the selftest, which walks the struct by reflection so that a field
// added in year five is caught by the test rather than by a person reading a
// dataset.
func policyFor(field string) fieldPolicy {
	return mineFieldPolicy[field] // zero value is policyUnclassified
}
