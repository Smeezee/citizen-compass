package main

import (
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strconv"
	"strings"
	"time"
)

const (
	maxUpdatesShown = 20
)

var (
	latestHandoffPath  string
	updateCounterPath  string
)

func initHandoffPaths() {
	latestHandoffPath = filepath.Join(projectRoot, "LATEST_HANDOFF.md")
	updateCounterPath = filepath.Join(handoffArchiveDir, ".handoff_update_counter")
}

func nextUpdateCounter() int {
	n := 0
	if raw, err := os.ReadFile(updateCounterPath); err == nil {
		if parsed, perr := strconv.Atoi(strings.TrimSpace(string(raw))); perr == nil {
			n = parsed
		}
	}
	n++
	os.MkdirAll(filepath.Dir(updateCounterPath), 0755)
	os.WriteFile(updateCounterPath, []byte(strconv.Itoa(n)), 0644)
	return n
}

func buildAutoBlock(p *ccppPacket) string {
	if p == nil {
		return "**[UNKNOWN]** ccpp.py scan not found or failed — could not pull current project stats."
	}

	var lines []string
	lines = append(lines,
		fmt.Sprintf("**Generated:** %s (auto-regenerated every time a file lands in inbox/ or this script runs — don't hand-edit this section)", time.Now().Format("2006-01-02 15:04:05")),
		"",
		fmt.Sprintf("**Project health score:** %.1f/100", p.Scores.OverallHealth),
		fmt.Sprintf("- Data completeness: %.1f%%", p.Scores.DataCompleteness),
		fmt.Sprintf("- Viewer progress: %.1f%%", p.Scores.ViewerProgress),
		fmt.Sprintf("- Documentation: %.1f%%", p.Scores.Documentation),
		"",
		fmt.Sprintf("**Ships:** %d complete viewers / %d total (%.1f%%)",
			p.Crossref.ShipsWithViewers, p.Crossref.ShipsTotal, p.Crossref.ViewersProgressPct),
	)

	var complete, incomplete []string
	for slug, s := range p.Inventory.Ships {
		if s.ViewerComplete {
			complete = append(complete, slug)
		} else {
			incomplete = append(incomplete, slug)
		}
	}
	sort.Strings(complete)
	sort.Strings(incomplete)
	if len(complete) > 0 {
		lines = append(lines, fmt.Sprintf("- Complete: %s", strings.Join(complete, ", ")))
	}
	if len(incomplete) > 0 {
		shown := incomplete
		more := ""
		if len(incomplete) > 10 {
			shown = incomplete[:10]
			more = fmt.Sprintf(" (+%d more)", len(incomplete)-10)
		}
		lines = append(lines, fmt.Sprintf("- In progress / not started: %s%s", strings.Join(shown, ", "), more))
	}

	lines = append(lines, "", "**Data layers:**")
	if len(p.Inventory.DataLayers) == 0 {
		lines = append(lines, "- (none detected)")
	} else {
		var names []string
		for name := range p.Inventory.DataLayers {
			names = append(names, name)
		}
		sort.Strings(names)
		for _, name := range names {
			d := p.Inventory.DataLayers[name]
			lines = append(lines, fmt.Sprintf("- %s: %d files (%.2f MB)", name, d.FileCount, d.TotalSizeMB))
		}
	}

	lines = append(lines, "",
		fmt.Sprintf("**Scripts:** %d  |  **3D models:** %d  |  **Docs:** %d",
			len(p.Inventory.Scripts), len(p.Inventory.Models), len(p.Inventory.Docs)))

	return strings.Join(lines, "\n")
}

func parseUpdateEntries() []string {
	raw, err := os.ReadFile(updatesLogPath())
	if err != nil {
		return nil
	}
	chunks := strings.Split(string(raw), "\n### ")
	var entries []string
	for _, chunk := range chunks {
		chunk = strings.TrimSpace(chunk)
		if chunk == "" {
			continue
		}
		if !strings.HasPrefix(chunk, "### ") {
			chunk = "### " + chunk
		}
		entries = append(entries, chunk)
	}
	return entries
}

func buildUpdatesBlock() string {
	entries := parseUpdateEntries()
	if len(entries) == 0 {
		return "*No updates logged yet. Drop a small `.md` file into `inbox/` with \"update\" in the filename or heading — " +
			"just the new information, nothing you've already logged — and it'll be appended here automatically, newest at the top.*"
	}
	// reverse for newest-first
	newestFirst := make([]string, len(entries))
	for i, e := range entries {
		newestFirst[len(entries)-1-i] = e
	}
	shown := newestFirst
	remaining := 0
	if len(newestFirst) > maxUpdatesShown {
		shown = newestFirst[:maxUpdatesShown]
		remaining = len(newestFirst) - maxUpdatesShown
	}
	block := strings.Join(shown, "\n\n")
	if remaining > 0 {
		block += fmt.Sprintf("\n\n*(+%d older update(s) — full history in docs/handoff_archive/_updates_log.md)*", remaining)
	}
	return block
}

// buildNotesBlock writes the most recently adopted handoff doc's raw text
// directly, immediately -- no compression step. (An earlier version routed
// this through a local Ollama call first; that was removed entirely after
// it failed 100% of the time it was tested. Re-introducing compression is a
// separate future decision, not something to work around here.)
func buildNotesBlock() string {
	raw, err := os.ReadFile(latestRawPath())
	if err != nil {
		return "*No handoff document has been processed yet. Drop a handoff-style `.md` file into `inbox/` " +
			"(filename or heading containing \"handoff\" or \"session archive\") and it'll appear here.*"
	}
	return string(raw)
}

// regenerateHandoff mirrors generate_handoff.py's regenerate(), plus a
// version marker at the very top: an incrementing update counter and the
// real system date/time at the moment of regeneration (not estimated).
func regenerateHandoff() {
	if latestHandoffPath == "" {
		initHandoffPaths()
	}

	var packet *ccppPacket
	if p, err := loadCcpp(ccppFile); err == nil {
		packet = p
	} else {
		packet = scanProject()
		saveCcpp(packet, ccppFile)
	}

	autoBlock := buildAutoBlock(packet)
	updatesBlock := buildUpdatesBlock()
	notesBlock := buildNotesBlock()

	counter := nextUpdateCounter()
	versionMarker := fmt.Sprintf("# LATEST_HANDOFF.md — Update #%d — %s\n\n---\n\n", counter, time.Now().Format("2006-01-02 3:04 PM"))

	content := versionMarker +
		"# CITIZEN COMPASS — LATEST HANDOFF\n\n" +
		"Copy/paste this whole file into a new AI conversation for instant context. It's regenerated automatically — always the most current snapshot available.\n\n" +
		"---\n\n## CURRENT STATE (auto)\n\n" + autoBlock + "\n\n" +
		"---\n\n## RECENT UPDATES (append-only, newest first)\n\n" + updatesBlock + "\n\n" +
		"---\n\n## PROJECT NOTES (from most recent full handoff doc)\n\n" + notesBlock + "\n"

	if err := os.WriteFile(latestHandoffPath, []byte(content), 0644); err != nil {
		logMsg("could not write %s: %v", latestHandoffPath, err)
		return
	}
	logMsg("LATEST_HANDOFF.md regenerated (update #%d, %d chars)", counter, len(content))
}
