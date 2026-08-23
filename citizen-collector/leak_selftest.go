package main

// leak_selftest.go - the sidecar must never carry a player identifier.
//
// THIS IS THE CHECK THAT GATES PUTTING THE COLLECTOR ON ANOTHER PERSON'S
// MACHINE, so it is written to fail loudly rather than to pass quietly.
//
// The defect it guards against was live for months and was found by reading a
// captures folder, not by any check: `location_candidates[]` shipped the raw
// log lines whenever the location parser could not name a place, and in-world
// the parser NEVER could - so 364 of 450 sidecars in one session each carried
// about forty raw lines, complete with playerGEID, the account handle and shard
// ids. It was the single field in the whole tool that bypassed allow-listing.
//
// Every fixture line below is a REAL shape from Sleven's archive, including the
// identifiers, because a leak test built from invented data proves only that
// invented data does not leak.

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"strings"
)

// The identifiers that must never appear in a sidecar. These are the actual
// values observed in the leaking captures - a test that searched for a
// placeholder would pass on a file full of the real thing.
var leakNeedles = []string{
	"204354536218", // playerGEID, in 57 sidecars when first counted
	"Sleven-K",     // the account handle
	"864133595285", // a third party's GEID, from a Channel Disconnected line
}

// An in-world log. THIS IS THE CASE THAT LEAKED: gamerules is SC_Default, so
// the frontend shortcut does not apply, and the location has to come from a
// pattern. Every line here is location-shaped enough to have been swept into
// location_candidates[].
const leakFixtureInWorld = `<2026-08-13T00:40:31.100Z> Changelist: 12399239
<2026-08-13T00:40:31.200Z> [Notice] <Context Establisher Done> establisher="CReplicationModel" message="eSpawn" gamerules="SC_Default" map="megamap"
<2026-08-13T00:40:32.000Z> [Notice] <Legacy login response> [CIG-net] User Login Success - Handle[Sleven-K] - Time[279748185]
<2026-08-13T00:40:35.000Z> [Notice] <OnClientSpawned> player="Sleven-K" playerGEID=204354536218 zone="AsteroidClusterBase_Nyx_Social_Keeger_002"
<2026-08-13T00:40:37.000Z> [Notice] <RequestLocationInventory> Player[Sleven-K] requested inventory for Location[AsteroidClusterBase_Nyx_Social_Keeger_002] [Team_CoreGameplayFeatures][Inventory]
<2026-08-13T00:40:38.000Z> [Notice] <Channel Disconnected> nickname="Containerstadt" playerGEID=864133595285
<2026-08-13T00:40:39.000Z> [Notice] <Vehicle Control Flow> releasing control token for 'DRAK_Vulture_864140490741' [864140490741]
`

// The same session in the menu, where the parser always worked and where the
// original "it did its job" reading came from.
const leakFixtureMenu = `<2026-08-13T00:30:31.100Z> Changelist: 12399239
<2026-08-13T00:30:31.200Z> [Notice] <Context Establisher Done> establisher="CReplicationModel" message="eNoValue" gamerules="SC_Frontend" map="megamap"
<2026-08-13T00:30:32.000Z> [Notice] <Legacy login response> [CIG-net] User Login Success - Handle[Sleven-K] - Time[279748185]
`

// A log that mentions places but names none of them in any known format - the
// case the raw-line payload existed to serve. It must still produce a useful
// diagnostic and still carry no log text.
const leakFixtureUnparseable = `<2026-08-13T00:50:31.100Z> Changelist: 12399239
<2026-08-13T00:50:31.200Z> [Notice] <Context Establisher Done> gamerules="SC_Default" map="megamap"
<2026-08-13T00:50:33.000Z> [Notice] <SomeFutureSubsystem> player="Sleven-K" playerGEID=204354536218 somewhere=Stanton_NewBabbage_Landing
<2026-08-13T00:50:34.000Z> [Notice] <AnotherOne> zone_id=99 planet_thing="microTech" handle="Sleven-K"
`

// escapedLT is how encoding/json spells "<" - taken FROM the encoder rather
// than typed out here. Writing the six characters by hand is what broke this
// check once already: a copy step collapsed them back into a literal "<", so
// the assertion read !contains("<") && contains("<") and could never be true.
// Asking the encoder removes the possibility of disagreeing with it.
var escapedLT = func() string {
	b, _ := json.Marshal("<")
	return strings.Trim(string(b), `"`)
}()

func writeLeakFixture(dir, name, body string) (string, error) {
	p := filepath.Join(dir, name)
	return p, os.WriteFile(p, []byte(body), 0o644)
}

// sidecarJSON marshals GameLogInfo exactly as the capture path writes it, so
// the test inspects the BYTES that would reach disk rather than a struct.
func sidecarJSON(info GameLogInfo) (string, error) {
	b, err := json.MarshalIndent(info, "", "  ")
	return string(b), err
}

func runSidecarLeakSelftest(check func(name string, ok bool, detail string)) {
	dir, err := os.MkdirTemp("", "cc-leak-")
	if err != nil {
		check("leak: temp dir", false, err.Error())
		return
	}
	defer os.RemoveAll(dir)

	// --- 1. THE CASE THAT LEAKED ---------------------------------------
	p, err := writeLeakFixture(dir, "inworld.log", leakFixtureInWorld)
	if err != nil {
		check("leak: fixture", false, err.Error())
		return
	}
	inWorld := ReadGameLog(p, "selftest")
	js, err := sidecarJSON(inWorld)
	if err != nil {
		check("leak: sidecar marshals", false, err.Error())
		return
	}

	var found []string
	for _, n := range leakNeedles {
		if strings.Contains(js, n) {
			found = append(found, n)
		}
	}
	check("LEAK: an in-world sidecar carries NO player id, handle or third-party id",
		len(found) == 0,
		fmt.Sprintf("found %v in the sidecar JSON", found))

	check("LEAK: and no raw log line - no timestamp-and-[Notice] text at all",
		!strings.Contains(js, "[Notice]") && !strings.Contains(js, "<2026-"),
		"a raw log line survived into the sidecar")

	// --- 2. THE OTHER HALF: it must now KNOW where it is ----------------
	//
	// Closing the leak by muting alone would pass check 1 while leaving every
	// in-world capture unable to say where it was taken. The erratum is
	// explicit that this is the real fix, so it is asserted, not assumed.
	check("an in-world sidecar reports a NON-NULL location",
		inWorld.Location != nil,
		"location is still null in the very case the burst path resolves")
	check("and it is the location the burst path names, from the VERIFIED pattern",
		inWorld.Location != nil &&
			*inWorld.Location == "AsteroidClusterBase_Nyx_Social_Keeger_002" &&
			inWorld.LocationOK,
		fmt.Sprintf("location=%v src=%q verified=%v",
			derefOr(inWorld.Location, "<nil>"), inWorld.LocationSrc, inWorld.LocationOK))

	// --- 3. the menu case must not have regressed -----------------------
	p2, _ := writeLeakFixture(dir, "menu.log", leakFixtureMenu)
	menu := ReadGameLog(p2, "selftest")
	js2, _ := sidecarJSON(menu)
	check("the menu case still resolves, and still leaks nothing",
		menu.Location != nil && strings.Contains(*menu.Location, "main menu") &&
			!strings.Contains(js2, "Sleven-K"),
		fmt.Sprintf("location=%v", derefOr(menu.Location, "<nil>")))

	// --- 4. THE CASE THE RAW LINES EXISTED FOR --------------------------
	//
	// Nothing parseable. This is where the payload used to be attached, so it
	// is the strongest test that the replacement carries no text - and it must
	// STILL be diagnostically useful, or the fix traded a leak for blindness.
	p3, _ := writeLeakFixture(dir, "unparseable.log", leakFixtureUnparseable)
	unk := ReadGameLog(p3, "selftest")
	js3, _ := sidecarJSON(unk)

	var found3 []string
	for _, n := range leakNeedles {
		if strings.Contains(js3, n) {
			found3 = append(found3, n)
		}
	}
	check("LEAK: an UNPARSEABLE in-world log still leaks nothing",
		len(found3) == 0,
		fmt.Sprintf("found %v - this is the case the raw payload was attached to", found3))

	check("and it still says which matchers were tried, so the gap is diagnosable",
		len(unk.LocationPatternsTried) > 0 && unk.LocationCandidateLines > 0,
		fmt.Sprintf("tried=%v lines=%d - a leak traded for blindness is not a fix",
			unk.LocationPatternsTried, unk.LocationCandidateLines))

	// --- 5. NEGATIVE CONTROL -------------------------------------------
	//
	// The needles must be findable in the SOURCE, or checks 1 and 4 would pass
	// against a fixture that never contained them - a leak test that cannot
	// detect a leak.
	srcFound := 0
	for _, n := range leakNeedles {
		if strings.Contains(leakFixtureInWorld, n) {
			srcFound++
		}
	}
	check("NEGATIVE CONTROL: every identifier IS present in the source log",
		srcFound == len(leakNeedles),
		fmt.Sprintf("%d of %d needles are in the fixture - if this is short, the "+
			"leak checks above are vacuous", srcFound, len(leakNeedles)))
}

// A DirectX session whose GPU driver line mentions the Vulkan API. This is a
// real shape from the archive and it is the exact case the old `\bVulkan\b`
// matcher got wrong - the driver stating what it supports, not what the game is
// running on.
const rendererFixtureDX = `<2026-08-13T00:40:31.100Z> Changelist: 12399239
<2026-08-13T00:40:31.150Z> [Notice] <Context Establisher Done> gamerules="SC_Default" map="megamap"
<2026-08-13T00:40:31.180Z> Video adapter: NVIDIA GeForce RTX 4080 Ti) Driver Version (581.57.0.0) Vulkan API (1.4.312)
<2026-08-13T00:40:31.200Z> D3D Adapter: FeatureLevel = DirectX 11.1
`

// A genuine Vulkan session: the [VK] channel appears.
const rendererFixtureVK = `<2026-08-13T00:40:31.100Z> Changelist: 12399239
<2026-08-13T00:40:31.150Z> [Notice] <Context Establisher Done> gamerules="SC_Default" map="megamap"
<2026-08-13T00:40:31.180Z> Video adapter: NVIDIA GeForce RTX 4080 Ti) Driver Version (581.57.0.0) Vulkan API (1.4.312)
<2026-08-13T00:40:31.370Z> [VK] Available Vulkan Layer - Layer: VK_LAYER_NV_optimus
`

func runRendererSelftest(check func(name string, ok bool, detail string)) {
	dir, err := os.MkdirTemp("", "cc-renderer-")
	if err != nil {
		check("renderer: temp dir", false, err.Error())
		return
	}
	defer os.RemoveAll(dir)

	dxPath, _ := writeLeakFixture(dir, "dx.log", rendererFixtureDX)
	dx := ReadGameLog(dxPath, "selftest")
	check("renderer: a DirectX session reports DirectX",
		dx.Renderer != nil && *dx.Renderer == "DirectX 11.1",
		fmt.Sprintf("got %q", derefOr(dx.Renderer, "<nil>")))

	// THE CASE THAT MOTIVATED CORRECTING THE MATCHER. Both fixtures carry the
	// driver's "Vulkan API (1.4.312)" line; only one is a Vulkan session.
	check("NEGATIVE CONTROL: a driver line mentioning the Vulkan API does NOT make it a Vulkan session",
		dx.Renderer != nil && *dx.Renderer != "Vulkan",
		"the old \bVulkan\b matcher reported Vulkan for this exact log shape")

	vkPath, _ := writeLeakFixture(dir, "vk.log", rendererFixtureVK)
	vk := ReadGameLog(vkPath, "selftest")
	check("renderer: a session with the [VK] channel reports Vulkan",
		vk.Renderer != nil && *vk.Renderer == "Vulkan",
		fmt.Sprintf("got %q", derefOr(vk.Renderer, "<nil>")))
	check("renderer: and it names where the answer came from",
		vk.RendererSrc != "" && dx.RendererSrc != "",
		fmt.Sprintf("vk=%q dx=%q", vk.RendererSrc, dx.RendererSrc))

	// Every sidecar must carry the field, which is the acceptance item.
	inw, _ := writeLeakFixture(dir, "inw.log", leakFixtureInWorld)
	noR := ReadGameLog(inw, "selftest")
	check("renderer: a log that never states one reports null rather than guessing",
		noR.Renderer == nil,
		fmt.Sprintf("got %q from a log with no renderer line", derefOr(noR.Renderer, "<nil>")))
}

// §6: the export must REFUSE a leaking sidecar, and say what it found.
//
// Driven through listCaptures - the real admission path - rather than by
// calling the predicate directly, because a guard that is never reached is
// exactly the defect this is guarding against.
func runExportPrivacyGuardSelftest(check func(name string, ok bool, detail string)) {
	dir, err := os.MkdirTemp("", "cc-guard-")
	if err != nil {
		check("guard: temp dir", false, err.Error())
		return
	}
	defer os.RemoveAll(dir)

	// A frame is admitted on the strength of its sidecar naming the game, so
	// every fixture below names it. The ONLY difference between the clean one
	// and the leaking ones is the privacy content - otherwise a refusal could
	// be happening for an unrelated reason and this would prove nothing.
	write := func(stem, sidecar string) string {
		png := filepath.Join(dir, stem+".png")
		_ = os.WriteFile(png, []byte("not really a png"), 0o644)
		_ = os.WriteFile(filepath.Join(dir, stem+".json"), []byte(sidecar), 0o644)
		return png
	}

	clean := write("clean", `{"window":{"exe":"StarCitizen.exe","title":"Star Citizen"},
	  "game_log":{"location":"AsteroidClusterBase_Nyx_Social_Keeger_002","renderer":"Vulkan"}}`)
	geid := write("geid", `{"window":{"exe":"StarCitizen.exe","title":"Star Citizen"},
	  "game_log":{"location":null,"note":"playerGEID=204354536218"}}`)
	cands := write("cands", `{"window":{"exe":"StarCitizen.exe","title":"Star Citizen"},
	  "game_log":{"location_candidates":["something location-shaped"]}}`)
	// ENCODED BY encoding/json, NOT HAND-WRITTEN. This is the fixture that
	// matters most and the one that was wrong.
	//
	// Go HTML-escapes < > and & by default, so a raw log line reaches disk as
	// "<2026-08-13T...>" and there is no literal < in any sidecar this
	// program has ever written. The first version of this test hand-wrote the
	// JSON with a literal <, so it proved the guard could catch a shape the
	// collector does not produce - while the guard could not see a single real
	// leaking file on this disk.
	//
	// Marshalling through the same encoder the collector uses is the only way
	// this fixture stays honest when the escaping changes again.
	rawlnDoc := map[string]interface{}{
		"window": map[string]interface{}{"exe": "StarCitizen.exe", "title": "Star Citizen"},
		"game_log": map[string]interface{}{
			"note": "<2026-08-13T00:40:37.000Z> [Notice] <RequestLocationInventory> Player[Sleven-K] ...",
		},
	}
	rawlnBytes, _ := json.Marshal(rawlnDoc)
	rawln := write("rawln", string(rawlnBytes))
	handle := write("handle", `{"window":{"exe":"StarCitizen.exe","title":"Star Citizen"},
	  "game_log":{"note":"User Login Success - Handle[Sleven-K] - Time[279748185]"}}`)

	// The fixture must actually be escaped, or this test has quietly gone back
	// to proving nothing.
	check("NEGATIVE CONTROL: the encoded fixture really is escaped (no literal <)",
		!strings.Contains(string(rawlnBytes), "<") &&
			strings.Contains(string(rawlnBytes), escapedLT),
		fmt.Sprintf("encoder produced: %s", string(rawlnBytes)))

	a := listCaptures(dir)
	sent := map[string]bool{}
	for _, p := range a.OK {
		sent[p] = true
	}

	check("GUARD: a sidecar carrying a playerGEID is REFUSED",
		!sent[geid], "it would have been sent")
	check("GUARD: and the refusal names the field",
		strings.Contains(a.Why[geid], "playerGEID"),
		fmt.Sprintf("reason was %q", a.Why[geid]))

	check("GUARD: a sidecar carrying location_candidates is REFUSED",
		!sent[cands] && strings.Contains(a.Why[cands], "location_candidates"),
		fmt.Sprintf("reason was %q", a.Why[cands]))

	check("GUARD: a sidecar quoting a raw log line is REFUSED",
		!sent[rawln] && strings.Contains(a.Why[rawln], "raw log line"),
		fmt.Sprintf("reason was %q", a.Why[rawln]))

	check("GUARD: a sidecar carrying an account handle is REFUSED",
		!sent[handle] && strings.Contains(a.Why[handle], "handle"),
		fmt.Sprintf("reason was %q", a.Why[handle]))

	// THE NEGATIVE CONTROL, and it is the one that keeps the four above
	// honest. If the guard refused everything - a broken predicate, a wrong
	// path, an empty folder - all four would still "pass".
	check("NEGATIVE CONTROL: a clean sidecar IS still sent",
		sent[clean],
		"the guard refused a clean frame, so the refusals above prove nothing")

	check("guard: exactly one frame of five was admitted",
		len(a.OK) == 1 && len(a.Quaranti) == 4,
		fmt.Sprintf("admitted %d, held %d", len(a.OK), len(a.Quaranti)))
}

func derefOr(s *string, or string) string {
	if s == nil {
		return or
	}
	return *s
}
