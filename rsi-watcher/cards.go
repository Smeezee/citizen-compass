package main

// cards.go - a new CIG item becomes one structured JSON card on its shelf under
// sc-brain/cig-firehose/, and a change becomes the wake marker. No summaries: v1
// has no model, so a card carries only what the source itself said.
//
// NEVER TWICE. A card whose file already exists is not rewritten - an id seen
// again (a state file lost, say) must not overwrite what was first recorded.

import (
	"encoding/json"
	"errors"
	"os"
	"path/filepath"
	"regexp"
	"strings"
)

// Card is one new item.
type Card struct {
	Source       string `json:"source"`
	ID           string `json:"id"`
	Title        string `json:"title"`
	URL          string `json:"url"`
	Time         string `json:"time"` // as the source wrote it
	FirstSeenUTC string `json:"first_seen_utc"`
	Trigger      string `json:"trigger"`
	Shelf        string `json:"-"`
}

// Wake is what a later session is woken with - only ever written on change.
type Wake struct {
	At      string `json:"at"`
	Trigger string `json:"trigger"`
	Items   []Card `json:"items"`
}

var reUnsafe = regexp.MustCompile(`[^A-Za-z0-9._-]`)

func fileNameFor(id string) string {
	n := reUnsafe.ReplaceAllString(id, "_")
	// No separators survive the line above; a LEADING dot is replaced too, so a
	// card is never a hidden file and never starts with "..".
	for strings.HasPrefix(n, ".") {
		n = "_" + n[1:]
	}
	if n == "" {
		n = "_"
	}
	return n + ".json"
}

// WriteCard -> (path, written). written is false when the card already existed.
func WriteCard(shelfRoot string, c Card) (string, bool, error) {
	dir := filepath.Join(shelfRoot, c.Shelf)
	if err := os.MkdirAll(dir, 0o755); err != nil {
		return "", false, err
	}
	path := filepath.Join(dir, fileNameFor(c.ID))
	if _, err := os.Stat(path); err == nil {
		return path, false, nil
	} else if !errors.Is(err, os.ErrNotExist) {
		return path, false, err
	}
	b, err := json.MarshalIndent(c, "", "  ")
	if err != nil {
		return path, false, err
	}
	tmp := path + ".tmp"
	if err := os.WriteFile(tmp, append(b, '\n'), 0o644); err != nil {
		return path, false, err
	}
	return path, true, os.Rename(tmp, path)
}

// WriteWake overwrites the marker. Called ONLY when something changed.
func WriteWake(path string, w Wake) error {
	if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		return err
	}
	b, err := json.MarshalIndent(w, "", "  ")
	if err != nil {
		return err
	}
	tmp := path + ".tmp"
	if err := os.WriteFile(tmp, append(b, '\n'), 0o644); err != nil {
		return err
	}
	return os.Rename(tmp, path)
}
