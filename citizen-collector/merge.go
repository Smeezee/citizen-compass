package main

// merge.go - turn N people's exports into one dataset.
//
// # WHY THIS IS NOT OPTIONAL
//
// Shipping the collector to Sleven's wife and his friend produces a pile of
// zips. Without this, that is all it produces: three files nobody can ask a
// question of. The merge is the step where contribution turns into data.
//
// # THE THING THIS EXISTS TO MEASURE
//
// Three exports report Copper at 1,000 aUEC at Levski. That is either three
// people agreeing - which is the single most valuable signal a crowd-sourced
// price set can carry - or one person's log counted three times.
//
// The install id decides it, which is why it was built before anything shipped.
// Merging counts DISTINCT CONTRIBUTORS per fact, never rows. A person who
// exports the same session five times still counts once.
//
// # DISAGREEMENT IS DATA, NOT AN ERROR
//
// When two contributors report different prices for the same item at the same
// shop, the merge does NOT pick a winner, average them, or take the newest.
// It records both, with who saw what and on which build, and flags it.
//
// That is this project's standing auditor rule - flag, never auto-fix - and it
// is right here for a specific reason: a price that changed between patches and
// a price somebody misread produce identical-looking disagreement, and the
// merge cannot tell them apart. Something that cannot tell them apart must not
// choose between them.

import (
	"archive/zip"
	"encoding/json"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"sort"
	"strings"
)

// Observation is one fact and everyone who saw it.
type Observation struct {
	Value        string   `json:"value"`
	Contributors []string `json:"contributors"`  // install ids, sorted
	Sightings    int      `json:"sightings"`     // total rows, may exceed contributors
	Builds       []string `json:"builds"`        // game builds it was seen on
	FirstSeen    string   `json:"first_seen"`
	LastSeen     string   `json:"last_seen"`
}

// Confidence is the honest summary: how many INDEPENDENT people saw this.
func (o Observation) Confidence() int { return len(o.Contributors) }

// PriceDisagreement is two contributors reporting different numbers for the
// same thing in the same place.
type PriceDisagreement struct {
	Shop   string        `json:"shop"`
	Item   string        `json:"item"`
	Values []Observation `json:"values"`
	Note   string        `json:"note"`
}

// MergedStore is what the merge produces.
type MergedStore struct {
	SchemaVersion int      `json:"schema_version"`
	Generated     string   `json:"generated"`
	Sources       []string `json:"sources"`
	Contributors  []string `json:"contributors"`
	SchemasSeen   []int    `json:"source_schema_versions"`

	Prices        map[string]*Observation `json:"prices"`
	Locations     map[string]*Observation `json:"locations"`
	Ships         map[string]*Observation `json:"ship_classes"`
	Equipment     map[string]*Observation `json:"equipment_seen"`
	Deaths        map[string]*Observation `json:"deaths"`
	Disagreements []PriceDisagreement     `json:"price_disagreements"`

	// Coverage is what nobody has contributed yet: subsystems every source
	// listed as a gap. A merged to-do list, ranked by distinct shapes.
	Coverage []SubsystemGap `json:"still_unread_by_everyone"`

	Warnings []string `json:"warnings"`
}

func newMergedStore() *MergedStore {
	return &MergedStore{
		SchemaVersion: MineSchemaVersion,
		Prices:        map[string]*Observation{},
		Locations:     map[string]*Observation{},
		Ships:         map[string]*Observation{},
		Equipment:     map[string]*Observation{},
		Deaths:        map[string]*Observation{},
	}
}

func (m *MergedStore) note(set map[string]*Observation, key, value, who, build, ts string, n int) {
	o := set[key]
	if o == nil {
		o = &Observation{Value: value, FirstSeen: ts, LastSeen: ts}
		set[key] = o
	}
	o.Sightings += n
	if who != "" && !containsStr(o.Contributors, who) {
		o.Contributors = append(o.Contributors, who)
		sort.Strings(o.Contributors)
	}
	if build != "" && !containsStr(o.Builds, build) {
		o.Builds = append(o.Builds, build)
		sort.Strings(o.Builds)
	}
	if ts != "" {
		if o.FirstSeen == "" || ts < o.FirstSeen {
			o.FirstSeen = ts
		}
		if ts > o.LastSeen {
			o.LastSeen = ts
		}
	}
}

func containsStr(xs []string, v string) bool {
	for _, x := range xs {
		if x == v {
			return true
		}
	}
	return false
}

// MergeExports reads every export or dataset in paths and folds them together.
//
// Accepts either a .zip written by BuildExport or a bare gamelog-dataset.json,
// because somebody will hand over one of each and being strict about it helps
// nobody.
func MergeExports(paths []string, logf func(string, ...interface{})) (*MergedStore, error) {
	if logf == nil {
		logf = func(string, ...interface{}) {}
	}
	m := newMergedStore()
	seenInstall := map[string]int{}

	for _, p := range paths {
		st, err := readDataset(p)
		if err != nil {
			m.Warnings = append(m.Warnings,
				fmt.Sprintf("%s could not be read: %v", filepath.Base(p), err))
			logf("merge: SKIPPED %s - %v", filepath.Base(p), err)
			continue
		}
		m.Sources = append(m.Sources, filepath.Base(p))

		// A NEWER schema is not merged blind. Unknown fields would be silently
		// dropped and the result would look complete - the same failure the
		// dataset loader refuses on a single machine, and worse here because
		// the loss would be somebody else's contribution.
		if st.SchemaVersion > MineSchemaVersion {
			m.Warnings = append(m.Warnings, fmt.Sprintf(
				"%s is schema v%d, this tool understands v%d - NOT MERGED",
				filepath.Base(p), st.SchemaVersion, MineSchemaVersion))
			logf("merge: REFUSED %s - written by a newer collector", filepath.Base(p))
			continue
		}
		if !containsInt(m.SchemasSeen, st.SchemaVersion) {
			m.SchemasSeen = append(m.SchemasSeen, st.SchemaVersion)
		}

		who := st.InstallID
		if who == "" {
			// An export with no id cannot be told apart from any other. Counting
			// it as a contributor would inflate every confidence number in the
			// file, so it contributes facts but not corroboration, and says so.
			m.Warnings = append(m.Warnings, fmt.Sprintf(
				"%s carries no contributor id - its rows are included but count "+
					"toward nobody's agreement", filepath.Base(p)))
		} else {
			seenInstall[who]++
			if !containsStr(m.Contributors, who) {
				m.Contributors = append(m.Contributors, who)
			}
			if seenInstall[who] > 1 {
				logf("merge: %s is the %d%s export from the same install - its rows "+
					"still count once toward agreement",
					filepath.Base(p), seenInstall[who], ordinal(seenInstall[who]))
			}
		}

		for _, t := range st.Txns {
			key := t.Shop + "|" + t.Item
			m.note(m.Prices, key+"|"+t.Price, t.Price, who, t.Build, t.TS, 1)
		}
		for k, n := range st.Locations {
			m.note(m.Locations, k, k, who, "", st.Generated, n)
		}
		for k, n := range st.Ships {
			m.note(m.Ships, k, k, who, "", st.Generated, n)
		}
		for k, n := range st.Equipment {
			m.note(m.Equipment, k, k, who, "", st.Generated, n)
		}
		for k, n := range st.Deaths {
			m.note(m.Deaths, k, k, who, "", st.Generated, n)
		}
		m.Coverage = mergeGaps(m.Coverage, st.Uncovered)
	}

	sort.Strings(m.Contributors)
	sort.Ints(m.SchemasSeen)
	m.Disagreements = findDisagreements(m.Prices)
	return m, nil
}

// findDisagreements groups price observations by shop+item and reports any that
// carry more than one value.
func findDisagreements(prices map[string]*Observation) []PriceDisagreement {
	byThing := map[string][]*Observation{}
	for key, o := range prices {
		parts := strings.Split(key, "|")
		if len(parts) < 3 {
			continue
		}
		byThing[parts[0]+"|"+parts[1]] = append(byThing[parts[0]+"|"+parts[1]], o)
	}
	var out []PriceDisagreement
	for thing, obs := range byThing {
		if len(obs) < 2 {
			continue
		}
		parts := strings.SplitN(thing, "|", 2)
		d := PriceDisagreement{Shop: parts[0], Item: parts[1]}
		for _, o := range obs {
			d.Values = append(d.Values, *o)
		}
		sort.Slice(d.Values, func(i, j int) bool {
			return d.Values[i].Confidence() > d.Values[j].Confidence()
		})
		// NO WINNER IS CHOSEN. A patch change and a misread look identical here.
		d.Note = "prices differ. This is NOT resolved automatically - a price that " +
			"changed between builds and a price recorded wrong are indistinguishable " +
			"from inside this file. Compare the builds column."
		out = append(out, d)
	}
	sort.Slice(out, func(i, j int) bool {
		if out[i].Shop != out[j].Shop {
			return out[i].Shop < out[j].Shop
		}
		return out[i].Item < out[j].Item
	})
	return out
}

func mergeGaps(into, add []SubsystemGap) []SubsystemGap {
	idx := map[string]int{}
	for i, g := range into {
		idx[g.Subsystem] = i
	}
	for _, g := range add {
		if i, ok := idx[g.Subsystem]; ok {
			into[i].Lines += g.Lines
			if g.Shapes > into[i].Shapes {
				into[i].Shapes = g.Shapes
			}
			continue
		}
		idx[g.Subsystem] = len(into)
		into = append(into, g)
	}
	sort.Slice(into, func(i, j int) bool {
		if into[i].Shapes != into[j].Shapes {
			return into[i].Shapes > into[j].Shapes
		}
		return into[i].Subsystem < into[j].Subsystem
	})
	return into
}

func containsInt(xs []int, v int) bool {
	for _, x := range xs {
		if x == v {
			return true
		}
	}
	return false
}

func ordinal(n int) string {
	switch {
	case n%100 >= 11 && n%100 <= 13:
		return "th"
	case n%10 == 1:
		return "st"
	case n%10 == 2:
		return "nd"
	case n%10 == 3:
		return "rd"
	}
	return "th"
}

// readDataset accepts a BuildExport zip or a bare dataset json.
// errRawDataset means somebody pointed the merge at an UNSCRUBBED local store.
//
// Review 2026-08-08 caught this as a second, undefended door. scrub.go argues
// carefully that raw names stay local and only pseudonyms leave - and then
// readDataset happily accepted a bare "gamelog-dataset.json", which is exactly
// the filename of the raw local store. The obvious thing to do when merging is
// to drop your own dataset in beside the contributors' zips, and doing so put
// real handles into merged-dataset.json, which feeds the public site.
//
// A .zip written by BuildExport has already been through ScrubForExport. A bare
// dataset has not, and nothing in the file says which it is. So bare datasets
// are refused by name, and the message says what to do instead.
var errRawDataset = fmt.Errorf("this is an unscrubbed local dataset, not an export")

func readDataset(p string) (*MineStore, error) {
	if strings.EqualFold(filepath.Base(p), "gamelog-dataset.json") {
		return nil, fmt.Errorf("%w: gamelog-dataset.json is the RAW local store and "+
			"still contains real player names. Press SEND MY DATA to produce an "+
			"export zip and merge that instead", errRawDataset)
	}
	if strings.EqualFold(filepath.Ext(p), ".zip") {
		zr, err := zip.OpenReader(p)
		if err != nil {
			return nil, err
		}
		defer zr.Close()
		for _, f := range zr.File {
			if filepath.Base(f.Name) != "gamelog-dataset.json" {
				continue
			}
			rc, err := f.Open()
			if err != nil {
				return nil, err
			}
			defer rc.Close()
			b, err := io.ReadAll(rc)
			if err != nil {
				return nil, err
			}
			return unmarshalDataset(b)
		}
		return nil, fmt.Errorf("no gamelog-dataset.json inside the zip")
	}
	b, err := os.ReadFile(p)
	if err != nil {
		return nil, err
	}
	return unmarshalDataset(b)
}

func unmarshalDataset(b []byte) (*MineStore, error) {
	st := newMineStore()
	st.SchemaVersion = 0 // absence means v1 - same rule as loadMineStore
	if err := json.Unmarshal(b, st); err != nil {
		return nil, err
	}
	if st.SchemaVersion == 0 {
		st.SchemaVersion = 1
	}
	return st, nil
}

// SaveMerged writes the merged dataset.
func SaveMerged(m *MergedStore, path string) error {
	b, err := json.MarshalIndent(m, "", "  ")
	if err != nil {
		return err
	}
	tmp := path + ".tmp"
	if err := os.WriteFile(tmp, b, 0o644); err != nil {
		return err
	}
	return os.Rename(tmp, path)
}

func jsonMarshalIndent(v interface{}) ([]byte, error) { return json.MarshalIndent(v, "", "  ") }
