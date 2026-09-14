package main

// memo_answer_routing_test.go - an answer goes back to the desk that asked.
//
// EVERY ASSERTION HERE TOUCHES THE FILESYSTEM, and that is the whole reason the
// file exists. `TestAnAnsweredMemoLeavesTheOpenTray` asserted the path
// memoDestination RETURNED and never looked at a directory, so it passed for a
// month while the same memo existed twice - and memo.go says so in its own
// comment. Asserting a returned string is asserting that a function agrees with
// itself.
//
// The defect these guard, found by Sleven on 2026-09-10: the answered test ran
// before the To: line was read, so every answer from every desk went to
// correspondence/answered/. Nine of Architecture's letters to him were in there
// and his tray showed one item all afternoon.

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
)

// newTree builds an empty correspondence tree and points the package at it.
// Not parallel: these swap package-level globals.
func newTree(t *testing.T) string {
	t.Helper()
	root := t.TempDir()
	oldC, oldN := correspondenceDir, needsReviewDir
	correspondenceDir = filepath.Join(root, "correspondence")
	needsReviewDir = filepath.Join(root, "_needs_review")
	t.Cleanup(func() { correspondenceDir, needsReviewDir = oldC, oldN })

	for _, tray := range memoTrays {
		if err := os.MkdirAll(filepath.Join(correspondenceDir, "open", tray),
			0o755); err != nil {
			t.Fatal(err)
		}
	}
	if err := os.MkdirAll(filepath.Join(correspondenceDir, "answered"),
		0o755); err != nil {
		t.Fatal(err)
	}
	return root
}

func memoText(to, from, status, body string) string {
	return "# Memo\n\nTo:      " + to + "\nFrom:    " + from +
		"\nDate:    2026-09-10\nSubject: the thing that needs deciding\nStatus:  " +
		status + "\n\n" + body + "\n"
}

// drop puts a file in a holding folder and runs the real router over it.
func drop(t *testing.T, root, base, text string) (string, string) {
	t.Helper()
	in := filepath.Join(root, "inbox")
	if err := os.MkdirAll(in, 0o755); err != nil {
		t.Fatal(err)
	}
	p := filepath.Join(in, base)
	if err := os.WriteFile(p, []byte(text), 0o644); err != nil {
		t.Fatal(err)
	}
	note, dest, handled, err := classifyMemo(p, text)
	if err != nil {
		t.Fatalf("classifyMemo: %v", err)
	}
	if !handled {
		t.Fatalf("%q was not recognised as a memo at all", base)
	}
	return note, dest
}

func mustExist(t *testing.T, path, why string) {
	t.Helper()
	if _, err := os.Stat(path); err != nil {
		t.Fatalf("%s: %s is not there (%v)", why, path, err)
	}
}

func mustNotExist(t *testing.T, path, why string) {
	t.Helper()
	if _, err := os.Stat(path); err == nil {
		t.Fatalf("%s: %s is STILL there", why, path)
	}
}

const base = "2026-09-10_the-question.md"

// THE MAIN EVENT. Architecture is asked something by Build; Architecture
// answers; the answer has to arrive in BUILD's tray, the stale question has to
// leave Architecture's, and THE ANSWER HAS TO STILL BE THERE when the dust
// settles.
//
// RUN TWENTY-FIVE TIMES, WITH A FRESH TREE EACH TIME, because the failure this
// guards is Go's randomised map iteration order. A single green run proves
// nothing at all here - it proves one draw of a coin.
func TestAnAnswerArrivesInTheSendersTrayAndSurvives(t *testing.T) {
	for i := 0; i < 25; i++ {
		root := newTree(t)
		question := filepath.Join(correspondenceDir, "open", "engineering", base)
		if err := os.WriteFile(question,
			[]byte(memoText("Engineering", "Build", "Open", "the question")),
			0o644); err != nil {
			t.Fatal(err)
		}

		note, dest := drop(t, root, base,
			memoText("Engineering", "Build", "Answered",
				"the question\n\nANSWERS:\n\nthe answer, which must not vanish"))

		answer := filepath.Join(correspondenceDir, "open", "build", base)
		if dest != answer {
			t.Fatalf("run %d: the answer went to %q, want %q", i, dest, answer)
		}
		mustExist(t, answer, "run "+string(rune('0'+i%10))+
			": THE ANSWER ITSELF was swept away by the supersede loop")
		body, err := os.ReadFile(answer)
		if err != nil || !strings.Contains(string(body), "must not vanish") {
			t.Fatalf("run %d: the file in build's tray is not the answer: %v", i, err)
		}
		mustNotExist(t, question,
			"the answered question is still sitting in Engineering's tray")
		if !strings.Contains(note, "superseded the open copy in engineering") {
			t.Fatalf("run %d: the note does not say what was superseded: %q", i, note)
		}
		kept, _ := filepath.Glob(filepath.Join(root, "_to_delete", base+".superseded-*"))
		if len(kept) != 1 {
			t.Fatalf("run %d: rule 1 - the superseded copy was not kept: %v", i, kept)
		}
	}
}

// THE GUARD IS LOAD-BEARING, AND THIS IS WHAT PROVES IT RATHER THAN ASSERTING
// IT. Call the sweep the way the old code did - with nothing to skip - and the
// answer is what gets moved aside, on roughly half the runs.
//
// It is probabilistic on purpose: two trays hold the basename, the loop takes
// the first hit, and Go shuffles. Forty draws makes "it never happened" a
// 1-in-10^12 event. If this test ever reports zero, the map order stopped being
// random and the whole argument for the skip needs re-reading.
func TestWithoutTheSkipTheSweepEatsTheAnswer(t *testing.T) {
	eaten := 0
	for i := 0; i < 40; i++ {
		root := newTree(t)
		question := filepath.Join(correspondenceDir, "open", "engineering", base)
		answer := filepath.Join(correspondenceDir, "open", "build", base)
		for _, p := range []string{question, answer} {
			if err := os.WriteFile(p, []byte("x"), 0o644); err != nil {
				t.Fatal(err)
			}
		}
		if tray := clearOpenCopy(base, ""); tray == "build" {
			eaten++
			mustNotExist(t, answer, "it reported moving build's copy")
		}
		_ = root
	}
	if eaten == 0 {
		t.Fatal("the unguarded sweep never once took the answer in 40 runs, so " +
			"either the map order is no longer random or this test is not " +
			"exercising what it claims to")
	}
	t.Logf("the unguarded sweep took the ANSWER on %d of 40 runs - that is the "+
		"defect the skip argument exists to close", eaten)
}

// Closed is the only thing that reaches the archive now, and the tray copy still
// has to leave.
func TestClosedGoesToTheArchiveAndStillClearsTheTray(t *testing.T) {
	root := newTree(t)
	question := filepath.Join(correspondenceDir, "open", "engineering", base)
	if err := os.WriteFile(question, []byte("the question"), 0o644); err != nil {
		t.Fatal(err)
	}
	_, dest := drop(t, root, base,
		// Carries its CLOSED: record since 2026-09-12: a close WITHOUT one is now
		// refused at filing (memo_closed_record_test.go). This test is about where
		// a proper close goes and what it clears, and that is unchanged.
		memoText("Engineering", "Build", "Closed",
			"done with this\n\nCLOSED:\n\nClosed - the thread is finished, nothing owed back."))

	if want := filepath.Join(correspondenceDir, "answered", base); dest != want {
		t.Fatalf("a closed memo went to %q, want %q", dest, want)
	}
	mustNotExist(t, question, "a closed thread is still sitting in a tray")
}

// AN UNKNOWN SENDER IS REFUSED, NOT GUESSED AT - and, just as important,
// NOTHING IS MOVED OUT OF ANY TRAY when it is. A refusal that also swept the
// original would turn one bad header into a lost question.
func TestAnAnsweredMemoFromAnUnknownDeskIsRefused(t *testing.T) {
	root := newTree(t)
	question := filepath.Join(correspondenceDir, "open", "engineering", base)
	if err := os.WriteFile(question, []byte("the question"), 0o644); err != nil {
		t.Fatal(err)
	}
	// Was `Research (CIC)` until 2026-09-12, when a trailing parenthetical became
	// a SIGNATURE (Architecture's order) and that address started delivering to
	// Research - memo_signature_clearout_test.go proves it. An unknown desk WITH
	// a signature is the case that must still be refused, quoted back whole.
	note, dest := drop(t, root, base,
		memoText("Engineering", "Legal (Outside Counsel)", "Answered", "an answer"))

	if !strings.Contains(dest, "_needs_review") {
		t.Fatalf("an answer from an unknown desk was filed to %q", dest)
	}
	if !strings.Contains(note, "Legal (Outside Counsel)") || !strings.Contains(note, "From:") {
		t.Fatalf("the refusal does not say what was wrong or why: %q", note)
	}
	mustExist(t, question,
		"a refused answer swept the original question out of its tray")
	if _, err := os.Stat(filepath.Join(root, "_to_delete")); err == nil {
		t.Fatal("a refused answer moved something aside")
	}
}

// A desk answering its own memo has nobody to send it back to.
func TestADeskAnsweringItselfGoesToTheArchive(t *testing.T) {
	root := newTree(t)
	note, dest := drop(t, root, base,
		memoText("Build", "Build", "Answered", "a note to myself"))
	if want := filepath.Join(correspondenceDir, "answered", base); dest != want {
		t.Fatalf("a self-addressed answer went to %q, want %q", dest, want)
	}
	if !strings.Contains(note, "itself") {
		t.Fatalf("the note does not explain the archive: %q", note)
	}
}

// AND THE TRAFFIC THAT WORKS TODAY MUST NOT CHANGE. From: is validated only
// where it decides delivery; an OPEN letter with an odd From: still routes on
// To:, exactly as it did yesterday.
func TestAnOpenMemoWithAnOddFromStillRoutesOnTo(t *testing.T) {
	root := newTree(t)
	_, dest := drop(t, root, base,
		memoText("Engineering", "Research (CIC)", "Open", "a question"))
	if want := filepath.Join(correspondenceDir, "open", "engineering", base); dest != want {
		t.Fatalf("an open memo with an odd From: went to %q, want %q", dest, want)
	}
}

// The four status words, in one place, so the contract is readable as a table.
func TestTheFourStatusWordsRouteWhereTheSpecSays(t *testing.T) {
	// A close carries its record since 2026-09-12 - without one it is refused at
	// filing, which memo_closed_record_test.go proves. The table here is about
	// ROUTING, so each close is given a real record and the routes are unchanged.
	closeBody := "body\n\nCLOSED:\n\nClosed - the thread is finished, nothing owed back."
	for _, c := range []struct {
		status string
		want   string
		body   string
	}{
		{"Open", filepath.Join("open", "engineering"), "body"},
		{"Answered", filepath.Join("open", "build"), "body"},
		{"Closed", "answered", closeBody},
		{"Done", "answered", closeBody},
	} {
		root := newTree(t)
		_, dest := drop(t, root, base,
			memoText("Engineering", "Build", c.status, c.body))
		if !strings.Contains(dest, c.want) {
			t.Fatalf("Status: %s filed to %q, want it under %q",
				c.status, dest, c.want)
		}
	}
}
