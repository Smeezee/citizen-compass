package main

// ops-mail-wake — watch correspondence/open/architecture for NEW .md letters,
// write a wake marker, and POST the Engineering webhook (credit-cheap vs blind poll).
//
// Anti-runaway: debounce, .md only, skip temps, max wakes/hour, idempotent path set.
// Owner pastes webhook URL into ops-mail-wake-settings.json (gitignored). Hard rule:
// registering a Windows Scheduled Task is Owner-only; this tool can -WhatIf / dry-run.

import (
	"bytes"
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"sync"
	"time"

	"github.com/fsnotify/fsnotify"
)

type settings struct {
	ProjectRoot string `json:"project_root"`
	WatchRel    string `json:"watch_rel"`
	WebhookURL  string `json:"webhook_url"`
	MaxPerHour  int    `json:"max_per_hour"`
	DebounceMs  int    `json:"debounce_ms"`
}

type wakePayload struct {
	Event     string `json:"event"`
	Path      string `json:"path"`
	RelPath   string `json:"rel_path"`
	At        string `json:"at"`
	Source    string `json:"source"`
}

type stateFile struct {
	FiredPaths map[string]string `json:"fired_paths"` // path -> RFC3339
	HourBucket string            `json:"hour_bucket"`
	HourCount  int               `json:"hour_count"`
}

func main() {
	check := flag.Bool("check", false, "validate settings + watch dir, exit")
	once := flag.String("once", "", "fire once for an existing path (test), then exit")
	dry := flag.Bool("dry-run", false, "log wake without POST / without writing marker")
	settingsPath := flag.String("settings", "ops-mail-wake-settings.json", "settings file")
	flag.Parse()

	cfg, err := loadSettings(*settingsPath)
	if err != nil {
		log.Fatalf("settings: %v", err)
	}
	if cfg.WatchRel == "" {
		cfg.WatchRel = `correspondence\open\engineering`
	}
	if cfg.MaxPerHour <= 0 {
		cfg.MaxPerHour = 6
	}
	if cfg.DebounceMs <= 0 {
		cfg.DebounceMs = 1500
	}
	root := cfg.ProjectRoot
	if root == "" {
		wd, _ := os.Getwd()
		// if started from ops-mail-wake/, parent is project root
		if filepath.Base(wd) == "ops-mail-wake" {
			root = filepath.Dir(wd)
		} else {
			root = wd
		}
	}
	watchDir := filepath.Join(root, cfg.WatchRel)
	statePath := filepath.Join(root, `correspondence\_ops_state\mail_wake_state.json`)
	markerPath := filepath.Join(root, `correspondence\_ops_state\wake.json`)

	if _, err := os.Stat(watchDir); err != nil {
		log.Fatalf("watch dir missing: %s (%v)", watchDir, err)
	}

	if *check {
		fmt.Printf("ok watch=%s webhook_set=%v max_per_hour=%d\n", watchDir, cfg.WebhookURL != "", cfg.MaxPerHour)
		os.Exit(0)
	}

	st, err := loadState(statePath)
	if err != nil {
		log.Fatalf("state: %v", err)
	}

	fire := func(abs string) {
		if err := handleNew(abs, root, cfg, st, statePath, markerPath, *dry); err != nil {
			log.Printf("wake failed: %v", err)
		}
	}

	if *once != "" {
		p := *once
		if !filepath.IsAbs(p) {
			p = filepath.Join(watchDir, p)
		}
		fire(p)
		return
	}

	w, err := fsnotify.NewWatcher()
	if err != nil {
		log.Fatal(err)
	}
	defer w.Close()
	if err := w.Add(watchDir); err != nil {
		log.Fatal(err)
	}
	log.Printf("watching %s (webhook_set=%v dry=%v)", watchDir, cfg.WebhookURL != "", *dry)

	var mu sync.Mutex
	pending := map[string]*time.Timer{}
	debounce := time.Duration(cfg.DebounceMs) * time.Millisecond

	for {
		select {
		case ev, ok := <-w.Events:
			if !ok {
				return
			}
			if ev.Op&(fsnotify.Create|fsnotify.Write|fsnotify.Rename) == 0 {
				continue
			}
			name := ev.Name
			if !interesting(name) {
				continue
			}
			mu.Lock()
			if t, ok := pending[name]; ok {
				t.Stop()
			}
			n := name
			pending[n] = time.AfterFunc(debounce, func() {
				mu.Lock()
				delete(pending, n)
				mu.Unlock()
				fire(n)
			})
			mu.Unlock()
		case err, ok := <-w.Errors:
			if !ok {
				return
			}
			log.Printf("watch err: %v", err)
		}
	}
}

func interesting(path string) bool {
	base := filepath.Base(path)
	if strings.HasPrefix(base, ".") || strings.HasPrefix(base, "~") || strings.HasSuffix(base, ".tmp") {
		return false
	}
	return strings.EqualFold(filepath.Ext(base), ".md")
}

func handleNew(abs, root string, cfg settings, st *stateFile, statePath, markerPath string, dry bool) error {
	abs = filepath.Clean(abs)
	if _, err := os.Stat(abs); err != nil {
		return nil // vanished (rename/move)
	}
	rel, _ := filepath.Rel(root, abs)
	rel = filepath.ToSlash(rel)

	bucket := time.Now().UTC().Format("2006-01-02T15")
	if st.HourBucket != bucket {
		st.HourBucket = bucket
		st.HourCount = 0
	}
	if st.FiredPaths == nil {
		st.FiredPaths = map[string]string{}
	}
	if _, seen := st.FiredPaths[rel]; seen {
		log.Printf("skip already-fired %s", rel)
		return nil
	}
	if st.HourCount >= cfg.MaxPerHour {
		return fmt.Errorf("cap: %d wakes this hour (anti-runaway)", cfg.MaxPerHour)
	}

	payload := wakePayload{
		Event:   "engineering_mail_new",
		Path:    abs,
		RelPath: rel,
		At:      time.Now().UTC().Format(time.RFC3339),
		Source:  "ops-mail-wake",
	}
	body, _ := json.Marshal(payload)

	if dry {
		log.Printf("dry-run wake %s", rel)
		return nil
	}

	if err := os.MkdirAll(filepath.Dir(markerPath), 0o755); err != nil {
		return err
	}
	if err := os.WriteFile(markerPath, body, 0o644); err != nil {
		return err
	}

	if cfg.WebhookURL == "" {
		log.Printf("marker written; webhook_url empty — Owner paste URL into settings")
	} else {
		req, err := http.NewRequest(http.MethodPost, cfg.WebhookURL, bytes.NewReader(body))
		if err != nil {
			return err
		}
		req.Header.Set("Content-Type", "application/json")
		resp, err := http.DefaultClient.Do(req)
		if err != nil {
			return err
		}
		defer resp.Body.Close()
		b, _ := io.ReadAll(io.LimitReader(resp.Body, 2048))
		if resp.StatusCode < 200 || resp.StatusCode >= 300 {
			return fmt.Errorf("webhook HTTP %d: %s", resp.StatusCode, strings.TrimSpace(string(b)))
		}
		log.Printf("webhook ok %s", rel)
	}

	st.FiredPaths[rel] = payload.At
	st.HourCount++
	return saveState(statePath, st)
}

func loadSettings(path string) (settings, error) {
	var s settings
	b, err := os.ReadFile(path)
	if err != nil {
		// try next to exe / cwd variants
		alt := filepath.Join(filepath.Dir(os.Args[0]), path)
		b, err = os.ReadFile(alt)
		if err != nil {
			return s, fmt.Errorf("read %s: %w (copy from ops-mail-wake-settings.example.json)", path, err)
		}
	}
	if err := json.Unmarshal(b, &s); err != nil {
		return s, err
	}
	return s, nil
}

func loadState(path string) (*stateFile, error) {
	st := &stateFile{FiredPaths: map[string]string{}}
	b, err := os.ReadFile(path)
	if err != nil {
		if os.IsNotExist(err) {
			return st, nil
		}
		return nil, err
	}
	if err := json.Unmarshal(b, st); err != nil {
		return nil, err
	}
	if st.FiredPaths == nil {
		st.FiredPaths = map[string]string{}
	}
	return st, nil
}

func saveState(path string, st *stateFile) error {
	if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		return err
	}
	b, err := json.MarshalIndent(st, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(path, b, 0o644)
}
