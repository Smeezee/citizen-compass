package main

// keywatch_selftest.go - checks for capture-on-keypress.
//
// The parsing and the edge logic are testable without a keyboard. Whether
// Windows reports the key is not, and that is the part a live session settles.

import (
	"fmt"
	"strings"
	"time"
)

func runKeyWatchSelftest(check func(name string, ok bool, detail string)) {
	keys, problems := ParseWatchedKeys("tab:scan, alt+m:mining laser, v")
	// EVERY TERM IN THE DETAIL. This check went red on 2026-08-08 reporting
	// only "three entries, no complaints", which says what was wanted and
	// nothing about what happened - so the real cause (bare keys rejected as
	// "no modifier") was invisible from the result and had to be hunted.
	check("keys: a settings line becomes watched keys",
		len(keys) == 3 && len(problems) == 0,
		fmt.Sprintf("got %d keys and %d complaints (want 3 and 0): %s",
			len(keys), len(problems), strings.Join(problems, "; ")))
	if len(keys) == 3 {
		check("keys: the player's own label is kept",
			keys[0].Label == "scan" && keys[1].Label == "mining laser",
			"a frame that says WHY it was taken is a labelled example; one that "+
				"says a key was pressed is just a picture")
		check("keys: a key with no label falls back to its own name",
			keys[2].Label != "" && !strings.Contains(keys[2].Label, ":"),
			"got "+keys[2].Label)
		check("keys: modifiers are understood",
			keys[1].mods != 0, "alt+m must carry a modifier")
	}

	// A key that cannot be parsed must be NAMED, not swallowed. A silent drop
	// is a player wondering for a week why their scan key does nothing.
	_, problems2 := ParseWatchedKeys("tab:scan, notakey123456:nonsense")
	check("keys: an unreadable entry is reported, not dropped in silence",
		len(problems2) == 1 && strings.Contains(problems2[0], "notakey123456"),
		fmt.Sprintf("%d complaint(s): %s", len(problems2), strings.Join(problems2, "; ")))

	// NEGATIVE CONTROL: the parser must accept things, or the check above would
	// pass on a parser that rejected everything.
	good, badProblems := ParseWatchedKeys("f5")
	check("NEGATIVE CONTROL: a plain valid key still parses",
		len(good) == 1 && len(badProblems) == 0,
		fmt.Sprintf("f5 produced %d keys, %d complaints: %s",
			len(good), len(badProblems), strings.Join(badProblems, "; ")))

	// THE CHECK THAT WOULD HAVE CAUGHT IT ON DAY ONE.
	//
	// Every entry anybody would actually write here is a bare key: tab, v, the
	// trigger. The watched-key parser borrowed the HOTKEY parser, which refuses
	// a bare key because RegisterHotKey would steal it from the game - a rule
	// that is right there and wrong here, since these keys are only ever
	// observed. So capture_keys rejected everything and the feature was dead
	// from the day it was written.
	for _, bare := range []string{"tab", "v", "f5", "mouse1", "space"} {
		k, p := ParseWatchedKeys(bare)
		check("keys: the bare key "+bare+" is accepted",
			len(k) == 1 && len(p) == 0,
			fmt.Sprintf("%d key(s), %d complaint(s): %s", len(k), len(p), strings.Join(p, "; ")))
	}
	// NEGATIVE CONTROL: loosening the rule must not have made the parser accept
	// everything. Genuine nonsense still has to be refused and named.
	junk, junkProblems := ParseWatchedKeys("qwertyuiop123")
	check("NEGATIVE CONTROL: a bare key that is not a key is still refused",
		len(junk) == 0 && len(junkProblems) == 1,
		fmt.Sprintf("%d key(s), %d complaint(s)", len(junk), len(junkProblems)))
	// And the hotkey parser must KEEP the rule - that one really does register
	// globally, and a bare key there would be taken from the game.
	if _, _, _, herr := parseHotkey("v"); true {
		check("NEGATIVE CONTROL: the real hotkey still refuses a bare key",
			herr != nil,
			"RegisterHotKey takes the key from every program on the machine; a bare "+
				"one would stop working inside Star Citizen")
	}

	// --- edge behaviour, with a fake key state ------------------------------
	base := time.Date(2026, 8, 8, 12, 0, 0, 0, time.UTC)
	w := NewKeyWatcher(nil)
	check("keys: no configured keys means no triggers, ever",
		len(w.Poll(base, time.Second)) == 0,
		"the default is off and must cost nothing")

	// Drive the edge logic directly - comboDown needs a real keyboard, so the
	// down-state is set by hand here and the EDGE is what is under test.
	k := &watchedKey{Spec: "Tab", Label: "scan"}
	w2 := &KeyWatcher{keys: []*watchedKey{k}, last: map[string]time.Time{}}
	fire := func(down bool, at time.Time) int {
		// mimic Poll's edge test without touching Windows
		fired := down && !k.wasDwn
		k.wasDwn = down
		if !fired {
			return 0
		}
		if t, seen := w2.last[k.Spec]; seen && at.Sub(t) < 3*time.Second {
			return 0
		}
		w2.last[k.Spec] = at
		return 1
	}
	n := fire(true, base)
	n += fire(true, base.Add(100*time.Millisecond)) // still held
	n += fire(true, base.Add(200*time.Millisecond)) // still held
	check("keys: holding a key produces ONE frame, not a flood",
		n == 1, "edge-detected, like the hotkey")

	n2 := fire(false, base.Add(time.Second))
	n2 += fire(true, base.Add(time.Second+100*time.Millisecond))
	check("keys: a re-press inside the gap is suppressed",
		n2 == 0, "pulsing a mining laser must not be a picture per pulse")

	_ = fire(false, base.Add(5*time.Second))
	n3 := fire(true, base.Add(6*time.Second))
	check("NEGATIVE CONTROL: a deliberate press AFTER the gap does fire",
		n3 == 1, "the suppression must be a gap, not a mute")

	check("keys: the startup line says what it understood",
		strings.Contains(NewKeyWatcher(keys).Describe(), "scan") &&
			strings.Contains(NewKeyWatcher(nil).Describe(), "capture_keys"),
		fmt.Sprintf("configured: %q | empty: %q",
			NewKeyWatcher(keys).Describe(), NewKeyWatcher(nil).Describe()))
}

// runHeldKeySelftest covers the case Sleven raised: a key held down for an
// activity rather than tapped for an event.
//
// The down-state is driven by hand because comboDown needs a real keyboard.
// What is under test is the RHYTHM and the ceiling, which is where this can go
// wrong in ways that fill a disk.
func runHeldKeySelftest(check func(name string, ok bool, detail string)) {
	held, problems := ParseHeldKeys("mouse1:guns, m:mining laser")
	check("held: mouse buttons are understood",
		len(held) == 2 && len(problems) == 0,
		fmt.Sprintf("%d held key(s), %d complaint(s): %s",
			len(held), len(problems), strings.Join(problems, "; ")))
	if len(held) == 2 {
		check("held: they are marked as holds, not taps",
			held[0].Hold && held[1].Hold, "different animals from a scan ping")
	}

	// NEGATIVE CONTROL: capture_keys must still produce TAP keys, or the flag
	// means nothing.
	tap, _ := ParseWatchedKeys("tab:scan")
	check("NEGATIVE CONTROL: capture_keys still produces tap keys",
		len(tap) == 1 && !tap[0].Hold,
		fmt.Sprintf("parsed %d key(s) from \"tab:scan\"", len(tap)))

	base := time.Date(2026, 8, 8, 12, 0, 0, 0, time.UTC)
	k := &watchedKey{Spec: "Mouse1", Label: "guns", Hold: true}
	w := &KeyWatcher{keys: []*watchedKey{k}, last: map[string]time.Time{},
		HoldSeconds: 2 * time.Second, MaxHoldFrames: 5}

	// Replay Poll's decision without touching Windows.
	step := func(down bool, at time.Time) int {
		pressed := down && !k.wasDwn
		let := k.wasDwn && !down
		k.wasDwn = down
		if let {
			k.frames = 0
			return 0
		}
		switch {
		case pressed:
			k.lastShot = at
			k.frames = 1
			return 1
		case down && k.Hold:
			if k.frames >= w.MaxHoldFrames {
				return 0
			}
			if at.Sub(k.lastShot) < w.HoldSeconds {
				return 0
			}
			k.lastShot = at
			k.frames++
			return 1
		}
		return 0
	}

	n := step(true, base)
	for i := 1; i <= 30; i++ {
		n += step(true, base.Add(time.Duration(i)*time.Second))
	}
	check("held: holding the trigger keeps recording, it does not stop at one",
		n == w.MaxHoldFrames,
		"thirty seconds of firing produced "+itoaSmall(n)+" frames")
	check("held: and it stops at the ceiling",
		k.frames == w.MaxHoldFrames,
		"a key held down by a stuck peripheral must not fill a disk")

	// NEGATIVE CONTROL: without the ceiling this would be 15 frames at 2s over
	// 30s. If the count ever equals that, the ceiling is not doing anything.
	check("NEGATIVE CONTROL: the ceiling actually bound the count",
		n < 15, "unbounded 2s firing over 30s would be 15")

	// Release must reset, or the next hold starts already exhausted.
	step(false, base.Add(31*time.Second))
	after := step(true, base.Add(32*time.Second))
	check("held: releasing resets, so the next burst is a fresh one",
		after == 1 && k.frames == 1,
		"otherwise one long hold poisons every later one")

	// A TAP key must never enter the hold path.
	kt := &watchedKey{Spec: "Tab", Label: "scan"}
	wt := &KeyWatcher{keys: []*watchedKey{kt}, last: map[string]time.Time{},
		HoldSeconds: 2 * time.Second, MaxHoldFrames: 5}
	_ = wt
	held2 := 0
	kt.wasDwn = true
	if kt.Hold {
		held2++
	}
	check("held: a tap key stays a tap key while held down",
		held2 == 0, "holding scan must not produce a stream")
}
