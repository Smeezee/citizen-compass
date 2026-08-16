package main

// store.go - the stored record, and the fingerprint diff.
//
// SAME SHAPE AS data-layer/derived/model-fingerprints/, on purpose. The order
// says these are concrete integrations two and three of the same mechanism -
// snapshot a payload, store the fingerprint, diff next run - and that they must
// NOT be generalised into a shared pipeline yet. The standing rule is 2-3
// concrete integrations before abstracting.
//
// So: built plainly, but with the stored record deliberately the same shape, so
// generalising later is a refactor rather than a rewrite.

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"time"
)

// State is everything that survives between runs.
type State struct {
	Version int `json:"version"`

	// Baseline is the set of watched cards known at the time the baseline was
	// taken. A card outside this set is THE SIGNAL.
	//
	// IT IS DATA, NOT A NUMBER IN A COMMENT. The work order keys on "any card
	// beyond the one known card" - and there are THREE on Release View today:
	// RSI Constellation Phoenix, Merlin/Constellation Docking, and RSI
	// Constellation Taurus. A watcher built to "beyond the one" fires twice on
	// its first run, on cards that have sat there for years, and then gets
	// muted before the real signal ever arrives.
	Baseline map[string]BaselineCard `json:"baseline"`

	// Fingerprints is per-card, so an edit is localised to the card that moved
	// rather than reported as "the board changed".
	Fingerprints map[string]string `json:"fingerprints"`

	// BoardLastUpdated is the board-level timestamp, stored because it is a
	// real change signal at board scope. Not triggered on by itself - the
	// per-card hash is what says WHAT changed.
	BoardLastUpdated map[string]int64 `json:"board_last_updated"`

	LastRun   string `json:"last_run"`
	LastRunBy string `json:"last_run_by"`

	// THE TIME OF THE LAST SUCCESSFUL CHECK - success:1, parsed, diffed.
	// NOT the last attempt and NOT the last time the process was alive.
	//
	// A tripwire that died three weeks ago produces exactly the same output as
	// one that ran an hour ago and found nothing: silence. This project has
	// already been bitten twice - a supervisor that masked 42 crashes by
	// restarting all day, and checkers that reported success by never looking.
	// The lifecycle rule adopted after the second is the same principle: a
	// finding is CLOSED only by a run that LOOKED and did not find it.
	LastGood string `json:"last_good_run"`

	// The last successful SCHEDULED run, tracked separately so a hand-run
	// cannot paper over a dead timer. Without this a manual check says
	// "nothing new" while the scheduler has been down for a month - worse
	// than no answer, because it reads as reassurance.
	LastGoodScheduled string `json:"last_good_scheduled_run"`
}

// BaselineCard is the minimum needed to recognise a card again and to say
// something useful about it in an alert.
type BaselineCard struct {
	Board   int    `json:"board"`
	Surface string `json:"surface"`
	Name    string `json:"name"`

	// THE RELEASE CONTEXT, STORED. "Constellation" already appears 23 times on
	// Release View and every occurrence is historical. With these two fields a
	// record reads "RSI Constellation Taurus, Release View, release 3.14,
	// Released" and can never be misread as news by whoever finds it later.
	//
	// A record that does not carry its own context gets misread eventually.
	Release  string `json:"release"`
	Released bool   `json:"released"`

	FirstAt string `json:"first_seen"`
}

func newState() *State {
	return &State{
		Version:          1,
		Baseline:         map[string]BaselineCard{},
		Fingerprints:     map[string]string{},
		BoardLastUpdated: map[string]int64{},
	}
}

// cardKey identifies a card across runs.
//
// Board AND id: ids are only unique within a board, and this tool watches more
// than one board. Keying on id alone would let a Squadron 42 card silently
// shadow a Release View one.
func cardKey(board, id int) string { return fmt.Sprintf("b%d/c%d", board, id) }

// Fingerprint is the normalised hash of the fields worth noticing a change in.
//
// updateDate is DELIBERATELY EXCLUDED. The order found it reporting 2024 for a
// card the UI renders as 2021, and hashing it would make every alert
// unreproducible by looking at the page - the exact defect the order warns
// against, reintroduced through the back door.
func Fingerprint(c Card) string {
	h := sha256.New()
	fmt.Fprintf(h, "name=%s\x00desc=%s\x00release=%d\x00",
		strings.TrimSpace(c.Name), strings.TrimSpace(c.Description), c.ReleaseID)
	return hex.EncodeToString(h.Sum(nil))[:16]
}

// Change is one thing worth telling a human about.
type Change struct {
	Kind    string `json:"kind"` // "new-card" | "card-changed"
	Board   int    `json:"board"`
	Surface string `json:"surface"`
	Card    string `json:"card"`
	Detail  string `json:"detail"`
}

// Diff compares this poll against stored state and returns what moved.
//
// It MUTATES state, so a caller that does not save has still consumed the
// signal - which is why main saves before it reports.
func Diff(st *State, res FetchResult, watch string) []Change {
	var out []Change
	now := time.Now().UTC().Format(time.RFC3339)
	matches := Matches(res.Cards, watch)

	for _, c := range matches {
		key := cardKey(res.Board, c.ID)
		fp := Fingerprint(c)

		if _, known := st.Baseline[key]; !known {
			// THE SIGNAL, if a baseline already exists. On the very first run
			// every card is new, which is a baseline being taken rather than
			// news - main says which, because "3 new Constellation cards" on
			// day one would be a lie of framing.
			out = append(out, Change{
				Kind: "new-card", Board: res.Board, Surface: res.Surface,
				Card: c.Name,
				Detail: fmt.Sprintf("a card matching %q that was not here before",
					watch),
			})
			st.Baseline[key] = BaselineCard{
				Board: res.Board, Surface: res.Surface, Name: c.Name,
				Release: c.Release, Released: c.Released, FirstAt: now,
			}
		} else if old, ok := st.Fingerprints[key]; ok && old != fp {
			out = append(out, Change{
				Kind: "card-changed", Board: res.Board, Surface: res.Surface,
				Card:   c.Name,
				Detail: "the card's own fields changed (title, description or release)",
			})
		}
		st.Fingerprints[key] = fp
	}

	// A card that DISAPPEARS is worth knowing about too - it is how a card gets
	// replaced by a rework card under a new id.
	for key, b := range st.Baseline {
		if b.Board != res.Board {
			continue
		}
		found := false
		for _, c := range matches {
			if cardKey(res.Board, c.ID) == key {
				found = true
				break
			}
		}
		if !found {
			out = append(out, Change{
				Kind: "card-gone", Board: res.Board, Surface: res.Surface,
				Card:   b.Name,
				Detail: "was on this board and is not any more",
			})
			delete(st.Baseline, key)
			delete(st.Fingerprints, key)
		}
	}

	sort.Slice(out, func(i, j int) bool { return out[i].Card < out[j].Card })
	return out
}

// LoadState reads the store, or returns a fresh one on first run.
func LoadState(path string) (*State, bool, error) {
	b, err := os.ReadFile(path)
	if os.IsNotExist(err) {
		return newState(), true, nil
	}
	if err != nil {
		return nil, false, err
	}
	st := newState()
	if err := json.Unmarshal(b, st); err != nil {
		// FAIL CLOSED. A corrupt store must not silently become an empty one:
		// that would re-baseline against whatever is on the board today and
		// throw away the very history this tool exists to hold.
		return nil, false, fmt.Errorf("%s exists but is not readable as state "+
			"(%w). Refusing to start over and lose the baseline - move it aside "+
			"deliberately if that is what you want", filepath.Base(path), err)
	}
	if st.Baseline == nil {
		st.Baseline = map[string]BaselineCard{}
	}
	if st.Fingerprints == nil {
		st.Fingerprints = map[string]string{}
	}
	if st.BoardLastUpdated == nil {
		st.BoardLastUpdated = map[string]int64{}
	}
	return st, false, nil
}

// SaveState writes atomically - a half-written state file on a crash would be
// indistinguishable from a corrupt one, and LoadState refuses those.
func SaveState(path string, st *State) error {
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
