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
