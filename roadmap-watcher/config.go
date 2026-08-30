package main

// config.go - everything Sleven can change without a rebuild.
//
// The cadence, the endpoints and the stage-2 switch all live in a plain JSON
// file next to the exe, for the same reason collector-settings.txt does: the
// person who wants to change the interval should not need a toolchain.

import (
	"encoding/json"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"time"
)

const configFileName = "roadmap-watcher-settings.json"

// Config is the whole of the tool's tunable surface.
type Config struct {
	// IntervalHours is the polling cadence. FOUR IS THE ORDER'S STARTING VALUE,
	// in config so it can move without a rebuild.
	//
	// HOURLY IS REFUSED, not merely discouraged - see Validate. A tight loop on
	// somebody else's public endpoint is how a project gets an IP blocked, and
	// this board changes weekly at most.
	IntervalHours float64 `json:"interval_hours"`

	// Boards to poll on the Release-View side. NOT just board 1: board 2 is
	// "Squadron 42" and exists. Measured 2026-08-14 - it carries no
	// Constellation cards today, but "none today" is not "never would", and
	// naming the surface per result costs nothing.
	Boards []int `json:"boards"`

	BoardURL string `json:"board_url"`

	// Stage2Enabled gates the GraphQL client. BUILT NOW, SCHEDULED LATER, per
	// the order: Sleven's decision was to roll out in increments, not to refuse
	// the second endpoint. Flipping this is his call.
	Stage2Enabled bool   `json:"stage2_enabled"`
	GraphQLURL    string `json:"graphql_url"`

	// StaleAfterCycles is how many missed cadences make the watcher STALE.
	//
	// In cycles rather than hours so it stays correct when the interval moves -
	// a threshold in absolute hours silently becomes wrong the moment somebody
	// changes the cadence, which is the sort of coupling that goes unnoticed
	// until it matters.
	StaleAfterCycles float64 `json:"stale_after_cycles"`

	// Watch is the case-insensitive substring that makes a card interesting.
	Watch string `json:"watch"`

	// UserAgent identifies us to RSI. A watcher that will not say who it is has
	// no business running on somebody else's endpoint every four hours.
	UserAgent string `json:"user_agent"`
}

func defaultConfig() Config {
	return Config{
		IntervalHours: 4,

		// BOARD 2 RETIRED 2026-08-30, Q5d. Squadron 42's own payload says
		// "This version of the Squadron 42 Roadmap will not be updated" -
		// confirmed live on that date, and the watcher now reads that field.
		// Polling a board that declares itself dead every four hours is work
		// that can only ever report nothing, and a tripwire that cannot fire
		// looks exactly like coverage. Re-add 2 if RSI revives it; the URL
		// still resolves and nothing else about it changed.
		Boards:           []int{1},
		BoardURL:         "https://robertsspaceindustries.com/api/roadmap/v1/boards/%d",
		StaleAfterCycles: 3,
		Stage2Enabled:    false,
		GraphQLURL:       "https://robertsspaceindustries.com/graphql",
		// "*" IS EVERY CARD, Q5a. This was "Constellation" - seeded on one
		// test ship and never widened - and the baseline held three cards as a
		// result. R3's question is board-wide and a one-ship filter cannot
		// answer it. The settings file is gitignored, so this default is the
		// only place the decision survives a fresh checkout.
		Watch:     "*",
		UserAgent: "CitizenCompass-RoadmapWatcher/1.0 (+https://citizencompass.netlify.app)",
	}
}

// Validate refuses a configuration that would embarrass us on RSI's servers.
//
// It returns an error rather than silently correcting, because a settings file
// that says one thing while the program does another is the shape of defect
// this project keeps finding.
func (c Config) Validate() error {
	if c.IntervalHours < 2 {
		return fmt.Errorf(
			"interval_hours is %.2f, which is too aggressive for somebody else's "+
				"public endpoint. The order sets four hours and rules hourly out "+
				"explicitly; two is the floor this build will accept. Nothing was polled",
			c.IntervalHours)
	}
	if len(c.Boards) == 0 {
		return fmt.Errorf("no boards configured, so there is nothing to check")
	}
	// Q5a, 2026-08-30: "*" WATCHES THE WHOLE BOARD.
	//
	// This required a non-empty substring, and the settings file carried
	// "Constellation" - seeded on one test ship and never widened. R3's
	// question is board-wide and cannot be answered through a one-ship filter.
	//
	// EMPTY IS STILL REJECTED. An empty string would make a forgotten field and
	// a deliberate "everything" identical, and this program's whole job is
	// telling those two apart. "*" has to be typed on purpose.
	if c.BoardURL == "" || c.Watch == "" {
		return fmt.Errorf("board_url and watch must both be set " +
			"(watch \"*\" means every card on the board)")
	}
	return nil
}

func (c Config) Interval() time.Duration {
	return time.Duration(c.IntervalHours * float64(time.Hour))
}

// StaleAfter is how long without a good run before the watcher calls itself
// stale. Derived from the cadence, so moving the cadence moves this with it.
func (c Config) StaleAfter() time.Duration {
	n := c.StaleAfterCycles
	if n <= 0 {
		n = 3
	}
	return time.Duration(float64(c.Interval()) * n)
}

// LoadConfig reads the settings file beside the exe, writing a default one the
// first time so there is something to edit rather than a blank.
func LoadConfig(dir string) (Config, string, error) {
	path := filepath.Join(dir, configFileName)
	f, err := os.Open(path)
	if os.IsNotExist(err) {
		c := defaultConfig()
		if werr := writeConfig(path, c); werr != nil {
			return c, "defaults (could not write a settings file: " + werr.Error() + ")", nil
		}
		return c, "defaults, and a settings file was written to " + path, nil
	}
	if err != nil {
		return Config{}, "", err
	}
	defer f.Close()
	b, err := io.ReadAll(f)
	if err != nil {
		return Config{}, "", err
	}
	// Start from defaults so a settings file written before a key existed keeps
	// the default for it rather than receiving a zero. That exact defect cost
	// the collector its burst feature on every machine in the world.
	c := defaultConfig()
	if err := json.Unmarshal(b, &c); err != nil {
		return Config{}, "", fmt.Errorf("%s is not valid JSON (%w). Refusing to "+
			"guess what was meant; nothing was polled", configFileName, err)
	}
	return c, path, nil
}

func writeConfig(path string, c Config) error {
	b, err := json.MarshalIndent(c, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(path, append(b, '\n'), 0o644)
}
