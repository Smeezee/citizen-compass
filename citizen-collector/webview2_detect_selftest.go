package main

// webview2_detect_selftest.go - can the fallback decision actually say NO?
//
// WHY THIS FILE EXISTS
//
// Every BROWSER UI check in ui_browser_selftest.go is downstream of one
// question: webview2Available(). If that function can only ever return true,
// the browser fallback is unreachable code and every one of those checks still
// passes - they would be testing a page that is never served. The whole group
// would report green while the feature it covers had never run once.
//
// That is this project's SILENT SUCCESS shape at the level of a decision rather
// than an assertion, and until now webview2Available had no test at all, in
// either direction. It is also the one path the handoff records as having zero
// real-world evidence, because both machines it has run on have the runtime
// installed - so on those machines the answer is always yes and the negative
// branch is never taken.
//
// The detector reads only the filesystem and the environment, so both answers
// can be produced on demand here without needing a second machine.

import (
	"fmt"
	"os"
	"path/filepath"
)

// withEnv sets environment variables for the duration of fn and restores what
// was there before - including restoring "unset" as unset, which a plain
// Setenv("") does not do.
func withEnv(kv map[string]string, fn func()) {
	type prev struct {
		val string
		ok  bool
	}
	saved := make(map[string]prev, len(kv))
	for k, v := range kv {
		old, ok := os.LookupEnv(k)
		saved[k] = prev{old, ok}
		if v == "" {
			_ = os.Unsetenv(k)
		} else {
			_ = os.Setenv(k, v)
		}
	}
	defer func() {
		for k, p := range saved {
			if p.ok {
				_ = os.Setenv(k, p.val)
			} else {
				_ = os.Unsetenv(k)
			}
		}
	}()
	fn()
}

func runWebView2DetectSelftest(check func(name string, ok bool, detail string)) {
	dir, err := os.MkdirTemp("", "cc-wv2-")
	if err != nil {
		check("WEBVIEW2 DETECT: testable", false, fmt.Sprintf("no temp dir: %v", err))
		return
	}
	defer os.RemoveAll(dir)

	fail := func(e error) {
		check("WEBVIEW2 DETECT: testable", false, e.Error())
	}

	// An exe directory with no webview2-runtime beside it, so the bundled
	// branch cannot be what answers any of these.
	exeDir := filepath.Join(dir, "exe")
	if err := os.MkdirAll(exeDir, 0o755); err != nil {
		fail(err)
		return
	}

	// Every search root redirected into empty temp space. Without this the test
	// would read the real machine, where the answer is always yes and nothing
	// below could fail.
	empty := filepath.Join(dir, "empty")
	if err := os.MkdirAll(empty, 0o755); err != nil {
		fail(err)
		return
	}
	blank := map[string]string{
		"ProgramFiles(x86)":                  empty,
		"ProgramFiles":                       empty,
		"LOCALAPPDATA":                       empty,
		"WEBVIEW2_BROWSER_EXECUTABLE_FOLDER": "",
	}

	// THE CHECK THAT MATTERS MOST. If this cannot produce false, the browser
	// fallback is unreachable and the entire BROWSER UI group is vacuous.
	withEnv(blank, func() {
		check("WEBVIEW2 DETECT: says NO when no runtime exists anywhere",
			!webview2Available(exeDir),
			"nothing on disk and nothing in the environment - the fallback must be reachable")
	})

	// The documented wrong-direction failure, called out by name in
	// webview2_detect.go: an uninstall leaves the version directory behind with
	// the binaries removed. A directory-only test reports a runtime that will
	// not load, and the person gets a dead window instead of a browser tab.
	leftoverRoot := filepath.Join(dir, "leftover")
	if err := os.MkdirAll(filepath.Join(leftoverRoot, "Microsoft", "EdgeWebView",
		"Application", "121.0.2277.128"), 0o755); err != nil {
		fail(err)
		return
	}
	stale := map[string]string{
		"ProgramFiles(x86)":                  leftoverRoot,
		"ProgramFiles":                       empty,
		"LOCALAPPDATA":                       empty,
		"WEBVIEW2_BROWSER_EXECUTABLE_FOLDER": "",
	}
	withEnv(stale, func() {
		check("WEBVIEW2 DETECT: an uninstall leftover is NOT counted as installed",
			!webview2Available(exeDir),
			"the version folder exists but msedgewebview2.exe does not - a directory test would wrongly say yes")
	})

	// POSITIVE CONTROL. Without this, the two checks above would pass just as
	// happily if the function were `return false`, and a detector stuck on
	// false sends every machine to the browser including the ones with a
	// perfectly good runtime.
	realRoot := filepath.Join(dir, "real")
	realVer := filepath.Join(realRoot, "Microsoft", "EdgeWebView", "Application", "121.0.2277.128")
	if err := os.MkdirAll(realVer, 0o755); err != nil {
		fail(err)
		return
	}
	if err := os.WriteFile(filepath.Join(realVer, "msedgewebview2.exe"),
		[]byte("stand-in for the engine"), 0o644); err != nil {
		fail(err)
		return
	}
	present := map[string]string{
		"ProgramFiles(x86)":                  realRoot,
		"ProgramFiles":                       empty,
		"LOCALAPPDATA":                       empty,
		"WEBVIEW2_BROWSER_EXECUTABLE_FOLDER": "",
	}
	withEnv(present, func() {
		check("WEBVIEW2 DETECT: POSITIVE CONTROL - a real engine IS found",
			webview2Available(exeDir),
			"the detector must not be stuck on no, or every machine gets the browser")
	})

	// Per-user installs are the common shape on a locked-down machine, and they
	// land in LOCALAPPDATA rather than in either Program Files.
	userRoot := filepath.Join(dir, "user")
	userVer := filepath.Join(userRoot, "Microsoft", "EdgeWebView", "Application", "120.0.1.2")
	if err := os.MkdirAll(userVer, 0o755); err != nil {
		fail(err)
		return
	}
	if err := os.WriteFile(filepath.Join(userVer, "msedgewebview2.exe"), []byte("x"), 0o644); err != nil {
		fail(err)
		return
	}
	withEnv(map[string]string{
		"ProgramFiles(x86)":                  empty,
		"ProgramFiles":                       empty,
		"LOCALAPPDATA":                       userRoot,
		"WEBVIEW2_BROWSER_EXECUTABLE_FOLDER": "",
	}, func() {
		check("WEBVIEW2 DETECT: a per-user install is found too",
			webview2Available(exeDir),
			"LOCALAPPDATA is where a non-admin install lands")
	})

	// A non-version folder such as "Installer" must be skipped even when it
	// contains something with the engine's name, because it is not a runtime.
	instRoot := filepath.Join(dir, "instonly")
	instDir := filepath.Join(instRoot, "Microsoft", "EdgeWebView", "Application", "Installer")
	if err := os.MkdirAll(instDir, 0o755); err != nil {
		fail(err)
		return
	}
	if err := os.WriteFile(filepath.Join(instDir, "msedgewebview2.exe"), []byte("x"), 0o644); err != nil {
		fail(err)
		return
	}
	withEnv(map[string]string{
		"ProgramFiles(x86)":                  instRoot,
		"ProgramFiles":                       empty,
		"LOCALAPPDATA":                       empty,
		"WEBVIEW2_BROWSER_EXECUTABLE_FOLDER": "",
	}, func() {
		check("WEBVIEW2 DETECT: a non-version folder is not mistaken for a runtime",
			!webview2Available(exeDir),
			"only folders whose name looks like a version count")
	})

	// The pinned-folder override, which is what the relaunch sets. Both
	// directions, because a pin honoured while empty would send a machine at a
	// runtime that is not there.
	pinned := filepath.Join(dir, "pinned")
	if err := os.MkdirAll(pinned, 0o755); err != nil {
		fail(err)
		return
	}
	pinnedEnv := map[string]string{
		"ProgramFiles(x86)":                  empty,
		"ProgramFiles":                       empty,
		"LOCALAPPDATA":                       empty,
		"WEBVIEW2_BROWSER_EXECUTABLE_FOLDER": pinned,
	}
	withEnv(pinnedEnv, func() {
		check("WEBVIEW2 DETECT: an EMPTY pinned folder is refused",
			!webview2Available(exeDir),
			"the pin names a folder with no engine in it, so it is not an answer")
	})
	if err := os.WriteFile(filepath.Join(pinned, "msedgewebview2.exe"), []byte("x"), 0o644); err != nil {
		fail(err)
		return
	}
	withEnv(pinnedEnv, func() {
		check("WEBVIEW2 DETECT: a pinned folder WITH the engine is accepted",
			webview2Available(exeDir),
			"the relaunch sets this and it must win")
	})

	// THE DETECTOR MUST ACTUALLY CHANGE ITS ANSWER. Each check above is a
	// single reading; this states the difference, so a function ignoring its
	// inputs could not satisfy the pair no matter which constant it returned.
	var no, yes bool
	withEnv(blank, func() { no = webview2Available(exeDir) })
	withEnv(present, func() { yes = webview2Available(exeDir) })
	check("WEBVIEW2 DETECT: the same exeDir yields BOTH answers",
		!no && yes,
		fmt.Sprintf("empty machine -> %v, machine with a runtime -> %v", no, yes))
}
