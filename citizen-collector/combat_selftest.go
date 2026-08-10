package main

// combat_selftest.go - checks for the death / vehicle-destruction extractors.
//
// These matter more than the others because the source lines contain OTHER
// PEOPLE'S HANDLES. Every fixture below is a real line shape out of Sleven's
// 227-session archive, with the real handles left in - which is what makes the
// leak checks able to fail.

import (
	"os"
	"strings"
)

const combatFixture = `<2026-08-07T22:00:00.000Z> <Actor Death> CActor::Kill: 'Jeri_Blade' [864133595285] in zone 'OOC_Stanton_4_Microtech' killed by 'DukeSP' [204354536218] using 'behr_rifle_ballistic_01_864140490741' [Class behr_rifle_ballistic_01] with damage type 'Bullet'
<2026-08-07T22:00:01.000Z> <Actor Death> CActor::Kill: 'NPC_Archetypes-Male-Human-Civilians-Utilitarian-Technician_Utilitarian_01_855480118723' [855480118723] in zone 'ObjectContainer-ugf_lta_a_0002' killed by 'Sleven-K' [855480118723] using 'gmni_smg_ballistic_01_204354536218' [Class gmni_smg_ballistic_01] with damage type 'Bullet'
<2026-08-07T22:00:02.000Z> <Vehicle Destruction> CVehicle::OnAdvanceDestroyLevel: Vehicle 'AEGS_Vanguard_Harbinger_864140490741' [864140490741] in zone 'Hangar_MediumFront_RestStop_433183157784' [pos x: 1.0, y: 2.0]
`

func runCombatSelftest(check func(name string, ok bool, detail string)) {
	st := newMineStore()
	for _, line := range strings.Split(combatFixture, "\n") {
		if strings.TrimSpace(line) != "" {
			mineLineInto(st, line, "12399239", "PTU")
		}
	}

	check("combat: deaths are recorded at all",
		len(st.Deaths) == 2, "two deaths in the fixture")
	check("combat: vehicle destruction is recorded",
		len(st.VehicleLosses) == 1, "one hull lost in the fixture")

	// THE LOCAL STORE NOW KEEPS RAW NAMES ON PURPOSE. What must be clean is the
	// EXPORT copy, so that is what these checks read.
	rawJoined := ""
	for k := range st.Deaths {
		rawJoined += k + "\n"
	}
	check("raw: the local dataset DOES keep the real name",
		strings.Contains(rawJoined, "Jeri_Blade"),
		"deciding at collection time is deciding forever - the raw stays so a "+
			"better rule can be re-run over it later")

	tmp, _ := os.MkdirTemp("", "scrub-")
	defer os.RemoveAll(tmp)
	safe, people := ScrubForExport(st, tmp, nil)
	check("scrub: the export replaced the people it found",
		people >= 2, "Jeri_Blade and DukeSP at least")

	joined := ""
	for k := range safe.Deaths {
		joined += k + "\n"
	}
	for k := range safe.VehicleLosses {
		joined += k + "\n"
	}

	// PRIVACY. Three real handles out of the archive, in three different fields.
	for _, handle := range []string{"Jeri_Blade", "DukeSP", "Sleven-K"} {
		check("PRIVACY: the handle "+handle+" never reaches the dataset",
			!strings.Contains(joined, handle),
			"victim, killer and weapon fields can all hold a person's name")
	}
	check("PRIVACY: a person becomes a stable token, not a blank",
		strings.Contains(joined, "player:"),
		"a blank would be indistinguishable from a parse failure, and a flat "+
			"<player> would destroy every relationship in the dataset")

	// The valuable half must survive, or the scrubber is just a delete button.
	check("combat: the WEAPON survives",
		strings.Contains(joined, "behr_rifle_ballistic_01") &&
			strings.Contains(joined, "gmni_smg_ballistic_01"),
		"weapon class is the point of collecting this")
	check("combat: the DAMAGE TYPE survives",
		strings.Contains(joined, "Bullet"), "ballistic vs energy vs collision")
	check("combat: an NPC archetype survives - it is an asset, not a person",
		strings.Contains(joined, "NPC_Archetypes-Male-Human"),
		"telling an NPC kill from a player kill is most of the value")
	check("combat: the destroyed ship class and zone survive",
		strings.Contains(joined, "AEGS_Vanguard_Harbinger") &&
			strings.Contains(joined, "Hangar_MediumFront_RestStop"),
		"what was lost and where")
	check("PRIVACY: entity ids inside asset names are scrubbed",
		!strings.Contains(joined, "864140490741"),
		"the id rides inside the ship and weapon names")

	// A person becomes the SAME token every time, or every relationship in the
	// dataset is destroyed and this is just redaction with extra steps.
	safe2, _ := ScrubForExport(st, tmp, nil)
	j2 := ""
	for k := range safe2.Deaths {
		j2 += k + "\n"
	}
	_ = safe2
	// Compare the TOKEN for one known name across two runs. Comparing whole
	// dumps was a bad check - Go map order varies, so it could fail for a
	// reason that has nothing to do with the salt.
	s1 := newScrubber(tmp, nil)
	s2 := newScrubber(tmp, nil)
	check("scrub: the same person gets the same token across runs",
		s1.Value("Jeri_Blade") == s2.Value("Jeri_Blade") &&
			strings.HasPrefix(s1.Value("Jeri_Blade"), "player:"),
		"a salt that changed per run would make every token useless")
	check("scrub: two different people get two different tokens",
		s1.Value("Jeri_Blade") != s1.Value("DukeSP"),
		"otherwise relationships collapse into one person")
	check("scrub: tokens are shaped player:xxxxxxxx",
		strings.Contains(joined, "player:"), "stable, unreversible, and obviously a token")

	// NEGATIVE CONTROLS for safeActor itself. Without these, a function that
	// returned "<player>" for EVERYTHING would pass every privacy check above
	// and destroy the dataset.
	check("NEGATIVE CONTROL: safeActor passes a real item class through",
		safeActor("behr_rifle_ballistic_01", "<player>") == "behr_rifle_ballistic_01",
		"the guard must let game assets travel")
	check("NEGATIVE CONTROL: safeActor blocks a bare handle",
		safeActor("Jeri_Blade", "<player>") == "<player>",
		"and stop people")
	check("NEGATIVE CONTROL: safeActor blocks a handle that CONTAINS an asset name",
		safeActor("xX_behr_rifle_ballistic_01_Xx", "<player>") == "<player>",
		"the pattern is anchored, so wrapping an asset name in a handle does not smuggle it")
	check("NEGATIVE CONTROL: unknown stays unknown, not <player>",
		safeActor("unknown", "<player>") == "unknown",
		"the game says unknown when there was no killer - that is a fact, not a person")
}
