package main

// livebuild.go - FETCH stays here; PARSE is citizencompass/pkg/livever
// (folded 2026-09-14 with roadmap-watcher).

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"

	"citizencompass/pkg/livever"
)

const ptuNone = "none"

// ParseBuild -> (live, ptu, error). ptu is "none" when the board says so.
func ParseBuild(description string) (string, string, error) {
	return livever.ParseBuild(description)
}

// FetchBuild reads the board and parses its description.
func FetchBuild(client *http.Client, ua, url string) (string, string, error) {
	req, err := http.NewRequest(http.MethodGet, url, nil)
	if err != nil {
		return "", "", err
	}
	req.Header.Set("User-Agent", ua)
	req.Header.Set("Accept", "application/json")
	resp, err := client.Do(req)
	if err != nil {
		return "", "", err
	}
	defer resp.Body.Close()
	raw, err := io.ReadAll(io.LimitReader(resp.Body, maxBody))
	if err != nil {
		return "", "", err
	}
	if resp.StatusCode != http.StatusOK {
		return "", "", fmt.Errorf("HTTP %d", resp.StatusCode)
	}
	var b struct {
		Success int    `json:"success"`
		Msg     string `json:"msg"`
		Data    struct {
			Description string `json:"description"`
		} `json:"data"`
	}
	if err := json.Unmarshal(raw, &b); err != nil {
		return "", "", fmt.Errorf("not JSON: %v", err)
	}
	if b.Success != 1 {
		return "", "", fmt.Errorf("the board says it FAILED: success=%d %q", b.Success, b.Msg)
	}
	return ParseBuild(b.Data.Description)
}