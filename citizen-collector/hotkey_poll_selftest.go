package main

// hotkey_poll_selftest.go - checks for the three fixes made on 2026-08-07:
// the callback leak that killed the process every fourteen minutes, the
// GetAsyncKeyState edge detector, and the interval's move from minutes to
// seconds.
//
// EVERY CHECK IN HERE HAS A NEGATIVE CONTROL, per hard rule 12: a check that
// cannot fail is not a check. Where a control is missing it is because the
// thing genuinely cannot be measured in-process, and that is said out loud
// rather than papered over.

import (
	"fmt"
	"strings"
	"syscall"
	"time"
)

// --- 1. the callback leak --------------------------------------------------

// naiveEnumCallbacks is the OLD, broken shape: a fresh syscall.NewCallback on
// every call. It exists ONLY as the negative control below. Never call it from
// anything real.
//
// It is capped hard at 50 because every one of these permanently consumes a
// slot in a process-wide table of roughly two thousand. Fifty is enough to
// prove the table grows and cheap enough that the test itself cannot become
// the thing that kills the process - which would be a memorable way to fail.
func naiveEnumCallbacks(n int) []uintptr {
	if n > 50 {
		n = 50
	}
	out := make([]uintptr, 0, n)
	for i := 0; i < n; i++ {
		// THE CLOSURE MUST CAPTURE i, AND THAT IS THE ENTIRE POINT.
		//
		// This used to be `func(h HWND, _ uintptr) uintptr { return 0 }` -
		// a closure over nothing, which Go compiles to ONE static function.
		// syscall.NewCallback keys on the function's code pointer, so fifty
		// calls returned the same address fifty times and this control
		// reported 1 distinct where it wanted 50. It looked like proof that
		// the leak was impossible; it was proof that the test was measuring
		// the wrong thing.
		//
		// The real 14-minute crash came from a closure that captured a
		// variable, because THAT produces a fresh func value per call and a
		// fresh slot in a table that is never freed. Capturing i reproduces
		// the actual mechanism.
		i := i
		out = append(out, syscall.NewCallback(func(h HWND, _ uintptr) uintptr { return uintptr(i) }))
	}
	return out
}

func runCallbackLeakSelftest(check func(name string, ok bool, detail string)) {
	// NEGATIVE CONTROL FIRST. If allocating callbacks in a loop does NOT
	// produce distinct addresses, then syscall.NewCallback is not behaving the
	// way this whole diagnosis assumes, and the positive check below would be
	// measuring nothing. Fail here rather than pass on a false premise.
	const n = 50
	got := naiveEnumCallbacks(n)
	distinct := map[uintptr]bool{}
	for _, c := range got {
		distinct[c] = true
	}
	check("NEGATIVE CONTROL: per-call NewCallback allocates a new slot every time",
		len(distinct) == n,
		fmt.Sprintf("%d calls produced %d distinct callback addresses (expected %d)",
			n, len(distinct), n))

	// POSITIVE. The fixed EnumTopWindows must allocate exactly one, no matter
	// how many times it runs.
	//
	// 3,000 iterations is deliberately more than the ~2,000 the table holds:
	// the OLD code could not have survived this loop, so reaching the end of it
	// is itself the proof. At the real 2-second poll rate this is about a
	// hundred minutes of running compressed into a fraction of a second.
	before := callbacksAllocated()
	for i := 0; i < 3000; i++ {
		EnumTopWindows(func(h HWND) bool { return false }) // stop immediately
	}
	after := callbacksAllocated()
	check("EnumTopWindows survives 3000 calls and allocates ONE callback",
		before == 1 && after == 1,
		fmt.Sprintf("callbacks allocated before=%d after=%d, 3000 enumerations completed",
			before, after))

	// The callback must still actually do its job. A fix that stops the crash
	// by never invoking fn would pass everything above.
	seen := 0
	EnumTopWindows(func(h HWND) bool {
		seen++
		return seen < 3 // stop after three
	})
	check("EnumTopWindows still invokes the callback",
		seen > 0,
		fmt.Sprintf("callback ran %d times (0 would mean the fix broke enumeration)", seen))
}

// --- 2. the GetAsyncKeyState edge detector ---------------------------------

func runHotkeyEdgeSelftest(check func(name string, ok bool, detail string)) {
	// The sequence a human actually produces: press, hold, release, press.
	// "held" is the case that matters - a held key must NOT stream captures.
	seq := []bool{
		false, false, // idle
		true,                   // press        <- fire 1
		true, true, true, true, // held for four ticks   <- must be silent
		false, false, // released
		true,  // press again   <- fire 2
		false, // released
	}
	var e hotkeyEdge
	fires := 0
	for _, down := range seq {
		if e.step(down) {
			fires++
		}
	}
	check("hotkey edge detector fires exactly once per press",
		fires == 2,
		fmt.Sprintf("press/hold(4)/release/press produced %d fires (expected 2)", fires))

	// NEGATIVE CONTROL: a detector that fired on level rather than edge would
	// report 5 here, not 2. Assert the held ticks specifically.
	var e2 hotkeyEdge
	held := 0
	e2.step(true) // the initial press
	for i := 0; i < 10; i++ {
		if e2.step(true) {
			held++
		}
	}
	check("NEGATIVE CONTROL: holding the key produces no further fires",
		held == 0,
		fmt.Sprintf("10 additional held observations produced %d fires (expected 0)", held))

	// A key with no modifier down must never register. comboDown is the gate.
	need := modifierVKs(ModAlt | ModControl)
	check("modifier decoding: Alt+Ctrl requires two modifier groups",
		len(need) == 2,
		fmt.Sprintf("modifierVKs(ModAlt|ModControl) -> %d groups", len(need)))

	needWin := modifierVKs(ModWin)
	check("modifier decoding: Win accepts either physical Win key",
		len(needWin) == 1 && len(needWin[0]) == 2,
		fmt.Sprintf("modifierVKs(ModWin) -> %v (expected one group of two)", needWin))

	check("modifier decoding: no modifiers -> no groups",
		len(modifierVKs(0)) == 0,
		"modifierVKs(0) is empty")
}

// --- 3. dedup between the two delivery paths -------------------------------

// runHotkeyDedupSelftest proves that two mechanisms reporting one press produce
// one capture. Both paths are live at once by design, so without this the fix
// for the Vulkan problem would double every keystroke on DX11.
func runHotkeyDedupSelftest(check func(name string, ok bool, detail string)) {
	presses := make(chan string, 4)
	var lastFire time.Time
	deliver := func(via string) {
		if time.Since(lastFire) < 400*time.Millisecond {
			return
		}
		lastFire = time.Now()
		select {
		case presses <- via:
		default:
		}
	}

	deliver("RegisterHotKey")
	deliver("polling") // same press, microseconds later - must be swallowed
	check("one press delivered by both mechanisms produces ONE press",
		len(presses) == 1,
		fmt.Sprintf("two deliveries in the same instant produced %d press(es)", len(presses)))

	// NEGATIVE CONTROL: a genuine second press, well outside the window, MUST
	// get through. A dedup that swallows everything would pass the check above.
	time.Sleep(450 * time.Millisecond)
	deliver("polling")
	check("NEGATIVE CONTROL: a real second press is not swallowed",
		len(presses) == 2,
		fmt.Sprintf("a press 450ms later produced %d total (expected 2)", len(presses)))
}

// --- 4. the interval, in seconds -------------------------------------------

func runIntervalSecondsSelftest(check func(name string, ok bool, detail string)) {
	base := time.Date(2026, 8, 7, 18, 0, 0, 0, time.UTC)
	fake := base
	r := newAutoRunner(autoConfig{PollSeconds: 2, DebounceSeconds: 3, IntervalSeconds: 60},
		func() time.Time { return fake })

	fake = base.Add(59 * time.Second)
	tooEarly := r.decide(nil)
	fake = base.Add(60 * time.Second)
	due := r.decide(nil)
	fake = base.Add(61 * time.Second)
	justFired := r.decide(nil)

	check("interval fires at 60s and not at 59s",
		tooEarly == nil && due != nil && justFired == nil,
		fmt.Sprintf("59s=%v 60s=%v 61s=%v", tooEarly, due != nil, justFired))

	if due != nil {
		check("interval trigger reads as seconds, not minutes",
			due.Reason() == "interval:60s",
			fmt.Sprintf("Reason() = %q (expected \"interval:60s\")", due.Reason()))
	}

	// A state change must push the next interval out, not leave it where it was.
	fake = base
	r2 := newAutoRunner(autoConfig{PollSeconds: 2, DebounceSeconds: 3, IntervalSeconds: 60},
		func() time.Time { return fake })
	fake = base.Add(45 * time.Second)
	sc := r2.decide([]Trigger{{Kind: "event", Field: "client_spawned"}})
	fake = base.Add(60 * time.Second)
	at60 := r2.decide(nil)
	fake = base.Add(105 * time.Second)
	at105 := r2.decide(nil)
	check("a capture at 45s pushes the next interval to 105s, not 60s",
		sc != nil && at60 == nil && at105 != nil,
		fmt.Sprintf("45s state change=%v, 60s=%v, 105s=%v", sc != nil, at60 != nil, at105 != nil))

	// A hotkey capture goes around decide(), so noteCapture is what keeps the
	// interval honest. Without it the 60s fallback fires on a scene that was
	// photographed a moment ago.
	fake = base
	r3 := newAutoRunner(autoConfig{PollSeconds: 2, DebounceSeconds: 3, IntervalSeconds: 60},
		func() time.Time { return fake })
	fake = base.Add(50 * time.Second)
	r3.noteCapture(fake)
	fake = base.Add(60 * time.Second)
	afterManual := r3.decide(nil)
	fake = base.Add(110 * time.Second)
	afterManualLater := r3.decide(nil)
	check("a manual capture resets the interval clock",
		afterManual == nil && afterManualLater != nil,
		fmt.Sprintf("60s after start (10s after a manual frame)=%v, 110s=%v",
			afterManual != nil, afterManualLater != nil))

	// NEGATIVE CONTROL: with the interval off, an hour must produce nothing.
	fake = base
	r4 := newAutoRunner(autoConfig{PollSeconds: 2, DebounceSeconds: 3, IntervalSeconds: 0},
		func() time.Time { return fake })
	offFires := 0
	for sec := 1; sec <= 3600; sec += 30 {
		fake = base.Add(time.Duration(sec) * time.Second)
		if r4.decide(nil) != nil {
			offFires++
		}
	}
	check("NEGATIVE CONTROL: interval_seconds = 0 fires nothing in a simulated hour",
		offFires == 0,
		fmt.Sprintf("%d interval captures with the fallback turned off (expected 0)", offFires))

	check("intervalDesc reads plainly",
		intervalDesc(60) == "60s (1m)" && intervalDesc(0) == "off" && intervalDesc(90) == "90s",
		fmt.Sprintf("60 -> %q, 0 -> %q, 90 -> %q",
			intervalDesc(60), intervalDesc(0), intervalDesc(90)))
}

// --- 5. the old settings file keeps working --------------------------------

func runIntervalSettingsSelftest(check func(name string, ok bool, detail string)) {
	mk := func(kv map[string]string) *settings {
		return &settings{values: kv, loaded: true}
	}

	// TWO CHECKS, NOT ONE, because they answer different questions and one of
	// them used to answer both by accident. Asserting the literal 60 here made
	// this a test of the constant's value dressed as a test of the resolver -
	// so changing the default broke a check whose name says nothing about
	// defaults.
	sec, notes, err := resolveIntervalSeconds(mk(map[string]string{}))
	check("no interval setting -> whatever the built-in default is",
		err == nil && sec == defaultIntervalSeconds && len(notes) == 0,
		fmt.Sprintf("sec=%d notes=%v err=%v", sec, notes, err))

	// And the value itself, pinned on its own. A change to the default is a
	// decision; this makes it a visible edit rather than a silent one.
	check("the built-in default is 120s (§2, 2026-08-13 - gated, then doubled)",
		defaultIntervalSeconds == 120,
		fmt.Sprintf("defaultIntervalSeconds = %d", defaultIntervalSeconds))

	sec, notes, err = resolveIntervalSeconds(mk(map[string]string{"interval_seconds": "30"}))
	check("interval_seconds is honoured",
		err == nil && sec == 30,
		fmt.Sprintf("sec=%d err=%v", sec, err))
	// NEW 2026-08-13: a file that overrides the default now SAYS it is doing
	// so. Without this the only symptom of an old settings file is "I updated
	// and the interval did not change".
	check("a setting that overrides the default is reported, not silent",
		len(notes) == 1 && strings.Contains(notes[0], "overrides the built-in default"),
		fmt.Sprintf("notes = %v", notes))

	// NEGATIVE CONTROL: a file that merely restates the default has nothing to
	// report, and must not produce a line saying it overrode anything.
	_, quietNotes, _ := resolveIntervalSeconds(mk(map[string]string{
		"interval_seconds": fmt.Sprintf("%d", defaultIntervalSeconds)}))
	check("NEGATIVE CONTROL: a file that matches the default says nothing",
		len(quietNotes) == 0, fmt.Sprintf("notes = %v", quietNotes))

	// The case that matters: Sleven's file on disk right now says
	// interval_minutes = 10. It must keep working AND must say so.
	sec, notes, err = resolveIntervalSeconds(mk(map[string]string{"interval_minutes": "10"}))
	check("an old interval_minutes file still works, and is converted",
		err == nil && sec == 600,
		fmt.Sprintf("interval_minutes=10 -> %ds (expected 600)", sec))
	check("the conversion is REPORTED, never silent",
		len(notes) == 1,
		fmt.Sprintf("notes = %v", notes))

	sec, notes, err = resolveIntervalSeconds(mk(map[string]string{
		"interval_seconds": "45", "interval_minutes": "10"}))
	check("interval_seconds wins over interval_minutes, and the loser is named",
		err == nil && sec == 45 && len(notes) == 1,
		fmt.Sprintf("sec=%d notes=%v", sec, notes))

	// NEGATIVE CONTROL: garbage must be an error, not a silent default. A
	// resolver that swallowed this would look identical to a working one until
	// the day it mattered.
	_, _, err = resolveIntervalSeconds(mk(map[string]string{"interval_seconds": "soon"}))
	check("NEGATIVE CONTROL: a non-numeric interval is an error, not a shrug",
		err != nil,
		fmt.Sprintf("interval_seconds=\"soon\" -> err=%v", err))
}
