package main

// selfinstall_selftest.go - prove the install, and prove the REFUSALS.
//
// ===========================================================================
// THIS RUNS IN A THROWAWAY PREFIX, ON PURPOSE
// ===========================================================================
//
// Every check below uses a temp root and a scratch registry key under
// HKCU\Software\CitizenCompassTest. Nothing here writes to the real Start menu,
// the real desktop, %LOCALAPPDATA%\Programs, or the real Add/Remove Programs
// entry. Hard rule 6 says I ask before writing outside the repo, and I asked
// about the real prefix and have not been answered - so the mechanism is proved
// where it can be proved without leaving anything on somebody's machine.
//
// WHAT THAT DOES NOT PROVE, stated rather than glossed: that a shortcut appears
// on Sleven's real desktop and that Settings > Apps shows the entry. Those need
// a person, exactly like the tray menu.

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"
)

const testRegKey = `Software\CitizenCompassTest\Uninstall\CitizenCollector`

func runSelfInstallSelftest(check func(name string, ok bool, detail string)) {
	// ---- 1. THE TEMP / ARCHIVE REFUSAL --------------------------------
	//
	// The failure it prevents is silent and total, so it is checked with the
	// paths Windows actually produces rather than with something invented.
	for _, c := range []struct {
		dir  string
		want bool
		why  string
	}{
		{`C:\Users\dave\AppData\Local\Temp\Temp1_citizen-collector.zip`, true,
			"the zip-preview folder, which is the one that actually happens"},
		{`C:\Users\dave\AppData\Local\Temp`, true, "the temp folder itself"},
		{`C:\Users\dave\AppData\Local\Temp\rar$abc\collector`, true,
			"underneath the temp folder"},
		{`C:\Users\dave\Downloads\collector.zip\citizen-collector`, true,
			"inside an archive, unpacked in place"},
		{`C:\Users\dave\AppData\Local\Programs\CitizenCollector`, false,
			"the real install location must NOT be refused"},
		{`C:\Users\dave\Desktop\Citizen Collector`, false,
			"a folder on the desktop is a fine home and must not be refused"},
		{`D:\Games\CitizenCollector`, false, "another drive is fine"},
	} {
		got, why := IsTempOrArchivePath(c.dir)
		check(fmt.Sprintf("install: %q is %srefused", c.dir,
			map[bool]string{true: "", false: "NOT "}[c.want]),
			got == c.want,
			fmt.Sprintf("got refused=%v (%s) - %s", got, why, c.why))
	}

	// ---- 2. INSTALL, ADOPT, AND NEVER OVERWRITE -----------------------
	tmp, err := os.MkdirTemp("", "selfinstall-")
	if err != nil {
		check("install: temp dir", false, err.Error())
		return
	}
	defer os.RemoveAll(tmp)

	oldDir := filepath.Join(tmp, "Desktop", "Citizen Collector")
	newRoot := filepath.Join(tmp, "Programs", "CitizenCollector")
	if err := os.MkdirAll(oldDir, 0o755); err != nil {
		check("install: fixture dirs", false, err.Error())
		return
	}
	// A folder install as it exists today: the exe, an identity, a consent
	// answer, and what has been collected.
	fakeExe := filepath.Join(oldDir, "collector.exe")
	writeAll := map[string]string{
		fakeExe: "MZ fake",
		filepath.Join(oldDir, "collector-install-id.txt"):  "install-7c2f",
		filepath.Join(oldDir, "collector-consent.txt"):     "yes 2026-08-01",
		filepath.Join(oldDir, "captures", "shot_0001.png"): "png",
		filepath.Join(oldDir, "diary", "20260818.log.gz"):  "gz",
	}
	for p, body := range writeAll {
		_ = os.MkdirAll(filepath.Dir(p), 0o755)
		if err := os.WriteFile(p, []byte(body), 0o644); err != nil {
			check("install: fixture files", false, err.Error())
			return
		}
	}

	cfg := installConfig{Root: newRoot, RegKeyPath: testRegKey, Shortcuts: false}
	newExe, moved, err := InstallSelf(cfg, fakeExe, nil)
	check("install: the program is copied into a proper home",
		err == nil && moved && strings.HasPrefix(newExe, newRoot),
		fmt.Sprintf("err=%v moved=%v newExe=%q", err, moved, newExe))

	readOr := func(p string) string {
		b, err := os.ReadFile(p)
		if err != nil {
			return ""
		}
		return string(b)
	}
	check("install: the contributor's id comes with it - SAME contributor",
		readOr(filepath.Join(newRoot, "collector-install-id.txt")) == "install-7c2f",
		"a new id would make their data stop joining to what they have already sent")
	check("install: their consent answer comes with it - NOT asked twice",
		readOr(filepath.Join(newRoot, "collector-consent.txt")) == "yes 2026-08-01",
		"they would be asked to agree to something they already agreed to")
	check("install: the pictures come with it",
		readOr(filepath.Join(newRoot, "captures", "shot_0001.png")) == "png",
		"months of somebody's captures left behind in a folder they will delete")
	check("install: the diary comes with it",
		readOr(filepath.Join(newRoot, "diary", "20260818.log.gz")) == "gz",
		"the whole point of keeping session logs is that they survive")

	// NEVER OVERWRITE AN EXISTING IDENTITY. Two folder installs adopting into
	// one home must not have the second silently replace the first.
	second := filepath.Join(tmp, "Downloads", "Citizen Collector")
	_ = os.MkdirAll(second, 0o755)
	secondExe := filepath.Join(second, "collector.exe")
	_ = os.WriteFile(secondExe, []byte("MZ fake"), 0o644)
	_ = os.WriteFile(filepath.Join(second, "collector-install-id.txt"),
		[]byte("install-OTHER"), 0o644)
	if _, _, err := InstallSelf(cfg, secondExe, nil); err != nil {
		check("install: a second folder install can be adopted", false, err.Error())
	}
	check("install: NEGATIVE CONTROL - a second install does NOT overwrite the id",
		readOr(filepath.Join(newRoot, "collector-install-id.txt")) == "install-7c2f",
		"the first contributor's identity was replaced by the second's")

	// AND AN ALREADY-INSTALLED COPY DOES NOTHING.
	_, moved2, err2 := InstallSelf(cfg, newExe, nil)
	check("install: running from the installed location is a no-op",
		err2 == nil && !moved2,
		fmt.Sprintf("moved=%v err=%v - it would copy itself on every launch",
			moved2, err2))

	// ---- 3. THE ADD/REMOVE PROGRAMS ENTRY -----------------------------
	//
	// Written to a scratch key, then read back through the same API a person's
	// Settings app would use.
	if err := WriteUninstallEntry(cfg, newExe, "9.9.9"); err != nil {
		check("install: the Add/Remove Programs entry is written", false, err.Error())
	} else {
		name, ok := regGetString(cfg.RegKeyPath, "DisplayName")
		ver, _ := regGetString(cfg.RegKeyPath, "DisplayVersion")
		un, _ := regGetString(cfg.RegKeyPath, "UninstallString")
		check("install: the Add/Remove Programs entry is written and readable",
			ok && name == "Citizen Collector" && ver == "9.9.9",
			fmt.Sprintf("name=%q version=%q", name, ver))
		check("install: and it says how to uninstall, pointing at the installed exe",
			strings.Contains(un, "-uninstall") && strings.Contains(un, newRoot),
			"UninstallString is "+un)
		check("install: NEGATIVE CONTROL - a key that was never written reads as absent",
			!func() bool {
				_, ok := regGetString(cfg.RegKeyPath+`\NoSuchThing`, "DisplayName")
				return ok
			}(),
			"the registry reader answers yes to everything, so the check above "+
				"proves nothing")
	}

	// ---- 4. UNINSTALL ------------------------------------------------
	//
	// THE ONE THAT MATTERS: the startup entry goes with it. Today "delete the
	// folder" leaves a Startup shortcut pointing at nothing while the README
	// says nothing is left behind - so this is proved by EFFECT, in a
	// disposable Startup folder rather than the real one.
	fakeStartup := filepath.Join(tmp, "Startup")
	_ = os.MkdirAll(fakeStartup, 0o755)
	autostartDirOverride = fakeStartup
	defer func() { autostartDirOverride = "" }()

	if err := EnableAutostart(newExe, newRoot); err != nil {
		check("uninstall: could not set up the startup entry to remove", false,
			err.Error())
	}
	check("uninstall: the startup entry EXISTS before uninstalling",
		AutostartEnabled(),
		"the removal check below would pass on a machine that never had one, "+
			"which is exactly the shape of a check that cannot fail")

	res := UninstallSelf(cfg, false, nil)
	check("uninstall: THE STARTUP ENTRY GOES WITH IT",
		res.StartupRemoved && !AutostartEnabled(),
		fmt.Sprintf("removed=%v still enabled=%v - today deleting the folder "+
			"leaves this pointing at nothing while the README says nothing is "+
			"left behind", res.StartupRemoved, AutostartEnabled()))

	check("uninstall: the Add/Remove Programs entry is removed",
		res.EntryRemoved && !InstalledEntryExists(cfg),
		fmt.Sprintf("removed=%v still there=%v", res.EntryRemoved,
			InstalledEntryExists(cfg)))
	check("uninstall: collected data is KEPT when that is the answer",
		res.DataKept && readOr(filepath.Join(newRoot, "diary", "20260818.log.gz")) == "gz",
		"somebody's session logs were deleted by a question they answered no to")
	check("uninstall: and the pictures are still there too",
		readOr(filepath.Join(newRoot, "captures", "shot_0001.png")) == "png",
		"the data question was not honoured")

	// AND THE OTHER ANSWER ACTUALLY REMOVES IT, or "keep" is not a choice, it
	// is the only behaviour with a prompt in front of it.
	res2 := UninstallSelf(cfg, true, nil)
	check("uninstall: NEGATIVE CONTROL - answering yes DOES remove the data",
		!res2.DataKept && res2.DataRemoved >= 2 &&
			readOr(filepath.Join(newRoot, "diary", "20260818.log.gz")) == "",
		fmt.Sprintf("removed %d file(s); the diary is %q", res2.DataRemoved,
			readOr(filepath.Join(newRoot, "diary", "20260818.log.gz"))))

	// Removing an entry that is already gone is the desired end state, not an
	// error - an uninstaller that complains when there is nothing to remove
	// teaches people to ignore its errors.
	res3 := UninstallSelf(cfg, false, nil)
	check("uninstall: running it twice is not an error",
		len(res3.Problems) == 0,
		fmt.Sprintf("problems: %v", res3.Problems))

	_ = regDeleteTree(`Software\CitizenCompassTest`)
}
