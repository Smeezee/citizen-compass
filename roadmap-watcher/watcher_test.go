package main

// watcher_test.go - the watcher must be able to SEE a Constellation card appear.
//
// A tripwire that reports "no change" forever is indistinguishable from a
// working one right up until the day it matters, which is the whole failure
// mode this project keeps logging. So the detection path is driven with a card
// that must fire, not only with the real board that currently must not.
//
// `watcher-go` already uses Go tests, so this follows that convention rather
// than inventing a second one.

import (
	"io"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"strings"
	"testing"
	"time"
)

func card(id int, name string) Card {
	return Card{ID: id, Name: name, Description: "a card", ReleaseID: 42}
}

// The three that are genuinely on Release View today, measured 2026-08-14.
func liveCards() []Card {
	return []Card{
		card(1, "RSI Constellation Phoenix"),
		card(2, "Merlin/Constellation Docking"),
		card(3, "RSI Constellation Taurus"),
		card(4, "Drake Cutlass Black"), // a non-matching card, so the filter has work to do
	}
}

func result(cards []Card) FetchResult {
	return FetchResult{Board: 1, Surface: "Release View", Cards: cards}
}

// THE BASELINE IS NOT NEWS. Three cards that have sat on the board for years
// must be recorded, not announced - announcing them is how the alert gets muted
// before the real signal arrives.
func TestFirstRunTakesABaselineAndReportsNothingNew(t *testing.T) {
	st := newState()
	changes := Diff(st, result(liveCards()), "Constellation")

	if len(st.Baseline) != 3 {
		t.Fatalf("baseline holds %d cards, want the 3 real ones", len(st.Baseline))
	}
	// Diff reports them; main is what frames the first run as a baseline. What
	// matters here is that the SECOND run is silent.
	if len(changes) != 3 {
		t.Fatalf("first pass produced %d changes, want 3 (they become the baseline)", len(changes))
	}
	again := Diff(st, result(liveCards()), "Constellation")
	if len(again) != 0 {
		t.Fatalf("second pass reported %d change(s) on an unchanged board: %+v", len(again), again)
	}
}

// THE SIGNAL. This is the entire point of the tool.
func TestANewConstellationCardIsDetected(t *testing.T) {
	st := newState()
	Diff(st, result(liveCards()), "Constellation") // baseline

	withRework := append(liveCards(), card(99, "RSI Constellation Mk5 Gold Standard"))
	changes := Diff(st, result(withRework), "Constellation")

	if len(changes) != 1 {
		t.Fatalf("want exactly 1 change, got %d: %+v", len(changes), changes)
	}
	c := changes[0]
	if c.Kind != "new-card" || c.Card != "RSI Constellation Mk5 Gold Standard" {
		t.Fatalf("wrong change reported: %+v", c)
	}
	if c.Surface != "Release View" {
		t.Fatalf("the surface must be named on every result, got %q", c.Surface)
	}
}

// An EDIT to an existing card, caught by the payload hash rather than by a date.
func TestAnEditedCardIsCaughtByTheFingerprint(t *testing.T) {
	st := newState()
	Diff(st, result(liveCards()), "Constellation")

	edited := liveCards()
	edited[2].Description = "now mentions a gold standard pass"
	changes := Diff(st, result(edited), "Constellation")

	if len(changes) != 1 || changes[0].Kind != "card-changed" {
		t.Fatalf("an edited card was not caught: %+v", changes)
	}
}

// THE TRAP THE ORDER WARNS ABOUT. updateDate reported 2024 for a card the UI
// renders as 2021. It is stored and must never move the fingerprint, or every
// alert becomes unreproducible by looking at the page.
func TestUpdateDateNeverTriggersAnything(t *testing.T) {
	a := card(3, "RSI Constellation Taurus")
	b := a
	b.UpdateDate = "Wed, 21 Aug 2024 20:25:52 +0000"

	if Fingerprint(a) != Fingerprint(b) {
		t.Fatal("updateDate moved the fingerprint - the exact trap the order names")
	}

	st := newState()
	Diff(st, result([]Card{a}), "Constellation")
	if ch := Diff(st, result([]Card{b}), "Constellation"); len(ch) != 0 {
		t.Fatalf("a changed updateDate raised %d alert(s): %+v", len(ch), ch)
	}
}

// Dates are RFC-1123, not ISO 8601. An ISO layout fails on every card, which
// reads as "no dates in the payload" rather than as a parsing bug.
func TestRoadmapDatesParse(t *testing.T) {
	if _, ok := parseRoadmapDate("Mon, 11 Jan 2021 00:00:00 +0000"); !ok {
		t.Fatal("RFC-1123Z date did not parse")
	}
	if _, ok := parseRoadmapDate("2021-01-11T00:00:00Z"); ok {
		t.Fatal("an ISO date parsed, which means the layout is looser than intended")
	}
	if _, ok := parseRoadmapDate(""); ok {
		t.Fatal("an empty date reported success")
	}
}

// Boards are keyed separately. Ids are only unique within a board, and this
// watcher polls two - keying on id alone would let a Squadron 42 card shadow a
// Release View one.
func TestBoardsDoNotShadowEachOther(t *testing.T) {
	st := newState()
	Diff(st, FetchResult{Board: 1, Surface: "Release View",
		Cards: []Card{card(7, "RSI Constellation Taurus")}}, "Constellation")
	changes := Diff(st, FetchResult{Board: 2, Surface: "Squadron 42",
		Cards: []Card{card(7, "RSI Constellation Something Else")}}, "Constellation")

	if len(changes) != 1 || changes[0].Surface != "Squadron 42" {
		t.Fatalf("a same-id card on another board was not seen as new: %+v", changes)
	}
}

// A corrupt store must NOT silently become an empty one - that would
// re-baseline against today's board and throw away the history the tool exists
// to hold, while reporting success.
func TestACorruptStateFileIsRefusedRatherThanReset(t *testing.T) {
	dir := t.TempDir()
	p := filepath.Join(dir, "state.json")
	if err := os.WriteFile(p, []byte("{not json"), 0o644); err != nil {
		t.Fatal(err)
	}
	if _, _, err := LoadState(p); err == nil {
		t.Fatal("a corrupt state file loaded cleanly, which would silently reset the baseline")
	}
}

// Hourly polling of somebody else's public endpoint is refused, not corrected.
func TestTooAggressiveACadenceIsRefused(t *testing.T) {
	c := defaultConfig()
	c.IntervalHours = 1
	if err := c.Validate(); err == nil {
		t.Fatal("an hourly cadence was accepted; the order rules it out explicitly")
	}
	c.IntervalHours = 4
	if err := c.Validate(); err != nil {
		t.Fatalf("the order's own cadence was rejected: %v", err)
	}
}

// §3A - THE SILENT FAILURE. RSI answers a dead or failed board with HTTP 200
// and the failure in the body. A client that branches on the status code reads
// that as a valid board with zero cards, which is byte-for-byte the same
// conclusion as "no Constellation card found" - on a tripwire whose only job is
// not to miss something.
//
// Driven through the real FetchBoard against a server that reproduces RSI's
// envelope exactly.
func TestABoardErrorAt200IsNotReadAsZeroCards(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK) // 200, exactly as RSI does
		io.WriteString(w, `{"success":0,"code":"ErrInvalidObject","msg":"Specified board does not exist.","data":null}`)
	}))
	defer srv.Close()

	cfg := defaultConfig()
	cfg.BoardURL = srv.URL + "/%d"
	res := FetchBoard(srv.Client(), cfg, 3)

	if res.Err == nil {
		t.Fatal("a failed board answered 200 and was accepted - this is the exact " +
			"silent failure: it would have been logged as '0 cards, 0 matching'")
	}
	if !strings.Contains(res.Err.Error(), "NOT 'no cards found'") {
		t.Fatalf("the error does not distinguish failure from emptiness: %v", res.Err)
	}
}

// NEGATIVE CONTROL: a genuine success envelope with genuinely no cards is NOT
// an error. Without this, the check above would be satisfied by a client that
// simply rejected everything.
func TestAGenuinelyEmptyBoardIsNotAnError(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		io.WriteString(w, `{"success":1,"code":"OK","msg":"OK","data":{"id":9,"name":"Quiet Board","releases":[]}}`)
	}))
	defer srv.Close()

	cfg := defaultConfig()
	cfg.BoardURL = srv.URL + "/%d"
	res := FetchBoard(srv.Client(), cfg, 9)

	if res.Err != nil {
		t.Fatalf("a real but empty board was reported as an error: %v", res.Err)
	}
	if res.Surface != "Quiet Board" || len(res.Cards) != 0 {
		t.Fatalf("surface=%q cards=%d", res.Surface, len(res.Cards))
	}
}

// §3B - a card carries the release it sits in, so a historical Constellation
// card can never be misread as news.
func TestCardsCarryTheirReleaseContext(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		io.WriteString(w, `{"success":1,"code":"OK","msg":"OK","data":{"id":1,"name":"Release View",
		 "releases":[{"name":"3.14","released":1,"cards":[
		   {"id":1,"name":"RSI Constellation Taurus","description":"RSI&#039;s hauler"}]}]}}`)
	}))
	defer srv.Close()

	cfg := defaultConfig()
	cfg.BoardURL = srv.URL + "/%d"
	res := FetchBoard(srv.Client(), cfg, 1)
	if res.Err != nil {
		t.Fatal(res.Err)
	}
	if len(res.Cards) != 1 {
		t.Fatalf("got %d cards", len(res.Cards))
	}
	c := res.Cards[0]
	if c.Release != "3.14" || !c.Released {
		t.Fatalf("release context missing: release=%q released=%v", c.Release, c.Released)
	}
	// Descriptions are entity-encoded; a search for an apostrophe phrase would
	// otherwise silently return nothing.
	if !strings.Contains(c.Description, "RSI's") {
		t.Fatalf("description was not unescaped: %q", c.Description)
	}
}

// --- the addendum: a stopped watcher must not look like one finding nothing --

// RULE 12, AS THE ADDENDUM DEMANDS IT: "a staleness detector that has never
// been observed reporting stale is the same category of thing it exists to
// catch." So the stale state is reached, not reasoned about.
func TestStaleIsActuallyReachable(t *testing.T) {
	cfg := defaultConfig() // 4h cadence, 3 cycles -> stale after 12h
	now := time.Now().UTC()

	st := newState()
	st.LastGoodScheduled = now.Add(-13 * time.Hour).Format(time.RFC3339)
	stale, why := scheduledIsStale(st, cfg, now)
	if !stale {
		t.Fatal("13 hours without a scheduled run was reported as healthy")
	}
	if !strings.Contains(why, "may be dead") {
		t.Fatalf("the reason does not say what it means: %q", why)
	}

	// NEGATIVE CONTROL. Without this, a detector that always says STALE would
	// pass the check above while being useless.
	st.LastGoodScheduled = now.Add(-1 * time.Hour).Format(time.RFC3339)
	if stale, _ := scheduledIsStale(st, cfg, now); stale {
		t.Fatal("a run an hour ago was reported as stale")
	}
}

// A watcher that has only ever been hand-run is STALE, because the timer has
// never produced anything. This is the case where "nothing new" is most
// reassuring and least earned.
func TestOnlyEverHandRunCountsAsStale(t *testing.T) {
	cfg := defaultConfig()
	st := newState()
	st.LastGood = time.Now().UTC().Format(time.RFC3339) // a manual run just succeeded
	st.LastGoodScheduled = ""

	stale, why := scheduledIsStale(st, cfg, time.Now().UTC())
	if !stale {
		t.Fatal("a watcher whose timer has never completed a run was called healthy")
	}
	if !strings.Contains(why, "NEVER") {
		t.Fatalf("reason: %q", why)
	}
}

// An unreadable timestamp must be treated as stale. Assuming health from a
// value you could not parse is how a dead watcher stays invisible.
func TestAnUnreadableTimestampIsStaleNotHealthy(t *testing.T) {
	st := newState()
	st.LastGoodScheduled = "not a time"
	if stale, _ := scheduledIsStale(st, defaultConfig(), time.Now().UTC()); !stale {
		t.Fatal("an unparseable timestamp was treated as healthy")
	}
}

// The threshold follows the cadence. A threshold in absolute hours silently
// becomes wrong the moment somebody changes the interval.
func TestStaleThresholdFollowsTheCadence(t *testing.T) {
	c := defaultConfig()
	c.IntervalHours = 4
	if c.StaleAfter() != 12*time.Hour {
		t.Fatalf("4h x 3 cycles = %s, want 12h", c.StaleAfter())
	}
	c.IntervalHours = 8
	if c.StaleAfter() != 24*time.Hour {
		t.Fatalf("8h x 3 cycles = %s, want 24h", c.StaleAfter())
	}
}
