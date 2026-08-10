package main

// shortcut.go - put it where they can find it.
//
// # THE PROBLEM, FROM THE ONLY TEST THAT COUNTS
//
// Sleven ran it on his friend's machine, 2026-08-08:
//
//	"it didn't give a desktop app or shortcut. That's something that is needed
//	 so people can find it easily once it installs. I did drag the application
//	 that launched it, citizen collector. It says collector on it"
//
// That is the same objection as the 271 MB package, one step later. The program
// unzips into a folder, and a folder somewhere in Downloads is a thing you find
// once and then never again. Dragging the exe out yourself produces a shortcut
// named "collector" with whatever icon Windows guessed - which is exactly what
// happened, and it is not a thing anybody wants on their desktop.
//
// # WHY IT ASKS INSTEAD OF JUST DOING IT
//
// Somebody's desktop is theirs. A program that puts an icon there uninvited is
// behaving like the software this project is deliberately not - and the whole
// consent design would be undercut by a tool that asks politely about reading a
// log file and then decorates your desktop without a word.
//
// So: one Yes/No box, once, on first run only, right after consent. Yes is one
// click and answers it forever. No is remembered and never asked again.
//
// # WHY BOTH DESKTOP AND START MENU
//
// The desktop icon is how it gets found tomorrow. The Start Menu entry is how it
// gets found in a month, when the desktop has been tidied - typing "citizen"
// finds it. Neither costs anything and they fail independently.
//
// # WHY SHGetKnownFolderPath AND NOT %USERPROFILE%\Desktop
//
// OneDrive redirects the Desktop folder on a large share of consumer machines,
// and it is the default on a new Windows 11 install with a Microsoft account.
// Writing to %USERPROFILE%\Desktop on a redirected machine creates a shortcut in
// a folder the user never sees - it succeeds, reports success, and produces
// nothing. That is the silent-success shape, and this project has logged it six
// times. The known-folder API returns the real location, redirected or not.

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"syscall"
	"unsafe"
)

const shortcutAnswerFile = "collector-shortcut.txt"

// shortcutName is what appears under the icon. NOT the exe name - "collector"
// is what Windows produces from collector.exe when somebody drags it out, and
// it is the thing Sleven reported.
const shortcutName = "Citizen Collector"

// modOle32 and the GUID type already exist in winapi.go. Reused rather than
// redeclared - two handles to the same DLL is exactly the kind of duplicate
// that drifts.
var (
	modShell = syscall.NewLazyDLL("shell32.dll")

	procCoCreateInstance     = modOle32.NewProc("CoCreateInstance")
	procCoTaskMemFree        = modOle32.NewProc("CoTaskMemFree")
	procSHGetKnownFolderPath = modShell.NewProc("SHGetKnownFolderPath")
)

var (
	clsidShellLink   = GUID{0x00021401, 0x0000, 0x0000, [8]byte{0xC0, 0, 0, 0, 0, 0, 0, 0x46}}
	iidShellLinkW    = GUID{0x000214F9, 0x0000, 0x0000, [8]byte{0xC0, 0, 0, 0, 0, 0, 0, 0x46}}
	iidPersistFile   = GUID{0x0000010B, 0x0000, 0x0000, [8]byte{0xC0, 0, 0, 0, 0, 0, 0, 0x46}}
	folderIDDesktop  = GUID{0xB4BFCC3A, 0xDB2C, 0x424C, [8]byte{0xB0, 0x29, 0x7F, 0xE9, 0x9A, 0x87, 0xC6, 0x41}}
	folderIDPrograms = GUID{0xA77F5D77, 0x2E2B, 0x44C3, [8]byte{0xA6, 0xA2, 0xAB, 0xA6, 0x01, 0x05, 0x4A, 0x51}}
)

// IShellLinkW and IPersistFile vtable slots. Written out rather than computed,
// because an off-by-one here calls a different method with the same arguments
// and the failure is a crash inside a system DLL with no useful message.
const (
	slotRelease         = 2
	slotShellSetPath    = 20
	slotShellSetWorkDir = 9
	slotShellSetDesc    = 7
	slotShellSetIcon    = 17
	slotQueryInterface  = 0
	slotPersistSave     = 6
)

// comCall invokes a method on a COM interface pointer.
//
// obj is unsafe.Pointer rather than uintptr on purpose. Holding a COM pointer
// as a uintptr and converting it back is what `go vet` flags as "possible
// misuse of unsafe.Pointer", and the warning is not pedantry - a uintptr is
// just a number to the compiler, so nothing stops it being kept across a point
// where the value stops being valid. Keeping it typed the whole way removes
// both the warning and the class of bug it is pointing at.
func comCall(obj unsafe.Pointer, slot int, args ...uintptr) uintptr {
	vtbl := *(**[32]uintptr)(obj)
	call := append([]uintptr{uintptr(obj)}, args...)
	r, _, _ := syscall.SyscallN(vtbl[slot], call...)
	return r
}

// knownFolder resolves a shell folder, honouring OneDrive redirection.
func knownFolder(id GUID) (string, error) {
	// Typed as *uint16 throughout - see the note on comCall. The shell
	// allocates this and we must free it, so it is COM memory, not Go memory.
	var p *uint16
	r, _, _ := procSHGetKnownFolderPath.Call(
		uintptr(unsafe.Pointer(&id)), 0, 0, uintptr(unsafe.Pointer(&p)))
	if r != 0 || p == nil {
		return "", fmt.Errorf("SHGetKnownFolderPath returned 0x%x", r)
	}
	defer procCoTaskMemFree.Call(uintptr(unsafe.Pointer(p)))

	// UTF-16, NUL-terminated, length unknown. unsafe.Add rather than arithmetic
	// on a uintptr, for the same reason.
	var out []uint16
	for q := p; *q != 0; q = (*uint16)(unsafe.Add(unsafe.Pointer(q), 2)) {
		out = append(out, *q)
	}
	return syscall.UTF16ToString(out), nil
}

// CreateShortcut writes a .lnk pointing at this executable.
func CreateShortcut(lnkPath, target, workDir, desc, icon string) error {
	var psl unsafe.Pointer
	// CLSCTX_INPROC_SERVER = 1. The apartment is already initialised - the
	// process is apartment-threaded from go-webview2's init, and the CLI path
	// initialises before calling here.
	r, _, _ := procCoCreateInstance.Call(
		uintptr(unsafe.Pointer(&clsidShellLink)), 0, 1,
		uintptr(unsafe.Pointer(&iidShellLinkW)), uintptr(unsafe.Pointer(&psl)))
	if r != 0 || psl == nil {
		return fmt.Errorf("could not create a shell link object (0x%x)", r)
	}
	defer comCall(psl, slotRelease)

	set := func(slot int, s string) error {
		p, err := syscall.UTF16PtrFromString(s)
		if err != nil {
			return err
		}
		if hr := comCall(psl, slot, uintptr(unsafe.Pointer(p))); hr != 0 {
			return fmt.Errorf("shell link setter %d returned 0x%x", slot, hr)
		}
		return nil
	}
	if err := set(slotShellSetPath, target); err != nil {
		return err
	}
	if err := set(slotShellSetWorkDir, workDir); err != nil {
		return err
	}
	if err := set(slotShellSetDesc, desc); err != nil {
		return err
	}
	if icon != "" {
		if p, err := syscall.UTF16PtrFromString(icon); err == nil {
			comCall(psl, slotShellSetIcon, uintptr(unsafe.Pointer(p)), 0)
		}
	}

	var ppf unsafe.Pointer
	if hr := comCall(psl, slotQueryInterface,
		uintptr(unsafe.Pointer(&iidPersistFile)), uintptr(unsafe.Pointer(&ppf))); hr != 0 || ppf == nil {
		return fmt.Errorf("the shell link does not support saving (0x%x)", hr)
	}
	defer comCall(ppf, slotRelease)

	wp, err := syscall.UTF16PtrFromString(lnkPath)
	if err != nil {
		return err
	}
	// Save(path, fRemember=TRUE)
	if hr := comCall(ppf, slotPersistSave, uintptr(unsafe.Pointer(wp)), 1); hr != 0 {
		return fmt.Errorf("the shortcut could not be written (0x%x)", hr)
	}

	// VERIFY IT IS ACTUALLY THERE.
	//
	// Save returning S_OK is the API's opinion. A file on disk is the fact, and
	// the two have differed before on redirected folders. Six silent successes
	// on this project say check.
	if _, err := os.Stat(lnkPath); err != nil {
		return fmt.Errorf("the shortcut reported success but is not on disk: %w", err)
	}
	return nil
}

// shortcutAsked reports whether this machine has already answered.
func shortcutAsked(dir string) bool {
	_, err := os.Stat(filepath.Join(dir, shortcutAnswerFile))
	return err == nil
}

func recordShortcutAnswer(dir, answer string) {
	body := "# citizen-collector - your answer about desktop and Start Menu shortcuts.\n" +
		"# Delete this file to be asked again.\n\n" +
		"shortcuts = " + answer + "\n"
	_ = os.WriteFile(filepath.Join(dir, shortcutAnswerFile), []byte(body), 0o644)
}

// OfferShortcuts asks once, on first run, and acts on the answer.
//
// Never fatal. Every failure below leaves a working program that is merely
// harder to find, and refusing to start over a missing desktop icon would be a
// far worse trade than the one it is trying to fix.
func OfferShortcuts(exeDir string, logf func(string, ...interface{})) {
	if logf == nil {
		logf = func(string, ...interface{}) {}
	}
	if shortcutAsked(exeDir) {
		return
	}

	exe, err := os.Executable()
	if err != nil {
		logf("shortcut: cannot find my own path, so no shortcut was offered (%v)", err)
		return
	}

	const (
		mbYesNo        = 0x00000004
		mbIconQuestion = 0x00000020
		idYes          = 6
	)
	proc := modUser32.NewProc("MessageBoxW")
	title, _ := syscall.UTF16PtrFromString("Citizen Collector")
	msg, _ := syscall.UTF16PtrFromString(
		"Put Citizen Collector on your desktop and in your Start Menu?\n\n" +
			"Otherwise it only exists in this folder, and folders get lost.\n\n" +
			"Nothing is installed either way - a shortcut is just a pointer to " +
			"this file, and deleting the folder removes everything.")
	r, _, _ := proc.Call(0,
		uintptr(unsafe.Pointer(msg)), uintptr(unsafe.Pointer(title)),
		uintptr(mbYesNo|mbIconQuestion))

	if int(r) != idYes {
		recordShortcutAnswer(exeDir, "no")
		logf("shortcut: declined - not asking again. Delete %s to be asked once more.",
			shortcutAnswerFile)
		return
	}

	// The icon comes from the exe itself now that resources are embedded, so
	// there is no .ico file to ship, lose, or get out of step with the binary.
	icon := exe + ",0"

	targets := []struct {
		id    GUID
		label string
	}{
		{folderIDDesktop, "desktop"},
		{folderIDPrograms, "Start Menu"},
	}

	made := 0
	for _, t := range targets {
		dir, err := knownFolder(t.id)
		if err != nil {
			logf("shortcut: could not find your %s folder (%v)", t.label, err)
			continue
		}
		lnk := filepath.Join(dir, shortcutName+".lnk")
		if err := CreateShortcut(lnk, exe, exeDir,
			"Records what Star Citizen already writes down, so the community can map prices and places.",
			icon); err != nil {
			logf("shortcut: could not create the %s shortcut (%v)", t.label, err)
			continue
		}
		logf("shortcut: created %s", lnk)
		made++
	}

	// Recorded either way. Asking again next launch because the desktop folder
	// was unavailable once would turn a minor failure into a nag.
	recordShortcutAnswer(exeDir, "yes")

	if made == 0 {
		logf("shortcut: none could be created. The program works exactly the same; " +
			"it is just in this folder only.")
	}
}

// shortcutTargetName is used by the selftest, and exists so the name cannot be
// changed in one place and asserted in another.
func shortcutTargetName() string { return strings.TrimSpace(shortcutName) }
