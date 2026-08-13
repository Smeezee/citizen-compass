package main

// ui.go - the window. WO-UI-01 §2, §3, §4.
//
// THE TEST THIS HAS TO PASS
//
//	A person who has never opened a terminal downloads a zip, unzips it,
//	double-clicks one thing, plays Star Citizen, and presses one button.
//
// So: no arguments opens this window (§4.1), never a console (§4.2), and the
// status is measured rather than remembered (§9 - see ui_state.go).
//
// The Go capture engine underneath is untouched. §3: "KEEP THE GO CAPTURE
// ENGINE... The UI drives it. The UI never reimplements it." runAuto is the
// same loop the command line has always used; this file starts it and reports
// on it, and contains no capture logic of its own.

import (
	"sync"
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"time"

	"github.com/jchv/go-webview2"
)

// bundledRuntimeDir is where the fixed-version WebView2 runtime lives relative
// to the exe. See WEBVIEW2_RUNTIME_PROVENANCE.md.
const bundledRuntimeDir = "webview2-runtime"

// resolveBundledRuntime points WebView2 at the runtime shipped beside the exe.
//
// # WHY THIS MATTERS MORE THAN IT LOOKS
//
// Sleven's ruling: the runtime being installed on the development machine is a
// trap, because the runtime-missing path cannot occur there and will never be
// exercised by normal testing. Bundling makes that failure impossible instead
// of rare - but ONLY if the bundled copy is actually the one loaded. If this
// silently falls back to a system install, the bundling is decoration and the
// first machine without the runtime is where anyone finds out.
//
// go-webview2 passes nil for browserExecutableFolder, so the WebView2 loader
// does its own resolution - and that resolution honours this environment
// variable. Setting it is therefore how the bundled copy wins.
//
// Returns the folder and how it was chosen, both of which are reported, because
// "which runtime am I actually running" must be answerable.
func resolveBundledRuntime(exeDir string) (dir string, how string) {
	root := filepath.Join(exeDir, bundledRuntimeDir)
	entries, err := os.ReadDir(root)
	if err != nil {
		return "", "no bundled runtime folder beside the exe"
	}
	// Version directories, newest name last.
	var versions []string
	for _, e := range entries {
		if e.IsDir() {
			versions = append(versions, e.Name())
		}
	}
	if len(versions) == 0 {
		return "", "bundled runtime folder is empty"
	}
	pick := versions[len(versions)-1]
	cand := filepath.Join(root, pick)

	// Presence of the actual engine, not merely of a directory. A folder that
	// exists but holds nothing would otherwise report success and then fail at
	// window creation with something unreadable.
	if _, err := os.Stat(filepath.Join(cand, "msedgewebview2.exe")); err != nil {
		return "", "bundled runtime folder has no msedgewebview2.exe"
	}
	return cand, "bundled " + pick
}

// uiRuntimeNote records what happened when the runtime was resolved, so the
// selftest and the window can both report it rather than assuming.
var uiRuntimeNote string

const (
	runtimeEnvVar = "WEBVIEW2_BROWSER_EXECUTABLE_FOLDER"
	// reexecGuard stops the relaunch below from recursing. Without it a failure
	// to apply the variable would fork forever.
	reexecGuard = "CITIZEN_COLLECTOR_RUNTIME_PINNED"
	// superviseGuard marks the child, so it never tries to supervise itself.
	superviseGuard = "CITIZEN_COLLECTOR_SUPERVISED"
)

// pinBundledRuntime makes the BUNDLED runtime the one that actually loads, by
// relaunching once with the variable inherited from process creation.
//
// # WHY A RELAUNCH RATHER THAN JUST os.Setenv
//
// Setting the variable in-process does not work, and this was measured, not
// assumed. With os.Setenv the log cheerfully reported
//
//	webview2 runtime: bundled 151.0.4129.59
//
// while the process had in fact loaded
//
//	C:\Program Files (x86)\Microsoft\EdgeWebView\Application\...
//
// go-webview2 loads WebView2Loader.dll from memory via go-winloader, and that
// copy resolves the runtime against the environment block the process was
// CREATED with. A variable set afterwards is not seen. Pre-setting it in the
// parent and launching again loads the bundled copy - the difference was
// confirmed by looking at which msedgewebview2.exe was actually running.
//
// That old log line is the exact defect this project keeps finding: it reported
// an INTENTION as though it were an OUTCOME. On this machine, where a system
// runtime exists, everything worked and nothing would ever have shown it.
//
// Returns true when a relaunch was started and this process should exit.
func pinBundledRuntime(exeDir string) bool {
	dir, how := resolveBundledRuntime(exeDir)
	uiRuntimeNote = how

	// No bundle: fall back to a system runtime. Deliberately not fatal -
	// refusing to start would turn a degraded state into no program at all.
	if dir == "" {
		return false
	}
	// Already inherited correctly, or already relaunched once. Either way,
	// going round again would be a loop.
	if os.Getenv(runtimeEnvVar) == dir || os.Getenv(reexecGuard) == "1" {
		return false
	}

	exe, err := os.Executable()
	if err != nil {
		uiRuntimeNote = "bundled runtime found but could not relaunch to use it: " + err.Error()
		return false
	}
	superviseChild(exe, dir, exeDir)
	return true
}

// superviseChild runs the window in a child process and RESTARTS it if it dies.
//
// # WHY THE PARENT STAYS
//
// The relaunch for the bundled runtime already created a parent/child pair, and
// the parent had nothing left to do but exit. Keeping it costs almost nothing
// and buys the thing WO-UI-01's audience actually needs: a person who starts
// this in the morning still has it running in the evening without checking.
//
// The supervisor is deliberately tiny. It owns no window, no WebView, no
// capture backend and no hotkey - the components that can crash are all in the
// child. A supervisor that shared their failure modes would be pointless.
//
// It restarts on ANY unexpected exit, and stops for the one case that means the
// person is finished: the child exiting 0, which is what closing the window
// does.
func superviseChild(exe, runtimeDir, exeDir string) {
	logPath := filepath.Join(exeDir, "collector-auto.log")

	say := func(format string, args ...interface{}) {
		f, err := openAutoLog(logPath)
		if err != nil {
			return
		}
		defer f.Close()
		fmt.Fprintf(f, "[%s] supervisor: %s\n",
			time.Now().Format("2006-01-02 15:04:05"), fmt.Sprintf(format, args...))
	}

	// Backoff so a child that fails instantly and repeatedly - a missing
	// runtime, a corrupt install - cannot become a spin loop that fills the
	// disk with log lines.
	backoff := 2 * time.Second
	const maxBackoff = 60 * time.Second

	for {
		started := time.Now()

		cmd := exec.Command(exe, os.Args[1:]...)
		cmd.Env = append(os.Environ(),
			runtimeEnvVar+"="+runtimeDir,
			reexecGuard+"=1",
			superviseGuard+"=1")
		if err := cmd.Start(); err != nil {
			say("could not start the collector: %v - giving up", err)
			return
		}

		err := cmd.Wait()
		ran := time.Since(started)

		// Closing the window is a clean exit and means the person is done.
		if err == nil {
			say("collector exited normally after %s - not restarting", ran.Round(time.Second))
			return
		}

		say("collector STOPPED UNEXPECTEDLY after %s (%v) - restarting in %s",
			ran.Round(time.Second), err, backoff)

		time.Sleep(backoff)

		// A child that survived a decent while was healthy; reset the backoff so
		// one bad night does not leave the delay pinned at a minute forever.
		if ran > 2*time.Minute {
			backoff = 2 * time.Second
		} else if backoff < maxBackoff {
			backoff *= 2
			if backoff > maxBackoff {
				backoff = maxBackoff
			}
		}
	}
}

// verifiedRuntimeNote reports the runtime this process will ACTUALLY use.
//
// Reported from the inherited environment rather than from what was intended,
// because the previous version of this note was wrong in precisely that way.
func verifiedRuntimeNote(exeDir string) string {
	inherited := os.Getenv(runtimeEnvVar)
	bundled, _ := resolveBundledRuntime(exeDir)
	switch {
	case bundled != "" && inherited == bundled:
		return "bundled, pinned and inherited: " + inherited
	case inherited != "":
		return "pinned to " + inherited + " (NOT the bundled copy)"
	case bundled == "":
		return "NO BUNDLED RUNTIME - falling back to whatever is installed on this machine"
	}
	return "bundled copy present but NOT pinned - a system runtime will be used"
}

// runUI opens the window and runs until it is closed.
func runUI(cfg autoConfig, outDir, exeDir, autoLogPath, hotkeySpec, sendURL, sendKey string,
	clearAfterSend, offerShortcuts bool) error {
	// Relaunch once so the bundled runtime is inherited from process creation.
	// This process then has nothing left to do.
	if pinBundledRuntime(exeDir) {
		return nil
	}

	lf, err := openAutoLog(autoLogPath)
	if err != nil {
		return fmt.Errorf("cannot open the log file: %w", err)
	}
	defer lf.Close()
	logf := func(format string, args ...interface{}) {
		fmt.Fprintf(lf, "[%s] %s\n", time.Now().Format("2006-01-02 15:04:05"),
			fmt.Sprintf(format, args...))
	}
	// ONE COLLECTOR. Checked AFTER the runtime relaunch, deliberately: the
	// parent that re-executes must not hold the mutex, or the child it just
	// started would see it and mistake itself for a duplicate. The process that
	// actually opens the window is the one that claims the instance.
	//
	// Checked after the log is open so a duplicate launch leaves a record. A
	// second launch that vanished silently would be indistinguishable from one
	// that crashed on startup.
	if yieldToExistingInstance(logf) {
		return nil
	}

	// AFTER the instance check, and after the runtime relaunch, so exactly one
	// process ever offers and it is the one that goes on to open a window. A
	// launch that turns out to be a duplicate now exits without having touched
	// the Desktop - which it previously did, every time, on its way out.
	if offerShortcuts {
		OfferShortcuts(exeDir, logf)
	}

	// A panic in ANY goroutine now lands in the log instead of a dead stderr.
	// On a -H windowsgui build there is no console, so this is the difference
	// between a stack trace and total silence.
	redirectStderrToLog(lf)
	defer logPanic(logf, exeDir, "the window process")

	logf("---- citizen-collector %s (%s) UI start ----", Version, BuildVariant)

	// Did the LAST run end through a path of its own? A leftover marker means
	// it did not - killed or crashed - which is the one thing an exit handler
	// can never report about itself.
	checkPreviousRun(exeDir, logf)

	// Reported from what will ACTUALLY be used, not from what was intended.
	// State the environment BEFORE anything can go wrong in it. See
	// startup_diag.go - four wrong hotkey diagnoses in two days would all have
	// been settled by these lines.
	LogStartupDiagnostics(logf, exeDir)

	// A visible sign of life. Built to fail without consequence - see tray.go.
	// If the notification area refuses it, the icon is missing and nothing else
	// changes.
	tray := StartTray(logf)
	defer tray.Stop()
	tray.SetStatus("Citizen Collector - waiting for Star Citizen")

	logf("webview2 runtime: %s", verifiedRuntimeNote(exeDir))

	seq := nextSequence(outDir)
	// seq is touched by the auto loop AND by the Capture-now button, which run
	// on different threads. Without this both read the same number, format the
	// same second-resolution filename, and the second write truncates the first.
	var seqMu sync.Mutex

	// liveStore accumulates during play; MineAll merges from the log files at
	// exit. Held here so the exit hook above can report what it saw.
	liveStore := newMineStore()

	// THE ENGINE. Same loop the command line runs - not a reimplementation.
	// §7: it follows the game, because runAuto's window gate already means no
	// game window is no capture. There is nothing to start and nothing to stop.
	var hotkeyPresses <-chan string
	hotkeyName := ""
	if hl, err := startHotkeyListener(hotkeyID, hotkeySpec); err != nil {
		// SAY WHAT IT ACTUALLY MEANS. "Hot key is already registered" reads as
		// "your hotkey is broken" and sends the reader hunting for a keyboard
		// conflict. The overwhelmingly common cause is another collector still
		// running - which is now prevented, so if this appears at all it is
		// worth naming the likely culprit rather than quoting the API.
		logf("NOTE: could not register %s (%v).", hotkeySpec, err)
		logf("      This almost always means another collector is still running - " +
			"check Task Manager for collector-master.exe. The button in the window works regardless.")
	} else {
		hotkeyPresses = hl.Presses
		hotkeyName = hl.Pretty
		logf("hotkey registered: %s", hl.Pretty)
	}

	deps := autoDeps{
		logf:       logf,
		hotkeys:    hotkeyPresses,
		hotkeyName: hotkeyName,
		gameAlive: func() error {
			_, err := findGameWindow(false, "")
			return err
		},
		// LIVE MINING AND THE EXIT MINE, IN THE MODE PEOPLE ACTUALLY RUN.
		//
		// Both were wired into --auto and left nil here. Review 2026-08-08 caught
		// it, and it is the SECOND time this exact gap has been found: main.go
		// already carries a comment celebrating the fix on the other branch. A
		// passing selftest proved the plumbing again, not the feature, because
		// the test supplies its own closure.
		onLogLine: func(line string) {
			liveStore.MineLive(line, "", "LIVE")
		},
		onGameExit: func() {
			logf("live: %d transactions, %d deaths, %d ships seen while playing",
				len(liveStore.Txns), len(liveStore.Deaths), len(liveStore.Ships))
			in, err := LoadOrCreateInstall(exeDir, logf)
			if err != nil {
				logf("mine: continuing without a contributor id (%v)", err)
			}
			if _, err := MineAll(outDir, in, logf); err != nil {
				logf("mine: this pass did not complete: %v", err)
			}
		},

		capture: func(t Trigger) (string, error) {
			seqMu.Lock()
			mySeq := seq
			seq++
			seqMu.Unlock()
			p, err := doCapture(outDir, false, "", "", mySeq, t)
			// The tooltip is the only place a person sees this without opening
			// a file, so it says the COUNT and the last reason - the two things
			// that distinguish "working" from "running".
			tray.SetStatus(fmt.Sprintf("Citizen Collector - %d captures, last: %s",
				seq+1, t.Reason()))
			if err == nil {
			}
			return p, err
		},
	}

	stop := make(chan struct{})
	go func() {
		defer logPanic(logf, exeDir, "the capture loop")
		_ = runAuto(cfg, autoLogPath, deps, stop)
	}()
	defer close(stop)

	uid := defaultUIDeps(outDir, autoLogPath)

	// What the window says about input. hotkeyName is "" exactly when
	// registration failed, which is the distinction the panel has to show:
	// a key that was never taken and a key that is broken look identical from
	// the outside, and only this knows which happened.
	uid.hotkey = hotkeyName
	uid.hotkeyOK = hotkeyName != ""
	if uid.hotkey == "" {
		uid.hotkey = hotkeySpec
	}
	uid.watchKeys = NewKeyWatcher(cfg.Keys).Describe()
	uid.settings = filepath.Join(exeDir, settingsFileName)

	// ONE DEFINITION OF WHAT THE BUTTONS DO. See ui_actions.go.
	//
	// Both transports dispatch into this map. Nothing below implements an
	// action; the bindings are three-line adapters that convert a typed webview
	// call into a JSON one, and the browser server does the same in the other
	// direction. That is the only way two front ends can be guaranteed not to
	// drift, and hard rule 14 is on the books because this project has been
	// bitten by drift five times.
	acts := buildUIActions(uiActionCtx{
		Deps:           uid,
		Auto:           deps,
		ExeDir:         exeDir,
		OutDir:         outDir,
		SendURL:        sendURL,
		SendKey:        sendKey,
		ClearAfterSend: clearAfterSend,
		Logf:           logf,
	})
	// The tray is the only place a person sees a message without opening a
	// file, so long-running work reports there. Set after the tray exists; if
	// the notification area refused the icon this stays a harmless no-op.
	uiNotify = tray.SetStatus

	callString := func(name string, arg interface{}) string {
		var raw json.RawMessage
		if arg != nil {
			raw, _ = json.Marshal(arg)
		}
		v, err := acts[name](raw)
		if err != nil {
			return "That didn't work: " + err.Error()
		}
		s, _ := v.(string)
		return s
	}

	// WEBVIEW2 OR THE BROWSER - decided here, once, and never asked about.
	//
	// A missing runtime used to be a dead end that the 271 MB package existed
	// to prevent. It is now simply the other path, and the person on the far
	// end is never told which one they got because there is nothing they could
	// usefully do with the information.
	if !webview2Available(exeDir) {
		logf("window: no WebView2 runtime found, using the browser instead")
		return serveBrowserUI(acts, logf)
	}

	w := webview2.NewWithOptions(webview2.WebViewOptions{
		Debug:     false,
		AutoFocus: true,
		WindowOptions: webview2.WindowOptions{
			Title:  "Citizen Collector",
			Width:  480,
			Height: 660,
			Center: true,
		},
	})
	if w == nil {
		// THE SECOND ANSWER TO THE SAME QUESTION, and the reason
		// webview2Available says it is not the last word.
		//
		// A runtime can be present on disk and still fail to load: wrong
		// architecture, a half-applied update, group policy, a profile
		// directory the user cannot write to. Before the browser path existed
		// this was a dead end and the program simply stopped. Now it is just
		// the other route, and the person never finds out anything went wrong.
		logf("window: the WebView2 window could not be created, using the browser instead")
		return serveBrowserUI(acts, logf)
	}
	defer w.Destroy()

	// The nine bindings. Each one is an adapter, not an implementation.
	w.Bind("state", func() string { return callString("state", nil) })
	w.Bind("captureNow", func() string { return callString("captureNow", nil) })
	w.Bind("countData", func() string { return callString("countData", nil) })
	w.Bind("sendData", func(includePNG bool) string { return callString("sendData", includePNG) })
	w.Bind("checkUpdate", func() string { return callString("checkUpdate", nil) })
	w.Bind("applyUpdate", func() string { return callString("applyUpdate", nil) })
	w.Bind("makePackage", func() string { return callString("makePackage", nil) })
	w.Bind("openCaptures", func() string { return callString("openCaptures", nil) })
	w.Bind("restartNow", func() string { return callString("restartNow", nil) })
	w.Bind("canPackage", func() bool {
		v, err := acts["canPackage"](nil)
		if err != nil {
			return false
		}
		ok, _ := v.(bool)
		return ok
	})

	w.SetHtml(uiHTML)
	w.Run()

	// w.Run returns when the window is closed. That is the one exit that means
	// the person is finished, and the supervisor treats it as final.
	logExit(logf, exeDir, "window closed")
	return nil
}

// Sequence numbering uses main.go's nextSequence, which reads the highest
// sequence already on disk. Counting files instead would restart numbering at
// the wrong place after a deletion and silently overwrite an earlier capture.

// uiHTML is the whole interface. §2: three states, one button, one reassurance
// line. Inline because a single self-contained executable is the distribution
// model and a file that can go missing is a failure mode nobody needs.
const uiHTML = `<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
  :root { color-scheme: dark; }
  * { box-sizing: border-box; }
  html, body { height: 100%; }
  body {
    margin: 0; padding: 22px 22px 18px;
    overflow: hidden;
    font: 15px/1.5 "Segoe UI Variable Text", "Segoe UI", system-ui, sans-serif;
    background: #14171c; color: #e8ecf2;
    user-select: none; -webkit-user-select: none;
  }
  h1 { font-size: 12px; font-weight: 600; letter-spacing: .09em;
       text-transform: uppercase; color: #7e8794; margin: 0 0 18px; }
  .status { display: flex; align-items: flex-start; gap: 11px; margin-bottom: 4px; }
  .dot { width: 11px; height: 11px; border-radius: 50%; margin-top: 6px; flex: none;
         background: #59606b; transition: background .3s; }
  .dot.on { background: #46c17c; box-shadow: 0 0 0 4px rgba(70,193,124,.16); }
  .headline { font-size: 19px; font-weight: 600; color: #59606b; transition: color .3s; }
  .headline.on { color: #e8ecf2; }
  .sub { margin: 2px 0 0 22px; color: #8b95a3; font-size: 13.5px; min-height: 20px; }
  button {
    width: 100%; padding: 12px 16px; margin-top: 15px;
    font: 600 15px/1 inherit; color: #0d1014; background: #46c17c;
    border: 0; border-radius: 7px; cursor: pointer;
  }
  button:hover  { background: #52cf89; }
  button:active { transform: translateY(1px); }
  button.ghost  { background: transparent; color: #b9c2cd;
                  border: 1px solid #2d333c; margin-top: 9px; }
  button.ghost:hover { background: #1b1f26; color: #e8ecf2; }
  .note { margin-top: 14px; font-size: 12.5px; color: #6f7885; text-align: center; }
  .panel { margin-top: 16px; border-top: 1px solid #232830; padding-top: 15px;
           font-size: 12.5px; color: #7e8794; }
  .row { display: flex; gap: 10px; margin-bottom: 7px; }
  .row .k { flex: none; width: 78px; color: #626b78; }
  .row .v { flex: 1; color: #b9c2cd; word-break: break-all; }
  .problem { margin-top: 16px; padding: 11px 13px; border-radius: 7px;
             background: #3a2a18; color: #ffcf94; font-size: 13.5px; display: none; }
  .toast { margin-top: 11px; font-size: 13px; color: #46c17c; min-height: 18px; text-align: center; }
  .log { margin-top: 4px; font: 11.5px/1.55 Consolas, monospace; color: #5d6673;
         white-space: pre-wrap; word-break: break-all; }
  .kv { display: flex; gap: 10px; margin-top: 7px; font-size: 13px; align-items: baseline; }
  .kv .k { color: #7e8794; flex: none; min-width: 92px; }
  .kv .v { color: #cfd6df; }
  .kv .v.bad { color: #e0a34a; }
</style></head><body>
  <h1>Citizen Collector</h1>

  <div class="status">
    <div class="dot" id="dot"></div>
    <div>
      <div class="headline" id="headline">Starting…</div>
    </div>
  </div>
  <div class="sub" id="sub"></div>

  <!-- THE KEY, ON SCREEN. The panel told a person the log path, the capture
       count and the folder - everything except the one thing they have to DO.
       Sleven, watching it run on a friend's machine: "there need to be a place
       for users to look at what the hotkey [is]". -->
  <div class="kv"><span class="k">Picture key</span><span class="v" id="hotkey">—</span></div>
  <div class="kv" id="watchrow" style="display:none"><span class="k">Watched keys</span><span class="v" id="watchkeys">—</span></div>

  <div class="problem" id="problem"></div>

  <!-- ALWAYS VISIBLE, whatever the answer.
       This used to be display:none unless an update existed, and the check ran
       once at startup. So on a machine with no update, a machine with no
       internet, or - as was true for the whole of 2026-08-08 - a feed that had
       never been published, the person saw absolutely nothing and had no way to
       ask. "I don't see an easy way for that to happen" was exactly right.
       A status you can read and click beats a box that appears by magic. -->
  <div class="note" id="updateline" title="Click to check again">Checking for updates…</div>
  <div id="updatebox" style="display:none">
    <div class="note" id="updatemsg" style="margin-bottom:6px"></div>
    <button id="updatego">Update now</button>
    <button class="ghost" id="updatelater">Not now</button>
  </div>
  <div id="restartbox" style="display:none">
    <div class="note" id="restartmsg" style="margin-bottom:6px"></div>
    <button id="restartgo">Restart now</button>
  </div>

  <button id="send">Send my data back</button>
  <div id="sendchoice" style="display:none">
    <div class="note" id="sendmsg" style="margin-bottom:6px"></div>
    <button class="ghost" id="senddata">Data only</button>
    <button class="ghost" id="sendboth">Include my screenshots too</button>
    <button class="ghost" id="sendcancel">Cancel</button>
  </div>
  <button class="ghost" id="capture">Take a picture now</button>
  <button class="ghost" id="open">Open the pictures folder</button>
  <button class="ghost" id="pkg" style="display:none">Make a copy to give somebody</button>
  <div id="pkgchoice" style="display:none">
    <!-- ONE package now. The two-option version offered "For any PC - about
         200 MB" against "Small - only if they already have WebView2", which
         was true until the browser fallback landed and then actively steered
         you to the 271 MB file you cannot send. The small one works
         everywhere now, so there is nothing left to choose. -->
    <div class="note" style="margin-bottom:6px">Makes a zip of about 6 MB that runs on
      any Windows PC with nothing to install. Your data, screenshots and contributor
      id are left out.</div>
    <button class="ghost" id="pkgmake">Make it</button>
    <button class="ghost" id="pkgcancel">Cancel</button>
  </div>
  <div class="toast" id="toast"></div>

  <div class="note">Nothing leaves your computer until you press that button.</div>

  <div class="panel">
    <div class="row"><div class="k">Watching</div><div class="v" id="logpath">—</div></div>
    <div class="row"><div class="k">Pictures</div><div class="v" id="captures">—</div></div>
    <div class="row"><div class="k">Data</div><div class="v" id="rows">—</div></div>
    <div class="log" id="recent"></div>
  </div>

<script>
  var toastTimer = null;
  function toast(msg) {
    var t = document.getElementById('toast');
    t.textContent = msg || '';
    if (toastTimer) clearTimeout(toastTimer);
    if (msg) toastTimer = setTimeout(function(){ t.textContent = ''; }, 6000);
  }

  function refresh() {
    window.state().then(function (raw) {
      var s = JSON.parse(raw);

      var hk = document.getElementById('hotkey');
      if (s.hotkey_ok) {
        hk.textContent = s.hotkey + '  —  press it any time to take a picture';
        hk.className = 'v';
      } else {
        // NOT SILENT WHEN IT FAILED. Registration really does fail - another
        // collector still running, a vendor utility that took the combination
        // first - and pressing a key that was never registered feels exactly
        // like pressing a broken one. This is the only place that difference
        // can be seen.
        hk.textContent = (s.hotkey || 'none') +
          '  —  NOT registered. Another collector may still be running. ' +
          'The button below works either way.';
        hk.className = 'v bad';
      }
      if (s.watch_keys) {
        document.getElementById('watchrow').style.display = '';
        document.getElementById('watchkeys').textContent = s.watch_keys;
      }

      document.getElementById('dot').className = 'dot' + (s.collecting ? ' on' : '');
      var h = document.getElementById('headline');
      h.textContent = s.headline;
      h.className = 'headline' + (s.collecting ? ' on' : '');

      var sub = '';
      if (s.captures > 0) {
        sub = s.captures + (s.captures === 1 ? ' picture saved' : ' pictures saved');
        if (s.last_capture) {
          sub += ' · last ' + s.last_capture;
          if (s.last_reason) sub += ' (' + s.last_reason + ')';
        }
      } else if (s.collecting) {
        sub = 'No pictures yet.';
      }
      document.getElementById('sub').textContent = sub;

      var p = document.getElementById('problem');
      if (s.problem) { p.textContent = s.problem; p.style.display = 'block'; }
      else { p.style.display = 'none'; }

      document.getElementById('logpath').textContent =
        s.log_path ? (s.log_path + (s.log_how ? '  (' + s.log_how + ')' : '')) : 'not found yet';
      document.getElementById('captures').textContent =
        s.captures + '  in  ' + s.capture_dir;
      // PENDING, not lifetime. A row already confirmed sent is dropped from
      // the local dataset (see MarkTxnsSent), so this count only ever shows
      // what SEND MY DATA would actually package right now.
      document.getElementById('rows').textContent =
        s.pending_rows + (s.pending_rows === 1 ? ' new row since your last send'
                                                : ' new rows since your last send');
      document.getElementById('recent').textContent = (s.recent_log || []).join('\n');
    });
  }

  document.getElementById('capture').addEventListener('click', function () {
    toast('…');
    window.captureNow().then(toast);
  });
  document.getElementById('open').addEventListener('click', function () {
    window.openCaptures();
  });

    // The package button only exists on the master build. It is hidden rather
    // than disabled, because a control you cannot use is a question you have to
    // answer every time you see it.
    //
    // THREE BUTTONS, NOT A CONFIRM BOX, AND THIS IS WHY.
    //
    // The first version asked with confirm(): OK meant "include the runtime",
    // Cancel meant "do not". Sleven pressed Cancel expecting nothing to happen
    // and got a 3.5 MB package - the wrong one to send, built anyway, with no
    // way to back out once the button was clicked.
    //
    // A two-state control cannot express three intentions. Cancel now cancels.
    canPackage().then(function (ok) {
      if (!ok) { return; }
      var btn = document.getElementById('pkg');
      var choice = document.getElementById('pkgchoice');
      btn.style.display = '';

      function show(showChoice) {
        choice.style.display = showChoice ? '' : 'none';
        btn.style.display = showChoice ? 'none' : '';
      }
      btn.addEventListener('click', function () { show(true); });
      document.getElementById('pkgcancel').addEventListener('click', function () {
        show(false);
        toast('Nothing was made.');
      });
      document.getElementById('pkgmake').addEventListener('click', function () {
        show(false);
        makePackage().then(toast);
      });
    });
  document.getElementById('send').addEventListener('click', function () {
    // Ask BEFORE writing, and say the real numbers.
    //
    // SAME FIX AS THE PACKAGE BUTTON. This used confirm() too, where Cancel
    // meant "data only" - so somebody who clicked Send and then changed their
    // mind got a zip written anyway. Cancel now cancels, and the two choices
    // are named rather than hidden behind OK.
    //
    // The screenshot question is asked every time on purpose: the dataset is
    // scrubbed and safe to hand to anyone, and a screenshot is not.
    window.countData().then(function (raw) {
      var d = JSON.parse(raw);
      var choice = document.getElementById('sendchoice');
      var btn = document.getElementById('send');
      // "New" because rows already confirmed sent were dropped from the
      // local dataset the moment they were confirmed - this is never the
      // whole history, only what happened since the last confirmed send.
      var msg = 'Ready to package ' + d.rows +
        (d.rows === 1 ? ' new row' : ' new rows') + ' of game data since your last send.';
      if (d.frames > 0) {
        msg += ' You also have ' + d.frames + ' screenshots. Screenshots are NOT ' +
               'scrubbed - a frame can show your handle, the names of players near ' +
               'you, and chat.';
      }
      if (d.held_back > 0) {
        msg += ' (' + d.held_back + ' picture(s) will be left out either way - they ' +
               'cannot prove they photographed the game.)';
      }
      document.getElementById('sendmsg').textContent = msg;
      document.getElementById('sendboth').style.display = d.frames > 0 ? '' : 'none';
      choice.style.display = '';
      btn.style.display = 'none';

      function done(withPNG) {
        choice.style.display = 'none';
        btn.style.display = '';
        if (withPNG === null) { toast('Nothing was written.'); return; }
        toast('Packaging…');
        window.sendData(withPNG).then(toast);
      }
      document.getElementById('senddata').onclick   = function () { done(false); };
      document.getElementById('sendboth').onclick   = function () { done(true); };
      document.getElementById('sendcancel').onclick = function () { done(null); };
    });
  });

  // UPDATES - always say something, and always be askable.
  //
  // A failed check is a normal state: no internet, or the feed not published
  // yet. It must never stop the window working, so nothing here is awaited by
  // anything else. But it must also never be SILENT, which is what it was.
  var updateLine = document.getElementById('updateline');
  var updateBox  = document.getElementById('updatebox');

  document.getElementById('updatelater').addEventListener('click', function () {
    updateBox.style.display = 'none';
  });
  document.getElementById('updatego').addEventListener('click', function () {
    toast('Downloading…');
    updateLine.textContent = 'Downloading the update…';
    applyUpdate().then(function (m) {
      toast(m);
      updateBox.style.display = 'none';
      updateLine.textContent = m;
      // The new file is in place but this process is still the old code, so
      // offer the restart rather than describing it. "Close it and open it
      // again" is a step, and steps are where people stop.
      if (m && m.indexOf('installed') !== -1) {
        document.getElementById('restartmsg').textContent = m;
        document.getElementById('restartbox').style.display = '';
      }
    });
  });
  document.getElementById('restartgo').addEventListener('click', function () {
    toast('Restarting…');
    restartNow();
  });

  function doUpdateCheck() {
    updateLine.textContent = 'Checking for updates…';
    checkUpdate().then(function (raw) {
      var u = {};
      try { u = JSON.parse(raw); } catch (e) {
        updateLine.textContent = 'Could not check for updates. Click to try again.';
        return;
      }
      if (u.problem) {
        updateLine.textContent = 'Could not check for updates: ' + u.problem +
                                 ' Click to try again.';
        return;
      }
      if (!u.available) {
        updateLine.textContent = 'Up to date \u00b7 version ' + u.current +
                                 '. Click to check again.';
        updateBox.style.display = 'none';
        return;
      }
      updateLine.textContent = 'An update is available.';
      document.getElementById('updatemsg').textContent =
        'Version ' + u.latest + ' is available. You have ' + u.current + '.' +
        (u.notes ? ' ' + u.notes : '');
      updateBox.style.display = '';
    });
  }
  updateLine.addEventListener('click', doUpdateCheck);
  doUpdateCheck();
  // Re-check every six hours. A collector left running across a weekend would
  // otherwise never learn about a release published on the Saturday.
  setInterval(doUpdateCheck, 6 * 60 * 60 * 1000);

  refresh();
  setInterval(refresh, 1500);
</script>
</body></html>`

// uiHTMLContains is used by the selftest to assert the interface carries the
// things WO-UI-01 §2 requires, without launching a window on a build machine.
func uiHTMLContains(s string) bool { return strings.Contains(uiHTML, s) }
