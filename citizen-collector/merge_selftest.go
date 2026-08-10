package main

// merge_selftest.go - checks for the multi-contributor merge.
//
// The load-bearing question this answers: when three exports report the same
// price, is that three people agreeing or one person exporting three times?
// Getting that wrong in either direction destroys the dataset - inflating
// counts, or deleting the corroboration that made crowd-sourcing worth doing.

import (
	"os"
	"path/filepath"
)

func writeTestDataset(dir, name, installID string, txns []MineTxn) string {
	st := newMineStore()
	st.InstallID = installID
	st.Txns = txns
	st.Locations["Levski"] = 3
	p := filepath.Join(dir, name)
	_ = SaveMerged(&MergedStore{}, p+".ignore")
	b, _ := jsonMarshalIndent(st)
	_ = os.WriteFile(p, b, 0o644)
	return p
}

func runMergeSelftest(check func(name string, ok bool, detail string)) {
	tmp, err := os.MkdirTemp("", "merge-")
	if err != nil {
		check("merge: temp dir", false, err.Error())
		return
	}
	defer os.RemoveAll(tmp)

	copper := func(price, build string) MineTxn {
		return MineTxn{TS: "2026-08-08T10:00:00Z", Side: "sell", Market: "commodity",
			Shop: "Levski", Item: "Copper", Price: price, Build: build}
	}

	// Two different people, same observation.
	a := writeTestDataset(tmp, "alice.json", "aaaa-1111", []MineTxn{copper("1000", "12344265")})
	b := writeTestDataset(tmp, "bob.json", "bbbb-2222", []MineTxn{copper("1000", "12344265")})
	// The SAME person, exporting twice. This must not look like a third witness.
	c := writeTestDataset(tmp, "alice-again.json", "aaaa-1111", []MineTxn{copper("1000", "12344265")})

	m, err := MergeExports([]string{a, b, c}, nil)
	if err != nil {
		check("merge: runs", false, err.Error())
		return
	}
	check("merge: reads every source", len(m.Sources) == 3, "three files in")
	check("merge: counts DISTINCT contributors, not files",
		len(m.Contributors) == 2,
		"three exports from two people is two people")

	var price *Observation
	for _, o := range m.Prices {
		price = o
	}
	check("merge: confidence is the number of PEOPLE who saw it",
		price != nil && price.Confidence() == 2,
		"one person exporting twice must not become a second witness")
	check("merge: total sightings still counts every row",
		price != nil && price.Sightings == 3,
		"three rows were read; that is a different fact from two people agreeing")

	// NEGATIVE CONTROL. If Confidence just returned the source count, the check
	// above would pass. A fourth person must move it.
	d := writeTestDataset(tmp, "carol.json", "cccc-3333", []MineTxn{copper("1000", "12344265")})
	m2, _ := MergeExports([]string{a, b, c, d}, nil)
	var p2 *Observation
	for _, o := range m2.Prices {
		p2 = o
	}
	check("NEGATIVE CONTROL: a genuinely new contributor DOES raise confidence",
		p2 != nil && p2.Confidence() == 3,
		"the guard must count people, not merely refuse to count")

	// Disagreement must be reported, not resolved.
	e := writeTestDataset(tmp, "dave.json", "dddd-4444", []MineTxn{copper("1450", "12399239")})
	m3, _ := MergeExports([]string{a, b, e}, nil)
	check("merge: a price disagreement is REPORTED",
		len(m3.Disagreements) == 1,
		"two values for Copper at Levski")
	if len(m3.Disagreements) == 1 {
		check("merge: both values survive - no winner is picked",
			len(m3.Disagreements[0].Values) == 2,
			"a patch change and a misread are indistinguishable from in here")
		check("merge: the builds are carried so a human can tell them apart",
			len(m3.Disagreements[0].Values[0].Builds) > 0,
			"12344265 vs 12399239 is the whole explanation, and it is in the data")
	}

	// An export with no id contributes facts but not agreement.
	f := writeTestDataset(tmp, "anon.json", "", []MineTxn{copper("1000", "12344265")})
	m4, _ := MergeExports([]string{f}, nil)
	var p4 *Observation
	for _, o := range m4.Prices {
		p4 = o
	}
	check("merge: an anonymous export still contributes its rows",
		p4 != nil && p4.Sightings == 1, "the data is still good")
	check("merge: but it counts toward nobody's agreement, and says so",
		p4 != nil && p4.Confidence() == 0 && len(m4.Warnings) > 0,
		"counting it would inflate every confidence number in the file")

	// A newer schema must be refused rather than silently stripped.
	st := newMineStore()
	st.SchemaVersion = MineSchemaVersion + 5
	st.InstallID = "eeee-5555"
	nb, _ := jsonMarshalIndent(st)
	g := filepath.Join(tmp, "future.json")
	_ = os.WriteFile(g, nb, 0o644)
	m5, _ := MergeExports([]string{a, g}, nil)
	check("merge: an export from a NEWER collector is refused, not stripped",
		len(m5.Warnings) > 0 && len(m5.Contributors) == 1,
		"silently dropping its unknown fields would lose somebody else's contribution")
}
