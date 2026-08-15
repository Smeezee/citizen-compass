package main

// send_now.go - sending, without needing the window to work.
//
// # WHY THIS EXISTS
//
// Sleven was at a shop terminal with 26 captures and a working hotkey, and
// could not send any of it, because the window was dead. There was no flag, no
// command and no menu item that sends - the ONLY way to contribute was a button
// inside a UI that had stopped answering.
//
// That makes a rendering failure into a total loss of function, and it cannot
// be talked through on a phone either: there was nothing to tell him to type.
//
// # ONE IMPLEMENTATION, THREE DOORS
//
// The button, the -send flag and the tray menu all call SendNow. They are three
// ways in, not three copies of the logic. A second implementation of "package
// and send" would drift from the first, and the drift would show up as one door
// clearing the local pictures and another not - on somebody else's machine,
// with their only copy of a session.
//
// # CONSENT IS NOT ROUTED AROUND
//
// The flag asks exactly what the window asks, with the same text, through the
// same AskConsent. A command-line path that skipped the consent screen would be
// a silent way to upload somebody's screenshots without the screen that tells
// them screenshots are uploaded - which is the one thing consent v3 exists to
// prevent, and it would be introduced by a convenience feature.

import (
	"fmt"
	"path/filepath"
	"strings"
	"time"
)

// SendNow packages what has been collected and sends it.
//
// THE SHARED CORE. Returns the sentence a person should be shown, which is the
// same sentence in the window, in a message box, and in the log.
func SendNow(exeDir, outDir, sendURL, sendKey string, clearAfterSend bool,
	logf func(string, ...interface{})) (string, error) {
	if logf == nil {
		logf = func(string, ...interface{}) {}
	}

	res, err := BuildExport(exeDir, outDir, outDir, true, logf)
	if err != nil {
		return "", fmt.Errorf("the package could not be built: %w", err)
	}

	if strings.TrimSpace(sendURL) == "" {
		// §3 of the destination work: blank must never look like a send.
		return LocalOnlyResult(filepath.Base(res.Path)), nil
	}

	up, uerr := SendExport(res, outDir, sendURL, sendKey, res.InstallID, clearAfterSend, logf)
	if uerr != nil {
		return "", fmt.Errorf("packaged, but sending failed: %w. Your data is "+
			"untouched and the file is in the folder", uerr)
	}
	if !up.Sent {
		return "Packaged, but the server did not confirm it. Nothing was removed.", nil
	}
	return up.Note, nil
}

// SendFromCommandLine is the -send flag.
//
// # NO CONSOLE TO PRINT TO
//
// This is a -H windowsgui build, so a person who runs it from a shortcut or a
// double-click has nowhere to read output. The result goes to a message box AND
// to the log: the box because that is where they are looking, the log because
// that is what they can send back when it goes wrong.
func SendFromCommandLine(exeDir, outDir string) int {
	logPath := filepath.Join(exeDir, "collector-auto.log")
	lf, err := openAutoLog(logPath)
	if err != nil {
		showErrorBox("Citizen Collector", "Could not open the log to record this: "+err.Error())
		return 1
	}
	defer lf.Close()
	logf := func(format string, args ...interface{}) {
		fmt.Fprintf(lf, "[%s] %s\n", nowStamp(), fmt.Sprintf(format, args...))
	}
	logf("---- send requested from the command line (-send) ----")

	// THE SAME CONSENT SCREEN THE WINDOW SHOWS. Not a variant, not a shorter
	// one, and not skipped because this path has no window of its own.
	if !AskConsent(exeDir, logf) {
		logf("send: declined at the consent screen - nothing was collected or sent")
		return 1
	}

	// SAME PRECEDENCE AS THE WINDOW: local settings win, then the feed's
	// address, then the last one this machine remembered.
	cfg, _ := loadSettings(exeDir)
	lu, _ := cfg.str("send_url")
	lk, _ := cfg.str("send_key")
	lu, _ = StripWrappingBrackets(lu)
	lk, _ = StripWrappingBrackets(lk)
	dest := ResolveDestination(lu, lk, "", "", LoadCachedDestination(exeDir))

	clearAfterSend := true
	if v, ok := cfg.boolVal("clear_after_send"); ok {
		clearAfterSend = v
	}

	if !dest.Configured() {
		msg := "There is nowhere to send to yet, so nothing was sent.\n\n" +
			"Open Citizen Collector normally once while you have an internet " +
			"connection - it collects the address by itself - then try again."
		logf("send: no destination configured")
		showErrorBox("Citizen Collector", msg)
		return 1
	}
	logf("send: sending to %s (from %s)", dest.URL, dest.Source)

	note, err := SendNow(exeDir, outDir, dest.URL, dest.Key, clearAfterSend, logf)
	if err != nil {
		logf("send: FAILED - %v", err)
		showErrorBox("Citizen Collector",
			"That did not work:\n\n"+err.Error()+
				"\n\nNothing was deleted. Everything is still on this computer.")
		return 1
	}
	logf("send: %s", note)
	messageBox("Citizen Collector", note, 0x00000040 /* MB_ICONINFORMATION */)
	return 0
}

// nowStamp is the log timestamp format, in one place.
func nowStamp() string { return time.Now().Format("2006-01-02 15:04:05") }
