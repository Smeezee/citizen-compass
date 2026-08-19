package main

// activity.go - what the program did, in words, where the person can see it.
//
// ===========================================================================
// V1 §7: NOTHING THE PROGRAM DOES IS INVISIBLE TO THE PERSON IT IS HAPPENING TO
// ===========================================================================
//
// Everything this program does is already written down - in collector-auto.log,
// in a technical register, in a file nobody opens while flying. From the
// window's point of view the collector has always been a headline and a row of
// counts: "41 captures". WHICH forty-one, and why, and when, are answerable only
// by opening a log and reading timestamps.
//
// The worst version of that gap has a name. Somebody presses Alt+F3 by accident,
// nothing visible happens, and days later they find a picture of their desktop
// in a folder and do not know what made it. The order is explicit:
//
//	"An Alt+F3 press appears in it and NAMES THE KEYS - so somebody who hits it
//	 by accident understands what they did rather than finding a mystery picture
//	 later."
//
// So the activity list is not a log viewer. It is the program saying what it
// just did, in the words the person would use, as it happens.
//
// ===========================================================================
// WHY IT IS A SEPARATE STREAM AND NOT A TAIL OF THE LOG FILE
// ===========================================================================
//
// The log is for diagnosis: paths, byte counts, poll intervals, the reason a
// gate refused something. Showing that in the window would be showing a person
// the wrong thing loudly - and worse, it would make the window's honesty depend
// on the log's formatting never changing.
//
// This is a small, deliberate list of events written in plain language at the
// point they happen. If an event is worth telling somebody about, it is added
// here explicitly. That is a cost per event, and it is the right cost: it makes
// "is this visible to the person?" a question somebody has to answer when they
// add a feature, rather than something that happens by accident or not at all.

import (
	"fmt"
	"strings"
	"sync"
	"time"
)

// activityMax is how far back the list scrolls.
//
// A session is a few hours. At the busiest this records a line per capture and
// a line per held key, so a thousand lines is a long evening with room to spare,
// and it is a few hundred kilobytes at worst. Old lines are dropped from the
// FRONT, so the list is always the most recent history rather than the first
// thousand things that happened and then silence.
const activityMax = 1000

// ActivityEntry is one thing the program did.
type ActivityEntry struct {
	At   time.Time
	Text string
}

// activityFeed is the session's running list. One per process.
type activityFeed struct {
	mu      sync.Mutex
	entries []ActivityEntry

	// version increments on every add, so the window can ask "is there anything
	// new?" without copying a thousand strings on a timer.
	version uint64
}

var theActivity = &activityFeed{}

// Activity adds one line, in plain language.
//
// Called from wherever something happens that a person would want to know
// about. Deliberately a package-level function: the alternative is threading a
// feed pointer through every call site, and a feature that is awkward to reach
// is a feature people quietly stop reaching for.
func Activity(format string, args ...interface{}) {
	theActivity.add(fmt.Sprintf(format, args...))
}

func (f *activityFeed) add(text string) {
	text = strings.TrimSpace(text)
	if text == "" {
		return
	}
	f.mu.Lock()
	defer f.mu.Unlock()
	f.entries = append(f.entries, ActivityEntry{At: time.Now(), Text: text})
	if len(f.entries) > activityMax {
		// Drop from the front. Keeping the OLDEST thousand would leave the
		// window frozen on the start of the session, which reads exactly like a
		// program that has stopped working.
		f.entries = append([]ActivityEntry(nil), f.entries[len(f.entries)-activityMax:]...)
	}
	f.version++
}

// Snapshot returns the list as it stands, oldest first, and its version.
func (f *activityFeed) Snapshot() ([]ActivityEntry, uint64) {
	f.mu.Lock()
	defer f.mu.Unlock()
	out := make([]ActivityEntry, len(f.entries))
	copy(out, f.entries)
	return out, f.version
}

// Version is what the window polls. Cheap: no copying.
func (f *activityFeed) Version() uint64 {
	f.mu.Lock()
	defer f.mu.Unlock()
	return f.version
}

// Line renders one entry the way the window shows it.
func (e ActivityEntry) Line() string {
	return e.At.Format("15:04:05") + "  " + e.Text
}

// ---------------------------------------------------------------------------
// The events. Written as functions rather than call-site strings so the wording
// is in one place and can be read as a set - which is how you notice that one
// of them is jargon.
// ---------------------------------------------------------------------------

// ActivityCapture is THE ONE THE ORDER NAMES. It always states the keys.
//
// `keys` is the hotkey's canonical name - "Alt+F3" - and it is not optional. A
// line that says "picture taken" leaves the accidental presser exactly where
// they started: something happened, they do not know what they did.
func ActivityCapture(keys, file string, why string) {
	if keys == "" {
		// A capture with no key named should be impossible - but if it ever
		// happens, say so rather than printing a blank where the answer goes.
		keys = "an unknown key"
	}
	if file == "" {
		Activity("You pressed %s - picture taken.", keys)
		return
	}
	if why != "" {
		Activity("You pressed %s - picture taken (%s): %s", keys, why, file)
		return
	}
	Activity("You pressed %s - picture taken: %s", keys, file)
}

// ActivityHeldKeyStart / ActivityHeldKeyEnd - the held keys, RECORDED here
// rather than photographed. §6 removed the pictures; §7 keeps the fact.
func ActivityHeldKeyStart(what string) {
	Activity("You started %s - recording it in the diary, not photographing it.", what)
}

func ActivityHeldKeyEnd(what string, seconds int) {
	if seconds > 0 {
		Activity("You finished %s after %d seconds - it is in the diary.", what, seconds)
		return
	}
	Activity("You finished %s - it is in the diary.", what)
}
