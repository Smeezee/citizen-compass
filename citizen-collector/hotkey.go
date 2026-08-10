package main

// hotkey.go - parsing "alt+f3" into RegisterHotKey arguments.

import (
	"fmt"
	"runtime"
	"strings"
	"sync"
	"time"
)

// defaultHotkey and fallbackHotkey - chosen from the game's own bindings, not
// from guesswork.
//
// THE RULE THAT MATTERS IS NOT "IS THIS KEY FREE"
//
// The useful question is: DOES THE GAME REFUSE THIS KEY WHEN A MODIFIER IS
// HELD? Star Citizen's defaultProfile answers it directly, because a binding
// carrying noModifiers="1" is refused by the game the moment any modifier is
// down. Alt+<that key> is therefore unclaimed no matter what the bare key does.
//
// F3's only bare binding is:
//
//	<action name="flymode" onPress="1" noModifiers="1" keyboard="f3"/>
//
// Verified against data-layer/processed/defaultProfile.plain.xml (1,106
// actions): f3 has exactly one bare binding, it carries noModifiers="1", and
// there is no lalt+f3 combination anywhere. F3 is the ONLY F key of which all
// of that is true - f5, f6 and f7 each have two bare bindings with no
// noModifiers flag AND two lalt combinations, so Alt+F5/F6/F7 are all claimed.
//
// So Alt+F3 cannot collide: holding Alt makes the game refuse flymode, and
// nothing else in the profile wants that combination.
//
// FALLBACK. On a keyboard where Alt+F3 will not register - some laptops give
// the F row to media keys, and some vendor utilities take Alt+F combinations
// before any application sees them - alt+insert is the alternative. "insert"
// appears NOWHERE in any of the 1,106 actions, so it cannot conflict with the
// game at all.
const (
	defaultHotkey  = "alt+f3"
	fallbackHotkey = "alt+insert"
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
	// Pretty is the canonical name ("Alt+F3"), for logs and for telling
	// the operator which key is actually live.
	Pretty string
	// Presses fires once per press. The value is the MECHANISM that delivered
	// it - "RegisterHotKey" or "polling" - not a payload.
	//
	// WHY THE MECHANISM IS ON THE WIRE AND NOT JUST IN A LOG LINE HERE
	//
	// There are two independent delivery paths below and they fail under
	// different conditions. Carrying the name through to the place that writes
	// the log means one grep after a session answers "which path is actually
	// working on this machine, on this renderer". Without it we would be back
	// to inferring, which is what cost four wrong diagnoses.
	Presses <-chan string

	// threadID is the thread that holds the registration. Only that thread can
	// release it, so Close has to reach this specific one.
	threadID uint32
	// done closes once the pump has exited and the key is genuinely given back.
	done chan struct{}
	// stopPoll ends the GetAsyncKeyState fallback loop.
	stopPoll chan struct{}
	// pollDone closes when that loop has exited.
	pollDone chan struct{}
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
	if h.stopPoll != nil {
		close(h.stopPoll)
		if h.pollDone != nil {
			select {
			case <-h.pollDone:
			case <-time.After(2 * time.Second):
			}
		}
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

	presses := make(chan string, 1)
	registered := make(chan error, 1)
	tid := make(chan uint32, 1)
	done := make(chan struct{})
	stopPoll := make(chan struct{})
	pollDone := make(chan struct{})

	// deliver is shared by both mechanisms and is what makes them safe to run
	// together. Two paths that both work would otherwise take two pictures of
	// one keystroke.
	//
	// The window is 400ms: comfortably longer than the gap between the OS
	// message and the next poll tick, comfortably shorter than a human pressing
	// the key twice on purpose. Sleven's own test pressed it twice three seconds
	// apart and both must count.
	var (
		fireMu   sync.Mutex
		lastFire time.Time
	)
	deliver := func(via string) {
		fireMu.Lock()
		if time.Since(lastFire) < 400*time.Millisecond {
			fireMu.Unlock()
			return // the other mechanism already reported this press
		}
		lastFire = time.Now()
		fireMu.Unlock()

		select {
		case presses <- via:
		default:
			// A press arriving while the previous one is still being serviced is
			// dropped rather than queued. Holding the key down should not build
			// a backlog of captures that fire minutes later.
		}
	}

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
			deliver("RegisterHotKey")
		}
	}()

	go pollHotkey(mods, vk, deliver, stopPoll, pollDone)

	threadID := <-tid
	if err := <-registered; err != nil {
		close(stopPoll)
		<-pollDone
		return nil, err
	}
	return &hotkeyListener{
		Pretty:   pretty,
		Presses:  presses,
		threadID: threadID,
		done:     done,
		stopPoll: stopPoll,
		pollDone: pollDone,
	}, nil
}

// modifierVKs turns the RegisterHotKey modifier bitmask into the virtual-key
// codes GetAsyncKeyState wants. Win is a pair because there is no "either Win"
// code the way VK_MENU covers either Alt.
func modifierVKs(mods uint32) [][]uint32 {
	var need [][]uint32
	if mods&ModAlt != 0 {
		need = append(need, []uint32{vkMenu})
	}
	if mods&ModControl != 0 {
		need = append(need, []uint32{vkControl})
	}
	if mods&ModShift != 0 {
		need = append(need, []uint32{vkShift})
	}
	if mods&ModWin != 0 {
		need = append(need, []uint32{vkLWin, vkRWin})
	}
	return need
}

// comboDown reports whether the key AND every required modifier are down now.
func comboDown(need [][]uint32, vk uint32) bool {
	if !keyIsDown(vk) {
		return false
	}
	for _, group := range need {
		any := false
		for _, m := range group {
			if keyIsDown(m) {
				any = true
				break
			}
		}
		if !any {
			return false
		}
	}
	return true
}

// pollHotkey is the second delivery path, and on Star Citizen's Vulkan renderer
// it is expected to be the only one that works.
//
// # WHY THIS EXISTS
//
// RegisterHotKey depends on Windows DELIVERING A MESSAGE to a background
// process. Established on 2026-08-07 by Sleven, with one variable changed and
// everything else held constant:
//
//	Vulkan  ->  registers, and no press is ever delivered
//	DX11    ->  registers, and every press is delivered
//
// A Vulkan application can hold true exclusive presentation through
// VK_EXT_full_screen_exclusive REGARDLESS of the window being styled
// borderless, which is why the game's display-mode setting was never what
// decided this. 4.10 ships Vulkan and CIG is retiring DX11, so "run DX11" is a
// workaround with an expiry date, not a fix.
//
// GetAsyncKeyState reads the keyboard's own async state. It waits for no
// message, hooks nothing, injects nothing and touches no other process - which
// keeps it inside the standing rule "no injection, no hooking, no reading game
// memory, no synthetic input".
//
// # THE EDGE DETECTION IS THE WHOLE THING
//
// We read only bit 0x8000, "down right now", and track the transition
// ourselves. The tempting bit is 0x0001, "pressed since the last call" - but
// that bit is process-wide and is CLEARED BY WHOEVER READS IT FIRST, so any
// other code calling GetAsyncKeyState steals our press. Doing our own edge
// detection cannot be perturbed by anything else in this process, now or later.
//
// down=true is held until the key is physically released, which is what
// preserves ModNoRepeat's behaviour: holding the key gives one capture, not a
// stream of them.
func pollHotkey(mods, vk uint32, deliver func(string), stop <-chan struct{}, done chan<- struct{}) {
	defer close(done)
	need := modifierVKs(mods)
	ticker := time.NewTicker(30 * time.Millisecond)
	defer ticker.Stop()

	down := false
	for {
		select {
		case <-stop:
			return
		case <-ticker.C:
		}
		if comboDown(need, vk) {
			if !down {
				down = true
				deliver("polling")
			}
			continue
		}
		down = false
	}
}

// hotkeyEdge is the edge detector on its own, with no Win32 in it, so the
// selftest can drive it with a synthetic key-state source and assert the exact
// number of fires. See hotkey_poll_selftest.go.
//
// It is the SAME logic as the loop above rather than a copy that could drift:
// the loop's body is three lines and this is those three lines. If you change
// one, change both, and the selftest will tell you if you did not.
type hotkeyEdge struct{ down bool }

// step feeds one observation and reports whether this is a fresh press.
func (e *hotkeyEdge) step(isDown bool) bool {
	if isDown {
		if !e.down {
			e.down = true
			return true
		}
		return false
	}
	e.down = false
	return false
}

// prettyKeyName renders a key the way a person writes it: F3, not f3, and
// Insert rather than INSERT. It is shown in the window and in the log, so
// shouting at the reader is a small thing done needlessly.
func prettyKeyName(p string) string {
	if len(p) >= 2 && p[0] == 'f' {
		if _, isFKey := vkNames[p]; isFKey && p[1] >= '0' && p[1] <= '9' {
			return strings.ToUpper(p)
		}
	}
	if len(p) == 1 {
		return strings.ToUpper(p)
	}
	return strings.ToUpper(p[:1]) + p[1:]
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

	// MOUSE BUTTONS. Added 2026-08-08 for capture_keys_held: "when they pull the
	// trigger and the guns are shooting" is a mouse button on most setups, and a
	// key watcher that cannot see the trigger misses the whole of combat.
	//
	// These are only ever READ, never registered as hotkeys - GetAsyncKeyState
	// reports them exactly like any other virtual key. parseHotkey still refuses
	// them for the global hotkey, where swallowing a mouse button system-wide
	// would be indefensible.
	"mouse1": 0x01, "lmb": 0x01, "leftclick": 0x01,
	"mouse2": 0x02, "rmb": 0x02, "rightclick": 0x02,
	"mouse3": 0x04, "mmb": 0x04, "middleclick": 0x04,
	"mouse4": 0x05, "mouse5": 0x06,
}

// parseHotkey turns "alt+f3" into (modifiers, virtual-key, pretty name).
//
// Rejects a bare key with no modifier on purpose. RegisterHotKey is global: a
// modifier-less F3 would be swallowed system-wide, including inside the game,
// which would break the very thing the operator is trying to photograph.
// parseHotkey parses a spec for RegisterHotKey - a GLOBAL hotkey.
//
// Requires a modifier. See parseKeySpec for why that rule exists and why it
// must not be applied to watched keys.
func parseHotkey(s string) (mods uint32, vk uint32, pretty string, err error) {
	return parseKeySpec(s, true)
}

// parseKeySpec decodes a key description. requireModifier decides the POLICY;
// the decoding is the same either way.
//
// # WHY THIS SPLIT EXISTS - a feature that was dead on arrival
//
// The modifier rule is correct for a global hotkey and only for a global
// hotkey. RegisterHotKey takes the key away from every other program on the
// machine, so a bare "V" would be swallowed system-wide and stop working inside
// Star Citizen. Refusing it is right.
//
// capture_keys and capture_keys_held are not hotkeys. They are polled with
// GetAsyncKeyState's down-state bit - they OBSERVE the keyboard and take
// nothing from anyone. A bare key is exactly what they are for: tab, v, mouse1,
// the trigger.
//
// The watched-key parser called parseHotkey anyway, so every single-key entry
// was rejected with "has no modifier" - and single keys are the only kind
// anybody would ever write there. capture_keys and capture_keys_held have
// therefore NEVER worked, in any build, since the day they were added. Nothing
// errored at runtime: the settings were read, the entries were refused, the
// problems went into a log line, and the feature quietly did nothing.
//
// Found by the selftest on 2026-08-08, on its first ever run. It would not have
// been found by using the program, because the failure looks exactly like "I
// pressed the key and no picture appeared".
func parseKeySpec(s string, requireModifier bool) (mods uint32, vk uint32, pretty string, err error) {
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
			prettyParts = append(prettyParts, prettyKeyName(p))
		}
	}

	if !keySet {
		return 0, 0, "", fmt.Errorf("hotkey %q has modifiers but no key", s)
	}
	if requireModifier && mods == 0 {
		return 0, 0, "", fmt.Errorf(
			"hotkey %q has no modifier. A bare key would be captured globally and "+
				"stop working inside the game - use something like "+defaultHotkey, s)
	}
	return mods, vk, strings.Join(prettyParts, "+"), nil
}
