package main

// consent.go - the first thing a new person sees.
//
// # WHY THIS EXISTS
//
// Everything else in this tool is about being careful with data. None of it
// means anything if the person running it never agreed to any of it.
//
// Up to now the only reason that was acceptable is that the only person running
// it built it. The moment it lands on Sleven's wife's machine or his friend's,
// "he explained it to me once" is not consent - and neither is a README nobody
// opens. So the program asks, in its own words, before it reads anything.
//
// # THE SHAPE OF THE PROMISE, IN THE ORDER IT MATTERS
//
// What it reads. What it never reads. That nothing leaves the machine unless
// they press a button. How to stop it. In that order, because "what do you take
// from me" is the question people actually have and burying it under features
// is how tools lose trust.
//
// # WHY A WINDOWS MESSAGE BOX AND NOT A PRETTY SCREEN
//
// It has to appear in EVERY mode - the window, --auto, and a shortcut somebody
// made - before the first log line is read. A dialog inside the webview UI
// would miss two of those three, and the two it misses are the unattended ones
// that read the most.
//
// # IT FAILS CLOSED
//
// No answer, a closed dialog, an error creating the file: all of them mean no.
// A tool that starts collecting because it could not ask has learned nothing
// from having asked.

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"syscall"
	"time"
	"unsafe"
)

const consentFile = "collector-consent.txt"

// consentVersion is bumped when the PROMISE changes - not when the code does.
//
// Bumping it asks everybody again. That is the point: agreement to the old
// terms is not agreement to new ones, and quietly widening what a tool collects
// while holding on to a year-old yes is the exact behaviour this file exists to
// avoid.
// Version 4, 2026-08-30. The chat promise was stronger than the mechanism.
// "Your chat. Chat is never sampled, at all." was true only in the sense that
// nothing was sampled from anywhere - there is no reader. But a picture is the
// whole Star Citizen window, and chat drawn inside that window is inside the
// picture. Q45 makes those pictures longer-lived, which is what made a comfort-
// able sentence into one that would soon be false.
//
// What replaced it is the promise the program can actually keep, and it is a
// stronger one: no picture is ever taken by itself. no_auto_capture_selftest.go
// drives the real loop with every trigger that ever fired a capture, requires
// ZERO pictures, then presses a key and requires one. The person chooses the
// moment, and the text now says what follows from that rather than what would
// be nicer to read.
//
// Sleven approved the wording, 2026-08-30. Hard rule 8: this text is his.
//
// Version 2, 2026-08-08. Three things in version 1 became untrue and it is
// worth writing down which, because every one of them drifted the same way -
// the code grew a capability and the promise did not move with it:
//
//  1. "Nothing is uploaded, ever. There is no server." There is now. SEND MY
//     DATA posts to a receiver. Still a button press, still never automatic,
//     but "there is no server" was a promise about architecture and the
//     architecture changed.
//  2. "Player names are replaced before the file is written." True of the file
//     that gets SENT. Not true of the file on their own disk, which now holds
//     raw names on purpose so the scrubbing can be checked and improved. That
//     distinction matters to the person whose disk it is.
//  3. The updater. The program can now download a new version of itself and
//     replace itself with it. Nobody agreed to that, because when they agreed
//     it could not do it.
//
// The rule this file already stated - "quietly widening what a tool collects
// while holding on to a year-old yes is the exact behaviour this file exists to
// avoid" - is the rule that was about to be broken. Bumping asks everybody
// again, including Sleven.
// Version 3, 2026-08-13. Sleven's decision on screenshots, and the promise had
// been quietly soft on the one thing people care most about.
//
// Version 2 said screenshots "are NOT sent unless you specifically ask for
// them" and left the rest to a tick box. That is true about the mechanism and
// misleading about the outcome: the whole reason the box exists is that the
// pictures are wanted, and a promise that leads with what does NOT happen is
// one somebody can agree to without understanding what does.
//
// Three things are now said plainly instead:
//
//  1. Screenshots ARE uploaded when you send. Not "unless you ask" - it is what
//     sending includes.
//  2. A picture can show your handle and the handles of players near you.
//     Version 2 said this. It stays, and it moves up.
//  3. They are used INTERNALLY and are never published, and nothing extracted
//     from a picture ever carries anybody's name. Neither was stated at all,
//     and they are the two facts that make the first two acceptable.
//
// Bumping asks everybody again. Agreement to the old wording is not agreement
// to this one.
const consentVersion = 4

const consentText = `Citizen Collector

This program watches Star Citizen while you play and writes down what the
game itself records, so the community can build a better map of prices,
ships and places.

WHAT IT READS
  - Star Citizen's own Game.log, the file the game already writes.
  - Pictures of the Star Citizen window, and nothing else on your screen.

WHAT IT NEVER READS
  - Any other program. It checks the window belongs to Star Citizen first.
  - Your password, your account, your email, your files.

WHAT IT NEVER DOES ON ITS OWN
  It never takes a picture by itself. Not on a timer, not when you dock,
  not when you open a shop. Every picture exists because YOU pressed the
  key.

  So it does not go hunting for your chat - but a picture is the whole
  Star Citizen window, and if chat is open when you press the key, chat
  is in it. Close it first, or delete the picture afterwards. They sit
  on your own disk until you press SEND MY DATA.

WHAT IS KEPT ON YOUR OWN DISK
  Everything it notices, including player names it saw in the log - yours
  and other people's. It is kept as-is so the names can be checked before
  they are removed. That file never leaves this computer on its own.

WHAT LEAVES YOUR COMPUTER, AND ONLY WHEN YOU SAY SO
  Nothing is sent automatically. Ever.

  When you press SEND MY DATA, and only then, the program packages what it
  has collected and uploads it. Before it does, every player name in the
  written-down data is replaced with a made-up one - yours and everyone
  else's.

  PICTURES OF YOUR SCREEN ARE PART OF WHAT IS SENT. Read this bit twice.

  A picture is not name-swapped and cannot be. It can show YOUR handle, the
  handles of players standing near you, your party list, and anything else
  the game had on screen at that moment.

  What happens to them:

    - They are looked at by us, to read prices and stock off the screen.
      That is the entire reason they are wanted.
    - They are NEVER PUBLISHED. They do not go on the website, into a
      public dataset, or anywhere someone else can see them.
    - Anything we take OUT of a picture - a price, an item, a place -
      carries no name. Not yours, not anybody's. The numbers get used;
      the names do not survive being read.

  If that is not a trade you want to make, do not send. You can press
  PACKAGE instead, which writes the same file to your own disk and sends
  nothing. Then it is yours to look at, or send by hand, or delete.

UPDATING ITSELF
  It checks whether a newer version exists and tells you in the window.
  It does not install anything unless you click update. When you do, the
  download is checked against a fingerprint published with it and is
  thrown away if it does not match.

HOW TO STOP IT
  Close the window. Delete the folder. Nothing is left behind.

Do you agree to run it on these terms?`

// HasConsent reports whether this machine has agreed to the current version.
func HasConsent(dir string) bool {
	b, err := os.ReadFile(filepath.Join(dir, consentFile))
	if err != nil {
		return false
	}
	for _, line := range strings.Split(string(b), "\n") {
		k, v, ok := strings.Cut(strings.TrimSpace(line), "=")
		if !ok {
			continue
		}
		if strings.TrimSpace(k) == "agreed_version" {
			var n int
			if _, err := fmt.Sscanf(strings.TrimSpace(v), "%d", &n); err == nil && n >= consentVersion {
				return true
			}
		}
	}
	return false
}

func recordConsent(dir string) error {
	var b strings.Builder
	b.WriteString("# citizen-collector - your answer, kept here so you are not asked again.\n")
	b.WriteString("#\n")
	b.WriteString("# Delete this file to be asked again. Change agreed_version to 0 to\n")
	b.WriteString("# withdraw - the program will ask on the next start and will not\n")
	b.WriteString("# collect anything until you say yes.\n\n")
	fmt.Fprintf(&b, "agreed_version = %d\n", consentVersion)
	fmt.Fprintf(&b, "agreed_at = %s\n", time.Now().UTC().Format(time.RFC3339))
	fmt.Fprintf(&b, "tool_version = %s\n", Version)
	return os.WriteFile(filepath.Join(dir, consentFile), []byte(b.String()), 0o644)
}

// AskConsent shows the terms and returns true only on an explicit yes.
func AskConsent(dir string, logf func(string, ...interface{})) bool {
	if logf == nil {
		logf = func(string, ...interface{}) {}
	}
	if HasConsent(dir) {
		return true
	}

	const (
		mbYesNo        = 0x00000004
		mbIconQuestion = 0x00000020
		idYes          = 6
	)
	proc := modUser32.NewProc("MessageBoxW")
	t, _ := syscall.UTF16PtrFromString("Citizen Collector - before we start")
	m, _ := syscall.UTF16PtrFromString(consentText)
	r, _, _ := proc.Call(0,
		uintptr(unsafe.Pointer(m)), uintptr(unsafe.Pointer(t)),
		uintptr(mbYesNo|mbIconQuestion))

	if int(r) != idYes {
		// FAIL CLOSED. A dialog that was closed, dismissed, or never rendered
		// is not a yes. This branch is also what happens when the message box
		// cannot be shown at all, which is exactly when guessing would be worst.
		logf("consent: not granted - nothing has been read and nothing was written. " +
			"Start it again if you change your mind.")
		return false
	}
	if err := recordConsent(dir); err != nil {
		logf("consent: you agreed, but the answer could not be saved (%v) - you will "+
			"be asked again next time.", err)
	} else {
		logf("consent: granted and recorded in %s", consentFile)
	}
	return true
}
