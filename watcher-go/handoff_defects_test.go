package main

import (
	"os"
	"path/filepath"
	"regexp"
	"strings"
	"testing"
)

// Rule 12: a check that cannot fail is not a check. Every test here feeds
// known-bad input to a defect that was live in this binary and asserts the
// fixed behaviour. Reading the diff and declaring it fixed does not satisfy
// this.

var stampedHeader = regexp.MustCompile(`^### \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}`)

// --- DEFECT 1: parseUpdateEntries invented entries that were never logged ---

// A body containing ### subheadings must yield exactly ONE entry, not one per
// subheading, and must not be truncated at the first subheading.
func TestParseUpdateEntries_SubheadingsStayInsideTheirEntry(t *testing.T) {
	dir := t.TempDir()
	logPath := filepath.Join(dir, "_updates_log.md")
	content := "### 2026-01-01 00:00:00 — a.md\n\n" +
		"# UPDATE\n\nIntro paragraph.\n\n" +
		"### Subheading One\n\nBelongs to a.md.\n\n" +
		"### Subheading Two\n\nAlso belongs to a.md.\n\n" +
		"### 2026-01-02 00:00:00 — b.md\n\n" +
		"# UPDATE\n\nSecond entry.\n"
	if err := os.WriteFile(logPath, []byte(content), 0o644); err != nil {
		t.Fatal(err)
	}

	entries := parseUpdateEntriesFrom(logPath)

	if len(entries) != 2 {
		t.Fatalf("expected 2 entries, got %d: %#v", len(entries), entries)
	}
	for i, e := range entries {
		if !stampedHeader.MatchString(e) {
			t.Errorf("entry %d does not begin with a timestamped header: %q", i, firstLine(e))
		}
	}
	if !strings.Contains(entries[0], "Subheading One") {
		t.Error("entry 1 lost 'Subheading One' - it was truncated at the subheading")
	}
	if !strings.Contains(entries[0], "Subheading Two") {
		t.Error("entry 1 lost 'Subheading Two'")
	}
}

// Edge case required by the work order: a log with no recognisable headers must
// return the whole file as one entry rather than dropping content.
func TestParseUpdateEntries_NoHeadersReturnsWholeFile(t *testing.T) {
	dir := t.TempDir()
	logPath := filepath.Join(dir, "_updates_log.md")
	body := "no timestamped headers here at all\njust prose\n"
	if err := os.WriteFile(logPath, []byte(body), 0o644); err != nil {
		t.Fatal(err)
	}
	entries := parseUpdateEntriesFrom(logPath)
	if len(entries) != 1 {
		t.Fatalf("expected the whole file as 1 entry, got %d", len(entries))
	}
	if !strings.Contains(entries[0], "just prose") {
		t.Error("content was dropped")
	}
}

// Edge case required by the work order: preamble before the first header is
// kept, not discarded.
func TestParseUpdateEntries_PreamblePreserved(t *testing.T) {
	dir := t.TempDir()
	logPath := filepath.Join(dir, "_updates_log.md")
	content := "preamble text written before any header\n\n" +
		"### 2026-01-01 00:00:00 — a.md\n\nbody\n"
	if err := os.WriteFile(logPath, []byte(content), 0o644); err != nil {
		t.Fatal(err)
	}
	entries := parseUpdateEntriesFrom(logPath)
	if len(entries) != 2 {
		t.Fatalf("expected preamble + 1 entry = 2, got %d", len(entries))
	}
	if !strings.Contains(entries[0], "preamble text") {
		t.Error("preamble was discarded")
	}
}

// A hyphen separator must parse as well as an em dash.
func TestParseUpdateEntries_HyphenSeparatorParses(t *testing.T) {
	dir := t.TempDir()
	logPath := filepath.Join(dir, "_updates_log.md")
	content := "### 2026-01-01 00:00:00 - a.md\n\nbody\n"
	if err := os.WriteFile(logPath, []byte(content), 0o644); err != nil {
		t.Fatal(err)
	}
	if got := len(parseUpdateEntriesFrom(logPath)); got != 1 {
		t.Fatalf("expected 1 entry, got %d", got)
	}
}

// --- DEFECT 2: classification scanned prose instead of the title ---

func TestIsHandoffDoc_UpdateMentioningHandoffInBodyIsNotAHandoff(t *testing.T) {
	text := "# UPDATE - push landed\n\nCorrects the session handoff filed earlier.\n"
	if isHandoffDoc("update_push_landed.md", text) {
		t.Error("update whose BODY mentions 'handoff' was classified as a handoff doc")
	}
	if !isUpdateDoc("update_push_landed.md", text) {
		t.Error("it should classify as an update doc")
	}
}

func TestIsHandoffDoc_GenuineHandoffStillDetectedByTitle(t *testing.T) {
	if !isHandoffDoc("state_dump.md", "# CITIZEN COMPASS HANDOFF\n\nFull state.\n") {
		t.Error("a genuine handoff title was not detected")
	}
	if !isHandoffDoc("state_dump2.md", "# SESSION ARCHIVE\n\nArchived.\n") {
		t.Error("SESSION ARCHIVE title was not detected")
	}
}

// Evaluation order must not change: filename hints win, and isHandoffDoc runs
// before isUpdateDoc, so a doc matching both is a full handoff.
func TestIsHandoffDoc_FilenameHintStillWins(t *testing.T) {
	if !isHandoffDoc("weekly_handoff_notes.md", "# UPDATE\n\nSmall note.\n") {
		t.Error("filename hint no longer wins - evaluation order changed")
	}
}

func TestTitleLine_UsesFirstHeadingOrFirstNonBlankLine(t *testing.T) {
	cases := []struct{ in, want string }{
		{"# UPDATE - thing\n\nbody handoff\n", "UPDATE - THING"},
		{"\n\n## Session Archive\nbody\n", "SESSION ARCHIVE"},
		{"plain first line\n# LATER HEADING\n", "PLAIN FIRST LINE"},
		{"", ""},
	}
	for _, c := range cases {
		if got := titleLine(c.in); got != c.want {
			t.Errorf("titleLine(%q) = %q, want %q", c.in, got, c.want)
		}
	}
}

func firstLine(s string) string {
	if i := strings.IndexByte(s, '\n'); i >= 0 {
		return s[:i]
	}
	return s
}
