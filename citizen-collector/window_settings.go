package main

// window_settings.go - every setting, changeable without opening a text file.
//
// Sleven's standing ruling: nobody should ever open a text file to configure
// this. collector-settings.txt stays readable as the escape hatch, but it is
// never how a person is expected to change anything.
//
// # WRITING A SETTINGS FILE WITHOUT DESTROYING IT
//
// The file carries comments explaining every key, and those comments are the
// only documentation a person who opens it will ever read. Regenerating it from
// current values would throw all of that away the first time somebody ticked a
// box. So a change rewrites THE ONE LINE it changes and leaves the rest of the
// file exactly as it was, comments included.

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"
)

// SetSetting changes one key in collector-settings.txt, preserving everything
// else - including comments, ordering, and keys this build has never heard of.
func SetSetting(exeDir, key, value string) error {
	p := filepath.Join(exeDir, settingsFileName)
	raw, err := os.ReadFile(p)
	if err != nil && !os.IsNotExist(err) {
		return err
	}
	lines := strings.Split(strings.ReplaceAll(string(raw), "\r\n", "\n"), "\n")

	found := false
	for i, line := range lines {
		trimmed := strings.TrimSpace(line)
		if trimmed == "" || strings.HasPrefix(trimmed, "#") {
			continue
		}
		k, _, ok := strings.Cut(trimmed, "=")
		if ok && strings.EqualFold(strings.TrimSpace(k), key) {
			lines[i] = fmt.Sprintf("%s = %s", key, value)
			found = true
			break
		}
	}
	if !found {
		for len(lines) > 0 && strings.TrimSpace(lines[len(lines)-1]) == "" {
			lines = lines[:len(lines)-1]
		}
		lines = append(lines, fmt.Sprintf("%s = %s", key, value), "")
	}
	return os.WriteFile(p, []byte(strings.Join(lines, "\n")), 0o644)
}

// showWindowKey is the tray-or-window choice, in the settings file so it is
// visible and so the escape hatch works.
const showWindowKey = "show_window"

// ShowWindowSetting reports whether the window opens on launch.
//
// # THE UPGRADE RULE (§3), WHICH IS THE WHOLE POINT OF THIS FUNCTION
//
// Sleven's wife and his friend will take this as an ordinary update they did
// not ask for. They must not be interrogated on first launch, and they must not
// silently LOSE anything either - and what they have today is a window that
// opens every time.
//
// So an install that already exists gets `true` and is never asked. Only an
// install with no history at all is a candidate for the question. Same
// principle as the auto-send choice, for the same reason: an update must not
// change the deal underneath somebody.
func ShowWindowSetting(exeDir string) bool {
	if cfg, _ := loadSettings(exeDir); true {
		if v, ok := cfg.boolVal(showWindowKey); ok {
			return v
		}
	}
	// Nothing recorded. Which way that falls depends entirely on whether this
	// machine is new.
	if IsUpgradedInstall(exeDir) {
		return true
	}
	return defaultShowWindow
}

// IsUpgradedInstall reports whether this machine was running the collector
// before this version arrived.
//
// The consent record is the signal, because it is the one file that only exists
// once somebody has agreed to something - which is exactly the population that
// must not be ambushed. A fresh unzip has no consent file, no install id and no
// captures folder.
func IsUpgradedInstall(exeDir string) bool {
	if _, err := os.Stat(filepath.Join(exeDir, consentFile)); err == nil {
		return true
	}
	return false
}

// HasWindowChoice reports whether this machine has an explicit answer recorded.
//
// Distinct from what the answer IS. A machine with no recorded answer that is
// also not an upgrade is the only one that may be asked, and asking twice is
// how a reasonable question becomes a nuisance.
func HasWindowChoice(exeDir string) bool {
	cfg, _ := loadSettings(exeDir)
	_, ok := cfg.boolVal(showWindowKey)
	return ok
}

// SetShowWindow records the choice.
func SetShowWindow(exeDir string, show bool) error {
	return SetSetting(exeDir, showWindowKey, boolWord(show))
}

func boolWord(b bool) string {
	if b {
		return "true"
	}
	return "false"
}

// windowChoiceText is the question a genuinely fresh crew install is asked.
const windowChoiceText = `Citizen Collector

How would you like it to run?

    YES  - show me the window.
           It opens when you start it, and shows what it is doing.

    NO   - just sit in the tray.
           No window. It rests by the clock and collects while you play.
           Right-click that icon any time to open the window, send your
           data, or stop it.

Either way it works exactly the same. You can change this whenever you
like from the tray icon - it is not permanent.

Show the window?`

// AskWindowChoice asks a fresh install, once, and records the answer.
//
// NEVER ASKS AN UPGRADE. That is checked here rather than at the call site, so
// there is no way to add a second caller that forgets.
func AskWindowChoice(exeDir string, logf func(string, ...interface{})) bool {
	if logf == nil {
		logf = func(string, ...interface{}) {}
	}
	if HasWindowChoice(exeDir) {
		return ShowWindowSetting(exeDir)
	}
	if IsUpgradedInstall(exeDir) {
		// SILENTLY KEEP WHAT THEY HAVE. Recorded so the question never comes
		// up later either, and so the tray menu shows the right tick.
		show := true
		_ = SetShowWindow(exeDir, show)
		logf("window: this install predates the window choice, so it keeps the "+
			"window it already had. Not asking. Change it from the tray icon. (%s)",
			showWindowKey)
		return show
	}
	if defaultShowWindow {
		// The master build does not need asking - it is the working build and
		// the window is the point.
		_ = SetShowWindow(exeDir, true)
		return true
	}

	const (
		mbYesNo        = 0x00000004
		mbIconQuestion = 0x00000020
		idYes          = 6
	)
	show := messageBox("Citizen Collector", windowChoiceText, mbYesNo|mbIconQuestion) == idYes
	if err := SetShowWindow(exeDir, show); err != nil {
		logf("window: could not record your choice (%v) - showing the window this "+
			"time and asking again next start.", err)
		return true
	}
	logf("window: %s on startup, chosen at setup. Changeable from the tray icon.",
		map[bool]string{true: "showing the window", false: "staying in the tray"}[show])
	return show
}
