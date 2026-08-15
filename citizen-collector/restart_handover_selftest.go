package main

// restart_handover_selftest.go - the guard must refuse a real duplicate and
// must NOT refuse a handover.
//
// THE DEFECT THESE COVER
//
// Sleven updated to 0.3.0. The download, the checksum and the install were all
// correct. The restart was not:
//
//	23:05:29 restart: started ...collector-master.exe, this process is exiting
//	23:05:29 another collector is already running ... its window could not be
//	         found to raise. Look for collector-master.exe in Task Manager.
//
// Both lines in the same second. The process that had just launched its own
// replacement was still holding the single-instance lock, so the replacement
// saw "already running", found no window to raise because the launcher's had
// gone, and exited. Nothing was left running, and the message sent him to Task
// Manager to look for a process that was not there.
//
// The old code slept 1500ms before exiting, commented as "so the child is past
// its single-instance check before this one releases the lock". That is
// backwards - the child checks immediately, so the sleep only held the lock
// across the check. It did not prevent the race; it guaranteed losing it.
//
// WHAT IS ACTUALLY BEING TESTED
//
// Not the timing, which is a race and would make a flaky test. The two
// properties that make the race impossible:
//
//  1. Releasing the lock genuinely releases it, so a later check sees it free.
//  2. A liveness check answers "no" for a dead pid and for a recycled one, and
//     "yes" only for a live process running this same image.
//
// Every check below has a case that must fail it (hard rule 12).

import (
	"fmt"
	"os"
	"os/exec"
	"strings"
)

func runRestartHandoverSelftest(check func(name string, ok bool, detail string)) {
	// ----------------------------------------------------------------------
	// THE LOCK CAN BE RELEASED, AND RELEASING IT IS OBSERVABLE
	// ----------------------------------------------------------------------
	//
	// A test-only mutex name, never the product's: running this while a real
	// collector is open would otherwise make the guard correctly report
	// "already running" and fail the check for a reason unrelated to the guard.
	const testMutex = "Local\\CitizenCollector.SelfTest.Handover"

	saved := instanceLock
	instanceLock = 0

	first := alreadyRunningNamed(testMutex)
	check("an unheld lock reads as free", !first,
		"nothing holds the test mutex, so the first look must say so")
	check("looking at a free lock CLAIMS it", instanceLock != 0,
		"the handle is kept so the claim can be released deliberately later")

	// NEGATIVE CONTROL. While held, a second look must say it is taken -
	// otherwise the check above proves nothing and two collectors could run.
	held := alreadyRunningNamed(testMutex)
	check("a held lock reads as taken", held,
		"the claim is real - without this, the release check below is meaningless")

	// THE ONE THAT MATTERS. Asking a second time must not itself keep the lock
	// alive. The old code kept the handle CreateMutex returns even when the
	// object already existed, so once a process had looked it became a reason
	// for the answer to stay "yes" and could never see the owner let go.
	releaseInstanceLock()
	check("releasing the lock frees it", !alreadyRunningNamed(testMutex),
		"a handover must be observable, or the replacement refuses to start")
	releaseInstanceLock()

	instanceLock = saved

	// ----------------------------------------------------------------------
	// LIVENESS - a dead pid must not hold a launch hostage
	// ----------------------------------------------------------------------
	check("this process is a live sibling of itself", pidIsLiveSibling(os.Getpid()),
		"the check must say yes to a process that is genuinely running this exe")

	// A pid that cannot exist. NEGATIVE CONTROL for the line above: without it,
	// a function that returned true unconditionally would pass.
	check("an impossible pid is not alive", !pidIsLiveSibling(0x7FFFFFF0),
		"a dead pid must answer no, or a stale record blocks every launch")

	check("pid 0 is not alive", !pidIsLiveSibling(0),
		"an unparsed or missing pid must never read as a running collector")
	check("a negative pid is not alive", !pidIsLiveSibling(-1),
		"a malformed marker must not be read as a running collector")

	// PID RECYCLING. A live process that is NOT this executable must answer no.
	// Windows reuses pids, so "the number is in use" is not "the collector is
	// running" - answering on the number alone would refuse to start because
	// something unrelated inherited it.
	other := exec.Command("cmd.exe", "/c", "ping -n 4 127.0.0.1 >nul")
	if err := other.Start(); err == nil {
		otherPid := other.Process.Pid
		check("a live NON-collector pid is not a sibling", !pidIsLiveSibling(otherPid),
			"pids are recycled; identity is the image name, not the number")
		_ = other.Process.Kill()
		_, _ = other.Process.Wait()

		// And now that same pid is dead.
		check("a killed process is not a sibling", !pidIsLiveSibling(otherPid),
			"the check must notice a process that has gone")
	}

	// ----------------------------------------------------------------------
	// THE MARKER REPORT - reads the pid rather than assuming the worst
	// ----------------------------------------------------------------------
	dir, err := os.MkdirTemp("", "cc-handover")
	if err != nil {
		return
	}
	defer os.RemoveAll(dir)

	var lines []string
	logf := func(format string, args ...interface{}) {
		lines = append(lines, fmt.Sprintf(format, args...))
	}
	said := func(needle string) bool {
		for _, l := range lines {
			if strings.Contains(l, needle) {
				return true
			}
		}
		return false
	}

	// A marker naming a pid that is long gone.
	_ = os.WriteFile(markerPath(dir), []byte("pid=2147483632 started=2026-08-14T23:05:00Z"), 0o644)
	lines = nil
	checkPreviousRun(dir, logf)
	check("a dead pid is reported as not running", said("NOT running now"),
		"checked, not assumed - the old wording asserted a cause it had not established")
	check("a dead pid does not accuse a live collector", !said("ALREADY RUNNING"),
		"NEGATIVE CONTROL: the live branch must not fire for a dead process")

	// A marker naming a pid that IS alive and IS this executable.
	_ = os.WriteFile(markerPath(dir),
		[]byte(fmt.Sprintf("pid=%d started=2026-08-14T23:05:00Z", os.Getpid())), 0o644)
	lines = nil
	checkPreviousRun(dir, logf)
	check("a live pid is reported as already running", said("ALREADY RUNNING"),
		"a marker naming a live process describes a second copy, not a crash")
	check("a live pid is not called a crash", !said("DID NOT SHUT DOWN CLEANLY"),
		"NEGATIVE CONTROL: the crash branch must not fire for a running process")

	// The marker is always reclaimed for this run, whichever branch reported.
	b, _ := os.ReadFile(markerPath(dir))
	check("this run claims the marker", strings.Contains(string(b), fmt.Sprintf("pid=%d", os.Getpid())),
		"the marker must name the run that is alive now")

}
