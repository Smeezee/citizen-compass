package main

// state.go - what this machine has already seen, in sc-brain/plumbing/state/.
//
// A BASELINE IS PER SOURCE. The first successful poll of a source records every
// id it returns as already known and reports none of them as news - so a feed
// configured next month (when Research's endpoint lands) arrives as a baseline,
// not as twenty "new" posts that are years old.

import (
	"encoding/json"
	"errors"
	"os"
	"path/filepath"
)

const maxKnown = 5000

// SourceState is one feed's memory.
type SourceState struct {
	Known      []string `json:"known_ids"`
	LastOK     string   `json:"last_ok"`
	LastError  string   `json:"last_error"`
	NewestID   string   `json:"newest_id"`
	NewestTime string   `json:"newest_time"`
	// NewestTimeSince: when THIS exact newest id + time string was first seen.
	// A relative age ("51 minutes ago") that has not moved in hours is a stuck
	// page - the old watcher's first sign it had gone blind.
	NewestTimeSince string `json:"newest_time_since"`
}

// State is the whole memory.
type State struct {
	Sources           map[string]*SourceState `json:"sources"`
	Live              string                  `json:"live"`
	PTU               string                  `json:"ptu"`
	BuildSince        string                  `json:"build_since"`
	LastRun           string                  `json:"last_run"`
	LastRunBy         string                  `json:"last_run_by"`
	LastGood          string                  `json:"last_good"`
	LastGoodScheduled string                  `json:"last_good_scheduled"`
}

func (st *State) source(name string) *SourceState {
	if st.Sources == nil {
		st.Sources = map[string]*SourceState{}
	}
	s := st.Sources[name]
	if s == nil {
		s = &SourceState{}
		st.Sources[name] = s
	}
	return s
}

func (s *SourceState) known(id string) bool {
	for _, k := range s.Known {
		if k == id {
			return true
		}
	}
	return false
}

func (s *SourceState) remember(id string) {
	s.Known = append(s.Known, id)
	if len(s.Known) > maxKnown {
		s.Known = s.Known[len(s.Known)-maxKnown:]
	}
}

// LoadState -> (state, first-ever run, error). An unreadable file is an error:
// silently starting from nothing would re-baseline and hide real news.
func LoadState(path string) (*State, bool, error) {
	b, err := os.ReadFile(path)
	if errors.Is(err, os.ErrNotExist) {
		return &State{Sources: map[string]*SourceState{}}, true, nil
	}
	if err != nil {
		return nil, false, err
	}
	var st State
	if err := json.Unmarshal(b, &st); err != nil {
		return nil, false, err
	}
	if st.Sources == nil {
		st.Sources = map[string]*SourceState{}
	}
	return &st, false, nil
}

// SaveState writes through a temp file so a crash never leaves half a state.
func SaveState(path string, st *State) error {
	if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		return err
	}
	b, err := json.MarshalIndent(st, "", "  ")
	if err != nil {
		return err
	}
	tmp := path + ".tmp"
	if err := os.WriteFile(tmp, append(b, '\n'), 0o644); err != nil {
		return err
	}
	return os.Rename(tmp, path)
}
