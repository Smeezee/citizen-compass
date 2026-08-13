package main

// consent_selftest.go - keep the promise tied to the program.
//
// # THE FAILURE THIS EXISTS TO CATCH
//
// On 2026-08-08 the consent text still said "Nothing is uploaded, ever. There
// is no server." while upload.go was posting zips to a Cloudflare Worker, and
// still said names were "replaced before the file is written" while the local
// store had been deliberately switched to keep raw names. Nothing errored.
// Nothing looked wrong. The program simply told two people a thing that had
// stopped being true, and the only reason it was caught is that somebody
// happened to re-read a file nobody had a reason to open.
//
// That is the same silent-success shape logged six times on this project, and
// it is worse here than anywhere else in the codebase: every other instance
// cost time, and this one costs somebody's trust in a tool running on their
// machine while they play.
//
// # WHY A TEST AND NOT A NOTE-TO-SELF
//
// "Remember to update the consent text" is not a mechanism. Capabilities get
// added under time pressure, by whoever is in the file that day, and the
// consent text is in a different file that nothing forces you to open.
//
// So these checks fire from the ARTEFACTS. They ask whether the shipped promise
// still matches the shipped code - not whether somebody remembered to think
// about it.
//
// # THE LIMIT OF WHAT THIS CAN PROVE, STATED PLAINLY
//
// It cannot verify a promise is honoured. It cannot prove the uploader really
// scrubs, or that chat is really excluded - other tests do that. What it proves
// is narrower and still worth having: the text does not contain a claim the
// code has already contradicted, and the version was bumped when the claim
// changed. A capability nobody thought to add a check for can still slip
// through, which is exactly why the list below is written as "if the code can
// do X, the text must not deny X" rather than as a fixed word list.

import "strings"

func runConsentSelftest(check func(name string, ok bool, detail string)) {
	text := consentText
	low := strings.ToLower(text)

	// ---------------------------------------------------------------
	// 1. CLAIMS THE CODE HAS ALREADY DISPROVED
	// ---------------------------------------------------------------
	//
	// Each entry is a phrase that WAS in the shipped text and became false.
	// They stay listed after being removed, because the way this breaks a
	// second time is somebody restoring an old paragraph.
	disproved := []struct {
		phrase string
		why    string
	}{
		{"there is no server",
			"upload.go posts to a configured endpoint and collector-receiver.worker.js is the server"},
		{"nothing is uploaded, ever",
			"SEND MY DATA uploads; it is manual, but it is an upload"},
		{"is replaced before the file is written",
			"the local store keeps raw names on purpose - scrubbing happens at export, not at write"},
		{"never leaves your computer",
			"too absolute now that there is a send path at all"},
	}
	var found []string
	for _, d := range disproved {
		if strings.Contains(low, d.phrase) {
			found = append(found, d.phrase+" ("+d.why+")")
		}
	}
	check("CONSENT: the text makes no claim the code has already disproved",
		len(found) == 0,
		"still claiming: "+strings.Join(found, "; "))

	// NEGATIVE CONTROL. The check above is worthless unless it fires. Prove
	// the matcher catches a reintroduced claim rather than just never finding
	// anything.
	fake := strings.ToLower("Nothing is uploaded, ever. There is no server. It never leaves your computer.")
	var caught int
	for _, d := range disproved {
		if strings.Contains(fake, d.phrase) {
			caught++
		}
	}
	check("CONSENT: negative control - a reintroduced false claim IS caught",
		caught >= 2,
		"the matcher found only "+itoaSmall(caught)+" of the planted claims")

	// ---------------------------------------------------------------
	// 2. CAPABILITIES THAT MUST BE DISCLOSED
	// ---------------------------------------------------------------
	//
	// Written as capability -> required disclosure. Adding a capability without
	// adding its line here is still possible; adding one and then DENYING it is
	// what section 1 catches. Between the two, the gap is narrow.
	mustMention := []struct {
		what   string
		anyOf  []string
		reason string
	}{
		{"the send path",
			[]string{"send my data", "uploads it"},
			"the program can transmit; a consent screen that never says so is not consent"},
		{"raw names held locally",
			[]string{"player names it saw", "including player names"},
			"the local store keeps real handles - the person whose disk it is should be told"},
		{"screenshots are not scrubbed",
			[]string{"not name-swapped", "not covered by that name-swapping", "are not scrubbed"},
			"a frame can show handles; the name-swapping promise must not appear to cover it"},
		{"the updater",
			[]string{"newer version", "updating itself"},
			"update.go can replace the running exe - that needs saying before it happens"},

		// SLEVEN'S DECISION, 2026-08-13. Four statements the consent must make
		// about screenshots, each one required here so it cannot quietly go
		// missing in a future rewrite the way the name-swapping line just did.
		//
		// The decision's own words: "Must be true before any build goes to a
		// third party." These checks are what make that enforceable rather
		// than remembered.
		{"screenshots are uploaded, plainly",
			[]string{"pictures of your screen are part of what is sent",
				"screenshots are part of what is sent"},
			"version 2 led with what does NOT happen; somebody could agree without " +
				"understanding that the pictures are the point"},
		{"a frame can carry OTHER people's handles",
			[]string{"handles of players standing near you",
				"names of players standing near you"},
			"the user can consent for themselves; they must at least know whose " +
				"else's name is in the frame"},
		{"screenshots are never published",
			[]string{"never published"},
			"internal-only use is the fact that makes the upload acceptable - " +
				"if it is not stated, it is not agreed to"},
		{"nothing extracted carries a name",
			[]string{"carries no name", "carry no name"},
			"the governing rule, in the words of the person agreeing to it: a " +
				"frame may contain a name, nothing derived from it ever may"},
	}
	var missing []string
	for _, m := range mustMention {
		hit := false
		for _, p := range m.anyOf {
			if strings.Contains(low, strings.ToLower(p)) {
				hit = true
				break
			}
		}
		if !hit {
			missing = append(missing, m.what+" ("+m.reason+")")
		}
	}
	check("CONSENT: every capability that can surprise somebody is disclosed",
		len(missing) == 0,
		"not mentioned: "+strings.Join(missing, "; "))

	// ---------------------------------------------------------------
	// 3. THE VERSION WAS BUMPED WHEN THE PROMISE CHANGED
	// ---------------------------------------------------------------
	//
	// Version 1 predates the send path, the raw local store and the updater.
	// Shipping any of those under an agreement given to version 1 is holding on
	// to a yes that was given to a different question - which is the exact
	// behaviour consent.go's own header says it exists to prevent.
	mentionsSending := strings.Contains(low, "uploads it") || strings.Contains(low, "send my data")
	check("CONSENT: the version was bumped when the promise widened",
		!mentionsSending || consentVersion >= 2,
		"the text describes uploading but consentVersion is still "+itoaSmall(consentVersion))

	// ---------------------------------------------------------------
	// 4. IT STILL SAYS THE THINGS THAT WERE ALWAYS TRUE
	// ---------------------------------------------------------------
	//
	// Rewrites lose things. Chat exclusion and the manual-only rule are the two
	// promises this project has treated as absolute from the start, and a
	// rewrite that quietly drops one is a regression even though nothing false
	// was added.
	keep := []struct{ label, phrase string }{
		{"chat is never sampled", "chat is never sampled"},
		{"nothing is sent automatically", "nothing is sent automatically"},
		{"the game window only", "and nothing else on your screen"},
		{"how to stop it", "how to stop it"},
	}
	var lost []string
	for _, k := range keep {
		if !strings.Contains(low, strings.ToLower(k.phrase)) {
			lost = append(lost, k.label)
		}
	}
	check("CONSENT: the original promises survived the rewrite",
		len(lost) == 0,
		"dropped: "+strings.Join(lost, ", "))

	// ---------------------------------------------------------------
	// 5. IT HAS TO FIT IN A MESSAGE BOX
	// ---------------------------------------------------------------
	//
	// MessageBoxW does not scroll. Past a certain length Windows truncates or
	// grows the dialog off-screen, and a promise somebody physically cannot
	// read is not one they agreed to. Measured against the longest line as well
	// as the total, because one long line is what actually pushes it off the
	// side of the screen.
	longest := 0
	for _, line := range strings.Split(text, "\n") {
		if len(line) > longest {
			longest = len(line)
		}
	}
	check("CONSENT: no line is too wide for a message box",
		longest <= 78,
		"longest line is "+itoaSmall(longest)+" characters")
	check("CONSENT: the whole text still fits in a dialog",
		len(text) <= 2600,
		"the text is "+itoaSmall(len(text))+" characters")

	// ---------------------------------------------------------------
	// 6. THE GATE FAILS CLOSED
	// ---------------------------------------------------------------
	//
	// HasConsent on a directory with no consent file must be false. This is the
	// branch that runs on a brand-new machine, which is the only machine where
	// getting it wrong matters.
	check("CONSENT: an unanswered machine has no consent",
		!HasConsent(".\\__no_such_dir_consent_selftest__"),
		"HasConsent returned true for a directory that does not exist")
}
