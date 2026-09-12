package main

// memo_signature_clearout_test.go - the other two mail repairs Architecture
// ordered on 2026-09-12. Every case runs the real router over a real file and
// then LOOKS AT THE DIRECTORIES.
//
//	1  a trailing parenthetical on To:/From: is a SIGNATURE, not an address:
//	   `From: Research (CIC)` delivers to Research, and the "(CIC)" is kept.
//	2  a returned answer can be CLEARED from the tray it came home to: a
//	   byte-identical re-drop files to answered/ instead of duplicating.

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestAnAnswerSignedResearchCICGoesHomeToResearch(t *testing.T) {
	root := newTree(t)
	note, dest := drop(t, root, base,
		memoText("Architecture", "Research (CIC)", "Answered", "Q.\n\nANSWERS:\n\nThe answer, in full."))
	if want := filepath.Join(correspondenceDir, "open", "research", base); dest != want {
		t.Fatalf("an answer signed `Research (CIC)` went to %q, want %q", dest, want)
	}
	if !strings.Contains(note, "(CIC)") {
		t.Fatalf("the signature was stripped and LOST - the note must keep it: %q", note)
	}
}

func TestAnOpenMemoToASignedDeskReachesTheDesk(t *testing.T) {
	root := newTree(t)
	_, dest := drop(t, root, base, memoText("Build (Code)", "Owner", "Open", "a question"))
	if want := filepath.Join(correspondenceDir, "open", "build", base); dest != want {
		t.Fatalf("a memo to `Build (Code)` went to %q, want %q", dest, want)
	}
}

// A PARENTHETICAL WITH NOTHING BEFORE IT IS NOT A SIGNATURE - there is no desk
// name left to deliver to, so it fails closed as an unknown sender.
func TestAnAddressThatIsOnlyAParentheticalIsStillRefused(t *testing.T) {
	root := newTree(t)
	_, dest := drop(t, root, base, memoText("Architecture", "(CIC)", "Answered", "an answer"))
	if !strings.Contains(dest, "_needs_review") {
		t.Fatalf("an answer From: `(CIC)` alone was delivered to %q", dest)
	}
}

func TestSplitSignature(t *testing.T) {
	for _, c := range []struct{ in, name, sig string }{
		{"Research (CIC)", "Research", "(CIC)"},
		{"  Research   (CIC)  ", "Research", "(CIC)"},
		{"Research", "Research", ""},
		{"(CIC)", "(CIC)", ""},
		{"Research (a) (b)", "Research (a)", "(b)"},
	} {
		n, s := splitSignature(c.in)
		if n != c.name || s != c.sig {
			t.Fatalf("splitSignature(%q) = %q, %q; want %q, %q", c.in, n, s, c.name, c.sig)
		}
	}
}

// Research's exact case: the answer came home, and dropping the SAME file back
// must clear it - not park a timestamped twin beside it.
func TestAnIdenticalReDropOfAReturnedAnswerClearsTheTray(t *testing.T) {
	root := newTree(t)
	text := memoText("Design", "Research", "Answered", "Q.\n\nANSWERS:\n\nThe answer, in full.")
	home := filepath.Join(correspondenceDir, "open", "research", base)
	if err := os.WriteFile(home, []byte(text), 0o644); err != nil {
		t.Fatal(err)
	}
	note, dest := drop(t, root, base, text)
	if want := filepath.Join(correspondenceDir, "answered", base); dest != want {
		t.Fatalf("an identical re-drop went to %q, want %q (note %q)", dest, want, note)
	}
	mustNotExist(t, home, "the returned answer is still in the tray after being cleared")
	entries, _ := os.ReadDir(filepath.Join(correspondenceDir, "open", "research"))
	if len(entries) != 0 {
		t.Fatalf("the research tray is not empty after a clear-out: %d file(s)", len(entries))
	}
	aside, _ := filepath.Glob(filepath.Join(root, "_to_delete", base+".superseded-*"))
	if len(aside) != 1 {
		t.Fatalf("the tray copy was not moved aside exactly once (rule 1): %v", aside)
	}
}

// A CHANGED answer of the same name is a second round, not a clear-out: it must
// NOT be swept to the archive - the newest stays in the tray, as before.
func TestAChangedAnswerOfTheSameNameStaysInTheTray(t *testing.T) {
	root := newTree(t)
	home := filepath.Join(correspondenceDir, "open", "research", base)
	first := memoText("Design", "Research", "Answered", "Q.\n\nANSWERS:\n\nThe first answer.")
	if err := os.WriteFile(home, []byte(first), 0o644); err != nil {
		t.Fatal(err)
	}
	second := memoText("Design", "Research", "Answered", "Q.\n\nANSWERS:\n\nA second, different answer.")
	_, dest := drop(t, root, base, second)
	if dest != home {
		t.Fatalf("a changed answer went to %q, want it in the tray at %q", dest, home)
	}
	got, _ := os.ReadFile(home)
	if string(got) != second {
		t.Fatal("the tray does not hold the newest answer")
	}
	mustNotExist(t, filepath.Join(correspondenceDir, "answered", base),
		"a changed answer was swept to the archive as if it were a clear-out")
}
