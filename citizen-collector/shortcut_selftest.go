package main

// shortcut_selftest.go - the shortcut has to actually land, and be findable.
//
// # WHY THIS IS TESTED RATHER THAN EYEBALLED
//
// The failure it exists to catch is invisible. IPersistFile::Save returns S_OK
// against a redirected Desktop folder and produces a .lnk somewhere the user
// will never look. Nothing errors, the log says "created", and the person is
// still hunting for the program. That is the sixth-time-this-project
// silent-success shape, and the only defence is checking the file is on disk
// where it was asked for.
//
// # WHAT IT DELIBERATELY DOES NOT DO
//
// It does not write to the real Desktop or Start Menu. A selftest that
// decorated somebody's desktop every time it ran would be its own bug. It
// creates a shortcut in a temp folder, proves the whole COM path works end to
// end, reads the folder locations to prove they resolve, and cleans up.

import (
	"os"
	"path/filepath"
	"strings"
)

func runShortcutSelftest(check func(name string, ok bool, detail string)) {

	// -----------------------------------------------------------------
	// 1. THE NAME IS THE PRODUCT NAME, NOT THE FILE NAME
	// -----------------------------------------------------------------
	//
	// The entire reason this file exists is that dragging collector.exe out
	// produces an icon labelled "collector". If the shortcut we create says the
	// same thing, nothing was fixed.
	name := shortcutTargetName()
	check("SHORTCUT: the shortcut is named for the product, not the exe",
		name == "Citizen Collector",
		"the shortcut would be labelled "+name)
	check("SHORTCUT: negative control - the exe's own stem would NOT have passed",
		strings.ToLower(name) != "collector",
		"the check above would accept the thing it is meant to reject")

	// -----------------------------------------------------------------
	// 2. THE KNOWN FOLDERS RESOLVE
	// -----------------------------------------------------------------
	//
	// Reading them proves SHGetKnownFolderPath works on this machine and, more
	// usefully, reports where they actually are - which is how a OneDrive
	// redirection becomes visible instead of mysterious.
	desktop, dErr := knownFolder(folderIDDesktop)
	check("SHORTCUT: the real Desktop folder resolves",
		dErr == nil && desktop != "",
		"could not resolve it: "+errText(dErr))
	if dErr == nil {
		redirected := strings.Contains(strings.ToLower(desktop), "onedrive")
		note := desktop
		if redirected {
			note += "  (REDIRECTED TO ONEDRIVE - %USERPROFILE%\\Desktop would have " +
				"written to a folder nobody looks at)"
		}
		check("SHORTCUT: Desktop location reported", true, note)
	}

	programs, pErr := knownFolder(folderIDPrograms)
	check("SHORTCUT: the Start Menu programs folder resolves",
		pErr == nil && programs != "",
		"could not resolve it: "+errText(pErr))

	// -----------------------------------------------------------------
	// 3. THE WHOLE COM PATH, END TO END, IN A TEMP FOLDER
	// -----------------------------------------------------------------
	tmp, err := os.MkdirTemp("", "cc-shortcut-selftest")
	if err != nil {
		check("SHORTCUT: could not make a temp folder to test in", false, err.Error())
		return
	}
	defer os.RemoveAll(tmp)

	exe, err := os.Executable()
	if err != nil {
		check("SHORTCUT: could not find my own path", false, err.Error())
		return
	}

	lnk := filepath.Join(tmp, shortcutTargetName()+".lnk")
	// A PATH, NOT "path,index". This test used to pass exe+",0" - the exact
	// defect it should have been catching - so it reproduced the bug and
	// reported success.
	cErr := CreateShortcut(lnk, exe, filepath.Dir(exe), "selftest", exe)
	check("SHORTCUT: a shortcut can actually be created",
		cErr == nil,
		"CreateShortcut failed: "+errText(cErr))

	if cErr == nil {
		fi, sErr := os.Stat(lnk)
		check("SHORTCUT: the created shortcut is a real, non-empty file",
			sErr == nil && fi.Size() > 0,
			"stat: "+errText(sErr))

		// A .lnk always begins with a 76-byte header whose first DWORD is 0x4C.
		// Checking the magic rather than only the size means a zero-filled or
		// truncated file cannot pass.
		if b, rErr := os.ReadFile(lnk); rErr == nil {
			ok := len(b) > 4 && b[0] == 0x4C && b[1] == 0 && b[2] == 0 && b[3] == 0
			check("SHORTCUT: the file is a real shell link, not just bytes on disk",
				ok, "the .lnk header magic is wrong - "+itoaSmall(len(b))+" bytes")
		}
	}

	// -----------------------------------------------------------------
	// 3b. THE ICON, READ BACK OFF THE SAVED FILE
	// -----------------------------------------------------------------
	//
	// THE CHECK THAT WOULD HAVE CAUGHT IT, and the only one that would have.
	// Every other check in this file passed for the entire life of the feature
	// while the shortcut on the Desktop was a blank white page: the name was
	// right, the file existed, the header magic was right, and the icon pointed
	// at a filename that could not exist.
	if cErr == nil {
		gotIcon, gotIdx, iErr := ReadShortcutIconLocation(lnk)
		check("SHORTCUT: the icon location can be read back off the saved .lnk",
			iErr == nil && gotIcon != "",
			"read: "+errText(iErr))
		check("SHORTCUT: the saved icon is the exe itself, with no index glued on",
			strings.EqualFold(gotIcon, exe),
			"the .lnk records icon path "+gotIcon+" (index "+itoaSmall(gotIdx)+")")
		check("SHORTCUT: the icon index is passed as an index, not inside the path",
			gotIdx == 0 && !strings.Contains(gotIcon, ","),
			"path/index came back as "+gotIcon+" / "+itoaSmall(gotIdx))
		check("SHORTCUT: the saved icon location exists on disk",
			VerifyShortcutIcon(lnk) == nil,
			"VerifyShortcutIcon: "+errText(VerifyShortcutIcon(lnk)))
	}

	// -----------------------------------------------------------------
	// 3c. NEGATIVE CONTROLS FOR THE ICON CHECK ITSELF
	// -----------------------------------------------------------------
	//
	// THE LOAD-BEARING ONES. A shortcut verifier that has never been observed
	// rejecting anything is exactly the thing it exists to catch. Both of these
	// build a shortcut the old code would have produced and confirm the new
	// check refuses it.
	{
		// The original defect, reproduced deliberately: path with ",0" glued on.
		badIcon := filepath.Join(tmp, "with-comma-index.lnk")
		mkErr := createShortcutNoVerify(badIcon, exe, filepath.Dir(exe), "selftest", exe+",0")
		if mkErr == nil {
			vErr := VerifyShortcutIcon(badIcon)
			check("SHORTCUT: NEGATIVE CONTROL - an icon path with ,0 glued on IS rejected",
				vErr != nil,
				"the exact shortcut every install has been getting was accepted as fine")
			check("SHORTCUT: and the rejection names the real cause",
				vErr != nil && strings.Contains(vErr.Error(), "index appended"),
				"the message would send somebody looking for a missing icon file: "+errText(vErr))
		} else {
			check("SHORTCUT: NEGATIVE CONTROL - could not build the bad shortcut to test with",
				false, errText(mkErr))
		}

		// An icon that is simply not there.
		missing := filepath.Join(tmp, "missing-icon.lnk")
		gone := filepath.Join(tmp, "no-such-icon-file.ico")
		if mkErr := createShortcutNoVerify(missing, exe, filepath.Dir(exe), "selftest", gone); mkErr == nil {
			check("SHORTCUT: NEGATIVE CONTROL - an icon file that does not exist IS rejected",
				VerifyShortcutIcon(missing) != nil,
				"a shortcut pointing at a non-existent icon passed verification")
		}

		// AND THE CHECK MUST NOT REJECT EVERYTHING. Without this, a verifier
		// that always failed would satisfy both controls above and break every
		// shortcut the program makes.
		check("SHORTCUT: NEGATIVE CONTROL - a correct shortcut is still accepted",
			VerifyShortcutIcon(lnk) == nil,
			"the verifier rejects good shortcuts too, so it proves nothing")
	}

	// -----------------------------------------------------------------
	// 4. NEGATIVE CONTROL - AN IMPOSSIBLE PATH MUST FAIL
	// -----------------------------------------------------------------
	//
	// Without this, CreateShortcut could return nil unconditionally and every
	// check above would still be green.
	bad := filepath.Join(tmp, "no-such-subfolder", "x.lnk")
	bErr := CreateShortcut(bad, exe, filepath.Dir(exe), "selftest", "")
	check("SHORTCUT: negative control - an unwritable path IS reported as a failure",
		bErr != nil,
		"creating a shortcut in a non-existent folder reported success")

	// -----------------------------------------------------------------
	// 5. THE QUESTION IS ASKED ONCE, NOT EVERY LAUNCH
	// -----------------------------------------------------------------
	//
	// A dialog on every start is how a helpful prompt becomes the reason
	// somebody stops running the program.
	check("SHORTCUT: a fresh folder has not been asked yet",
		!shortcutAsked(tmp), "shortcutAsked said yes before anything was recorded")
	recordShortcutAnswer(tmp, "no")
	check("SHORTCUT: recording an answer stops it being asked again",
		shortcutAsked(tmp), "the answer was not remembered - it would ask on every launch")

	// -----------------------------------------------------------------
	// 6. REPAIR APPLIES TO YES, AND ONLY TO YES
	// -----------------------------------------------------------------
	//
	// Existing installs have a broken icon through no fault of theirs and must
	// be corrected without a second prompt. Somebody who said NO must not have
	// shortcuts appear on their desktop because of a repair pass - that would
	// turn a bug fix into doing the opposite of what they asked.
	check("SHORTCUT: an answer of no is not treated as a request to repair",
		!shortcutAnswerWasYes(tmp),
		"a machine that declined shortcuts would have them written by the repair")
	recordShortcutAnswer(tmp, "yes")
	check("SHORTCUT: an answer of yes is recognised, so repairs can happen silently",
		shortcutAnswerWasYes(tmp),
		"an install that asked for shortcuts would never get its icon fixed")
}
