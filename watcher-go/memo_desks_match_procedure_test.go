package main

// EVERY DESK THE PROCEDURE NAMES MUST BE DELIVERABLE TO.
//
// Two desks were added on consecutive days and each was half-wired, in opposite
// directions:
//
//   audit   2026-09-08  the ROUTER learned first. The checker stayed silent
//                       until its own drift assertion caught it on a sweep.
//   design  2026-09-08  the CHECKER, the README and the tray learned first and
//                       the ROUTER did not - so a memo to Design would have
//                       been refused and filed to _needs_review. A desk with a
//                       tray it cannot receive post into.
//
// A desk is not a name in a list. It is four things: the procedure, the tray,
// the router and the checker. Updating any three leaves something that looks
// finished.
//
// checks/_verify_correspondence.py already holds the CHECKER to the README.
// This holds the ROUTER to it. Between them, a desk added to the procedure
// cannot stay half-delivered in either direction.
//
// It reads the README rather than a list typed here, on purpose: a list here
// would be a fifth place to forget.

import (
	"os"
	"path/filepath"
	"regexp"
	"sort"
	"testing"
)

var reReadmeDesk = regexp.MustCompile(`(?m)open/([a-z][a-z0-9_-]*)`)

func TestEveryDeskInTheProcedureCanReceivePost(t *testing.T) {
	// Walk up to the repo root from wherever `go test` is running.
	var readme string
	for _, up := range []string{"..", "../..", "."} {
		p := filepath.Join(up, "correspondence", "README.md")
		if _, err := os.Stat(p); err == nil {
			readme = p
			break
		}
	}
	if readme == "" {
		t.Skip("correspondence/README.md not found from here")
	}
	b, err := os.ReadFile(readme)
	if err != nil {
		t.Fatal(err)
	}

	named := map[string]bool{}
	for _, m := range reReadmeDesk.FindAllStringSubmatch(string(b), -1) {
		named[m[1]] = true
	}
	if len(named) == 0 {
		t.Fatal("no `open/<desk>` names found in the README - this test would " +
			"pass vacuously, which is worse than failing")
	}

	var missing []string
	for desk := range named {
		if _, ok := memoTrays[desk]; !ok {
			missing = append(missing, desk)
		}
	}
	sort.Strings(missing)
	if len(missing) > 0 {
		t.Fatalf("the procedure names desk(s) the router cannot deliver to: %v\n"+
			"A memo addressed to one of these is REFUSED and filed to "+
			"_needs_review, so the desk has a tray it can never receive post "+
			"into. Add it to memoTrays.", missing)
	}

	// And the other direction: a desk the router accepts but the procedure
	// never mentions is a delivery nobody documented.
	var undocumented []string
	for desk := range memoTrays {
		if !named[desk] {
			undocumented = append(undocumented, desk)
		}
	}
	sort.Strings(undocumented)
	if len(undocumented) > 0 {
		t.Errorf("the router accepts desk(s) the procedure never names: %v\n"+
			"Post would be delivered somewhere no one has been told to look.",
			undocumented)
	}
}
