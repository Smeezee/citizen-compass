package main

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"time"
)

// Mirrors generate_handoff.py's HANDOFF_*/UPDATE_* hint constants and the
// is_handoff_doc/is_update_doc/append_update functions exactly, since
// generate_handoff.py itself is staying in Python for now (not touched by
// this migration step) but inbox_watcher.py needs the same classification
// logic to decide where a dropped .md goes.

var handoffFilenameHints = []string{"handoff", "session_archive", "session-archive"}
var handoffHeadingHints = []string{"HANDOFF", "SESSION ARCHIVE", "AI KNOWLEDGE BASE"}

var updateFilenameHints = []string{"update", "updates"}
var updateHeadingHints = []string{"UPDATE", "UPDATES", "CHANGELOG"}

func latestRawPath() string {
	return filepath.Join(handoffArchiveDir, "_latest_raw.md")
}

func updatesLogPath() string {
	return filepath.Join(handoffArchiveDir, "_updates_log.md")
}

// firstRunesUpper returns the first n runes of s, uppercased -- a
// rune-safe equivalent of Python's text[:500].upper(), so a multi-byte
// UTF-8 character never gets split mid-sequence.
func firstRunesUpper(s string, n int) string {
	r := []rune(s)
	if len(r) > n {
		r = r[:n]
	}
	return strings.ToUpper(string(r))
}

func isHandoffDoc(path string, text string) bool {
	name := strings.ToLower(strings.TrimSuffix(filepath.Base(path), filepath.Ext(path)))
	for _, hint := range handoffFilenameHints {
		if strings.Contains(name, hint) {
			return true
		}
	}
	head := firstRunesUpper(text, 500)
	for _, hint := range handoffHeadingHints {
		if strings.Contains(head, hint) {
			return true
		}
	}
	return false
}

func isUpdateDoc(path string, text string) bool {
	name := strings.ToLower(strings.TrimSuffix(filepath.Base(path), filepath.Ext(path)))
	for _, hint := range updateFilenameHints {
		if strings.Contains(name, hint) {
			return true
		}
	}
	head := firstRunesUpper(text, 500)
	for _, hint := range updateHeadingHints {
		if strings.Contains(head, hint) {
			return true
		}
	}
	return false
}

// appendUpdate appends one timestamped entry to the running updates log --
// never overwrites, matching generate_handoff.py's append_update() exactly.
func appendUpdate(text string, sourceName string) error {
	if err := os.MkdirAll(handoffArchiveDir, 0755); err != nil {
		return err
	}
	timestamp := time.Now().Format("2006-01-02 15:04:05")
	entry := fmt.Sprintf("### %s — %s\n\n%s\n", timestamp, sourceName, strings.TrimSpace(text))

	needsLeadingBlank := false
	if info, err := os.Stat(updatesLogPath()); err == nil && info.Size() > 0 {
		needsLeadingBlank = true
	}

	f, err := os.OpenFile(updatesLogPath(), os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		return err
	}
	defer f.Close()

	if needsLeadingBlank {
		if _, err := f.WriteString("\n"); err != nil {
			return err
		}
	}
	_, err = f.WriteString(entry)
	return err
}
