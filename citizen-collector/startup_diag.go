package main

// startup_diag.go - state the environment before anything can go wrong in it.
//
// # WHY THIS IS WORTH A FILE
//
// The dead hotkey cost four wrong diagnoses and the better part of two days.
// Missing LockOSThread (it was already there). Exclusive fullscreen (he was
// borderless). Elevation mismatch (never checked). --auto never registering
// (it did).
//
// Every one of those would have been settled in ten seconds by a line at
// startup saying which renderer the game was using, whether the collector was
// elevated, and what the window actually was. The information was free the
// whole time and nobody wrote it down.
//
// The rule this encodes: a program that can cheaply state its own environment
// should do it BEFORE it is asked, because by the time somebody asks, the
// session that would have answered is over.

import (
	"os"
	"runtime"
	"syscall"
	"unsafe"
)

// isElevated reports whether this process is running as administrator.
//
// It matters for a specific, non-obvious reason: a normal-privilege process
// cannot receive input events from an elevated one. If Star Citizen is running
// elevated and the collector is not, a global hotkey registers successfully and
// then never fires - which is EXACTLY the symptom that was chased for two days.
func isElevated() (bool, error) {
	token, err := syscall.OpenCurrentProcessToken()
	if err != nil {
		return false, err
	}
	defer token.Close()

	var elevation uint32
	var outLen uint32
	const tokenElevation = 20
	err = syscall.GetTokenInformation(token, tokenElevation,
		(*byte)(unsafe.Pointer(&elevation)), uint32(unsafe.Sizeof(elevation)), &outLen)
	if err != nil {
		return false, err
	}
	return elevation != 0, nil
}

// LogStartupDiagnostics writes what the environment is, once, at startup.
//
// It never fails the run. Every value it cannot read is reported as unreadable
// rather than omitted, because a missing line and a line that says "could not
// determine" mean very different things to whoever is reading this at 2am.
func LogStartupDiagnostics(logf func(string, ...interface{}), exeDir string) {
	if logf == nil {
		return
	}
	logf("env: citizen-collector %s (%s), Go %s, %s/%s",
		Version, BuildVariant, runtime.Version(), runtime.GOOS, runtime.GOARCH)

	if elevated, err := isElevated(); err != nil {
		logf("env: could not determine whether this process is elevated (%v)", err)
	} else if elevated {
		logf("env: running ELEVATED (as administrator). If the game is NOT elevated, " +
			"that is fine. If the game IS elevated and this is not, global hotkeys " +
			"register and never fire - that exact mismatch cost two days in August.")
	} else {
		logf("env: running at normal privilege (not elevated)")

	// WINDOW OR CONSOLE, RECORDED RATHER THAN ASSERTED.
	//
	// A GUI-subsystem build (PE subsystem 2) gets no console from Windows, so
	// GetConsoleWindow returns 0 unless this process deliberately attached to a
	// parent's - which console.go does on purpose when run from a terminal.
	//
	// This program spent months claiming in seven files to be a GUI build while
	// both binaries were subsystem 3, which is why a black Windows Terminal
	// window appeared on every launch and why closing it killed the collector.
	// The comment was the defect. This is the observation.
	if hasConsole() {
		logf("env: a console IS attached to this process. If it was not started " +
			"from a terminal, this binary was built without -H=windowsgui and " +
			"Windows opened a console for it - closing that window kills the collector.")
	} else {
		logf("env: no console window (GUI build, as intended)")
	}
	}

	if wd, err := os.Getwd(); err == nil {
		logf("env: working directory %s", wd)
	}
	logf("env: program directory %s", exeDir)

	// The game window, if it is up, and what it actually is. This is the line
	// that would have ended the hotkey investigation on day one.
	if win, err := findGameWindow(false, ""); err == nil {
		logf("env: game window %q, class %q, exe %s, rect %dx%d, found by %s",
			win.Title, win.Class, win.Exe, win.Rect.Width(), win.Rect.Height(), win.How)

		fg := GetForegroundWindowHandle()
		logf("env: the game %s the foreground window at startup",
			map[bool]string{true: "IS", false: "is NOT"}[fg == win.H])

		// The renderer is stated in the game's own log. It decides whether the
		// message-based hotkey path can work at all: on Vulkan it registers and
		// never delivers, on DX11 it delivers every press.
		logPath, how := FindGameLog(win.H)
		if logPath != "" {
			gl := ReadGameLog(logPath, how)
			if gl.Patch != nil {
				logf("env: game patch %s (%s)", *gl.Patch, gl.PatchSrc)
			}
			logf("env: renderer/display mode are read from Game.log as the session " +
				"runs; the miner records them alongside every row")
		} else {
			logf("env: no Game.log located yet (%s)", how)
		}
	} else {
		logf("env: no game window at startup (%v) - this is normal if Star Citizen "+
			"is not running yet", err)
	}
}

