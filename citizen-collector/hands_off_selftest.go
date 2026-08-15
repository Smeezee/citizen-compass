package main

// hands_off_selftest.go - unattended sending, and the promise it must not break.
//
// The load-bearing check in this file is the one that proves an install
// upgraded from 0.3.1 does NOT send by itself. Sleven's wife and his friend
// agreed to a README that says nothing is ever sent on its own. If that
// defaults the wrong way, the product contradicts a written promise on machines
// belonging to people who are not in this conversation, and nothing errors.

import (
	"os"
	"path/filepath"
	"regexp"
	"strconv"
	"strings"
)

func runHandsOffSelftest(check func(name string, ok bool, detail string)) {
	dir, err := os.MkdirTemp("", "cc-handsoff")
	if err != nil {
		check("HANDS-OFF: could not make a temp folder", false, err.Error())
		return
	}
	defer os.RemoveAll(dir)

	// -----------------------------------------------------------------
	// 1. THE DEFAULT IS ASK, DOWN EVERY PATH THAT CANNOT DECIDE
	// -----------------------------------------------------------------
	check("HANDS-OFF: no consent file at all reads as ASK",
		ReadSendMode(dir) == SendAsk,
		"a machine with nothing recorded would send unattended")

	// THE ONE THAT MATTERS. An install upgraded from 0.3.1 has a consent file
	// with no send_mode line in it. It must read as ask AND as never-offered,
	// because those drive different things: what it does now, and whether it
	// gets asked.
	upgraded := "agreed_version = 3\nagreed_at = 2026-08-14T00:00:00Z\ntool_version = 0.3.1\n"
	_ = os.WriteFile(filepath.Join(dir, consentFile), []byte(upgraded), 0o644)
	check("HANDS-OFF: an install upgraded from 0.3.1 reads as ASK",
		ReadSendMode(dir) == SendAsk,
		"THE PROMISE: 'It never sends anything on its own' is written on those machines")
	check("HANDS-OFF: and it is recorded as never having been offered the choice",
		!HasBeenOfferedSendChoice(dir),
		"it would never be asked, and would sit on ask forever without being told why")

	// Fail-closed on things that are not answers.
	for _, bad := range []string{
		"send_mode = \n",
		"send_mode = sometimes\n",
		"send_mode = AUTO\n",
		"send_mode\n",
		"# send_mode = automatic\n",
	} {
		_ = os.WriteFile(filepath.Join(dir, consentFile), []byte(upgraded+bad), 0o644)
		check("HANDS-OFF: "+strings.TrimSpace(strings.ReplaceAll(bad, "\n", ""))+" is not automatic",
			ReadSendMode(dir) == SendAsk,
			"a value this build does not understand must never mean 'upload it'")
	}

	// A commented-out line must not count as having been asked either.
	_ = os.WriteFile(filepath.Join(dir, consentFile), []byte(upgraded+"# send_mode = automatic\n"), 0o644)
	check("HANDS-OFF: a commented-out choice does not count as answered",
		!HasBeenOfferedSendChoice(dir),
		"a comment is not a decision")

	// -----------------------------------------------------------------
	// 2. NEGATIVE CONTROL - AUTOMATIC MUST ACTUALLY WORK
	// -----------------------------------------------------------------
	//
	// Without this, everything above would pass on a build that can only ever
	// return ask - which would silently remove the feature Sleven asked for.
	_ = os.WriteFile(filepath.Join(dir, consentFile), []byte(upgraded), 0o644)
	if err := WriteSendMode(dir, SendAutomatic); err != nil {
		check("HANDS-OFF: the choice can be recorded", false, err.Error())
	} else {
		check("HANDS-OFF: NEGATIVE CONTROL - a machine that chose automatic reads as automatic",
			ReadSendMode(dir) == SendAutomatic,
			"the person asked for hands-off and would not get it")
		check("HANDS-OFF: and it is recorded as having been offered",
			HasBeenOfferedSendChoice(dir),
			"it would be asked the same question on every launch")
	}

	// CHANGING IT BACK MUST WORK, and must not disturb the consent record - the
	// file's whole purpose is remembering WHEN somebody agreed and to WHAT.
	_ = WriteSendMode(dir, SendAsk)
	check("HANDS-OFF: the choice can be changed back to ask",
		ReadSendMode(dir) == SendAsk,
		"'you can change this later' would be false")
	body, _ := os.ReadFile(filepath.Join(dir, consentFile))
	check("HANDS-OFF: changing it preserves the consent record",
		strings.Contains(string(body), "agreed_at = 2026-08-14T00:00:00Z") &&
			strings.Contains(string(body), "agreed_version = 3"),
		"the record of when and to what somebody agreed was rewritten")
	check("HANDS-OFF: and does not duplicate the key",
		strings.Count(string(body), "send_mode =") == 1,
		"a second send_mode line would make the answer depend on read order")

	// -----------------------------------------------------------------
	// 3. THE LOCAL SIZE LIMIT MUST MATCH THE RECEIVER'S
	// -----------------------------------------------------------------
	//
	// The number lives in two languages. A local limit HIGHER than the
	// receiver's means unattended sends upload for minutes and are refused; a
	// local limit LOWER means refusing sends the receiver would have taken.
	// Read the actual worker source rather than trusting a comment.
	if wsrc, rerr := os.ReadFile("collector-receiver.worker.js"); rerr == nil {
		m := regexp.MustCompile(`MAX_BYTES\s*=\s*(\d+)\s*\*\s*1024\s*\*\s*1024`).FindSubmatch(wsrc)
		if m != nil {
			mb, _ := strconv.Atoi(string(m[1]))
			check("HANDS-OFF: the local size ceiling matches the receiver's",
				int64(mb)*1024*1024 == receiverMaxBytes,
				"worker says "+string(m[1])+" MB, this build refuses at "+
					strconv.FormatInt(receiverMaxBytes/(1024*1024), 10)+" MB")
		} else {
			check("HANDS-OFF: could not read MAX_BYTES out of the worker", true,
				"NOT COMPARED - the worker's limit could not be parsed, so drift "+
					"between the two numbers is unverified here")
		}
	} else {
		check("HANDS-OFF: worker source not beside the exe", true,
			"NOT COMPARED - this only runs from the source tree, and that is fine")
	}

	// -----------------------------------------------------------------
	// 4. AN UNATTENDED OUTCOME REACHES THE PERSON
	// -----------------------------------------------------------------
	check("HANDS-OFF: no notice reads as empty, not as an error",
		ReadPendingNotice(dir) == "",
		"a fresh install would show a message about a send that never happened")
	WritePendingNotice(dir, "Your last session was too big to send by itself.")
	got := ReadPendingNotice(dir)
	check("HANDS-OFF: an unattended outcome is recorded where a person will find it",
		strings.Contains(got, "too big to send"),
		"a refusal nobody is present for would exist only in the diagnostic log")
	check("HANDS-OFF: and the file's own comments are not shown back as content",
		!strings.Contains(got, "#"),
		"the person would be shown the housekeeping header")

	// -----------------------------------------------------------------
	// 5. AUTOSTART
	// -----------------------------------------------------------------
	//
	// NOT EXERCISED BY WRITING. EnableAutostart writes into the real per-user
	// Startup folder, and a selftest that installed an autostart entry on
	// whatever machine ran it would be its own bug. What is checked is that the
	// folder resolves and that the path is inside it - the parts that can be
	// wrong without anybody noticing.
	p := autostartPath()
	check("HANDS-OFF: the Startup folder resolves",
		p != "",
		"it could never be set to start with Windows, and would fail silently")
	if p != "" {
		startup, _ := knownFolder(folderIDStartup)
		check("HANDS-OFF: the startup entry lands in the real Startup folder",
			samePath(filepath.Dir(p), startup),
			"resolved to "+filepath.Dir(p)+" but Startup is "+startup)
		check("HANDS-OFF: it is a .lnk a person can see and delete",
			strings.EqualFold(filepath.Ext(p), ".lnk"),
			"a registry value cannot be deleted by somebody who does not know it exists")
		check("HANDS-OFF: removal instructions name the actual file",
			strings.Contains(AutostartRemovalInstructions(), p),
			"a person is told to remove something without being told where it is")
		check("HANDS-OFF: NOT EXERCISED - no autostart entry was created by this test", true,
			"EnableAutostart writes to the real Startup folder, so it is deliberately "+
				"not called here. Its effect is NOT verified by this run.")
	}

	// -----------------------------------------------------------------
	// 6. THE WATCHER DOES NOT FIGHT THE COLLECTOR
	// -----------------------------------------------------------------
	//
	// If the watcher claimed the collector's lock, the collector it starts would
	// see "already running" and exit - the 2026-08-14 restart-handover defect,
	// rebuilt deliberately.
	check("HANDS-OFF: the watcher's lock is not the collector's lock",
		watcherMutex != singleInstanceMutex,
		"the watcher would make every collector it starts exit immediately")
}
