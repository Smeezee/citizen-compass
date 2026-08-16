package main

// routing_prefix_test.go - prose must not decide where a document goes.
//
// THE CASE THAT HAPPENED: a WORK ORDER whose title says "do NOT key on
// updateDate" was classified as an update doc, because "UPDATE" is a substring
// of "updateDate". It was routed into handoff_archive/ and the amendment that
// referenced it then pointed somewhere nobody would look.

import "testing"

// The real filename and the real title line, verbatim.
const reworkTitle = "# WORK ORDER — build spec for the rework tripwires, now that the " +
	"endpoints are known. Watch BOTH roadmap surfaces, key on card presence and a " +
	"payload hash, and do NOT key on updateDate."

func TestAWorkOrderIsNotAnUpdateDocBecauseItSaysUpdateDate(t *testing.T) {
	path := "WORKORDER_rework-tripwire-build-spec-2026-08-14.md"
	if isUpdateDoc(path, reworkTitle) {
		t.Fatal("a WORK ORDER was classified as an update doc - this is the live " +
			"misrouting: 'UPDATE' matched inside 'updateDate'")
	}
	if isHandoffDoc(path, reworkTitle) {
		t.Fatal("a WORK ORDER was classified as a handoff doc")
	}
}

// NEGATIVE CONTROL: real update docs must still be recognised, or the fix has
// simply switched the routing off. Every one of these is a filename this
// session actually produced.
func TestRealUpdateDocsAreStillRecognised(t *testing.T) {
	for _, name := range []string{
		"update-slots-are-now-1-to-N.md",
		"update-hotkey-is-a-burst.md",
		"update_something_else.md",
	} {
		if !isUpdateDoc(name, "# Update — something happened") {
			t.Fatalf("%s is no longer recognised as an update doc", name)
		}
	}
}

// A handoff is still a handoff.
func TestHandoffDocsAreStillRecognised(t *testing.T) {
	if !isHandoffDoc("HANDOFF_c3-outstanding-2026-08-10.md", "# HANDOFF") {
		t.Fatal("a HANDOFF_ document was not recognised")
	}
	if isUpdateDoc("HANDOFF_c3-outstanding-2026-08-10.md", "# HANDOFF") {
		t.Fatal("a handoff was also claimed as an update doc")
	}
}

// Documents with NO type prefix still fall back to the title hints, which is
// most of what lands in inbox/. The bug was never that the hints exist - it was
// that they outranked an explicit declaration.
func TestUnprefixedDocsStillUseTitleHints(t *testing.T) {
	if !isUpdateDoc("notes-from-tonight.md", "# UPDATE — what happened") {
		t.Fatal("an unprefixed doc with an UPDATE title was not routed as one")
	}
	if !isHandoffDoc("notes-from-tonight.md", "# HANDOFF — state of play") {
		t.Fatal("an unprefixed doc with a HANDOFF title was not routed as one")
	}
}

// The other prefixed types are documents in their own right and must be neither.
func TestOtherDocumentTypesAreNeither(t *testing.T) {
	for _, name := range []string{
		"FINDING_holo-loadout-join-is-100-percent-2026-08-13.md",
		"DECISION_screenshots-are-internal-only-2026-08-13.md",
		"ERRATUM-collector-leak-and-location-parser-2026-08-13.md",
		"AMENDS_tripwire-release-view-only-2026-08-14.md",
		"prompt-code-loadout-real-data-2026-08-13.md",
	} {
		// Titles deliberately containing the trap words.
		title := "# Something — this mentions an UPDATE and a HANDOFF in passing"
		if isUpdateDoc(name, title) || isHandoffDoc(name, title) {
			t.Fatalf("%s was hijacked by a word in its title", name)
		}
	}
}
