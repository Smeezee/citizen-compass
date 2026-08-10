package main

// identity.go - who sent this data, without knowing who anybody is.
//
// # THE PROBLEM THIS SOLVES, WHICH IS NOT OBVIOUS
//
// Three people report the same price at the same kiosk.
//
// Is that three independent confirmations - the single most valuable thing a
// crowd-sourced price dataset can produce - or is it one person exporting the
// same log three times?
//
// Without a way to tell, BOTH available answers are wrong:
//
//   - Dedup across contributors, and genuine independent corroboration is
//     silently deleted. The dataset gets smaller and looks cleaner while losing
//     exactly the signal that made it worth gathering.
//   - Do not dedup, and one person clicking SEND twice inflates every count.
//
// No amount of later cleverness recovers the distinction if it was never
// recorded. That is why this exists now, while there is exactly one producer
// and it is on Sleven's desk, rather than after other people's exports are in
// the wild.
//
// # WHAT THIS IS NOT
//
// It is NOT derived from the player handle, the Windows account, the machine
// name, the hardware, the MAC address, the install path, or anything else about
// the person or their computer. It is 16 bytes of cryptographic randomness.
//
// That distinction is the whole design. A hash of the machine name would look
// anonymous and would not be: anyone holding a list of candidate machine names
// could confirm a guess against it. Random bytes cannot be reversed into a
// person because they were never a function of one.
//
// It identifies a SOURCE OF OBSERVATIONS. It does not identify a human, and it
// cannot be made to.
//
// # IT IS DELIBERATELY VISIBLE
//
// The ID lives in a plain text file the person can open, read, delete, or
// regenerate. Nothing about it is hidden from the person it came from. A
// tracking identifier the user cannot see is a different kind of object than
// this one, and the difference is entirely in whether they can look at it.
//
// Because the file is readable it is also EDITABLE, and somebody will
// eventually type their name into it. See validInstallID: an ID that is not
// exactly 32 hex characters is rejected outright rather than sent. The one
// thing this file must never do is carry a handle into a dataset whose entire
// purpose is to not contain handles.

import (
	"crypto/rand"
	"encoding/hex"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"time"
)

// InstallIDFile sits beside the exe, next to collector-settings.txt.
const InstallIDFile = "collector-install-id.txt"

// Install is the contributor identity attached to every export.
type Install struct {
	ID        string `json:"install_id"`
	FirstSeen string `json:"install_first_seen"`

	// Regenerated is true when a previous ID existed and could not be used.
	// It is reported rather than smoothed over: a regenerated ID means this
	// machine's older exports and its newer ones look like two different
	// contributors, and whoever merges them is entitled to know that happened.
	Regenerated bool   `json:"install_id_regenerated,omitempty"`
	RegenReason string `json:"install_id_regenerated_reason,omitempty"`
}

// validInstallID accepts only what this file writes: 32 hex characters,
// optionally grouped with dashes for readability.
//
// This is the guard against the readable-file-is-an-editable-file problem. If
// somebody replaces the ID with "dave's gaming pc" or their Star Citizen
// handle, that string must never reach an export. Rejecting it costs one
// regenerated ID; accepting it puts a real identifier into the one dataset the
// whole pipeline exists to keep identifiers out of.
func validInstallID(s string) bool {
	t := strings.ToLower(strings.TrimSpace(s))
	t = strings.ReplaceAll(t, "-", "")
	if len(t) != 32 {
		return false
	}
	if _, err := hex.DecodeString(t); err != nil {
		return false
	}
	return true
}

// newInstallID returns 16 random bytes as grouped hex.
//
// THERE IS NO FALLBACK, AND THAT IS DELIBERATE. If the system's random source
// is unavailable, this returns an error and the caller ships an export with no
// contributor ID and says so. The tempting fallback - seed from the clock, the
// PID, the hostname - would produce something that looks like an ID, collides
// with other installs that started at a similar moment, and IS derived from the
// machine. Every property that matters would be quietly gone while the field
// still looked populated.
func newInstallID() (string, error) {
	b := make([]byte, 16)
	if _, err := rand.Read(b); err != nil {
		return "", fmt.Errorf("no secure random source available: %w", err)
	}
	h := hex.EncodeToString(b)
	return fmt.Sprintf("%s-%s-%s-%s", h[0:8], h[8:16], h[16:24], h[24:32]), nil
}

func installIDPath(dir string) string { return filepath.Join(dir, InstallIDFile) }

// LoadOrCreateInstall reads the ID beside the exe, creating one if needed.
//
// It never returns a partially-valid Install: either the ID is good, or the
// error is set and the ID is empty. An empty ID is a legitimate state that the
// export handles honestly.
func LoadOrCreateInstall(dir string, logf func(string, ...interface{})) (Install, error) {
	if logf == nil {
		logf = func(string, ...interface{}) {}
	}
	var in Install
	path := installIDPath(dir)

	regenReason := ""
	if b, err := os.ReadFile(path); err == nil {
		id, first := parseInstallFile(string(b))
		switch {
		case validInstallID(id):
			in.ID = strings.ToLower(strings.TrimSpace(id))
			in.FirstSeen = first
			if in.FirstSeen == "" {
				in.FirstSeen = time.Now().UTC().Format(time.RFC3339)
			}
			return in, nil
		case id == "":
			regenReason = "the file existed but contained no id line"
		default:
			// Deliberately does NOT echo the rejected value into the log. If
			// somebody typed their handle in there, repeating it into a log
			// file that gets pasted into chat defeats the point of rejecting it.
			regenReason = "the id in the file was not 32 hex characters, so it was not " +
				"something this tool wrote - it has been replaced rather than sent"
		}
	} else if !os.IsNotExist(err) {
		regenReason = fmt.Sprintf("the existing file could not be read (%v)", err)
	}

	id, err := newInstallID()
	if err != nil {
		logf("install id: %v - this export will go out with no contributor id, and will "+
			"say so", err)
		return Install{}, err
	}
	in.ID = id
	in.FirstSeen = time.Now().UTC().Format(time.RFC3339)
	if regenReason != "" {
		in.Regenerated = true
		in.RegenReason = regenReason
		logf("install id: replaced - %s", regenReason)
		logf("install id: your earlier exports carry the OLD id, so they will look like a " +
			"different contributor. Nothing is lost; it is worth knowing.")
	}

	if err := writeInstallFile(path, in); err != nil {
		// A working ID that could not be saved is still usable for THIS export.
		// It will differ next run, which is worse than stable but better than
		// refusing to export at all - and it is reported, not hidden.
		logf("install id: generated but could not be saved (%v) - it will not be the "+
			"same next time", err)
	}
	return in, nil
}

// parseInstallFile reads "name = value" lines and ignores # comments, matching
// the format of collector-settings.txt so there is one file shape to learn.
func parseInstallFile(s string) (id, firstSeen string) {
	for _, raw := range strings.Split(s, "\n") {
		line := strings.TrimSpace(raw)
		if line == "" || strings.HasPrefix(line, "#") {
			continue
		}
		k, v, ok := strings.Cut(line, "=")
		if !ok {
			continue
		}
		k = strings.ToLower(strings.TrimSpace(k))
		v = strings.TrimSpace(v)
		switch k {
		case "id", "install_id":
			id = v
		case "first_seen":
			firstSeen = v
		}
	}
	return id, firstSeen
}

func writeInstallFile(path string, in Install) error {
	var b strings.Builder
	b.WriteString("# citizen-collector - contributor id\n")
	b.WriteString("#\n")
	b.WriteString("# This is 16 random bytes. It is NOT built from your name, your Star\n")
	b.WriteString("# Citizen handle, your Windows account, your computer's name or anything\n")
	b.WriteString("# else about you or your machine. It cannot be turned back into a person\n")
	b.WriteString("# because it was never made from one.\n")
	b.WriteString("#\n")
	b.WriteString("# It goes into the file you get when you press SEND MY DATA. Its only job\n")
	b.WriteString("# is to let two reports of the same price be told apart from the same\n")
	b.WriteString("# report sent twice.\n")
	b.WriteString("#\n")
	b.WriteString("# Delete this file and a new id is made. That is allowed - your older\n")
	b.WriteString("# exports will simply look like they came from somebody else.\n")
	b.WriteString("#\n")
	b.WriteString("# Do not put your name in here. Anything that is not 32 hex characters is\n")
	b.WriteString("# thrown away and replaced, so it would not be sent anyway.\n\n")
	fmt.Fprintf(&b, "id = %s\n", in.ID)
	fmt.Fprintf(&b, "first_seen = %s\n", in.FirstSeen)

	tmp := path + ".tmp"
	if err := os.WriteFile(tmp, []byte(b.String()), 0o644); err != nil {
		return err
	}
	return os.Rename(tmp, path)
}
