//go:build master

package main

// variant_master.go - the master build (WO-COLLECT-01 rev 5 addendum, 2026-08-06).
//
// Built with:   go build -tags master -o collector-master.exe .
//
// Sleven only. Everything the crew build does, plus calibration, zone tuning,
// the review pen, and "Generate crew package".
//
// STATUS: this file is the build-flag split ONLY. None of the master features
// exist yet, and this file does not pretend they do.
//
// WHY THEY ARE NOT HERE YET
//   The grabber (rev 5 sec 5.1) is scoped "NO OCR. No atlas. No vocabulary. No
//   zones." Calibration, zone tuning and the review pen are all part of the
//   reading half, which is gated on the legibility question this very binary
//   was built to answer.
//
//   Generate crew package is blocked on its own payload: of the seven files it
//   must assemble, only names.dat can be built today. atlas\, zones.json and
//   profiles.json are all downstream of calibration. A generator written now
//   would assert against a payload it cannot produce, and its verify step would
//   report PASS having checked nothing - the exact silent-success shape that
//   hard rule 12 exists to prevent.
//
// The split lands now because it is structural and cheap now; the features land
// when their inputs exist.

import "flag"

const BuildVariant = "master"

// defaultShowWindow is TRUE for the master build.
//
// Sleven is working ON this, not merely running it, so the window is the point
// rather than an interruption. Same window as the crew build, different default
// - see window.go. One implementation.
const defaultShowWindow = true

// registerBenchFlags defines the bench-testing flags. They exist ONLY here.
//
// --allow-any-window lifts the StarCitizen.exe process restriction so the
// capture backends can be exercised against an ordinary window. That is how the
// three backends were proven in the first place - there is no way to test a
// screen-capture tool against a game that is not running without it.
//
// --window is a title HINT used to choose among candidate windows. It is not
// authority to capture: without --allow-any-window it can only narrow the set
// of StarCitizen.exe windows, never widen it to another process.
func registerBenchFlags() func() (allowAny bool, windowHint string) {
	allow := flag.Bool("allow-any-window", false,
		"MASTER ONLY: lift the StarCitizen.exe process restriction (bench testing)")
	win := flag.String("window", "",
		"title hint used to choose among candidate windows; not authority to capture")
	return func() (bool, string) { return *allow, *win }
}

func masterOnlyCommands() map[string]func() int {
	return map[string]func() int{
		// "generate-package": generateCrewPackage,  // blocked - see above
		// "calibrate":        runCalibration,       // blocked - reading half
	}
}

// runVariantSelftests runs the controls that only exist in this build.
//
// Q45's pair store is master-only by Sleven's ruling of 2026-08-30: the
// learning half does not ship to crew. The crew copy of this function is empty
// and pairstore.go is not compiled into that binary at all, so there is no
// symbol to find and no folder to wonder about.
func runVariantSelftests(check func(name string, ok bool, detail string)) {
	runPairStoreSelftest(check)
}
