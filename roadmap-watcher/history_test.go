package main

// history_test.go - prove the history KEEPS things. Hard rule 12.
//
// The order names the check that matters:
//
//     "the check that matters is one proving a CHANGED card produces two rows
//      with different fingerprints and BOTH SURVIVE. A history that has never
//      been observed retaining anything is the same category of thing it exists
//      to prevent."
//
// So the test edits a card between two runs and reads the file back. And
// because a retention check that cannot fail is worth nothing, the last test
// deliberately destroys a row and confirms the same assertion catches it.

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func histResult(board int, surface string, cards []Card) FetchResult {
	return FetchResult{Board: board, Surface: surface, Cards: cards}
}

func constellation(id int, name, desc string) Card {
	return Card{ID: id, Name: name, Description: desc, ReleaseID: 42,
		Release: "3.14", Released: false}
}

// THE CHECK THAT MATTERS.
func TestChangedCardKeepsBothFingerprints(t *testing.T) {
	dir := t.TempDir()
	path := HistoryPath(dir)

	before := constellation(9001, "RSI Constellation Taurus", "as it was")
	if _, err := AppendObservations(path, histResult(1, "Release View",
		[]Card{before}), "Constellation", "scheduled", nil); err != nil {
		t.Fatalf("first run: %v", err)
	}

	// The card is edited on the board - the exact event the watcher exists to
	// notice, and the exact one that used to destroy its own evidence.
	after := constellation(9001, "RSI Constellation Taurus", "and as it became")
	if _, err := AppendObservations(path, histResult(1, "Release View",
		[]Card{after}), "Constellation", "scheduled", nil); err != nil {
		t.Fatalf("second run: %v", err)
	}

	rows, bad, err := ReadHistory(path)
	if err != nil {
		t.Fatalf("read: %v", err)
	}
	if bad != 0 {
		t.Fatalf("%d unreadable line(s) in a file this test just wrote", bad)
	}
	if len(rows) != 2 {
		t.Fatalf("expected 2 rows, got %d - the second run overwrote the first, "+
			"which is the defect this file exists to close", len(rows))
	}
	if rows[0].Fingerprint == rows[1].Fingerprint {
		t.Fatalf("both rows carry the same fingerprint %q - the change was not "+
			"recorded", rows[0].Fingerprint)
	}
	if rows[0].Fingerprint != Fingerprint(before) {
		t.Fatalf("the FIRST row no longer says what the card was: got %q, want %q. "+
			"The history is being rewritten.", rows[0].Fingerprint, Fingerprint(before))
	}
	if rows[1].Fingerprint != Fingerprint(after) {
		t.Fatalf("the second row does not carry the new fingerprint")
	}

	// EVERY ROW CARRIES ITS OWN CONTEXT, or a time series of bare hashes is
	// unreadable exactly when it finally matters.
	for i, r := range rows {
		if r.Board != 1 || r.Surface != "Release View" || r.CardID != 9001 ||
			r.Name != "RSI Constellation Taurus" || r.Release != "3.14" ||
			r.Source != "scheduled" || r.At == "" {
			t.Fatalf("row %d is missing its context: %+v", i, r)
		}
	}
}

// A RUN THAT CHANGES NOTHING STILL RECORDS. Without this the archive has holes
// exactly where a card sat still, and "was it the same in June?" cannot be
// answered - only "it changed in July".
func TestUnchangedCardStillAppends(t *testing.T) {
	dir := t.TempDir()
	path := HistoryPath(dir)
	c := constellation(9002, "Merlin/Constellation Docking", "unchanged")
	for i := 0; i < 3; i++ {
		if _, err := AppendObservations(path, histResult(1, "Release View",
			[]Card{c}), "Constellation", "scheduled", nil); err != nil {
			t.Fatalf("run %d: %v", i, err)
		}
	}
	rows, _, err := ReadHistory(path)
	if err != nil {
		t.Fatalf("read: %v", err)
	}
	if len(rows) != 3 {
		t.Fatalf("expected one row per run (3), got %d", len(rows))
	}
}

// ONLY WATCHED CARDS, and a board with none of them writes nothing rather than
// an empty file full of noise.
func TestOnlyMatchingCardsAreRecorded(t *testing.T) {
	dir := t.TempDir()
	path := HistoryPath(dir)
	n, err := AppendObservations(path, histResult(1, "Release View", []Card{
		constellation(1, "RSI Constellation Taurus", "watched"),
		constellation(2, "Drake Cutlass Black", "not watched"),
	}), "Constellation", "manual", nil)
	if err != nil {
		t.Fatalf("append: %v", err)
	}
	if n != 1 {
		t.Fatalf("expected 1 matching row, got %d", n)
	}
	rows, _, _ := ReadHistory(path)
	if len(rows) != 1 || !strings.Contains(rows[0].Name, "Constellation") {
		t.Fatalf("the wrong card was recorded: %+v", rows)
	}
}

// A TRUNCATED LINE MUST NOT DESTROY THE ARCHIVE. This file may be years old
// when a power cut catches it mid-write; one bad line is skipped and counted,
// never fatal.
func TestCorruptLineIsSkippedAndCounted(t *testing.T) {
	dir := t.TempDir()
	path := HistoryPath(dir)
	c := constellation(9003, "RSI Constellation Phoenix", "fine")
	_, _ = AppendObservations(path, histResult(1, "Release View", []Card{c}),
		"Constellation", "scheduled", nil)

	f, err := os.OpenFile(path, os.O_APPEND|os.O_WRONLY, 0o644)
	if err != nil {
		t.Fatalf("open: %v", err)
	}
	_, _ = f.WriteString("{\"at\":\"2026-08-17T00:00:00Z\",\"board\"\n")
	_ = f.Close()

	_, _ = AppendObservations(path, histResult(1, "Release View", []Card{c}),
		"Constellation", "scheduled", nil)

	rows, bad, err := ReadHistory(path)
	if err != nil {
		t.Fatalf("a single bad line made the whole archive unreadable: %v", err)
	}
	if bad != 1 {
		t.Fatalf("expected 1 unreadable line reported, got %d", bad)
	}
	if len(rows) != 2 {
		t.Fatalf("expected the 2 good rows to survive, got %d", len(rows))
	}
}

// NEGATIVE CONTROL - THE RETENTION CHECK CAN FAIL.
//
// Everything above asserts that rows survive. If the assertion could not detect
// a row that did NOT survive, it would pass on a file that was being
// overwritten every run - which is precisely the failure being fixed, wearing a
// green tick. So: write two rows, destroy one the way a truncating writer
// would, and confirm the same assertion catches it.
func TestRetentionCheckDetectsLoss(t *testing.T) {
	dir := t.TempDir()
	path := HistoryPath(dir)
	a := constellation(9004, "RSI Constellation Taurus", "before")
	b := constellation(9004, "RSI Constellation Taurus", "after")
	_, _ = AppendObservations(path, histResult(1, "Release View", []Card{a}),
		"Constellation", "scheduled", nil)
	_, _ = AppendObservations(path, histResult(1, "Release View", []Card{b}),
		"Constellation", "scheduled", nil)

	rows, _, _ := ReadHistory(path)
	if len(rows) != 2 {
		t.Fatalf("fixture is wrong: expected 2 rows before the damage, got %d",
			len(rows))
	}

	// What a rewriting writer leaves behind: only the newest row.
	last := rows[len(rows)-1]
	if err := os.WriteFile(path, mustLine(t, last), 0o644); err != nil {
		t.Fatalf("damage: %v", err)
	}

	rows, _, _ = ReadHistory(path)
	if len(rows) == 2 {
		t.Fatalf("the check cannot tell a kept history from a destroyed one")
	}
	if len(rows) != 1 || rows[0].Fingerprint != Fingerprint(b) {
		t.Fatalf("expected exactly the overwriting writer's single row, got %+v", rows)
	}
	// And that is what a failure looks like: the "before" fingerprint is gone.
	for _, r := range rows {
		if r.Fingerprint == Fingerprint(a) {
			t.Fatalf("the destroyed row is somehow still here - this control is " +
				"not controlling anything")
		}
	}
}

func mustLine(t *testing.T, o Observation) []byte {
	t.Helper()
	dir := t.TempDir()
	p := filepath.Join(dir, "one.jsonl")
	res := histResult(o.Board, o.Surface, []Card{{
		ID: o.CardID, Name: o.Name, Description: "after", ReleaseID: 42,
		Release: o.Release, Released: o.Released,
	}})
	if _, err := AppendObservations(p, res, "Constellation", o.Source, nil); err != nil {
		t.Fatalf("mustLine: %v", err)
	}
	b, err := os.ReadFile(p)
	if err != nil {
		t.Fatalf("mustLine read: %v", err)
	}
	return b
}
