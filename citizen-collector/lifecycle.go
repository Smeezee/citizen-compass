package main

// lifecycle.go - a death must state itself.
//
// THE DEFECT
//
// The collector died silently three times in one night. The log ended
// mid-normal-operation - a routine capture, a normal heartbeat cadence, then
// nothing. No error, no window, no line saying it was going. A crash and a
// clean exit produced identical evidence.
//
// That is this project's oldest defect one level up. The heartbeat proved the
// process had STOPPED, which was a real improvement - but only to someone
// reading the log, and the whole point of the window is that nobody should have
// to.
//
// WHY A PANIC LEFT NOTHING AT ALL
//
// The program is built -H windowsgui (§4.2, never a console). Such a process
// has NO stderr. Go's runtime writes an unrecovered panic and its stack to
// stderr, so on a GUI build that output goes to a closed handle and is lost
// completely. The most likely cause of a silent death was also the one
// guaranteed to leave no trace.
//
// THREE MECHANISMS HERE
//
//  1. redirectStderrToLog - point the process's real stderr HANDLE at the log
//     file, so even a panic in a goroutine nobody wrapped lands in the log.
//  2. logExit - a shutdown line on every path this code controls.
//  3. the running marker - a file that exists only while the process is alive.
//     If it is still there at startup, the previous run did NOT exit through
//     any path of its own, which means it was killed or it crashed hard. That
//     is the one thing an exit handler can never report about itself.

import (
	"fmt"
	"os"
	"path/filepath"
	"runtime/debug"
	"strconv"
	"strings"
	"time"
)

const (
	// STD_ERROR_HANDLE is (DWORD)-12.
	stdErrorHandle = 0xFFFFFFF4
	runningMarker  = "collector-running.marker"
)

var procSetStdHandle = modKernel32.NewProc("SetStdHandle")

// redirectStderrToLog makes the runtime's panic output land in the log file.
//
// Both halves are needed. os.Stderr covers Go code that writes to it; the
// SetStdHandle call covers the RUNTIME, which writes panics using the process's
// stderr handle directly and would otherwise still be writing into the void.
func redirectStderrToLog(f *os.File) {
	if f == nil {
		return
	}
	os.Stderr = f
	procSetStdHandle.Call(uintptr(stdErrorHandle), f.Fd())
}

// markerPath is where the running marker lives.
func markerPath(exeDir string) string { return filepath.Join(exeDir, runningMarker) }

// checkPreviousRun reports how the LAST run ended, and starts marking this one.
//
// Returns a sentence for the log, or "" when the previous run ended cleanly.
//
// The marker holds the pid and the start time, so a report can say WHICH run
// died rather than merely that one did.
func checkPreviousRun(exeDir string, logf func(string, ...interface{})) {
	p := markerPath(exeDir)

	if b, err := os.ReadFile(p); err == nil {
		prev := strings.TrimSpace(string(b))
		pid, when := parseMarker(prev)

		// ASK WHETHER THAT PID IS STILL ALIVE before saying what happened.
		//
		// A marker naming a LIVE process and one naming a dead process describe
		// opposite situations - a second copy running right now, versus a
		// previous one that died - and this used to report them identically.
		//
		// pidIsLiveSibling also checks the image name, so a pid Windows has
		// recycled for some unrelated program is correctly read as "gone"
		// rather than as a collector that is somehow still here.
		switch {
		case pid != 0 && pidIsLiveSibling(pid):
			logf("A COLLECTOR IS ALREADY RUNNING as pid %d, started %s.", pid, when)
			logf("    That process is alive right now, so this is not a leftover " +
				"from a crash. If you did not mean to open a second one, close this window.")
		case pid != 0:
			logf("PREVIOUS RUN DID NOT SHUT DOWN CLEANLY.")
			logf("    It was pid %d, started %s, and left no shutdown line. That "+
				"process is NOT running now - checked, not assumed.", pid, when)
			logf("    So it was killed from outside (Task Manager, a script, " +
				"sign-out) or it crashed hard. A clean exit always writes one.")
			logf("    The stale marker has been cleared. It never blocked startup, " +
				"and it is not blocking this one.")
		default:
			logf("PREVIOUS RUN DID NOT SHUT DOWN CLEANLY, and its marker names no " +
				"readable pid, so which run it was cannot be established.")
		}
	}

	// Claim this run.
	_ = os.WriteFile(p,
		[]byte(fmt.Sprintf("pid=%d started=%s", os.Getpid(), time.Now().Format(time.RFC3339))),
		0o644)
}

func parseMarker(s string) (pid int, started string) {
	for _, part := range strings.Fields(s) {
		k, v, ok := strings.Cut(part, "=")
		if !ok {
			continue
		}
		switch k {
		case "pid":
			pid, _ = strconv.Atoi(v)
		case "started":
			started = v
		}
	}
	return pid, started
}

// clearRunningMarker records that this run ended through a path it controls.
func clearRunningMarker(exeDir string) {
	_ = os.Remove(markerPath(exeDir))
}

// logExit writes the shutdown line. Called from every exit path.
//
// why is a short phrase - "window closed", "restarting", "panic" - so the log
// distinguishes the ways a run can end instead of only recording that it did.
func logExit(logf func(string, ...interface{}), exeDir, why string) {
	logf("---- shutting down: %s ----", why)
	clearRunningMarker(exeDir)
}

// logPanic records a panic with its stack and then re-panics.
//
// Deferred at the top of every goroutine this program starts. Recovering and
// CONTINUING would be worse than dying: the process would carry on in a state
// its author never reasoned about. So the panic is recorded and then allowed to
// proceed - the point is evidence, not survival at any cost.
func logPanic(logf func(string, ...interface{}), exeDir, where string) {
	r := recover()
	if r == nil {
		return
	}
	logf("---- PANIC in %s: %v ----", where, r)
	for _, line := range strings.Split(strings.TrimRight(string(debug.Stack()), "\n"), "\n") {
		logf("    %s", line)
	}
	clearRunningMarker(exeDir)
	panic(r)
}
