package main

// watcher_test.go - most of what follows is a feed that LOOKS fine and is not:
// a failure inside a 200, a 200 with nothing readable in it, a newest post whose
// age never moves, an endpoint nobody verified. Each must be said out loud, and
// none may read as "CIG was quiet".

import (
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"strings"
	"sync"
	"testing"
	"time"

	"citizencompass/pkg/pipelinelog"
)

// feed is a planted server whose body can be changed between passes.
type feed struct {
	mu     sync.Mutex
	body   string
	status int
}

func (f *feed) set(status int, body string) { f.mu.Lock(); f.status, f.body = status, body; f.mu.Unlock() }
func (f *feed) ServeHTTP(w http.ResponseWriter, _ *http.Request) {
	f.mu.Lock()
	defer f.mu.Unlock()
	w.WriteHeader(f.status)
	_, _ = w.Write([]byte(f.body))
}

const boardOK = `{"success":1,"data":{"description":"Live Version: 4.10.0 ▪ Latest Roadmap Roundup: 08/26/2026 ▪ PTU Version: ø"}}`

func jsonFeed(ids ...string) string {
	var parts []string
	for _, id := range ids {
		parts = append(parts, `{"id":`+id+`,"title":"T`+id+`","url":"/p/`+id+`","time":"5 minutes ago"}`)
	}
	return `{"success":1,"data":{"items":[` + strings.Join(parts, ",") + `]}}`
}

type rig struct {
	t      *testing.T
	root   string
	p      Paths
	cfg    Config
	devt   *feed
	board  *feed
	log    *pipelinelog.Logger
	client *http.Client
}

func newRig(t *testing.T) *rig {
	t.Helper()
	root := t.TempDir()
	devt := &feed{status: 200, body: jsonFeed("101", "100")}
	board := &feed{status: 200, body: boardOK}
	sd := httptest.NewServer(devt)
	sb := httptest.NewServer(board)
	t.Cleanup(sd.Close)
	t.Cleanup(sb.Close)
	cfg := defaultConfig()
	cfg.LiveURL = sb.URL
	cfg.Sources[0] = Source{Name: "devtracker", Shelf: "devtracker", URL: sd.URL, Method: "GET",
		Format: "json", ItemsPath: "data.items", IDField: "id", TitleField: "title", URLField: "url",
		TimeField: "time", SuccessField: "success", SuccessValue: "1", URLPrefix: "https://example.invalid",
		CacheBustParam: "cb"}
	if err := cfg.Validate(); err != nil {
		t.Fatal(err)
	}
	return &rig{t: t, root: root, p: pathsFor(root), cfg: cfg, devt: devt, board: board,
		log: pipelinelog.New(root, "rsi-watcher-test"), client: &http.Client{Timeout: 5 * time.Second}}
}

func (r *rig) run(at time.Time) Result { return runOnce(r.log, r.cfg, r.p, r.client, "manual", at) }

func (r *rig) shelf(name string) []string {
	ents, _ := os.ReadDir(filepath.Join(r.p.Shelf, name))
	var out []string
	for _, e := range ents {
		out = append(out, e.Name())
	}
	return out
}

var t0 = time.Date(2026, 9, 14, 10, 0, 0, 0, time.UTC)

func TestFirstPassIsABaselineNotNews(t *testing.T) {
	r := newRig(t)
	res := r.run(t0)
	if res.Outcome != "BASELINE" || len(res.Cards) != 0 {
		t.Fatalf("first pass: outcome %q, cards %v - a baseline is never news", res.Outcome, res.Cards)
	}
	if _, err := os.Stat(r.p.Wake); err == nil {
		t.Fatal("a baseline wrote a wake marker")
	}
}

func TestANewIDBecomesOneCardAndAWake(t *testing.T) {
	r := newRig(t)
	r.run(t0)
	r.devt.set(200, jsonFeed("102", "101", "100"))
	res := r.run(t0.Add(time.Hour))
	if res.Outcome != "NEW" || len(res.Cards) != 1 {
		t.Fatalf("outcome %q cards %v, want NEW with exactly one card", res.Outcome, res.Cards)
	}
	if got := r.shelf("devtracker"); len(got) != 1 || got[0] != "102.json" {
		t.Fatalf("shelf holds %v, want [102.json]", got)
	}
	b, _ := os.ReadFile(filepath.Join(r.p.Shelf, "devtracker", "102.json"))
	if !strings.Contains(string(b), `"url": "https://example.invalid/p/102"`) {
		t.Fatalf("the card lost the source's own url: %s", b)
	}
	if _, err := os.Stat(r.p.Wake); err != nil {
		t.Fatal("new item, but no wake marker")
	}
}

func TestNothingNewWritesNoCardAndNoWake(t *testing.T) {
	r := newRig(t)
	r.run(t0)
	r.devt.set(200, `{"success":1,"data":{"items":[{"id":101,"title":"T","url":"u","time":"6 minutes ago"},{"id":100}]}}`)
	res := r.run(t0.Add(time.Hour))
	if res.Outcome != "NOTHING NEW" || len(res.Cards) != 0 {
		t.Fatalf("outcome %q cards %v", res.Outcome, res.Cards)
	}
	if _, err := os.Stat(r.p.Wake); err == nil {
		t.Fatal("a quiet pass wrote a wake marker")
	}
}

func TestAFailureInsideA200IsNotQuiet(t *testing.T) {
	r := newRig(t)
	r.run(t0)
	// Valid items INSIDE a failure envelope, so only the envelope check can refuse it
	// (with "data":null the parse broke anyway, and a mutant that dropped the check survived).
	r.devt.set(200, `{"success":0,"msg":"nope","data":{"items":[{"id":102,"title":"T","url":"u","time":"1 minute ago"}]}}`)
	res := r.run(t0.Add(time.Hour))
	if len(res.Failed) != 1 || len(res.Polled) != 0 {
		t.Fatalf("failed %v polled %v - a failure envelope must be a failure", res.Failed, res.Polled)
	}
}

func TestA200WithNothingReadableIsNotQuiet(t *testing.T) {
	r := newRig(t)
	r.devt.set(200, `{"success":1,"data":{"items":[]}}`)
	if res := r.run(t0); len(res.Failed) != 1 {
		t.Fatalf("an empty 200 read as %+v - it must be DID NOT LOOK for that source", res)
	}
}

func TestNothingReadAtAllIsDidNotLook(t *testing.T) {
	r := newRig(t)
	r.run(t0)
	st1, _, _ := LoadState(r.p.State)
	r.devt.set(503, "down")
	r.board.set(503, "down")
	res := r.run(t0.Add(time.Hour))
	if res.Outcome != "DID NOT LOOK" {
		t.Fatalf("outcome %q, want DID NOT LOOK", res.Outcome)
	}
	st2, _, _ := LoadState(r.p.State)
	if st2.LastGood != st1.LastGood {
		t.Fatal("a pass that read nothing advanced LastGood")
	}
}

func TestAStuckRelativeAgeIsStale(t *testing.T) {
	r := newRig(t)
	r.run(t0)
	r.run(t0.Add(30 * time.Minute)) // same newest post, same "5 minutes ago"
	res := r.run(t0.Add(3 * time.Hour))
	if len(res.Stale) != 1 {
		t.Fatalf("the newest post read '5 minutes ago' for three hours and stale is %v", res.Stale)
	}
}

func TestAnUnconfiguredSourceIsNamedEveryRun(t *testing.T) {
	r := newRig(t)
	res := r.run(t0)
	if strings.Join(res.NotConfigured, ",") != "comm-link,patchbot" {
		t.Fatalf("not configured %v", res.NotConfigured)
	}
}

func TestABuildChangeIsACard(t *testing.T) {
	r := newRig(t)
	r.run(t0)
	r.board.set(200, `{"success":1,"data":{"description":"Live Version: 4.10.1 ▪ PTU Version: 4.11.0"}}`)
	res := r.run(t0.Add(time.Hour))
	got := strings.Join(r.shelf("patches"), ",")
	if res.Outcome != "NEW" || got != "live-4.10.1.json,ptu-4.11.0.json" {
		t.Fatalf("outcome %q, patches shelf %q", res.Outcome, got)
	}
}

func TestACardIsNeverWrittenTwice(t *testing.T) {
	dir := t.TempDir()
	c := Card{Shelf: "devtracker", ID: "7", Title: "first"}
	if _, wrote, err := WriteCard(dir, c); err != nil || !wrote {
		t.Fatal(err)
	}
	c.Title = "second"
	if _, wrote, _ := WriteCard(dir, c); wrote {
		t.Fatal("an existing card was overwritten")
	}
	b, _ := os.ReadFile(filepath.Join(dir, "devtracker", "7.json"))
	if !strings.Contains(string(b), "first") {
		t.Fatal("the first record was lost")
	}
}

func TestAnIDCannotClimbOutOfItsShelf(t *testing.T) {
	if n := fileNameFor(`..\..\x/y`); strings.ContainsAny(n, `/\`) || strings.HasPrefix(n, "..") {
		t.Fatalf("unsafe file name %q", n)
	}
}

func TestConfigRefusals(t *testing.T) {
	bad := defaultConfig()
	bad.IntervalHours = 0.25
	if bad.Validate() == nil {
		t.Fatal("a 15-minute cadence was accepted")
	}
	bad = defaultConfig()
	bad.Sources[1].URL = "https://x.invalid"
	bad.Sources[1].Method = "GET"
	bad.Sources[1].Format = "html"
	bad.Sources[1].ItemRegex = `<a href="(.*?)">`
	if bad.Validate() == nil {
		t.Fatal("an html source with no (?P<id>) group was accepted")
	}
	bad = defaultConfig()
	bad.Sources[2].Shelf = "../escape"
	if bad.Validate() == nil {
		t.Fatal("a shelf that climbs out of sc-brain was accepted")
	}
}

func TestUnknownSettingsKeysAreRefused(t *testing.T) {
	dir := t.TempDir()
	_ = os.WriteFile(filepath.Join(dir, configFileName), []byte(`{"interval_hours":1,"intervall":2}`), 0o644)
	if _, _, err := LoadConfig(dir); err == nil {
		t.Fatal("a misspelt key was silently ignored")
	}
}

func TestParseBuildFailsLoud(t *testing.T) {
	for _, s := range []string{"", "Roadmap updates weekly.", "LiveVersion 4.10.0"} {
		if _, _, err := ParseBuild(s); err == nil {
			t.Fatalf("%q read as a build", s)
		}
	}
	if live, ptu, err := ParseBuild("Live Version: 4.10.0 ▪ PTU Version: ø"); err != nil || live != "4.10.0" || ptu != ptuNone {
		t.Fatalf("got %q %q %v", live, ptu, err)
	}
	if _, _, err := ParseBuild("Live Version: 4.10.0 ▪ PTU Version: soon"); err == nil {
		t.Fatal("a PTU line in no accepted shape was read")
	}
}

// THE BOARD AS IT READ ON 2026-09-13 19:58, VERBATIM - the rewording the first
// real -check refused, loudly, instead of calling it quiet.
func TestParseBuildTheRealSeptemberShape(t *testing.T) {
	d := "Live Version: 4.10.0 ([more info](https://robertsspaceindustries.com/comm-link/transmission/21242-Alpha-410-Siege-Of-Orison)) " +
		"▪ Latest Roadmap Roundup: 09/09/2026 ([more info](https://robertsspaceindustries.com/spectrum/community/SC/forum/3/thread/roadmap-roundup-september-9-2026)) " +
		"▪ PTU Version: Alpha 4.10.1 PTU - 12578875"
	live, ptu, err := ParseBuild(d)
	if err != nil || live != "4.10.0" || ptu != "4.10.1 (12578875)" {
		t.Fatalf("got live %q ptu %q err %v", live, ptu, err)
	}
	if _, p2, _ := ParseBuild(strings.Replace(d, "12578875", "12578999", 1)); p2 == ptu {
		t.Fatal("a new PTU build under the same version must read as a different value")
	}
}

func TestHTMLItemsNeedAnID(t *testing.T) {
	s := Source{Format: "html", ItemRegex: `<li data-id="(?P<id>[^"]*)"><a href="(?P<url>[^"]*)">(?P<title>[^<]*)</a>`}
	items, err := parseHTML(`<li data-id="9"><a href="/a">A &amp; B</a><li data-id="10"><a href="/b">C</a>`, s)
	if err != nil || len(items) != 2 || items[0].Title != "A & B" {
		t.Fatalf("items %+v err %v", items, err)
	}
	if _, err := parseHTML(`<li data-id=""><a href="/a">A</a>`, s); err == nil {
		t.Fatal("an empty id was skipped rather than refused")
	}
}
