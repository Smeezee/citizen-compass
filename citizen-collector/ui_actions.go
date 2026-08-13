package main

// ui_actions.go - the nine things the window can do, defined ONCE.
//
// # WHY THIS FILE EXISTS
//
// Sleven, 2026-08-08: "if its not simple or one click ppl wont use it they will
// be like no there to many steps i do it later and later never comes."
//
// He is right, and it invalidated the plan that was in front of it. The package
// somebody has to be handed is 271 MB, and the ONLY reason it is that big is
// that it carries an entire browser engine so the program can draw a window.
// Discord refuses anything over 10 MB, and the workaround - "install Microsoft's
// WebView2 first" - is precisely the extra step that means nobody ever runs it.
//
// So the fix is not a smaller zip. It is to stop bundling a browser, because
// every Windows machine already has one. When WebView2 is present the window
// looks exactly as it does today; when it is absent the same interface opens as
// a tab in whatever browser they already use. One 11 MB file either way, and
// nothing for the recipient to decide, install, or understand.
//
// # WHY THE ACTIONS MOVED OUT OF ui.go TO MAKE THAT POSSIBLE
//
// Two transports means two chances to implement "send my data" - and hard rule
// 14 exists because this project has had five artefacts with two writers, every
// one of which drifted. A second copy of `sendData` would be worse than most:
// the two would be identical on the day they were written, and the day they
// stopped being identical is the day somebody's screenshots go somewhere they
// did not agree to.
//
// So there is one map. The webview binds thin wrappers to it. The HTTP server
// dispatches to it. Neither contains any logic of its own, and a new action
// added here appears in both without anybody remembering to do it twice.
//
// # THE SIGNATURE IS UNIFORM ON PURPOSE
//
// Every action takes a raw JSON argument and returns something JSON-encodable.
// The webview bindings are typed and the HTTP layer is not, so a uniform shape
// is what lets one definition serve both. Actions that take nothing ignore the
// argument; actions that take a bool decode it and default to false, because a
// missing argument must never be read as "yes, include my screenshots".

import (
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"time"
)

// uiCall is one action. The argument is whatever the page sent, unparsed.
type uiCall func(arg json.RawMessage) (interface{}, error)

// uiActionCtx is everything the actions need from the running program. Passed
// as a struct rather than as nine parameters so that adding a dependency does
// not mean editing every call site.
type uiActionCtx struct {
	Deps           uiDeps
	Auto           autoDeps
	ExeDir         string
	OutDir         string
	SendURL        string
	SendKey        string
	ClearAfterSend bool
	Logf           func(string, ...interface{})
}

// argBool decodes a boolean argument, FAILING TO false.
//
// This is the only place in the program where a decode failure has a safe
// direction and an unsafe one. Both callers of a bool action ask the same
// question - "include the screenshots?" - and a malformed or absent argument
// must answer no. Reading a parse failure as yes would send frames that can
// show handles, party lists and chat, on the strength of a bug.
func argBool(arg json.RawMessage) bool {
	if len(arg) == 0 {
		return false
	}
	var b bool
	if err := json.Unmarshal(arg, &b); err != nil {
		return false
	}
	return b
}

func buildUIActions(c uiActionCtx) map[string]uiCall {
	logf := c.Logf
	if logf == nil {
		logf = func(string, ...interface{}) {}
	}

	return map[string]uiCall{

		// state() is called by the page on a timer. Every call rebuilds from
		// reality; nothing is cached between calls (§9).
		"state": func(json.RawMessage) (interface{}, error) {
			b, _ := json.Marshal(buildUIState(c.Deps))
			return string(b), nil
		},

		// CAPTURE NOW. §8's one button plus this: a button cannot silently fail
		// to register, which the hotkey demonstrably can.
		"captureNow": func(json.RawMessage) (interface{}, error) {
			if err := c.Auto.gameAlive(); err != nil {
				return "Star Citizen isn't running, so there's nothing to photograph yet.", nil
			}
			p, err := c.Auto.capture(Trigger{Kind: "hotkey", Note: "button"})
			if err != nil {
				logf("button capture FAILED: %v", err)
				return "That didn't work. The details are in the log file.", nil
			}
			logf("captured %s  <- button (manual)", filepath.Base(p))
			return "Saved " + filepath.Base(p), nil
		},

		// countData() tells the page how many rows and how many SCREENSHOTS
		// exist, so it can say what is about to leave BEFORE anything is
		// written. A person should not find out what they sent by opening the
		// zip afterwards.
		"countData": func(json.RawMessage) (interface{}, error) {
			st, err := loadMineStore(c.OutDir)
			n := 0
			// THE ERROR IS REPORTED, NOT SWALLOWED.
			//
			// This used to return 0 for both "no data yet" and "the store is
			// unreadable", which are the same number and completely different
			// situations. The second one means the export is about to be built
			// from nothing while the page cheerfully says "0 rows" - the
			// silent-success shape, in the one place where the consequence is
			// somebody believing they sent their data when they sent an empty
			// file.
			problem := ""
			if err == nil {
				n = len(st.Txns)
			} else if !os.IsNotExist(err) {
				problem = "the collected data could not be read: " + err.Error()
				logf("countData: %v", err)
			}
			caps := listCaptures(c.OutDir)
			b, _ := json.Marshal(map[string]interface{}{
				"rows":   n,
				"frames": len(caps.OK),
				// Frames that cannot prove they photographed the game are
				// counted separately so the window can say so before anything
				// is written.
				"held_back": len(caps.Quaranti),
				"problem":   problem,
			})
			return string(b), nil
		},

		// SENDING INCLUDES THE PICTURES, and that is decided here.
		//
		// This used to read the operator's per-send choice off the page. It no
		// longer does, because consent v3 states "Screenshots ARE uploaded when
		// you send" - the promise now says what happens, so the code must do
		// it. Version 2 was worded around a tick box and that is exactly the
		// drift the version number exists to catch.
		//
		// It is fixed HERE rather than by passing true from the page because
		// the page is not the only caller: ui_browser binds the same name over
		// a socket. A promise enforced only in the UI is enforced nowhere.
		//
		// The parameter stays on BuildExport - the selftests exercise both
		// paths, and which value was used is still recorded in the zip README.
		"sendData": func(arg json.RawMessage) (interface{}, error) {
			// arg is ignored on purpose; see above. It stays in the signature
			// so an older page that still sends a boolean does not error.
			res, err := BuildExport(c.ExeDir, c.OutDir, c.OutDir, true, logf)
			if err != nil {
				logf("export FAILED: %v", err)
				return "That didn't work: " + err.Error(), nil
			}

			// One click packages AND sends. With no send address configured
			// this does nothing at all and the zip is simply on disk, which is
			// exactly how it behaved before sending existed.
			if strings.TrimSpace(c.SendURL) != "" {
				up, uerr := SendExport(res, c.OutDir, c.SendURL, c.SendKey, res.InstallID, c.ClearAfterSend, logf)
				if uerr != nil {
					logf("send FAILED: %v", uerr)
					revealFile(res.Path)
					return "Packaged, but sending failed: " + uerr.Error() +
						" Your data is untouched and the file is in the folder.", nil
				}
				if up.Sent {
					return up.Note, nil
				}
			}
			revealFile(res.Path)
			return "Saved " + filepath.Base(res.Path) + " — " + res.Note, nil
		},

		// The CHECK is automatic, the INSTALL is a click. A stale build nobody
		// knows is stale is the defect that cost a full day on 2026-08-07; a
		// program that replaces itself unasked is a different problem entirely.
		"checkUpdate": func(json.RawMessage) (interface{}, error) {
			b, _ := json.Marshal(CheckForUpdate(logf))
			return string(b), nil
		},
		"applyUpdate": func(json.RawMessage) (interface{}, error) {
			msg, err := ApplyUpdate(c.ExeDir, logf)
			if err != nil {
				logf("update FAILED: %v", err)
				return "Update failed: " + err.Error(), nil
			}
			return msg, nil
		},

		// MASTER ONLY. A crew build must not be able to make more crew builds.
		"canPackage": func(json.RawMessage) (interface{}, error) {
			return packageIsAvailable(), nil
		},
		"makePackage": func(json.RawMessage) (interface{}, error) {
			if !packageIsAvailable() {
				return "This build cannot make packages.", nil
			}
			// No argument any more. There is one package - see the note on
			// BuildCrewPackage. It takes a second, not minutes, now that there
			// is no 500 MB runtime to copy, but it stays async so a slow disk
			// cannot make the window look hung.
			go func() {
				res, err := BuildCrewPackage(c.ExeDir, logf)
				if err != nil {
					logf("package FAILED: %v", err)
					uiNotify("Citizen Collector - package FAILED, see the log")
					return
				}
				uiNotify(fmt.Sprintf("Citizen Collector - package ready (%d MB)",
					res.Bytes/(1024*1024)))
				revealFile(res.Path)
			}()
			return "Making the copy. The folder will open when it is done.", nil
		},

		// RESTART, so "close it and open it again" stops being a step.
		//
		// ApplyUpdate puts the new binary in place, but THIS process is still
		// running the old code and cannot become the new one - Windows has the
		// image mapped. The only honest move is to start the new file and let
		// this one go.
		//
		// It is a separate button, pressed deliberately, and never automatic. A
		// program that vanishes and reappears on its own while somebody is
		// mid-session is indistinguishable from a crash.
		"restartNow": func(json.RawMessage) (interface{}, error) {
			exe, err := os.Executable()
			if err != nil {
				return "Could not work out which program to start again: " + err.Error(), nil
			}
			cmd := exec.Command(exe)
			cmd.Dir = c.ExeDir
			if err := cmd.Start(); err != nil {
				return "Could not start the new version: " + err.Error() +
					" Close this and open collector.exe yourself.", nil
			}
			logf("restart: started %s, this process is exiting", exe)
			// A beat, so the child is past its single-instance check before this
			// one releases the lock. Without it the new process can see the old
			// one still holding the marker and refuse to start - which would
			// leave the person with nothing running at all, which is far worse
			// than a second of delay.
			go func() {
				time.Sleep(1500 * time.Millisecond)
				os.Exit(0)
			}()
			return "Starting the new version…", nil
		},

		"openCaptures": func(json.RawMessage) (interface{}, error) {
			_ = os.MkdirAll(c.OutDir, 0o755)
			_ = exec.Command("explorer.exe", c.OutDir).Start()
			return "", nil
		},
	}
}

// revealFile opens Explorer with the file selected.
//
// One definition because the "/select," argument is easy to get subtly wrong -
// it must be a single argument with the comma attached and NO space before the
// path, and the version with a space silently opens the user's Documents folder
// instead. That is a wrong-looking-right failure, so it lives in one place.
// revealFile is a package-level hook for the same reason uiNotify below is
// one: the selftest has to be able to drive the real sendData action, and the
// real sendData action ends by opening Explorer. A check that pops a window on
// somebody's desktop every time the suite runs would be turned off, and a check
// that is turned off is not a check. Production behaviour is unchanged.
var revealFile = func(path string) {
	_ = exec.Command("explorer.exe", "/select,"+path).Start()
}

// uiNotify puts a line where somebody will see it without opening a file.
//
// Set by RunUI to the tray tooltip. A package-level hook rather than a field on
// the context because the actions are built before the tray is guaranteed to
// have succeeded, and a tray that failed to register must not take the actions
// down with it - it stays a no-op and everything else works.
var uiNotify = func(string) {}
