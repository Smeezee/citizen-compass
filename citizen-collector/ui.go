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
)

// pinBundledRuntime makes the BUNDLED runtime the one that actually loads, by
// relaunching once with the variable inherited from process creation.
//
// WHY A RELAUNCH RATHER THAN JUST os.Setenv
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
	cmd := exec.Command(exe, os.Args[1:]...)
	cmd.Env = append(os.Environ(), runtimeEnvVar+"="+dir, reexecGuard+"=1")
	if err := cmd.Start(); err != nil {
		uiRuntimeNote = "bundled runtime found but relaunch failed: " + err.Error()
		return false
	}
	return true
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
func runUI(cfg autoConfig, outDir, exeDir, autoLogPath string, hotkeySpec string) error {
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
	logf("---- citizen-collector %s (%s) UI start ----", Version, BuildVariant)
	// Reported from what will ACTUALLY be used, not from what was intended.
	logf("webview2 runtime: %s", verifiedRuntimeNote(exeDir))

	seq := nextSequence(outDir)

	// THE ENGINE. Same loop the command line runs - not a reimplementation.
	// §7: it follows the game, because runAuto's window gate already means no
	// game window is no capture. There is nothing to start and nothing to stop.
	var hotkeyPresses <-chan struct{}
	hotkeyName := ""
	if hl, err := startHotkeyListener(hotkeyID, hotkeySpec); err != nil {
		logf("WARNING: hotkey %q NOT REGISTERED: %v - the button in the window still works", hotkeySpec, err)
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
		capture: func(t Trigger) (string, error) {
			p, err := doCapture(outDir, false, "", "", seq, t)
			if err == nil {
				seq++
			}
			return p, err
		},
	}

	stop := make(chan struct{})
	go func() { _ = runAuto(cfg, autoLogPath, deps, stop) }()
	defer close(stop)

	uid := defaultUIDeps(outDir, autoLogPath)

	w := webview2.NewWithOptions(webview2.WebViewOptions{
		Debug:     false,
		AutoFocus: true,
		WindowOptions: webview2.WindowOptions{
			Title:  "Citizen Collector",
			Width:  460,
			Height: 520,
			Center: true,
		},
	})
	if w == nil {
		return fmt.Errorf("the window could not be created")
	}
	defer w.Destroy()

	// state() is called by the page on a timer. Every call rebuilds from
	// reality; nothing is cached between calls (§9).
	w.Bind("state", func() string {
		b, _ := json.Marshal(buildUIState(uid))
		return string(b)
	})

	// CAPTURE NOW. §8's one button plus this: a button cannot silently fail to
	// register, which the hotkey demonstrably can.
	w.Bind("captureNow", func() string {
		if err := deps.gameAlive(); err != nil {
			return "Star Citizen isn't running, so there's nothing to photograph yet."
		}
		p, err := deps.capture(Trigger{Kind: "hotkey", Note: "button"})
		if err != nil {
			logf("button capture FAILED: %v", err)
			return "That didn't work. The details are in the log file."
		}
		logf("captured %s  <- button (manual)", filepath.Base(p))
		return "Saved " + filepath.Base(p)
	})

	w.Bind("openCaptures", func() string {
		_ = os.MkdirAll(outDir, 0o755)
		_ = exec.Command("explorer.exe", outDir).Start()
		return ""
	})

	w.SetHtml(uiHTML)
	w.Run()
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
  body {
    margin: 0; padding: 26px 24px;
    font: 15px/1.5 "Segoe UI Variable Text", "Segoe UI", system-ui, sans-serif;
    background: #14171c; color: #e8ecf2;
    user-select: none; -webkit-user-select: none;
  }
  h1 { font-size: 13px; font-weight: 600; letter-spacing: .09em;
       text-transform: uppercase; color: #7e8794; margin: 0 0 22px; }
  .status { display: flex; align-items: flex-start; gap: 11px; margin-bottom: 4px; }
  .dot { width: 11px; height: 11px; border-radius: 50%; margin-top: 6px; flex: none;
         background: #59606b; transition: background .3s; }
  .dot.on { background: #46c17c; box-shadow: 0 0 0 4px rgba(70,193,124,.16); }
  .headline { font-size: 19px; font-weight: 600; color: #59606b; transition: color .3s; }
  .headline.on { color: #e8ecf2; }
  .sub { margin: 2px 0 0 22px; color: #8b95a3; font-size: 13.5px; min-height: 20px; }
  button {
    width: 100%; padding: 13px 16px; margin-top: 18px;
    font: 600 15px/1 inherit; color: #0d1014; background: #46c17c;
    border: 0; border-radius: 7px; cursor: pointer;
  }
  button:hover  { background: #52cf89; }
  button:active { transform: translateY(1px); }
  button.ghost  { background: transparent; color: #b9c2cd;
                  border: 1px solid #2d333c; margin-top: 9px; }
  button.ghost:hover { background: #1b1f26; color: #e8ecf2; }
  .note { margin-top: 14px; font-size: 12.5px; color: #6f7885; text-align: center; }
  .panel { margin-top: 20px; border-top: 1px solid #232830; padding-top: 15px;
           font-size: 12.5px; color: #7e8794; }
  .row { display: flex; gap: 10px; margin-bottom: 7px; }
  .row .k { flex: none; width: 78px; color: #626b78; }
  .row .v { flex: 1; color: #b9c2cd; word-break: break-all; }
  .problem { margin-top: 16px; padding: 11px 13px; border-radius: 7px;
             background: #3a2a18; color: #ffcf94; font-size: 13.5px; display: none; }
  .toast { margin-top: 11px; font-size: 13px; color: #46c17c; min-height: 18px; text-align: center; }
  .log { margin-top: 4px; font: 11.5px/1.55 Consolas, monospace; color: #5d6673;
         white-space: pre-wrap; word-break: break-all; }
</style></head><body>
  <h1>Citizen Collector</h1>

  <div class="status">
    <div class="dot" id="dot"></div>
    <div>
      <div class="headline" id="headline">Starting…</div>
    </div>
  </div>
  <div class="sub" id="sub"></div>

  <div class="problem" id="problem"></div>

  <button id="send">Send my data back</button>
  <button class="ghost" id="capture">Take a picture now</button>
  <button class="ghost" id="open">Open the pictures folder</button>
  <div class="toast" id="toast"></div>

  <div class="note">Nothing leaves your computer until you press that button.</div>

  <div class="panel">
    <div class="row"><div class="k">Watching</div><div class="v" id="logpath">—</div></div>
    <div class="row"><div class="k">Pictures</div><div class="v" id="captures">—</div></div>
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
  document.getElementById('send').addEventListener('click', function () {
    toast('Not built yet — coming next.');
  });

  refresh();
  setInterval(refresh, 1500);
</script>
</body></html>`

// uiHTMLContains is used by the selftest to assert the interface carries the
// things WO-UI-01 §2 requires, without launching a window on a build machine.
func uiHTMLContains(s string) bool { return strings.Contains(uiHTML, s) }
