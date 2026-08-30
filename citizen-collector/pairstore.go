//go:build master

// MASTER BUILD ONLY - Sleven's ruling, 2026-08-30.
//
// The learning half does not ship to crew. Not compiled-and-disabled: ABSENT.
// variant_crew.go states the principle for calibration, zone tuning, the review
// pen and the package generator, and it applies here for the same reason - a
// feature that is compiled out cannot be found by a curious crew member, and a
// pairs/ folder that cannot be written cannot be wondered about.
//
// Everything shared stays shared. This forks nothing: capture, logging, the
// send path and the scrub layer remain one implementation each.

package main

// pairstore.go - the game labels its own objects; record that, and nothing else.
//
// Q45 first slice, 2026-08-30. Sleven's insight: the game already draws an
// object AND names it in the same frame - inventory, item inspect, a ground
// prompt, a HUD target, a shop kiosk. Every one of those is a labelled example
// the player generates by playing, and nobody annotates anything.
//
// # WHAT THIS IS NOT
//
// It does not recognise, classify, match, or decide anything. No model, no
// vocabulary, no OCR of its own. It RECORDS what the game put on screen next to
// itself. Anything resembling inference in this file is out of scope and
// belongs to a later item.
//
// It also adds no capture trigger, no hotkey and no send path. The store is fed
// through StorePair by a caller; today the only caller is the selftest, and
// that is deliberate.
//
// # THE INVERSION, WHICH IS THE WHOLE PRIVACY DESIGN OF THIS SLICE
//
// scrub_policy.go's real contribution is not its code - it governs the FIELDS
// of MineStore, a struct built from the game log, and has no view of a pixel.
// Its contribution is a SHAPE: a field with no policy is not exported, and the
// export says so out loud.
//
// This store inverts the same way. A pair is recorded ONLY when it comes from a
// screen context on the list below. An unlisted context is not recorded, and
// the store says which one it refused. The default is refusal, so a context
// nobody has thought about yet cannot leak in by being unanticipated - which is
// the failure mode a blocklist has and an allowlist does not.
//
// # WHAT THE PRIVACY GUARANTEE ACTUALLY RESTS ON
//
// Every picture this program takes is taken by a KEY PRESS.
// no_auto_capture_selftest.go drives the real loop with a log containing every
// trigger that ever fired a capture, requires ZERO pictures, then presses a key
// and requires one - so the negative control cannot rot. The player chooses the
// moment. That is the guarantee.
//
// THE CHAT-REGION EXCLUSION DOES NOT EXIST, anywhere in this program, and this
// file does not pretend otherwise or build one. It was described as a shipped
// precondition and is not; see the correction in NEXT.md's Q45. What this file
// does instead is narrower and real: it never records from a context that has
// not been named.
//
// pairs/ IS LOCAL. It is not on the send path, and it is excluded from the crew
// package in package.go beside "captures". Sending a new kind of thing would
// change what the consent text promises, and that text is Sleven's.
//
// Rule 15's Go equivalent: every file this opens is opened explicitly, and the
// index is opened O_APPEND so a second writer cannot truncate the first.

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"sync"
	"time"
)

// PairContext is the screen a pair was read from. It is a closed set on
// purpose: see the inversion note above.
type PairContext string

const (
	CtxInventory   PairContext = "inventory"
	CtxItemInspect PairContext = "item_inspect"
	CtxGroundPmt   PairContext = "ground_prompt"
	CtxHUDTarget   PairContext = "hud_target"
	CtxShopKiosk   PairContext = "shop_kiosk"
)

// pairContextAllowed is the allowlist, with each entry's reason written down -
// the same convention packageExcluded uses, and for the same reason: the list
// is where somebody will look when they want to know why.
var pairContextAllowed = map[PairContext]string{
	CtxInventory:   "the object is drawn AND named in one frame",
	CtxItemInspect: "the object, rotatable, with its name beside it",
	CtxGroundPmt:   "the interaction prompt names the thing being looked at",
	CtxHUDTarget:   "a ship's name while the ship is on screen",
	CtxShopKiosk:   "a priced item drawn beside its own label",
}

// PairView is one sighting. A pair seen twice is one entry with two views.
type PairView struct {
	At     string `json:"at"`
	Build  string `json:"build,omitempty"`
	Image  string `json:"image"` // sha256 of the region bytes, hex
	Bytes  int    `json:"bytes"`
	Width  int    `json:"w,omitempty"`
	Height int    `json:"h,omitempty"`
}

// PairEntry is one (label, context) fact with every view of it recorded.
//
// The IMAGE IS NOT PART OF IDENTITY. The same helmet photographed twice is one
// entry with two views; two different helmets sharing a name are still one
// entry, and that is correct - the label is what the game asserted, and a later
// recogniser wants every view it can get of the thing that carries that label.
type PairEntry struct {
	Key     string     `json:"key"`
	Label   string     `json:"label"`
	Context string     `json:"context"`
	First   string     `json:"first_seen"`
	Views   []PairView `json:"views"`
}

// PairRefusal records a pair that was NOT stored, and why. It is written to the
// index like anything else: a refusal nobody can count is indistinguishable
// from a pair nobody offered.
type PairRefusal struct {
	At      string `json:"at"`
	Context string `json:"context"`
	Reason  string `json:"reason"`
	Refused bool   `json:"refused"`
}

// PairStore appends to pairs/ and never rewrites it.
type PairStore struct {
	mu    sync.Mutex
	dir   string
	index string
	blobs string
}

// NewPairStore prepares pairs/ beside the other collector output. It creates
// nothing it does not need and destroys nothing that is there.
func NewPairStore(root string) (*PairStore, error) {
	dir := filepath.Join(root, "pairs")
	blobs := filepath.Join(dir, "views")
	if err := os.MkdirAll(blobs, 0o755); err != nil {
		return nil, fmt.Errorf("pairs directory: %w", err)
	}
	return &PairStore{
		dir:   dir,
		index: filepath.Join(dir, "pairs.jsonl"),
		blobs: blobs,
	}, nil
}

func pairKey(label string, ctx PairContext) string {
	sum := sha256.Sum256([]byte(string(ctx) + "\x00" + label))
	return hex.EncodeToString(sum[:8])
}

// ContextAllowed reports whether a context may be recorded, and why not when it
// may not. Exported so a caller can ask BEFORE it goes to the trouble of
// cutting a region out of a frame.
func ContextAllowed(ctx PairContext) (bool, string) {
	if _, ok := pairContextAllowed[ctx]; ok {
		return true, ""
	}
	names := make([]string, 0, len(pairContextAllowed))
	for k := range pairContextAllowed {
		names = append(names, string(k))
	}
	sort.Strings(names)
	return false, fmt.Sprintf("context %q is not on the recorded list (%s)",
		string(ctx), strings.Join(names, ", "))
}

// StorePair records one pair, or refuses it and says which context it refused.
//
// Returns (stored, key, err). stored=false with err=nil is a REFUSAL, which is
// a normal outcome and not a failure: an unlisted context is exactly what this
// is built to decline.
func (ps *PairStore) StorePair(label string, ctx PairContext, region []byte,
	w, h int, build string, at time.Time) (bool, string, error) {

	if ps == nil {
		return false, "", fmt.Errorf("no pair store")
	}
	ps.mu.Lock()
	defer ps.mu.Unlock()

	if ok, why := ContextAllowed(ctx); !ok {
		// THE REFUSAL IS RECORDED. Silence would make "nothing was on screen"
		// and "something was refused" the same observation, and the second is
		// the one that tells you what to teach next.
		return false, "", ps.appendLine(PairRefusal{
			At:      at.UTC().Format(time.RFC3339),
			Context: string(ctx),
			Reason:  why,
			Refused: true,
		})
	}
	if strings.TrimSpace(label) == "" {
		return false, "", ps.appendLine(PairRefusal{
			At:      at.UTC().Format(time.RFC3339),
			Context: string(ctx),
			Reason:  "empty label - a pair with no text is not a pair",
			Refused: true,
		})
	}
	if len(region) == 0 {
		return false, "", ps.appendLine(PairRefusal{
			At:      at.UTC().Format(time.RFC3339),
			Context: string(ctx),
			Reason:  "empty region - a pair with no view is not a pair",
			Refused: true,
		})
	}

	sum := sha256.Sum256(region)
	imgHash := hex.EncodeToString(sum[:])
	blob := filepath.Join(ps.blobs, imgHash+".bin")
	if _, err := os.Stat(blob); os.IsNotExist(err) {
		// Written once, by content hash. The same region seen again is the same
		// file, so a second view costs an index line and no bytes.
		if err := os.WriteFile(blob, region, 0o644); err != nil {
			return false, "", fmt.Errorf("pair view: %w", err)
		}
	}

	key := pairKey(label, ctx)
	view := PairView{
		At: at.UTC().Format(time.RFC3339), Build: build,
		Image: imgHash, Bytes: len(region), Width: w, Height: h,
	}

	existing, err := ps.load()
	if err != nil {
		return false, "", err
	}
	if e, ok := existing[key]; ok {
		for _, v := range e.Views {
			if v.Image == imgHash {
				// Same label, same context, same bytes: already recorded. Not
				// an error and not a second view.
				return true, key, nil
			}
		}
		e.Views = append(e.Views, view)
		return true, key, ps.appendLine(e)
	}
	return true, key, ps.appendLine(PairEntry{
		Key: key, Label: label, Context: string(ctx),
		First: view.At, Views: []PairView{view},
	})
}

// appendLine is the ONLY writer of the index, and it only ever appends.
//
// O_APPEND rather than seek-to-end: two processes appending to the same file
// with O_APPEND interleave whole writes, where seek-and-write silently
// overwrites. This store is meant to survive a crash mid-session, so the
// cheaper call is not the right one.
func (ps *PairStore) appendLine(v interface{}) error {
	b, err := json.Marshal(v)
	if err != nil {
		return err
	}
	f, err := os.OpenFile(ps.index, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0o644)
	if err != nil {
		return err
	}
	defer f.Close()
	_, err = f.Write(append(b, '\n'))
	return err
}

// load folds the append-only log into current state: last line for a key wins.
//
// A TRUNCATED FINAL LINE IS SURVIVED, NOT FATAL. A crash mid-write leaves a
// partial line; refusing to read the file because of it would lose every pair
// before it, which is the opposite of what an append-only store is for.
func (ps *PairStore) load() (map[string]PairEntry, error) {
	out := map[string]PairEntry{}
	raw, err := os.ReadFile(ps.index)
	if os.IsNotExist(err) {
		return out, nil
	}
	if err != nil {
		return nil, err
	}
	for _, line := range strings.Split(string(raw), "\n") {
		line = strings.TrimSpace(line)
		if line == "" {
			continue
		}
		var probe struct {
			Refused bool   `json:"refused"`
			Key     string `json:"key"`
		}
		if json.Unmarshal([]byte(line), &probe) != nil {
			continue // partial or corrupt line; the rest of the log still counts
		}
		if probe.Refused || probe.Key == "" {
			continue // refusals are recorded, not folded into state
		}
		var e PairEntry
		if json.Unmarshal([]byte(line), &e) != nil {
			continue
		}
		out[e.Key] = e
	}
	return out, nil
}

// Entries returns the folded state, sorted, for anything that wants to read the
// store without knowing its file format.
func (ps *PairStore) Entries() ([]PairEntry, error) {
	ps.mu.Lock()
	defer ps.mu.Unlock()
	m, err := ps.load()
	if err != nil {
		return nil, err
	}
	keys := make([]string, 0, len(m))
	for k := range m {
		keys = append(keys, k)
	}
	sort.Strings(keys)
	out := make([]PairEntry, 0, len(keys))
	for _, k := range keys {
		out = append(out, m[k])
	}
	return out, nil
}

// Refusals counts what was declined, by context. What the store would not
// record is as much a part of its report as what it did.
func (ps *PairStore) Refusals() (map[string]int, error) {
	ps.mu.Lock()
	defer ps.mu.Unlock()
	out := map[string]int{}
	raw, err := os.ReadFile(ps.index)
	if os.IsNotExist(err) {
		return out, nil
	}
	if err != nil {
		return nil, err
	}
	for _, line := range strings.Split(string(raw), "\n") {
		if strings.TrimSpace(line) == "" {
			continue
		}
		var r PairRefusal
		if json.Unmarshal([]byte(line), &r) != nil || !r.Refused {
			continue
		}
		out[r.Context]++
	}
	return out, nil
}
