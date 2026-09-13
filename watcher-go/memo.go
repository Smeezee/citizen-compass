package main

// memo.go - correspondence between the people working on this project.
//
// ===========================================================================
// WHY THIS LOOKS LIKE AN OFFICE AND NOT LIKE A MESSAGE BUS
// ===========================================================================
//
// Sleven, 2026-08-30: "I'd prefer if we made it look like a human is operating
// this. So that way, if I ever hand this off to somebody, they know what to
// look at."
//
// So a message is a MEMO. It has To, From, Date, Subject and Status, it lands
// in a tray with the recipient's name on it, and when it has been answered it
// moves to the answered file. A person who has never seen this project can open
// `correspondence/` and know what they are looking at in about four seconds,
// which is the entire specification.
//
// NOTHING HERE IS ADDRESSED TO A CODENAME. `C1` and `Code` mean nothing to a
// stranger, so memos are addressed to the JOB:
//
//     Architecture   design, code review, the queue, the decisions
//     Build          the one who executes on the machine
//     Research       source-gathering and verification
//     Owner          Sleven. His alone: legal, going live, anything public.
//
// ===========================================================================
// WHY THIS IS IN THE WATCHER AND NOT A FOLDER SOMEBODY WRITES TO DIRECTLY
// ===========================================================================
//
// Because the inbox already exists and already sorts. On 2026-08-30 C1 built a
// separate `channel/` folder to avoid the watcher, having dropped two files in
// `inbox/` and watched them get filed into `docs/` within seconds. That was the
// wrong lesson: the watcher was doing its job and the files were not addressed
// to anybody. **A second sorting system beside the one that works is how a
// project ends up with two of everything** - which this repository has been
// bitten by three times, and the reason `OWNERS.md` exists at all.
//
// So: everything goes in the inbox, the header says who it is for, and the
// watcher files it. One way in, one sorter, one place to look.

import (
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"sort"
	"strings"
	"time"
)

// The trays. Lowercased folder names, human words, no codenames.
// A NEW DESK GETS A MAILING PATH WHEN IT IS CREATED, not when somebody asks
// whether it wants one. Sleven's ruling, 2026-09-08: the audit desk was stood
// up and spent a day able to send post and unable to receive any.
//
// THIS LIST IS A LIST AND NOT A FREE-TEXT FIELD ON PURPOSE. A memo to a desk
// that does not exist is REFUSED and sent to _needs_review, because a letter
// delivered to the wrong desk is worse than one that visibly failed to arrive.
// Adding a fifth valid name must not soften that, and
// TestAMemoToAnUnknownDeskIsRefused is what holds it.
var memoTrays = map[string]string{
	"architecture": "architecture",
	"build":        "build",
	"research":     "research",
	"audit":        "audit",
	"design":       "design",
	"owner":        "owner",
}

// `design` added 2026-09-08, and it arrived the OTHER WAY ROUND from `audit` -
// which is the useful part.
//
// audit:  the router learned first, and the CHECKER stayed silent until its own
//         drift assertion caught it on the next sweep.
// design: the checker, the README and the tray all learned first, and THE
//         ROUTER did not. A memo addressed to Design would have been refused
//         and sent to _needs_review - a desk with a tray it cannot receive post
//         into.
//
// Same defect, opposite direction, one day apart. **A desk is not a name in a
// list; it is four things** - the procedure, the tray, the router and the
// checker - and updating any three of them leaves something that looks
// finished. The checker catches a missing checker entry. Nothing but this
// comment catches a missing ROUTER entry, which is why the test beside it
// asserts every desk the README names can actually be delivered to.

var (
	reMemoTo      = regexp.MustCompile(`(?im)^To:\s*(.+?)\s*$`)
	reMemoFrom    = regexp.MustCompile(`(?im)^From:\s*(.+?)\s*$`)
	reMemoSubject = regexp.MustCompile(`(?im)^Subject:\s*(.+?)\s*$`)
	reMemoStatus  = regexp.MustCompile(`(?im)^Status:\s*(.+?)\s*$`)

	// A filename that already opens with an ISO date keeps it. Anchored and
	// followed by a separator, so `2026-08-31_x.md` matches and a file that
	// merely CONTAINS a date does not.
	reLeadingDate = regexp.MustCompile(`^\d{4}-\d{2}-\d{2}[_-]`)
)

// Memo is one letter.
//
// ToSig / FromSig hold a trailing parenthetical stripped off the address - the
// SIGNATURE, e.g. "(CIC)" in `From: Research (CIC)`. Architecture's order,
// 2026-09-12: a parenthetical after a valid desk name is a signature, not an
// address - so it is taken off before the desk is looked up, and KEPT, so the
// routing note still says exactly what the letter said.
type Memo struct {
	To      string
	From    string
	Subject string
	Status  string
	ToSig   string
	FromSig string
}

// reSignature matches "<name> (<anything without parens>)" at the end of an
// address. It needs a non-empty name BEFORE the parenthetical, so an address
// that is ONLY a parenthetical - `From: (CIC)` - is left whole and fails as an
// unknown desk rather than being stripped to nothing.
var reSignature = regexp.MustCompile(`^(.*\S)\s+(\([^()]*\))\s*$`)

// splitSignature returns the address without a trailing parenthetical, and
// the parenthetical itself ("" when there was none).
func splitSignature(s string) (name string, sig string) {
	s = strings.TrimSpace(s)
	if mm := reSignature.FindStringSubmatch(s); mm != nil {
		return mm[1], mm[2]
	}
	return s, ""
}

// rawFrom is the From: line as the letter wrote it, signature included - what a
// refusal must quote back so the writer recognises their own header.
func (m Memo) rawFrom() string {
	if m.FromSig == "" {
		return m.From
	}
	return m.From + " " + m.FromSig
}

// readMemo returns the memo and whether the text is one at all.
//
// IT IS STRICT ON PURPOSE. A document is a memo only if it carries To, From
// AND Subject. `routing_prefix_test.go` records what loose matching costs here:
// a WORK ORDER was filed as an update doc because "UPDATE" appeared inside
// "updateDate", and the amendment referencing it then pointed somewhere nobody
// would look. **Requiring three headers means an ordinary document that happens
// to contain the word "To:" is not quietly posted to somebody.**
func readMemo(text string) (Memo, bool) {
	first := text
	if len(first) > 4000 {
		// The header is at the top of a letter or it is not a header. This
		// also stops a quoted memo INSIDE a long document being routed as if
		// it were the document.
		first = first[:4000]
	}
	to := reMemoTo.FindStringSubmatch(first)
	from := reMemoFrom.FindStringSubmatch(first)
	subj := reMemoSubject.FindStringSubmatch(first)
	if to == nil || from == nil || subj == nil {
		return Memo{}, false
	}
	toName, toSig := splitSignature(to[1])
	fromName, fromSig := splitSignature(from[1])
	m := Memo{
		To:      strings.ToLower(toName),
		From:    fromName,
		Subject: strings.TrimSpace(subj[1]),
		Status:  "open",
		ToSig:   toSig,
		FromSig: fromSig,
	}
	if st := reMemoStatus.FindStringSubmatch(first); st != nil {
		m.Status = strings.ToLower(strings.TrimSpace(st[1]))
	}
	return m, true
}

// deskNames lists the real desks, in a stable order, for a refusal message.
//
// Sorted so the message does not shuffle between runs, and built from
// memoTrays so a desk added to the map cannot be missing from the sentence
// that tells somebody which desks exist.
func deskNames() string {
	names := make([]string, 0, len(memoTrays))
	for k := range memoTrays {
		names = append(names, k)
	}
	sort.Strings(names)
	if len(names) < 2 {
		return strings.Join(names, "")
	}
	return strings.Join(names[:len(names)-1], ", ") + " or " + names[len(names)-1]
}

// memoDestination decides which tray, or returns "" when the addressee is not
// somebody who works here.
//
// AN UNKNOWN ADDRESSEE IS NOT FILED AND NOT GUESSED AT. It goes to
// _needs_review like any other unrecognised drop, because a memo delivered to
// the wrong desk is worse than one that visibly failed to arrive.
// AN ANSWER TRAVELS BACK UP THE LINE IT CAME DOWN - 2026-09-10.
//
// Until today this function tested "is it answered" BEFORE it looked at who the
// memo was for, and sent every answer from every desk to correspondence/answered.
// So a desk could not reply to a desk; it could only reply to an archive. Sleven
// found it after a day of believing nothing was coming back: nine of
// Architecture's letters to him were in there and his tray showed one item.
//
// THE FIX IS ONE LOOKUP, AND THE OBVIOUS VERSION OF IT IS WRONG. Answering a memo
// appends a block and flips the status - IT DOES NOT CHANGE THE HEADERS. So an
// answered memo still says `To: Architecture`, and routing it on To: sends the
// answer straight back to the desk that just wrote it.
//
//	Status: Open      ->  open/<To:>     a question travelling out
//	Status: Answered  ->  open/<From:>   the answer travelling back
//	Status: Closed    ->  answered/      the thread is finished
//	Status: Done      ->  answered/      same as Closed
//
// The three status words were already in the code and were treated identically.
// Separating them costs nothing and makes `answered/` mean what its name says:
// threads that are FINISHED, rather than threads somebody replied to once.
//
// ONE COPY EXISTS AT EVERY MOMENT. It moves; it is never duplicated. Filing the
// answer in a tray AND in the archive was considered and refused: the tray copy
// is the one that gets edited and the archive copy rots beside it, and this
// repository has been bitten by two-of-everything three times.
func memoDestination(m Memo) (dir string, why string, ok bool) {
	if m.Status == "closed" || m.Status == "done" {
		return filepath.Join(correspondenceDir, "answered"),
			fmt.Sprintf("memo from %s, CLOSED — the thread is finished", m.From), true
	}
	if m.Status == "answered" {
		// From: HAS NEVER BEEN VALIDATED, because until now nothing routed on
		// it. To: is lowercased and checked against the desk list; From: is
		// free text, and a letter in the live archive today says
		// `From: Research (CIC)`, which matches no tray.
		//
		// It is validated HERE ONLY - on an answered memo, where it decides
		// delivery. Refusing an OPEN letter over an odd From: would break
		// working traffic for nothing.
		from := strings.ToLower(strings.TrimSpace(m.From))
		tray, known := memoTrays[from]
		if !known {
			return "", fmt.Sprintf("answered memo from %q, which is not one of "+
				"%s — an answer is delivered on From:, so an unknown sender "+
				"cannot be delivered and is not guessed at", m.rawFrom(), deskNames()), false
		}
		sig := ""
		if m.FromSig != "" {
			sig = fmt.Sprintf(" (From: signature %s kept, not used as an address)", m.FromSig)
		}
		if from == m.To {
			// A desk answering its own memo has nobody to send it back to.
			return filepath.Join(correspondenceDir, "answered"),
				fmt.Sprintf("memo from %s to itself, answered — filed to the "+
					"archive: there is no other desk to return it to", m.From), true
		}
		return filepath.Join(correspondenceDir, "open", tray),
			fmt.Sprintf("ANSWER for %s from %s — %s%s", tray, m.To, m.Subject, sig), true
	}
	tray, known := memoTrays[m.To]
	if !known {
		// THE LIST IS DERIVED, NOT TYPED.
		//
		// This message read "not one of architecture, build, research or
		// owner" as a hand-written string. Adding the audit desk on
		// 2026-09-08 made it wrong instantly: somebody who misspelled a desk
		// was told a list that omitted a real one, which is worse than no list
		// because it reads as authoritative.
		//
		// Caught by a test asserting the message names every desk in the map -
		// written at the same time as the desk itself, and it failed on the
		// first run.
		return "", fmt.Sprintf("memo addressed to %q, which is not one of %s",
			m.To, deskNames()), false
	}
	return filepath.Join(correspondenceDir, "open", tray),
		fmt.Sprintf("memo for %s from %s — %s", tray, m.From, m.Subject), true
}

// clearOpenCopy removes the stale copy of a memo that has just been answered.
//
// FOUND ON THE LIVE PATH, 2026-08-30, within minutes of the router going in.
// Answering a memo wrote the answered copy to answered/ and LEFT THE ORIGINAL
// SITTING IN THE OPEN TRAY, so the same memo existed twice:
//
//	open/owner/2026-08-30_the-watcher-binary-swap.md   4595 bytes  Status: Open
//	answered/2026-08-30_the-watcher-binary-swap.md     5984 bytes  Status: Answered
//
// A question that has been answered still reads as waiting. The tray stops
// meaning what it says, which is the only thing a tray is for.
//
// TestAnAnsweredMemoLeavesTheOpenTray did not catch it, and its name is why it
// looked covered: it asserts memoDestination RETURNS a path containing
// "answered" and not "open". That is where the memo GOES. Nothing asserted that
// it LEAVES anywhere, because nothing touched the filesystem. The name claimed
// the behaviour; the body checked a string.
//
// MOVED, NOT DELETED - hard rule 1. The superseded copy goes to _to_delete/ with
// a timestamp, so an answer that was filed against the wrong original can still
// be reconstructed.
//
// `skip` IS THE TRAY THE ANSWER WAS JUST FILED INTO, AND WITHOUT IT THIS
// FUNCTION DELETES THE ANSWER IT IS CLEANING UP AFTER.
//
// This loop was safe for exactly as long as answers went to answered/, which it
// never scans. From 2026-09-10 an answer lands in open/<From:>, which IS one of
// these trays - and the loop takes the FIRST hit it finds. Go randomises map
// iteration order, so it would have moved the stale copy on some runs and the
// answer on others. A defect that works most of the time is worse than one that
// never does, and the failing case would have been a lost reply.
func clearOpenCopy(base string, skip string) string {
	keep := filepath.Join(filepath.Dir(correspondenceDir), "_to_delete")
	for _, tray := range memoTrays {
		if tray == skip {
			continue
		}
		p := filepath.Join(correspondenceDir, "open", tray, base)
		if st, err := os.Stat(p); err != nil || st.IsDir() {
			continue
		}
		if err := os.MkdirAll(keep, 0o755); err != nil {
			return ""
		}
		to := filepath.Join(keep, base+".superseded-"+
			time.Now().Format("20060102-150405"))
		if err := os.Rename(p, to); err == nil {
			return tray
		}
	}
	return ""
}

// A CLOSED THREAD MUST CARRY ITS RECORD - refused at FILING time, 2026-09-12.
//
// checks/_verify_correspondence.py requires every Closed or Done letter in
// answered/ to carry an ANSWERS: or a CLOSED: line with 20+ characters under it.
// Until today the router filed a malformed close into answered/ anyway, and the
// control found it hours later, in a sweep - where the cost was a red sweep and
// a blocked deploy. On 2026-09-12 that happened to two sweeps in a row: three
// letters closed with a bare "CLOSED." (a full stop where the marker has a
// colon) landed fourteen minutes into a 44-minute sweep.
//
// Architecture's ruling: refuse it HERE, the way a memo to a desk that does not
// exist is refused - to _needs_review with the reason on it - where the cost is
// a bounce and a one-line fix by whoever still has the file open.
//
// THE RULE IS THE CONTROL'S, SPELLED THE SAME WAY, so the two cannot drift into
// disagreeing about what a record is: the same two markers, the same optional
// leading bold, case-insensitive, and the length measured on everything after
// the marker. An Answered memo is NOT held to this - it is routed on From: and
// the control holds it to ANSWERS: separately.
var (
	reAnswersLine = regexp.MustCompile(`(?im)^\s*(?:\*\*)?ANSWERS:`)
	reClosedLine  = regexp.MustCompile(`(?im)^\s*(?:\*\*)?CLOSED:`)
)

// THE STATUS LINE IS REQUIRED, AND ITS VALUE COMES FROM A LIST - 2026-09-12.
//
// readMemo defaults a missing Status: to "open", so a letter with no Status line
// filed silently as if it were open while BOOT.md and every tray control skipped
// it: 38 such letters across four trays on the night it was measured. The list is
// the one ON DISK (Open 90, Answered 304, Closed 56) plus Done, which the close rule
// already accepts - measured, not invented (Architecture's order). BOOT.md reads the
// same map to count what it could not read, so the two cannot disagree.
var memoStatusValues = map[string]bool{"open": true, "answered": true, "closed": true, "done": true}

// statusProblem returns why a memo's Status line cannot be filed, or "".
func statusProblem(text string) string {
	head := text
	if len(head) > 4000 {
		head = head[:4000]
	}
	st := reMemoStatus.FindStringSubmatch(head)
	if st == nil {
		return "memo with no Status: line - BOOT.md and every tray control would skip it. " +
			"Add `Status: Open` (or Answered, Closed, Done) under the Subject line and drop it again"
	}
	v := strings.TrimSpace(st[1])
	if !memoStatusValues[strings.ToLower(v)] {
		return fmt.Sprintf("memo whose Status: is %q - it must be exactly one of Open, Answered, "+
			"Closed, Done; put any qualification in the body and drop it again", v)
	}
	return ""
}

const closedRecordMin = 20

// closedRecord reports whether a Closed/Done letter carries its record.
func closedRecord(text string) (ok bool, why string) {
	longest, found := 0, false
	for _, re := range []*regexp.Regexp{reAnswersLine, reClosedLine} {
		if loc := re.FindStringIndex(text); loc != nil {
			found = true
			if n := len([]rune(strings.TrimSpace(text[loc[1]:]))); n > longest {
				longest = n
			}
		}
	}
	if !found {
		return false, "closed memo with neither an ANSWERS: nor a CLOSED: line - a " +
			"finished thread with no record is as invisible as an unanswered one. " +
			"Add `CLOSED:` (with the colon) above the closing paragraph and drop it again"
	}
	if longest < closedRecordMin {
		return false, fmt.Sprintf("closed memo whose closing marker has %d character(s) "+
			"under it, under the %d a record needs - that is a tick, not a record",
			longest, closedRecordMin)
	}
	return true, ""
}

// classifyMemo routes a memo. Returns handled=false when the file is not one.
func classifyMemo(path string, text string) (note string, dest string, handled bool, err error) {
	m, isMemo := readMemo(text)
	if !isMemo {
		return "", "", false, nil
	}
	if why := statusProblem(text); why != "" {
		n, d, e := routeSimple(path, needsReviewDir, why)
		return n, d, true, e
	}
	if m.Status == "closed" || m.Status == "done" {
		if ok, why := closedRecord(text); !ok {
			n, d, e := routeSimple(path, needsReviewDir, why)
			return n, d, true, e
		}
	}
	dir, why, ok := memoDestination(m)
	if !ok {
		n, d, e := routeSimple(path, needsReviewDir, why)
		if e == nil {
			// A refused ANSWER tells the desk that wrote it (memo_bounce_notice.go).
			// Only after the refusal itself succeeded, and it never changes where
			// the letter went.
			n += tellTheAnsweringDesk(m, filepath.Base(path), d, why)
		}
		return n, d, true, e
	}
	if mkErr := os.MkdirAll(dir, 0o755); mkErr != nil {
		return "", "", true, mkErr
	}
	// The date goes on the FILENAME so a tray reads in order at a glance,
	// which is what a person wants from a tray.
	//
	// ANY leading ISO date counts, not just TODAY's. This checked
	// `HasPrefix(base, stamp)` against today's stamp alone, so a memo carrying
	// any other date got a second one stapled in front of it:
	//
	//     2026-08-30_2026-08-31_owners-md-is-yours-and-says-so-twice.md
	//
	// Seen twice on 2026-08-30, on memos written with the next day's date. It is
	// cosmetic, and it sorts a tray by the day the file was FILED while showing
	// the day it was WRITTEN - two dates, neither labelled.
	base := filepath.Base(path)
	if !reLeadingDate.MatchString(base) {
		base = time.Now().Format("2006-01-02") + "_" + base
	}
	// A RETURNED ANSWER CAN BE CLEARED FROM THE TRAY IT CAME HOME TO - 2026-09-12.
	//
	// Research found it on its own tray: an answer routed home to open/research,
	// and dropping it back in inbox/ to clear it - what the README says to do -
	// re-filed it as a fresh arrival, and routeTo's collision rule put a second,
	// timestamped copy beside the first. Two identical answers, both open,
	// neither filed; and every further attempt made another. A tray that can
	// only fill up stops meaning anything.
	//
	// THE RULE IS NARROW ON PURPOSE: an Answered memo arriving at an open tray
	// that ALREADY HOLDS A BYTE-IDENTICAL COPY is a clear-out, so it is filed to
	// answered/ and the tray copy moves aside to _to_delete/ (rule 1). A CHANGED
	// answer of the same name is new content - a second round - and keeps the
	// existing behaviour: the newest sits in the tray, the older is archived.
	// Filed FIRST, moved aside SECOND, so a filing failure leaves the tray intact.
	if m.Status == "answered" && filepath.Dir(dir) == filepath.Join(correspondenceDir, "open") {
		home := filepath.Join(dir, base)
		prev, perr := os.ReadFile(home)
		cur, cerr := os.ReadFile(path)
		if perr == nil && cerr == nil && string(prev) == string(cur) {
			archive := filepath.Join(correspondenceDir, "answered")
			if mkErr := os.MkdirAll(archive, 0o755); mkErr != nil {
				return "", "", true, mkErr
			}
			n, d, e := routeTo(path, filepath.Join(archive, base), why+
				" — CLEARED: an identical copy was already in the "+filepath.Base(dir)+
				" tray, so this drop files the answer to answered/")
			if e == nil {
				keep := filepath.Join(filepath.Dir(correspondenceDir), "_to_delete")
				if os.MkdirAll(keep, 0o755) == nil && os.Rename(home, filepath.Join(keep,
					base+".superseded-"+time.Now().Format("20060102-150405"))) == nil {
					n += " (the tray copy moved to _to_delete)"
				}
			}
			return n, d, true, e
		}
	}
	n, finalDest, e := routeTo(path, filepath.Join(dir, base), why)
	// An answer supersedes the open copy. Done AFTER the answered file is
	// safely filed, never before: if routeTo fails, the original must still be
	// in its tray rather than moved aside on the strength of an answer that
	// never landed.
	//
	// THE GATE IS "IS IT ANSWERED", NOT "DID IT GO TO answered/". Those were the
	// same question until today. Now an answer lands in a tray, and keeping the
	// old gate would leave the stale open copy sitting in the original tray -
	// the same letter reading as waiting in one place and answered in another,
	// which is the exact defect this function was written for on 2026-08-30.
	answered := m.Status == "answered" || m.Status == "closed" || m.Status == "done"
	if e == nil && answered {
		skip := ""
		if filepath.Dir(dir) == filepath.Join(correspondenceDir, "open") {
			skip = filepath.Base(dir)
		}
		if tray := clearOpenCopy(base, skip); tray != "" {
			n += fmt.Sprintf(" (superseded the open copy in %s)", tray)
		}
	}
	return n, finalDest, true, e
}
