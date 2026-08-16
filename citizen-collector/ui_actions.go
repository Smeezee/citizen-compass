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
// So the fix was not a smaller zip. It was to stop bundling a browser.
//
// The first answer used the browser already on the machine - WebView2 if
// present, an ordinary browser tab if not. THAT ANSWER IS ALSO GONE as of
// 2026-08-15: four defects in one day traced to rendering three buttons in a
// browser engine, so the window is now a plain Windows window with no engine
// underneath. One ~12 MB file, and nothing for the recipient to decide, install
// or understand. See window.go.
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

	// SendURL/SendKey are the destination IN EFFECT, which may have come from
	// the feed. LocalURL/LocalKey are what collector-settings.txt actually
	// said, kept because precedence has to be re-decided every time the feed
	// answers - and a machine somebody configured on purpose must never be
	// repointed by a published default.
	SendURL        string
	SendKey        string
	LocalURL       string
	LocalKey       string
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

func buildUIActions(cv uiActionCtx) map[string]uiCall {
	// A POINTER, so the update check can repoint this collector without a
	// restart. Taken once here rather than threaded through every action.
	c := &cv
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

			// One click packages AND sends - when there is anywhere to send.
			//
			// THE SAME CORE THE -send FLAG AND THE TRAY MENU USE. Three doors,
			// one implementation: a second copy of "package and send" would
			// drift, and the drift would show up as one door clearing somebody's
			// pictures and another not.
			if strings.TrimSpace(c.SendURL) != "" {
				note, serr := SendNow(c.ExeDir, c.OutDir, c.SendURL, c.SendKey, c.ClearAfterSend, logf)
				if serr != nil {
					logf("send FAILED: %v", serr)
					revealFile(res.Path)
					return serr.Error() + ".", nil
				}
				return note, nil
			}
			revealFile(res.Path)

			// §3: A LOCAL-ONLY ZIP MUST NOT READ AS "SENT".
			//
			// This used to return "Saved <file>", which is what a successful
			// send also looks like from across the room. Sleven's wife pressed
			// SEND, got a 27 MB zip and nothing else, and read a correctly
			// working program as broken. Name the file, say it stayed here, say
			// why.
			if strings.TrimSpace(c.SendURL) == "" {
				return LocalOnlyResult(filepath.Base(res.Path)), nil
			}
			return "Saved " + filepath.Base(res.Path) + " — " + res.Note, nil
		},

		// The CHECK is automatic, the INSTALL is a click. A stale build nobody
		// knows is stale is the defect that cost a full day on 2026-08-07; a
		// program that replaces itself unasked is a different problem entirely.
		// THE PAGE SAYING HELLO. See ui.go's bridge deadline.
		//
		// In the webview this name is ALSO bound directly, because there the
		// hello is the only evidence the bridge works. Over the browser
		// transport the request arriving is itself the proof, so this only has
		// to exist and succeed.
		"uiReady": func(json.RawMessage) (interface{}, error) {
			return "", nil
		},

		"checkUpdate": func(json.RawMessage) (interface{}, error) {
			st := CheckForUpdate(logf)

			// THE FEED MAY ALSO SAY WHERE TO SEND.
			//
			// Remembered on disk first, so a machine that is offline next time
			// still knows, and only then applied - with the same precedence as
			// at startup, which means a locally configured machine is left
			// exactly as its owner set it.
			if st.SendURL != "" && st.SendKey != "" {
				if err := SaveCachedDestination(c.ExeDir, st.SendURL, st.SendKey); err != nil {
					logf("destination: could not remember the feed's address (%v) - "+
						"it still applies to this run", err)
				}
			}
			was := c.SendURL
			dest := ResolveDestination(c.LocalURL, c.LocalKey, st.SendURL, st.SendKey,
				LoadCachedDestination(c.ExeDir))
			c.SendURL, c.SendKey = dest.URL, dest.Key

			// SAY WHERE IT CAME FROM, ONCE (§3). A program that starts uploading
			// to an address the operator never entered should announce it rather
			// than let them discover it later.
			if c.SendURL != "" && c.SendURL != was {
				logf("destination: sending to %s - this address came from %s, "+
					"not from anything typed on this computer", c.SendURL, dest.Source)
			}

			b, _ := json.Marshal(st)
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
			// LET GO BEFORE HANDING OVER.
			//
			// The replacement checks the single-instance lock the moment it
			// starts. While this process still holds it, that check says "a
			// collector is already running" - about this one, which is leaving -
			// and the new process exits. The person is left with nothing.
			//
			// The previous version slept 1500ms here "so the child is past its
			// check before this one releases the lock", which is backwards: the
			// child's check happens first either way, and the sleep only held
			// the lock across it. Releasing first is what the comment always
			// meant.
			releaseInstanceLock()

			cmd := exec.Command(exe)
			cmd.Dir = c.ExeDir
			if err := cmd.Start(); err != nil {
				return "Could not start the new version: " + err.Error() +
					" Close this and open collector.exe yourself.", nil
			}
			logf("restart: released the single-instance lock, started %s, this process is exiting", exe)
			// A short beat so the reply reaches the window before the process
			// goes. The lock is already released, so the replacement's check
			// cannot see this one at all.
			go func() {
				time.Sleep(250 * time.Millisecond)
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
