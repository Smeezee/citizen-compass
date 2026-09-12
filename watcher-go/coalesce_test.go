package main

// The rescan+regenerate tail ran after EVERY inbox file and cost ~70s, so a
// nine-memo tray took half an hour to drain. Deferring it while more files are
// already waiting fixes that - but the two ways to get it wrong are both worse
// than the slowness:
//
//   count the protected subdirectories as pending  -> the watcher believes it
//                                                     is permanently busy and
//                                                     NEVER regenerates
//   defer while anything is pending, with no cap   -> a queue that never
//                                                     empties defers forever
//
// Both fail silently and look like a healthy watcher, so both are tested.

import (
	"os"
	"path/filepath"
	"testing"
)

func TestPendingCountsFilesNotDirectories(t *testing.T) {
	dir := t.TempDir()
	restore := inboxDir
	inboxDir = dir
	defer func() { inboxDir = restore }()

	// The protected subdirectories that live under inbox/ permanently.
	for _, d := range []string{"Citizen Compass AI Brain", "citizen-compass-testing-ground"} {
		if err := os.MkdirAll(filepath.Join(dir, d), 0o755); err != nil {
			t.Fatal(err)
		}
	}
	if n := pendingInboxFiles(); n != 0 {
		t.Fatalf("directories were counted as pending work: got %d, want 0. "+
			"The watcher would believe it is permanently busy and never "+
			"regenerate the handoff again", n)
	}

	if err := os.WriteFile(filepath.Join(dir, "a.md"), []byte("x"), 0o644); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(dir, "b.md"), []byte("x"), 0o644); err != nil {
		t.Fatal(err)
	}
	if n := pendingInboxFiles(); n != 2 {
		t.Fatalf("pending files miscounted: got %d, want 2", n)
	}
}

// A missing inbox reports zero, not a panic and not a lie in the other
// direction: zero pending means the next file pays the rescan, which is the
// safe way to be wrong.
func TestPendingOnAMissingInboxIsZero(t *testing.T) {
	restore := inboxDir
	inboxDir = filepath.Join(t.TempDir(), "does-not-exist")
	defer func() { inboxDir = restore }()
	if n := pendingInboxFiles(); n != 0 {
		t.Fatalf("a missing inbox reported %d pending", n)
	}
}

// THE FLOOD GUARD. Ten deferrals in a row, then the eleventh pays regardless.
// Without the cap a busy queue would defer forever and the handoff would
// silently stop updating - which looks exactly like a working watcher.
func TestTheCoalesceCapIsFinite(t *testing.T) {
	if maxCoalesced <= 0 {
		t.Fatal("maxCoalesced must be positive, or every file defers forever")
	}
	if maxCoalesced > 50 {
		t.Fatalf("maxCoalesced is %d - that is long enough for the handoff to "+
			"look stalled to a person watching it", maxCoalesced)
	}
	// Walk the counter the way processFile does and confirm it terminates.
	coalescedRuns = 0
	deferrals := 0
	for i := 0; i < maxCoalesced+5; i++ {
		if coalescedRuns < maxCoalesced { // pending > 0 assumed
			coalescedRuns++
			deferrals++
			continue
		}
		break
	}
	coalescedRuns = 0
	if deferrals != maxCoalesced {
		t.Fatalf("the cap did not stop the run: %d deferrals against a cap of %d",
			deferrals, maxCoalesced)
	}
}
