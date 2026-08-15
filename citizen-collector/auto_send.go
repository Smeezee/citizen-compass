package main

// auto_send.go - the session ended, and nobody is watching.
//
// # THE RULE THAT SHAPES EVERY BRANCH HERE
//
// Nobody is present. That is the whole point of the feature and it is also what
// makes every failure mode different from the ones the SEND button has:
//
//   - A refused send cannot be retried by a person who saw it fail.
//   - A message in a window nobody has open is not a message.
//   - Anything deleted here is deleted with no witness.
//
// So: NOTHING IS EVER DELETED THAT THE SERVER HAS NOT CONFIRMED, a refusal
// keeps everything and leaves a record the person finds later, and the record
// is written where they will actually see it rather than only in the log.
//
// # THE 64 MB CEILING IS NOW LOAD-BEARING
//
// The receiver refuses anything over 64 MB, and Sleven's friend has 76 frames
// on one machine. An unattended send is exactly where that gets hit, and the
// person is not there to notice. A refusal for size must therefore keep the
// data, say so plainly next time the window is opened, and never look like a
// completed send.

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"time"
)

// pendingNoticeFile is what the window reads to tell somebody what happened
// while they were not looking.
//
// A FILE, not a log line. collector-auto.log is a diagnostic record that nobody
// who is not debugging will ever open. Something that happened to a person's
// data, without them present, has to surface where they will actually meet it.
const pendingNoticeFile = "collector-last-send.txt"

// WritePendingNotice records the outcome of an unattended send.
func WritePendingNotice(dir, text string) {
	body := "# Citizen Collector - what happened the last time it tried to send\n" +
		"# by itself. Safe to delete; it is written again after each attempt.\n\n" +
		time.Now().Format("2006-01-02 15:04") + "\n\n" + text + "\n"
	_ = os.WriteFile(filepath.Join(dir, pendingNoticeFile), []byte(body), 0o644)
}

// ReadPendingNotice returns the last unattended-send outcome, or "".
func ReadPendingNotice(dir string) string {
	b, err := os.ReadFile(filepath.Join(dir, pendingNoticeFile))
	if err != nil {
		return ""
	}
	var out []string
	for _, line := range strings.Split(string(b), "\n") {
		if strings.HasPrefix(strings.TrimSpace(line), "#") {
			continue
		}
		out = append(out, line)
	}
	return strings.TrimSpace(strings.Join(out, "\n"))
}

// AutoSendIfChosen packages and sends the finished session, but only if this
// machine chose that.
//
// Reads the choice from disk at the moment of use. A value captured at startup
// would honour an answer the person may have changed hours ago, and for a
// decision about uploading their screenshots the freshest reading is the only
// honest one.
func AutoSendIfChosen(exeDir, outDir string, logf func(string, ...interface{})) {
	if logf == nil {
		logf = func(string, ...interface{}) {}
	}
	mode := ReadSendMode(exeDir)
	if mode != SendAutomatic {
		// NOT AN ERROR, AND NOT SILENT EITHER. The ask-every-time machines are
		// the majority and the log should say why nothing happened, so that
		// "it never sends" is distinguishable from "it is broken".
		logf("session ended: not sending, because this machine is on ask-every-time. " +
			"Open the window and press the button when you want to send.")
		return
	}

	dest := ResolveDestination("", "", "", "", LoadCachedDestination(exeDir))
	// LOCAL SETTINGS STILL WIN, read exactly the way the window reads them -
	// same loader, same bracket stripping. A second reader with its own idea of
	// the file is how an unattended send ends up going somewhere the window
	// would not have sent it.
	if cfg, _ := loadSettings(exeDir); true {
		lu, _ := cfg.str("send_url")
		lk, _ := cfg.str("send_key")
		lu, _ = StripWrappingBrackets(lu)
		lk, _ = StripWrappingBrackets(lk)
		dest = ResolveDestination(lu, lk, "", "", LoadCachedDestination(exeDir))
	}
	if !dest.Configured() {
		logf("session ended: automatic sending is on, but there is nowhere to send yet.")
		WritePendingNotice(exeDir, "Nothing was sent when you finished playing, because "+
			"this computer does not have a destination yet. Your data is untouched. "+
			"It will send by itself once the address arrives.")
		return
	}

	logf("session ended: packaging and sending automatically, as chosen at setup.")
	res, err := BuildExport(exeDir, outDir, outDir, true, logf)
	if err != nil {
		logf("auto-send: the package could not be built (%v) - nothing was sent or removed", err)
		WritePendingNotice(exeDir, "Nothing was sent when you finished playing: the "+
			"package could not be built ("+err.Error()+"). Your data is untouched.")
		return
	}

	// SIZE IS CHECKED HERE, BEFORE THE UPLOAD.
	//
	// The receiver would refuse it anyway, but finding out by being refused
	// means uploading it first - which on a home connection can be several
	// minutes of somebody's bandwidth spent to be told no.
	if sz := fileSize(res.Path); sz > receiverMaxBytes {
		logf("auto-send: REFUSED LOCALLY - %d MB is over the %d MB the receiver "+
			"accepts. Nothing was sent, and NOTHING WAS REMOVED.",
			sz/(1024*1024), receiverMaxBytes/(1024*1024))
		WritePendingNotice(exeDir, fmt.Sprintf(
			"Your last session was too big to send by itself: %d MB, and the limit is %d MB.\n\n"+
				"NOTHING WAS DELETED. Every picture and every note is still on this computer.\n\n"+
				"Open the window and press the button - a send you start yourself is not "+
				"limited in the same way, and it can be done in pieces.",
			sz/(1024*1024), receiverMaxBytes/(1024*1024)))
		return
	}

	in, _ := LoadOrCreateInstall(exeDir, logf)
	installID := in.ID
	up, err := SendExport(res, outDir, dest.URL, dest.Key, installID, true, logf)
	if err != nil {
		// KEEP EVERYTHING. A dropped connection must never cost somebody their
		// session, and clearAfterSend inside SendExport only fires after the
		// server confirms - so there is nothing to undo here, only to report.
		logf("auto-send: FAILED (%v) - nothing was removed. The file is still in the folder.", err)
		WritePendingNotice(exeDir, "The automatic send did not go through ("+err.Error()+
			").\n\nNOTHING WAS DELETED. Everything is still on this computer, and the "+
			"packaged file is in the captures folder. Press the button in the window to try again.")
		return
	}
	if !up.Sent {
		logf("auto-send: not confirmed - nothing was removed")
		WritePendingNotice(exeDir, "The automatic send was not confirmed by the server, "+
			"so nothing was deleted. Press the button in the window to try again.")
		return
	}

	logf("auto-send: %s", up.Note)
	WritePendingNotice(exeDir, "Your last session was sent automatically when you "+
		"finished playing.\n\n"+up.Note+
		"\n\nThe pictures were removed only after the server confirmed it had them. "+
		"The notes stay on this computer so you can see what you gave.")
}

// receiverMaxBytes mirrors MAX_BYTES in collector-receiver.worker.js.
//
// Duplicated across two languages, which is a real risk of drift - so it is
// named, commented on both sides, and the local check is deliberately the same
// number rather than a rounder "safe" one. A local limit lower than the real one
// would refuse sends the receiver would have taken.
const receiverMaxBytes int64 = 64 * 1024 * 1024

func fileSize(p string) int64 {
	fi, err := os.Stat(p)
	if err != nil {
		return 0
	}
	return fi.Size()
}
