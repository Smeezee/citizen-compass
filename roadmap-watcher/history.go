package main

// history.go - what the card WAS, kept forever.
//
// ===========================================================================
// THE DEFECT THIS CLOSES
// ===========================================================================
//
// C3, 2026-08-16, docs/WORKORDER_historian-foundations-2026-08-16.md §1:
//
//     "The watcher records that something changed, then destroys what it was."
//
// `State.Fingerprints` holds ONE fingerprint per card. Diff compares the new
// value against it, reports the change, and writes the new value over the old.
// The previous fingerprint is gone. So the watcher can say a card changed and
// cannot say what it changed FROM, and cannot be asked anything about last
// month at all.
//
// The current-state map is untouched - the diff depends on it and it works.
// This ADDS an append-only record beside it: one line per matched card per
// run, never rewritten.
//
// ===========================================================================
// WHY THIS IS URGENT WHEN THE THING IT SERVES IS NOT
// ===========================================================================
//
// The value is entirely in elapsed time. A history started today is worth
// something in six months; one started in six months is worth nothing for a
// year. AND IT CANNOT BE BACKFILLED - not from CIG, not from anywhere. Every
// week of delay is a week permanently missing.
//
// It is also nearly free: a few hundred cards, six runs a day, one short line
// each. Kilobytes.
//
// ===========================================================================
// JSONL, NOT A TABLE - and the reason, since the order left the choice open
// ===========================================================================
//
// The order says "JSONL is fine. A table is better." A table is better where
// the writer already has a database. This one does not: the roadmap watcher is
// a standalone .exe on a desktop, started by Task Scheduler, whose whole job is
// to keep running unattended for years. Giving it a database dependency means
// it stops recording history on the day Postgres is down, moved, or upgraded -
// and the one property this file must have is that it NEVER stops recording.
//
// A JSONL file appended with O_APPEND has that property with no daemon, no
// driver and no credentials. It is also trivially importable into a table later
// by anything that wants to query it, which is the direction that costs
// nothing; the reverse is a migration.
//
// ===========================================================================
// THE SHAPE IS SHARED WITH THE MODEL FINGERPRINTS, DELIBERATELY
// ===========================================================================
//
// data-layer/derived/model-fingerprints/ has the same defect and gets the same
// treatment, with the same column names, so a later query can read both as one
// time series. That is the only design constraint the order imposes and it is
// worth more than either format choice.

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"time"
)

// historyFileName sits beside the state file. One writer: this program.
const historyFileName = "roadmap-watcher-history.jsonl"

// Observation is one card, as it stood on one run.
//
// EVERY ROW CARRIES ITS OWN CONTEXT. The same argument BaselineCard already
// makes: a record that does not say which board, which release and whether it
// had shipped gets misread by whoever finds it in a year. A time series of
// bare fingerprints would be unreadable exactly when it finally matters.
type Observation struct {
	At string `json:"at"`

	// KIND AND SUBJECT ARE THE COLUMNS THE MODEL FINGERPRINT LOG SHARES.
	//
	// The order's one design constraint is that the roadmap watcher and the
	// model fingerprints be recorded "the same way, so a later query can read
	// both as one time series". Boards and card ids mean nothing to a .glb, and
	// a vertex count means nothing to a roadmap card - so the shared spine is
	// these two plus at / name / fingerprint / source, and each side adds its
	// own fields after them.
	Kind    string `json:"kind"`    // "roadmap-card"
	Subject string `json:"subject"` // "b1/c9001" - stable across runs

	Board       int    `json:"board"`
	Surface     string `json:"surface"`
	CardID      int    `json:"card_id"`
	Name        string `json:"name"`
	Release     string `json:"release"`
	Released    bool   `json:"released"`
	Fingerprint string `json:"fingerprint"`
	Source      string `json:"source"`
}

// HistoryPath is where the log lives, beside the state it accompanies.
func HistoryPath(stateDir string) string {
	return filepath.Join(stateDir, historyFileName)
}

// AppendObservations writes one line per matched card. It never rewrites.
//
// OPENED O_APPEND, WHICH IS THE WHOLE GUARANTEE. Not "opened for writing and we
// are careful to seek to the end" - the kernel appends, so a second writer, a
// crash mid-run, or a bug in this file cannot truncate what is already there.
// There is no code path here that opens the file any other way, and that is the
// property to preserve if anything in this file is ever edited.
//
// Returns the number of rows written.
func AppendObservations(path string, res FetchResult, watch, source string,
	logf func(string, ...interface{})) (int, error) {

	matches := Matches(res.Cards, watch)
	if len(matches) == 0 {
		return 0, nil
	}
	now := time.Now().UTC().Format(time.RFC3339)

	f, err := os.OpenFile(path, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0o644)
	if err != nil {
		return 0, fmt.Errorf("cannot open the history log (%w) - this run's "+
			"observations are LOST and cannot be recovered later", err)
	}
	defer f.Close()

	n := 0
	for _, c := range matches {
		row := Observation{
			At:          now,
			Kind:        "roadmap-card",
			Subject:     cardKey(res.Board, c.ID),
			Board:       res.Board,
			Surface:     res.Surface,
			CardID:      c.ID,
			Name:        c.Name,
			Release:     c.Release,
			Released:    c.Released,
			Fingerprint: Fingerprint(c),
			Source:      source,
		}
		b, err := json.Marshal(row)
		if err != nil {
			// One unmarshallable card must not cost the other 200 rows.
			if logf != nil {
				logf("history: could not encode card %d (%v) - the other rows "+
					"in this run are still being written", c.ID, err)
			}
			continue
		}
		if _, err := f.Write(append(b, '\n')); err != nil {
			return n, fmt.Errorf("history write failed after %d row(s) (%w)", n, err)
		}
		n++
	}

	// SYNC, BECAUSE THIS IS THE COPY THAT CANNOT BE REBUILT.
	//
	// The state file can be regenerated by re-polling; a lost history row is
	// gone for good. A machine that loses power between runs should still have
	// yesterday's observations on disk.
	if err := f.Sync(); err != nil && logf != nil {
		logf("history: wrote %d row(s) but could not flush them to disk (%v)", n, err)
	}
	return n, nil
}

// ReadHistory loads every row. Used by the verifier and by anything that wants
// to ask a question about the past.
//
// A BAD LINE IS SKIPPED AND COUNTED, NEVER FATAL. This file is append-only and
// may be decades old; a single truncated line from a power cut must not make
// the entire archive unreadable. The count of skipped lines is returned so a
// caller can say so out loud rather than quietly returning less history than
// exists.
func ReadHistory(path string) ([]Observation, int, error) {
	b, err := os.ReadFile(path)
	if os.IsNotExist(err) {
		return nil, 0, nil
	}
	if err != nil {
		return nil, 0, err
	}
	var out []Observation
	bad := 0
	start := 0
	for i := 0; i <= len(b); i++ {
		if i == len(b) || b[i] == '\n' {
			line := b[start:i]
			start = i + 1
			if len(line) == 0 {
				continue
			}
			var o Observation
			if err := json.Unmarshal(line, &o); err != nil {
				bad++
				continue
			}
			out = append(out, o)
		}
	}
	return out, bad, nil
}
