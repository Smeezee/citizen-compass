package main

// selfinstall_run.go - the first run, and the last one.
//
// selfinstall.go is the mechanism. This is where it meets a person: what
// happens when somebody double-clicks the file they downloaded, and what
// happens when they choose Uninstall in Settings > Apps.
//
// BOTH PATHS TELL THEM WHAT HAPPENED. A program that silently relocates itself
// is indistinguishable from one that failed to start, and an uninstaller that
// says nothing leaves somebody wondering whether their pictures went with it.

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"syscall"
)

const (
	mbOK          = 0x00000000
	mbYesNo       = 0x00000004
	mbYesNoCancel = 0x00000003
	mbIconWarn    = 0x00000030
	mbIconInfo    = 0x00000040
	mbIconError   = 0x00000010
	idYes         = 6
	idNo          = 7
	idCancel      = 2
)

// messageBox lives in send_mode.go - one place a modal question is asked.

// RefuseTempOrArchive stops the program dead when it is running from somewhere
// Windows will wipe.
//
// IT REFUSES RATHER THAN RELOCATES. Copying itself out of a zip preview and
// carrying on would work, and it would also mean the person never learns that
// what they did does not work - so the next download, and the one after, goes
// the same way. The message names the fix, and the fix is one drag.
//
// Returns true if the caller should stop.
func RefuseTempOrArchive(exeDir string, logf func(string, ...interface{})) bool {
	bad, why := IsTempOrArchivePath(exeDir)
	if !bad {
		return false
	}
	if logf != nil {
		logf("REFUSING TO RUN: %s is %s", exeDir, why)
	}
	messageBox("Citizen Collector",
		"This is running "+why+".\r\n\r\n"+
			"Windows deletes that folder without asking, and everything the "+
			"collector saves - your pictures and your session diary - would go "+
			"with it. You would not be told.\r\n\r\n"+
			"Please drag Citizen Collector out of the zip to a real folder "+
			"first - your Desktop is fine - and run it from there.\r\n\r\n"+
			"Nothing has been saved and nothing has been changed.",
		mbOK|mbIconWarn)
	return true
}

// FirstRunInstall puts the program in a proper home and registers it.
//
// ASKED, NOT ASSUMED, the first time. It moves somebody's program and puts
// entries in their Start menu; doing that silently is the behaviour of software
// people uninstall on principle. After the first time it is silent, because
// there is nothing left to ask.
//
// Returns true if the caller should exit - the installed copy has been started
// and this one is finished.
func FirstRunInstall(exeDir string, logf func(string, ...interface{})) bool {
	if logf == nil {
		logf = func(string, ...interface{}) {}
	}
	cfg := defaultInstallConfig()
	if cfg.Root == "" {
		logf("install: no per-user program folder on this machine - carrying on " +
			"from where the file is")
		return false
	}
	exe, err := os.Executable()
	if err != nil {
		return false
	}
	if samePath(filepath.Dir(exe), cfg.Root) {
		// Already installed. Keep the registration honest - a person who
		// deleted the Add/Remove entry, or upgraded from a build that never
		// wrote one, should still be able to remove this properly.
		if !InstalledEntryExists(cfg) {
			if err := WriteUninstallEntry(cfg, exe, Version); err != nil {
				logf("install: could not write the Add/Remove Programs entry (%v)", err)
			} else {
				logf("install: restored the Add/Remove Programs entry")
			}
		}
		return false
	}

	answer := messageBox("Citizen Collector",
		"Install Citizen Collector for you?\r\n\r\n"+
			"It will be copied to your own program folder, added to the Start "+
			"menu, and listed in Add or remove programs so you can remove it "+
			"the normal way later.\r\n\r\n"+
			"No administrator rights are needed and nothing outside your own "+
			"account is touched.\r\n\r\n"+
			"Anything you have already collected in this folder comes with it.",
		mbYesNo|mbIconInfo)
	if answer != idYes {
		logf("install: the person said no - running from %s", exeDir)
		Activity("Left where it is, as you asked. It will keep working from here.")
		return false
	}

	newExe, moved, err := InstallSelf(cfg, exe, logf)
	if err != nil {
		logf("install: FAILED (%v) - carrying on from where the file is", err)
		messageBox("Citizen Collector",
			"Citizen Collector could not install itself:\r\n\r\n"+err.Error()+
				"\r\n\r\nIt will keep running from where it is, and nothing has "+
				"been lost.", mbOK|mbIconWarn)
		return false
	}
	if !moved {
		return false
	}

	if err := WriteUninstallEntry(cfg, newExe, Version); err != nil {
		logf("install: the Add/Remove Programs entry could not be written (%v)", err)
	}
	if cfg.Shortcuts {
		makeInstalledShortcuts(newExe, cfg.Root, logf)
	}

	// THE OLD FOLDER'S STARTUP ENTRY GOES NOW.
	//
	// Leaving it would mean two collectors: the Startup shortcut pointing at the
	// old copy and the Start menu pointing at the new one. Exactly one collector
	// afterwards is the requirement, and this is the line that keeps it.
	if AutostartEnabled() {
		if err := DisableAutostart(); err != nil {
			logf("install: could not remove the old startup entry (%v)", err)
		} else if err := EnableAutostart(newExe, cfg.Root); err != nil {
			logf("install: the startup entry was removed but not re-created (%v)", err)
		} else {
			logf("install: the startup entry now points at the installed copy")
		}
	}

	logf("install: installed to %s", cfg.Root)
	messageBox("Citizen Collector",
		"Citizen Collector is installed.\r\n\r\n"+
			"It is in your Start menu, and in Add or remove programs when you "+
			"want it gone.\r\n\r\n"+
			"It is starting now. You can delete the file you downloaded.",
		mbOK|mbIconInfo)

	if err := startDetached(newExe, cfg.Root); err != nil {
		logf("install: could not start the installed copy (%v)", err)
		messageBox("Citizen Collector",
			"Citizen Collector is installed, but could not start itself:\r\n\r\n"+
				err.Error()+"\r\n\r\nOpen it from the Start menu.",
			mbOK|mbIconWarn)
	}
	return true
}

func makeInstalledShortcuts(exe, workDir string, logf func(string, ...interface{})) {
	for _, p := range shortcutPlaces() {
		dir, err := knownFolder(p.id)
		if err != nil || dir == "" {
			logf("install: could not find the %s folder - no shortcut there", p.label)
			continue
		}
		lnk := filepath.Join(dir, shortcutName+".lnk")
		if err := CreateShortcut(lnk, exe, workDir,
			"Citizen Collector", exe); err != nil {
			logf("install: could not create the %s shortcut (%v)", p.label, err)
			continue
		}
		logf("install: %s shortcut created", p.label)
	}
}

// RunUninstall is what Add/Remove Programs calls.
//
// THE DATA QUESTION IS SEPARATE AND IT IS ASKED SECOND. Somebody removing a
// program has decided about the program, not about the months of pictures and
// session logs it collected. Bundling the two into one Yes is how people lose
// things they meant to keep - and defaulting to keeping it silently is how a
// machine ends up with gigabytes nobody can account for.
func RunUninstall(quiet bool, logf func(string, ...interface{})) int {
	if logf == nil {
		logf = func(string, ...interface{}) {}
	}
	cfg := defaultInstallConfig()

	if !quiet {
		if messageBox("Citizen Collector",
			"Remove Citizen Collector from this computer?\r\n\r\n"+
				"This removes the program, its Start menu and desktop shortcuts, "+
				"and stops it starting with Windows.",
			mbYesNo|mbIconWarn) != idYes {
			return 0
		}
	}

	// THE SECOND QUESTION, and it says what is at stake in numbers rather than
	// in the word "data".
	removeData := false
	if !quiet {
		pics := countFiles(filepath.Join(cfg.Root, "captures"))
		diary := countFiles(filepath.Join(cfg.Root, "diary"))
		if pics+diary > 0 {
			ans := messageBox("Citizen Collector",
				fmt.Sprintf("Also delete what you have collected?\r\n\r\n"+
					"%d picture file(s) and %d saved session log(s) are in\r\n%s"+
					"\r\n\r\nYes - delete them.\r\nNo - keep them, and remove "+
					"only the program.", pics, diary, cfg.Root),
				mbYesNoCancel|mbIconWarn)
			if ans == idCancel {
				return 0
			}
			removeData = ans == idYes
		}
	}

	res := UninstallSelf(cfg, removeData, logf)

	// THE PROGRAM ITSELF CANNOT DELETE ITSELF WHILE IT IS RUNNING, and pretending
	// otherwise is how an uninstaller leaves a file behind and reports success.
	// A short detached command does it after this process exits.
	exe, _ := os.Executable()
	if err := scheduleSelfDelete(exe, cfg.Root, removeData); err != nil {
		res.Problems = append(res.Problems,
			"the program folder could not be scheduled for removal: "+err.Error())
	}

	if !quiet {
		var b strings.Builder
		b.WriteString("Citizen Collector has been removed.\r\n\r\n")
		if res.StartupRemoved {
			b.WriteString("- it will no longer start with Windows\r\n")
		}
		if res.ShortcutsRemoved > 0 {
			b.WriteString(fmt.Sprintf("- %d shortcut(s) removed\r\n", res.ShortcutsRemoved))
		}
		if res.EntryRemoved {
			b.WriteString("- removed from Add or remove programs\r\n")
		}
		if res.DataKept {
			b.WriteString("\r\nYour pictures and session logs have been KEPT in\r\n")
			b.WriteString(cfg.Root)
		} else {
			b.WriteString(fmt.Sprintf("\r\n%d collected file(s) deleted, as you asked.",
				res.DataRemoved))
		}
		if len(res.Problems) > 0 {
			b.WriteString("\r\n\r\nThese could not be done:\r\n")
			for _, p := range res.Problems {
				b.WriteString("- " + p + "\r\n")
			}
		}
		messageBox("Citizen Collector", b.String(), mbOK|mbIconInfo)
	}
	if len(res.Problems) > 0 {
		return 1
	}
	return 0
}

// scheduleSelfDelete removes the program folder after this process exits.
//
// KEEPS THE DATA FOLDERS unless they were explicitly chosen for removal - which
// has already happened by this point, so what is left here is only the program.
func scheduleSelfDelete(exe, root string, dataToo bool) error {
	if root == "" {
		return nil
	}
	keep := ""
	if !dataToo {
		// Remove the executable and leave the folder, so kept data stays where
		// the person was just told it is.
		cmd := exec.Command("cmd", "/c", "ping", "127.0.0.1", "-n", "3", ">nul",
			"&", "del", "/q", exe)
		cmd.SysProcAttr = &syscall.SysProcAttr{HideWindow: true}
		return cmd.Start()
	}
	_ = keep
	cmd := exec.Command("cmd", "/c", "ping", "127.0.0.1", "-n", "3", ">nul",
		"&", "rmdir", "/s", "/q", root)
	cmd.SysProcAttr = &syscall.SysProcAttr{HideWindow: true}
	return cmd.Start()
}
