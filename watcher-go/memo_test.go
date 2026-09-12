package main

// memo_test.go - a memo reaches the right desk, and nothing else becomes a memo.
//
// The negative controls are the point. Routing that only proves it CAN deliver
// is routing nobody has tested; what costs real work is a document quietly
// posted to somebody because it happened to contain the word "To:".

import (
	"os"
	"path/filepath"
	"testing"
)

// TestAnAnsweredMemoLeavesTheOpenTray asserts where an answered memo GOES. It
// does not touch the filesystem, so it never noticed that the original STAYS.
// That defect reached the live trays on 2026-08-30 and put the same memo in two
// places at once, one of them still reading "Status: Open".
//
// This test is the one its name describes: answer a memo and confirm the open
// copy is no longer in the tray - and, per hard rule 1, that it was kept rather
// than deleted.
func TestAnsweringActuallyEmptiesTheOpenTray(t *testing.T) {
	root := t.TempDir()
	restore := correspondenceDir
	correspondenceDir = filepath.Join(root, "correspondence")
	defer func() { correspondenceDir = restore }()

	openBuild := filepath.Join(correspondenceDir, "open", "build")
	if err := os.MkdirAll(openBuild, 0o755); err != nil {
		t.Fatal(err)
	}
	const base = "2026-08-30_a-question.md"
	const body = "the original question, as it was asked"
	stale := filepath.Join(openBuild, base)
	if err := os.WriteFile(stale, []byte(body), 0o644); err != nil {
		t.Fatal(err)
	}

	// The second argument is the tray the answer was just filed into, which
	// this test does not have - nothing was filed, only swept.
	if tray := clearOpenCopy(base, ""); tray != "build" {
		t.Fatalf("clearOpenCopy reported %q, want \"build\"", tray)
	}
	if _, err := os.Stat(stale); !os.IsNotExist(err) {
		t.Fatal("the answered memo's open copy is STILL in the tray, so the " +
			"same question reads as both answered and waiting")
	}

	kept, _ := filepath.Glob(filepath.Join(root, "_to_delete", base+".superseded-*"))
	if len(kept) != 1 {
		t.Fatalf("rule 1: the superseded copy was not kept, found %v", kept)
	}
	got, err := os.ReadFile(kept[0])
	if err != nil || string(got) != body {
		t.Fatalf("the kept copy is not the original question: %v / %q", err, got)
	}
}

// A memo that has NOT been answered must not have its open copy swept. The
// sweep is keyed on the filename, so this is the case where a same-named
// document arriving for another reason would silently empty somebody's tray.
func TestNothingIsSweptWhenNoOpenCopyExists(t *testing.T) {
	root := t.TempDir()
	restore := correspondenceDir
	correspondenceDir = filepath.Join(root, "correspondence")
	defer func() { correspondenceDir = restore }()

	if err := os.MkdirAll(filepath.Join(correspondenceDir, "open", "build"),
		0o755); err != nil {
		t.Fatal(err)
	}
	if tray := clearOpenCopy("2026-08-30_no-such-memo.md", ""); tray != "" {
		t.Fatalf("clearOpenCopy claimed to sweep %q when nothing was there", tray)
	}
	if _, err := os.Stat(filepath.Join(root, "_to_delete")); err == nil {
		t.Fatal("it created _to_delete/ for a sweep that had nothing to move")
	}
}

const realMemo = `# Memo

To:      Architecture
From:    Build
Date:    2026-08-30
Subject: CLAUDE.md and OWNERS.md disagree on testing/
Status:  Open

CLAUDE.md says testing/ is Build's. OWNERS.md assigns three page files to
Architecture. Q35 needs all three. Stopping rather than writing.
`

func TestAMemoIsReadAndAddressed(t *testing.T) {
	m, ok := readMemo(realMemo)
	if !ok {
		t.Fatal("a memo with To, From and Subject was not recognised as one")
	}
	if m.To != "architecture" {
		t.Fatalf("addressed to %q, want architecture", m.To)
	}
	if m.From != "Build" || m.Status != "open" {
		t.Fatalf("from=%q status=%q", m.From, m.Status)
	}
	dir, _, ok := memoDestination(m)
	if !ok {
		t.Fatal("a memo to a real desk was refused")
	}
	if want := "open"; !contains(dir, want) || !contains(dir, "architecture") {
		t.Fatalf("filed to %q, want the open architecture tray", dir)
	}
}

// REWRITTEN 2026-09-10. It used to require an answered memo to land in
// answered/, which is the defect Sleven found: every answer, from every desk, to
// every recipient, went into an archive nobody reads.
//
// `realMemo` is To: Architecture, From: Build. Answered, it goes BACK TO BUILD -
// not to Architecture, whose name is still on the To: line, and not to the
// archive.
func TestAnAnsweredMemoGoesBackToTheSender(t *testing.T) {
	m, _ := readMemo(realMemo + "\nStatus: Answered\n")
	// Status appears twice; the LAST word wins is NOT what happens - the first
	// match is taken - so assert the behaviour rather than assume it.
	m.Status = "answered"
	dir, _, ok := memoDestination(m)
	if !ok || !contains(dir, "open") || !contains(dir, "build") {
		t.Fatalf("an answered memo from Build filed to %q, want the open "+
			"build tray", dir)
	}
	if contains(dir, "answered") {
		t.Fatalf("an answer went to the archive: %q", dir)
	}
}

// Closed is what puts a thread in the archive now, and it is a deliberate act by
// a desk rather than a side effect of somebody replying once.
func TestAClosedMemoGoesToTheArchive(t *testing.T) {
	m, _ := readMemo(realMemo + "\nStatus: Closed\n")
	m.Status = "closed"
	dir, _, ok := memoDestination(m)
	if !ok || !contains(dir, "answered") || contains(dir, "open") {
		t.Fatalf("a closed memo filed to %q, want the archive", dir)
	}
}

// NEGATIVE CONTROL 1: an ordinary document must not become a memo.
func TestAnOrdinaryDocumentIsNotAMemo(t *testing.T) {
	for _, text := range []string{
		"# FINDING — the page speaks CIG file shorthand\n\nTo: be clear, this is prose.\n",
		"# WORK ORDER\n\nFrom: the measurements below, three things follow.\n",
		"# Update\n\nSubject: matter experts disagree.\n",
	} {
		if _, ok := readMemo(text); ok {
			t.Fatalf("prose was classified as a memo:\n%s", text)
		}
	}
}

// NEGATIVE CONTROL 2: a memo to nobody is refused, not delivered somewhere.
func TestAMemoToAnUnknownDeskIsRefused(t *testing.T) {
	m, ok := readMemo("To: Marketing\nFrom: Build\nSubject: nope\n")
	if !ok {
		t.Fatal("it should still parse as a memo - it is addressed, just not to us")
	}
	if _, why, ok := memoDestination(m); ok {
		t.Fatal("a memo to a desk that does not exist was delivered anyway")
	} else if why == "" {
		t.Fatal("it was refused without saying why, which is the same as losing it")
	}
}

// NEGATIVE CONTROL 3: the real defect this project already paid for.
// A memo whose SUBJECT contains "update" must not be filed as an update doc.
// classifyMarkdown checks memos first for exactly this reason.
func TestAMemoAboutAnUpdateIsStillAMemo(t *testing.T) {
	text := "To: Build\nFrom: Architecture\nSubject: the 4.10 update changes eight names\n"
	if _, ok := readMemo(text); !ok {
		t.Fatal("a memo whose subject mentions an update stopped being a memo")
	}
}

// NEGATIVE CONTROL 4: a header buried deep in a long document is not an address.
func TestAQuotedHeaderDeepInADocumentIsNotAnAddress(t *testing.T) {
	long := make([]byte, 5000)
	for i := range long {
		long[i] = 'x'
	}
	text := string(long) + "\nTo: Architecture\nFrom: Build\nSubject: buried\n"
	if _, ok := readMemo(text); ok {
		t.Fatal("a header 5000 bytes down was treated as the document's address")
	}
}

func contains(s, sub string) bool {
	for i := 0; i+len(sub) <= len(s); i++ {
		if s[i:i+len(sub)] == sub {
			return true
		}
	}
	return false
}
