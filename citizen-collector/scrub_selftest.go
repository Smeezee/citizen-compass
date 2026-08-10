package main

// scrub_selftest.go - the check that the 2026-08-08 review proved was missing.
//
// The existing combat fixtures used Jeri_Blade, DukeSP and Sleven-K. Every one
// carries an uppercase letter or a hyphen, so every one failed the asset regex
// by ACCIDENT rather than by design - and a handle shaped like an item class
// sailed straight through. These fixtures are chosen to have the shape that
// used to pass.

import "strings"

func runScrubShapeSelftest(check func(name string, ok bool, detail string)) {
	tmp := "."
	sc := newScrubber(tmp, nil)

	// Handles that LOOK like item classes. Every one of these used to be
	// exported verbatim.
	leaky := []string{
		"dark_wolf_77", "space_cowboy_42", "the_real_slim_shady",
		"john_smith_1", "big_red_one",
	}
	var escaped []string
	for _, h := range leaky {
		if v := sc.Value(h); v == h {
			escaped = append(escaped, h)
		}
	}
	check("PRIVACY: a handle shaped like an item class does NOT pass through",
		len(escaped) == 0,
		"still escaping: "+strings.Join(escaped, ", "))

	// NEGATIVE CONTROL. If the fix were "pseudonymise everything", the check
	// above would pass and the dataset would be destroyed. Real classes must
	// still travel untouched.
	keep := map[string]bool{
		"behr_rifle_ballistic_01":   true,
		"gmni_smg_ballistic_01":     true,
		"AEGS_Vanguard_Harbinger":   true,
		"NPC_Archetypes-Male-Human": true,
	}
	var lost []string
	for k := range keep {
		if sc.Value(k) != k {
			lost = append(lost, k)
		}
	}
	check("NEGATIVE CONTROL: real game asset names still travel unchanged",
		len(lost) == 0, "wrongly pseudonymised: "+strings.Join(lost, ", "))

	// And the originals still work.
	check("PRIVACY: the original fixture handles are still caught",
		sc.Value("Jeri_Blade") != "Jeri_Blade" &&
			sc.Value("DukeSP") != "DukeSP" &&
			sc.Value("Sleven-K") != "Sleven-K",
		"the old cases must not regress")
}
