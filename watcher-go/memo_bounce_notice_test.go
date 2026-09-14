package main

// memo_bounce_notice_test.go - the DONE-WHEN for Architecture's order of
// 2026-09-13: an answer with an unresolvable From: still lands in _needs_review/
// exactly as it does today, AND a notice appears in the tray of the desk that
// wrote the answer; a deliverable answer produces no notice. Both directions,
// through the real router (drop -> classifyMemo).

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func notices(t *testing.T) []string {
	t.Helper()
	var out []string
	_ = filepath.Walk(correspondenceDir, func(p string, info os.FileInfo, err error) error {
		if err == nil && !info.IsDir() && strings.Contains(filepath.Base(p), "_undeliverable-answer_") {
			out = append(out, p)
		}
		return nil
	})
	return out
}

func TestARefusedAnswerTellsTheDeskThatWroteIt(t *testing.T) {
	root := newTree(t)
	note, dest := drop(t, root, base,
		memoText("Engineering", "Grok (Design / CIC)", "Answered", "Q.\n\nANSWERS:\n\nthe ruling"))
	if !strings.Contains(dest, "_needs_review") {
		t.Fatalf("the refused answer is no longer refused - it went to %q", dest)
	}
	ns := notices(t)
	if len(ns) != 1 {
		t.Fatalf("want exactly one notice, got %v", ns)
	}
	if filepath.Base(filepath.Dir(ns[0])) != "engineering" {
		t.Fatalf("the notice went to %q, not the tray of the desk that wrote the answer", ns[0])
	}
	raw, err := os.ReadFile(ns[0])
	if err != nil {
		t.Fatal(err)
	}
	text := string(raw)
	for _, want := range []string{base, "_needs_review", "Grok (Design / CIC)", "not one of", "Status:  Open"} {
		if !strings.Contains(text, want) {
			t.Fatalf("the notice does not name %q:\n%s", want, text)
		}
	}
	nm, ok := readMemo(text)
	if !ok {
		t.Fatal("the notice is not itself a memo, so the mail checks would call it junk")
	}
	if d, why, ok := memoDestination(nm); !ok || filepath.Base(d) != "engineering" {
		t.Fatalf("the notice would not route to the answering desk: %q %s", d, why)
	}
	if !strings.Contains(note, "was told") {
		t.Fatalf("the router's note does not record the notice: %q", note)
	}
}

func TestADeliverableAnswerProducesNoNotice(t *testing.T) {
	root := newTree(t)
	_, dest := drop(t, root, base, memoText("Engineering", "Build", "Answered", "an answer"))
	if want := filepath.Join(correspondenceDir, "open", "build", base); dest != want {
		t.Fatalf("a deliverable answer went to %q, want %q", dest, want)
	}
	if ns := notices(t); len(ns) != 0 {
		t.Fatalf("a deliverable answer produced a notice: %v", ns)
	}
}

func TestAnOpenLetterWithAnOddFromProducesNoNotice(t *testing.T) {
	root := newTree(t)
	drop(t, root, base, memoText("Engineering", "Grok (Design / CIC)", "Open", "a question"))
	if ns := notices(t); len(ns) != 0 {
		t.Fatalf("an OPEN letter produced a bounce notice: %v", ns)
	}
}

func TestWhenToIsNotADeskEitherNobodyIsTold(t *testing.T) {
	root := newTree(t)
	note, dest := drop(t, root, base, memoText("Legal", "Grok (Design / CIC)", "Answered", "an answer"))
	if !strings.Contains(dest, "_needs_review") {
		t.Fatalf("went to %q", dest)
	}
	if ns := notices(t); len(ns) != 0 {
		t.Fatalf("a notice was written with no desk to tell: %v", ns)
	}
	if !strings.Contains(note, "nobody told") {
		t.Fatalf("the note does not say nobody could be told: %q", note)
	}
}

func TestARedroppedBounceIsToldOnceNotTwice(t *testing.T) {
	root := newTree(t)
	text := memoText("Engineering", "Grok (Design / CIC)", "Answered", "an answer")
	drop(t, root, base, text)
	ns := notices(t)
	if len(ns) != 1 {
		t.Fatalf("the first bounce produced %d notices, want 1", len(ns))
	}
	// A desk may already have written on the notice; a second bounce must not erase it.
	f, err := os.OpenFile(ns[0], os.O_APPEND|os.O_WRONLY, 0o644)
	if err != nil {
		t.Fatal(err)
	}
	_, _ = f.WriteString("\nREAD BY THE DESK\n")
	f.Close()
	note, _ := drop(t, root, base, text)
	if ns2 := notices(t); len(ns2) != 1 {
		t.Fatalf("a re-dropped bounce produced %d notices, want 1: %v", len(ns2), ns2)
	}
	raw, _ := os.ReadFile(ns[0])
	if !strings.Contains(string(raw), "READ BY THE DESK") {
		t.Fatal("a re-dropped bounce OVERWROTE the notice the desk had already touched")
	}
	if !strings.Contains(note, "already told") {
		t.Fatalf("the second note does not say the desk was already told: %q", note)
	}
}

func TestARefusedLetterThatIsNotAnAnswerMentionsNoNotice(t *testing.T) {
	root := newTree(t)
	note, dest := drop(t, root, base, memoText("Legal", "Build", "Open", "a question to nobody"))
	if !strings.Contains(dest, "_needs_review") {
		t.Fatalf("an open letter to no desk was delivered to %q", dest)
	}
	if strings.Contains(note, "told") || len(notices(t)) != 0 {
		t.Fatalf("a refused OPEN letter was treated as a bounced answer: %q", note)
	}
}
