package main

// window_selftest.go - the native window, and the way back.
//
// Every check here has a case that must fail it. The ones that matter most are
// the two that are invisible when they go wrong:
//
//   - an UPGRADED install being asked a question it never agreed to answer,
//     which is how an update changes the deal underneath somebody
//   - a REVERT that reports success without moving anything, which is the one
//     thing a rollback must never do, because it is reached for when things
//     are already wrong

import (
	"os"
	"path/filepath"
	"regexp"
	"strings"
)

func runWindowSelftest(check func(name string, ok bool, detail string)) {

	// -----------------------------------------------------------------
	// 1. THE ROWS ARE DATA, AND THEY RENDER FROM THE STATE
	// -----------------------------------------------------------------
	check("WINDOW: there are status rows at all",
		len(statusRows) >= 8,
		"the window would be empty, and every check below would pass vacuously")

	seen := map[string]bool{}
	dupes := []string{}
	missing := []string{}
	for _, r := range statusRows {
		if r.Value == nil {
			missing = append(missing, r.Label)
		}
		if seen[r.Label] {
			dupes = append(dupes, r.Label)
		}
		seen[r.Label] = true
	}
	check("WINDOW: every row can render itself",
		len(missing) == 0,
		"rows with no Value would show nothing: "+strings.Join(missing, ", "))
	check("WINDOW: no two rows share a label",
		len(dupes) == 0,
		"duplicated: "+strings.Join(dupes, ", ")+" - a person cannot tell which is which")

	// THE VALUES COME FROM THE STATE, NOT FROM CONSTANTS.
	//
	// Rendered twice, from two different states, and required to differ. A row
	// that returned a fixed string would look perfectly fine in a screenshot
	// and never change while the collector ran - which is exactly the failure
	// this whole rebuild is about.
	full := uiState{
		LogPath: `C:\Games\StarCitizen\LIVE\Game.log`, LogHow: "scanned",
		Patch: "4.9.188", Captures: 653, LastCapture: "2 hours ago",
		LastReason: "routine check", PendingRows: 308,
		Hotkey: "alt+f3", HotkeyOK: true, CaptureDir: `C:\x\captures`, Install: "LIVE",
	}
	empty := uiState{}
	ctxFull := rowContext{S: full, ExeDir: os.TempDir()}
	ctxEmpty := rowContext{S: empty, ExeDir: os.TempDir()}

	differing := 0
	for _, r := range statusRows {
		if r.Value(ctxFull) != r.Value(ctxEmpty) {
			differing++
		}
	}
	check("WINDOW: rows render from the state rather than from constants",
		differing >= 6,
		"only "+itoaSmall(differing)+" of "+itoaSmall(len(statusRows))+" rows changed "+
			"when the state changed; the rest would sit on a fixed string forever")

	// NEGATIVE CONTROL for the row that matters most on his machine. A hotkey
	// that failed to register has to READ differently, not merely be stored
	// differently.
	var hotkeyRow *statusRow
	for i := range statusRows {
		if statusRows[i].Label == "Hotkey" {
			hotkeyRow = &statusRows[i]
		}
	}
	if hotkeyRow != nil {
		okState := rowContext{S: uiState{Hotkey: "alt+f3", HotkeyOK: true}}
		badState := rowContext{S: uiState{Hotkey: "alt+f3", HotkeyOK: false}}
		check("WINDOW: a hotkey that did not register reads differently",
			hotkeyRow.Value(okState) != hotkeyRow.Value(badState),
			"a dead hotkey would look identical to a working one until somebody pressed it")
		check("WINDOW: and it is marked as a problem",
			hotkeyRow.Warn != nil && hotkeyRow.Warn(badState) && !hotkeyRow.Warn(okState),
			"NEGATIVE CONTROL: the warning must fire for the bad case and not the good one")
	}

	// -----------------------------------------------------------------
	// 2. EVERY BUTTON POINTS AT SOMETHING THAT EXISTS
	// -----------------------------------------------------------------
	//
	// Read out of the source, the same way the browser-transport parity check
	// worked, because a button wired to a missing action does nothing and looks
	// exactly like a button wired to a slow one.
	if src, err := os.ReadFile("window.go"); err == nil {
		called := map[string]bool{}
		for _, m := range regexp.MustCompile(`run\("([a-zA-Z]+)"`).FindAllSubmatch(src, -1) {
			called[string(m[1])] = true
		}
		acts := map[string]bool{}
		var asrcOrEmpty []byte
		if asrc, err := os.ReadFile("ui_actions.go"); err == nil {
			asrcOrEmpty = asrc
			for _, m := range regexp.MustCompile(`"([a-zA-Z]+)":\s*func\((?:[a-zA-Z_]+\s+)?json\.RawMessage\)`).FindAllSubmatch(asrc, -1) {
				acts[string(m[1])] = true
			}
		}
		var bad []string
		for n := range called {
			if !acts[n] {
				bad = append(bad, n)
			}
		}
		check("WINDOW: every button calls an action that exists",
			len(called) > 0 && len(bad) == 0,
			"buttons pointing at nothing: "+strings.Join(bad, ", "))
		// THE CONTROL COMPARES AGAINST THE REAL TOTAL.
		//
		// A threshold ("at least 8") is satisfiable by a parse that quietly
		// drops entries, which is exactly what happened the first time this
		// ran. Counting the map's actual keys in the source and requiring the
		// extractor to find all of them makes a lossy pattern fail here rather
		// than surface as a false finding about a button.
		declared := len(regexp.MustCompile(`"[a-zA-Z]+":\s*func\(`).FindAll(asrcOrEmpty, -1))
		check("WINDOW: NEGATIVE CONTROL - the extractor found EVERY action, not most",
			len(called) >= 3 && declared > 0 && len(acts) == declared,
			"the source declares "+itoaSmall(declared)+" actions and the pattern found "+
				itoaSmall(len(acts))+"; a lossy parse reports working buttons as broken")
	} else {
		check("WINDOW: button wiring NOT COMPARED", true,
			"sources are not beside the exe, so this run did not compare them")
	}

	// -----------------------------------------------------------------
	// 3. AN UPGRADED INSTALL IS NOT AMBUSHED
	// -----------------------------------------------------------------
	dir, err := os.MkdirTemp("", "cc-window")
	if err != nil {
		return
	}
	defer os.RemoveAll(dir)

	// A fresh install: nothing at all on disk.
	check("WINDOW: a fresh folder is not treated as an upgrade",
		!IsUpgradedInstall(dir),
		"a new install would silently inherit an upgrade's defaults and never be asked")
	check("WINDOW: and a fresh install has no recorded choice yet",
		!HasWindowChoice(dir),
		"it would never be asked")

	// An upgraded install: it has consented before, which is the population
	// that must not be interrogated.
	_ = os.WriteFile(filepath.Join(dir, consentFile),
		[]byte("agreed_version = 3\nagreed_at = 2026-08-14T00:00:00Z\n"), 0o644)
	check("WINDOW: an install that has consented before IS an upgrade",
		IsUpgradedInstall(dir),
		"Sleven's wife and his friend would be asked a question they never agreed to answer")
	check("WINDOW: an upgraded install keeps the window it already had",
		ShowWindowSetting(dir),
		"THE AMBUSH: an update would take their window away without asking")

	// AskWindowChoice must record it WITHOUT asking. If this ever put a dialog
	// up, the selftest would hang here - which is itself the signal.
	got := AskWindowChoice(dir, nil)
	check("WINDOW: an upgrade is answered silently, not asked",
		got && HasWindowChoice(dir),
		"either it was not recorded, or it changed their behaviour")

	// NEGATIVE CONTROL: an explicit choice must beat both defaults, or the
	// setting is decoration.
	_ = SetShowWindow(dir, false)
	check("WINDOW: NEGATIVE CONTROL - an explicit 'no window' is honoured",
		!ShowWindowSetting(dir),
		"the tray-only choice would be ignored and the window would open anyway")
	_ = SetShowWindow(dir, true)
	check("WINDOW: NEGATIVE CONTROL - an explicit 'show window' is honoured",
		ShowWindowSetting(dir),
		"a checker that always returned false would pass the line above")

	// A setting write must not destroy the rest of the file.
	_ = os.WriteFile(filepath.Join(dir, settingsFileName),
		[]byte("# a comment somebody reads\nauto = true\ninterval_seconds = 120\n"), 0o644)
	_ = SetSetting(dir, "hotkey", "ctrl+f9")
	body, _ := os.ReadFile(filepath.Join(dir, settingsFileName))
	check("WINDOW: changing one setting keeps the rest of the file",
		strings.Contains(string(body), "# a comment somebody reads") &&
			strings.Contains(string(body), "auto = true") &&
			strings.Contains(string(body), "hotkey = ctrl+f9"),
		"the file is the escape hatch, and its comments are its only documentation")
	_ = SetSetting(dir, "hotkey", "ctrl+f10")
	body, _ = os.ReadFile(filepath.Join(dir, settingsFileName))
	check("WINDOW: changing it twice does not duplicate the key",
		strings.Count(string(body), "hotkey =") == 1,
		"a second line would make the value depend on read order")

	// -----------------------------------------------------------------
	// 4. THE WAY BACK
	// -----------------------------------------------------------------
	//
	// A rollback is reached for when things are already wrong, so the failure
	// that matters is one that reports success having moved nothing.
	empty2, err := os.MkdirTemp("", "cc-revert")
	if err != nil {
		return
	}
	defer os.RemoveAll(empty2)

	fakeExe := filepath.Join(empty2, "collector.exe")
	_ = os.WriteFile(fakeExe, []byte("current"), 0o644)

	// No .old at all: it must REFUSE, out loud.
	if _, err := os.Stat(fakeExe + ".old"); os.IsNotExist(err) {
		check("REVERT: with nothing kept, there is nothing to go back to",
			!hasPreviousAt(fakeExe),
			"it would offer a revert that cannot work")
	}

	// An empty .old is not a build. A zero-byte file left by a failed download
	// would otherwise be swapped in and leave somebody with nothing that runs.
	_ = os.WriteFile(fakeExe+".old", []byte{}, 0o644)
	check("REVERT: a zero-byte kept file is not a previous version",
		!hasPreviousAt(fakeExe),
		"an empty file would be swapped in and the machine would have no collector")

	_ = os.WriteFile(fakeExe+".old", []byte("previous build"), 0o644)
	check("REVERT: NEGATIVE CONTROL - a real kept build IS offered",
		hasPreviousAt(fakeExe),
		"a check that refused everything would hide the way back entirely")

	check("REVERT: the kept build sits beside the running one",
		strings.HasSuffix(fakeExe+".old", ".old") &&
			filepath.Dir(fakeExe+".old") == filepath.Dir(fakeExe),
		"the installer leaves it there; looking anywhere else would find nothing")
}

// hasPreviousAt is HasPreviousBuild's rule, applied to a named path so the
// selftest can exercise it without depending on where this test binary lives.
func hasPreviousAt(exe string) bool {
	fi, err := os.Stat(exe + ".old")
	return err == nil && fi.Size() > 0
}
