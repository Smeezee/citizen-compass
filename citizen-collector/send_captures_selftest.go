package main

// send_captures_selftest.go - the SEND button cannot quietly send less than the
// promise says.
//
// # WHY THIS EXISTS AS ITS OWN CHECK
//
// Consent v3 states "Screenshots ARE uploaded when you send". BuildExport still
// takes an explicit includeCaptures, and it should: the value is recorded in
// the zip's README, and runExportSelftest drives both paths through it on
// purpose.
//
// But every other check in this suite calls BuildExport DIRECTLY. Not one of
// them looked at the single place that decides what the SEND button passes. A
// `false` reinstated at that call site - by a merge, by somebody restoring the
// old "Data only" button, by a stale page - would have left all 437 other
// checks green while the program did less than the promise it had just asked
// everybody to agree to.
//
// That is the exact drift consentVersion exists to catch, and until now nothing
// could catch it. The promise is enforced in ui_actions.go rather than in the
// page because ui_browser binds the same "sendData" name over a socket; this
// check is aimed at that same place, for the same reason.

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
)

func runSendIncludesCapturesSelftest(check func(name string, ok bool, detail string)) {
	tmp, err := os.MkdirTemp("", "send-captures-")
	if err != nil {
		check("SEND: fixture directory", false, err.Error())
		return
	}
	defer os.RemoveAll(tmp)

	// One frame that CAN prove it photographed the game.
	//
	// It has to be a provable one. A frame with no sidecar is held back whatever
	// the caller asked for, so a fixture built from one would make "included"
	// and "omitted" produce identical zips and the assertion below would be true
	// for the wrong reason.
	if err := os.WriteFile(filepath.Join(tmp, "shot_0001.png"),
		[]byte("\x89PNG\r\n\x1a\nfake"), 0o644); err != nil {
		check("SEND: fixture frame", false, err.Error())
		return
	}
	if err := os.WriteFile(filepath.Join(tmp, "shot_0001.json"), []byte(
		`{"window":{"exe":"starcitizen.exe","how_found":"process is starcitizen.exe",`+
			`"title":"Star Citizen"}}`), 0o644); err != nil {
		check("SEND: fixture sidecar", false, err.Error())
		return
	}

	// The real action ends by opening Explorer. Not on a test machine.
	restore := revealFile
	revealFile = func(string) {}
	defer func() { revealFile = restore }()

	// SendURL is deliberately empty: this check is about what gets PACKAGED,
	// and nothing in a selftest should be able to reach the network.
	acts := buildUIActions(uiActionCtx{ExeDir: tmp, OutDir: tmp})
	send := acts["sendData"]
	if send == nil {
		check("SEND: buildUIActions still defines sendData", false,
			"no sendData action - the page and the socket both dispatch to this name")
		return
	}

	// FALSE IS THE WHOLE POINT.
	//
	// This is what the removed "Data only" button sent, what a cached copy of
	// the old page still sends, and what anybody hand-rolling a socket call can
	// send today. The answer must not depend on it.
	if _, err := send(json.RawMessage(`false`)); err != nil {
		check("SEND: sendData(false) completes", false, err.Error())
		return
	}

	zips, _ := filepath.Glob(filepath.Join(tmp, "*.zip"))
	if len(zips) != 1 {
		check("SEND: sendData wrote exactly one zip", false,
			fmt.Sprintf("found %d zip(s) in the output folder", len(zips)))
		return
	}
	names := zipNames(zips[0])
	check("CONSENT: SEND includes the frames even when the caller asks for false",
		hasPrefix(names, "captures/"),
		fmt.Sprintf("sendData(false) produced %v", names))

	// NEGATIVE CONTROL - and this one is not decoration.
	//
	// The check above passes if captures/ is present. That is also what it would
	// do if this fixture were incapable of producing a zip WITHOUT captures/ -
	// in which case it would be green forever and would never notice the
	// regression it was written for. So: the same fixture, through BuildExport
	// with a real false, must still be able to omit the frames.
	res, err := BuildExport(tmp, tmp, tmp, false, nil)
	if err != nil {
		check("NEGATIVE CONTROL: an export can still omit the frames", false, err.Error())
		return
	}
	check("NEGATIVE CONTROL: the same fixture CAN omit the frames, so the check above can fail",
		!hasPrefix(zipNames(res.Path), "captures/"),
		fmt.Sprintf("BuildExport(false) produced %v", zipNames(res.Path)))
}
