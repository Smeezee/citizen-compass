package main

// destination.go - where a send goes, without anybody typing it.
//
// THE DEFECT
//
// Sleven's wife's collector updated itself to 0.3.0 cleanly, she pressed SEND,
// and got a 27 MB zip on her disk and nothing else. Nothing was broken: the
// updater replaces the executable and does not touch collector-settings.txt, her
// send_url and send_key were blank, and blank means "write a zip locally and
// stop". A correctly working collector silently did nothing useful, and it
// looked like a failure.
//
// Every person who ever installs this hits that, and the fix was "open a text
// file and paste two values, one of which is a 51-character password". That does
// not survive a second contributor, let alone two hundred.
//
// SO THE DESTINATION COMES DOWN THE FEED
//
// update.go already fetches releases/collector-latest.json over HTTPS on a
// schedule, and already trusts it enough to download and run a binary named in
// it. Carrying a destination in the same file is strictly less dangerous than
// what the program already does with it.
//
// # PRECEDENCE, AND WHY LOCAL WINS
//
//	1. a non-empty send_url in collector-settings.txt   <- local wins
//	2. otherwise, whatever the feed supplied
//	3. otherwise, the last feed values cached on disk
//	4. otherwise, nothing - and SAY SO, loudly
//
// Local wins deliberately. Sleven has his own values, and a future tester may
// need to point somewhere else. The feed is a default for people who configured
// nothing, never an override that silently redirects a machine somebody set up
// on purpose.
//
// # A LOCAL URL NEVER GETS THE PUBLISHED KEY
//
// The pair is taken from ONE source or the other, never mixed. Filling a locally
// configured endpoint's blank key from the feed would post the shared token to
// whatever address that machine happened to name - including a tester's laptop,
// or a typo. The key belongs to the address it was published with.

import (
	"encoding/json"
	"io"
	"os"
	"path/filepath"
	"strings"
)

// destinationCacheFile keeps the last destination the feed supplied, so a
// machine with no network still knows where to send when the network returns.
const destinationCacheFile = "collector-destination.json"

// Destination is where a send goes and how that was decided.
type Destination struct {
	URL string `json:"send_url"`
	Key string `json:"send_key"`

	// Source is for the operator, not for logic. A program that starts
	// uploading to an address nobody typed should be able to say where it got
	// it (§3).
	Source string `json:"-"`
}

// Configured reports whether there is anywhere to send at all.
func (d Destination) Configured() bool { return strings.TrimSpace(d.URL) != "" }

// ResolveDestination applies the precedence rules. Pure, so every rule can be
// driven with input that must fail it - see restart_handover_selftest.go's
// sibling, destination_selftest.go.
//
// feedURL/feedKey are what the feed supplied this run ("" when it was not
// reached). cached is what the feed supplied on some previous run.
func ResolveDestination(localURL, localKey, feedURL, feedKey string, cached Destination) Destination {
	localURL, localKey = strings.TrimSpace(localURL), strings.TrimSpace(localKey)
	feedURL, feedKey = strings.TrimSpace(feedURL), strings.TrimSpace(feedKey)

	// 1. LOCAL WINS, and takes its own key with it - never the feed's.
	if localURL != "" {
		return Destination{
			URL:    localURL,
			Key:    localKey,
			Source: "collector-settings.txt on this computer",
		}
	}

	// 2. THE FEED. Both halves or neither: a URL with no key would post to the
	//    receiver and be refused, which looks like a broken endpoint rather
	//    than an incomplete feed.
	if feedURL != "" && feedKey != "" {
		return Destination{
			URL:    feedURL,
			Key:    feedKey,
			Source: "the published update feed",
		}
	}

	// 3. THE LAST GOOD FEED VALUES. A machine that has been offline since it
	//    was installed still knows where to send once the network returns.
	if strings.TrimSpace(cached.URL) != "" && strings.TrimSpace(cached.Key) != "" {
		return Destination{
			URL:    strings.TrimSpace(cached.URL),
			Key:    strings.TrimSpace(cached.Key),
			Source: "the last destination the feed supplied, remembered on this computer",
		}
	}

	// 4. NOTHING. The caller must not let this look like a send.
	return Destination{Source: "nowhere - no destination is configured"}
}

// StripWrappingBrackets removes ONE matching pair of < > and reports whether it
// had to, so the caller can say so out loud.
//
// THE DEFECT
//
// Sleven's own send_key was written as <the-key>, angle brackets included -
// which is exactly what happens when a line printed as a template
//
//	send_key = <the value you gave to wrangler secret put>
//
// gets pasted with the real value dropped between the brackets. Nothing trimmed
// them, so the collector sent a key two characters longer than the secret on the
// Worker, and the Worker answered 403. From the operator's side that is
// indistinguishable from a broken endpoint or a wrong key, and it would have
// been diagnosed by taking the receiver apart rather than by reading the line.
//
// IT IS NEVER SILENT
//
// Stripping quietly would trade one invisible failure for another: a settings
// file that means something different to the program than it says to the person
// reading it. So every strip is logged, once, naming what it did.
func StripWrappingBrackets(s string) (string, bool) {
	t := strings.TrimSpace(s)
	if len(t) >= 2 && strings.HasPrefix(t, "<") && strings.HasSuffix(t, ">") {
		return strings.TrimSpace(t[1 : len(t)-1]), true
	}
	return t, false
}

// BracketWarning is what to say when a value ARRIVES still wrapped after one
// pair has been taken off - <<key>>, or a stray bracket on one side only.
//
// One pair is a paste artefact and is safe to correct. Anything past that is a
// value nobody has actually looked at, and accepting it silently is how a 403
// gets blamed on the receiver for a second time.
func BracketWarning(name, v string) string {
	t := strings.TrimSpace(v)
	if t == "" {
		return ""
	}
	if strings.HasPrefix(t, "<") || strings.HasSuffix(t, ">") {
		return name + " still has angle brackets on it after one pair was removed. " +
			"That value is being used EXACTLY as written and will almost certainly " +
			"be refused - open collector-settings.txt and remove them."
	}
	return ""
}

// LoadCachedDestination reads the remembered feed destination.
//
// A missing or unreadable file is not an error worth reporting: it means this
// machine has not yet had a successful feed check, which is the normal state of
// a fresh install.
func LoadCachedDestination(exeDir string) Destination {
	f, err := os.Open(filepath.Join(exeDir, destinationCacheFile))
	if err != nil {
		return Destination{}
	}
	defer f.Close()
	b, err := io.ReadAll(io.LimitReader(f, 64*1024))
	if err != nil {
		return Destination{}
	}
	var d Destination
	if err := json.Unmarshal(b, &d); err != nil {
		return Destination{}
	}
	return d
}

// SaveCachedDestination remembers what the feed supplied.
//
// Written only when the feed actually supplied both halves, so a feed that
// temporarily omits them cannot erase a working machine's memory of where to
// send.
func SaveCachedDestination(exeDir, url, key string) error {
	if strings.TrimSpace(url) == "" || strings.TrimSpace(key) == "" {
		return nil
	}
	b, err := json.MarshalIndent(Destination{URL: url, Key: key}, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(filepath.Join(exeDir, destinationCacheFile), append(b, '\n'), 0o644)
}

// NoDestinationWarning is what the operator is told BEFORE packaging, when
// there is nowhere to send.
//
// §3: blank must never look like success. The old behaviour wrote a local zip
// and returned a completed-looking result, which Sleven read as a failure and
// somebody less patient reads as the tool being broken.
const NoDestinationWarning = "There is nowhere to send to yet, so this will only write a zip to your disk."

// LocalOnlyResult is what it says AFTER writing a local-only zip: name the file,
// say it stayed here, say why.
func LocalOnlyResult(path string) string {
	return "Saved to " + path + " on this computer. It was NOT sent anywhere - " +
		"there is no destination configured yet, so nothing left this machine."
}
