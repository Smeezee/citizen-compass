package main

// ui_browser_socket_selftest.go - the guard is tested; is it WIRED IN?
//
// # THE GAP THIS CLOSES
//
// ui_browser_selftest.go proves authorised() is correct. Every one of its checks
// builds a synthetic httptest.NewRequest and hands it straight to the predicate:
//
//	b := &browserUI{token: "GOODTOKEN"}
//	bad := httptest.NewRequest("POST", "/WRONGTOKEN/call/sendData", nil)
//	check("a wrong token is refused", !b.authorised(bad), ...)
//
// That is a real check and it passes for a real reason. But NOTHING IN IT TOUCHES
// A HANDLER. Delete `if !b.authorised(r) { http.NotFound(w, r); return }` from
// all three routes and every one of those checks still goes green, because none
// of them ever asks the server anything. The guard would be perfect and
// unreachable, and sendData - which uploads a contributor's data - would answer
// any tab that asked.
//
// # WHICH LAYER REFUSES WHAT - measured, not assumed
//
// Removing the guard from /call/ and re-running this file showed the two
// refusals do NOT come from the same place:
//
//	WRONG TOKEN  -> refused by the ROUTER. The token is part of the mux
//	                pattern, so a wrong one matches no route and 404s before
//	                any handler runs. Still 404s with the guard deleted.
//	CROSS-SITE   -> refused by the GUARD, and only by the guard. With it
//	                deleted this returned 200 and sendData actually ran.
//
// So the cross-site pair below is what proves the wiring; the wrong-token pair
// proves the routing. Both are worth having and they are not the same claim,
// which is why they are no longer described as though they were.
//
// This project has now found seven silent successes of exactly that shape: a
// check that passes because it never actually looked. So the routes are driven
// here over a REAL loopback socket with a REAL http.Client, and the answers that
// matter are the ones from the server, not from the predicate.
//
// # WHY THIS COULD NOT BE WRITTEN BEFORE
//
// Starting the server also opened a browser. A selftest cannot pop a tab on
// somebody's machine, so there was no way to reach the routes. startBrowserUI
// exists for this - see the comment on it in ui_browser.go.
//
// # THE NEGATIVE CONTROL
//
// A test that hits three routes and gets three 404s for a bad token proves nothing
// unless a good token gets something else. Both directions are checked on every
// route, and the sensitive routes are checked by NAME rather than as a group,
// because "one of them refused" is not the claim being made.

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
	"time"
)

func runBrowserSocketSelftest(check func(name string, ok bool, detail string)) {
	// The action set does not need to be the real one - it needs to be
	// OBSERVABLE, so a handler that ran when it should not have leaves a mark
	// that cannot be confused with anything else.
	var fired []string
	calls := map[string]uiCall{
		"state":    func(arg json.RawMessage) (interface{}, error) { fired = append(fired, "state"); return "ok", nil },
		"sendData": func(arg json.RawMessage) (interface{}, error) { fired = append(fired, "sendData"); return "sent", nil },
	}

	b, url, err := startBrowserUI(calls, nil)
	if err != nil {
		check("BROWSER SOCKET: server starts", false, err.Error())
		return
	}
	defer b.Quit()
	check("BROWSER SOCKET: server starts on loopback", true, url)

	// LOOPBACK ONLY. §3 of ui_browser.go's header - nothing on the network can
	// reach this, including whoever else is on an RV park's wifi.
	check("BROWSER SOCKET: bound to 127.0.0.1, not 0.0.0.0",
		strings.HasPrefix(b.addr, "127.0.0.1:"),
		fmt.Sprintf("listening on %s", b.addr))

	base := strings.TrimSuffix(url, "/")
	client := &http.Client{Timeout: 5 * time.Second}

	do := func(method, u string, hdr map[string]string) (int, string) {
		req, err := http.NewRequest(method, u, nil)
		if err != nil {
			return -1, err.Error()
		}
		for k, v := range hdr {
			req.Header.Set(k, v)
		}
		resp, err := client.Do(req)
		if err != nil {
			return -1, err.Error()
		}
		defer resp.Body.Close()
		body, _ := io.ReadAll(io.LimitReader(resp.Body, 2048))
		return resp.StatusCode, string(body)
	}

	// ---- the page itself -------------------------------------------------
	code, body := do("GET", base+"/", nil)
	check("BROWSER SOCKET: the page is served to a correct token",
		code == 200 && strings.Contains(body, "<html"),
		fmt.Sprintf("status %d, %d bytes", code, len(body)))

	// A WRONG TOKEN MUST NOT REACH THE PAGE. This is the request a hostile tab
	// can actually make, since it cannot read the real token.
	wrong := strings.Replace(base, b.token, strings.Repeat("a", len(b.token)), 1)
	code, _ = do("GET", wrong+"/", nil)
	check("BROWSER SOCKET: a wrong token does NOT get the page",
		code == 404, fmt.Sprintf("status %d (want 404)", code))

	// ---- the actions, which are the ones that matter ---------------------
	before := len(fired)
	code, _ = do("POST", wrong+"/call/sendData", nil)
	check("BROWSER SOCKET: a wrong token is refused by /call/ (by the router)",
		code == 404, fmt.Sprintf("status %d (want 404) - the token is part of the mux pattern", code))

	// THE POINT OF THE WHOLE FILE. A refusal that still ran the action is not a
	// refusal, and a status code alone cannot tell the difference.
	check("BROWSER SOCKET: the refused action DID NOT RUN",
		len(fired) == before,
		fmt.Sprintf("actions fired during the refused request: %v", fired[before:]))

	// NEGATIVE CONTROL. Without this, every check above is satisfied by a
	// server that refuses everything, including the page's own requests.
	before = len(fired)
	code, body = do("POST", base+"/call/sendData", map[string]string{"Sec-Fetch-Site": "same-origin"})
	check("BROWSER SOCKET: NEGATIVE CONTROL - the real token DOES reach sendData",
		code == 200 && len(fired) > before,
		fmt.Sprintf("status %d, body %q, fired %v", code, strings.TrimSpace(body), fired[before:]))

	// A cross-site POST carries a correct token only if the attacker somehow has
	// it; Sec-Fetch-Site is the browser's own label and the second line.
	before = len(fired)
	code, _ = do("POST", base+"/call/sendData", map[string]string{"Sec-Fetch-Site": "cross-site"})
	check("BROWSER SOCKET: a cross-site POST is refused ON THE WIRE (by the guard)",
		code == 404, fmt.Sprintf("status %d (want 404) - this one fails if authorised() is not called", code))
	check("BROWSER SOCKET: the cross-site action DID NOT RUN",
		len(fired) == before,
		fmt.Sprintf("actions fired during the cross-site request: %v", fired[before:]))

	// ---- /leaving, the third route ---------------------------------------
	code, _ = do("POST", wrong+"/leaving", nil)
	check("BROWSER SOCKET: a wrong token is refused by /leaving",
		code == 404, fmt.Sprintf("status %d (want 404)", code))

	code, _ = do("POST", base+"/leaving", map[string]string{"Sec-Fetch-Site": "same-origin"})
	check("BROWSER SOCKET: NEGATIVE CONTROL - /leaving accepts the real token",
		code == 204, fmt.Sprintf("status %d (want 204)", code))

	// An unknown action name must be a plain 404 from the action lookup, NOT a
	// 200 with an empty result - a page asking for something that does not
	// exist should hear so.
	code, _ = do("POST", base+"/call/noSuchAction", map[string]string{"Sec-Fetch-Site": "same-origin"})
	check("BROWSER SOCKET: an unknown action is refused, not silently accepted",
		code == 404, fmt.Sprintf("status %d (want 404)", code))

	// The page must never be cacheable: a stale panel showing a capture count
	// from ten minutes ago is indistinguishable from a collector that stopped.
	req, _ := http.NewRequest("GET", base+"/", nil)
	if resp, err := client.Do(req); err == nil {
		cc := resp.Header.Get("Cache-Control")
		xf := resp.Header.Get("X-Frame-Options")
		resp.Body.Close()
		check("BROWSER SOCKET: the page is served no-store and DENY-framed",
			strings.Contains(cc, "no-store") && xf == "DENY",
			fmt.Sprintf("Cache-Control %q, X-Frame-Options %q", cc, xf))
	} else {
		check("BROWSER SOCKET: the page is served no-store and DENY-framed", false, err.Error())
	}
}
