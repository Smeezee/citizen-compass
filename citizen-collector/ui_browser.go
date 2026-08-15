package main

// ui_browser.go - the same window, in a browser they already have.
//
// # WHAT THIS REPLACES
//
// A 271 MB download, because the program was carrying an entire copy of Edge to
// draw one 480x660 panel with five buttons.
//
// With this, the exe is ~11 MB and needs nothing installed. If WebView2 exists
// it is still used and the window looks exactly as it does now. If it does not,
// this serves the identical page on 127.0.0.1 and opens their default browser.
// The recipient double-clicks one file. There is no second step, no runtime, no
// choice to make, and nothing that can be put off until later.
//
// # THE SECURITY PROBLEM A LOCAL SERVER CREATES, AND WHAT IS DONE ABOUT IT
//
// A plain HTTP server on 127.0.0.1 is reachable by ANY page in that browser.
// Websites cannot read cross-origin responses, but they can fire a POST and it
// will execute. `sendData` uploads somebody's collected data. `applyUpdate`
// downloads and runs a binary. Those must not be triggerable by a tab the
// person opened in the background.
//
// Three things, none of which is sufficient alone:
//
//  1. A 256-bit random token in the URL PATH. Every request carries it, and it
//     is compared in constant time. A hostile page cannot read the token - it
//     would need to read the response of a request it cannot make - so it
//     cannot construct a valid URL. This is the one that actually does the
//     work; the rest are belt and braces.
//
//  2. Sec-Fetch-Site is required to be same-origin or absent. Every browser
//     that can reach this sends it, and a cross-site POST is labelled by the
//     browser itself rather than by anything the attacker controls.
//
//  3. Listening on 127.0.0.1 only, never 0.0.0.0, so nothing on the network -
//     including whoever else is on an RV park's wifi - can reach it at all.
//
// The port is whatever the OS hands out, not a fixed number, so there is also
// nothing predictable to aim at.
//
// # HOW IT KNOWS TO QUIT
//
// The webview window has an obvious answer: w.Run() returns when it closes. A
// browser tab has none - closing it tells the program nothing.
//
// So the page sends a heartbeat, and the program exits when the heartbeat stops
// for long enough. The timeout is deliberately generous, because a background
// tab gets throttled by every modern browser and a program that quits because
// somebody looked at something else for two minutes is worse than one that
// lingers. The tray icon's Exit remains the deliberate way to stop it.

import (
	"context"
	"crypto/rand"
	"crypto/subtle"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"net"
	"net/http"
	"os/exec"
	"strings"
	"sync"
	"time"
)

// browserIdleTimeout is how long the page can go silent before the program
// treats the person as finished.
//
// Chrome throttles timers in a hidden tab to roughly one per minute, so a
// 1.5-second heartbeat can legitimately arrive a minute apart. Anything under
// about two minutes would therefore shut the collector down while somebody is
// playing the game in the foreground - which is the exact moment it is supposed
// to be working. Five minutes is chosen to be obviously outside that window
// rather than nearly outside it.
const browserIdleTimeout = 5 * time.Minute

// browserHeartbeat is how often the page checks in. It piggybacks on the
// existing 1.5s state() poll rather than adding a second timer, so a page that
// is rendering is a page that is alive by definition.

// browserLeaveGrace is how long the program waits after the page says it is
// going away.
//
// THIS IS NOT THE SAME AS CLOSING THE TAB, AND CONFLATING THEM IS A BUG.
// `pagehide` fires on a refresh, on a navigation, and on a tab being discarded
// to save memory - not only on a close. Quitting the moment it arrives means
// pressing F5 kills the collector, which would look exactly like a crash and
// would be blamed on one.
//
// So the hint only shortens the wait. Anything from the page - a reload, a
// state poll - cancels it outright, and a real close never comes back.
const browserLeaveGrace = 20 * time.Second

type browserUI struct {
	token    string
	addr     string
	srv      *http.Server
	mu       sync.Mutex
	lastSeen time.Time
	leaving  bool
	quit     chan struct{}
	once     sync.Once
}

// serveBrowserUI starts the local server, opens the browser, and blocks until
// the page stops checking in or Quit is called, mirroring w.Run().
//
// It is a thin wrapper over startBrowserUI + openInBrowser + wait, and it is
// thin on purpose: see startBrowserUI for why the split exists.
func serveBrowserUI(calls map[string]uiCall, logf func(string, ...interface{})) error {
	if logf == nil {
		logf = func(string, ...interface{}) {}
	}
	b, url, err := startBrowserUI(calls, logf)
	if err != nil {
		return err
	}
	logf("browser window: no WebView2 runtime, so the interface is a page in your " +
		"default browser instead. Nothing else is different.")
	logf("browser window: %s", url)
	openInBrowser(url, logf)
	return b.wait(logf)
}

// startBrowserUI builds the server and starts listening, WITHOUT opening a
// browser and without blocking. It returns the running instance and its URL.
//
// # WHY THIS IS SPLIT OUT
//
// sendData uploads a contributor's data and applyUpdate downloads and runs a
// binary. Both sit behind authorised(), and a local HTTP server is reachable by
// any page in the browser, so that function is the only thing between a hostile
// tab and either of them.
//
// ui_browser_selftest.go proves authorised() is CORRECT - right token accepted,
// wrong token refused, truncated token refused, cross-site refused. It does not
// prove the three handlers CALL it: every one of those checks builds a synthetic
// httptest.NewRequest and hands it straight to the predicate. A handler that
// forgot the call would leave all of them green - the guard tested, the wiring
// untested, which is this project's silent-success shape.
//
// Testing the wiring means driving the real routes over a real socket, and that
// was impossible while starting the server also launched a browser: a selftest
// cannot open a tab on somebody's machine. Hence the seam. serveBrowserUI is
// unchanged in behaviour; it just calls this first.
func startBrowserUI(calls map[string]uiCall, logf func(string, ...interface{})) (*browserUI, string, error) {
	if logf == nil {
		logf = func(string, ...interface{}) {}
	}

	// A token, not a password. 32 bytes from crypto/rand, and NO fallback if
	// that fails - identity.go already settled this argument for the install
	// id and the reasoning is stronger here. A token seeded from the clock
	// would be guessable by anything that knows roughly when the program
	// started, which is every page the person has open.
	raw := make([]byte, 32)
	if _, err := rand.Read(raw); err != nil {
		return nil, "", fmt.Errorf("no secure random source, so the local page cannot be "+
			"protected and will not be started: %w", err)
	}
	b := &browserUI{
		token:    hex.EncodeToString(raw),
		quit:     make(chan struct{}),
		lastSeen: time.Now(),
	}

	// Port 0 = let the OS choose. Loopback only.
	ln, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		return nil, "", fmt.Errorf("could not open a local port for the window: %w", err)
	}
	b.addr = ln.Addr().String()

	mux := http.NewServeMux()
	base := "/" + b.token

	mux.HandleFunc(base+"/", func(w http.ResponseWriter, r *http.Request) {
		if !b.authorised(r) {
			http.NotFound(w, r)
			return
		}
		b.seen()
		// No caching, ever. A stale panel showing a capture count from ten
		// minutes ago is indistinguishable from a collector that has stopped.
		w.Header().Set("Cache-Control", "no-store, must-revalidate")
		w.Header().Set("Content-Type", "text/html; charset=utf-8")
		// Nothing here should ever be framed or fetched by another origin.
		w.Header().Set("X-Frame-Options", "DENY")
		w.Header().Set("Referrer-Policy", "no-referrer")
		fmt.Fprint(w, browserPage(b.token))
	})

	mux.HandleFunc(base+"/call/", func(w http.ResponseWriter, r *http.Request) {
		if !b.authorised(r) {
			http.NotFound(w, r)
			return
		}
		b.seen()
		name := strings.TrimPrefix(r.URL.Path, base+"/call/")
		fn, ok := calls[name]
		if !ok {
			http.Error(w, "no such action", http.StatusNotFound)
			return
		}
		var arg json.RawMessage
		if r.Body != nil {
			_ = json.NewDecoder(http.MaxBytesReader(w, r.Body, 64*1024)).Decode(&arg)
		}
		v, err := fn(arg)
		w.Header().Set("Content-Type", "application/json")
		w.Header().Set("Cache-Control", "no-store")
		if err != nil {
			// Actions return their problems as text for the person to read;
			// reaching here means something unexpected, so say so rather than
			// returning a success shape with nothing in it.
			_ = json.NewEncoder(w).Encode(map[string]interface{}{"error": err.Error()})
			return
		}
		_ = json.NewEncoder(w).Encode(map[string]interface{}{"result": v})
	})

	// "I am going away" - a hint, not an order. See browserLeaveGrace.
	mux.HandleFunc(base+"/leaving", func(w http.ResponseWriter, r *http.Request) {
		if !b.authorised(r) {
			http.NotFound(w, r)
			return
		}
		b.mu.Lock()
		b.leaving = true
		b.lastSeen = time.Now()
		b.mu.Unlock()
		w.WriteHeader(http.StatusNoContent)
	})

	b.srv = &http.Server{
		Handler:           mux,
		ReadHeaderTimeout: 10 * time.Second,
	}

	go func() {
		if err := b.srv.Serve(ln); err != nil && err != http.ErrServerClosed {
			logf("browser window: the local server stopped: %v", err)
			b.Quit()
		}
	}()

	return b, "http://" + b.addr + base + "/", nil
}

// wait blocks until the page stops checking in or Quit is called.
func (b *browserUI) wait(logf func(string, ...interface{})) error {
	if logf == nil {
		logf = func(string, ...interface{}) {}
	}

	// Watchdog. The page checks in on every state() poll; when it stops for
	// long enough, the person has closed the tab.
	tick := time.NewTicker(5 * time.Second)
	defer tick.Stop()
	for {
		select {
		case <-b.quit:
			ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
			_ = b.srv.Shutdown(ctx)
			cancel()
			return nil
		case <-tick.C:
			b.mu.Lock()
			idle := time.Since(b.lastSeen)
			limit := browserIdleTimeout
			why := "has not checked in"
			if b.leaving {
				limit = browserLeaveGrace
				why = "was closed"
			}
			b.mu.Unlock()
			if idle > limit {
				logf("browser window: the page %s (%s), so the collector is stopping.",
					why, idle.Round(time.Second))
				b.Quit()
			}
		}
	}
}

// seen records contact from the page AND cancels any pending close.
//
// The cancel is the important half: a refresh fires pagehide and then
// immediately reloads, so without clearing the flag here, pressing F5 would
// shut the collector down twenty seconds later for no reason anybody could see.
func (b *browserUI) seen() {
	b.mu.Lock()
	b.lastSeen = time.Now()
	b.leaving = false
	b.mu.Unlock()
}

func (b *browserUI) Quit() {
	b.once.Do(func() { close(b.quit) })
}

// authorised checks the token in constant time and rejects anything the browser
// itself labels as cross-site.
func (b *browserUI) authorised(r *http.Request) bool {
	// The token is in the path, so a request that reached a handler at all
	// already matched the prefix - but check it explicitly rather than relying
	// on ServeMux's prefix matching, which is not a security boundary and was
	// never meant to be one.
	parts := strings.SplitN(strings.TrimPrefix(r.URL.Path, "/"), "/", 2)
	if len(parts) == 0 {
		return false
	}
	if subtle.ConstantTimeCompare([]byte(parts[0]), []byte(b.token)) != 1 {
		return false
	}
	// Set by the browser, not by the page. "cross-site" is a hostile tab;
	// "none" is somebody typing the URL, which is fine. Absent means an older
	// browser, and refusing those would break the fallback for exactly the
	// people who need it most.
	switch r.Header.Get("Sec-Fetch-Site") {
	case "cross-site", "same-site":
		return false
	}
	return true
}

// openInBrowser asks Windows to open the URL with whatever the person uses.
//
// rundll32 url.dll,FileProtocolHandler rather than `cmd /c start`, because
// `start` treats the first quoted argument as a window title and a URL
// containing an ampersand splits the command line. Neither failure is visible -
// the browser simply opens the wrong thing or nothing at all.
func openInBrowser(url string, logf func(string, ...interface{})) {
	if err := exec.Command("rundll32", "url.dll,FileProtocolHandler", url).Start(); err != nil {
		logf("browser window: could not open your browser automatically (%v).", err)
		logf("browser window: open this address yourself: %s", url)
	}
}

// browserPage is uiHTML with a shim in front of it.
//
// THE PAGE ITSELF IS NOT COPIED, MODIFIED, OR FORKED. uiHTML is one string used
// by both transports; this only prepends the functions that the webview would
// otherwise have injected. A second copy of the interface would drift from the
// first within a week, and the drift would be invisible until somebody without
// WebView2 reported a button that did nothing.
func browserPage(token string) string {
	shim := `<script>
(function () {
  var base = "/` + token + `";

  // The webview injects these as functions returning Promises. Recreate the
  // same contract exactly, so the page below is unchanged and unaware.
  function call(name) {
    return function (arg) {
      return fetch(base + "/call/" + name, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(arg === undefined ? null : arg)
      }).then(function (r) { return r.json(); })
        .then(function (j) {
          if (j.error) { throw new Error(j.error); }
          return j.result;
        });
    };
  }

  // uiReady is in this list for a reason. The page calls it unconditionally,
  // and a browser without it would throw on the first line of its own
  // bootstrap - breaking the fallback that exists to rescue a broken bridge.
  var names = ["state","captureNow","countData","sendData","checkUpdate",
               "applyUpdate","canPackage","makePackage","openCaptures",
               "restartNow","uiReady"];
  for (var i = 0; i < names.length; i++) { window[names[i]] = call(names[i]); }

  // Closing the tab is how somebody stops it, so say so on the way out rather
  // than making the program wait five minutes to work it out. This is a HINT -
  // pagehide also fires on refresh, so the program only shortens its wait and
  // cancels entirely if the page comes back.
  window.addEventListener("pagehide", function () {
    // keepalive, because a normal fetch is cancelled when the page unloads and
    // this one has to outlive it.
    try { fetch(base + "/leaving", { method: "POST", keepalive: true }); } catch (e) {}
  });
}());
</script>
`
	// Inserted before the page's own <script>, so the functions exist by the
	// time anything calls them.
	return strings.Replace(uiHTML, "<script>", shim+"<script>", 1)
}
