package main

// The watcher was a LIVE PRODUCER of mixed line endings.
//
// `git ls-files --eol` found seven tracked files with mixed worktree endings on
// 2026-08-30. One of them - docs/handoff_archive/_updates_log.md - is written by
// this program. appendUpdate wrote a bare "\n" into a file whose existing lines
// end "\r\n", on every single update filed, so the mixing was not history: it
// was going to keep happening.
//
// Architecture's ruling was "fix the producer, not the product": correcting the
// writer stops recurrence without a bulk rewrite of files nobody has complained
// about. These two tests are that fix held to rule 12 - one for each direction,
// because a writer that always emitted CRLF would pass the first and be just as
// wrong.

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func withArchive(t *testing.T) string {
	t.Helper()
	dir := t.TempDir()
	restore := handoffArchiveDir
	handoffArchiveDir = dir
	t.Cleanup(func() { handoffArchiveDir = restore })
	return dir
}

// A CRLF log must not gain lone LF lines. This is the live defect.
func TestAppendingToACRLFLogDoesNotMixEndings(t *testing.T) {
	dir := withArchive(t)
	path := filepath.Join(dir, "_updates_log.md")
	seed := "### 2026-01-01 00:00:00 — seed.md\r\n\r\n# UPDATE\r\n\r\nbody\r\n"
	if err := os.WriteFile(path, []byte(seed), 0o644); err != nil {
		t.Fatal(err)
	}

	if err := appendUpdate("# UPDATE\n\nsomething happened", "new.md"); err != nil {
		t.Fatal(err)
	}

	b, err := os.ReadFile(path)
	if err != nil {
		t.Fatal(err)
	}
	got := string(b)
	// A lone LF is any "\n" not preceded by "\r".
	lone := 0
	for i := 0; i < len(got); i++ {
		if got[i] == '\n' && (i == 0 || got[i-1] != '\r') {
			lone++
		}
	}
	if lone != 0 {
		t.Fatalf("appending to a CRLF log introduced %d lone LF line ending(s) - "+
			"the file is now mixed, which is the defect this test exists for", lone)
	}
	if !strings.Contains(got, "new.md") {
		t.Fatal("the entry was not appended at all")
	}
}

// THE OTHER DIRECTION, AND IT MATTERS AS MUCH. A writer that simply always
// emitted CRLF would pass the test above and would be a new defect: it would
// convert every LF log on every append, which is the bulk rewrite the ruling
// explicitly refused.
func TestAppendingToAnLFLogStaysLF(t *testing.T) {
	dir := withArchive(t)
	path := filepath.Join(dir, "_updates_log.md")
	seed := "### 2026-01-01 00:00:00 — seed.md\n\n# UPDATE\n\nbody\n"
	if err := os.WriteFile(path, []byte(seed), 0o644); err != nil {
		t.Fatal(err)
	}

	if err := appendUpdate("# UPDATE\n\nsomething happened", "new.md"); err != nil {
		t.Fatal(err)
	}

	b, err := os.ReadFile(path)
	if err != nil {
		t.Fatal(err)
	}
	if strings.Contains(string(b), "\r\n") {
		t.Fatal("appending to an LF log introduced CRLF - the writer is " +
			"converting files instead of matching them, which is the bulk " +
			"rewrite the ruling refused")
	}
}

// A log that does not exist yet is LF. A failure to read is not a reason to
// guess CRLF, and a new file should not inherit the platform's habit.
func TestANewLogIsLF(t *testing.T) {
	dir := withArchive(t)
	if err := appendUpdate("# UPDATE\n\nfirst ever", "first.md"); err != nil {
		t.Fatal(err)
	}
	b, err := os.ReadFile(filepath.Join(dir, "_updates_log.md"))
	if err != nil {
		t.Fatal(err)
	}
	if strings.Contains(string(b), "\r\n") {
		t.Fatal("a brand-new log was written with CRLF")
	}
}
