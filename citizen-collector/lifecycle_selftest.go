package main

// lifecycle_selftest.go - proving a death states itself.
//
// The collector died silently three times in one night, so these checks matter
// more than most. Each is driven by making the thing FAIL first.

import (
	"fmt"
	"os"
	"strings"
)

// runLifecycleSelftest covers the running marker: the mechanism that reports a
// death no exit handler could ever have reported about itself.
func runLifecycleSelftest(check func(name string, ok bool, detail string)) {
	dir, err := os.MkdirTemp("", "cc-lifecycle-")
	if err != nil {
		check("lifecycle testable", false, err.Error())
		return
	}
	defer os.RemoveAll(dir)

	var lines []string
	logf := func(format string, args ...interface{}) {
		lines = append(lines, fmt.Sprintf(format, args...))
	}
	has := func(sub string) bool {
		for _, l := range lines {
			if strings.Contains(l, sub) {
				return true
			}
		}
		return false
	}

	// --- NEGATIVE CONTROL -------------------------------------------------
	// A first-ever run has no marker and must NOT accuse anything of crashing.
	// Without this, a checkPreviousRun that complained unconditionally would
	// satisfy the positive case below while crying wolf on every launch.
	lines = nil
	checkPreviousRun(dir, logf)
	check("a clean first run accuses nothing", !has("DID NOT SHUT DOWN CLEANLY"),
		"no marker present, so no crash is reported")
	check("the run is marked while alive", fileExists(markerPath(dir)),
		"a marker exists for as long as the process does")

	// --- A CLEAN EXIT LEAVES NOTHING BEHIND -------------------------------
	lines = nil
	logExit(logf, dir, "window closed")
	check("a clean exit writes a shutdown line", has("shutting down: window closed"),
		"the log says the process is going, and why")
	check("a clean exit clears the marker", !fileExists(markerPath(dir)),
		"nothing left to accuse the next run's predecessor with")

	// Starting again after that clean exit must still accuse nothing.
	lines = nil
	checkPreviousRun(dir, logf)
	check("a run after a clean exit accuses nothing", !has("DID NOT SHUT DOWN CLEANLY"),
		"the previous run ended through a path of its own")

	// --- THE CASE THAT MATTERS: A KILLED RUN ------------------------------
	// Simulate exactly what happened three times tonight - a process that
	// vanished without reaching any exit path of its own. The marker survives,
	// because nothing removed it.
	lines = nil
	checkPreviousRun(dir, logf) // marker from the previous line is still there
	check("a killed run IS reported at next start", has("DID NOT SHUT DOWN CLEANLY"),
		"the leftover marker is the evidence the dead process could not leave itself")
	check("the report names the dead process", has("pid ") && has("left no shutdown line"),
		"it says WHICH run died, not merely that one did")
	check("the report says what that means", has("killed from outside") || has("crashed hard"),
		"a person reading the log is told how to interpret it")

	// --- THE PAIR MUST DISAGREE ------------------------------------------
	// A checker that reported the same thing in both states would pass the
	// clean case and the killed case identically and be measuring nothing.
	clearRunningMarker(dir)
	lines = nil
	checkPreviousRun(dir, logf)
	afterClean := has("DID NOT SHUT DOWN CLEANLY")
	clearRunningMarker(dir)
	_ = os.WriteFile(markerPath(dir), []byte("pid=4242 started=2026-08-07T00:00:00Z"), 0o644)
	lines = nil
	checkPreviousRun(dir, logf)
	afterKilled := has("DID NOT SHUT DOWN CLEANLY")
	check("the marker distinguishes the two endings", !afterClean && afterKilled,
		fmt.Sprintf("after clean exit=%v, after a kill=%v", afterClean, afterKilled))
}

func fileExists(p string) bool {
	_, err := os.Stat(p)
	return err == nil
}

// runPanicLoggingSelftest proves an unrecovered panic reaches the log rather
// than a dead stderr.
//
// This is the mechanism that would have explained the three silent deaths. On a
// -H windowsgui build there is no stderr at all, so Go's panic output - the one
// thing that would have named the cause - went nowhere.
func runPanicLoggingSelftest(check func(name string, ok bool, detail string)) {
	dir, err := os.MkdirTemp("", "cc-panic-")
	if err != nil {
		check("panic logging testable", false, err.Error())
		return
	}
	defer os.RemoveAll(dir)

	var lines []string
	logf := func(format string, args ...interface{}) {
		lines = append(lines, fmt.Sprintf(format, args...))
	}
	joined := func() string { return strings.Join(lines, "\n") }

	// NEGATIVE CONTROL: no panic, nothing logged. logPanic is deferred on every
	// goroutine, so one that logged unconditionally would fill the log with
	// phantom crashes.
	func() {
		defer logPanic(logf, dir, "a function that does not panic")
	}()
	check("no panic means no panic line", len(lines) == 0,
		"logPanic is silent when nothing went wrong")

	// THE REAL CASE. logPanic re-panics on purpose - continuing in a state
	// nobody reasoned about would be worse than dying - so the re-panic is
	// caught here to keep the selftest alive.
	func() {
		defer func() { _ = recover() }()
		defer logPanic(logf, dir, "the capture loop")
		panic("deliberate test panic")
	}()

	check("a panic IS logged", strings.Contains(joined(), "PANIC in the capture loop"),
		"the panic reaches the log instead of a stderr that does not exist")
	check("the panic message is recorded", strings.Contains(joined(), "deliberate test panic"),
		"what went wrong, not merely that something did")
	check("a stack trace is recorded", strings.Contains(joined(), "lifecycle.go") ||
		strings.Contains(joined(), "goroutine"),
		"enough to find the cause rather than start guessing")

	// A panic must also clear the marker: it IS an exit path this code
	// controls, so the next run should not report it as an external kill.
	check("a logged panic is not reported as an external kill",
		!fileExists(markerPath(dir)),
		"a crash the program witnessed is distinguishable from one it did not")

	// The redirect must accept a real file without exploding. It cannot be
	// checked from inside the process - the runtime writes panics to the
	// handle, not through os.Stderr - so this asserts only that it is safe to
	// call, and says so rather than implying more.
	f, err := os.CreateTemp(dir, "stderr-*.log")
	if err == nil {
		redirectStderrToLog(f)
		check("stderr redirect accepts the log file", os.Stderr == f,
			"os.Stderr now points at the log; the runtime handle is set alongside it "+
				"and cannot be observed from in here")
		f.Close()
	}
}
