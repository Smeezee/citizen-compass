package main

// The design desk, added 2026-09-08. It arrived the OTHER WAY ROUND from
// `audit`, and that is the useful part:
//
//	audit   the router learned first, and the CHECKER stayed silent until its
//	        own drift assertion caught it on the next sweep.
//	design  the checker, the README and the tray all learned first, and THE
//	        ROUTER did not - a desk with a tray it could not receive post into.
//
// Twice in one day, from opposite ends. THE RISK IN ADDING A DESK IS NOT THE
// DESK: it is that widening the list quietly widens what the list REFUSES.
// Architecture's order names the near-miss explicitly - "Designer and Designs
// must bounce" - so both directions are asserted here rather than assumed to be
// covered by the audit desk's negative test.

import (
	"path/filepath"
	"sort"
	"strings"
	"testing"
)

func TestTheDesignDeskCanReceivePost(t *testing.T) {
	m := Memo{To: "design", From: "Build", Subject: "s", Status: "open"}
	dir, why, ok := memoDestination(m)
	if !ok {
		t.Fatalf("a memo to design was refused: %s", why)
	}
	if filepath.Base(dir) != "design" {
		t.Fatalf("a memo to design was filed to %q", dir)
	}
}

// readMemo lowercases To, so "Design" in a header must reach the same tray.
func TestTheDesignDeskIsCaseFolded(t *testing.T) {
	m, ok := readMemo("To: Design\nFrom: Build\nSubject: s\n")
	if !ok {
		t.Fatal("a memo addressed to Design was not read as a memo at all")
	}
	if m.To != "design" {
		t.Fatalf("To was normalised to %q, not \"design\"", m.To)
	}
	if _, _, ok := memoDestination(m); !ok {
		t.Fatal("Design with a capital D did not reach the design tray")
	}
}

// THE ONE THE ORDER NAMED. "Designer" and "Designs" are the near-misses a
// human actually types, and both must bounce. The rest are the same shape.
func TestAddingDesignDidNotWidenWhatIsAccepted(t *testing.T) {
	for _, bad := range []string{"designer", "Designer", "designs", "Designs",
		"des", "designing", "ux", "", "  "} {
		m := Memo{To: strings.ToLower(strings.TrimSpace(bad)), From: "Build",
			Subject: "s", Status: "open"}
		// Deliberately NOT trimming the two whitespace cases into equality with
		// each other - an empty addressee and a blank one are both refusals and
		// both are checked.
		if bad == "" || strings.TrimSpace(bad) == "" {
			m.To = bad
		}
		dir, why, ok := memoDestination(m)
		if ok {
			t.Errorf("a memo to %q was ACCEPTED and filed to %q - the desk list "+
				"has stopped being a list", bad, dir)
		}
		if bad == "designer" && !strings.Contains(why, "not one of") {
			t.Errorf("the refusal does not say what the real desks are: %s", why)
		}
	}
}

// THE REFUSAL MESSAGE MUST NAME EVERY REAL DESK, AND THE LIST IS READ FROM THE
// ROUTER RATHER THAN TYPED HERE.
//
// Its sibling in memo_audit_desk_test.go types five desk names, and it was
// already stale the day design landed - it passes without ever mentioning
// design, so it would not notice a seventh desk either. A test that has to be
// edited whenever the thing it tests changes is the same defect as a desk list
// typed in three places, one layer down.
func TestTheRefusalNamesEveryDeskTheRouterKnows(t *testing.T) {
	m := Memo{To: "designer", From: "Build", Subject: "s", Status: "open"}
	_, why, ok := memoDestination(m)
	if ok {
		t.Fatal("the near-miss addressee was accepted, so there is no refusal to read")
	}
	names := make([]string, 0, len(memoTrays))
	for k := range memoTrays {
		names = append(names, k)
	}
	sort.Strings(names)
	for _, desk := range names {
		if !strings.Contains(why, desk) {
			t.Errorf("the refusal message does not mention %q, so somebody "+
				"reading it would not know that desk exists: %s", desk, why)
		}
	}
}
