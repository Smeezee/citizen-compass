package main

// destination_selftest.go - every precedence rule, and a case that must fail it.
//
// This decides WHERE A CONTRIBUTOR'S DATA GOES. Getting it wrong does not
// produce an error message; it produces an upload to the wrong place, or a
// machine that quietly sends nowhere. Neither announces itself.
//
// The rule that matters most is the one with no error path at all: a machine
// somebody configured on purpose must never be repointed by a published
// default, and the published key must never be attached to a locally named
// address. If that check were absent, everything else would still pass.

import (
	"os"
	"path/filepath"
	"strings"
)

func runDestinationSelftest(check func(name string, ok bool, detail string)) {
	const (
		feedURL = "https://collector-receiver.example.workers.dev"
		feedKey = "FEEDKEY-published-in-the-feed"
		locURL  = "https://tester-laptop.example.invalid/upload"
		locKey  = "LOCALKEY-typed-by-hand"
	)
	cachedGood := Destination{URL: "https://cached.example.workers.dev", Key: "CACHEDKEY"}

	// --- 1. LOCAL WINS ----------------------------------------------------
	d := ResolveDestination(locURL, locKey, feedURL, feedKey, cachedGood)
	check("local settings beat the feed", d.URL == locURL && d.Key == locKey,
		"a machine configured on purpose is not repointed by a published default")

	// THE ONE WITH NO ERROR PATH. A local URL whose key is blank must NOT be
	// filled in from the feed: that would post the shared token to whatever
	// address that machine happened to name - a tester's laptop, or a typo.
	d = ResolveDestination(locURL, "", feedURL, feedKey, cachedGood)
	check("a local URL never borrows the feed's key", d.URL == locURL && d.Key == "",
		"the published key belongs to the address it was published with, and nowhere else")

	// NEGATIVE CONTROL for "local wins": with nothing local, the feed MUST be
	// used - otherwise a resolver that always returned local would pass above
	// and leave every fresh install sending nowhere.
	d = ResolveDestination("", "", feedURL, feedKey, Destination{})
	check("the feed is used when nothing is configured", d.URL == feedURL && d.Key == feedKey,
		"this is the whole feature: a fresh install sends with nothing typed")

	// --- 2. THE FEED NEEDS BOTH HALVES ------------------------------------
	d = ResolveDestination("", "", feedURL, "", Destination{})
	check("a feed URL with no key is not used", !d.Configured(),
		"a URL without a key would post and be refused, which reads as a broken endpoint")
	d = ResolveDestination("", "", "", feedKey, Destination{})
	check("a feed key with no URL is not used", !d.Configured(),
		"there is nowhere to send a key to")

	// --- 3. THE CACHE ------------------------------------------------------
	d = ResolveDestination("", "", "", "", cachedGood)
	check("the cache is used when the feed is unreachable", d.URL == cachedGood.URL,
		"a machine that has been offline still knows where to send")

	// NEGATIVE CONTROL: a live feed must OUTRANK the cache, or changing the
	// destination in the feed would never move anybody who had already cached
	// the old one - acceptance rule 5.
	d = ResolveDestination("", "", feedURL, feedKey, cachedGood)
	check("a fresh feed outranks the cache", d.URL == feedURL,
		"changing send_url in the feed must move the next send, with no reinstall")

	// A half-written cache is not a destination.
	d = ResolveDestination("", "", "", "", Destination{URL: cachedGood.URL})
	check("a cache missing its key is not used", !d.Configured(),
		"half a destination is not a destination")

	// --- 4. NOTHING AT ALL -------------------------------------------------
	d = ResolveDestination("", "", "", "", Destination{})
	check("nothing configured means NOT configured", !d.Configured(),
		"acceptance rule 4 - this must not be allowed to look like a send")
	check("and it says so", strings.Contains(d.Source, "nowhere"),
		"the operator is told what is missing rather than left guessing")

	// Whitespace is not configuration. A settings line left as "send_url = "
	// reads as a space, and a resolver that trusted it would send to nowhere.
	d = ResolveDestination("   ", "  ", "  ", "  ", Destination{URL: " ", Key: " "})
	check("whitespace is not a destination", !d.Configured(),
		"a blank settings line must not read as an address")

	// --- 5. THE CACHE ROUND-TRIPS ON DISK ---------------------------------
	dir, err := os.MkdirTemp("", "cc-dest")
	if err != nil {
		return
	}
	defer os.RemoveAll(dir)

	check("no cache file reads as empty, not as an error", !LoadCachedDestination(dir).Configured(),
		"a fresh install has no cache and that is normal, not a fault")

	if err := SaveCachedDestination(dir, feedURL, feedKey); err != nil {
		check("the cache can be written", false, err.Error())
		return
	}
	got := LoadCachedDestination(dir)
	check("the cache round-trips", got.URL == feedURL && got.Key == feedKey,
		"what the feed supplied is what a later offline run will use")

	// NEGATIVE CONTROL: a feed that omits the destination must NOT erase what a
	// working machine already remembered. Overwriting with blanks would leave a
	// collector unable to send because of a temporary gap in a file it does not
	// control.
	_ = SaveCachedDestination(dir, "", "")
	still := LoadCachedDestination(dir)
	check("an empty feed does not erase the remembered destination",
		still.URL == feedURL && still.Key == feedKey,
		"a gap in the feed must not disable a machine that was working")

	// A corrupt cache is not a destination, and must not crash the resolver.
	_ = os.WriteFile(filepath.Join(dir, destinationCacheFile), []byte("{not json"), 0o644)
	check("a corrupt cache reads as empty", !LoadCachedDestination(dir).Configured(),
		"unreadable is treated as absent, never as a half-parsed address")

	// --- 6. PASTED ANGLE BRACKETS -----------------------------------------
	//
	// send_key was written as <the-key> on Sleven's own machine. Two extra
	// characters, a 403 from the Worker, and a failure that looks exactly like a
	// broken receiver. Every case here is paired with one that must NOT be
	// touched, because a stripper that trimmed enthusiastically would corrupt
	// keys that were fine.
	got1, did1 := StripWrappingBrackets("<abc123>")
	check("a wrapped value is unwrapped", got1 == "abc123" && did1,
		"one matching pair comes off, and the caller is told it happened")

	got2, did2 := StripWrappingBrackets("  <abc123>  ")
	check("surrounding whitespace does not hide the brackets", got2 == "abc123" && did2,
		"a pasted line usually arrives with spaces around it")

	// NEGATIVE CONTROLS. Without these, a function that stripped the first and
	// last character of everything would pass every check above.
	got3, did3 := StripWrappingBrackets("abc123")
	check("a clean value is left alone", got3 == "abc123" && !did3,
		"nothing is reported as corrected when nothing was")

	got4, did4 := StripWrappingBrackets("<abc123")
	check("a leading bracket alone is not stripped", got4 == "<abc123" && !did4,
		"only a MATCHING pair, or a key beginning with < would be silently altered")

	got5, did5 := StripWrappingBrackets("abc123>")
	check("a trailing bracket alone is not stripped", got5 == "abc123>" && !did5,
		"the pair has to match")

	got6, did6 := StripWrappingBrackets("")
	check("an empty value is not mangled", got6 == "" && !did6,
		"blank stays blank rather than becoming a one-character key")

	got7, _ := StripWrappingBrackets("<>")
	check("an empty pair yields nothing, not a bracket", got7 == "",
		"<> is not a key")

	// A URL that legitimately contains a bracket in the middle must survive.
	got8, did8 := StripWrappingBrackets("https://example.com/a<b>c")
	check("brackets inside a value are untouched", got8 == "https://example.com/a<b>c" && !did8,
		"only a wrapping pair is a paste artefact")

	// DO NOT SILENTLY ACCEPT ONE THAT IS STILL WRAPPED.
	stillWrapped, _ := StripWrappingBrackets("<<abc123>>")
	check("a doubly-wrapped value is flagged, not accepted quietly",
		BracketWarning("send_key", stillWrapped) != "",
		"one pair is a paste artefact; two means nobody has looked at this value")
	check("a clean value produces no warning", BracketWarning("send_key", "abc123") == "",
		"NEGATIVE CONTROL: a warning that always fires would be noise, not a check")
	check("a blank value produces no warning", BracketWarning("send_key", "") == "",
		"unset is a different problem, reported elsewhere")

	// --- 7. THE MESSAGES SAY WHAT HAPPENED --------------------------------
	msg := LocalOnlyResult("citizen-collector-export.zip")
	check("a local-only result does not read as sent",
		strings.Contains(msg, "NOT sent") && strings.Contains(msg, "citizen-collector-export.zip"),
		"the exact confusion that made a working collector look broken")
	check("the no-destination warning explains itself",
		strings.Contains(NoDestinationWarning, "only write a zip"),
		"said BEFORE packaging, so nobody presses SEND expecting a send")
}
