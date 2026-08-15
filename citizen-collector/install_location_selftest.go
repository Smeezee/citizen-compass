package main

// install_location_selftest.go - the guard must refuse a Desktop and allow
// everywhere else.
//
// Both directions are load-bearing and they fail in opposite ways. A guard that
// never refuses leaves somebody's Desktop filling with screenshots. A guard that
// refuses too readily is worse: it stops a working install from starting, on a
// machine nobody is watching, with a dialog the person cannot get past.
//
// Sleven's own install is in its proper folder and must see none of this.

import (
	"os"
	"path/filepath"
	"strings"
)

func runInstallLocationSelftest(check func(name string, ok bool, detail string)) {

	// -----------------------------------------------------------------
	// 1. THE REAL KNOWN FOLDERS ARE REFUSED
	// -----------------------------------------------------------------
	//
	// Pointed at the actual Desktop of the machine running this, resolved the
	// same way the guard resolves it. A guard only ever observed allowing things
	// is not a guard.
	desktop, dErr := knownFolder(folderIDDesktop)
	if dErr == nil && desktop != "" {
		homeless, place := IsHomelessInstall(desktop)
		check("LOCATION: the real Desktop IS refused",
			homeless && place != "",
			"an exe sitting on the Desktop would have been allowed to run: "+desktop)

		// THE REDIRECTED CASE, reported honestly either way.
		//
		// OneDrive moves Desktop on a large share of consumer machines, and a
		// guard built on %USERPROFILE%\Desktop would pass on exactly those. This
		// machine can only demonstrate the case it actually has.
		if strings.Contains(strings.ToLower(desktop), "onedrive") {
			check("LOCATION: a OneDrive-REDIRECTED Desktop is refused", homeless,
				"redirected to "+desktop+" - the case a %USERPROFILE% compare would miss")
		} else {
			check("LOCATION: redirected-Desktop case NOT EXERCISED here", true,
				"this machine's Desktop is "+desktop+", which is not redirected. The "+
					"guard resolves it with SHGetKnownFolderPath rather than building "+
					"a path, so redirection is handled by construction - but it was "+
					"NOT observed on this machine and this line is not a pass for it.")
		}

		// THE DESTINATION THE FIX CREATES MUST BE ALLOWED.
		//
		// Without this, the guard would refuse its own solution and the program
		// could never start after being moved - a loop with a dialog in it.
		inner := filepath.Join(desktop, "Citizen Collector")
		notHomeless, _ := IsHomelessInstall(inner)
		check("LOCATION: a folder UNDER the Desktop is allowed",
			!notHomeless,
			"the guard refuses the very folder the one-click fix moves into: "+inner)
	}

	for _, p := range []struct {
		id    GUID
		label string
	}{
		{folderIDDownloads, "Downloads"},
		{folderIDProfile, "the user folder"},
	} {
		if dir, err := knownFolder(p.id); err == nil && dir != "" {
			h, _ := IsHomelessInstall(dir)
			check("LOCATION: "+p.label+" IS refused", h,
				"observed twice on Sleven's friend's machine - Desktop, then Downloads: "+dir)
		}
	}

	// -----------------------------------------------------------------
	// 2. NEGATIVE CONTROL - A NORMAL INSTALL IS UNTOUCHED
	// -----------------------------------------------------------------
	//
	// Without this, "refuses to run on the Desktop" would also pass on a build
	// that refuses to run anywhere.
	tmp, err := os.MkdirTemp("", "cc-location")
	if err != nil {
		check("LOCATION: could not make a temp folder to test in", false, err.Error())
		return
	}
	defer os.RemoveAll(tmp)

	h, _ := IsHomelessInstall(tmp)
	check("LOCATION: NEGATIVE CONTROL - an ordinary folder is allowed", !h,
		"a normal install would be blocked from starting: "+tmp)

	check("LOCATION: NEGATIVE CONTROL - this collector's own folder is allowed",
		func() bool { d, _ := os.Executable(); hh, _ := IsHomelessInstall(filepath.Dir(d)); return !hh }(),
		"the machine running this selftest would be refused by its own guard")

	// -----------------------------------------------------------------
	// 3. PATH COMPARISON
	// -----------------------------------------------------------------
	check("LOCATION: a trailing slash does not defeat the compare",
		samePath(`C:\Users\x\Desktop`, `C:\Users\x\Desktop\`),
		"a guard defeated by a trailing separator is decoration")
	check("LOCATION: capitalisation does not defeat the compare",
		samePath(`c:\users\X\desktop`, `C:\Users\x\Desktop`),
		"Windows paths are case-insensitive; the guard must be too")
	check("LOCATION: NEGATIVE CONTROL - different folders are not equal",
		!samePath(`C:\Users\x\Desktop`, `C:\Users\x\Desktop\Citizen Collector`),
		"a comparer that said yes to everything would refuse every folder")
	check("LOCATION: NEGATIVE CONTROL - an empty path matches nothing",
		!samePath("", "") && !samePath("", `C:\Users\x\Desktop`),
		"an unresolvable folder must not read as a match")

	// -----------------------------------------------------------------
	// 4. THE MOVE, AND WHAT AN INTERRUPTED ONE LEAVES
	// -----------------------------------------------------------------
	src := filepath.Join(tmp, "fake-desktop")
	_ = os.MkdirAll(filepath.Join(src, "captures"), 0o755)
	fakeExe := filepath.Join(src, "collector.exe")
	for _, f := range []string{
		"collector.exe", "collector-settings.txt", "collector-auto.log",
		"collector-install-id.txt", "collector-consent.txt",
	} {
		_ = os.WriteFile(filepath.Join(src, f), []byte("x"), 0o644)
	}
	_ = os.WriteFile(filepath.Join(src, "captures", "shot_0001.png"), []byte("png"), 0o644)
	// Something that is NOT ours must be left exactly where it is.
	_ = os.WriteFile(filepath.Join(src, "somebody-elses-homework.docx"), []byte("mine"), 0o644)

	// ASSERTED BY MEMBERSHIP, NOT BY COUNT. The first version of this checked
	// len(found) == 4 against a fixture that has five items, so it failed on a
	// correct result. A count is also the wrong assertion in principle: this
	// list is expected to grow, and a test that breaks every time a new
	// collector-* file appears teaches people to adjust the number rather than
	// look at what moved.
	found := collectorFiles(src, "collector.exe")
	missing := []string{}
	for _, want := range []string{
		"captures", "collector-settings.txt", "collector-auto.log",
		"collector-install-id.txt", "collector-consent.txt",
	} {
		if !contains(found, want) {
			missing = append(missing, want)
		}
	}
	check("LOCATION: the file list finds every data file and the captures folder",
		len(missing) == 0,
		"left behind: "+strings.Join(missing, ", ")+" (found: "+strings.Join(found, ", ")+")")
	check("LOCATION: the file list does NOT claim the exe (it moves last, separately)",
		!contains(found, "collector.exe"),
		"the exe must move after its data, or an interrupt strands the consent answer")
	check("LOCATION: NEGATIVE CONTROL - unrelated files are not swept up",
		!contains(found, "somebody-elses-homework.docx"),
		"this moves files on somebody else's computer; taking the wrong ones is unforgivable")

	dst := filepath.Join(tmp, "fake-desktop", "Citizen Collector")
	if err := MoveInstallInto(src, dst, fakeExe, nil); err != nil {
		check("LOCATION: the install can be moved", false, err.Error())
		return
	}
	check("LOCATION: the install can be moved", true, "into "+dst)

	for _, f := range []string{"collector.exe", "collector-settings.txt", "collector-consent.txt"} {
		_, e := os.Stat(filepath.Join(dst, f))
		check("LOCATION: "+f+" arrived", e == nil, "missing from the destination")
	}
	_, e := os.Stat(filepath.Join(dst, "captures", "shot_0001.png"))
	check("LOCATION: the captures folder came with its contents", e == nil,
		"screenshots left behind on the Desktop")

	_, e = os.Stat(filepath.Join(src, "somebody-elses-homework.docx"))
	check("LOCATION: NEGATIVE CONTROL - the unrelated file was left where it was",
		e == nil, "a file that is not ours was moved off somebody's Desktop")

	// AN INTERRUPTED MOVE LEAVES ONE INSTALL, NOT TWO.
	//
	// Staged exactly as an interrupt would leave it: data already moved, exe
	// still behind. Running the move again must finish the job rather than
	// produce a second copy - which is why the destination is deterministic.
	src2 := filepath.Join(tmp, "fake-desktop-2")
	dst2 := filepath.Join(src2, "Citizen Collector")
	_ = os.MkdirAll(dst2, 0o755)
	exe2 := filepath.Join(src2, "collector.exe")
	_ = os.WriteFile(exe2, []byte("x"), 0o644)
	_ = os.WriteFile(filepath.Join(dst2, "collector-settings.txt"), []byte("already moved"), 0o644)
	_ = os.WriteFile(filepath.Join(src2, "collector-auto.log"), []byte("not yet"), 0o644)

	if err := MoveInstallInto(src2, dst2, exe2, nil); err != nil {
		check("LOCATION: an interrupted move can be resumed", false, err.Error())
	} else {
		_, exeLeft := os.Stat(exe2)
		_, logLeft := os.Stat(filepath.Join(src2, "collector-auto.log"))
		_, exeThere := os.Stat(filepath.Join(dst2, "collector.exe"))
		_, logThere := os.Stat(filepath.Join(dst2, "collector-auto.log"))
		check("LOCATION: resuming an interrupted move leaves ONE install",
			exeLeft != nil && logLeft != nil && exeThere == nil && logThere == nil,
			"after resuming, files are in both places - the person has two half-installs")

		body, _ := os.ReadFile(filepath.Join(dst2, "collector-settings.txt"))
		check("LOCATION: resuming does not overwrite what already moved",
			string(body) == "already moved",
			"the resumed move clobbered a file that had already arrived")
	}
}

func contains(ss []string, want string) bool {
	for _, s := range ss {
		if strings.EqualFold(s, want) {
			return true
		}
	}
	return false
}
