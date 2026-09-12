package main

// memo_closed_record_test.go - a Closed or Done letter without its record is
// refused at FILING time, not discovered by a sweep hours later (2026-09-12).
//
// Every case runs the real router over a real file and then LOOKS AT THE
// DIRECTORIES - the lesson memo_answer_routing_test.go records: asserting the
// path a function returns is asserting that it agrees with itself.
//
// The first refused case is the exact shape that turned two sweeps red on
// 2026-09-12: a closing round ending in a bare "CLOSED." with a full stop.

// mustNotExist, newTree, drop and memoText are memo_answer_routing_test.go's.
import (
	"path/filepath"
	"strings"
	"testing"
)

func TestAClosedMemoWithOnlyABareClosedFullStopIsRefused(t *testing.T) {
	root := newTree(t)
	body := "## ROUND 3 - CLOSED by Audit, 2026-09-12\n\nRecorded and taken.\n\nCLOSED."
	_, dest := drop(t, root, "bare-closed.md", memoText("Design", "Audit", "Closed", body))
	if !strings.Contains(dest, "_needs_review") {
		t.Fatalf("a bare `CLOSED.` was filed to %q - it must be refused to _needs_review", dest)
	}
	mustNotExist(t, filepath.Join(correspondenceDir, "answered", "bare-closed.md"),
		"a refused close must not reach answered/")
}

func TestAClosedMemoWithNoMarkerAtAllIsRefused(t *testing.T) {
	root := newTree(t)
	_, dest := drop(t, root, "no-marker.md",
		memoText("Owner", "Architecture", "Closed", "**Owner. Answered and closed.** All ruled."))
	if !strings.Contains(dest, "_needs_review") {
		t.Fatalf("a close with no marker was filed to %q", dest)
	}
}

func TestADoneMemoWithATickUnderTheMarkerIsRefused(t *testing.T) {
	root := newTree(t)
	_, dest := drop(t, root, "tick.md", memoText("Build", "Owner", "Done", "CLOSED:\n\nok"))
	if !strings.Contains(dest, "_needs_review") {
		t.Fatalf("a marker with two characters under it was filed to %q", dest)
	}
}

func TestAClosedMemoWithARealClosedRecordIsFiled(t *testing.T) {
	root := newTree(t)
	body := "Some thread.\n\nCLOSED:\n\n**Closed. Nothing owed back.** The record is here in full."
	_, dest := drop(t, root, "good-close.md", memoText("Design", "Audit", "Closed", body))
	if strings.Contains(dest, "_needs_review") {
		t.Fatalf("a close WITH its record was refused: %q", dest)
	}
	if !strings.Contains(dest, filepath.Join("correspondence", "answered")) {
		t.Fatalf("a close with its record was filed to %q, want answered/", dest)
	}
}

func TestADoneMemoWithAnAnswersBlockIsFiled(t *testing.T) {
	root := newTree(t)
	body := "The question.\n\nANSWERS:\n\nYes, and here is the reasoning in a full sentence."
	_, dest := drop(t, root, "done-answers.md", memoText("Build", "Owner", "Done", body))
	if !strings.Contains(dest, filepath.Join("correspondence", "answered")) {
		t.Fatalf("a Done memo with ANSWERS: was filed to %q, want answered/", dest)
	}
}

// THE RULE DOES NOT REACH PAST CLOSED AND DONE. An Open letter carries no record
// yet and an Answered one is held to ANSWERS: by the control, not here.
func TestOpenAndAnsweredMemosAreNotHeldToTheCloseRule(t *testing.T) {
	root := newTree(t)
	_, dest := drop(t, root, "open.md", memoText("Build", "Owner", "Open", "A question."))
	if strings.Contains(dest, "_needs_review") {
		t.Fatalf("an Open memo was refused by the close rule: %q", dest)
	}
	_, dest = drop(t, root, "answered.md",
		memoText("Owner", "Build", "Answered", "Q.\n\nANSWERS:\n\nThe answer, written out properly."))
	if strings.Contains(dest, "_needs_review") {
		t.Fatalf("an Answered memo was refused by the close rule: %q", dest)
	}
}

// THE REASON TRAVELS WITH THE REFUSAL - a bounce nobody can act on is a loss.
func TestTheRefusalSaysWhatToAdd(t *testing.T) {
	_, why := closedRecord("CLOSED.")
	if !strings.Contains(why, "CLOSED:") || !strings.Contains(why, "colon") {
		t.Fatalf("the refusal does not tell the writer what to add: %q", why)
	}
	ok, _ := closedRecord("x\nCLOSED:\n\n" + strings.Repeat("r", 20))
	if !ok {
		t.Fatal("exactly 20 characters under the marker must pass - the control's own threshold")
	}
	ok, _ = closedRecord("x\nCLOSED:\n\n" + strings.Repeat("r", 19))
	if ok {
		t.Fatal("19 characters under the marker must be refused")
	}
}
