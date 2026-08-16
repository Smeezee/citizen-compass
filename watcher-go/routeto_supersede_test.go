package main

// routeto_supersede_test.go - a corrected document must land where people look.
//
// THIS REPRODUCES A LIVE FAILURE, not a hypothetical one. On 2026-08-14 a
// corrected AMENDS document was filed and the watcher gave the NEWCOMER the
// timestamped name, leaving the plain filename holding rev 1 - which
// misattributed a decision to Sleven that he never made. The correction existed,
// was filed, and went somewhere nobody opens.
//
// The property under test: after any number of arrivals, the plain filename
// holds the NEWEST content, and every earlier version still exists.

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
	"time"
)

func writeFile(t *testing.T, path, body string) {
	t.Helper()
	if err := os.WriteFile(path, []byte(body), 0o644); err != nil {
		t.Fatal(err)
	}
}

func readFile(t *testing.T, path string) string {
	t.Helper()
	b, err := os.ReadFile(path)
	if err != nil {
		t.Fatal(err)
	}
	return string(b)
}

// THE CASE THAT HAPPENED.
func TestACorrectionTakesThePlainFilename(t *testing.T) {
	dir := t.TempDir()
	inbox := filepath.Join(dir, "inbox")
	docs := filepath.Join(dir, "docs")
	if err := os.MkdirAll(inbox, 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.MkdirAll(docs, 0o755); err != nil {
		t.Fatal(err)
	}

	name := "AMENDS_tripwire-release-view-only-2026-08-14.md"
	dest := filepath.Join(docs, name)

	// rev 1 arrives and is filed under the plain name.
	src1 := filepath.Join(inbox, name)
	writeFile(t, src1, "REV 1 - WRONG: says the tracker is not cleared for polling")
	if _, _, err := routeTo(src1, dest, "filed"); err != nil {
		t.Fatal(err)
	}
	if got := readFile(t, dest); !strings.Contains(got, "REV 1") {
		t.Fatalf("rev 1 did not land under the plain name: %q", got)
	}

	// Make rev 1's mtime distinct so the archive stamp is meaningful.
	old := time.Now().Add(-2 * time.Hour)
	if err := os.Chtimes(dest, old, old); err != nil {
		t.Fatal(err)
	}

	// rev 2, the correction, arrives with the same name.
	src2 := filepath.Join(inbox, name)
	writeFile(t, src2, "REV 2 - RIGHT: he said 'for now', meaning sequencing")
	note, finalPath, err := routeTo(src2, dest, "filed")
	if err != nil {
		t.Fatal(err)
	}

	// THE POINT. Whoever opens the obvious filename must get the correction.
	if finalPath != dest {
		t.Fatalf("the correction was filed as %q, not under the plain name", finalPath)
	}
	if got := readFile(t, dest); !strings.Contains(got, "REV 2") {
		t.Fatalf("the plain filename still holds the superseded text: %q", got)
	}

	// AND NOTHING WAS DESTROYED - rule 1.
	entries, _ := os.ReadDir(docs)
	var archived string
	for _, e := range entries {
		if e.Name() != name && strings.HasPrefix(e.Name(), "AMENDS_") {
			archived = filepath.Join(docs, e.Name())
		}
	}
	if archived == "" {
		t.Fatal("rev 1 vanished; superseding must keep both")
	}
	if got := readFile(t, archived); !strings.Contains(got, "REV 1") {
		t.Fatalf("the archived file is not rev 1: %q", got)
	}

	// The note has to SAY so, or the log reads as an ordinary filing.
	if !strings.Contains(note, "SUPERSEDES") {
		t.Fatalf("the note does not mention superseding: %q", note)
	}
}

// NEGATIVE CONTROL: with no collision, nothing is renamed and no archive is
// created. Without this, a routeTo that archived unconditionally would satisfy
// the test above while making a mess of every ordinary filing.
func TestAFirstArrivalIsNotTreatedAsASupersede(t *testing.T) {
	dir := t.TempDir()
	src := filepath.Join(dir, "new.md")
	writeFile(t, src, "first")
	dest := filepath.Join(dir, "out", "new.md")

	note, final, err := routeTo(src, dest, "filed")
	if err != nil {
		t.Fatal(err)
	}
	if final != dest {
		t.Fatalf("a first arrival was renamed to %q", final)
	}
	if strings.Contains(note, "SUPERSEDES") {
		t.Fatalf("a first arrival was reported as superseding: %q", note)
	}
	entries, _ := os.ReadDir(filepath.Dir(dest))
	if len(entries) != 1 {
		t.Fatalf("a first arrival produced %d files, want 1", len(entries))
	}
}

// Two corrections inside the same second must both survive. A second-resolution
// stamp collides, and an os.Rename onto an existing archive would silently
// destroy the first one - "we kept both" has to be true every time or it is a
// probability rather than a property.
func TestTwoCorrectionsInOneSecondBothSurvive(t *testing.T) {
	dir := t.TempDir()
	dest := filepath.Join(dir, "doc.md")

	writeFile(t, dest, "rev 1")
	when := time.Now()
	_ = os.Chtimes(dest, when, when)

	for i := 2; i <= 4; i++ {
		src := filepath.Join(dir, "incoming.md")
		writeFile(t, src, "rev "+string(rune('0'+i)))
		if _, _, err := routeTo(src, dest, "filed"); err != nil {
			t.Fatal(err)
		}
		// Force every archive to want the same stamp.
		_ = os.Chtimes(dest, when, when)
	}

	if got := readFile(t, dest); !strings.Contains(got, "rev 4") {
		t.Fatalf("plain name holds %q, want the newest", got)
	}
	entries, _ := os.ReadDir(dir)
	if len(entries) != 4 {
		names := []string{}
		for _, e := range entries {
			names = append(names, e.Name())
		}
		t.Fatalf("want 4 files (3 archived + the current one), got %d: %v",
			len(entries), names)
	}
}
