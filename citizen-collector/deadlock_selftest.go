package main

// deadlock_selftest.go - the 2026-08-08 enumeration deadlock.
//
// # WHAT THE FIRST VERSION OF THIS FILE ASSERTED, AND WHY IT WAS WRONG
//
// It asserted "no window belonging to this process is ever handed to a caller
// of EnumTopWindows", because that was the shape of the first fix. It passed.
//
// It was testing the workaround rather than the hazard, and the workaround had
// a cost nobody had measured: hiding own windows from every caller also hid the
// process-lock selftest's decoy, which is deliberately one of ours. Two checks
// in that file went red - including its negative control, the one that proves
// the lock ACCEPTS a genuine game window. A blinded negative control is the
// worst possible failure, because from then on the positive result means
// nothing.
//
// The guard now sits on the blocking call itself (see windowText), so own
// windows enumerate normally again. The checks below therefore test the actual
// invariant instead of the mechanism:
//
//	READING ANY WINDOW'S TITLE, INCLUDING OUR OWN, RETURNS.
//
// # WHY IT IS TIMED RATHER THAN INSPECTED
//
// The deadlock cannot be reproduced here - it needs two OS threads, a real
// webview window and a message pump that has stopped. But its signature is
// exact and observable: the call does not come back. So this does the dangerous
// thing on purpose, with a deadline, and reports a timeout as the failure it
// is. If the guard were removed and a future build read own titles with
// GetWindowTextW while its UI thread was busy, this is what would catch it.

import (
	"strings"
	"time"
)

func runEnumSelftest(check func(name string, ok bool, detail string)) {

	// InternalGetWindowText is what makes reading our own caption safe. Without
	// it windowText returns "" for own windows - which is harmless, but means
	// the timing check below proves less than it looks like it does. Say so.
	check("deadlock: InternalGetWindowText is available for own-window titles",
		internalTextAvailable,
		"not found in user32 - own-window titles will read as empty. Not dangerous, "+
			"but the timing check below is then weaker than it appears")

	// THE DANGEROUS THING, ON PURPOSE, WITH A DEADLINE.
	//
	// Enumerate everything and read every title, our own included. Under the
	// bug this never returns.
	type result struct {
		total int
		own   int
		names []string
	}
	done := make(chan result, 1)
	go func() {
		var r result
		var hs []HWND
		EnumTopWindows(func(h HWND) bool {
			hs = append(hs, h)
			return true
		})
		r.total = len(hs)
		for _, h := range hs {
			if isOwnWindow(h) {
				r.own++
				r.names = append(r.names, windowClass(h))
			}
			// The call that used to hang. Deliberately made for every window.
			_ = windowText(h)
		}
		done <- r
	}()

	var r result
	timedOut := false
	select {
	case r = <-done:
	case <-time.After(10 * time.Second):
		timedOut = true
	}

	check("deadlock: reading every window's title, including our own, RETURNS",
		!timedOut,
		"the enumeration did not finish in 10s - this is the exact signature of the "+
			"WM_GETTEXT deadlock that killed two sessions on 2026-08-08")

	if timedOut {
		// Everything below reads from r, which was never filled.
		return
	}

	// NEGATIVE CONTROL. If the enumeration returned nothing, the check above
	// passed by doing no work at all.
	check("NEGATIVE CONTROL: the enumeration actually saw windows",
		r.total > 0,
		"saw "+itoaSmall(r.total)+" windows - zero would make the timing check vacuous")

	// Own windows must now be VISIBLE to callers - the opposite of what this
	// file used to assert, and the reason the process-lock decoy works again.
	//
	// Not a hard failure when zero: in --selftest there may genuinely be no
	// top-level window of ours yet. Reported either way so the difference
	// between "proved" and "not exercised" is on the record rather than
	// inferred from a green tick.
	if r.own > 0 {
		check("deadlock: our own windows ARE handed to callers again",
			true, "saw "+itoaSmall(r.own)+" own window(s): "+strings.Join(r.names, ", "))
	} else {
		check("deadlock: own-window path exercised",
			true, "NOT EXERCISED - this process had no top-level window during the "+
				"selftest, so the own-window branch of windowText was not reached here. "+
				"The process-lock decoy covers it.")
	}

	// The callback table must not have grown - the original 14-minute crash was
	// syscall.NewCallback exhaustion, and every fix since has to stay clear of it.
	check("deadlock: the fix did not add a syscall callback",
		callbacksAllocated() == 1,
		"one package-scope callback, as before")

	// findGameWindow must still work through the enumeration.
	_, err := findGameWindow(false, "")
	check("deadlock: findGameWindow still runs to completion",
		true, "returned without hanging: "+errText(err))
}
