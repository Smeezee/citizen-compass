package main

// ui_bridge_selftest.go - a window that cannot answer must not look like one
// that can.
//
// # WHAT HAPPENED
//
// Sleven, at a shop terminal, 26 captures taken and the hotkey working: the
// window opened, the status stayed on dashes, and all five buttons did nothing
// when clicked. Both existing escape hatches were satisfied - webview2Available
// said yes, and NewWithOptions returned a window - because both of them look at
// the runtime BEFORE the page runs. Neither can see a bridge that fails after.
//
// NOT A NETWORK HANG, and that was established rather than assumed: httpClient
// carries a 15s timeout, so a permanently stuck "Checking for updates..." can
// only be a call that never returned, not a call that was slow.
//
// The checks below are about the two things that make that state impossible:
// the page must announce itself, and the browser transport must be able to run
// the identical page.

import (
	"os"
	"regexp"
	"sort"
	"strings"
	"time"
)

func runUIBridgeSelftest(check func(name string, ok bool, detail string)) {

	// -----------------------------------------------------------------
	// 1. THE PAGE ANNOUNCES ITSELF, AND BOTH TRANSPORTS CAN CARRY IT
	// -----------------------------------------------------------------
	check("BRIDGE: the page calls uiReady before anything else",
		strings.Contains(uiHTML, "window.uiReady()"),
		"nothing would ever prove the bridge works, and a dead window would "+
			"look exactly like a live one")

	// The page must not depend on uiReady EXISTING to keep going - a browser
	// that somehow lacked the shim should still render rather than throw on its
	// own first line.
	check("BRIDGE: the hello is guarded, so it cannot break the page itself",
		regexp.MustCompile(`try\s*\{\s*window\.uiReady\(\)`).MatchString(uiHTML),
		"an unguarded call would turn a missing shim into a blank page")

	tok := "0123456789abcdef"
	page := browserPage(tok)
	check("BRIDGE: the browser transport serves the SAME page, not a copy",
		strings.Contains(page, "window.uiReady()") && strings.Count(page, "<body") == strings.Count(uiHTML, "<body"),
		"a second copy of the interface would drift within a week")
	check("BRIDGE: the browser transport provides uiReady",
		strings.Contains(page, "uiReady"),
		"the fallback that exists to rescue a broken bridge would break on its "+
			"own first line")

	// -----------------------------------------------------------------
	// 2. THE TWO TRANSPORTS MUST OFFER THE SAME FUNCTIONS
	// -----------------------------------------------------------------
	//
	// THE DRIFT CHECK. Adding a binding to the window and forgetting the shim
	// produces a button that works for everybody with WebView2 and does nothing
	// for everybody without it - which is invisible on the machine of whoever
	// added it. Read both lists out of the source and compare them.
	uiSrc, e1 := os.ReadFile("ui.go")
	brSrc, e2 := os.ReadFile("ui_browser.go")
	if e1 != nil || e2 != nil {
		check("BRIDGE: transport parity NOT COMPARED", true,
			"the sources are not beside the exe, so the two function lists were "+
				"not compared on this run. That is expected outside the source tree.")
	} else {
		bound := map[string]bool{}
		for _, m := range regexp.MustCompile(`w\.Bind\("([A-Za-z0-9_]+)"`).FindAllSubmatch(uiSrc, -1) {
			bound[string(m[1])] = true
		}
		shim := map[string]bool{}
		if m := regexp.MustCompile(`var names = \[([^\]]*)\]`).FindSubmatch(brSrc); m != nil {
			for _, q := range regexp.MustCompile(`"([A-Za-z0-9_]+)"`).FindAllSubmatch(m[1], -1) {
				shim[string(q[1])] = true
			}
		}
		var missing, extra []string
		for n := range bound {
			if !shim[n] {
				missing = append(missing, n)
			}
		}
		for n := range shim {
			if !bound[n] {
				extra = append(extra, n)
			}
		}
		sort.Strings(missing)
		sort.Strings(extra)

		check("BRIDGE: every window binding exists in the browser transport",
			len(bound) > 0 && len(missing) == 0,
			"missing from the browser: "+strings.Join(missing, ", ")+
				" - those buttons would do nothing on a machine without WebView2")
		check("BRIDGE: the browser transport claims nothing the window does not have",
			len(extra) == 0,
			"only in the browser shim: "+strings.Join(extra, ", ")+
				" - a promise the window cannot keep")

		// NEGATIVE CONTROL. If the extractor found nothing, both checks above
		// would pass vacuously and prove exactly nothing.
		check("BRIDGE: NEGATIVE CONTROL - the comparison actually found bindings",
			len(bound) >= 9 && len(shim) >= 9,
			"found "+itoaSmall(len(bound))+" bindings and "+itoaSmall(len(shim))+
				" shim names; a parser that matched nothing would report parity "+
				"between two empty sets")
	}

	// -----------------------------------------------------------------
	// 3. THE DEADLINE IS SANE
	// -----------------------------------------------------------------
	check("BRIDGE: there is a deadline at all",
		uiBridgeTimeout > 0,
		"with no deadline a dead bridge waits forever, which is the defect")
	check("BRIDGE: the deadline is long enough for a cold start",
		uiBridgeTimeout >= 5*time.Second,
		"scrapping a merely slow window would swap a rare failure for a common one")
	check("BRIDGE: the deadline is short enough that nobody sits looking at it",
		uiBridgeTimeout <= 30*time.Second,
		"a person who waited this long has already decided the program is broken")

	// -----------------------------------------------------------------
	// 4. THE NO-RUNTIME PATH, AND ITS NEGATIVE CONTROL
	// -----------------------------------------------------------------
	//
	// Forced by pointing the resolver at a folder that has no runtime in it.
	// What is being proved is that the decision does not silently answer "yes,
	// there is a runtime here" - which is the answer that produces a window
	// nobody can use.
	empty, err := os.MkdirTemp("", "cc-noruntime")
	if err == nil {
		defer os.RemoveAll(empty)
		dir, how := resolveBundledRuntime(empty)
		check("BRIDGE: a folder with no runtime resolves to no bundled runtime",
			dir == "" && how != "",
			"resolved to "+dir+" ("+how+")")

		// A runtime FOLDER that exists but holds no engine must also fail. This
		// is the shape that would otherwise report success and then fail at
		// window creation with something unreadable.
		hollow := empty + string(os.PathSeparator) + bundledRuntimeDir +
			string(os.PathSeparator) + "151.0.0.0"
		if os.MkdirAll(hollow, 0o755) == nil {
			dir2, how2 := resolveBundledRuntime(empty)
			check("BRIDGE: a runtime folder with no engine in it is refused",
				dir2 == "",
				"an empty version folder was accepted as a runtime ("+how2+")")
		}

		// NEGATIVE CONTROL: a folder that DOES contain an engine must resolve.
		// Without this, a resolver that always returned "" would pass both
		// checks above and disable the bundled runtime entirely.
		if os.WriteFile(hollow+string(os.PathSeparator)+"msedgewebview2.exe",
			[]byte("not a real engine, but the right name"), 0o644) == nil {
			dir3, how3 := resolveBundledRuntime(empty)
			check("BRIDGE: NEGATIVE CONTROL - a real-looking bundled runtime IS accepted",
				dir3 != "",
				"a resolver that refuses everything would silently disable "+
					"bundling altogether ("+how3+")")
		}
	}
}
