package main

// memo_bounce_notice.go - a bounced answer is no longer invisible to the desk
// that wrote it. Architecture's order, 2026-09-13
// (memo_build_boot-line-go-the-844-are-not-a-chore-and-a-bounced-answer-is-
// invisible, item 3): "when the router refuses an answer, it drops a notice into
// the SENDER's tray naming the letter, the reason and the _needs_review/ path."
//
// THE INCIDENT. Three of Architecture's answers to Grok bounced at 03:34, 04:22
// and 04:47 because they were addressed back to `From: Grok (Design / CIC)`, and
// Architecture found out at 08:40 - because Build happened to tell it. For five
// hours a desk believed three rulings had arrived.
//
// WHO WROTE THE ANSWER. Not the letter's From: - that unresolvable name is the
// reason it bounced. The desk that answers a letter is the one it was addressed
// TO, so the notice goes to To:'s tray.
//
// WHAT DOES NOT CHANGE. The answer still lands in _needs_review/ exactly as
// before; the notice is written only AFTER that move succeeded, and a notice that
// cannot be written is recorded in the router's note rather than failing the
// route. A deliverable answer produces no notice; a letter refused for any other
// reason produces none; if To: is not a desk either there is nobody to tell, and
// the note says so. A re-dropped bounce is told once - the notice is never
// overwritten.

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"time"
)

func tellTheAnsweringDesk(m Memo, base, bouncedTo, why string) string {
	// Only an ANSWER. Today the only refusal an answered letter can reach through
	// memoDestination is the unknown sender, so no second guard is kept here: a
	// guard no test can make fail is not a guard (rule 12).
	if m.Status != "answered" {
		return ""
	}
	tray, knownTo := memoTrays[m.To]
	if !knownTo {
		return "; nobody told - To: is not a desk either"
	}
	stem := reLeadingDate.ReplaceAllString(base, "")
	name := time.Now().Format("2006-01-02") + "_memo_" + tray + "_undeliverable-answer_" + stem
	p := filepath.Join(correspondenceDir, "open", tray, name)
	if _, err := os.Stat(p); err == nil {
		return "; the answering desk (" + tray + ") was already told: " + p
	}
	rel := bouncedTo
	if r, err := filepath.Rel(filepath.Dir(correspondenceDir), bouncedTo); err == nil {
		rel = filepath.ToSlash(r)
	}
	title := strings.ToUpper(tray[:1]) + tray[1:]
	body := fmt.Sprintf("# Memo\n\n"+
		"To:      %s\n"+
		"From:    Build (router)\n"+
		"Subject: Your answer could not be delivered: %s\n"+
		"Status:  Open\n\n"+
		"**The router refused an answer this desk wrote, and nothing else would have told you.**\n\n"+
		"    the letter   %s\n"+
		"    now at       %s\n"+
		"    reason       %s\n\n"+
		"**Nothing was lost.** The answer is intact where it now sits. It was addressed back to "+
		"`From: %s`, which is not a desk, so it could not be delivered and was not guessed at.\n\n"+
		"**Re-sending it unchanged bounces again.** The letter's writer can re-send with a `From:` "+
		"line that names a real desk - that header is theirs, not the answering desk's, to edit.\n\n"+
		"*Build (router), %s.*\n",
		title, m.Subject, base, rel, why, m.rawFrom(), time.Now().Format("2006-01-02"))
	if err := os.WriteFile(p, []byte(body), 0o644); err != nil {
		return "; the answering desk could NOT be told: " + err.Error()
	}
	return "; the answering desk (" + tray + ") was told: " + p
}
