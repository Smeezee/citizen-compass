package main

// scrub_policy_selftest.go - the check that makes the NEXT field fail closed.
//
// The scrubber covered 4 of 28 fields. The other 24 were not decided about,
// which is not the same as being safe - and "not decided about" is exactly how
// `deaths` came to carry 13 real handles: it was added after the allow-list
// existed and never went through it.
//
// So this walks MineStore BY REFLECTION and fails if any field has no policy.
// Not a list somebody maintains alongside the struct - the struct itself is the
// list, so a field added in year five cannot avoid being noticed.

import (
	"os"
	"reflect"
	"sort"
	"strings"
)

func runScrubPolicySelftest(check func(name string, ok bool, detail string)) {

	// -----------------------------------------------------------------
	// 1. EVERY FIELD IS DECIDED ABOUT
	// -----------------------------------------------------------------
	t := reflect.TypeOf(MineStore{})
	var missing, fields []string
	for i := 0; i < t.NumField(); i++ {
		f := t.Field(i)
		if f.PkgPath != "" {
			continue // unexported: machinery, never serialised
		}
		fields = append(fields, f.Name)
		if policyFor(f.Name) == policyUnclassified {
			missing = append(missing, f.Name)
		}
	}
	sort.Strings(missing)

	check("POLICY: every exported field of MineStore has a scrub policy",
		len(missing) == 0,
		"undecided: "+strings.Join(missing, ", ")+
			" - an undecided field is dropped from the export and this is how you "+
			"find out, rather than by reading somebody's dataset months later")

	// NEGATIVE CONTROL. If reflection found nothing, the check above passes
	// vacuously and protects nobody.
	check("POLICY: NEGATIVE CONTROL - reflection actually found the fields",
		len(fields) >= 25,
		"walked "+itoaSmall(len(fields))+" exported fields; the struct has 28")

	// AND A FIELD THAT DOES NOT EXIST MUST COME BACK UNCLASSIFIED, or the
	// lookup is answering yes to everything and the check above is theatre.
	check("POLICY: NEGATIVE CONTROL - an unknown field is unclassified",
		policyFor("SomeFieldAddedInTwentyThirty") == policyUnclassified,
		"the zero value must mean 'not decided about', or nothing fails closed")

	// -----------------------------------------------------------------
	// 2. THE PROSE SCANNER - the two fields C1 named
	// -----------------------------------------------------------------
	//
	// The risk is a bounty objective naming its target. The danger in fixing it
	// is destroying the sentence, so both directions are checked.
	dir := osTempDirForPolicy()
	sc := newScrubber(dir, nil)

	// Somebody already known from a structured field is caught by name.
	known := sc.Value("DukeSP")
	got, hits := sc.ScrubProse("Eliminate DukeSP before the timer expires")
	check("PROSE: a known player named in an objective is replaced",
		hits == 1 && strings.Contains(got, known) && !strings.Contains(got, "DukeSP"),
		"got "+got)
	check("PROSE: and the sentence around them survives",
		strings.HasPrefix(got, "Eliminate ") && strings.HasSuffix(got, " before the timer expires"),
		"got "+got)

	// A handle nobody has seen before, caught by shape.
	got2, hits2 := sc.ScrubProse("Bounty: 8mole5duro last seen near Yela")
	check("PROSE: an unseen handle with digits in it is replaced",
		hits2 >= 1 && !strings.Contains(got2, "8mole5duro"),
		"got "+got2)

	// THE CONTROL THAT MATTERS MOST. Real mission text must come through
	// untouched, or this trades a leak for a destroyed dataset.
	for _, real := range []string{
		"Adagio Holdings in Need of Salvagers",
		"Alliance Aid: Interstellar Large Cargo Haul (Research)",
		"Board the Transport",
		"Investigate the Derelict Reclaimer",
	} {
		out, n := sc.ScrubProse(real)
		check("PROSE: NEGATIVE CONTROL - real mission text is untouched",
			out == real && n == 0,
			"mangled "+itoaSmall(n)+" token(s): "+out)
	}

	// Game vocabulary inside prose is not a person either.
	got3, hits3 := sc.ScrubProse("Destroy the AEGS_Sabre_Firebird_<id> at the station")
	_ = got3
	check("PROSE: NEGATIVE CONTROL - a ship class inside text is not swapped",
		hits3 == 0,
		"replaced "+itoaSmall(hits3)+" token(s) that were game vocabulary")

	// -----------------------------------------------------------------
	// 3. THE SCAN HAPPENS AT WRITE TIME, WHERE IT CAN ACTUALLY FIRE
	// -----------------------------------------------------------------
	//
	// The first version of this test scanned at EXPORT time and caught the real
	// defect by failing: the export scrubber starts empty and every structured
	// field already holds tags by then, so "somebody already known to be a
	// person" - the rule that catches a bounty target because they were also a
	// killer - could never fire there. safeActor again, in a new field.
	//
	// So the store scans as it writes, on the pass that saw the raw names, and
	// this proves it by effect rather than by calling the scanner directly.
	st := newMineStore()
	st.swapName = sc.Value
	st.swapProse = sc.ScrubProse

	// DukeSP is seen first as a person in a structured field - exactly what a
	// kill line does - and only then named in an objective.
	st.swap("DukeSP")
	obj, ok1 := st.prose("Eliminate DukeSP")
	con, ok2 := st.prose("Hunt down mrDonkey6511 for the Guild")
	check("PROSE: write time - a known person named in an objective is replaced",
		ok1 && !strings.Contains(obj, "DukeSP") && strings.Contains(obj, "player:"),
		"got "+obj+" - this is the rule that cannot fire at export time")
	check("PROSE: write time - a handle-shaped name in a contract is replaced",
		ok2 && !strings.Contains(con, "mrDonkey6511"),
		"got "+con)
	check("PROSE: NEGATIVE CONTROL - the sentence survives both",
		strings.HasPrefix(obj, "Eliminate ") && strings.HasSuffix(con, " for the Guild"),
		"obj="+obj+" con="+con)

	// FAIL CLOSED. A store with no scanner refuses the text rather than
	// writing it raw, and says so.
	bare := newMineStore()
	_, ok3 := bare.prose("Eliminate DukeSP")
	check("PROSE: a store with NO scanner refuses free text rather than keeping it",
		!ok3 && bare.proseDropped == 1,
		"dropped="+itoaSmall(bare.proseDropped)+" - without a scanner the only safe "+
			"answer is to record nothing, and to count it")

	// AND THE EXPORT DOES NOT UNDO IT. Scanning twice must not tag the tags.
	st.Objectives[obj]++
	st.Contracts[con]++
	safe, _ := ScrubForExport(st, dir, nil)
	joined := ""
	for k := range safe.Objectives {
		joined += k + " ~ "
	}
	for k := range safe.Contracts {
		joined += k + " ~ "
	}
	check("PROSE: exporting already-scanned text changes nothing",
		strings.Contains(joined, obj) && strings.Contains(joined, con),
		"got "+joined+" - a tag of a tag gives one person two identities")

	// THE GAP, STATED RATHER THAN GLOSSED.
	//
	// A handle with no digit and no underscore that this machine has never seen
	// in a structured field is indistinguishable from an org name - "Corjack"
	// and "ArcCorp" have the same shape. It is KEPT. That is a real limit, and
	// a check that asserted otherwise would be describing a scanner nobody
	// wrote. Recorded here so it is not later mistaken for coverage.
	gap, hits := sc.ScrubProse("Eliminate Corjack")
	check("PROSE: KNOWN LIMIT - an unseen handle with no digits is NOT caught",
		hits == 0 && strings.Contains(gap, "Corjack"),
		"if this ever fails the rule got broader - re-check that ArcCorp, "+
			"microTech and Covalex still come through untouched")
}

// osTempDirForPolicy gives the selftest a private folder for its salt, so it
// never reads or writes the real one beside the exe.
func osTempDirForPolicy() string {
	d, err := os.MkdirTemp("", "cc-policy")
	if err != nil {
		return os.TempDir()
	}
	return d
}
