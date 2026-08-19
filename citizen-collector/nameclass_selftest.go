package main

// nameclass_selftest.go - the name rules, driven from both directions.
//
// This decides whether a stranger's handle ends up in a file. Every KEEP has a
// case that must fail it, and the default - SWAP - is checked against the real
// handles that were found sitting in Sleven's own dataset, by name.

import (
	"os"
	"strings"
)

func runNameClassSelftest(check func(name string, ok bool, detail string)) {

	// -----------------------------------------------------------------
	// 1. THE REAL HANDLES. These were in gamelog-dataset.json on 2026-08-16.
	// -----------------------------------------------------------------
	//
	// Named individually rather than as a loop over a fixture, because if any
	// one of them ever passes again the failure should say WHICH.
	realHandles := []string{
		"DukeSP", "Jeri_Blade", "GimpyCat", "KDog79", "Corjack", "8mole5duro",
		"Kronicus42", "LighterBurrito", "SquiggleWigglez", "illin",
		"mrDonkey6511", "HDO", "Sleven-K",
	}
	leaked := []string{}
	for _, h := range realHandles {
		if KeepsName(h) {
			leaked = append(leaked, h)
		}
	}
	check("NAMES: every real handle found on his machine is swapped",
		len(leaked) == 0,
		"these would be written as-is: "+strings.Join(leaked, ", "))

	// The shapes that defeated the OLD pattern, from scrub.go's own header:
	// lowercase with underscores is also the shape of a great many handles.
	for _, h := range []string{"dark_wolf_77", "space_cowboy_42", "the_real_slim_shady"} {
		check("NAMES: "+h+" is swapped",
			!KeepsName(h),
			"lowercase_underscore handles passed through untouched before 2026-08-13")
	}

	// -----------------------------------------------------------------
	// 2. WHAT MUST BE KEPT - and each is a negative control for the above
	// -----------------------------------------------------------------
	//
	// Without these, a classifier that swapped EVERYTHING would pass every
	// check in section 1 and destroy the dataset.
	keeps := map[string]string{
		"NPC_Archetypes-Male-Human-Civilians-Utilitarian-Technician_Utilitarian_01_<id>": "ambient NPC",
		"PU_Human-Crusader-Guard-Male-Grunt_01_<id>":                                     "ambient NPC",
		"PU_Pilots-Human-Criminal-Pilot_Light_<id>":                                      "ambient NPC",
		"AEGS_Sabre_Firebird_<id>":                                                       "ship class",
		"behr_rifle_ballistic_01":                                                        "item class",
		"ksar_smg_energy_01_<id>":                                                        "item class",
		"unknown":                                                                        "placeholder",
		"Player":                                                                         "placeholder",
	}
	for v, why := range keeps {
		short := v
		if len(short) > 46 {
			short = short[:46] + "..."
		}
		check("NAMES: kept - "+short,
			KeepsName(v),
			why+" would be destroyed; 80 of 85 ambient NPC names were, before today")
	}

	// MISSION NPCs. A handle cannot contain a space, so a spaced human name is
	// a written character - and those are worth keeping.
	check("NAMES: a mission NPC with a spaced human name is kept",
		KeepsName("Ruto Vega") && KeepsName("Clovus Darneely"),
		"bounty and combat targets are exactly the names worth having")

	// AND THE HINT IS NOT A VERDICT. The same name without the space is
	// indistinguishable from a handle and must be swapped.
	check("NAMES: NEGATIVE CONTROL - the same name without a space is swapped",
		!KeepsName("RutoVega") && !KeepsName("ClovusDarneely"),
		"the space is the whole signal; without it this could be anybody's handle")

	// -----------------------------------------------------------------
	// 3. IDEMPOTENCE - the one that breaks joins if it is wrong
	// -----------------------------------------------------------------
	check("NAMES: a tag this program wrote is left alone",
		KeepsName("player:2860302f"),
		"swapping a tag gives one person two identities and every join breaks")
	check("NAMES: NEGATIVE CONTROL - something merely LOOKING like a tag is not",
		!KeepsName("player:notahexvalue") && !KeepsName("player_2860302f"),
		"the pattern has to be exact, or a handle shaped like one walks through")

	// -----------------------------------------------------------------
	// 4. THE SWAP IS STABLE, AND THE STORE FAILS CLOSED WITHOUT ONE
	// -----------------------------------------------------------------
	dir, err := os.MkdirTemp("", "cc-names")
	if err != nil {
		return
	}
	defer os.RemoveAll(dir)

	sc := newScrubber(dir, nil)
	a1 := sc.Value("DukeSP")
	a2 := sc.Value("DukeSP")
	b1 := sc.Value("Jeri_Blade")
	check("NAMES: the same person gets the same tag every time",
		a1 == a2 && strings.HasPrefix(a1, "player:"),
		"got "+a1+" then "+a2+"; unstable tags make the data unjoinable")
	check("NAMES: NEGATIVE CONTROL - different people get different tags",
		a1 != b1,
		"one tag for everybody would be safe and useless")

	// A SECOND SCRUBBER ON THE SAME MACHINE AGREES. The salt is on disk, so
	// tags survive a restart - otherwise every session would invent a new
	// identity for the same person.
	sc2 := newScrubber(dir, nil)
	check("NAMES: tags survive a restart",
		sc2.Value("DukeSP") == a1,
		"a fresh run produced a different tag for the same person")

	// A DIFFERENT MACHINE MUST NOT AGREE. Same salt everywhere would make the
	// tags a global identifier for a person across every contributor.
	other, err2 := os.MkdirTemp("", "cc-names2")
	if err2 == nil {
		defer os.RemoveAll(other)
		check("NAMES: NEGATIVE CONTROL - another machine gives a different tag",
			newScrubber(other, nil).Value("DukeSP") != a1,
			"a shared tag would identify one person across every contributor's data")
	}

	// THE STORE FAILS CLOSED. A pass with no swapper installed must redact
	// rather than write the name - a missing swapper is a programming error and
	// this is the direction it has to fail in.
	bare := &MineStore{}
	check("NAMES: a store with no swapper REDACTS rather than writes",
		bare.swap("DukeSP") == "<player>",
		"a forgotten swapper would write handles straight to disk")
	check("NAMES: NEGATIVE CONTROL - and it still keeps game vocabulary",
		bare.swap("AEGS_Sabre_Firebird_<id>") == "AEGS_Sabre_Firebird_<id>",
		"failing closed must not mean destroying everything")
}

// runPlayerEvidenceSelftest - the space rule is a HINT, never a verdict.
//
// Sleven, 2026-08-18: "The space rule is a hint, never a verdict - anything not
// clearly an NPC gets swapped. Losing an NPC name costs nothing, leaking a
// player name costs everything."
//
// The classifier keeps a spaced name on the claim that a handle cannot contain
// a space. Nothing in this repo can verify that claim, so the store overrides it
// with evidence: a name the log itself called a player is swapped whatever it
// looks like. This drives BOTH directions through the real mine path.
func runPlayerEvidenceSelftest(check func(name string, ok bool, detail string)) {
	dir, err := os.MkdirTemp("", "player-evidence-")
	if err != nil {
		check("evidence: temp dir", false, err.Error())
		return
	}
	defer os.RemoveAll(dir)

	sc := newScrubber(dir, nil)

	// A mission NPC with a spaced name, and a PLAYER whose name also has a
	// space - which the space rule alone would keep.
	st := newMineStore()
	st.swapName = sc.Value
	st.swapProse = sc.ScrubProse
	st.tagName = sc.Tag

	// Real line shapes, copied from the live Game.log.
	mineLineInto(st, `<2026-08-18T20:47:50.163Z> [Notice] <Expect Incoming Connection> `+
		`session=2594 node_id=0000 nickname="Ruto Vega" playerGEID=204354536218`, "1", "LIVE")
	mineLineInto(st, `<2026-08-18T20:47:47.002Z> [Notice] <AccountLoginCharacterStatus_Character> `+
		`Character: createdAt 1784177222540 - geid 204354536218 - accountId 1343523 - name Sleven`,
		"1", "LIVE")

	got := st.swap("Ruto Vega")
	check("evidence: a SPACED name the log called a player is swapped anyway",
		strings.HasPrefix(got, "player:"),
		"got "+got+" - the space rule was allowed to be the verdict, and a "+
			"player with a space in their name would be published")

	check("evidence: and a plain account name is swapped too",
		strings.HasPrefix(st.swap("Sleven"), "player:"),
		"got "+st.swap("Sleven"))

	// NEGATIVE CONTROL. A spaced name the log never called a player is still
	// kept - or this override has quietly turned into "swap everything", which
	// would destroy the mission-NPC data §4 says to keep.
	kept := st.swap("Kai Fenn")
	check("evidence: NEGATIVE CONTROL - an unseen spaced name is still KEPT",
		kept == "Kai Fenn",
		"got "+kept+" - the override is swallowing mission NPCs as well as players")

	// And the ambient archetypes are still cheap to keep.
	amb := st.swap("NPC_Archetypes-Male-Human-Civilians-Utilitarian-Technician_01_855480118723")
	check("evidence: NEGATIVE CONTROL - an ambient archetype is still kept",
		strings.HasPrefix(amb, "NPC_Archetypes-Male-Human"),
		"got "+amb)
}
