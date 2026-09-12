package main

// boot_poller.go - the Echo poller's line on BOOT.md. Architecture's ruling,
// 2026-09-12 (memo_build_the-beat-is-ruled-the-matchup-gets-labelled-and-apply-the-diff).
//
// On 2026-09-12 nothing said the poller had stopped. Its ledger's empty `refused`
// read exactly the same for "nothing to refuse" and "never ran", and it had not
// run for three hours. scripts/desk.py now records every run, whatever happened,
// in logs/desk_fetch_runs.json, and this line prints the last one:
//
//	no file                 MISSING - no fetch run is recorded
//	a file with no run      NOT FOUND
//	a run                   when, how it ended, why if it failed, how long ago
//	three ticks with none   STALE - so a stopped beat is on the page, not hidden

import (
	"fmt"
	"time"
)

const pollerRunsRel = "logs/desk_fetch_runs.json"

// pollerStaleAfter is three missed ticks. One late tick is noise; three is a stop.
const pollerStaleAfter = 3 * tickInterval

func bootPollerLine(root string, now time.Time) string {
	runs, why := bootJSON(root, pollerRunsRel)
	if runs == nil {
		return "    echo poller    " + why + " - " + pollerRunsRel + " (no fetch run is recorded)"
	}
	last, ok := runs["last"].(map[string]interface{})
	if !ok {
		return "    echo poller    NOT FOUND - no \"last\" run in " + pollerRunsRel
	}
	at, outcome := jStr(last, "attempted_at"), jStr(last, "outcome")
	if outcome == "" {
		outcome = "NO OUTCOME RECORDED"
	}
	line := fmt.Sprintf("    echo poller    last run %s, %s", at, outcome)
	if outcome == "ok" {
		line += fmt.Sprintf(" - read %s, filed %d, refused %d", jStr(last, "read"), jLen(last, "filed"), jLen(last, "refused"))
	}
	if r := jStr(last, "reason"); r != "" {
		line += " - " + bootClip(r, 80)
	}
	t, err := time.Parse(time.RFC3339, at)
	if err != nil {
		return line + "  [attempted_at UNREADABLE]  (" + pollerRunsRel + ")"
	}
	if age := bootAge(now, t); age == "just now" {
		line += " (just now)"
	} else {
		line += " (" + age + " ago)"
	}
	if now.Sub(t) > pollerStaleAfter {
		line += fmt.Sprintf("  STALE - the beat runs every %d min", int(tickInterval.Minutes()))
	}
	return line + "  (" + pollerRunsRel + ")"
}
