package main

// autostart.go - it comes up with the machine and waits for the game.
//
// ===========================================================================
// WHY THIS IS A PER-USER STARTUP ENTRY AND NOT A WINDOWS SERVICE
// ===========================================================================
//
// Sleven's ruling, 2026-08-15. This AMENDS the standing "long-running
// components run as real background services" rule FOR THIS COMPONENT ONLY.
// Recorded here, and in docs/ARCHITECTURE_DECISIONS.md, so that nobody
// "corrects" it back to a service later on the strength of the general rule.
//
// THE TECHNICAL REASON, which is the one that settles it:
//
//	A Windows service runs in session 0, isolated from the desktop since Vista.
//	It has no window station and no desktop of its own. This program takes
//	pictures of the Star Citizen window and shows a window to the person using
//	it. A service COULD NOT CAPTURE THE SCREEN and COULD NOT SHOW THE WINDOW.
//	The general rule and this component's whole purpose are in direct conflict,
//	and the purpose wins.
//
// THE HUMAN REASON, which matters just as much:
//
//	A service needs admin to install, does not appear in the Startup tab an
//	ordinary person can reach, and is removed with `sc delete` from an elevated
//	prompt. The order requires removal to be "one obvious action, not registry
//	surgery". A service cannot satisfy both that and "survives reboot".
//
// A shortcut in the per-user Startup folder satisfies every requirement:
// starts at login, silent, no console window, survives reboot - and is removed
// by deleting one file, or by one toggle in Task Manager -> Startup, with no
// admin rights either way. It also cannot outlive the user profile it belongs
// to, which matters on a shared family machine.
//
// NOT the registry Run key, though it would also work: a file in a folder is
// something a person can SEE. That is the whole difference between a program
// you can get rid of and one you have to look up how to get rid of.

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"time"
)

// FOLDERID_Startup - the per-user startup folder. Resolved, never built from
// %APPDATA%, for the same reason every other folder here is resolved.
var folderIDStartup = GUID{0xB97D20BB, 0xF46A, 0x4C97, [8]byte{0xBA, 0x10, 0x5E, 0x36, 0x08, 0x43, 0x08, 0x54}}

const autostartLinkName = "Citizen Collector (starts with Windows)"

// autostartPath is where the startup shortcut lives, or "" if the folder
// cannot be resolved.
// autostartDirOverride lets a check prove the startup entry is really removed
// without writing to somebody's real Startup folder.
//
// EMPTY IN EVERY REAL RUN. Hard rule 6 says I ask before writing outside the
// repo, and "the uninstaller takes the startup entry with it" is the single
// requirement of the install work that MUST be proved by effect - so the effect
// is produced somewhere disposable rather than left unproven.
var autostartDirOverride string

func autostartPath() string {
	if autostartDirOverride != "" {
		return filepath.Join(autostartDirOverride, autostartLinkName+".lnk")
	}
	dir, err := knownFolder(folderIDStartup)
	if err != nil || dir == "" {
		return ""
	}
	return filepath.Join(dir, autostartLinkName+".lnk")
}

// AutostartEnabled reports whether the startup entry is in place.
func AutostartEnabled() bool {
	p := autostartPath()
	if p == "" {
		return false
	}
	_, err := os.Stat(p)
	return err == nil
}

// EnableAutostart writes the startup shortcut, pointed at the watcher.
//
// The shortcut runs `collector.exe -watch`, not the collector itself. Starting
// the whole program at login would put a window in somebody's face every
// morning whether or not they intended to play; the watcher sits quiet and
// starts the collector when the game appears.
func EnableAutostart(exe, workDir string) error {
	p := autostartPath()
	if p == "" {
		return fmt.Errorf("your Startup folder could not be found, so it cannot start with Windows")
	}
	return CreateShortcutWithArgs(p, exe, workDir,
		"Waits for Star Citizen and starts the collector. Delete this file to stop it.",
		exe, "-watch")
}

// DisableAutostart removes the startup entry.
//
// os.Remove on a shortcut THIS program created in a folder whose only purpose
// is holding them. Not a data file, and not something the person put there -
// and turning it off has to be as easy as turning it on or it is not really
// optional.
func DisableAutostart() error {
	p := autostartPath()
	if p == "" {
		return nil
	}
	if err := os.Remove(p); err != nil && !os.IsNotExist(err) {
		return err
	}
	return nil
}

// AutostartRemovalInstructions is what the window tells a person who wants it
// gone, in words that do not assume they know what a shortcut is.
func AutostartRemovalInstructions() string {
	p := autostartPath()
	if p == "" {
		p = "your Startup folder"
	}
	return "To stop it starting with Windows: use the switch in this window, or " +
		"open Task Manager, go to the Startup tab and turn off \"" + autostartLinkName +
		"\", or simply delete this file:\n\n    " + p +
		"\n\nNo administrator rights are needed for any of those, and deleting the " +
		"folder this program lives in removes everything either way."
}

// ---------------------------------------------------------------------------
// THE WATCHER
// ---------------------------------------------------------------------------

// watchPollInterval is how often the watcher looks for the game.
//
// IDLE COST IS THE WHOLE DESIGN CONSTRAINT. This sits on a gaming machine
// forever. Fifteen seconds is far tighter than it needs to be - a session lasts
// hours - and one process enumeration at that cadence is unmeasurable against
// a machine running a game. Polling every second would be the same answer,
// arrived at sixty times as often.
const watchPollInterval = 15 * time.Second

// watcherMutex is DELIBERATELY NOT the collector's single-instance mutex.
//
// The watcher and the collector are different programs that happen to share an
// executable. If the watcher claimed the collector's lock, the collector it
// started would see "already running" and exit - which is the restart-handover
// defect from 2026-08-14 rebuilt on purpose. One watcher, one collector, two
// separate locks.
const watcherMutex = "Local\\CitizenCollector.Watcher"

// RunWatcher is `collector.exe -watch`: wait for the game, start the collector,
// and otherwise do nothing at all.
//
// # ON A MACHINE THAT NEVER RUNS STAR CITIZEN
//
// It must sit quiet and harmless, not log an error every fifteen seconds for a
// year. So the watcher logs when its state CHANGES and never when it does not:
// one line at startup, one when the game appears, one when it goes. A quiet
// machine produces a log file that stops growing.
func RunWatcher(exeDir string, logf func(string, ...interface{})) {
	if logf == nil {
		logf = func(string, ...interface{}) {}
	}

	// ONE WATCHER. Two of them would start two collectors, and the second would
	// yield and exit - noisy, pointless, and exactly the shape rule 14 exists
	// to prevent.
	if alreadyRunningNamed(watcherMutex) {
		logf("watcher: another watcher is already running - this one is exiting")
		return
	}

	exe, err := os.Executable()
	if err != nil {
		logf("watcher: cannot find my own path (%v) - not starting", err)
		return
	}

	logf("watcher: started. Waiting for Star Citizen; nothing else happens until "+
		"it appears. Checking every %s.", watchPollInterval)

	wasRunning := false
	for {
		running := gameProcessIsRunning()

		switch {
		case running && !wasRunning:
			// THE EDGE, not the state. Starting the collector on every poll
			// while the game is up would launch it hundreds of times a session
			// and lean entirely on the single-instance guard to clean up after.
			logf("watcher: Star Citizen started - launching the collector")
			if err := startDetached(exe, exeDir); err != nil {
				logf("watcher: could not start the collector (%v)", err)
			}
		case !running && wasRunning:
			logf("watcher: Star Citizen closed. The collector handles the rest.")
		}
		wasRunning = running

		time.Sleep(watchPollInterval)
	}
}

// gameProcessIsRunning reports whether Star Citizen is up.
//
// By PROCESS IMAGE NAME, never by window title. This project learned that in
// findGameWindow, where matching on a title picked the project's own terminal
// as "Star Citizen". The launcher counts too: somebody who has opened the
// launcher is about to play, and starting the collector then means it is ready
// rather than racing the game.
func gameProcessIsRunning() bool {
	for _, name := range []string{"starcitizen.exe", "rsi launcher.exe"} {
		if processRunningByName(name) {
			return true
		}
	}
	return false
}

// processRunningByName walks the top-level windows and asks what owns them.
//
// Uses the enumeration this program already has rather than adding a
// Toolhelp32 snapshot: a game and a launcher both have windows, and reusing the
// existing path means one thing to be wrong rather than two.
func processRunningByName(want string) bool {
	found := false
	EnumTopWindows(func(h HWND) bool {
		if found {
			return false
		}
		if strings.EqualFold(filepath.Base(processImageName(windowPID(h))), want) {
			found = true
			return false
		}
		return true
	})
	return found
}
