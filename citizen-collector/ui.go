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
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"sync"
	"time"
)

const (
	runtimeEnvVar = "WEBVIEW2_BROWSER_EXECUTABLE_FOLDER"
	// reexecGuard stops the relaunch below from recursing. Without it a failure
	// to apply the variable would fork forever.
	reexecGuard = "CITIZEN_COLLECTOR_RUNTIME_PINNED"
	// superviseGuard marks the child, so it never tries to supervise itself.
	superviseGuard = "CITIZEN_COLLECTOR_SUPERVISED"
)

// runUI opens the window and runs until it is closed.
func runUI(cfg autoConfig, outDir, exeDir, autoLogPath, hotkeySpec, localURL, localKey string,
	clearAfterSend, offerShortcuts bool) error {
	// BEFORE ANYTHING IS WRITTEN, including the log.
	//
	// The log lives beside the exe, so opening it first would put one more file
	// on the Desktop while deciding whether this program should be putting files
	// on the Desktop. Ahead of the runtime relaunch too - there is no point
	// starting a second process that is going to reach the same conclusion.
	if GuardInstallLocation(exeDir, nil) {
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

	// PASTED ANGLE BRACKETS ARE STRIPPED, AND SAID OUT LOUD.
	//
	// send_key was written as <the-key> on Sleven's own machine, which is what a
	// printed template invites. The collector then sent a key two characters
	// longer than the Worker's secret and got a 403 that looks exactly like a
	// broken endpoint.
	var strippedURL, strippedKey bool
	localURL, strippedURL = StripWrappingBrackets(localURL)
	localKey, strippedKey = StripWrappingBrackets(localKey)
	if strippedURL {
		logf("settings: send_url was wrapped in < > - the brackets have been " +
			"removed for this run. Take them out of collector-settings.txt.")
	}
	if strippedKey {
		logf("settings: send_key was wrapped in < > - the brackets have been " +
			"removed for this run. Left in place they add two characters to the " +
			"key and every send is refused with 403, which reads as a broken " +
			"receiver. Take them out of collector-settings.txt.")
	}
	for _, w := range []string{BracketWarning("send_url", localURL), BracketWarning("send_key", localKey)} {
		if w != "" {
			logf("settings: WARNING - %s", w)
		}
	}

	// WHERE THIS MACHINE SENDS. Local settings win outright; the fallback is
	// whatever the feed supplied on a previous run and this machine remembered.
	// The update check may supply a fresher one - see checkUpdate in
	// ui_actions.go.
	dest := ResolveDestination(localURL, localKey, "", "", LoadCachedDestination(exeDir))
	sendURL, sendKey := dest.URL, dest.Key
	if dest.Configured() {
		logf("destination: sending to %s (from %s)", sendURL, dest.Source)
	} else {
		logf("destination: NOTHING IS CONFIGURED YET, so SEND will only write a " +
			"zip to this computer. The next update check may supply an address.")
	}

	// AFTER the instance check, and after the runtime relaunch, so exactly one
	// process ever offers and it is the one that goes on to open a window. A
	// launch that turns out to be a duplicate now exits without having touched
	// the Desktop - which it previously did, every time, on its way out.
	// ASKED ONCE, AFTER CONSENT, AND NEVER RETROACTIVELY.
	//
	// An install upgraded from 0.3.1 has no recorded answer, so it is asked -
	// and until it answers it is on ask-every-time. Sleven's wife and his friend
	// agreed to a README that says nothing is ever sent on its own; they get the
	// question before that becomes untrue, not afterwards.
	sendMode := AskSendChoice(exeDir, logf)
	logf("send mode: %s", sendMode)

	// STARTS WITH WINDOWS, and says how to stop it in the same breath.
	//
	// A per-user startup entry, not a service - see autostart.go for why, which
	// is that a service runs outside the desktop session and could neither
	// capture the screen nor show this window.
	if !AutostartEnabled() {
		if exe, err := os.Executable(); err == nil {
			if err := EnableAutostart(exe, exeDir); err != nil {
				logf("autostart: could not set it to start with Windows (%v) - "+
					"everything else works, you just have to open it yourself.", err)
			} else {
				logf("autostart: it will now start with Windows and wait for Star Citizen.")
				logf("autostart: %s", AutostartRemovalInstructions())
			}
		}
	}

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

	// THE THIRD DOOR. Right-click the icon by the clock -> "Send my data now".
	//
	// This is the one that works when the window does not and the person has
	// never opened a terminal, which is exactly the situation that produced
	// this feature: 26 captures, a working hotkey, and no way to send any of it.
	//
	// Same core as the button and the -send flag - see send_now.go.
	if tray != nil {
		tray.onSend = func() {
			// RESOLVED HERE, NOT CAPTURED. The update check may have supplied a
			// destination since this window opened.
			d := ResolveDestination(localURL, localKey, "", "", LoadCachedDestination(exeDir))
			if !d.Configured() {
				showErrorBox("Citizen Collector",
					"There is nowhere to send to yet, so nothing was sent.\n\n"+
						"Leave this open for a minute while you have an internet "+
						"connection - it collects the address by itself.")
				return
			}
			tray.SetStatus("Citizen Collector - sending...")
			note, err := SendNow(exeDir, outDir, d.URL, d.Key, clearAfterSend, logf)
			if err != nil {
				logf("tray send: FAILED - %v", err)
				tray.SetStatus("Citizen Collector - send failed")
				showErrorBox("Citizen Collector",
					"That did not work:\n\n"+err.Error()+
						"\n\nNothing was deleted. Everything is still on this computer.")
				return
			}
			logf("tray send: %s", note)
			tray.SetStatus("Citizen Collector - sent")
			messageBox("Citizen Collector", note, 0x00000040)
		}
	}
	defer tray.Stop()
	tray.SetStatus("Citizen Collector - waiting for Star Citizen")

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
			Activity("Star Citizen closed. Reading the session and tidying up.")
			logf("live: %d transactions, %d deaths, %d ships seen while playing",
				len(liveStore.Txns), len(liveStore.Deaths), len(liveStore.Ships))

			// KEEP THE WHOLE SESSION LOG, BEFORE ANYTHING ELSE (V1 §3).
			//
			// The miner below reads the fields it understands and drops the
			// rest; the game overwrites Game.log on its next launch. Whatever
			// is not kept here cannot be recovered by any future parser, so it
			// is kept first: if the mine fails, the raw session is still safe.
			//
			// It stays on this computer - see diary.go. The scrubbed dataset is
			// what travels.
			if lp, _ := findLogFromRunningGame(); lp != "" {
				if dest, kept, err := KeepDiary(exeDir, lp, "game-exit",
					ReadGameLog(lp, "diary"), logf); kept && err == nil {
					Activity("Kept this session's whole log on this computer: %s",
						filepath.Base(dest))
				} else if err != nil {
					logf("diary: this session was NOT kept (%v) - the session is "+
						"lost when the game next overwrites its log", err)
				}
			}
			in, err := LoadOrCreateInstall(exeDir, logf)
			if err != nil {
				logf("mine: continuing without a contributor id (%v)", err)
			}
			if _, err := MineAll(outDir, in, logf); err != nil {
				logf("mine: this pass did not complete: %v", err)
			}

			// THE SESSION IS OVER. Act on what this person actually chose, and
			// on nothing else.
			//
			// Read from disk at the moment it is needed rather than captured at
			// startup: the choice is changeable from the window, and a value
			// read hours ago would honour an answer that has since been
			// withdrawn. For a decision about sending somebody's screenshots,
			// the freshest reading is the only honest one.
			AutoSendIfChosen(exeDir, outDir, logf)
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

	// THE STARTUP SWEEP (V1 §3).
	//
	// A session only reaches the diary through onGameExit, and there are
	// obvious ways to miss that: the collector was closed while the game ran,
	// it crashed, the machine was restarted. This picks up a log that is on
	// disk and not yet kept, so those sessions are not lost - and because the
	// diary is keyed on the log's CONTENT, a session already kept at exit is
	// recognised and not stored twice.
	go func() {
		defer logPanic(logf, exeDir, "the diary sweep")
		if lp, _ := findLogFromRunningGame(); lp != "" {
			if _, kept, err := KeepDiary(exeDir, lp, "startup-sweep",
				ReadGameLog(lp, "diary"), logf); err != nil {
				logf("diary: startup sweep could not keep %s (%v)", lp, err)
			} else if kept {
				logf("diary: a session that was never kept at exit has been " +
					"picked up now")
			}
		}
	}()

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
		Deps:    uid,
		Auto:    deps,
		ExeDir:  exeDir,
		OutDir:  outDir,
		SendURL: sendURL,
		SendKey: sendKey,
		// What this machine's own settings file said, kept so the feed can
		// never repoint a collector somebody configured deliberately.
		LocalURL:       localURL,
		LocalKey:       localKey,
		ClearAfterSend: clearAfterSend,
		Logf:           logf,
	})
	// The tray is the only place a person sees a message without opening a
	// file, so long-running work reports there. Set after the tray exists; if
	// the notification area refused the icon this stays a harmless no-op.
	uiNotify = tray.SetStatus

	// ===================================================================
	// THE NATIVE WINDOW - Sleven's ruling, 2026-08-15
	// ===================================================================
	//
	// The tray is home. The window is something you open when you want it,
	// never something you need, and it is a plain Windows window with no
	// browser engine underneath - see window.go for why.
	//
	// WEBVIEW2 IS STILL BELOW THIS, deliberately and temporarily. The order
	// keeps it working until the new window passes on his machine, because he
	// needs a usable collector in the meantime. Once it passes, everything from
	// here down goes - the browser fallback, the bridge timeout and the parity
	// check with it. Half-removed would be worse than either.
	{
		// The question is asked ONCE, and never of an install that predates it -
		// see window_settings.go. An update must not interrogate somebody who
		// did not ask for it.
		show := AskWindowChoice(exeDir, logf)

		stateFn := func() uiState { return buildUIState(uid) }
		if tray != nil {
			tray.onOpenWindow = func() {
				ShowCollectorWindow(exeDir, outDir, stateFn, acts, logf)
			}
			tray.onCaptureNow = func() { _, _ = acts["captureNow"](nil) }
			tray.onOpenPictures = func() { _, _ = acts["openCaptures"](nil) }
			tray.onRevert = func() {
				msg, err := RevertToPrevious(exeDir, logf)
				if err != nil {
					showErrorBox("Citizen Collector", err.Error())
					return
				}
				messageBox("Citizen Collector", msg, 0x00000040)
			}
		}

		if show {
			// ASKED FOR, NOT CREATED HERE. This goroutine has no message loop;
			// the tray's thread does. Creating it here produced a window that
			// drew once and then answered nothing.
			if tray == nil || !tray.RequestOpenWindow() {
				logf("window: the tray is not available, so the window cannot be " +
					"opened. The collector is running and still collecting.")
			} else {
				logf("window: open. Closing it leaves the collector running in the tray.")
			}
		} else {
			logf("window: staying in the tray, as chosen. Right-click the icon by " +
				"the clock to open it, send, or stop.")
		}

		// THE TRAY'S MESSAGE LOOP IS NOW THE PROGRAM'S LIFETIME. It is the one
		// surface that is always present, which is exactly why the revert lives
		// there too.
		waitForTrayExit(tray)
		return nil
	}

	// There is no other path. The native window is the UI; the tray is home.
	//
	// What used to be here: a WebView2 window, a browser fallback serving the
	// same page over 127.0.0.1, a twelve-second bridge timeout to notice when
	// the embedded browser opened a window and then answered nothing, and a
	// parity check keeping the two transports' function lists identical. All of
	// it existed to prop up an embedded browser, and all of it is gone. See
	// _to_delete/webview2_path_retired_20260815/.
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
    <button class="ghost" id="senddata">Send everything</button>
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
          '  —  NOT registered, because another copy of Citizen Collector is ' +
          'already running and has claimed this key. Installing a new copy does ' +
          'not stop the old one: close the other window, or end 'collector.exe' ' +
          'in Task Manager, then start this again. The button below works either way.';
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
    // THERE IS NO LONGER A SCREENSHOT QUESTION. Consent v3 says plainly that
    // "Screenshots ARE uploaded when you send", so offering "data only" here
    // would contradict the promise the person already agreed to - and a
    // choice that can silently reduce what is sent is how the code and the
    // promise drifted apart in the first place. The screen still states
    // exactly what is about to leave, and Cancel still cancels.
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
        msg += ' This includes ' + d.frames + ' screenshots. Screenshots are NOT ' +
               'scrubbed - a frame can show your handle, the names of players near ' +
               'you, and chat. They are used internally only, are never published ' +
               'or shared, and nothing taken from a picture ever carries ' +
               'a player name.';
      }
      if (d.held_back > 0) {
        msg += ' (' + d.held_back + ' picture(s) will be left out either way - they ' +
               'cannot prove they photographed the game.)';
      }
      document.getElementById('sendmsg').textContent = msg;
      choice.style.display = '';
      btn.style.display = 'none';

      function done(withPNG) {
        choice.style.display = 'none';
        btn.style.display = '';
        if (withPNG === null) { toast('Nothing was written.'); return; }
        toast('Packaging…');
        window.sendData(withPNG).then(toast);
      }
      document.getElementById('senddata').onclick   = function () { done(true); };
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

  // SAY HELLO FIRST. This is what proves the bridge works; if it never
  // arrives the program scraps this window and uses the browser instead.
  // Called before refresh() so a failure is detected even if state() is what
  // is broken.
  try { window.uiReady(); } catch (e) {}

  refresh();
  setInterval(refresh, 1500);
</script>
</body></html>`

// uiHTMLContains is used by the selftest to assert the interface carries the
// things WO-UI-01 §2 requires, without launching a window on a build machine.
func uiHTMLContains(s string) bool { return strings.Contains(uiHTML, s) }
