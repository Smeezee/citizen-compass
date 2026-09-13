package main

// memo_status_line_test.go - a letter with no Status: line, or a value outside the
// list, is refused at FILING time (Architecture, 2026-09-12). And BOOT.md counts,
// per desk, the letters it could not read instead of leaving them out of the sum.
//
// Real router, real files, then LOOK AT THE DIRECTORIES - the house style of
// memo_closed_record_test.go. newTree, drop and memoText are memo_answer_routing_test.go's.

import (
	"fmt"
	"strings"
	"testing"
)

const noStatusMemo = "# Memo\n\nTo:      Build\nFrom:    Architecture\nSubject: a letter with no status line\n\nThe body.\n"

func TestAMemoWithNoStatusLineIsRefused(t *testing.T) {
	root := newTree(t)
	_, dest := drop(t, root, "no-status.md", noStatusMemo)
	if !strings.Contains(dest, "_needs_review") {
		t.Fatalf("a memo with no Status: line was filed to %q - it must be refused to _needs_review", dest)
	}
}

// The live instance, 2026-09-12: "Open - PARTLY ANSWERED AND PARTLY WITHDRAWN".
func TestAMemoWithAQualifiedStatusIsRefused(t *testing.T) {
	root := newTree(t)
	_, dest := drop(t, root, "qualified.md",
		memoText("Owner", "Architecture", "Open - PARTLY ANSWERED AND PARTLY WITHDRAWN", "The body."))
	if !strings.Contains(dest, "_needs_review") {
		t.Fatalf("a Status: outside the list was filed to %q", dest)
	}
}

// Every value in use still files exactly as before - proven by filing, not by reading.
func TestEveryStatusInTheListStillFiles(t *testing.T) {
	root := newTree(t)
	record := "Thread.\n\nCLOSED:\n\n**Closed. Nothing owed back.** The record is here in full."
	cases := []struct{ status, body string }{
		{"Open", "A question."},
		{"open", "A question, lower-case status."},
		{"Answered", "Q.\n\nANSWERS:\n\nThe answer, written out properly."},
		{"Closed", record},
		{"Done", record},
	}
	for i, c := range cases {
		_, dest := drop(t, root, fmt.Sprintf("ok-%d.md", i), memoText("Build", "Owner", c.status, c.body))
		if strings.Contains(dest, "_needs_review") {
			t.Fatalf("Status: %s was refused (%q) - the list must keep every value in use", c.status, dest)
		}
	}
}

func TestTheStatusRefusalSaysWhatToAdd(t *testing.T) {
	if why := statusProblem(noStatusMemo); !strings.Contains(why, "Status: Open") {
		t.Fatalf("the refusal does not tell the writer what to add: %q", why)
	}
	if why := statusProblem(memoText("Build", "Owner", "Open", "x")); why != "" {
		t.Fatalf("a valid Status: was reported as a problem: %q", why)
	}
}

// BOOT.md: a letter it cannot read is COUNTED, per desk, and 0 is printed, not omitted.
func TestBootCountsLettersItCouldNotRead(t *testing.T) {
	r := bootTree(t)
	row := func(desk string, open, unreadable int) string {
		return fmt.Sprintf("    %-12s %5d  %10d", desk, open, unreadable)
	}
	page := buildBoot(r, bootNow, true)
	if !strings.Contains(page, row("build", 1, 0)) {
		t.Fatalf("the build row does not read 1 open, 0 unreadable:\n%s", page)
	}
	bootPut(t, r, "correspondence/open/build/2026-09-12_memo_build_nostatus.md", noStatusMemo)
	bootPut(t, r, "correspondence/open/build/2026-09-12_memo_build_qualified.md",
		strings.Replace(noStatusMemo, "Subject:", "Status:  Open - PARTLY\nSubject:", 1))
	page = buildBoot(r, bootNow, true)
	if !strings.Contains(page, row("build", 1, 2)) {
		t.Fatalf("two letters with no valid Status: are not counted as unreadable:\n%s", page)
	}
}
