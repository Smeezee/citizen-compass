package main

// auto_selftest.go - proves the --auto trigger actually triggers.
//
// WHY THIS IS NOT A UNIT TEST FILE
//   The rev 5 addendum has the package verifier run the shipped exe with
//   --selftest and require exit 0. A _test.go file is not compiled into that
//   exe, so a check that lives only there proves nothing about the binary a
//   crew member is holding. These run inside the product.
//
// ---------------------------------------------------------------------------
// THE NEGATIVE CONTROL IS THE POINT
// ---------------------------------------------------------------------------
// A trigger test that only ever feeds interesting input cannot distinguish
// "detects state changes correctly" from "fires on absolutely everything". The
// second is worse than a broken detector: it produces a full folder of captures
// and looks like a resounding success.
//
// So a log with NO state changes is fed through the identical path and must
// produce EXACTLY ZERO triggers. If it fires, the detector is indiscriminate,
// every count below is meaningless, and the whole group is reported VOID rather
// than as a set of passes. That is why runAutoSelftest returns a void flag and
// the caller refuses to report a pass on it.

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"
)

// A realistic header, matching the shape of the real log this parser was built
// against (776 lines, FileVersion 4.9.188.23497, a session that never left the
// menu). Everything after priming is what the test is actually about.
const synthPreamble = `<2026-08-02T02:43:28.680Z> FileVersion: 4.9.188.23497
<2026-08-02T02:43:29.309Z> Changelist: 12344265
<2026-08-02T02:43:29.309Z> Branch: sc-alpha-4.9.0
<2026-08-02T02:43:35.000Z> <Context Establisher Done> map="megamap" gamerules="SC_Frontend" state=eCVS_ReadyToStream(13)
`

// The sequence under test. Six triggers, and the comment on each line says
// which - so a change in behaviour shows up as a diff against a stated
// expectation rather than against a number nobody can explain.
const synthChanges = `<2026-08-02T02:44:01.000Z> Loading screen for Frontend_Main : SC_Frontend closed after 4.58 seconds
<2026-08-02T02:44:10.000Z> <Context Establisher Done> map="megamap" gamerules="SC_Default" state=eCVS_ReadyToStream(13)
<2026-08-02T02:44:20.000Z> <Context Establisher Done> map="pyro" gamerules="SC_Default" state=eCVS_ReadyToStream(13)
<2026-08-02T02:44:30.000Z> <OnClientSpawned> zone="Stanton_1_Hurston" entity="Player"
<2026-08-02T02:44:40.000Z> <OnClientSpawned> zone="Stanton_1_Hurston" entity="Player"
<2026-08-02T02:44:50.000Z> <Context Establisher Done> map="pyro" gamerules="SC_Default" state=eCVS_ReadyToStream(13)
`

// Same shape, same field names, same everything - except nothing changes.
// taskname/state are included on purpose: they are the fields that once got
// scraped into the location by a looser pattern.
const synthNoChanges = `<2026-08-02T02:45:00.000Z> <Context Establisher Done> map="megamap" gamerules="SC_Frontend" state=eCVS_ReadyToStream(13)
<2026-08-02T02:45:05.000Z> [CIG] Registered console variable sys_flash_edit
<2026-08-02T02:45:10.000Z> taskname="ResolveSpawnLocation" state=eCVS_UnstowPlayer(14)
<2026-08-02T02:45:15.000Z> <Context Establisher Done> map="megamap" gamerules="SC_Frontend" state=eCVS_ReadyToStream(13)
`

var wantReasons = []string{
	`event:loading_screen "Frontend_Main : SC_Frontend"`,
	`state_change:gamerules "SC_Frontend"->"SC_Default"`,
	`state_change:map "megamap"->"pyro"`,
	`state_change:zone ""->"Stanton_1_Hurston"`,
	`event:client_spawned "Stanton_1_Hurston"`,
	`event:client_spawned "Stanton_1_Hurston"`,
}

func reasonsOf(ts []Trigger) []string {
	out := make([]string, 0, len(ts))
	for _, t := range ts {
		out = append(out, t.Reason())
	}
	return out
}

// appendTo mimics the game appending to a log it holds open.
func appendTo(path, text string) error {
	f, err := os.OpenFile(path, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0o644)
	if err != nil {
		return err
	}
	if _, err := f.WriteString(text); err != nil {
		f.Close()
		return err
	}
	return f.Close()
}

// runAutoSelftest returns true if the results are VOID - i.e. the negative
// control fired and nothing else in the group can be believed.
func runAutoSelftest(dir string, check func(name string, ok bool, detail string)) bool {

	// --- 0. structural: the shared parser is still where this file thinks ---
	//
	// auto.go looks the OnClientSpawned parser up by name so a rename in
	// gamelog.go breaks loudly here rather than silently binding to nothing.
	check("auto: shared zone parser found",
		unverifiedPatternByName("OnClientSpawned-zone") != nil,
		"looked up by name from unverifiedLocationPatterns")

	tmp, err := os.MkdirTemp(dir, "selftest-auto-")
	if err != nil {
		check("auto: temp dir", false, err.Error())
		return false
	}
	defer os.RemoveAll(tmp)

	// =====================================================================
	// NEGATIVE CONTROL FIRST. If this fires, everything below is void, so it
	// is established before any positive result is reported.
	// =====================================================================
	negPath := filepath.Join(tmp, "Game.negative.log")
	if err := os.WriteFile(negPath, []byte(synthPreamble), 0o644); err != nil {
		check("auto: write negative control log", false, err.Error())
		return false
	}
	negTail := newLogTailer(negPath)
	if _, err := negTail.Poll(); err != nil { // prime
		check("auto: negative control prime", false, err.Error())
		return false
	}
	if err := appendTo(negPath, synthNoChanges); err != nil {
		check("auto: append negative control", false, err.Error())
		return false
	}
	negTriggers, err := negTail.Poll()
	if err != nil {
		check("auto: negative control poll", false, err.Error())
		return false
	}

	negClean := len(negTriggers) == 0
	negDetail := "a log with no state changes produced 0 triggers"
	if !negClean {
		negDetail = fmt.Sprintf("FIRED %d: %s", len(negTriggers),
			strings.Join(reasonsOf(negTriggers), " | "))
	}
	check("auto: NEGATIVE CONTROL (no changes)", negClean, negDetail)

	if !negClean {
		fmt.Println("  [VOID] the negative control fired, so the trigger tests below")
		fmt.Println("         cannot distinguish detection from indiscriminate firing.")
		fmt.Println("         Treat this run as NO RESULT, not as a failure of one check.")
		return true
	}

	// =====================================================================
	// 1. PRIMING - an existing backlog must not fire.
	// =====================================================================
	logPath := filepath.Join(tmp, "Game.log")
	if err := os.WriteFile(logPath, []byte(synthPreamble), 0o644); err != nil {
		check("auto: write synthetic log", false, err.Error())
		return false
	}
	tail := newLogTailer(logPath)
	primed, err := tail.Poll()
	check("auto: priming fires nothing", err == nil && len(primed) == 0,
		fmt.Sprintf("%d trigger(s) from the pre-existing backlog", len(primed)))

	// =====================================================================
	// 2. KNOWN SEQUENCE - exact count AND exact reasons.
	// =====================================================================
	if err := appendTo(logPath, synthChanges); err != nil {
		check("auto: append changes", false, err.Error())
		return false
	}
	got, err := tail.Poll()
	if err != nil {
		check("auto: poll after changes", false, err.Error())
		return false
	}

	gotReasons := reasonsOf(got)
	check("auto: trigger COUNT is exactly 6",
		len(got) == 6,
		fmt.Sprintf("got %d: %s", len(got), strings.Join(gotReasons, " | ")))

	exact := len(gotReasons) == len(wantReasons)
	if exact {
		for i := range wantReasons {
			if gotReasons[i] != wantReasons[i] {
				exact = false
				break
			}
		}
	}
	detail := "each trigger names the field and the transition"
	if !exact {
		detail = fmt.Sprintf("want [%s] got [%s]",
			strings.Join(wantReasons, " | "), strings.Join(gotReasons, " | "))
	}
	check("auto: trigger REASONS match exactly", exact, detail)

	// Every trigger must state a kind. A capture with no stated reason is a bug.
	kindsOK := true
	for _, t := range got {
		if strings.TrimSpace(t.Kind) == "" {
			kindsOK = false
		}
	}
	check("auto: every trigger states a kind", kindsOK,
		"a capture with no stated reason is a bug")

	// =====================================================================
	// 3. Feeding the same lines again must not re-fire.
	// =====================================================================
	again, err := tail.Poll()
	check("auto: re-poll with no new bytes is silent",
		err == nil && len(again) == 0,
		fmt.Sprintf("%d trigger(s) from an unchanged file", len(again)))

	// =====================================================================
	// 4. ROTATION - a new session truncates Game.log. Must re-prime, not
	//    replay the new session's backlog as a burst of captures.
	// =====================================================================
	if err := os.WriteFile(logPath, []byte(synthPreamble), 0o644); err != nil {
		check("auto: truncate for rotation test", false, err.Error())
	} else {
		rot, rerr := tail.Poll()
		check("auto: log rotation re-primes silently",
			rerr == nil && len(rot) == 0,
			fmt.Sprintf("%d trigger(s) after the log shrank", len(rot)))
	}

	// =====================================================================
	// SECTIONS 5-7 ARE GONE WITH THE FEATURE THEY TESTED.
	//
	// They covered the debounce, the interval fallback, the main-menu gate and
	// the state-change-outranks-interval rule - every one of them a property of
	// `decide()`, which §6 removed. Tests for a deleted feature that keep
	// passing are worse than no tests: they certify behaviour nobody can
	// reach.
	//
	// The text is in _to_delete/collector_auto_capture_removed_20260818/ rather
	// than destroyed, because the debounce fixture in particular is a good
	// pattern if a future feature ever needs one.
	//
	// What survives above: the detector and the log tailer, which still parse
	// every line for the diary and for the in-world flag on a hotkey capture.
	// What survives below: the settings reader.
	// =====================================================================

	// =====================================================================
	// 8. SETTINGS FILE - the values a non-technical user will actually edit,
	//    including the Notepad BOM that would otherwise eat the first line.
	// =====================================================================
	sdir := filepath.Join(tmp, "settings")
	if err := os.MkdirAll(sdir, 0o755); err == nil {
		// A REAL SETTING IS DELIBERATELY FIRST, ahead of any comment.
		//
		// The first version of this fixture opened with "# notes", so an
		// unstripped BOM corrupted a COMMENT - which changes nothing - and the
		// BOM check passed while the bug it exists to catch was fully present.
		// Caught by mutation testing on 2026-08-06: removing the TrimPrefix
		// left this check green. With a live setting on line 1 the check now
		// fails when the BOM is not stripped, which is the whole point.
		body := "\xEF\xBB\xBFauto = true\r\n# notes\r\ninterval_minutes = 5\r\n" +
			"debounce_seconds=7\r\n\r\nout = pics\r\nnonsense line\r\n"
		if werr := os.WriteFile(filepath.Join(sdir, settingsFileName), []byte(body), 0o644); werr == nil {
			s, notes := loadSettings(sdir)

			a, aok := s.boolVal("auto")
			check("auto: settings reads first line despite BOM", aok && a,
				"a UTF-8 BOM would otherwise be part of the first key name")

			iv, ok1, e1 := s.intVal("interval_minutes")
			db, ok2, e2 := s.intVal("debounce_seconds")
			check("auto: settings reads numbers",
				ok1 && ok2 && e1 == nil && e2 == nil && iv == 5 && db == 7,
				fmt.Sprintf("interval=%d debounce=%d", iv, db))

			outv, ok3 := s.str("out")
			check("auto: settings reads text", ok3 && outv == "pics",
				fmt.Sprintf("out=%q", outv))

			check("auto: settings reports a bad line", len(notes) == 1,
				fmt.Sprintf("%d note(s): %s", len(notes), strings.Join(notes, "; ")))

			// A key that is not in the file must report absent, not zero -
			// otherwise a typo'd setting silently becomes 0, and
			// interval_minutes=0 means "off".
			_, present, _ := s.intVal("interval_minute")
			check("auto: a missing key reports absent, not 0", !present,
				"a typo must not silently turn the interval off")
		}
	}

	return false
}
