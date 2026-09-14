package main

// livever.go - thin shim. Parse logic lives in citizencompass/pkg/livever
// (folded 2026-09-14 so rsi-watcher cannot drift).

import "citizencompass/pkg/livever"

type LiveVersions = livever.LiveVersions

func ParseLiveVersions(description string) LiveVersions {
	return livever.ParseLiveVersions(description)
}

func PatchGap(v LiveVersions, verified string) (bool, string) {
	return livever.PatchGap(v, verified)
}