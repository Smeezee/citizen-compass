package main

// hotkey.go - parsing "ctrl+alt+f9" into RegisterHotKey arguments.

import (
	"fmt"
	"strings"
)

var vkNames = map[string]uint32{
	"f1": 0x70, "f2": 0x71, "f3": 0x72, "f4": 0x73,
	"f5": 0x74, "f6": 0x75, "f7": 0x76, "f8": 0x77,
	"f9": 0x78, "f10": 0x79, "f11": 0x7A, "f12": 0x7B,
	"print": 0x2C, "printscreen": 0x2C, "prtsc": 0x2C,
	"scroll": 0x91, "scrolllock": 0x91,
	"pause": 0x13, "insert": 0x2D, "ins": 0x2D,
	"home": 0x24, "end": 0x23, "pgup": 0x21, "pgdn": 0x22,
	"space": 0x20, "tab": 0x09, "`": 0xC0, "grave": 0xC0,
}

// parseHotkey turns "ctrl+alt+f9" into (modifiers, virtual-key, pretty name).
//
// Rejects a bare key with no modifier on purpose. RegisterHotKey is global: a
// modifier-less F9 would be swallowed system-wide, including inside the game,
// which would break the very thing the operator is trying to photograph.
func parseHotkey(s string) (mods uint32, vk uint32, pretty string, err error) {
	parts := strings.Split(strings.ToLower(strings.TrimSpace(s)), "+")
	if len(parts) == 0 || parts[0] == "" {
		return 0, 0, "", fmt.Errorf("empty hotkey")
	}

	var prettyParts []string
	keySet := false

	for _, p := range parts {
		p = strings.TrimSpace(p)
		switch p {
		case "ctrl", "control":
			mods |= ModControl
			prettyParts = append(prettyParts, "Ctrl")
		case "alt":
			mods |= ModAlt
			prettyParts = append(prettyParts, "Alt")
		case "shift":
			mods |= ModShift
			prettyParts = append(prettyParts, "Shift")
		case "win", "super":
			mods |= ModWin
			prettyParts = append(prettyParts, "Win")
		default:
			if keySet {
				return 0, 0, "", fmt.Errorf("hotkey %q names more than one non-modifier key", s)
			}
			if v, ok := vkNames[p]; ok {
				vk = v
			} else if len(p) == 1 {
				c := p[0]
				switch {
				case c >= 'a' && c <= 'z':
					vk = uint32(c - 'a' + 'A')
				case c >= '0' && c <= '9':
					vk = uint32(c)
				default:
					return 0, 0, "", fmt.Errorf("unrecognised key %q in hotkey %q", p, s)
				}
			} else {
				return 0, 0, "", fmt.Errorf("unrecognised key %q in hotkey %q", p, s)
			}
			keySet = true
			prettyParts = append(prettyParts, strings.ToUpper(p))
		}
	}

	if !keySet {
		return 0, 0, "", fmt.Errorf("hotkey %q has modifiers but no key", s)
	}
	if mods == 0 {
		return 0, 0, "", fmt.Errorf(
			"hotkey %q has no modifier. A bare key would be captured globally and "+
				"stop working inside the game - use something like ctrl+alt+f9", s)
	}
	return mods, vk, strings.Join(prettyParts, "+"), nil
}
