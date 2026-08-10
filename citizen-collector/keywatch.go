package main

// keywatch.go - capture when the PLAYER does something, not when a clock says so.
//
// # THE PROBLEM WITH EVERY TRIGGER BUILT SO FAR
//
// Log events fire when the game writes a line. That covers a lot - shops,
// transactions, spawns, deaths - but the game does not write a line for most of
// what a player actually does. Sleven's own example: a mining ping. You press a
// key, numbers appear on screen for a few seconds, they are gone. Nothing in
// Game.log mentions it. Every name it could plausibly use was checked -
// Ping, ScanningComponent, RadarSignature, SignatureDetection, ResourceEntity,
// Deposit - and all six return zero across 227 sessions.
//
// So a whole class of information is invisible to text and lasts three seconds.
// A sixty-second timer will not catch it. A log trigger cannot know about it.
//
// # WATCHING KEYS THE PLAYER ALREADY PRESSES
//
// The collector already polls the keyboard for its own hotkey, and that path is
// now proven working in a live session - "hotkey press received (Alt+F3, via
// polling)". This is the same mechanism pointed at the keys the player uses to
// play: scan, ping, mining laser, salvage beam, whatever they name.
//
// It reads ONLY whether a key is currently down. It does not intercept, does
// not consume, does not send. The game receives every press exactly as it would
// have. That matters because "no synthetic input, no injection" is a standing
// rule, and because a tool that ate a keypress in a dogfight would be
// uninstalled the same day.
//
// # BIT 0x8000 ONLY, AND NEVER 0x0001
//
// GetAsyncKeyState's low bit means "pressed since somebody last asked", and it
// is CLEARED BY WHOEVER ASKS FIRST - process-wide. Reading it would race the
// game for the player's own keypresses. keyIsDown reads only 0x8000, the
// down-right-now bit, which is a question with no side effects.

import (
	"fmt"
	"strings"
	"time"
)

// watchedKey is one key the player told us to watch, and what it means to them.
//
// # EDGE KEYS AND HELD KEYS ARE DIFFERENT ANIMALS
//
// A scan ping is an EVENT. You tap it, something appears, it is gone. One frame
// at the moment of the tap is exactly right.
//
// A mining laser is an ACTIVITY. Sleven: "what if I'm holding a button down for
// longer than three seconds... I'm trying to capture actual salvaging
// operations or mining operations or even dogfighting when they pull the
// trigger and the guns are shooting, there's information going on the screen."
//
// He is right, and edge detection is the worst possible answer for that case:
// hold the trigger for thirty seconds of changing readouts and you get ONE
// frame, taken at the instant before anything happened.
//
// So a held key keeps shooting on a rhythm for as long as it is down, and stops
// the moment it is released. Same shape as the shop-terminal burst, driven by a
// finger instead of a log line.
type watchedKey struct {
	Spec  string // as written in settings, e.g. "alt+m"
	Label string // what the player called it, e.g. "mining laser"

	// Hold turns this from "one frame per press" into "keep going while down".
	Hold bool

	mods   uint32
	vk     uint32
	need   [][]uint32
	wasDwn bool

	// held-mode state
	lastShot time.Time
	frames   int
}

// KeyWatcher polls a set of keys and reports edges and holds.
type KeyWatcher struct {
	keys []*watchedKey
	last map[string]time.Time

	// HoldSeconds is the rhythm while a key is down. MaxHoldFrames is the
	// ceiling per continuous hold - the one stop condition that cannot fail,
	// because the other two depend on a key being released and a stuck key is
	// exactly the case where that does not happen.
	HoldSeconds   time.Duration
	MaxHoldFrames int

	// released is reported so the log can say how long an activity ran and how
	// much of it was recorded.
	released []string
}

// ParseWatchedKeys reads the capture_keys setting.
//
// Format is deliberately forgiving, because it is typed by a person:
//
//	capture_keys = tab:scan, alt+m:mining laser, v
//
// The label after the colon is optional and is only used to say WHY a frame was
// taken. A frame that says "you pressed the scan key" is a labelled training
// example; one that says "a key was pressed" is a picture.
func ParseWatchedKeys(raw string) ([]*watchedKey, []string) {
	return parseWatchedKeys(raw, false)
}

// ParseHeldKeys reads capture_keys_held - keys that describe an activity rather
// than a moment.
func ParseHeldKeys(raw string) ([]*watchedKey, []string) {
	return parseWatchedKeys(raw, true)
}

func parseWatchedKeys(raw string, hold bool) ([]*watchedKey, []string) {
	var out []*watchedKey
	var problems []string
	for _, entry := range strings.Split(raw, ",") {
		entry = strings.TrimSpace(entry)
		if entry == "" {
			continue
		}
		spec, label := entry, ""
		if i := strings.LastIndex(entry, ":"); i > 0 {
			spec = strings.TrimSpace(entry[:i])
			label = strings.TrimSpace(entry[i+1:])
		}
		// NOT parseHotkey. A watched key is polled, not registered, so it
		// takes nothing from the game and a bare key is the normal case.
		// Using the hotkey parser here rejected every single-key entry and
		// left this whole feature doing nothing. See parseKeySpec.
		mods, vk, pretty, err := parseKeySpec(spec, false)
		if err != nil {
			// NAMED, NOT SWALLOWED. A key that silently failed to parse is a
			// player wondering for a week why their scan key does nothing.
			problems = append(problems, fmt.Sprintf("%q could not be understood (%v)", spec, err))
			continue
		}
		if label == "" {
			label = pretty
		}
		out = append(out, &watchedKey{
			Spec: pretty, Label: label, Hold: hold,
			mods: mods, vk: vk, need: modifierVKs(mods),
		})
	}
	return out, problems
}

func NewKeyWatcher(keys []*watchedKey) *KeyWatcher {
	return &KeyWatcher{
		keys: keys, last: map[string]time.Time{},
		HoldSeconds: 2 * time.Second,
		// 60 frames is two minutes of continuous mining at the default rhythm,
		// and about 150 MB. A ceiling that is generous but finite: a key held
		// down by a stuck peripheral must not be able to fill a disk.
		MaxHoldFrames: 60,
	}
}

// Poll returns a trigger for each key that went from up to down since the last
// call. Edge-detected, so holding a key produces one frame rather than a flood.
//
// minGap suppresses a key held down and released repeatedly - a mining laser
// being pulsed would otherwise produce a picture per pulse.
func (w *KeyWatcher) Poll(now time.Time, minGap time.Duration) []Trigger {
	if w == nil || len(w.keys) == 0 {
		return nil
	}
	w.released = w.released[:0]
	var out []Trigger
	for _, k := range w.keys {
		down := comboDown(k.need, k.vk)
		pressed := down && !k.wasDwn
		let := k.wasDwn && !down
		k.wasDwn = down

		if let {
			// Released. Say what was recorded, because "I mined for four
			// minutes" and "the collector recorded four minutes of it" are
			// different claims and only the log can tell them apart.
			if k.Hold && k.frames > 0 {
				w.released = append(w.released,
					fmt.Sprintf("%s (%s): %d frames", k.Spec, k.Label, k.frames))
			}
			k.frames = 0
			continue
		}

		switch {
		case pressed:
			if t, seen := w.last[k.Spec]; seen && now.Sub(t) < minGap && !k.Hold {
				continue
			}
			w.last[k.Spec] = now
			k.lastShot = now
			k.frames = 1
			note := "the player pressed " + k.Spec + " (" + k.Label + ")"
			if k.Hold {
				note += " and this keeps recording while it is held"
			}
			out = append(out, Trigger{
				Kind: "keypress", Field: k.Label, To: k.Spec, Value: valueHigh,
				Note: note + " - this frame is labelled by what they were doing, " +
					"not by when a timer fired",
			})

		case down && k.Hold:
			// CEILING FIRST, before the clock, so a hold cannot take one more
			// frame than it is allowed to however the timing falls.
			if k.frames >= w.MaxHoldFrames {
				continue
			}
			if now.Sub(k.lastShot) < w.HoldSeconds {
				continue
			}
			k.lastShot = now
			k.frames++
			out = append(out, Trigger{
				Kind: "keypress", Field: k.Label, To: k.Spec, Value: valueHigh,
				Seconds: int(w.HoldSeconds / time.Second),
				Note: fmt.Sprintf("still holding %s (%s) - frame %d of at most %d",
					k.Spec, k.Label, k.frames, w.MaxHoldFrames),
			})
		}
	}
	return out
}

// Released reports the holds that ended on the most recent Poll.
func (w *KeyWatcher) Released() []string {
	if w == nil {
		return nil
	}
	return w.released
}

// Describe is what goes in the log at startup, so a player can see the tool
// understood them.
func (w *KeyWatcher) Describe() string {
	if w == nil || len(w.keys) == 0 {
		return "none (set capture_keys in collector-settings.txt to capture when you " +
			"press scan, ping, mining or salvage)"
	}
	var parts []string
	for _, k := range w.keys {
		mode := "on press"
		if k.Hold {
			mode = fmt.Sprintf("while held, every %ds", int(w.HoldSeconds/time.Second))
		}
		parts = append(parts, fmt.Sprintf("%s = %s (%s)", k.Spec, k.Label, mode))
	}
	return strings.Join(parts, ", ")
}
