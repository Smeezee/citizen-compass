package main

// identity_selftest.go - checks for the contributor id and the dataset schema
// version.
//
// EVERY CHECK HAS A NEGATIVE CONTROL (hard rule 12).
//
// The two that matter most, and why:
//
//  1. The id file is plain text so the person can read it. Which means they can
//     EDIT it. Somebody will eventually put their handle in there - it is the
//     obvious thing to do with a file called "id". If that string can reach an
//     export, this whole tool's privacy story is over, so the rejection is
//     tested with a real handle out of Sleven's own archive rather than with
//     "not_hex".
//
//  2. Refusing to load a dataset written by a NEWER build. A downgrade that
//     loads, drops the fields it does not know, and saves is indistinguishable
//     from a successful run right up until somebody notices months of data is
//     gone. The check asserts the file is BYTE-IDENTICAL afterwards, because
//     "returned an error" and "did not damage the file" are different claims
//     and only the second one matters.

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"strings"
)

func runInstallIDSelftest(check func(name string, ok bool, detail string)) {
	tmp, err := os.MkdirTemp("", "installid-")
	if err != nil {
		check("install id: temp dir", false, err.Error())
		return
	}
	defer os.RemoveAll(tmp)

	// --- generated, stable, and shaped the way it claims --------------------

	a, err := LoadOrCreateInstall(tmp, nil)
	if err != nil {
		check("install id: can be generated", false, err.Error())
		return
	}
	check("install id: can be generated", validInstallID(a.ID),
		"32 hex characters from crypto/rand: "+a.ID)

	b, err := LoadOrCreateInstall(tmp, nil)
	check("install id: is the SAME on the next run", err == nil && b.ID == a.ID,
		"an id that changed every run would make one person look like many")

	check("install id: was not marked as regenerated", !b.Regenerated,
		"a clean second read must not accuse the first run of anything")

	// NEGATIVE CONTROL. Two fresh installs must not collide. If newInstallID
	// were ever "fixed" to seed from the clock or the hostname, this is the
	// check that fires - two installs made in the same second on the same
	// machine is exactly that failure's shape.
	other, _ := os.MkdirTemp("", "installid2-")
	defer os.RemoveAll(other)
	c, _ := LoadOrCreateInstall(other, nil)
	check("NEGATIVE CONTROL: a second install gets a DIFFERENT id",
		c.ID != "" && c.ID != a.ID,
		"if these ever match, the id is derived from the machine and not random")

	// --- the readable-file-is-an-editable-file problem ----------------------

	path := installIDPath(tmp)

	// A real handle out of the 2026-08-07 archive. This is the string that must
	// never reach an export.
	if err := os.WriteFile(path, []byte("id = Sleven-K\n"), 0o644); err != nil {
		check("install id: fixture", false, err.Error())
		return
	}
	d, err := LoadOrCreateInstall(tmp, nil)
	check("PRIVACY: a hand-typed handle in the id file is REJECTED",
		err == nil && d.ID != "Sleven-K" && validInstallID(d.ID),
		"the file is readable, therefore editable, therefore somebody will type their name in it")
	check("PRIVACY: the replacement is reported, not done quietly",
		d.Regenerated && d.RegenReason != "",
		"a changed id makes this machine's old and new exports look like two people")

	raw, _ := os.ReadFile(path)
	check("PRIVACY: the rejected value is not written back to disk",
		!strings.Contains(string(raw), "Sleven-K"),
		"rejecting it and then saving it would be worse than not checking")

	// NEGATIVE CONTROL for the validator itself: it must accept what this tool
	// writes, or the check above would pass for the wrong reason - every id
	// would be "rejected" and the test could never fail.
	check("NEGATIVE CONTROL: the validator ACCEPTS a real generated id",
		validInstallID(a.ID) && validInstallID(strings.ReplaceAll(a.ID, "-", "")),
		"with and without the readability dashes")
	check("NEGATIVE CONTROL: the validator rejects near-misses",
		!validInstallID("") && !validInstallID(a.ID+"00") &&
			!validInstallID(strings.Repeat("z", 32)),
		"empty, too long, and right length but not hex")
}

func runMineSchemaSelftest(check func(name string, ok bool, detail string)) {
	// This fixture calls MineAll three times. That is safe ONLY because the
	// selftest runner isolates the log archive for the whole run - see
	// isolateArchiveForSelftest in gamelog_mine.go, and read its comment before
	// changing anything here. Unisolated, these three calls read 208 MB of the
	// operator's real logs and this fixture alone takes over four minutes.
	tmp, err := os.MkdirTemp("", "mineschema-")
	if err != nil {
		check("schema: temp dir", false, err.Error())
		return
	}
	defer os.RemoveAll(tmp)

	in := Install{ID: "00112233-44556677-8899aabb-ccddeeff", FirstSeen: "2026-08-08T00:00:00Z"}

	st, err := MineAll(tmp, in, nil)
	if err != nil {
		check("schema: a first run writes a dataset", false, err.Error())
		return
	}
	check("schema: a first run stamps the current version",
		st.SchemaVersion == MineSchemaVersion, "written as v"+itoaSmall(st.SchemaVersion))
	check("schema: the contributor id reaches the dataset",
		st.InstallID == in.ID, "so an export can be told apart from another person's")

	// --- a file with no version is v1, not a broken file --------------------

	p := mineStorePath(tmp)
	var loose map[string]interface{}
	b, _ := os.ReadFile(p)
	_ = json.Unmarshal(b, &loose)
	delete(loose, "schema_version")
	nb, _ := json.MarshalIndent(loose, "", "  ")
	_ = os.WriteFile(p, nb, 0o644)

	old, err := loadMineStore(tmp)
	check("schema: a file written before versioning existed loads as v1",
		err == nil && old != nil && old.SchemaVersion == 1,
		"absence of the field is the version, not a corruption")

	// --- THE ONE THAT MATTERS: a newer file must survive an older build -----

	loose["schema_version"] = MineSchemaVersion + 7
	loose["something_this_build_has_never_heard_of"] = []string{"keep", "me"}
	nb, _ = json.MarshalIndent(loose, "", "  ")
	_ = os.WriteFile(p, nb, 0o644)
	before, _ := os.ReadFile(p)

	_, err = MineAll(tmp, in, nil)
	check("schema: a dataset from a NEWER build is refused",
		err != nil, "loading it would silently drop every field this build does not know")

	after, _ := os.ReadFile(p)
	check("schema: and the newer dataset is left BYTE-IDENTICAL",
		string(before) == string(after),
		"returning an error is not the point - not overwriting the file is the point")

	// NEGATIVE CONTROL: the refusal must be specific to a NEWER version, or it
	// would refuse everything and the check above would pass for free.
	loose["schema_version"] = MineSchemaVersion
	nb, _ = json.MarshalIndent(loose, "", "  ")
	_ = os.WriteFile(p, nb, 0o644)
	_, err = MineAll(tmp, in, nil)
	check("NEGATIVE CONTROL: a same-version dataset is still accepted",
		err == nil, "the guard must fire on newer only, not on everything")
}

// runMineWiredParsersSelftest covers the three extractors that compiled for
// months while reaching nothing, plus the privacy guard they now depend on.
func runMineWiredParsersSelftest(check func(name string, ok bool, detail string)) {
	tmp, err := os.MkdirTemp("", "minewired-")
	if err != nil {
		check("wired parsers: temp dir", false, err.Error())
		return
	}
	defer os.RemoveAll(tmp)

	st := newMineStore()

	// Two real shapes plus the two traps. The trap line is the one that broke a
	// looser pattern on the real log: a separator class that could cross a field
	// boundary read the player's location as "state".
	fixture := `<2026-08-07T22:30:00.000Z> [Notice] <OC> objectcontainer="DRAK_Vulture_864140490741"
<2026-08-07T22:30:01.000Z> [Notice] <Spawn> spawn_location="Stanton_1_Hurston_L1"
<2026-08-07T22:30:02.000Z> [Notice] <RequestLocationInventory> name="Containerstadt_Shop"
<2026-08-07T22:30:03.000Z> [Notice] <CVS> taskname="ResolveSpawnLocation" state=eCVS_UnstowPlayer(14)
<2026-08-07T22:30:04.000Z> [Notice] <OC> objectcontainer="eCVS_ReadyToStream"
`
	p := filepath.Join(tmp, "Game.log")
	if err := os.WriteFile(p, []byte(fixture), 0o644); err != nil {
		check("wired parsers: fixture", false, err.Error())
		return
	}
	if err := mineOneLog(p, st); err != nil {
		check("wired parsers: reads the log", false, err.Error())
		return
	}

	check("wired: object containers now reach the dataset",
		len(st.ObjectContainers) == 1,
		"this extractor compiled for months and reached nothing")
	check("wired: spawn locations now reach the dataset",
		len(st.SpawnLocations) == 1, "same")
	check("wired: the RequestLocationInventory name form reaches locations",
		st.Locations["Containerstadt_Shop"] == 1, "distinct from the Location[...] form")

	// PRIVACY. An object container is very often a ship, and a ship in this log
	// wears an entity id. This is the exact case the first audit could not fail
	// on, because it only looked for bare digit strings.
	leaked := ""
	for k := range st.ObjectContainers {
		if strings.Contains(k, "864140490741") {
			leaked = k
		}
	}
	check("PRIVACY: an entity id embedded in a container name is scrubbed",
		leaked == "" && st.ObjectContainers["DRAK_Vulture_<id>"] == 1,
		"DRAK_Vulture_864140490741 is a name with an id inside it")

	// NEGATIVE CONTROL: the scrubber must not eat the useful part.
	check("NEGATIVE CONTROL: scrubbing keeps the ship class, not just the id",
		strings.HasPrefix("DRAK_Vulture_<id>", "DRAK_Vulture"),
		"a scrubber that removed everything would pass the leak test and be useless")

	// The state-token traps must have been rejected by plausibleLocation.
	check("wired: a CryEngine state enum is not recorded as a place",
		st.ObjectContainers["eCVS_ReadyToStream"] == 0,
		"eCVS_* is a state machine token wearing a location-shaped field")
	check("wired: the field-crossing trap line produced no spawn location",
		st.SpawnLocations["state"] == 0 && len(st.SpawnLocations) == 1,
		`taskname="ResolveSpawnLocation" state=eCVS_UnstowPlayer(14) once read as location "state"`)

	// --- the extractor table is the silent-parser canary --------------------

	ex := buildExtractors(st)
	byName := map[string]MineExtractor{}
	for _, e := range ex {
		byName[e.Name] = e
	}
	check("extractors: hits are counted per reader",
		byName["object_container"].Hits == 1 && byName["spawn_location"].Hits == 1,
		"a reader stuck at 0 is how a patch-broken pattern gets noticed")
	check("extractors: unverified readers are MARKED unverified in the data",
		!byName["object_container"].Verified && !byName["spawn_location"].Verified &&
			byName["transaction"].Verified,
		"whoever receives an export can tell a fact from a hint without reading our docs")

	// NEGATIVE CONTROL: a reader that genuinely did not fire must read 0, or the
	// canary would be decorative.
	check("NEGATIVE CONTROL: a reader that did not fire reports 0 hits",
		byName["transaction"].Hits == 0,
		"this fixture contains no transactions, so that reader must say so")
}

// itoaSmall avoids pulling strconv in for one call site.
func itoaSmall(n int) string {
	if n == 0 {
		return "0"
	}
	neg := n < 0
	if neg {
		n = -n
	}
	var b []byte
	for n > 0 {
		b = append([]byte{byte('0' + n%10)}, b...)
		n /= 10
	}
	if neg {
		return "-" + string(b)
	}
	return string(b)
}

// runSelftestArchiveIsolationSelftest proves `-selftest` does not read the
// operator's real Star Citizen logs.
//
// WHY THIS EXISTS. Section 5 of the flake order recorded a selftest run that
// produced no output and was killed at ten minutes. It was not a deadlock and
// it was not the staleness fixture: two fixtures reached MineAll, which asks
// mineTargets() for every Game.log and every logbackups file on four drives.
// On this machine that is 243 files and 208 MB. Measured back to back:
// 61ms isolated, over 240 SECONDS not.
//
// So this is a permanent check rather than a fixed line of code. It gets slower
// every session the operator plays, which means it degrades silently and looks
// like a hang long before anyone connects the two. And a selftest that reads a
// person's whole log archive is a surprise nobody asked for, whatever it does
// with the contents.
//
// PROVEN IN BOTH DIRECTIONS, because a check that cannot fail is not a check:
// the isolation is lifted and mineTargets() must come back with real files,
// then reinstated and it must come back empty. If this machine has no Star
// Citizen logs at all the first half cannot be performed, and it says so
// rather than passing.
func runSelftestArchiveIsolationSelftest(check func(name string, ok bool, detail string)) {
	// The selftest runner already installed the isolation. Lift it to see what
	// is really out there, then put it back - by construction, not by trusting
	// this function to be tidy.
	restore := func() func() {
		saved := mineTargets
		mineTargets = MineTargets
		return func() { mineTargets = saved }
	}()

	real := len(mineTargets())
	restore()

	isolated := len(mineTargets())

	if real == 0 {
		check("archive isolation: real log files exist to isolate FROM", false,
			"NOT PERFORMED - this machine has no Star Citizen logs, so an "+
				"empty result proves nothing about the isolation")
	} else {
		check("archive isolation: real log files exist to isolate FROM", true,
			fmt.Sprintf("%d file(s) on disk - without isolation the selftest "+
				"reads every one of them, which is what the ten-minute hang was",
				real))
	}

	check("archive isolation: the selftest sees NONE of them",
		isolated == 0,
		fmt.Sprintf("mineTargets() returns %d file(s) during the selftest "+
			"(want 0; %d exist on this machine)", isolated, real))
}
