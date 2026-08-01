package main

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
)

// Exercises the fixed parser against the LIVE _updates_log.md. Asserts the
// invariant (every entry begins with a timestamped header) rather than a fixed
// count, since the log grows. Reports the counts so drift is visible.
func TestLiveUpdatesLog_NoPhantomEntries(t *testing.T) {
	// handoffArchiveDir is populated by main(), which never runs under go
	// test, and go test's cwd is the package dir - so point it at the repo.
	saved := handoffArchiveDir
	handoffArchiveDir = filepath.Join("..", "docs", "handoff_archive")
	defer func() { handoffArchiveDir = saved }()

	path := updatesLogPath()
	raw, err := os.ReadFile(path)
	if err != nil {
		t.Skipf("live log not readable: %v", err)
	}
	totalHashHeaders := 0
	for _, line := range strings.Split(string(raw), "\n") {
		if strings.HasPrefix(strings.TrimSpace(line), "### ") {
			totalHashHeaders++
		}
	}
	entries := parseUpdateEntriesFrom(path)
	phantoms := 0
	for _, e := range entries {
		if !stampedHeader.MatchString(e) {
			phantoms++
			t.Errorf("phantom entry: %q", firstLine(e))
		}
	}
	t.Logf("live log: %d total '###' headers, %d parsed entries, %d phantoms",
		totalHashHeaders, len(entries), phantoms)
	if len(entries) >= totalHashHeaders && totalHashHeaders > len(entries) {
		t.Errorf("parser returned %d entries for %d headers", len(entries), totalHashHeaders)
	}
}
