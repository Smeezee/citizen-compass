// Citizen Compass — Inbox Watcher (Go port)
//
// Recursive replacement for inbox_watcher.py's core file-routing behavior.
// Watches inbox/ (and every subdirectory under it, at any depth) and files
// recognized types to their correct project location, exactly as the Python
// version did for: .py scripts, .md docs (handoff/update/plain), .glb/.blend
// models, and hardpoint/viewer/ship-spec JSON. Unrecognized files always go
// to _needs_review/ — nothing is ever silently discarded.
//
// Deliberately NOT ported in this first migration step (per instruction):
// .zip extraction, image/OCR handling, ccpp.py health-score refresh, and the
// generate_handoff.py trigger. Those still live only in the Python watcher.
package main

import (
	"flag"
	"io/fs"
	"log"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"sync"
	"time"

	"github.com/fsnotify/fsnotify"

	"citizencompass/pkg/pipelinelog"
)

var (
	projectRoot   string
	inboxDir      string
	needsReviewDir string
	docsDir       string
	shipsDir      string
	modelsUnsortedDir string
	handoffArchiveDir string
	protectedFoldersFile string
	ccppFile      string
	imageArchiveDir string
)

const (
	stableCheckInterval = 1 * time.Second
	stableChecksRequired = 2
)

// protectedInboxSubdirs lists folder names directly under inbox/ that must
// NEVER be watched or auto-processed. Loaded at startup from
// protected_folders.txt at the project root -- not hardcoded, so folders can
// be added or removed there without touching source. Checked for both the
// startup sweep and the live recursive watch, so neither the folder nor
// anything nested inside it at any depth is ever touched.
var protectedInboxSubdirs = map[string]bool{}

// loadProtectedFolders reads protected_folders.txt: one folder name per
// line, blank lines and lines starting with # ignored. Missing file just
// means an empty protected list (logged clearly, never silently assumed).
func loadProtectedFolders(path string) map[string]bool {
	result := map[string]bool{}
	data, err := os.ReadFile(path)
	if err != nil {
		logMsg("⚠ could not read %s (%v) — no folders are protected from auto-processing", path, err)
		return result
	}
	for _, line := range strings.Split(string(data), "\n") {
		line = strings.TrimSpace(line)
		line = strings.TrimRight(line, "\r")
		if line == "" || strings.HasPrefix(line, "#") {
			continue
		}
		result[line] = true
	}
	return result
}

// isProtected reports whether path is one of the protected directories
// (or the protected directory itself) or lives anywhere underneath one.
func isProtected(path string) bool {
	rel, err := filepath.Rel(inboxDir, path)
	if err != nil {
		return false
	}
	if rel == "." || strings.HasPrefix(rel, "..") {
		return false
	}
	parts := strings.Split(filepath.ToSlash(rel), "/")
	return protectedInboxSubdirs[parts[0]]
}

// logger is this tool's handle on the shared logs/<tool-name>.log
// convention (pkg/pipelinelog) -- the standardized location/format used by
// every Citizen Compass tool going forward, not just this one.
var logger *pipelinelog.Logger

func logMsg(format string, args ...interface{}) {
	logger.Logf(format, args...)
}

func main() {
	once := flag.Bool("once", false, "Run health-score refresh + LATEST_HANDOFF.md regeneration a single time and exit, without starting the file watcher")
	flag.Parse()

	exePath, err := os.Executable()
	if err != nil {
		log.Fatalf("could not determine executable path: %v", err)
	}
	projectRoot = filepath.Dir(exePath)

	inboxDir = filepath.Join(projectRoot, "inbox")
	needsReviewDir = filepath.Join(projectRoot, "_needs_review")
	docsDir = filepath.Join(projectRoot, "docs")
	shipsDir = filepath.Join(projectRoot, "tests", "testing-site", "ships")
	modelsUnsortedDir = filepath.Join(projectRoot, "models", "_unsorted")
	handoffArchiveDir = filepath.Join(projectRoot, "docs", "handoff_archive")
	protectedFoldersFile = filepath.Join(projectRoot, "protected_folders.txt")
	zipArchiveDir = filepath.Join(projectRoot, "_zip_archive")
	ccppFile = filepath.Join(projectRoot, "citizen-compass.ccpp")
	imageArchiveDir = filepath.Join(handoffArchiveDir, "images")
	initHandoffPaths()

	logger = pipelinelog.New(projectRoot, "inbox_watcher")

	os.MkdirAll(inboxDir, 0755)

	if *once {
		logMsg("Running one-shot regeneration (--once): health-score refresh + LATEST_HANDOFF.md, no watcher started")
		rescanAndScore()
		regenerateHandoff()
		return
	}

	logMsg("Watcher started (Go). Watching: %s", inboxDir)

	protectedInboxSubdirs = loadProtectedFolders(protectedFoldersFile)
	if len(protectedInboxSubdirs) > 0 {
		var names []string
		for name := range protectedInboxSubdirs {
			names = append(names, name)
		}
		sort.Strings(names)
		logMsg("Protected folders loaded from %s: %s", protectedFoldersFile, strings.Join(names, ", "))
	}

	watcher, err := fsnotify.NewWatcher()
	if err != nil {
		logMsg("FATAL: could not create watcher: %v", err)
		os.Exit(1)
	}
	defer watcher.Close()

	watchedDirs := make(map[string]bool)
	var watchedMu sync.Mutex

	addWatchRecursive := func(root string) {
		filepath.WalkDir(root, func(path string, d fs.DirEntry, err error) error {
			if err != nil {
				return nil
			}
			if d.IsDir() {
				if isProtected(path) {
					return fs.SkipDir
				}
				watchedMu.Lock()
				already := watchedDirs[path]
				if !already {
					watchedDirs[path] = true
				}
				watchedMu.Unlock()
				if !already {
					if werr := watcher.Add(path); werr != nil {
						logMsg("could not watch %s: %v", path, werr)
					}
				}
			}
			return nil
		})
	}

	// Watch inbox/ and every subdirectory that already exists, so nested
	// folders dropped before startup are covered too, not just top-level.
	addWatchRecursive(inboxDir)

	// Process anything already sitting in inbox/ before we started watching,
	// recursively -- unlike the original Python watcher, which only scanned
	// the top level on startup.
	var preexisting []string
	filepath.WalkDir(inboxDir, func(path string, d fs.DirEntry, err error) error {
		if err != nil {
			return nil
		}
		if d.IsDir() {
			if isProtected(path) {
				logMsg("Skipping protected folder (never auto-processed): %s", path)
				return fs.SkipDir
			}
			return nil
		}
		preexisting = append(preexisting, path)
		return nil
	})
	sort.Strings(preexisting)
	for _, p := range preexisting {
		processPath(p)
	}

	logMsg("Now watching for new files. Leave this running.")

	go func() {
		for {
			select {
			case event, ok := <-watcher.Events:
				if !ok {
					return
				}
				if event.Op&(fsnotify.Create|fsnotify.Rename) == 0 {
					continue
				}
				handleFsEvent(event.Name, watcher, &watchedMu, watchedDirs, addWatchRecursive)
			case err, ok := <-watcher.Errors:
				if !ok {
					return
				}
				logMsg("watcher error: %v", err)
			}
		}
	}()

	// Screenshot retention sweep: once shortly after startup, then every 24h.
	go func() {
		for {
			cleanupAgedConfirmedScreenshots()
			time.Sleep(24 * time.Hour)
		}
	}()

	select {}
}

// handleFsEvent reacts to a create/rename event for a path inside a watched
// directory. If it's a new directory, it starts watching it (and recurses
// into anything already inside it, in case files raced in before we could
// register the watch). If it's a file, it's routed once stable.
func handleFsEvent(path string, watcher *fsnotify.Watcher, watchedMu *sync.Mutex, watchedDirs map[string]bool, addWatchRecursive func(string)) {
	info, err := os.Stat(path)
	if err != nil {
		// Already gone (e.g. a rename's source side) -- nothing to do.
		return
	}

	if info.IsDir() {
		if isProtected(path) {
			logMsg("Skipping protected folder (never auto-processed): %s", path)
			return
		}

		watchedMu.Lock()
		alreadyWatched := watchedDirs[path]
		watchedDirs[path] = true
		watchedMu.Unlock()
		if !alreadyWatched {
			if werr := watcher.Add(path); werr != nil {
				logMsg("could not watch new folder %s: %v", path, werr)
			}
			logMsg("New folder detected: %s (now watching)", path)
		}
		// Catch anything already inside this folder (a whole folder can be
		// dropped in one move/copy operation, arriving with content already
		// present before we could register a watch on it) and make sure any
		// nested subfolders get watched too.
		var nested []string
		filepath.WalkDir(path, func(p string, d fs.DirEntry, err error) error {
			if err != nil {
				return nil
			}
			if d.IsDir() {
				if isProtected(p) {
					return fs.SkipDir
				}
				addWatchRecursive(p)
				return nil
			}
			nested = append(nested, p)
			return nil
		})
		sort.Strings(nested)
		for _, p := range nested {
			processPath(p)
		}
		return
	}

	processPath(path)
}

func processPath(path string) {
	if !waitUntilStable(path) {
		return
	}
	note, dest, err := classifyAndRoute(path)
	if err != nil {
		logMsg("✗ FAILED processing %s: %v", filepath.Base(path), err)
		return
	}
	logMsg("✓ %s -> %s (%s)", filepath.Base(path), dest, note)

	rescanAndScore()
	regenerateHandoff()
}

// waitUntilStable waits until a file's size stops changing across
// consecutive checks, so a still-copying file is never processed mid-write.
func waitUntilStable(path string) bool {
	lastSize := int64(-1)
	stableCount := 0
	for stableCount < stableChecksRequired {
		info, err := os.Stat(path)
		if err != nil {
			return false
		}
		size := info.Size()
		if size == lastSize {
			stableCount++
		} else {
			stableCount = 0
			lastSize = size
		}
		time.Sleep(stableCheckInterval)
	}
	return true
}

func extLower(path string) string {
	return strings.ToLower(filepath.Ext(path))
}
