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

// docTypePrefixes maps this project's naming convention to what a document IS.
//
// A PREFIX IS AN EXPLICIT DECLARATION BY WHOEVER WROTE THE FILE, and it beats
// anything inferred from prose. It exists because inference got it wrong in a
// way nobody would have caught by reading the code:
//
//	WORKORDER_rework-tripwire-build-spec-2026-08-14.md
//	title: "...and do NOT key on updateDate."
//
// "UPDATE" is a substring of "updateDate", so a work order was filed as an
// update doc and routed into handoff_archive/ - and the amendment that pointed
// at it then pointed somewhere nobody would look. The same shape as the old
// Python generator, where the word "handoff" in any document hijacked its
// routing.
//
// "" means "this type is neither a handoff nor an update" - it is a document
// that keeps its own name and goes where documents go. That is the case the
// misrouting broke.
//
// THE LIST IS TAKEN FROM THE DIRECTORY, NOT FROM MEMORY. Enumerating docs/ by
// prefix is how ADDENDUM_ was found missing: the first version of this map was
// written from the types I happened to have seen, and an ADDENDUM whose title
// read "a stopped watcher must not look like an update saying nothing" routed
// straight into the archive on the word "update". Third instance of the same
// bite in one evening.
var docTypePrefixes = map[string]string{
	"workorder_":    "",
	"workorder-":    "",
	"finding_":      "",
	"finding-":      "",
	"decision_":     "",
	"erratum_":      "",
	"erratum-":      "",
	"amends_":       "",
	"addendum_":     "",
	"addendum-":     "",
	"ruling_":       "",
	"report_":       "",
	"urgent_":       "",
	"project-":      "",
	"architecture_": "",
	"current-":      "",
	"screenshot_":   "",
	"prompt-":       "",
	"ai-":           "",
	"handoff_":      "handoff",
	"update-":       "update",
	"update_":       "update",
}

// docTypeFromPrefix returns the declared type and whether one was declared.
//
// Checked longest-first so a longer prefix cannot be shadowed by a shorter one
// that happens to be its head.
func docTypeFromPrefix(path string) (string, bool) {
	name := strings.ToLower(filepath.Base(path))
	best, bestLen, found := "", 0, false
	for p, kind := range docTypePrefixes {
		if strings.HasPrefix(name, p) && len(p) > bestLen {
			best, bestLen, found = kind, len(p), true
		}
	}
	return best, found
}

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
	// AN EXPLICIT DECLARATION WINS. If the filename says what this is, the
	// prose is not consulted - see docTypePrefixes.
	if kind, ok := docTypeFromPrefix(path); ok {
		return kind == "handoff"
	}
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
	if kind, ok := docTypeFromPrefix(path); ok {
		return kind == "update"
	}
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
