package main

// send_mode.go - whether a finished session sends by itself, and who decided.
//
// # THE PROMISE THAT CONSTRAINS THIS
//
// README-FOR-TESTERS.txt, on the machines Sleven's wife and his friend are
// running right now, says in writing:
//
//	"It never sends anything on its own. Not on a timer, not in the background,
//	 not when you are not looking. The only thing that sends anything is you
//	 pressing the button."
//
// Sleven asked for hands-off collection, and that is a reasonable thing to want.
// It is NOT a reason to make that sentence retroactively false on a machine
// where somebody already read it and said yes.
//
// > "The objection was never to automation - it was to changing the deal after
// > people said yes."
//
// So: automatic sending is a CHOICE, offered in plain words on the consent
// screen, and an install that has never been offered the choice DEFAULTS TO ASK.
// Not to automatic. The default is the safe direction, and the safe direction
// here is the one that keeps an existing promise.
//
// # WHY THE DEFAULT IS A FUNCTION AND NOT A CONSTANT
//
// A zero value that means "automatic" would turn every unreadable settings
// file, every fresh struct and every parse failure into an unattended upload.
// The zero value of SendMode is ask, by construction, and every path that
// cannot determine an answer returns ask.

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"syscall"
	"time"
	"unsafe"
)

// SendMode is what happens when a session ends.
type SendMode int

const (
	// SendAsk is the zero value ON PURPOSE. Anything that fails to decide -
	// a missing file, a corrupt line, an unrecognised word - lands here, and
	// landing here means nothing leaves the machine unasked.
	SendAsk SendMode = iota

	// SendAutomatic sends when the game closes, because the person chose that.
	SendAutomatic
)

func (m SendMode) String() string {
	if m == SendAutomatic {
		return "automatic"
	}
	return "ask"
}

// sendModeKey is stored beside the consent answer rather than in
// collector-settings.txt, deliberately: it is part of what the person agreed
// to, and it should travel with the agreement rather than sit in a file the
// packager rewrites.
const sendModeKey = "send_mode"

// ReadSendMode reports what this machine chose.
//
// FAILS TO ASK, ALWAYS. An unreadable file, an absent key or a word this build
// does not recognise all mean "we do not know what they chose", and the only
// safe reading of that is the one that sends nothing without a person.
func ReadSendMode(dir string) SendMode {
	b, err := os.ReadFile(filepath.Join(dir, consentFile))
	if err != nil {
		return SendAsk
	}
	for _, line := range strings.Split(string(b), "\n") {
		line = strings.TrimSpace(line)
		if strings.HasPrefix(line, "#") {
			continue
		}
		k, v, ok := strings.Cut(line, "=")
		if !ok || strings.TrimSpace(k) != sendModeKey {
			continue
		}
		if strings.EqualFold(strings.TrimSpace(v), "automatic") {
			return SendAutomatic
		}
		return SendAsk
	}
	return SendAsk
}

// HasBeenOfferedSendChoice reports whether this machine has ever been asked.
//
// Distinct from "chose ask". An install upgraded from 0.3.1 has no send_mode
// line at all, and the difference between "was asked and said ask" and "has
// never been asked" is the whole of §2: the second one gets the question, once,
// and the first one is left alone.
func HasBeenOfferedSendChoice(dir string) bool {
	b, err := os.ReadFile(filepath.Join(dir, consentFile))
	if err != nil {
		return false
	}
	for _, line := range strings.Split(string(b), "\n") {
		line = strings.TrimSpace(line)
		if strings.HasPrefix(line, "#") {
			continue
		}
		if k, _, ok := strings.Cut(line, "="); ok && strings.TrimSpace(k) == sendModeKey {
			return true
		}
	}
	return false
}

// WriteSendMode records the choice, preserving everything else in the file.
//
// Rewritten line by line rather than regenerated, because this file holds the
// consent record and regenerating it from current constants would quietly
// restamp WHEN somebody agreed and to WHICH version. That record is the reason
// the file exists.
func WriteSendMode(dir string, m SendMode) error {
	p := filepath.Join(dir, consentFile)
	b, err := os.ReadFile(p)
	if err != nil {
		return err
	}
	lines := strings.Split(strings.ReplaceAll(string(b), "\r\n", "\n"), "\n")
	found := false
	for i, line := range lines {
		k, _, ok := strings.Cut(strings.TrimSpace(line), "=")
		if ok && strings.TrimSpace(k) == sendModeKey {
			lines[i] = fmt.Sprintf("%s = %s", sendModeKey, m)
			found = true
			break
		}
	}
	if !found {
		if len(lines) > 0 && strings.TrimSpace(lines[len(lines)-1]) == "" {
			lines = lines[:len(lines)-1]
		}
		lines = append(lines,
			"",
			"# When a session ends: 'automatic' sends without asking, 'ask' asks first.",
			"# Changed from the window at any time. Nothing is sent while this says ask.",
			fmt.Sprintf("%s = %s", sendModeKey, m),
			fmt.Sprintf("%s_chosen_at = %s", sendModeKey, time.Now().UTC().Format(time.RFC3339)),
			"")
	}
	return os.WriteFile(p, []byte(strings.Join(lines, "\n")), 0o644)
}

// sendChoiceText is the question, in the plain words the ruling specifies.
const sendChoiceText = `Citizen Collector

One more thing, and then it is set up.

When you finish playing, the collector has a session's worth of notes and
pictures ready to send. It can do that by itself, or it can ask you first.

    YES  - send automatically when I finish playing.
           Nothing to click. It packages the session and sends it when
           Star Citizen closes.

    NO   - ask me every time.
           It waits, and tells you there is something to send. Nothing
           leaves this computer until you press the button.

Either way, the pictures are only removed after the server confirms it
received them, and nothing is ever sent while the game is running.

You can change this later in the window. Neither answer is permanent.

Send automatically when you finish playing?`

// AskSendChoice offers the choice and records it. Returns the chosen mode.
//
// ASKED ONCE, and only when it has never been asked. An install that has already
// answered is never re-prompted - being asked the same question every launch is
// how a reasonable prompt becomes the reason somebody stops running a program.
func AskSendChoice(dir string, logf func(string, ...interface{})) SendMode {
	if logf == nil {
		logf = func(string, ...interface{}) {}
	}
	if HasBeenOfferedSendChoice(dir) {
		return ReadSendMode(dir)
	}

	const (
		mbYesNo        = 0x00000004
		mbIconQuestion = 0x00000020
		idYes          = 6
	)
	mode := SendAsk
	if messageBox("Citizen Collector", sendChoiceText, mbYesNo|mbIconQuestion) == idYes {
		mode = SendAutomatic
	}
	if err := WriteSendMode(dir, mode); err != nil {
		// COULD NOT RECORD IT. Do not act on an answer that was not saved: the
		// next launch would ask again and could get the other answer, and in the
		// meantime "automatic" would be running on an agreement with no record.
		logf("send mode: could not record your answer (%v) - staying on ask, and "+
			"you will be asked again next time.", err)
		return SendAsk
	}
	logf("send mode: %s (chosen on the consent screen, recorded in %s)", mode, consentFile)
	return mode
}

// messageBox is the one place a modal question is asked.
//
// Gathered here because three call sites had grown their own copy of the same
// six lines, and a UTF16PtrFromString error was silently ignored in two of them
// - which would show a box with no text and no way to tell what was being
// agreed to.
func messageBox(title, body string, flags uintptr) int {
	t, err := syscall.UTF16PtrFromString(title)
	if err != nil {
		return 0
	}
	m, err := syscall.UTF16PtrFromString(body)
	if err != nil {
		return 0
	}
	r, _, _ := modUser32.NewProc("MessageBoxW").Call(0,
		uintptr(unsafe.Pointer(m)), uintptr(unsafe.Pointer(t)), flags)
	return int(r)
}
