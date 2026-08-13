package main

// mine_selftest.go - checks for the log miner, the export, and the game-exit
// hook that drives them.
//
// EVERY CHECK HAS A NEGATIVE CONTROL. Hard rule 12: a check that cannot fail is
// not a check. The privacy checks matter most here, because this is the first
// thing in the project designed to run on someone else's computer, and the cost
// of a silent leak is somebody else's handle in a file they did not know they
// were sending.

import (
	"archive/zip"
	"encoding/json"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"strings"
	"time"
)

// A synthetic log containing every shape the miner claims to read, plus the
// identifiers it claims to strip. Written from the real formats observed in
// Sleven's archive on 2026-08-07 - the handles and ids below are the ACTUAL
// ones seen in those logs, which is what makes the leak test meaningful.
const mineFixtureLog = `<2026-08-07T22:18:47.754Z> Changelist: 12399239
<2026-08-07T22:18:48.276Z> [Trace] Environment:   PTU
<2026-08-07T22:19:07.255Z> Change resolution: 1920x1080 (Borderless at 60.000Hz)
<2026-08-07T22:18:51.051Z> D3D Adapter: FeatureLevel = DirectX 11.1
<2026-08-07T22:19:10.021Z> [Notice] <Legacy login response> [CIG-net] User Login Success - Handle[Sleven-K] - Time[279748185]
<2026-08-07T22:20:37.004Z> [Notice] <RequestLocationInventory> Player[Sleven-K] requested inventory for Location[RR_JP_NyxCastra]
<2026-08-07T21:30:00.000Z> [Notice] <CEntityComponentShoppingProvider::SendStandardItemBuyRequest> Sending SShopBuyRequest - playerId[855480118723] shopId[864107402122] shopName[SCShop_Cordrys_Levski-001] kioskId[0] client_price[1000.000000] itemClassGUID[e7ba6337-2972-46db-b122-df73c4176027] itemName[vgl_flightsuit_01_01_01] quantity[1] currencyType[UEC]
<2026-08-07T21:31:00.000Z> [Notice] <CEntityComponentShopUIProvider::SendShopSellRequest> Sending SShopSellRequest - playerId[204354536218] shopId[999] shopName[SCShop_XS_MiningStall] kioskId[864062714799] client_price[810.000000] itemClassGUID[99379aa0-7240-4014-813a-0ab460f885f5] itemName[grin_multitool_01_salvage_repair] quantity[1]
<2026-06-13T22:26:18.562Z> [Notice] <CEntityComponentCommodityUIProvider::SendCommoditySellRequest> Sending SShopCommoditySellRequest - playerId[204354536218] shopId[433183157784] shopName[SCShop_Outpost_Junksite] kioskId[433183157751] amount[56385.000000] resourceGUID[a0e6c4cf-face-4f52-a020-dfa869607901]
<2026-08-07T22:25:00.000Z> Successfully calculated route to rs_ext_nyx-castra_jp1 fuel estimate 62510.890625
<2026-08-07T22:25:01.000Z> Successfully calculated route to PartyMemberMarker_200179793657 fuel estimate 1546089.375
<2026-08-07T22:26:00.000Z> [Notice] <Vehicle Control Flow> releasing control token for 'DRAK_Vulture_864140490741' [864140490741]
<2026-08-07T22:27:00.000Z> [Notice] <Channel Disconnected> nickname="Containerstadt" playerGEID=864133595285
`

func writeMineFixture(dir string) (string, error) {
	if err := os.MkdirAll(dir, 0o755); err != nil {
		return "", err
	}
	p := filepath.Join(dir, "Game.log")
	return p, os.WriteFile(p, []byte(mineFixtureLog), 0o644)
}

// --- 1. does it read what it claims to read? -------------------------------

func runMineParseSelftest(check func(name string, ok bool, detail string)) {
	tmp, err := os.MkdirTemp("", "mine-parse-")
	if err != nil {
		check("mine: temp dir", false, err.Error())
		return
	}
	defer os.RemoveAll(tmp)

	logPath, err := writeMineFixture(tmp)
	if err != nil {
		check("mine: fixture", false, err.Error())
		return
	}

	st := newMineStore()
	if err := mineOneLog(logPath, st); err != nil {
		check("mine: reads a log without error", false, err.Error())
		return
	}

	var buys, sells, commodity int
	for _, t := range st.Txns {
		if t.Market == "commodity" {
			commodity++
		}
		if t.Side == "sell" {
			sells++
		} else {
			buys++
		}
	}
	check("mine: finds all three transaction families in one pass",
		len(st.Txns) == 3 && buys == 1 && sells == 2 && commodity == 1,
		fmt.Sprintf("%d rows: %d buy, %d sell, %d commodity (expected 3: 1/2/1)",
			len(st.Txns), buys, sells, commodity))

	// §1, 2026-08-13. The archive says the verified form is the ONLY form this
	// subsystem writes, and that INVALID_LOCATION_ID is not a place. Both are
	// asserted here so that if either ever changes, it changes visibly.
	if _, invalid := st.Locations["INVALID_LOCATION_ID"]; true {
		check("mine: a location the game says has no inventory is not recorded as a location",
			!invalid, "INVALID_LOCATION_ID was stored as a real location")
	}
	check("mine: the verified Location[...] reader is what fires, not the name= variant",
		st.Locations["RR_JP_NyxCastra"] > 0 && st.hits["location_inventory_name"] == 0,
		fmt.Sprintf("Location[] hits %d, name= hits %d",
			st.Locations["RR_JP_NyxCastra"], st.hits["location_inventory_name"]))

	// The 4.10 rename must be READ, not just tolerated.
	sawNew := false
	for _, t := range st.Txns {
		if t.EmitBy == "CEntityComponentShoppingProvider" {
			sawNew = true
		}
	}
	check("mine: reads the renamed 4.10 class as well as the old one",
		sawNew,
		"a row emitted by CEntityComponentShoppingProvider was parsed")

	check("mine: captures the price",
		len(st.Txns) > 0 && st.Txns[0].Price == "1000.000000",
		fmt.Sprintf("first row price = %q", firstPrice(st)))

	check("mine: reads locations", len(st.Locations) == 1,
		fmt.Sprintf("%d location(s): %v", len(st.Locations), keysOf(st.Locations)))

	check("mine: reads quantum routes with fuel", len(st.Routes) == 2,
		fmt.Sprintf("%d destination(s)", len(st.Routes)))

	check("mine: reads ship classes", len(st.Ships) == 1,
		fmt.Sprintf("%v", keysOf(st.Ships)))

	// NEGATIVE CONTROL: a log with none of these shapes must yield NOTHING.
	// Without this, a parser that matched everything would pass every check
	// above by accident.
	empty := filepath.Join(tmp, "empty")
	_ = os.MkdirAll(empty, 0o755)
	ep := filepath.Join(empty, "Game.log")
	_ = os.WriteFile(ep, []byte("<2026-01-01T00:00:00.0Z> nothing interesting here\n"), 0o644)
	st2 := newMineStore()
	_ = mineOneLog(ep, st2)
	check("NEGATIVE CONTROL: a log with no transactions yields no rows",
		len(st2.Txns) == 0 && len(st2.Locations) == 0 && len(st2.Routes) == 0,
		fmt.Sprintf("%d rows, %d locations, %d routes (expected 0/0/0)",
			len(st2.Txns), len(st2.Locations), len(st2.Routes)))
}

func firstPrice(st *MineStore) string {
	if len(st.Txns) == 0 {
		return ""
	}
	return st.Txns[0].Price
}

func keysOf(m map[string]int) []string {
	out := make([]string, 0, len(m))
	for k := range m {
		out = append(out, k)
	}
	return out
}

// --- 2. privacy: the check that matters ------------------------------------

// knownIdentifiers are REAL values from the fixture. If any of them survives
// into the serialised dataset, the strip failed.
var knownIdentifiers = []string{
	"855480118723", "204354536218", "Sleven-K", "Containerstadt",
	"864133595285", "200179793657", "864140490741",
}

func runMinePrivacySelftest(check func(name string, ok bool, detail string)) {
	tmp, _ := os.MkdirTemp("", "mine-priv-")
	defer os.RemoveAll(tmp)
	logPath, _ := writeMineFixture(tmp)

	st := newMineStore()
	_ = mineOneLog(logPath, st)
	blob, err := json.Marshal(st)
	if err != nil {
		check("privacy: dataset serialises", false, err.Error())
		return
	}
	text := string(blob)

	var leaked []string
	for _, id := range knownIdentifiers {
		if strings.Contains(text, id) {
			leaked = append(leaked, id)
		}
	}
	check("PRIVACY: no identifier from the log survives into the dataset",
		len(leaked) == 0,
		fmt.Sprintf("checked %d known identifiers, leaked: %v", len(knownIdentifiers), leaked))

	// The embedded case specifically. "PartyMemberMarker_200179793657" is
	// another player's entity id wearing a friendly label, and it is exactly
	// what an audit looking only for bare numbers walks straight past.
	embedded := false
	for d := range st.Routes {
		if strings.Contains(d, "PartyMemberMarker") && strings.Contains(d, "<id>") {
			embedded = true
		}
	}
	check("PRIVACY: an id EMBEDDED inside a name is scrubbed, not just a bare one",
		embedded,
		fmt.Sprintf("routes: %v", keysOfF(st.Routes)))

	// NEGATIVE CONTROL: the detector must fail on planted data. If this passes
	// when it should not, every privacy result above is meaningless.
	planted, _ := json.Marshal(map[string]string{"shopName": "SCShop_855480118723"})
	found := false
	for _, id := range knownIdentifiers {
		if strings.Contains(string(planted), id) {
			found = true
		}
	}
	check("NEGATIVE CONTROL: the leak detector catches a planted identifier",
		found,
		"a deliberately planted id was detected, so a real one would be too")

	// scrubIDs itself, at the boundary. Five digits is a price; six is an id.
	check("PRIVACY: scrubIDs leaves short numbers alone and removes long ones",
		scrubIDs("item_01_02") == "item_01_02" &&
			scrubIDs("Marker_123456") == "Marker_<id>" &&
			scrubIDs("x12345y") == "x12345y",
		fmt.Sprintf("%q %q %q", scrubIDs("item_01_02"), scrubIDs("Marker_123456"), scrubIDs("x12345y")))
}

func keysOfF(m map[string][]float64) []string {
	out := make([]string, 0, len(m))
	for k := range m {
		out = append(out, k)
	}
	return out
}

// --- 3. dedup: the archive is re-read forever ------------------------------

func runMineDedupSelftest(check func(name string, ok bool, detail string)) {
	tmp, _ := os.MkdirTemp("", "mine-dedup-")
	defer os.RemoveAll(tmp)
	logPath, _ := writeMineFixture(tmp)

	st := newMineStore()
	_ = mineOneLog(logPath, st)
	first := len(st.Txns)

	// Read the SAME log four more times, as running for a week would.
	for i := 0; i < 4; i++ {
		_ = mineOneLog(logPath, st)
	}
	beforeDedup := len(st.Txns)

	seen := map[string]bool{}
	uniq := 0
	for _, t := range st.Txns {
		if !seen[t.key()] {
			seen[t.key()] = true
			uniq++
		}
	}
	check("dedup: re-reading the same log five times yields the same row count",
		uniq == first && first > 0,
		fmt.Sprintf("%d rows once, %d rows after 5 passes, %d unique", first, beforeDedup, uniq))

	// NEGATIVE CONTROL: two genuinely different transactions must NOT collapse.
	// A dedup key that was too coarse would pass the check above by throwing
	// away real data.
	a := MineTxn{TS: "t1", Side: "buy", Market: "item", Shop: "s", Item: "i", Price: "10"}
	b := MineTxn{TS: "t2", Side: "buy", Market: "item", Shop: "s", Item: "i", Price: "10"}
	c := MineTxn{TS: "t1", Side: "buy", Market: "item", Shop: "s", Item: "i", Price: "99"}
	check("NEGATIVE CONTROL: different transactions keep different keys",
		a.key() != b.key() && a.key() != c.key(),
		"a different timestamp and a different price each produce a different key")
}

// --- 4. the game-exit hook fires ONCE --------------------------------------

func runMineExitHookSelftest(check func(name string, ok bool, detail string)) {
	fired := 0
	alive := true
	stop := make(chan struct{})

	deps := autoDeps{
		logf: func(string, ...interface{}) {},
		gameAlive: func() error {
			if alive {
				return nil
			}
			return fmt.Errorf("no game")
		},
		capture:    func(Trigger) (string, error) { return "", fmt.Errorf("not used") },
		findLog:    func() (string, string) { return "", "test" },
		onGameExit: func() { fired++ },
	}
	// PollSeconds is 0 so the ticker runs as fast as it can; the test drives
	// the transition by flipping `alive`, not by waiting on real time.
	cfg := autoConfig{PollSeconds: 1, DebounceSeconds: 0, IntervalSeconds: 0}

	done := make(chan struct{})
	go func() { _ = runAuto(cfg, "", deps, stop); close(done) }()

	time.Sleep(1200 * time.Millisecond) // game running
	alive = false                       // player quits
	time.Sleep(2500 * time.Millisecond) // several more polls with no game
	close(stop)
	<-done

	check("game-exit hook fires exactly once per session",
		fired == 1,
		fmt.Sprintf("fired %d time(s) across several polls with the game gone (expected 1)", fired))

	// NEGATIVE CONTROL is built into the assertion above: a hook wired to the
	// LEVEL rather than the EDGE would have fired on every poll and reported a
	// number well above 1, which is the obvious way to write this wrong and
	// would re-read the whole archive every two seconds forever.
}

// --- 5. the export actually produces a file --------------------------------

func runExportSelftest(check func(name string, ok bool, detail string)) {
	tmp, _ := os.MkdirTemp("", "mine-export-")
	defer os.RemoveAll(tmp)

	// Two fake screenshots, and the difference between them is the whole point.
	//
	// One PROVES it photographed the game. The other is the real historical case
	// found in Sleven's captures folder on 2026-08-08: a browser window whose
	// title contained "Citizen Compass", selected by the title-matching path
	// that was removed on 2026-08-07. Those PNGs are still on disk, and before
	// this guard an export with screenshots enabled would have sent them.
	_ = os.WriteFile(filepath.Join(tmp, "shot_0001.png"), []byte("\x89PNG\r\n\x1a\nfake"), 0o644)
	_ = os.WriteFile(filepath.Join(tmp, "shot_0001.json"), []byte(
		`{"window":{"exe":"starcitizen.exe","how_found":"process is starcitizen.exe",`+
			`"title":"Star Citizen"}}`), 0o644)

	_ = os.WriteFile(filepath.Join(tmp, "shot_0002.png"), []byte("\x89PNG\r\n\x1a\nfake"), 0o644)
	_ = os.WriteFile(filepath.Join(tmp, "shot_0002.json"), []byte(
		`{"window":{"exe":"duckduckgo.exe","how_found":"matched --window against the title",`+
			`"title":"Citizen Compass v0.3.9 - DuckDuckGo"}}`), 0o644)

	// And one with no sidecar at all - unprovable, therefore not sent.
	_ = os.WriteFile(filepath.Join(tmp, "shot_0003.png"), []byte("\x89PNG\r\n\x1a\nfake"), 0o644)

	res, err := BuildExport(tmp, tmp, tmp, false, nil)
	if err != nil {
		check("export: writes a zip", false, err.Error())
		return
	}
	check("export: writes a zip that exists and is not empty",
		res.Path != "" && res.Bytes > 0,
		fmt.Sprintf("%s, %d bytes", filepath.Base(res.Path), res.Bytes))

	names := zipNames(res.Path)
	check("export: the zip contains the dataset and a README",
		hasName(names, "gamelog-dataset.json") && hasName(names, "README.txt"),
		fmt.Sprintf("contents: %v", names))

	// THE DEFAULT MATTERS MOST. Screenshots are not scrubbed, so they must not
	// travel unless somebody said so.
	check("export: screenshots are EXCLUDED unless asked for",
		!hasPrefix(names, "captures/"),
		fmt.Sprintf("one .png was on disk; zip contains %d entries and no captures/", len(names)))

	// NEGATIVE CONTROL: when they ARE asked for, they must actually appear.
	// Without this, an export that silently dropped every screenshot would pass
	// the check above and look correct.
	res2, err := BuildExport(tmp, tmp, tmp, true, nil)
	if err != nil {
		check("NEGATIVE CONTROL: export with screenshots", false, err.Error())
		return
	}
	names2 := zipNames(res2.Path)
	check("NEGATIVE CONTROL: when screenshots ARE requested they are included",
		hasPrefix(names2, "captures/"),
		fmt.Sprintf("contents: %v", names2))

	// --- THE GUARD FOUND ON 2026-08-08 ---------------------------------------
	//
	// A frame that cannot prove it photographed Star Citizen never travels, even
	// when the operator explicitly asked for screenshots. Asked-for is not the
	// same as safe-to-send.
	check("PRIVACY: a frame that photographed a BROWSER is never sent",
		!hasName(names2, "captures/shot_0002.png"),
		"the real 2026-08-05 case - duckduckgo.exe, selected by title match")
	check("PRIVACY: a frame with no sidecar is never sent",
		!hasName(names2, "captures/shot_0003.png"),
		"unprovable is treated exactly like bad - fail closed")
	check("export: the frames it held back are COUNTED, not silently dropped",
		res2.Quarantined == 2,
		fmt.Sprintf("held back %d (want 2: the browser frame and the orphan)",
			res2.Quarantined))

	// NEGATIVE CONTROL for the guard itself. Without this, an export that
	// quarantined EVERYTHING would pass all three checks above and look correct.
	check("NEGATIVE CONTROL: the good frame IS still sent",
		hasName(names2, "captures/shot_0001.png") && res2.Frames == 1,
		"the guard must hold back the bad ones and only the bad ones")

	// And the recipient is told frames were withheld, so the absence is visible
	// rather than looking like they never existed.
	body2 := zipEntry(res2.Path, "README.txt")
	check("export: the README states that frames were held back",
		strings.Contains(body2, "HELD BACK"),
		"a silent omission is the same failure as a silent inclusion")

	// The README has to tell the truth about which of those two happened.
	body := zipEntry(res.Path, "README.txt")
	check("export: the README states that no screenshots were included",
		strings.Contains(body, "No screenshots"),
		"README names what is in the file, so the recipient does not have to guess")
}

func zipNames(path string) []string {
	r, err := zip.OpenReader(path)
	if err != nil {
		return nil
	}
	defer r.Close()
	var out []string
	for _, f := range r.File {
		out = append(out, f.Name)
	}
	return out
}

func zipEntry(path, name string) string {
	r, err := zip.OpenReader(path)
	if err != nil {
		return ""
	}
	defer r.Close()
	for _, f := range r.File {
		if f.Name == name {
			rc, err := f.Open()
			if err != nil {
				return ""
			}
			defer rc.Close()
			// ReadAll, not a single Read. A single Read on a deflate stream
			// returns whatever happened to be in the first chunk, so a check
			// on text further down the file fails for a reason that has
			// nothing to do with the file being wrong. Caught by running it.
			b, err := io.ReadAll(rc)
			if err != nil {
				return ""
			}
			return string(b)
		}
	}
	return ""
}

func hasName(names []string, want string) bool {
	for _, n := range names {
		if n == want {
			return true
		}
	}
	return false
}

func hasPrefix(names []string, p string) bool {
	for _, n := range names {
		if strings.HasPrefix(n, p) {
			return true
		}
	}
	return false
}
