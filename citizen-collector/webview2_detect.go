package main

// webview2_detect.go - is there a browser engine on this machine, or not?
//
// # WHY THIS IS A SEPARATE, CAREFUL QUESTION
//
// Getting it wrong in one direction is invisible and getting it wrong in the
// other is fatal to the whole point of the exercise:
//
//	SAY YES WHEN THE ANSWER IS NO  -> the window fails to create on somebody
//	                                  else's machine, and the program looks
//	                                  broken on first run. That is the exact
//	                                  moment a new person decides not to bother.
//	SAY NO WHEN THE ANSWER IS YES  -> they get a browser tab instead of a
//	                                  window. Slightly less pretty. Everything
//	                                  works.
//
// The costs are wildly asymmetric, so this leans toward NO. A machine that has
// WebView2 but gets the browser has lost nothing that matters; a machine that
// lacks it and gets a dead window has lost the user.
//
// # WHY THE REGISTRY IS NOT USED
//
// The documented check is a version string under EdgeUpdate\Clients\{GUID}. It
// is also routinely left behind by an uninstall, and it has a per-user and a
// per-machine location that disagree. A registry key is a claim that something
// was installed once. The file being on disk is evidence it is there now, and
// this file is about the difference between those two things.
//
// # THE CHECK STILL CANNOT BE TRUSTED COMPLETELY, SO IT IS NOT THE ONLY ONE
//
// A runtime can be present and still fail to load - wrong architecture, a
// half-finished update, group policy. So RunUI treats a nil window as the same
// answer as "not installed" and falls back there too. This function exists to
// avoid the attempt in the common case, not to be the last word.

import (
	"os"
	"path/filepath"
	"strings"
)

// webview2Available reports whether a WebView2 runtime can plausibly be loaded.
func webview2Available(exeDir string) bool {
	// 1. The bundled copy beside the exe always wins if it is real. Same
	//    function the runtime pinning uses, so the two cannot disagree about
	//    what "bundled" means.
	if dir, _ := resolveBundledRuntime(exeDir); dir != "" {
		return true
	}

	// 2. An explicitly pinned folder, which is what the relaunch sets.
	if d := strings.TrimSpace(os.Getenv(runtimeEnvVar)); d != "" {
		if _, err := os.Stat(filepath.Join(d, "msedgewebview2.exe")); err == nil {
			return true
		}
	}

	// 3. The standard install locations. Per-machine first, then per-user -
	//    Evergreen installs to either depending on how it arrived, and a
	//    per-user install is the common shape on a locked-down machine.
	var roots []string
	for _, env := range []string{"ProgramFiles(x86)", "ProgramFiles", "LOCALAPPDATA"} {
		if v := os.Getenv(env); v != "" {
			roots = append(roots, filepath.Join(v, "Microsoft", "EdgeWebView", "Application"))
		}
	}
	for _, root := range roots {
		if hasWebView2Engine(root) {
			return true
		}
	}
	return false
}

// hasWebView2Engine looks for the actual engine under a versioned folder.
//
// The presence of the Application directory is NOT sufficient and checking only
// that is the mistake this looks like it is making. An uninstall commonly
// leaves the directory tree with the binaries removed, so a directory test
// reports a runtime that will not load - the wrong-direction failure this file
// exists to avoid.
func hasWebView2Engine(root string) bool {
	entries, err := os.ReadDir(root)
	if err != nil {
		return false
	}
	for _, e := range entries {
		if !e.IsDir() {
			continue
		}
		// Version folders only. Skip things like "Installer".
		if !strings.ContainsRune(e.Name(), '.') {
			continue
		}
		if _, err := os.Stat(filepath.Join(root, e.Name(), "msedgewebview2.exe")); err == nil {
			return true
		}
	}
	return false
}
