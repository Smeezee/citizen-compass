package main

// window_rows.go - what the window shows, as data.
//
// # THIS FILE IS THE ANSWER TO "IS THIS STILL CHEAP TO CHANGE IN 2046"
//
// Adding a status row is ONE ENTRY IN THIS LIST. The window reads the list,
// creates a label and a value for each, lays them out, and updates them on a
// timer. No measuring, no hand-placed coordinates, no second place to remember.
//
// The old window hand-wrote every row into an HTML template and then hand-wrote
// the JavaScript that filled it in, so a new row was two edits in two languages
// that could disagree - and did, which is how a status could sit on a
// placeholder while the value behind it was fine.
//
// # WHY VALUE IS A FUNCTION AND NOT A STRING
//
// A row has to be able to say "not registered" in the same breath as saying
// what the hotkey is, and the window must never format anything itself. The
// function receives the state that ui_state.go already built - the same state
// the old window used - so there is exactly one place that decides what any of
// this MEANS.

import "fmt"

// rowContext is everything a row may render from.
//
// Deliberately small. It carries the measured state and the install's own
// folder; a row that needs more than that is asking a question the window
// should not be answering.
type rowContext struct {
	S      uiState
	ExeDir string
}

// statusRow is one line in the window.
type statusRow struct {
	// Label is the left column. Written for somebody who did not build this.
	Label string

	// Value renders the right column from the state.
	Value func(c rowContext) string

	// Warn marks a row as a problem, so the window can colour it. Optional -
	// a nil Warn is a row that is never alarming.
	Warn func(c rowContext) bool
}

// statusRows is the window, in order.
//
// ADD A ROW BY ADDING AN ENTRY HERE. Nothing else needs to change.
var statusRows = []statusRow{
	{
		Label: "Watching",
		Value: func(c rowContext) string {
			if c.S.LogPath == "" {
				return "no Game.log found yet"
			}
			return c.S.LogPath
		},
		Warn: func(c rowContext) bool { return c.S.LogPath == "" },
	},
	{
		Label: "How it found it",
		Value: func(c rowContext) string { return orDash(c.S.LogHow) },
	},
	{
		Label: "Game version",
		Value: func(c rowContext) string { return orDash(c.S.Patch) },
	},
	{
		Label: "Pictures taken",
		Value: func(c rowContext) string {
			if c.S.Captures == 0 {
				return "none yet"
			}
			if c.S.LastCapture == "" {
				return fmt.Sprintf("%d", c.S.Captures)
			}
			return fmt.Sprintf("%d  (last: %s)", c.S.Captures, c.S.LastCapture)
		},
	},
	{
		Label: "Why the last one",
		Value: func(c rowContext) string { return orDash(c.S.LastReason) },
	},
	{
		Label: "Notes ready to send",
		Value: func(c rowContext) string { return fmt.Sprintf("%d", c.S.PendingRows) },
	},
	{
		Label: "Hotkey",
		Value: func(c rowContext) string {
			if c.S.Hotkey == "" {
				return "none set"
			}
			if !c.S.HotkeyOK {
				return c.S.Hotkey + "  -  NOT REGISTERED, another copy may hold it"
			}
			return c.S.Hotkey + "  -  working"
		},
		// THE ONE THAT MATTERS ON HIS MACHINE. A hotkey that did not register
		// looks identical to one that did until you press it.
		Warn: func(c rowContext) bool { return c.S.Hotkey != "" && !c.S.HotkeyOK },
	},
	{
		Label: "Keys being watched",
		Value: func(c rowContext) string { return orDash(c.S.WatchKeys) },
	},
	{
		Label: "Where the pictures go",
		Value: func(c rowContext) string { return orDash(c.S.CaptureDir) },
	},
	{
		Label: "This install",
		Value: func(c rowContext) string { return orDash(c.S.Install) },
	},
	{
		Label: "When you finish playing",
		Value: func(c rowContext) string {
			if ReadSendMode(c.ExeDir) == SendAutomatic {
				return "sends by itself"
			}
			return "waits and asks you first"
		},
	},
	{
		Label: "Version",
		Value: func(c rowContext) string { return Version + "  (" + BuildVariant + ")" },
	},
}

func orDash(s string) string {
	if s == "" {
		return "-"
	}
	return s
}
