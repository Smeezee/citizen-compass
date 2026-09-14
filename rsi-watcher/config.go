package main

// config.go - everything that can change without a rebuild, in
// rsi-watcher-settings.json next to the exe, written with defaults on first run.
//
// THE ENDPOINTS ARRIVE AS CONFIG, NOT CODE. On 2026-09-13 no DevTracker,
// Comm-Link-list or Patchbot endpoint was recorded anywhere on this machine - the
// old Claude sweep's prompt lived in a claude.ai scheduled task that has since
// been deleted - so discovery was routed to Research. A source with an empty URL
// is NOT CONFIGURED: reported on every run, never polled, and never mistaken for
// a quiet feed. When Research's verified answer lands, it is typed in here.
//
// UNKNOWN KEYS ARE REFUSED. A misspelt key that is silently ignored is a setting
// that says one thing while the program does another.

import (
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"strings"
	"time"
)

const configFileName = "rsi-watcher-settings.json"

// Source is one feed.
type Source struct {
	Name  string `json:"name"`  // devtracker | comm-link | patchbot
	Shelf string `json:"shelf"` // one folder under sc-brain/cig-firehose/

	URL    string `json:"url"`    // "" = NOT CONFIGURED
	Method string `json:"method"` // GET or POST
	Body   string `json:"body"`   // POST body, sent as application/json when set

	// CacheBustParam is a query key given the current unix time on every
	// request. The old watcher saw a DevTracker page whose newest post read
	// "51 minutes ago" across two real hours - a cache, not a quiet feed.
	CacheBustParam string `json:"cache_bust_param"`

	Format string `json:"format"` // "json" or "html"

	// JSON: a dot path to the item array, and the field names inside one item.
	ItemsPath  string `json:"items_path"`
	IDField    string `json:"id_field"`
	TitleField string `json:"title_field"`
	URLField   string `json:"url_field"`
	TimeField  string `json:"time_field"`

	// SuccessField/SuccessValue: when set, the top-level field must equal the
	// value, or the response is a FAILURE however it is dressed. RSI's roadmap
	// API answers failures with HTTP 200 and the failure in the body.
	SuccessField string `json:"success_field"`
	SuccessValue string `json:"success_value"`

	// HTML: one regex with named groups - id (required), title, url, time.
	ItemRegex string `json:"item_regex"`

	// URLPrefix is put in front of an item url that is not absolute.
	URLPrefix string `json:"url_prefix"`
}

// Configured reports whether there is an endpoint to poll at all.
func (s Source) Configured() bool { return strings.TrimSpace(s.URL) != "" }

// Config is the whole tunable surface.
type Config struct {
	// IntervalHours: hourly is the order's cadence (it replaces an hourly
	// sweep); anything faster is refused - somebody else's public endpoint.
	IntervalHours float64 `json:"interval_hours"`

	// UserAgent identifies us. A watcher that will not say who it is has no
	// business polling somebody else's site.
	UserAgent string `json:"user_agent"`

	// LiveURL is RSI's roadmap board: its description carries "Live Version:"
	// and "PTU Version:" - verified and parsed by roadmap-watcher since 08-30.
	LiveURL string `json:"live_url"`

	// StaleAgeMinutes: a newest post whose RELATIVE age string ("51 minutes
	// ago") has not moved for this long is a stuck page, and says so.
	StaleAgeMinutes float64 `json:"stale_age_minutes"`

	// StaleAfterCycles: missed cadences before the scheduled run is STALE.
	StaleAfterCycles float64 `json:"stale_after_cycles"`

	Sources []Source `json:"sources"`
}

func defaultConfig() Config {
	return Config{
		IntervalHours:    1,
		UserAgent:        "CitizenCompass-RSIWatcher/1.0 (+https://citizencompass.netlify.app)",
		LiveURL:          "https://robertsspaceindustries.com/api/roadmap/v1/boards/1",
		StaleAgeMinutes:  90,
		StaleAfterCycles: 3,
		Sources: []Source{
			{Name: "devtracker", Shelf: "devtracker"},
			{Name: "comm-link", Shelf: "comm-link"},
			{Name: "patchbot", Shelf: "patchbot"},
		},
	}
}

func (c Config) Interval() time.Duration { return time.Duration(c.IntervalHours * float64(time.Hour)) }

func (c Config) StaleAfter() time.Duration {
	return time.Duration(c.StaleAfterCycles * float64(c.Interval()))
}

var reSegment = regexp.MustCompile(`^[a-z0-9][a-z0-9-]*$`)

// Validate refuses rather than corrects: a settings file that says one thing
// while the program does another is the defect this project keeps finding.
func (c Config) Validate() error {
	if c.IntervalHours < 1 {
		return fmt.Errorf("interval_hours is %.2f; hourly is the floor - this polls "+
			"somebody else's public site. Nothing was polled", c.IntervalHours)
	}
	if strings.TrimSpace(c.UserAgent) == "" {
		return errors.New("user_agent is empty - the watcher must say who it is")
	}
	if strings.TrimSpace(c.LiveURL) == "" {
		return errors.New("live_url is empty")
	}
	if c.StaleAgeMinutes <= 0 || c.StaleAfterCycles <= 0 {
		return errors.New("stale_age_minutes and stale_after_cycles must both be positive")
	}
	if len(c.Sources) == 0 {
		return errors.New("no sources configured")
	}
	seen := map[string]bool{}
	for _, s := range c.Sources {
		if !reSegment.MatchString(s.Name) || !reSegment.MatchString(s.Shelf) {
			return fmt.Errorf("source %q / shelf %q: names and shelves are one lower-case "+
				"path segment [a-z0-9-] - nothing that could climb out of sc-brain", s.Name, s.Shelf)
		}
		if seen[s.Name] {
			return fmt.Errorf("source %q appears twice", s.Name)
		}
		seen[s.Name] = true
		if !s.Configured() {
			continue
		}
		if m := strings.ToUpper(s.Method); m != "GET" && m != "POST" {
			return fmt.Errorf("source %q: method must be GET or POST, got %q", s.Name, s.Method)
		}
		switch s.Format {
		case "json":
			if s.ItemsPath == "" || s.IDField == "" {
				return fmt.Errorf("source %q: json needs items_path and id_field", s.Name)
			}
		case "html":
			re, err := regexp.Compile(s.ItemRegex)
			if err != nil {
				return fmt.Errorf("source %q: item_regex does not compile: %v", s.Name, err)
			}
			if re.SubexpIndex("id") < 0 {
				return fmt.Errorf("source %q: item_regex needs a named group (?P<id>...)", s.Name)
			}
		default:
			return fmt.Errorf("source %q: format must be json or html, got %q", s.Name, s.Format)
		}
	}
	return nil
}

// LoadConfig reads the settings next to the exe, writing defaults if absent.
// -> (config, where it came from, error).
func LoadConfig(dir string) (Config, string, error) {
	path := filepath.Join(dir, configFileName)
	b, err := os.ReadFile(path)
	if errors.Is(err, os.ErrNotExist) {
		cfg := defaultConfig()
		out, _ := json.MarshalIndent(cfg, "", "  ")
		if werr := os.WriteFile(path, append(out, '\n'), 0o644); werr != nil {
			return cfg, "built-in defaults (could not write " + path + ")", nil
		}
		return cfg, path + " (defaults, written on first run)", nil
	}
	if err != nil {
		return Config{}, path, err
	}
	var cfg Config
	dec := json.NewDecoder(bytes.NewReader(b))
	dec.DisallowUnknownFields()
	if err := dec.Decode(&cfg); err != nil {
		return Config{}, path, fmt.Errorf("%s: %v (unknown keys are refused, not ignored)", path, err)
	}
	return cfg, path, nil
}
