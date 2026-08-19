package main

// selfinstall.go - the program installs itself, because it can.
//
// ===========================================================================
// WHY THERE IS NO INSTALLER
// ===========================================================================
//
// C1's ruling, 2026-08-19, after the antivirus question was put to it:
//
//   - an MSI needs WiX needs the .NET SDK on Sleven's machine: software fetched
//     from the network to solve a problem the program can solve itself
//   - an unsigned installer EXE is the dropper shape - worse antivirus
//     treatment, no upside
//   - the collector today IS an unsigned Go exe and both field machines have
//     run it. That shape has reputation with them. Keep it.
//
// So the one downloaded file installs itself on first run. Everything an
// installer was for is done here, per-user, with no admin rights anywhere:
//
//	%LOCALAPPDATA%\Programs\CitizenCollector   the program
//	HKCU\...\Uninstall\CitizenCollector        the Add/Remove Programs entry
//	Start menu + Desktop                       shortcuts
//	the Startup folder                         removed BY THE UNINSTALLER
//
// ===========================================================================
// THE THING THIS FIXES THAT NOTHING ELSE DOES
// ===========================================================================
//
// Today the way to remove the collector is "delete the folder", and that leaves
// a Startup shortcut pointing at nothing - while the README says nothing is
// left behind. That sentence is currently false. An uninstaller that owns what
// it created is what makes it true.

import (
	"fmt"
	"io"
	"os"
	"path/filepath"
	"strings"
	"syscall"
	"unsafe"
)

// installFolderName is the folder under %LOCALAPPDATA%\Programs.
const installFolderName = "CitizenCollector"

// arpKeyPath is the per-user Add/Remove Programs entry.
//
// HKEY_CURRENT_USER, NOT HKEY_LOCAL_MACHINE. The machine-wide key needs admin;
// the per-user one does not, and it is a documented, supported location that
// Settings > Apps reads. Requiring admin on a gaming PC for a fan tool is a
// reason to decline the tool, so nothing here ever asks for it.
const arpKeyPath = `Software\Microsoft\Windows\CurrentVersion\Uninstall\CitizenCollector`

// installConfig is what the installer touches. Injected so the checks can prove
// the mechanism inside a throwaway prefix rather than on somebody's real Start
// menu - hard rule 6, and I would rather ask than leave a shortcut on a desktop.
type installConfig struct {
	Root       string // where the program goes
	RegKeyPath string // the ARP key, under HKCU
	Shortcuts  bool   // create Start menu / Desktop entries
}

func defaultInstallConfig() installConfig {
	return installConfig{Root: InstalledRoot(), RegKeyPath: arpKeyPath, Shortcuts: true}
}

// InstalledRoot is where an installed collector lives.
func InstalledRoot() string {
	base := os.Getenv("LOCALAPPDATA")
	if strings.TrimSpace(base) == "" {
		// No LOCALAPPDATA is not a Windows this program understands. Returning
		// a plausible-looking path would install into somewhere arbitrary.
		return ""
	}
	return filepath.Join(base, "Programs", installFolderName)
}

// ===========================================================================
// THE TEMP / ARCHIVE REFUSAL
// ===========================================================================

// IsTempOrArchivePath reports whether a directory is one Windows will wipe.
//
// THE FAILURE THIS PREVENTS IS SILENT AND TOTAL. Windows lets somebody
// double-click a .zip and run the exe straight out of the preview window. It
// looks exactly like a normal install: the program starts, takes pictures,
// writes a diary. All of it goes to
//
//	%LOCALAPPDATA%\Temp\Temp1_citizen-collector.zip\
//
// which Windows deletes without asking. Everything the person collected is
// gone and nothing ever told them. Ordinary people do this constantly - it is
// the default way a zip behaves when you double-click it.
//
// Checked by PATH SHAPE rather than by asking whether the folder is writable,
// because a temp folder is perfectly writable right up until it is not there.
func IsTempOrArchivePath(dir string) (bool, string) {
	if strings.TrimSpace(dir) == "" {
		return false, ""
	}
	low := strings.ToLower(filepath.Clean(dir))

	// The zip-preview shape, which is the one that actually happens.
	base := strings.ToLower(filepath.Base(low))
	if strings.HasPrefix(base, "temp") && strings.Contains(base, ".zip") {
		return true, "inside a zip file that Windows opened for a preview"
	}
	for _, ext := range []string{".zip", ".rar", ".7z", ".cab"} {
		if strings.Contains(low, ext+string(filepath.Separator)) {
			return true, "inside a " + strings.TrimPrefix(ext, ".") + " archive"
		}
	}

	// The temp folders themselves, from the environment rather than guessed, so
	// a machine with a relocated TEMP is still covered.
	for _, env := range []string{"TEMP", "TMP"} {
		t := strings.ToLower(strings.TrimSpace(os.Getenv(env)))
		if t == "" {
			continue
		}
		t = filepath.Clean(t)
		if low == t || strings.HasPrefix(low, t+string(filepath.Separator)) {
			return true, "in the Windows temporary folder, which Windows deletes"
		}
	}
	// And the usual location even if the environment lies about it.
	if strings.Contains(low, `\appdata\local\temp\`) ||
		strings.HasSuffix(low, `\appdata\local\temp`) {
		return true, "in the Windows temporary folder, which Windows deletes"
	}
	return false, ""
}

// ===========================================================================
// REGISTRY - the smallest amount of it that does the job
// ===========================================================================

var (
	modAdvapi32        = syscall.NewLazyDLL("advapi32.dll")
	procRegCreateKeyEx = modAdvapi32.NewProc("RegCreateKeyExW")
	procRegSetValueEx  = modAdvapi32.NewProc("RegSetValueExW")
	procRegQueryValue  = modAdvapi32.NewProc("RegQueryValueExW")
	procRegCloseKey    = modAdvapi32.NewProc("RegCloseKey")
	procRegDeleteTree  = modAdvapi32.NewProc("RegDeleteTreeW")
	procRegOpenKeyEx   = modAdvapi32.NewProc("RegOpenKeyExW")
)

const (
	hkeyCurrentUser = 0x80000001
	keyAllAccess    = 0xF003F
	keyRead         = 0x20019
	regSZ           = 1
	regDWORD        = 4
)

func regSetString(keyPath, name, value string) error {
	kp, err := syscall.UTF16PtrFromString(keyPath)
	if err != nil {
		return err
	}
	var h syscall.Handle
	r, _, _ := procRegCreateKeyEx.Call(uintptr(hkeyCurrentUser),
		uintptr(unsafe.Pointer(kp)), 0, 0, 0, keyAllAccess, 0,
		uintptr(unsafe.Pointer(&h)), 0)
	if r != 0 {
		return fmt.Errorf("could not open %s for writing (code %d)", keyPath, r)
	}
	defer procRegCloseKey.Call(uintptr(h))

	n, err := syscall.UTF16PtrFromString(name)
	if err != nil {
		return err
	}
	v, err := syscall.UTF16FromString(value)
	if err != nil {
		return err
	}
	r, _, _ = procRegSetValueEx.Call(uintptr(h), uintptr(unsafe.Pointer(n)), 0,
		regSZ, uintptr(unsafe.Pointer(&v[0])), uintptr(len(v)*2))
	if r != 0 {
		return fmt.Errorf("could not write %s\\%s (code %d)", keyPath, name, r)
	}
	return nil
}

func regGetString(keyPath, name string) (string, bool) {
	kp, err := syscall.UTF16PtrFromString(keyPath)
	if err != nil {
		return "", false
	}
	var h syscall.Handle
	r, _, _ := procRegOpenKeyEx.Call(uintptr(hkeyCurrentUser),
		uintptr(unsafe.Pointer(kp)), 0, keyRead, uintptr(unsafe.Pointer(&h)))
	if r != 0 {
		return "", false
	}
	defer procRegCloseKey.Call(uintptr(h))

	n, err := syscall.UTF16PtrFromString(name)
	if err != nil {
		return "", false
	}
	buf := make([]uint16, 1024)
	size := uint32(len(buf) * 2)
	r, _, _ = procRegQueryValue.Call(uintptr(h), uintptr(unsafe.Pointer(n)), 0, 0,
		uintptr(unsafe.Pointer(&buf[0])), uintptr(unsafe.Pointer(&size)))
	if r != 0 {
		return "", false
	}
	return syscall.UTF16ToString(buf), true
}

func regDeleteTree(keyPath string) error {
	kp, err := syscall.UTF16PtrFromString(keyPath)
	if err != nil {
		return err
	}
	r, _, _ := procRegDeleteTree.Call(uintptr(hkeyCurrentUser),
		uintptr(unsafe.Pointer(kp)))
	// 2 is ERROR_FILE_NOT_FOUND: already gone is the desired end state, not a
	// failure. An uninstaller that errors because there was nothing to remove
	// teaches people to ignore its errors.
	if r != 0 && r != 2 {
		return fmt.Errorf("could not remove %s (code %d)", keyPath, r)
	}
	return nil
}

// ===========================================================================
// THE ADD/REMOVE PROGRAMS ENTRY
// ===========================================================================

// WriteUninstallEntry makes the collector appear in Settings > Apps.
//
// EVERY FIELD IS FILLED IN. An entry with no publisher and no version shows up
// as a blank row that looks like malware, which is the opposite of what this is
// for: a person who wants it gone should find something recognisable and be
// able to remove it in the ordinary way.
func WriteUninstallEntry(cfg installConfig, exe, version string) error {
	fields := [][2]string{
		{"DisplayName", "Citizen Collector"},
		{"DisplayVersion", version},
		{"Publisher", "Citizen Compass"},
		{"DisplayIcon", exe},
		{"InstallLocation", cfg.Root},
		{"UninstallString", `"` + exe + `" -uninstall`},
		{"QuietUninstallString", `"` + exe + `" -uninstall -quiet`},
		{"URLInfoAbout", "https://citizencompass.netlify.app"},
		{"NoModify", "1"},
		{"NoRepair", "1"},
	}
	for _, f := range fields {
		if err := regSetString(cfg.RegKeyPath, f[0], f[1]); err != nil {
			return err
		}
	}
	return nil
}

// RemoveUninstallEntry takes the Add/Remove Programs row away.
func RemoveUninstallEntry(cfg installConfig) error {
	return regDeleteTree(cfg.RegKeyPath)
}

// InstalledEntryExists reports whether Windows currently lists the collector.
func InstalledEntryExists(cfg installConfig) bool {
	_, ok := regGetString(cfg.RegKeyPath, "DisplayName")
	return ok
}

// ===========================================================================
// INSTALL
// ===========================================================================

// adoptFiles are the files that make an install THIS person's install.
//
// Carried across so an upgrade is the same contributor: the id keeps their data
// joining to what they have already sent, and the consent answer means they are
// not asked a second time for permission they have already given.
var adoptFiles = []string{
	"collector-install-id.txt",
	"collector-consent.txt",
	"collector-settings.txt",
	"collector-send-choice.txt",
}

// adoptDirs are the folders that hold what they have collected.
var adoptDirs = []string{"diary", "captures"}

// InstallSelf puts the program in a proper home and registers it.
//
// Returns the installed exe path and whether anything moved. Safe to call every
// run: an install that is already in place does nothing at all.
func InstallSelf(cfg installConfig, exePath string, logf func(string, ...interface{})) (string, bool, error) {
	if logf == nil {
		logf = func(string, ...interface{}) {}
	}
	if cfg.Root == "" {
		return exePath, false, fmt.Errorf("no per-user program folder is available " +
			"on this machine (LOCALAPPDATA is not set), so there is nowhere safe " +
			"to install to")
	}
	srcDir := filepath.Dir(exePath)
	dstExe := filepath.Join(cfg.Root, filepath.Base(exePath))

	// ALREADY HOME. Not an error and not a no-op-with-a-warning: this is the
	// normal case on every run after the first.
	if samePath(srcDir, cfg.Root) {
		return exePath, false, nil
	}

	if err := os.MkdirAll(cfg.Root, 0o755); err != nil {
		return exePath, false, err
	}

	// The program itself.
	if err := copyFileFresh(exePath, dstExe); err != nil {
		return exePath, false, fmt.Errorf("could not copy the collector into %s: %w",
			cfg.Root, err)
	}

	// WHAT MAKES IT THIS PERSON'S INSTALL. Copied, never moved: if anything
	// below fails the old folder is still a working collector.
	adopted := 0
	for _, name := range adoptFiles {
		src := filepath.Join(srcDir, name)
		if _, err := os.Stat(src); err != nil {
			continue
		}
		dst := filepath.Join(cfg.Root, name)
		if _, err := os.Stat(dst); err == nil {
			// NEVER OVERWRITE AN EXISTING IDENTITY. Two folder installs
			// adopting into one home must not have the second one silently
			// replace the first person's id.
			logf("install: %s already exists in the new home - keeping it", name)
			continue
		}
		if err := copyFileFresh(src, dst); err == nil {
			adopted++
		}
	}
	moved := 0
	for _, name := range adoptDirs {
		src := filepath.Join(srcDir, name)
		if st, err := os.Stat(src); err != nil || !st.IsDir() {
			continue
		}
		n, err := copyTreeFresh(src, filepath.Join(cfg.Root, name))
		if err != nil {
			logf("install: could not bring %s across (%v) - it is still in the "+
				"old folder and nothing was deleted", name, err)
			continue
		}
		moved += n
	}
	if adopted > 0 || moved > 0 {
		logf("install: adopted %d settings file(s) and %d collected file(s) from %s",
			adopted, moved, srcDir)
	}
	return dstExe, true, nil
}

// copyFileFresh copies src to dst, refusing to overwrite.
func copyFileFresh(src, dst string) error {
	in, err := os.Open(src)
	if err != nil {
		return err
	}
	defer in.Close()
	if err := os.MkdirAll(filepath.Dir(dst), 0o755); err != nil {
		return err
	}
	tmp := dst + ".part"
	out, err := os.Create(tmp)
	if err != nil {
		return err
	}
	if _, err := io.Copy(out, in); err != nil {
		out.Close()
		os.Remove(tmp)
		return err
	}
	if err := out.Close(); err != nil {
		os.Remove(tmp)
		return err
	}
	return os.Rename(tmp, dst)
}

// copyTreeFresh copies a folder, skipping anything already at the destination.
func copyTreeFresh(src, dst string) (int, error) {
	n := 0
	err := filepath.Walk(src, func(p string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		rel, rerr := filepath.Rel(src, p)
		if rerr != nil {
			return rerr
		}
		target := filepath.Join(dst, rel)
		if info.IsDir() {
			return os.MkdirAll(target, 0o755)
		}
		if _, err := os.Stat(target); err == nil {
			return nil // already there - never overwrite collected data
		}
		if err := copyFileFresh(p, target); err != nil {
			return err
		}
		n++
		return nil
	})
	return n, err
}

// ===========================================================================
// UNINSTALL
// ===========================================================================

// UninstallResult says what actually happened, so the program can tell the
// person rather than assuming.
type UninstallResult struct {
	StartupRemoved   bool
	ShortcutsRemoved int
	EntryRemoved     bool
	DataKept         bool
	DataRemoved      int
	Problems         []string
}

// UninstallSelf removes everything this program created.
//
// removeData is ASKED SEPARATELY and passed in. Removing the program must not
// silently delete somebody's diary and pictures - that is months of their own
// data - and it must not silently leave gigabytes behind either. The only
// honest version is to ask, which means the answer arrives here as a decision
// somebody made rather than a default somebody inherited.
func UninstallSelf(cfg installConfig, removeData bool,
	logf func(string, ...interface{})) UninstallResult {

	if logf == nil {
		logf = func(string, ...interface{}) {}
	}
	var res UninstallResult
	res.DataKept = !removeData

	// THE STARTUP ENTRY FIRST, because it is the one that outlives a folder
	// deletion today and the one the README currently lies about.
	if AutostartEnabled() {
		if err := DisableAutostart(); err != nil {
			res.Problems = append(res.Problems,
				"the startup entry could not be removed: "+err.Error())
		} else {
			res.StartupRemoved = true
			logf("uninstall: removed the Startup entry")
		}
	}

	// The shortcuts it created, resolved the same way the creator resolves
	// them - through the known folder, never by assembling a path by hand.
	for _, p := range shortcutPlaces() {
		dir, err := knownFolder(p.id)
		if err != nil || dir == "" {
			res.Problems = append(res.Problems,
				"could not find the "+p.label+" folder, so its shortcut may remain")
			continue
		}
		lnk := filepath.Join(dir, shortcutName+".lnk")
		if _, err := os.Stat(lnk); err != nil {
			continue
		}
		if _, err := os.Stat(lnk); err != nil {
			continue
		}
		if err := os.Remove(lnk); err != nil {
			res.Problems = append(res.Problems,
				"could not remove "+lnk+": "+err.Error())
			continue
		}
		res.ShortcutsRemoved++
	}

	// The Add/Remove Programs row.
	if err := RemoveUninstallEntry(cfg); err != nil {
		res.Problems = append(res.Problems, err.Error())
	} else {
		res.EntryRemoved = true
	}

	// The collected data, only if that is what was chosen.
	if removeData {
		for _, d := range adoptDirs {
			p := filepath.Join(cfg.Root, d)
			n := countFiles(p)
			if err := os.RemoveAll(p); err != nil {
				res.Problems = append(res.Problems,
					"could not remove "+p+": "+err.Error())
				continue
			}
			res.DataRemoved += n
		}
	}
	return res
}

func countFiles(dir string) int {
	n := 0
	_ = filepath.Walk(dir, func(_ string, info os.FileInfo, err error) error {
		if err == nil && info != nil && !info.IsDir() {
			n++
		}
		return nil
	})
	return n
}
