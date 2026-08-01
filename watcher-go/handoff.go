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

// firstRunesUpper was removed 2026-08-01. It returned the first n runes of a
// document body, uppercased, and was the mechanism by which both classifiers
// scanned prose for keywords - the cause of Defect 2. titleLine below replaces
// it. Nothing else called it.

// titleLine returns the doc's own title, uppercased -- its first markdown
// heading, or its first non-blank line. A doc's type is stated by its title,
// not by whatever it mentions in passing.
//
// Until 2026-08-01 both classifiers scanned the first 500 runes of the BODY, so
// any update that merely mentioned "handoff" early was treated as a full
// handoff doc: it overwrote _latest_raw.md, replaced the whole PROJECT NOTES
// section, and never reached the updates log at all.
func titleLine(text string) string {
	for _, line := range strings.Split(text, "\n") {
		stripped := strings.TrimSpace(line)
		if stripped == "" {
			continue
		}
		if strings.HasPrefix(stripped, "#") {
			return strings.ToUpper(strings.TrimSpace(strings.TrimLeft(stripped, "#")))
		}
		return strings.ToUpper(stripped)
	}
	return ""
}

func isHandoffDoc(path string, text string) bool {
	name := strings.ToLower(strings.TrimSuffix(filepath.Base(path), filepath.Ext(path)))
	for _, hint := range handoffFilenameHints {
		if strings.Contains(name, hint) {
			return true
		}
	}
	head := titleLine(text)
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
	head := titleLine(text)
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
