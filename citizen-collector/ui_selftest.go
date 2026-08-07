package main

// ui_selftest.go - WO-UI-01 §10. Each check must be able to fail.
//
// The two tests written against START and the version selector are gone; those
// controls no longer exist. These are their replacements, plus the retained
// ones that still apply.

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"
)

// runUIDetectSelftest covers §10's auto-detect requirement:
//
//	"point at a PTU install, assert the displayed name AND the watched path
//	 both contain PTU. Repeat for LIVE. A detector that does not change the
//	 path is decoration."
//
// The last sentence is the important one, so the two results are compared
// against each other rather than only checked individually.
func runUIDetectSelftest(check func(name string, ok bool, detail string)) {
	dir, err := os.MkdirTemp("", "cc-ui-detect-")
	if err != nil {
		check("detect testable", false, err.Error())
		return
	}
	defer os.RemoveAll(dir)

	base := `C:\Program Files\Roberts Space Industries\StarCitizen`
	ptu := base + `\PTU\Game.log`
	live := base + `\LIVE\Game.log`

	mk := func(logPath string) uiDeps {
		return uiDeps{
			gameAlive: func() error { return nil },
			findLog:   func() (string, string) { return logPath, "derived from the running game" },
			outDir:    dir,
			autoLog:   filepath.Join(dir, "collector-auto.log"),
		}
	}

	sPTU := buildUIState(mk(ptu))
	check("PTU: watched path contains PTU", strings.Contains(strings.ToUpper(sPTU.LogPath), `\PTU\`),
		"watching "+sPTU.LogPath)
	check("PTU: displayed name says PTU", sPTU.Install == "PTU",
		fmt.Sprintf("install reported as %q", sPTU.Install))
	check("PTU: the headline names it", strings.Contains(sPTU.Headline, "PTU"),
		fmt.Sprintf("headline %q", sPTU.Headline))

	sLIVE := buildUIState(mk(live))
	check("LIVE: watched path contains LIVE", strings.Contains(strings.ToUpper(sLIVE.LogPath), `\LIVE\`),
		"watching "+sLIVE.LogPath)
	check("LIVE: displayed name says LIVE", sLIVE.Install == "LIVE",
		fmt.Sprintf("install reported as %q", sLIVE.Install))

	// THE ONE THAT MAKES THE PAIR MEAN ANYTHING. A detector wired to a constant
	// would pass both halves above and still be decoration.
	check("the detector actually CHANGES the answer",
		sPTU.LogPath != sLIVE.LogPath && sPTU.Install != sLIVE.Install,
		fmt.Sprintf("PTU -> %q, LIVE -> %q", sPTU.Install, sLIVE.Install))

	// And the channel parser must not simply match any path containing the word.
	check("a path with no channel reports none",
		installChannelFromPath(`C:\somewhere\else\Game.log`) == "",
		"an unrecognised layout yields no install name rather than a guess")
}

// runUIFollowsGameSelftest covers §10's "follows the game" and the retained
// kill-the-process test, which are the same measurement from two directions:
// the headline must track whether a game window exists RIGHT NOW.
func runUIFollowsGameSelftest(check func(name string, ok bool, detail string)) {
	dir, err := os.MkdirTemp("", "cc-ui-follow-")
	if err != nil {
		check("follow testable", false, err.Error())
		return
	}
	defer os.RemoveAll(dir)

	alive := true
	d := uiDeps{
		gameAlive: func() error {
			if alive {
				return nil
			}
			return fmt.Errorf("no game window")
		},
		findLog: func() (string, string) {
			return `C:\Program Files\Roberts Space Industries\StarCitizen\LIVE\Game.log`, "test"
		},
		outDir:  dir,
		autoLog: filepath.Join(dir, "collector-auto.log"),
	}

	// NEGATIVE CONTROL of the pair: alive means collecting.
	s := buildUIState(d)
	check("game present -> COLLECTING", s.Collecting && strings.Contains(s.Headline, "Collecting"),
		fmt.Sprintf("headline %q", s.Headline))

	// The game goes away with nobody touching the program.
	alive = false
	s = buildUIState(d)
	check("game gone -> STOPPED, untouched", !s.Collecting && strings.Contains(s.Headline, "Waiting"),
		fmt.Sprintf("headline %q", s.Headline))

	// And back again, because a latch that only falls one way would pass above.
	alive = true
	s = buildUIState(d)
	check("game returns -> COLLECTING again", s.Collecting,
		"the status follows the game in both directions rather than latching")
}

// runUICountSelftest covers §10's "the capture count must come from counting
// files on disk. Delete one behind the UI's back and assert the number goes
// down."
func runUICountSelftest(check func(name string, ok bool, detail string)) {
	dir, err := os.MkdirTemp("", "cc-ui-count-")
	if err != nil {
		check("count testable", false, err.Error())
		return
	}
	defer os.RemoveAll(dir)

	d := uiDeps{
		gameAlive: func() error { return fmt.Errorf("no game") },
		findLog:   func() (string, string) { return "", "none" },
		outDir:    dir,
		autoLog:   filepath.Join(dir, "collector-auto.log"),
	}

	check("empty folder counts zero", buildUIState(d).Captures == 0, "nothing on disk, nothing reported")

	for i := 1; i <= 3; i++ {
		_ = os.WriteFile(filepath.Join(dir, fmt.Sprintf("shot_%04d.png", i)), []byte("x"), 0o644)
	}
	got := buildUIState(d).Captures
	check("three files count as three", got == 3, fmt.Sprintf("counted %d", got))

	// BEHIND THE UI'S BACK. Nothing tells the program this happened.
	_ = os.Remove(filepath.Join(dir, "shot_0002.png"))
	got = buildUIState(d).Captures
	check("deleting a file makes the number GO DOWN", got == 2,
		fmt.Sprintf("counted %d after a deletion the program was never told about", got))

	// A non-PNG must not inflate the count - otherwise the sidecars would
	// double every number the person sees.
	_ = os.WriteFile(filepath.Join(dir, "shot_0001.json"), []byte("{}"), 0o644)
	got = buildUIState(d).Captures
	check("sidecars are not counted as pictures", got == 2, fmt.Sprintf("counted %d", got))
}

// runUIInterfaceSelftest asserts the window carries what §2 requires, without
// opening a window on a build machine.
func runUIInterfaceSelftest(check func(name string, ok bool, detail string)) {
	check("the reassurance line is present",
		uiHTMLContains("Nothing leaves your computer until you press that button"),
		"§2 calls this out as not decoration - people are right to be careful")
	check("the one button is present", uiHTMLContains("Send my data back"), "§8's button")
	check("capture-now button is present", uiHTMLContains("Take a picture now"),
		"kept even after the hotkey is fixed - a button cannot silently fail to register")
	check("no START or STOP control", !uiHTMLContains(">START<") && !uiHTMLContains(">STOP<"),
		"§1 removed them - it follows the game")
}
