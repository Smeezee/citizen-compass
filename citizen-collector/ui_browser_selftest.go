package main

// ui_browser_selftest.go - prove the two front ends cannot drift apart.
//
// The whole argument for ui_actions.go is that one definition serves both
// transports. That argument is only worth anything if something enforces it,
// and the way it breaks is not subtle: somebody adds an action, binds it in the
// webview, and never touches the shim. The window works perfectly on the
// machine it was written on, and the button does nothing on every machine
// without WebView2 - which is every machine this change was made for.
//
// So the checks below compare the ARTEFACTS against each other rather than
// against a list somebody maintains by hand.

import (
	"encoding/json"
	"net/http/httptest"
	"strings"
)

func runBrowserUISelftest(check func(name string, ok bool, detail string)) {

	// -----------------------------------------------------------------
	// 1. EVERY ACTION IS REACHABLE FROM THE BROWSER, AND VICE VERSA
	// -----------------------------------------------------------------
	acts := buildUIActions(uiActionCtx{})
	page := browserPage("TESTTOKEN")

	// The shim's own list, read out of the generated page rather than
	// duplicated here. A copy of the list in this test would drift from the
	// shim exactly the way the shim drifts from the map.
	var jsNames []string
	if i := strings.Index(page, "var names = ["); i >= 0 {
		if j := strings.Index(page[i:], "]"); j > 0 {
			for _, part := range strings.Split(page[i+len("var names = ["):i+j], ",") {
				n := strings.Trim(strings.TrimSpace(part), `"`)
				if n != "" {
					jsNames = append(jsNames, n)
				}
			}
		}
	}
	check("BROWSER UI: the shim's action list could be read at all",
		len(jsNames) > 0,
		"found no names in the generated page - the check below would pass vacuously")

	inJS := map[string]bool{}
	for _, n := range jsNames {
		inJS[n] = true
	}
	var notExposed []string
	for name := range acts {
		if !inJS[name] {
			notExposed = append(notExposed, name)
		}
	}
	check("BROWSER UI: every action is exposed to the browser front end",
		len(notExposed) == 0,
		"the browser cannot call: "+strings.Join(notExposed, ", "))

	var notImplemented []string
	for _, n := range jsNames {
		if _, ok := acts[n]; !ok {
			notImplemented = append(notImplemented, n)
		}
	}
	check("BROWSER UI: the shim exposes nothing that does not exist",
		len(notImplemented) == 0,
		"the page would call missing actions: "+strings.Join(notImplemented, ", "))

	// NEGATIVE CONTROL. If the comparison above is vacuous - both lists empty,
	// or the parse silently returning nothing - it would pass while proving
	// nothing. Assert the count is the real one.
	check("BROWSER UI: negative control - the lists are non-trivial",
		len(acts) >= 9 && len(jsNames) == len(acts),
		"actions="+itoaSmall(len(acts))+" js="+itoaSmall(len(jsNames)))

	// -----------------------------------------------------------------
	// 2. THE SHIM RUNS BEFORE THE PAGE
	// -----------------------------------------------------------------
	//
	// If it is inserted after, every function is undefined at the moment the
	// page calls it and the panel never renders. Ordering is the failure, not
	// presence, so presence alone is not the check.
	shimAt := strings.Index(page, "var names = [")
	pageAt := strings.Index(page, "function refresh()")
	check("BROWSER UI: the shim is inserted BEFORE the page's own script",
		shimAt >= 0 && pageAt > shimAt,
		"shim at "+itoaSmall(shimAt)+", page script at "+itoaSmall(pageAt))

	// The page itself must survive intact - the shim prepends, it does not
	// rewrite.
	check("BROWSER UI: the original page is still whole inside the served copy",
		strings.Contains(page, "</html>") && strings.Contains(page, "setInterval(refresh, 1500)"),
		"the served page is missing parts of uiHTML")

	// -----------------------------------------------------------------
	// 3. THE TOKEN IS IN THE PAGE, AND IT IS THE ONE WE ASKED FOR
	// -----------------------------------------------------------------
	check("BROWSER UI: the shim calls back through the token path",
		strings.Contains(page, `var base = "/TESTTOKEN"`),
		"the shim's base path does not carry the token")

	// -----------------------------------------------------------------
	// 4. A BOOL ARGUMENT FAILS TO false
	// -----------------------------------------------------------------
	//
	// The bool arguments are "include my screenshots" and "include the 500 MB
	// runtime". A decode failure read as true sends frames that can show
	// handles and chat. This is the one default in the program where being
	// wrong has a direction.
	check("BROWSER UI: a missing argument is NOT read as yes",
		!argBool(nil), "argBool(nil) returned true")
	check("BROWSER UI: a malformed argument is NOT read as yes",
		!argBool(json.RawMessage(`"yes please"`)), "argBool of a string returned true")
	check("BROWSER UI: a null argument is NOT read as yes",
		!argBool(json.RawMessage(`null`)), "argBool(null) returned true")
	// NEGATIVE CONTROL: an explicit true must still get through, or the check
	// above is satisfied by a function that always returns false.
	check("BROWSER UI: negative control - an explicit yes IS honoured",
		argBool(json.RawMessage(`true`)), "argBool(true) returned false")

	// -----------------------------------------------------------------
	// 5. THE DOOR IS SHUT
	// -----------------------------------------------------------------
	//
	// sendData uploads somebody's data and applyUpdate downloads and runs a
	// binary. Both sit behind this function, and a local HTTP server is
	// reachable by any page in the browser, so this is the only thing standing
	// between a hostile tab and either of them.
	b := &browserUI{token: "GOODTOKEN"}

	good := httptest.NewRequest("POST", "/GOODTOKEN/call/state", nil)
	check("BROWSER UI: the real token is accepted",
		b.authorised(good), "a correct token was rejected")

	bad := httptest.NewRequest("POST", "/WRONGTOKEN/call/sendData", nil)
	check("BROWSER UI: a wrong token is refused",
		!b.authorised(bad), "a forged token was accepted")

	none := httptest.NewRequest("POST", "/call/sendData", nil)
	check("BROWSER UI: no token is refused",
		!b.authorised(none), "a request with no token was accepted")

	// A prefix of the token must not pass. This is what a comparison written
	// with strings.HasPrefix would let through.
	part := httptest.NewRequest("POST", "/GOOD/call/sendData", nil)
	check("BROWSER UI: a partial token is refused",
		!b.authorised(part), "a truncated token was accepted")

	cross := httptest.NewRequest("POST", "/GOODTOKEN/call/sendData", nil)
	cross.Header.Set("Sec-Fetch-Site", "cross-site")
	check("BROWSER UI: a cross-site request is refused even with a good token",
		!b.authorised(cross), "a cross-site POST was accepted")

	same := httptest.NewRequest("POST", "/GOODTOKEN/call/state", nil)
	same.Header.Set("Sec-Fetch-Site", "same-origin")
	check("BROWSER UI: a same-origin request is accepted",
		b.authorised(same), "the page's own request was rejected")

	// -----------------------------------------------------------------
	// 5b. THE SHIM IS VALID JAVASCRIPT
	// -----------------------------------------------------------------
	//
	// Run through the SAME balance checker that runUIScriptSelftest uses on the
	// page, because this project has already lost an evening to one stray `});`
	// that Go compiled, go vet passed, and the browser refused - stopping the
	// entire script and leaving a window with no buttons. The shim is a second
	// script block and inherits that risk exactly.
	if a := strings.Index(page, "<script>"); a >= 0 {
		if b := strings.Index(page, "</script>"); b > a {
			if detail, ok := balanceUIScript(page[a+len("<script>") : b]); !ok {
				check("BROWSER UI: the injected shim is balanced JavaScript", false, detail)
			} else {
				check("BROWSER UI: the injected shim is balanced JavaScript", true, "")
			}
		}
	}

	// -----------------------------------------------------------------
	// 6. A REFRESH DOES NOT SHUT THE COLLECTOR DOWN
	// -----------------------------------------------------------------
	//
	// pagehide fires on reload as well as on close. Treating the two the same
	// means F5 stops the collector twenty seconds later, which reads as a crash
	// and would be reported as one.
	b2 := &browserUI{token: "T"}
	b2.leaving = true
	b2.seen()
	check("BROWSER UI: contact from the page cancels a pending close",
		!b2.leaving, "the leaving flag survived a page check-in")
}
