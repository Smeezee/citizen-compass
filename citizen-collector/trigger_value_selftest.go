package main

// trigger_value_selftest.go - checks for the capture-value gate and the two
// triggers that were missing.
//
// This exists because of a complaint, not a crash. Sleven looked through a
// session's captures and said they were "random shots of nothing". The tally of
// what fired those 40 frames is in auto.go's Trigger doc comment; the short
// version is that 23 of 40 were menus, loading screens and spawns, and zero
// were shops.
//
// So the checks below assert two things that were both true before and are the
// wrong way round:
//
//   - a menu transition must NOT spend a frame
//   - a shop terminal opening MUST
//
// EVERY CHECK HAS A NEGATIVE CONTROL (hard rule 12). The important one is that
// the gate can be turned off: without that, "low value triggers do not capture"
// would also pass on a build where NOTHING captures.

import (
	"fmt"
	"strings"
	"time"
)

func runTriggerValueSelftest(check func(name string, ok bool, detail string)) {
	// --- the two new triggers are produced at all ---------------------------

	d := &autoDetector{primed: true}

	// Real 4.10 line shapes, taken from Sleven's own logs rather than invented.
	shopLine := `<2026-08-07T22:20:37.004Z> [Notice] <RequestLocationInventory> ` +
		`Player[Sleven-K] requested inventory for Location[RR_JP_NyxCastra]`
	buyLine := `<2026-08-07T21:30:00.000Z> [Notice] ` +
		`<CEntityComponentShoppingProvider::SendStandardItemBuyRequest> Sending ` +
		`SShopBuyRequest - playerId[855480118723] shopName[SCShop_Cordrys_Levski-001] ` +
		`client_price[1000.000000] itemName[vgl_flightsuit_01_01_01] quantity[1]`
	menuLine := `<2026-08-07T22:19:07.255Z> Context Establisher Done ` +
		`map="megamap" gamerules="SC_Frontend"`
	loadLine := `<2026-08-07T22:19:10.000Z> Loading screen for Pyro : SC_Frontend ` +
		`closed after 4.58 seconds`

	findTrigger := func(ts []Trigger, field string) *Trigger {
		for i := range ts {
			if ts[i].Field == field {
				return &ts[i]
			}
		}
		return nil
	}

	shopTs := d.Feed(shopLine)
	shopT := findTrigger(shopTs, "terminal_open")
	check("trigger: opening a shop terminal now fires",
		shopT != nil, "RequestLocationInventory was read by the miner and by nothing else")
	if shopT != nil {
		check("trigger: the shop terminal is HIGH value",
			shopT.isHigh(), "prices are on the screen at this exact moment")
		check("trigger: it names the place it opened",
			shopT.To == "RR_JP_NyxCastra", "got "+shopT.To)
	}

	buyT := findTrigger(d.Feed(buyLine), "transaction")
	check("trigger: a purchase now fires",
		buyT != nil, "the strongest signal in the log - the player is at a kiosk")
	if buyT != nil {
		check("trigger: the transaction is HIGH value", buyT.isHigh(), buyT.To)
		check("trigger: it distinguishes buy from sell and item from commodity",
			buyT.To == "item buy", "got "+buyT.To)
	}

	// --- and the noisy ones are marked low ----------------------------------

	menuT := findTrigger(d.Feed(menuLine), "gamerules")
	check("trigger: a change to the main menu is LOW value",
		menuT != nil && !menuT.isHigh(),
		"SC_Frontend IS the main menu - 10 of the 40 audited frames were this")

	loadT := findTrigger(d.Feed(loadLine), "loading_screen")
	check("trigger: a loading screen is LOW value",
		loadT != nil && !loadT.isHigh(),
		"3 of the 40 audited frames were photographs of loading screens")

	// --- the gate actually gates -------------------------------------------

	base := time.Date(2026, 8, 8, 12, 0, 0, 0, time.UTC)
	fake := base
	clock := func() time.Time { return fake }

	// Interval off, so anything that fires can only have come from a trigger.
	gated := autoConfig{PollSeconds: 2, DebounceSeconds: 0, IntervalSeconds: 0}
	r := newAutoRunner(gated, clock)

	fake = base.Add(10 * time.Second)
	lowOnly := r.decide([]Trigger{
		{Kind: "state_change", Field: "gamerules", To: "SC_Frontend", Value: valueLow},
		{Kind: "event", Field: "loading_screen", Value: valueLow},
	})
	check("gate: a poll of nothing but menu and loading takes NO picture",
		lowOnly == nil, "this is the 23-of-40 case, and it now costs nothing")
	check("gate: but the skipped ones are still reported",
		len(r.skipped) == 2,
		"silently dropping them would be indistinguishable from a broken detector")

	fake = base.Add(20 * time.Second)
	high := r.decide([]Trigger{
		{Kind: "state_change", Field: "gamerules", To: "SC_Frontend", Value: valueLow},
		{Kind: "event", Field: "terminal_open", To: "RR_JP_NyxCastra", Value: valueHigh},
	})
	check("gate: a shop in the same poll as a menu change DOES capture",
		high != nil && high.Field == "terminal_open",
		"and the chosen trigger is the shop, not whichever came first")

	// NEGATIVE CONTROL #1. If the gate were simply "never capture", every check
	// above would still pass. Turning it off must bring the low-value frames
	// back.
	ungated := autoConfig{PollSeconds: 2, DebounceSeconds: 0, IntervalSeconds: 0,
		CaptureLowValue: true}
	r2 := newAutoRunner(ungated, clock)
	fake = base.Add(30 * time.Second)
	back := r2.decide([]Trigger{
		{Kind: "state_change", Field: "gamerules", To: "SC_Frontend", Value: valueLow},
	})
	check("NEGATIVE CONTROL: capture_low_value=true brings the menu frames back",
		back != nil && len(r2.skipped) == 0,
		"proves the gate is a gate and not a wall")

	// NEGATIVE CONTROL #2. An unset Value must capture. A trigger added later by
	// someone who does not know about this field should cost a wasted frame, not
	// vanish - a missed moment cannot be recovered, a wasted frame can be deleted.
	r3 := newAutoRunner(gated, clock)
	fake = base.Add(40 * time.Second)
	unset := r3.decide([]Trigger{{Kind: "event", Field: "something_new_nobody_tagged"}})
	check("NEGATIVE CONTROL: a trigger with no value set still captures",
		unset != nil,
		"failing open is the right direction here - the two failure modes are not symmetric")

	// --- the shared-pattern guarantee ---------------------------------------
	//
	// The detector borrows reMineLocation and reMineTxn from gamelog_mine.go
	// rather than keeping its own copies. If someone re-adds a local copy, the
	// two will drift and the day CIG changes the format one will keep matching
	// and mask the other's failure.
	check("shared patterns: the shop pattern the detector uses is the miner's",
		reMineLocation.MatchString(shopLine) && reMineTxn.MatchString(buyLine),
		"one definition, so a CIG rename breaks both at once and is noticed")

	// NEGATIVE CONTROL: those patterns must not match an unrelated line, or the
	// check above would pass for any input at all.
	check("NEGATIVE CONTROL: the shared patterns reject an unrelated line",
		!reMineLocation.MatchString(menuLine) && !reMineTxn.MatchString(menuLine),
		"a pattern that matches everything confirms nothing")

	// --- what this would have done to the audited session -------------------
	//
	// Not an assertion about the fix, a statement of the arithmetic, printed so
	// the change is measurable rather than asserted.
	kept, dropped := 0, 0
	for _, tr := range []Trigger{
		{Value: valueLow}, {Value: valueLow}, {Value: valueLow}, // menu x3
		{Value: valueLow}, {Value: valueLow},                    // spawn x2
		{Value: valueHigh},                                      // hotkey
	} {
		if tr.isHigh() {
			kept++
		} else {
			dropped++
		}
	}
	check("gate: the arithmetic is stated, not assumed",
		kept == 1 && dropped == 5,
		fmt.Sprintf("on a 6-frame sample shaped like the audit: %d kept, %d dropped (%s)",
			kept, dropped, strings.TrimSpace("23 of 40 real frames were of this shape")))
}
