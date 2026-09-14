package main

// The audit desk, added 2026-09-08 on Sleven's ruling that a new desk gets a
// mailing path when it is created rather than when somebody asks whether it
// wants one.
//
// THE RISK IN ADDING A DESK IS NOT THE DESK. It is that widening the list
// quietly widens what the list REFUSES. A memo to a desk that does not exist
// must still go to _needs_review, because a letter delivered to the wrong desk
// is worse than one that visibly failed to arrive. Both directions are asserted
// here rather than trusting that the existing negative test still covers it.

import (
	"path/filepath"
	"strings"
	"testing"
)

func TestTheAuditDeskCanReceivePost(t *testing.T) {
	m := Memo{To: "audit", From: "Build", Subject: "s", Status: "open"}
	dir, why, ok := memoDestination(m)
	if !ok {
		t.Fatalf("a memo to audit was refused: %s", why)
	}
	if filepath.Base(dir) != "audit" {
		t.Fatalf("a memo to audit was filed to %q", dir)
	}
}

// Case is normalised the same way for the new desk as for the old ones -
// readMemo lowercases To, so "Audit" in a header must reach the same tray.
func TestTheAuditDeskIsCaseFolded(t *testing.T) {
	m, ok := readMemo("To: Audit\nFrom: Build\nSubject: s\n")
	if !ok {
		t.Fatal("a memo addressed to Audit was not read as a memo at all")
	}
	if m.To != "audit" {
		t.Fatalf("To was normalised to %q, not \"audit\"", m.To)
	}
	if _, _, ok := memoDestination(m); !ok {
		t.Fatal("Audit with a capital A did not reach the audit tray")
	}
}

// THE ONE THAT MATTERS. Adding a fifth valid name must not soften the refusal
// of an invalid one.
func TestAddingAuditDidNotWidenWhatIsAccepted(t *testing.T) {
	for _, bad := range []string{"legal", "auditing", "audits", "aud", "", "  "} {
		m := Memo{To: bad, From: "Build", Subject: "s", Status: "open"}
		dir, why, ok := memoDestination(m)
		if ok {
			t.Errorf("a memo to %q was ACCEPTED and filed to %q - the desk list "+
				"has stopped being a list", bad, dir)
		}
		if bad == "legal" && !strings.Contains(why, "not one of") {
			t.Errorf("the refusal does not say what the real desks are: %s", why)
		}
	}
}

// And the refusal message must name the new desk, or somebody reading it will
// not know audit is an option.
func TestTheRefusalNamesEveryRealDesk(t *testing.T) {
	m := Memo{To: "legal", From: "Build", Subject: "s", Status: "open"}
	_, why, _ := memoDestination(m)
	for _, desk := range []string{"engineering", "build", "research", "audit", "owner"} {
		if !strings.Contains(why, desk) {
			t.Errorf("the refusal message does not mention %q: %s", desk, why)
		}
	}
}
