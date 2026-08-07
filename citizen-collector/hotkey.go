package main

// hotkey.go - parsing "ctrl+alt+f9" into RegisterHotKey arguments.

import (
	"fmt"
	"runtime"
	"strings"
	"time"
)

// hotkeyListener owns one registered global hotkey and the OS thread that
// pumps its messages.
//
// # WHY IT OWNS A THREAD
//
// RegisterHotKey called with a NULL window delivers WM_HOTKEY to the message
// queue of the THREAD THAT REGISTERED IT. Nobody else can receive it. Manual
// mode gets away with registering on the main goroutine because main() calls
// runtime.LockOSThread and then sits in a GetMessage loop forever.
//
// --auto cannot do that: its main goroutine is inside runAuto's select, so
// there is no one draining the queue. Hence a dedicated locked thread whose
// only job is to register the key and pump for it, handing presses back on a
// channel that a select can wait on.
type hotkeyListener struct {
	// Pretty is the canonical name ("Ctrl+Alt+F9"), for logs and for telling
	// the operator which key is actually live.
	Pretty string
	// Presses fires once per press.
	Presses <-chan struct{}

	// threadID is the thread that holds the registration. Only that thread can
	// release it, so Close has to reach this specific one.
	threadID uint32
	// done closes once the pump has exited and the key is genuinely given back.
	done chan struct{}
}

// Close releases the hotkey and stops the pump.
//
// It posts WM_QUIT to the listener's own thread, which makes GetMessage return
// false so the deferred UnregisterHotKey runs THERE. Calling UnregisterHotKey
// from here would be a no-op with a success-shaped return: the registration
// belongs to the other thread.
//
// Close waits for the pump to actually exit. Returning before the key was
// released would let a caller observe it as still registered and conclude the
// wrong thing - which is precisely what the selftest is measuring.
func (h *hotkeyListener) Close() {
	if h == nil || h.done == nil {
		return
	}
	select {
	case <-h.done:
		return // already closed
	default:
	}
	PostThreadMessage(h.threadID, WM_QUIT, 0, 0)
	select {
	case <-h.done:
	case <-time.After(2 * time.Second):
		// The pump did not acknowledge. Say nothing reassuring - the caller's
		// own probe is the authority on whether the key is free.
	}
}

// startHotkeyListener parses spec, registers it, and starts pumping.
//
// Registration is reported SYNCHRONOUSLY - the call does not return until
// Windows has accepted or refused the key. A listener that reported success
// before the OS had agreed would be exactly the defect this is fixing, moved
// one layer down.
func startHotkeyListener(id int, spec string) (*hotkeyListener, error) {
	mods, vk, pretty, err := parseHotkey(spec)
	if err != nil {
		return nil, err
	}

	presses := make(chan struct{}, 1)
	registered := make(chan error, 1)
	tid := make(chan uint32, 1)
	done := make(chan struct{})

	go func() {
		// The registration and the GetMessage loop MUST be the same thread.
		// Without this the Go scheduler is free to move the goroutine and the
		// queue being pumped would no longer be the queue being posted to.
		runtime.LockOSThread()
		defer runtime.UnlockOSThread()
		defer close(done)

		tid <- GetCurrentThreadId()

		if err := RegisterHotKey(id, mods|ModNoRepeat, vk); err != nil {
			registered <- err
			return
		}
		registered <- nil
		defer UnregisterHotKey(id)

		var msg MSG
		for GetMessage(&msg) {
			if msg.Message != WM_HOTKEY {
				continue
			}
			select {
			case presses <- struct{}{}:
			default:
				// A press arriving while the previous one is still being
				// serviced is dropped rather than queued. Holding the key down
				// should not build a backlog of captures that fire minutes
				// later; ModNoRepeat already suppresses auto-repeat.
			}
		}
	}()

	threadID := <-tid
	if err := <-registered; err != nil {
		return nil, err
	}
	return &hotkeyListener{
		Pretty:   pretty,
		Presses:  presses,
		threadID: threadID,
		done:     done,
	}, nil
}

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
