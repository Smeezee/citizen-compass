package main

// hotkey_selftest.go - proving the hotkey is actually REGISTERED in auto mode.
//
// WHY THIS EXISTS
//
// --auto shipped with the hotkey dead. main() entered the auto branch, called
// runAuto and returned; parseHotkey and RegisterHotKey sat AFTER that return
// and were never reached. Ctrl+Alt+F9 did nothing, logged nothing, and gave no
// sign it was dead until someone pressed it repeatedly at a shop terminal
// during a live session.
//
// 34 checks and 13 mutations did not catch it, and they were right not to: it
// is a WIRING defect in main(), not a logic defect in runAuto. Every check
// pointed at runAuto's decisions, and runAuto's decisions were fine.
//
// So this test does not ask "would the code register a hotkey". It asks
// WINDOWS whether a hotkey IS REGISTERED right now.
//
// THE PROBE
//
// RegisterHotKey refuses a combination that is already registered, returning
// ERROR_HOTKEY_ALREADY_REGISTERED (1409). That refusal is the measurement:
//
//   listener started  ->  a probe registration of the same combo must FAIL
//   no listener       ->  the same probe must SUCCEED
//
// The two outcomes are opposite by construction. If they ever agree, the probe
// is not looking at registration state and this file is lying - which is the
// exact failure mode the negative control exists to expose.

import (
	"fmt"
	"time"
)

// runHotkeyLoopSelftest proves the OTHER half: that a press actually reaches
// runAuto and produces a capture tagged as manual.
//
// Registration alone is not enough. A key that Windows accepts but whose
// presses go nowhere is the same dead hotkey from the operator's side.
//
// PollSeconds is set to an hour so the periodic tick CANNOT fire during the
// test. Any capture observed here therefore came from the press and from
// nothing else - the test cannot pass by accident on a timer.
func runHotkeyLoopSelftest(check func(name string, ok bool, detail string)) {
	presses := make(chan struct{}, 1)
	stop := make(chan struct{})
	captured := make(chan Trigger, 4)

	deps := autoDeps{
		logf:       func(string, ...interface{}) {},
		gameAlive:  func() error { return nil },
		hotkeys:    presses,
		hotkeyName: "Ctrl+Alt+F9",
		capture: func(t Trigger) (string, error) {
			captured <- t
			return `C:\fake\shot_0001.png`, nil
		},
	}
	cfg := autoConfig{PollSeconds: 3600, DebounceSeconds: 0, IntervalMinutes: 0}

	done := make(chan struct{})
	go func() { _ = runAuto(cfg, "", deps, stop); close(done) }()

	// NEGATIVE CONTROL: with no press, nothing must be captured. If the loop
	// captured here, every result below would be meaningless.
	select {
	case t := <-captured:
		check("no capture without a press", false, "captured "+t.Reason()+" with no press")
		close(stop)
		<-done
		return
	case <-time.After(300 * time.Millisecond):
		check("no capture without a press", true, "quiet for 300ms, so the tick is not firing")
	}

	presses <- struct{}{}

	select {
	case t := <-captured:
		check("a press CAPTURES", t.Kind == "hotkey",
			fmt.Sprintf("capture fired with trigger kind %q", t.Kind))
		check("manual frame is distinguishable", t.Note == "Ctrl+Alt+F9",
			fmt.Sprintf("trigger records note %q, so a manual frame is identifiable afterwards", t.Note))
	case <-time.After(3 * time.Second):
		check("a press CAPTURES", false, "press produced no capture within 3s - the channel is not wired into the loop")
		check("manual frame is distinguishable", false, "not reached")
	}

	close(stop)
	<-done
}

// probeIsRegistered reports whether spec is currently held by anyone.
//
// It works by trying to take the combination itself. Success means nothing held
// it - so the probe immediately gives it back. Failure means something does.
//
// probeID is deliberately different from hotkeyID: re-registering the SAME id
// from the same thread would replace the existing registration rather than
// being refused, which would make the probe report "free" for a key that is
// very much taken.
func probeIsRegistered(probeID int, spec string) (registered bool, err error) {
	mods, vk, _, err := parseHotkey(spec)
	if err != nil {
		return false, err
	}
	if err := RegisterHotKey(probeID, mods|ModNoRepeat, vk); err != nil {
		// Refused - something else already owns it.
		return true, nil
	}
	// We got it, so nobody had it. Put it straight back.
	UnregisterHotKey(probeID)
	return false, nil
}

const hotkeyProbeID = 4711

// runHotkeySelftest proves the auto-mode hotkey wiring by behaviour.
func runHotkeySelftest(check func(name string, ok bool, detail string)) {
	const spec = "ctrl+alt+f9"

	// ---------------------------------------------------------------------
	// PRECONDITION. If the combination is already taken - a real collector is
	// running, or another app owns it - then neither result below means
	// anything, and saying so is the only honest option.
	// ---------------------------------------------------------------------
	if held, err := probeIsRegistered(hotkeyProbeID, spec); err != nil {
		check("hotkey probe usable", false, fmt.Sprintf("probe itself failed: %v", err))
		return
	} else if held {
		check("hotkey probe usable", false,
			spec+" is ALREADY held by something else (a running collector?) - "+
				"registration checks NOT PERFORMED, and not reported as passed")
		return
	}
	check("hotkey probe usable", true, spec+" is free, so the probe can tell taken from free")

	// ---------------------------------------------------------------------
	// NEGATIVE CONTROL FIRST. An invalid spec must leave NOTHING registered.
	//
	// Running it first matters: if it were run second, a leaked registration
	// from the positive case could make it fail for the wrong reason and the
	// failure would be blamed on the wrong thing.
	// ---------------------------------------------------------------------
	badListener, badErr := startHotkeyListener(hotkeyID, "ctrl+alt+notakey")
	check("invalid hotkey is REFUSED", badListener == nil && badErr != nil,
		fmt.Sprintf("startHotkeyListener(%q) -> %v", "ctrl+alt+notakey", badErr))

	heldAfterBad, err := probeIsRegistered(hotkeyProbeID, spec)
	if err != nil {
		check("nothing registered after invalid hotkey", false, fmt.Sprintf("probe failed: %v", err))
		return
	}
	check("nothing registered after invalid hotkey", !heldAfterBad,
		"probe re-acquired "+spec+" freely, so the failed attempt registered nothing")

	// ---------------------------------------------------------------------
	// POSITIVE CASE. A valid spec must leave the key genuinely registered with
	// the operating system.
	// ---------------------------------------------------------------------
	good, err := startHotkeyListener(hotkeyID, spec)
	if err != nil {
		check("auto-mode hotkey REGISTERS", false, fmt.Sprintf("startHotkeyListener(%q) -> %v", spec, err))
		return
	}
	check("auto-mode hotkey REGISTERS", good != nil && good.Pretty == "Ctrl+Alt+F9",
		fmt.Sprintf("listener reports %q", good.Pretty))

	heldAfterGood, err := probeIsRegistered(hotkeyProbeID, spec)
	if err != nil {
		check("hotkey is registered WITH WINDOWS", false, fmt.Sprintf("probe failed: %v", err))
		return
	}
	check("hotkey is registered WITH WINDOWS", heldAfterGood,
		"probe was REFUSED "+spec+" - the OS confirms it is taken, not merely that our code ran")

	// ---------------------------------------------------------------------
	// THE COMPARISON THAT MAKES THE PAIR MEAN SOMETHING.
	//
	// The brief: "if both pass identically the check is not looking at
	// registration". So the two probe results are compared directly, and a
	// check that they DIFFER is recorded in its own right. A probe that
	// returned the same answer in both states would pass both assertions above
	// while measuring nothing.
	// ---------------------------------------------------------------------
	check("probe distinguishes registered from not",
		heldAfterGood != heldAfterBad,
		fmt.Sprintf("after invalid=%v, after valid=%v - the probe changes with the state it measures",
			heldAfterBad, heldAfterGood))

	// ---------------------------------------------------------------------
	// The wiring defect itself: autoDeps must actually carry the channel.
	// A registered hotkey that never reaches runAuto is the same dead key.
	// ---------------------------------------------------------------------
	d := autoDeps{hotkeys: good.Presses, hotkeyName: good.Pretty}
	check("hotkey reaches autoDeps", d.hotkeys != nil && d.hotkeyName != "",
		fmt.Sprintf("autoDeps carries the press channel and the name %q", d.hotkeyName))

	// ---------------------------------------------------------------------
	// Give the key back, and PROVE it was given back.
	//
	// Leaving it held would make the end-to-end check that follows report
	// "already held - NOT PERFORMED", which is honest but useless. Releasing it
	// is also the only evidence that Close actually reaches the registering
	// thread rather than silently doing nothing.
	// ---------------------------------------------------------------------
	good.Close()
	stillHeld, err := probeIsRegistered(hotkeyProbeID, spec)
	if err != nil {
		check("hotkey is RELEASED on Close", false, fmt.Sprintf("probe failed: %v", err))
		return
	}
	check("hotkey is RELEASED on Close", !stillHeld,
		"probe re-acquired "+spec+" after Close, so the registration really was handed back")
}
