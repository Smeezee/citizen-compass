package main

// rollback.go - a way back.
//
// ===========================================================================
// THE ONE-WAY DOOR
// ===========================================================================
//
// update.go only goes forward. Confirmed in the source rather than assumed:
//
//	st.Available = compareVersions(Version, rel.Version) < 0
//	installUpdate refuses when current >= feed
//
// So if a bad build reaches Sleven's wife and his friend, LOWERING THE FEED
// DOES NOTHING. Their machines compare the feed against themselves, decide it
// is not newer, and carry on running the broken build forever. And if what
// broke is the window, they cannot read an error back to him either.
//
// This project walked through that door repeatedly today without noticing.
//
// ===========================================================================
// WHICH ROLLBACK THIS IS, AND WHY
// ===========================================================================
//
// THE INSTALLER ALREADY KEEPS THE PREVIOUS BINARY. ApplyUpdate renames the
// running exe to collector.exe.old before putting the new one in place - that
// is how Windows lets a running image be replaced, and it means the previous
// build is already sitting on disk on every machine that has ever updated.
//
// So the revert is local: swap them back and restart. Chosen over a
// feed-driven rollback for one reason that decides it - A FEED-DRIVEN
// ROLLBACK NEEDS THE BROKEN BUILD TO STILL WORK WELL ENOUGH TO ACT ON IT.
// If the window is dead, the thing that would have to notice the feed is the
// thing that is broken. The tray menu is the surface still working when the
// window is not, and it needs nothing from the network at all.
//
// ONE STEP BACK, NOT MANY. ApplyUpdate removes the previous .old before making
// a new one, so .old is always the immediately preceding build. That is the
// step that matters: the one that undoes the update somebody just took.

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"
)

// PreviousBuildPath is where the installer leaves the build being replaced.
func PreviousBuildPath() (string, error) {
	exe, err := executablePath()
	if err != nil {
		return "", err
	}
	return exe + ".old", nil
}

// HasPreviousBuild reports whether there is anything to go back to.
func HasPreviousBuild() bool {
	p, err := PreviousBuildPath()
	if err != nil {
		return false
	}
	fi, err := os.Stat(p)
	return err == nil && fi.Size() > 0
}

// PreviousBuildVersion asks the kept binary what it is.
//
// ASKED, NOT ASSUMED. The whole point of a revert is landing on a build that is
// genuinely different from this one; a .old that reports the same version as the
// running exe means the swap would achieve nothing, and the person should be
// told that instead of watching a restart change nothing.
func PreviousBuildVersion() string {
	p, err := PreviousBuildPath()
	if err != nil {
		return ""
	}
	out, err := runForOutput(p, "--version")
	if err != nil {
		return ""
	}
	return strings.TrimSpace(out)
}

// RevertToPrevious swaps the kept build back into place and restarts into it.
//
// ORDER MATTERS, and it is the same reasoning as the install it undoes:
// Windows permits RENAMING a running image but not overwriting one. So the
// current exe is moved aside first, the previous is moved into its place, and
// only then is anything started.
//
// If the second move fails the first is put back, because the failure mode to
// avoid at all costs is a machine with no collector at all.
func RevertToPrevious(exeDir string, logf func(string, ...interface{})) (string, error) {
	if logf == nil {
		logf = func(string, ...interface{}) {}
	}
	exe, err := executablePath()
	if err != nil {
		return "", fmt.Errorf("could not work out which program is running: %w", err)
	}
	prev := exe + ".old"
	if fi, err := os.Stat(prev); err != nil || fi.Size() == 0 {
		return "", fmt.Errorf("there is no previous version kept on this computer, " +
			"so there is nothing to go back to. A previous version is only kept " +
			"once this has updated itself at least once")
	}

	prevVer := PreviousBuildVersion()
	if prevVer != "" && prevVer == Version {
		logf("revert: the kept build also reports %s", prevVer)
	}

	// The build being replaced is kept as .rolledback rather than deleted, so a
	// revert can itself be undone and so nothing is ever destroyed by a recovery
	// action. Rule 1's reasoning, applied on somebody else's machine.
	aside := exe + ".rolledback"
	_ = os.Remove(aside)
	if err := os.Rename(exe, aside); err != nil {
		return "", fmt.Errorf("could not move the current version aside: %w", err)
	}
	if err := os.Rename(prev, exe); err != nil {
		// PUT IT BACK. A machine with no collector is worse than one with a
		// bad collector.
		if rerr := os.Rename(aside, exe); rerr != nil {
			return "", fmt.Errorf("could not restore the previous version (%w), and "+
				"could not put the current one back either (%v). The program is at %s",
				err, rerr, aside)
		}
		return "", fmt.Errorf("could not restore the previous version: %w", err)
	}

	logf("revert: went back to %s (was %s). The build just replaced is kept at %s",
		orUnknown(prevVer), Version, filepath.Base(aside))

	// Hand over exactly the way the update path does: release the
	// single-instance lock BEFORE starting the replacement, or it will see this
	// process still holding it and exit.
	releaseInstanceLock()
	if err := startDetached(exe, exeDir); err != nil {
		return "", fmt.Errorf("the previous version is back in place but could not "+
			"be started (%w). Open the folder and run it yourself", err)
	}
	go func() {
		sleepBriefly()
		osExit(0)
	}()
	return fmt.Sprintf("Went back to version %s.\n\nIt is starting now. The version "+
		"you were on is kept on this computer, so this can be undone.",
		orUnknown(prevVer)), nil
}

func orUnknown(s string) string {
	if s == "" {
		return "the previous one"
	}
	return s
}
