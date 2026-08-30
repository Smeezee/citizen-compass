package main

// board.go - the stage 1 client: RSI's public roadmap board JSON.
//
// GET https://robertsspaceindustries.com/api/roadmap/v1/boards/N
// Plain public JSON. No body, no headers, no login.
//
// THERE IS NO 304 PATH, AND ONE MUST NOT BE BUILT. Rev 1 asked for conditional
// requests to be tried rather than assumed; they were tried, by CIC and again
// here. `boards/1` returns no ETag, no Last-Modified, and sets
// Cache-Control: no-store. Both validators were sent and a full 200 came back
// either way. The question is closed - building a 304 path now would be dead
// code that looks like an optimisation.
//
// LEAVE Accept-Encoding UNSET. Go's net/http negotiates gzip transparently and
// decompresses for you: 149 KB on the wire, 820 KB decoded. Setting the header
// by hand, or building a Transport with DisableCompression, silently turns that
// into an 820 KB pull - 5.5x for nothing. It looks like an omission, which is
// why this comment exists.

import (
	"encoding/json"
	"fmt"
	"html"
	"io"
	"net/http"
	"strings"
	"time"
)

// Board is only the parts of the payload this tool reads. The response carries
// far more; trimming here keeps the stored record small and makes it obvious
// what a change in an unread field cannot break.
type Board struct {
	// THE ENVELOPE IS THE ONLY HONEST STATUS. RSI answers a dead or failed
	// board with HTTP 200 and the failure in the body:
	//
	//	{"success":0,"code":"ErrInvalidObject",
	//	 "msg":"Specified board does not exist.","data":null}
	//
	// A client that branches on the status code parses that into a Board with
	// no releases and reports "0 cards, 0 matching" - which is byte-for-byte
	// the same output as a genuine clean negative. On a tripwire whose entire
	// job is not to miss something, that is the worst available failure.
	Success int    `json:"success"`
	Code    string `json:"code"`
	Msg     string `json:"msg"`

	Data struct {
		ID   int    `json:"id"`
		Name string `json:"name"`

		// DECLARED 2026-08-30, Q5c. RSI puts the answer here:
		//
		//	"Live Version: 4.10.0 . Latest Roadmap Roundup: 08/26/2026
		//	 . PTU Version: o"
		//
		// This struct did not ask for it, so Go discarded it at unmarshal on
		// every poll for months while the watcher reported on cards instead
		// and the site stayed a full patch behind. An undeclared field is not
		// a missing field - it is a field being thrown away silently, which is
		// the same shape as the `success` envelope above.
		Description string `json:"description"`

		LastUpdated int64 `json:"last_updated"`
		Releases    []struct {
			Name string `json:"name"`
			// AN INT, NOT A BOOL. RSI sends `"released": 1` / `0`. Declaring it
			// bool makes the WHOLE BOARD fail to unmarshal - which this build
			// did on its first live run after the field was added.
			//
			// It failed LOUDLY ("NOTHING WAS POLLED ... it is 'we did not
			// look'") rather than quietly returning zero cards, which is the
			// only reason it was a five-minute fix instead of a silent tripwire.
			IsReleased int    `json:"released"`
			Cards      []Card `json:"cards"`
		} `json:"releases"`
	} `json:"data"`
}

// Card is one deliverable on the board.
type Card struct {
	ID          int    `json:"id"`
	Name        string `json:"name"`
	Description string `json:"description"`
	// BOTH DATES ARE STORED AND NEITHER IS TRIGGERED ON. The order found the
	// API reporting "Wed, 21 Aug 2024" for a card the UI renders as
	// "Updated Aug. 11th, 2021" - same card, three years apart. A tripwire on
	// that raises alerts nobody can reproduce by looking at the page.
	//
	// Measured 2026-08-14: on all three Constellation cards this field is
	// EMPTY, so the warning holds for a second reason.
	UpdateDate string `json:"updateDate"`
	ReleaseID  int    `json:"release_id"`

	// THE RELEASE THIS CARD SITS IN, carried on the card itself.
	//
	// "Constellation" already appears 23 times on Release View and every
	// occurrence is historical. A stored record that does not carry its own
	// context gets misread eventually - with these, "Constellation card,
	// release 3.14, Released" can never be mistaken for news.
	//
	// FILLED IN BY FetchBoard FROM THE ENCLOSING RELEASE, NOT BY THE API - and
	// the tags say so, which is not cosmetic.
	//
	// Tagging this `json:"released"` made the decoder try to fill it from the
	// card's OWN `released` field, which RSI sends as a number. The whole board
	// then failed to unmarshal. A derived field that shares a name with an API
	// field will be fed by the API whether you meant it or not.
	Release  string `json:"release_name"`
	Released bool   `json:"is_released"`
}

// FetchResult is one poll of one board.
type FetchResult struct {
	Board   int
	Surface string // the board's own name - "Release View", "Squadron 42"

	// Description is the board's own status line, Q5c:
	//
	//	"Live Version: 4.10.0 . Latest Roadmap Roundup: 08/26/2026
	//	 . PTU Version: o"
	//
	// Carried through rather than parsed here: FetchBoard's job is what came
	// off the wire, and reading meaning out of prose belongs in livever.go
	// where the failure modes are tested.
	Description string

	Status      int
	Bytes       int
	LastUpdated int64
	Cards       []Card
	Err         error
}

// FetchBoard performs one GET. There is no conditional variant - see the note
// at the top of this file; RSI offers no validators and sets no-store.
func FetchBoard(client *http.Client, cfg Config, board int) FetchResult {
	res := FetchResult{Board: board}
	url := fmt.Sprintf(cfg.BoardURL, board)

	req, err := http.NewRequest(http.MethodGet, url, nil)
	if err != nil {
		res.Err = err
		return res
	}
	req.Header.Set("User-Agent", cfg.UserAgent)
	req.Header.Set("Accept", "application/json")
	// Deliberately NO Accept-Encoding - see the note above.

	resp, err := client.Do(req)
	if err != nil {
		res.Err = err
		return res
	}
	defer resp.Body.Close()

	res.Status = resp.StatusCode
	if resp.StatusCode != http.StatusOK {
		res.Err = fmt.Errorf("HTTP %d from board %d", resp.StatusCode, board)
		return res
	}

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		res.Err = err
		return res
	}
	res.Bytes = len(body)

	var b Board
	if err := json.Unmarshal(body, &b); err != nil {
		res.Err = fmt.Errorf("board %d returned something that is not the JSON "+
			"this tool understands: %w", board, err)
		return res
	}

	// THE CHECK THAT STOPS A FAILURE READING AS A CLEAN NEGATIVE.
	// Branch on the envelope, never on the status code.
	if b.Success != 1 {
		res.Err = fmt.Errorf("board %d answered HTTP 200 but the body says it "+
			"FAILED: success=%d code=%q msg=%q. This is NOT 'no cards found'",
			board, b.Success, b.Code, b.Msg)
		return res
	}
	res.Surface = b.Data.Name
	res.Description = b.Data.Description
	res.LastUpdated = b.Data.LastUpdated
	for _, rel := range b.Data.Releases {
		for _, c := range rel.Cards {
			c.Release = rel.Name
			c.Released = rel.IsReleased == 1
			// DESCRIPTIONS ARE HTML-ENTITY-ENCODED - "RSI&#039;s". Title
			// matching is safe; description matching is not, and a search for
			// an apostrophe-bearing phrase silently returns nothing. Unescaped
			// on the way in so nothing downstream has to remember.
			c.Description = html.UnescapeString(c.Description)
			c.Name = html.UnescapeString(c.Name)
			res.Cards = append(res.Cards, c)
		}
	}
	return res
}

// Matches returns the cards whose title contains the watch term.
//
// TITLE ONLY, deliberately. The order says title matching is safe and
// description matching is not; unescaping above makes description matching
// possible later, but it is not what this triggers on.
func Matches(cards []Card, watch string) []Card {
	var out []Card
	// Q5a, 2026-08-30: "*" IS EVERY CARD.
	//
	// The filter was "Constellation" - seeded on one test ship and never
	// widened - and a board-wide question cannot be answered through a
	// one-ship filter. Note that a substring match would ALREADY have let "*"
	// through as a literal and matched nothing, which reads exactly like a
	// quiet board. That is the failure this branch removes.
	if strings.TrimSpace(watch) == "*" {
		return append(out, cards...)
	}
	w := strings.ToLower(watch)
	for _, c := range cards {
		if strings.Contains(strings.ToLower(c.Name), w) {
			out = append(out, c)
		}
	}
	return out
}

// parseRoadmapDate reads RSI's RFC-1123 dates.
//
// "Mon, 11 Jan 2021 00:00:00 +0000" - NOT ISO 8601. An ISO layout returns an
// error on every card, which reads as "no dates in the payload" rather than as
// a parsing bug. Kept even though nothing triggers on dates: they are stored,
// and a stored value that failed to parse should be visibly empty rather than
// quietly wrong.
func parseRoadmapDate(s string) (time.Time, bool) {
	s = strings.TrimSpace(s)
	if s == "" {
		return time.Time{}, false
	}
	if t, err := time.Parse(time.RFC1123Z, s); err == nil {
		return t, true
	}
	if t, err := time.Parse(time.RFC1123, s); err == nil {
		return t, true
	}
	return time.Time{}, false
}
