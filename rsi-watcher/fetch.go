package main

// fetch.go - one request to one source, and the items it names.
//
// NOTHING HERE MAY READ AS QUIET WHEN IT DID NOT LOOK. A non-200, a failure
// envelope inside a 200, or a 200 that yields zero items are all ERRORS - "0
// new items" is only ever said about a response that was read and understood.

import (
	"encoding/json"
	"fmt"
	"html"
	"io"
	"net/http"
	"net/url"
	"regexp"
	"strconv"
	"strings"
	"time"
)

// Item is one post as the source names it.
type Item struct {
	ID    string `json:"id"`
	Title string `json:"title"`
	URL   string `json:"url"`
	Time  string `json:"time"`
}

const maxBody = 8 << 20

// Fetch polls one configured source. -> (items, HTTP status, error).
func Fetch(client *http.Client, ua string, s Source, now time.Time) ([]Item, int, error) {
	u, err := url.Parse(s.URL)
	if err != nil {
		return nil, 0, fmt.Errorf("bad url: %v", err)
	}
	if s.CacheBustParam != "" {
		q := u.Query()
		q.Set(s.CacheBustParam, strconv.FormatInt(now.Unix(), 10))
		u.RawQuery = q.Encode()
	}
	var body io.Reader
	if s.Body != "" {
		body = strings.NewReader(s.Body)
	}
	req, err := http.NewRequest(strings.ToUpper(s.Method), u.String(), body)
	if err != nil {
		return nil, 0, err
	}
	req.Header.Set("User-Agent", ua)
	if s.Body != "" {
		req.Header.Set("Content-Type", "application/json")
	}
	// Accept-Encoding left unset on purpose: net/http negotiates gzip itself
	// (roadmap-watcher/board.go measured the 5.5x cost of setting it by hand).
	resp, err := client.Do(req)
	if err != nil {
		return nil, 0, err
	}
	defer resp.Body.Close()
	raw, err := io.ReadAll(io.LimitReader(resp.Body, maxBody))
	if err != nil {
		return nil, resp.StatusCode, err
	}
	if resp.StatusCode != http.StatusOK {
		return nil, resp.StatusCode, fmt.Errorf("HTTP %d", resp.StatusCode)
	}
	var items []Item
	switch s.Format {
	case "json":
		items, err = parseJSON(raw, s)
	case "html":
		items, err = parseHTML(string(raw), s)
	default:
		err = fmt.Errorf("format %q is not json or html", s.Format)
	}
	if err != nil {
		return nil, resp.StatusCode, err
	}
	if len(items) == 0 {
		return nil, resp.StatusCode, fmt.Errorf("HTTP 200 but 0 items could be read - "+
			"the page is unreadable, which is NOT the same as quiet (%d bytes)", len(raw))
	}
	for i := range items {
		if items[i].URL != "" && s.URLPrefix != "" && !strings.HasPrefix(items[i].URL, "http") {
			items[i].URL = strings.TrimRight(s.URLPrefix, "/") + "/" + strings.TrimLeft(items[i].URL, "/")
		}
	}
	return dedupe(items), resp.StatusCode, nil
}

func dedupe(items []Item) []Item {
	seen := map[string]bool{}
	out := items[:0]
	for _, it := range items {
		if !seen[it.ID] {
			seen[it.ID] = true
			out = append(out, it)
		}
	}
	return out
}

// parseJSON walks items_path (dot-separated object keys) to an array of objects.
// Numbers are kept as their exact text (UseNumber): an id past 2^53 must not be
// rounded into a different id.
func parseJSON(raw []byte, s Source) ([]Item, error) {
	dec := json.NewDecoder(strings.NewReader(string(raw)))
	dec.UseNumber()
	var doc any
	if err := dec.Decode(&doc); err != nil {
		return nil, fmt.Errorf("not JSON: %v", err)
	}
	if s.SuccessField != "" {
		top, _ := doc.(map[string]any)
		if got := text(top[s.SuccessField]); got != s.SuccessValue {
			return nil, fmt.Errorf("the response says it FAILED: %s=%q, want %q", s.SuccessField, got, s.SuccessValue)
		}
	}
	cur := doc
	for _, seg := range strings.Split(s.ItemsPath, ".") {
		m, ok := cur.(map[string]any)
		if !ok {
			return nil, fmt.Errorf("items_path %q: %q is not inside an object", s.ItemsPath, seg)
		}
		cur, ok = m[seg]
		if !ok {
			return nil, fmt.Errorf("items_path %q: no key %q", s.ItemsPath, seg)
		}
	}
	arr, ok := cur.([]any)
	if !ok {
		return nil, fmt.Errorf("items_path %q is not an array", s.ItemsPath)
	}
	var out []Item
	for n, el := range arr {
		m, ok := el.(map[string]any)
		if !ok {
			return nil, fmt.Errorf("item %d is not an object", n)
		}
		id := text(m[s.IDField])
		if id == "" {
			return nil, fmt.Errorf("item %d has no %q - refused rather than skipped", n, s.IDField)
		}
		out = append(out, Item{ID: id, Title: text(m[s.TitleField]), URL: text(m[s.URLField]), Time: text(m[s.TimeField])})
	}
	return out, nil
}

func text(v any) string {
	switch t := v.(type) {
	case nil:
		return ""
	case string:
		return strings.TrimSpace(t)
	case json.Number:
		return t.String()
	case bool:
		return strconv.FormatBool(t)
	default:
		b, _ := json.Marshal(t)
		return string(b)
	}
}

func parseHTML(page string, s Source) ([]Item, error) {
	re, err := regexp.Compile(s.ItemRegex)
	if err != nil {
		return nil, err
	}
	get := func(m []string, name string) string {
		if i := re.SubexpIndex(name); i >= 0 && i < len(m) {
			return strings.TrimSpace(html.UnescapeString(m[i]))
		}
		return ""
	}
	var out []Item
	for _, m := range re.FindAllStringSubmatch(page, -1) {
		id := get(m, "id")
		if id == "" {
			return nil, fmt.Errorf("a match had an empty id - refused rather than skipped")
		}
		out = append(out, Item{ID: id, Title: get(m, "title"), URL: get(m, "url"), Time: get(m, "time")})
	}
	return out, nil
}
