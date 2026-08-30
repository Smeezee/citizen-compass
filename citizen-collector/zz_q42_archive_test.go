package main

// zz_q42_archive_test.go - DIAGNOSTIC, not a test of correctness.
//
// Q42. gamelog_mine.go's own header records that the 2026-08-07 Python dig
// found "four transaction families, 183 priced items, 31 shops" across 233
// sessions. The Go port reports transactions: 0 while declaring its transaction
// extractor Verified: true.
//
// A verified extractor sitting at zero is either a broken pattern or a false
// declaration. This runs the real miner over the REAL archive - every file
// MineTargets() finds, which on this machine is 243 files and 208 MB - and
// prints what each extractor actually caught.
//
// IT IS SLOW ON PURPOSE. The header records 240 SECONDS over the real archive
// against 61ms isolated, and that the gap was once misdiagnosed as a flaky
// test. It is unbounded work proportional to how much the person has played.
// Run it with a timeout that expects minutes:
//
//	go test -run Q42 -v -timeout 30m
//
// It is a test FILE so it never reaches the shipped binary, and it writes its
// store to a temp directory rather than anywhere a real capture would go.

import (
	"os"
	"sort"
	"testing"
)

func TestQ42ArchiveCounts(t *testing.T) {
	if os.Getenv("CC_Q42") == "" {
		t.Skip("set CC_Q42=1 to run the full-archive dig (minutes, 208 MB)")
	}

	targets := MineTargets()
	t.Logf("archive: %d file(s) found by MineTargets()", len(targets))
	if len(targets) == 0 {
		t.Fatal("MineTargets() found nothing - there is no archive to measure, " +
			"so a zero here would mean nothing at all")
	}

	var bytes int64
	for _, p := range targets {
		if fi, err := os.Stat(p); err == nil {
			bytes += fi.Size()
		}
	}
	t.Logf("archive: %.1f MB across those files", float64(bytes)/(1024*1024))

	out := t.TempDir()
	st, err := MineAll(out, Install{}, func(f string, a ...interface{}) {})
	if err != nil {
		t.Fatalf("MineAll: %v", err)
	}

	// PER EXTRACTOR, which is what the order asks for. buildExtractors folds the
	// accumulated hit counts into the described table, so this reports the
	// program's own accounting rather than a second count written here.
	t.Log("")
	t.Log("  extractor              verified   hits")
	for _, e := range buildExtractors(st) {
		t.Logf("  %-22s %-9v  %d", e.Name, e.Verified, e.Hits)
	}

	t.Log("")
	t.Logf("  transactions[]         %d", len(st.Txns))
	t.Logf("  locations{}            %d", len(st.Locations))

	// The families the Python dig named, so a partial match is visible rather
	// than collapsing into one number.
	fam := map[string]int{}
	for _, x := range st.Txns {
		fam[x.Market+" "+x.Side]++
	}
	keys := make([]string, 0, len(fam))
	for k := range fam {
		keys = append(keys, k)
	}
	sort.Strings(keys)
	for _, k := range keys {
		t.Logf("  family %-16s %d", k, fam[k])
	}
	if len(fam) == 0 {
		t.Log("  family                 NONE - zero transactions of any kind")
	}
}
