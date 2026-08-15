package main

// install_location.go - the program will not make its home on your Desktop.
//
// # WHAT WAS OBSERVED
//
// Photographs of Sleven's friend's Desktop, 2026-08-15:
//
//	collector            <- the EXE ITSELF, on the Desktop
//	collector-settings.txt
//	collector-auto.log
//	collector-install-id.txt
//	captures/            <- A FOLDER OF SCREENSHOTS. On his Desktop.
//
// > "every time I click it, it puts two files on there... Why the fuck is that
// > on there?"
//
// NOTHING WAS MALFUNCTIONING. The program writes its files next to itself,
// which is deliberate and good - shortcut.go argues for it in its own header:
// "deleting the folder removes everything". The exe was on the Desktop, so
// next-to-itself WAS the Desktop, and every launch wrote more into the one
// folder a person looks at all day.
//
// It was also about to get much worse than untidy. captures/ grows by roughly
// 3 MB a frame during a session.
//
// # HOW IT GOT THERE
//
// He dragged the exe out of the unzipped folder, because there was no shortcut
// and the folder was unfindable. That was the correct instinct and the program
// had given him no better option. The shortcut feature was built in response -
// but for a machine where the exe stays put. It solved the NEXT person's
// problem, not this one's.
//
// # WHY THE DATA IS NOT SIMPLY MOVED SOMEWHERE HIDDEN
//
// %LOCALAPPDATA% would end the mess in one line and is refused deliberately.
// The promise is that everything this program holds sits in one folder you can
// open, inspect and delete, and that promise is load-bearing for a tool that
// reads a game log and takes pictures of your screen. Hiding the data would
// trade a visible mess for an invisible one, and the invisible one is worse for
// consent.
//
// The problem was never where the files go. It is that the exe was allowed to
// sit somewhere that made the answer "your Desktop".

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"syscall"
	"unsafe"
)

// The known folders a program has no business living directly inside.
//
// RESOLVED WITH SHGetKnownFolderPath, never built from %USERPROFILE%. OneDrive
// redirects Desktop and Documents on a large share of consumer machines, so a
// hardcoded compare would pass on exactly the machines that need this most -
// which is the same reason shortcut.go resolves them this way.
var (
	folderIDDownloads     = GUID{0x374DE290, 0x123F, 0x4565, [8]byte{0x91, 0x64, 0x39, 0xC4, 0x92, 0x5E, 0x46, 0x7B}}
	folderIDDocuments     = GUID{0xFDD39AD0, 0x238F, 0x46AF, [8]byte{0xAD, 0xB4, 0x6C, 0x85, 0x48, 0x03, 0x69, 0xC7}}
	folderIDProfile       = GUID{0x5E6C858F, 0x0E22, 0x4760, [8]byte{0x9A, 0xFE, 0xEA, 0x33, 0x17, 0xB6, 0x71, 0x73}}
	folderIDPublicDesktop = GUID{0xC4AA340D, 0xF20F, 0x4863, [8]byte{0xAF, 0xEF, 0xF8, 0x7E, 0xF2, 0xE6, 0xBA, 0x25}}
)

// knownFolderPlace pairs a folder with the words a person would use for it.
type knownFolderPlace struct {
	id    GUID
	label string
}

func homelessPlaces() []knownFolderPlace {
	return []knownFolderPlace{
		{folderIDDesktop, "Desktop"},
		{folderIDPublicDesktop, "shared Desktop"},
		{folderIDDownloads, "Downloads folder"},
		{folderIDDocuments, "Documents folder"},
		{folderIDProfile, "user folder"},
	}
}

// samePath compares two directories as Windows would.
//
// Case-insensitive, and trailing separators do not count. Comparing the raw
// strings would miss "C:\Users\x\Desktop" against "C:\Users\X\Desktop\", and a
// guard that can be defeated by a capital letter is decoration.
func samePath(a, b string) bool {
	clean := func(s string) string {
		s = strings.TrimSpace(s)
		if s == "" {
			return ""
		}
		s = filepath.Clean(s)
		return strings.ToLower(strings.TrimRight(s, `\/`))
	}
	ca, cb := clean(a), clean(b)
	return ca != "" && ca == cb
}

// IsHomelessInstall reports whether dir IS one of the folders a program must
// not live directly inside, and what a person calls it.
//
// DIRECTLY INSIDE, not underneath. `Desktop\Citizen Collector\` is a perfectly
// good home and is exactly what the fix creates; refusing that would refuse the
// solution along with the problem.
func IsHomelessInstall(dir string) (bool, string) {
	for _, p := range homelessPlaces() {
		known, err := knownFolder(p.id)
		if err != nil || known == "" {
			// A folder that cannot be resolved is not evidence of anything. It
			// must not read as "safe" and it must not read as "homeless".
			continue
		}
		if samePath(dir, known) {
			return true, p.label
		}
	}
	return false, ""
}

// collectorFiles lists what belongs to this install and lives beside the exe.
//
// Named by pattern rather than hardcoded, because the set has grown four times
// and a list that goes stale would leave files behind - which is the one
// outcome worse than not moving at all.
func collectorFiles(dir, exeName string) []string {
	var out []string
	entries, err := os.ReadDir(dir)
	if err != nil {
		return nil
	}
	for _, e := range entries {
		name := e.Name()
		low := strings.ToLower(name)
		switch {
		case strings.EqualFold(name, exeName):
			continue // the exe moves last, on its own
		case strings.HasPrefix(low, "collector-"),
			strings.HasPrefix(low, "citizen-collector"),
			low == "captures",
			low == "collector.exe.old",
			low == "wrangler.toml":
			out = append(out, name)
		}
	}
	return out
}

// MoveInstallInto moves this install into dst, data first and the exe last.
//
// # WHY THE ORDER IS THIS WAY ROUND
//
// A move of many files cannot be atomic. What it can be is RECOVERABLE, and the
// order decides what an interrupted move leaves behind:
//
//	EXE FIRST  -> the new folder has a program and none of its data. The next
//	              run looks like a fresh install: no consent answer, no install
//	              id, and the person is asked to agree to everything again while
//	              their old data sits on the Desktop.
//	DATA FIRST -> the exe is still in the old place with its data gone. The next
//	              launch of it lands here again, sees the same known folder, and
//	              finishes the move into the same destination.
//
// So data first. The guard firing a second time IS the recovery, which is why
// the destination is a deterministic path rather than a new folder each time -
// a second attempt must land on top of the first, not beside it.
//
// NOTHING IS EVER DELETED. Files are moved. A name that already exists at the
// destination means that file has already been moved, so the source is left
// alone and reported rather than overwritten.
func MoveInstallInto(srcDir, dstDir, exePath string, logf func(string, ...interface{})) error {
	if logf == nil {
		logf = func(string, ...interface{}) {}
	}
	if err := os.MkdirAll(dstDir, 0o755); err != nil {
		return fmt.Errorf("could not create %s: %w", dstDir, err)
	}

	exeName := filepath.Base(exePath)
	moved, skipped := 0, 0

	for _, name := range collectorFiles(srcDir, exeName) {
		from := filepath.Join(srcDir, name)
		to := filepath.Join(dstDir, name)
		if _, err := os.Stat(to); err == nil {
			// Already there from an interrupted attempt. Leave the source; do
			// not overwrite somebody's data with somebody's data.
			skipped++
			continue
		}
		if err := os.Rename(from, to); err != nil {
			return fmt.Errorf("could not move %s: %w", name, err)
		}
		moved++
	}

	// THE EXE LAST, and Windows permits renaming a running image - the same
	// property update.go relies on to replace itself.
	dstExe := filepath.Join(dstDir, exeName)
	if !samePath(filepath.Dir(exePath), dstDir) {
		if _, err := os.Stat(dstExe); err != nil {
			if err := os.Rename(exePath, dstExe); err != nil {
				return fmt.Errorf("could not move the program itself: %w", err)
			}
		}
	}
	logf("install: moved %d file(s) into %s (%d already there)", moved, dstDir, skipped)
	return nil
}

// homelessMessage is what the person reads. It names the files, because "the
// program writes files next to itself" means nothing to somebody looking at a
// cluttered Desktop.
func homelessMessage(place, dir, dstDir string, files []string) string {
	var b strings.Builder
	fmt.Fprintf(&b, "Citizen Collector is sitting directly in your %s.\n\n", place)
	b.WriteString("It keeps everything it makes in the same folder as itself, so " +
		"right now that folder is your " + place + ". It has already put these there:\n\n")

	shown := files
	if len(shown) > 8 {
		shown = shown[:8]
	}
	for _, f := range shown {
		b.WriteString("    " + f + "\n")
	}
	if len(files) > len(shown) {
		fmt.Fprintf(&b, "    ...and %d more\n", len(files)-len(shown))
	}
	b.WriteString("\nThe captures folder holds screenshots and grows by a few " +
		"megabytes every time it takes one, so this gets worse the more you play.\n\n")
	b.WriteString("Move it into its own folder?\n\n    " + dstDir + "\n\n")
	b.WriteString("Yes  - move the program and all of the files above into that " +
		"folder, fix the shortcut, and start.\nNo   - do nothing and close. " +
		"Nothing is deleted either way.")
	return b.String()
}

// GuardInstallLocation refuses to run from a known folder, and offers the fix.
//
// Returns true when the caller should STOP - either the person declined, or the
// install was moved and a new process has been started from the new location.
//
// Called before the log is opened, deliberately: the log lives beside the exe,
// so opening it first would put one more file on the Desktop while deciding
// whether to put files on the Desktop.
func GuardInstallLocation(exeDir string, logf func(string, ...interface{})) bool {
	if logf == nil {
		logf = func(string, ...interface{}) {}
	}
	homeless, place := IsHomelessInstall(exeDir)
	if !homeless {
		// A normal install is untouched and sees nothing. No dialog, no move,
		// no line in the log - the overwhelmingly common case stays silent.
		return false
	}

	exe, err := os.Executable()
	if err != nil {
		return false
	}
	files := collectorFiles(exeDir, filepath.Base(exe))
	dstDir := filepath.Join(exeDir, "Citizen Collector")

	const (
		mbYesNo       = 0x00000004
		mbIconWarning = 0x00000030
		idYes         = 6
	)
	proc := modUser32.NewProc("MessageBoxW")
	title, _ := syscall.UTF16PtrFromString("Citizen Collector")
	msg, _ := syscall.UTF16PtrFromString(homelessMessage(place, exeDir, dstDir, files))
	r, _, _ := proc.Call(0,
		uintptr(unsafe.Pointer(msg)), uintptr(unsafe.Pointer(title)),
		uintptr(mbYesNo|mbIconWarning))

	if int(r) != idYes {
		// Declined. Stop rather than start - starting would write the very
		// files the person just declined to have moved.
		return true
	}

	if err := MoveInstallInto(exeDir, dstDir, exe, logf); err != nil {
		showErrorBox("Citizen Collector",
			"The move could not be finished, so nothing was changed on purpose:\n\n"+
				err.Error()+"\n\nEverything is still where it was. Nothing was deleted.")
		return true
	}

	// THE SHORTCUT MUST POINT AT THE EXE THAT EXISTS.
	//
	// A .lnk aimed at a path that has moved goes blank, and this has just moved
	// it. Rewritten rather than assumed - shortcut.go's own header counts six
	// silent successes on this project.
	newExe := filepath.Join(dstDir, filepath.Base(exe))
	fixShortcutsFor(newExe, dstDir, logf)

	// Start from the new location and let this process go.
	if err := startDetached(newExe, dstDir); err != nil {
		showErrorBox("Citizen Collector",
			"Everything was moved into:\n\n"+dstDir+
				"\n\nbut it could not be started automatically. Open that folder and "+
				"run Citizen Collector from there.")
	}
	return true
}

// startDetached launches the moved copy so the person does not have to.
//
// The whole point of the one click is that it finishes the job. Telling somebody
// "now go and find the folder and run it again" hands the last step back to the
// person who did not build this - which is how the exe ended up on the Desktop
// in the first place.
func startDetached(exe, workDir string) error {
	cmd := exec.Command(exe)
	cmd.Dir = workDir
	return cmd.Start()
}

// fixShortcutsFor repoints existing shortcuts at a moved executable.
func fixShortcutsFor(exe, workDir string, logf func(string, ...interface{})) {
	for _, t := range shortcutPlaces() {
		dir, err := knownFolder(t.id)
		if err != nil {
			continue
		}
		lnk := filepath.Join(dir, shortcutName+".lnk")
		if _, err := os.Stat(lnk); err != nil {
			continue
		}
		if err := CreateShortcut(lnk, exe, workDir,
			"Records what Star Citizen already writes down, so the community can map prices and places.",
			exe); err != nil {
			logf("shortcut: could not repoint the %s shortcut after the move (%v)", t.label, err)
			continue
		}
		logf("shortcut: repointed the %s shortcut at the new location", t.label)
	}
}
