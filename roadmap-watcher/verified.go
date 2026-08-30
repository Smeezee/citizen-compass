package main

// verified.go - read what the SITE says it verified, from the site's own data.
//
// Q5c, 2026-08-30. The comparison only means something if the two sides come
// from different places. The live version comes from RSI's board; this side
// comes from the page's own data layer - NOT from a constant in this program.
//
// A watcher holding its own copy of the number it is checking would agree with
// itself forever and report "level" the day the site fell behind, which is the
// exact failure it exists to catch. Hard rule 16, and it is the whole point of
// the item.

import (
	"fmt"
	"os"
	"path/filepath"
	"regexp"
)

// reVerified reads last_verified_patch out of the generated data layer. It is
// deliberately not a JSON parse: loadout_data.gen.js is JavaScript with a
// const assignment around the object, and parsing four megabytes of it to read
// one field would be slower and no more correct.
var reVerified = regexp.MustCompile(`"last_verified_patch"\s*:\s*"([^"]+)"`)

// candidates are where the data layer lives, nearest first. The watcher runs
// from its own directory, so it walks up to the repo root.
var candidates = []string{
	filepath.Join("testing", "_src", "loadout_data.gen.js"),
	filepath.Join("testing", "_deploy", "loadout_data.gen.js"),
}

// ReadVerifiedPatch returns the site's own last_verified_patch.
//
// AN ERROR IS A RESULT, NOT A CRASH. A missing data layer must produce
// "NOT KNOWN" from PatchGap rather than an empty string that could be mistaken
// for agreement, so the caller is handed both the value and the reason.
func ReadVerifiedPatch(startDir string) (string, error) {
	dir, err := filepath.Abs(startDir)
	if err != nil {
		return "", err
	}
	var tried []string
	for i := 0; i < 6; i++ { // walk up to the repo root
		for _, rel := range candidates {
			p := filepath.Join(dir, rel)
			tried = append(tried, p)
			b, err := os.ReadFile(p)
			if err != nil {
				continue
			}
			if m := reVerified.FindSubmatch(b); m != nil {
				return string(m[1]), nil
			}
			return "", fmt.Errorf("%s carries no last_verified_patch field", p)
		}
		parent := filepath.Dir(dir)
		if parent == dir {
			break
		}
		dir = parent
	}
	return "", fmt.Errorf("no loadout_data.gen.js found above %s (looked in %d places)",
		startDir, len(tried))
}

// roundupSuffix adds the roundup date when the board gave one, and says
// nothing when it did not - rather than printing an empty bracket that reads
// like a missing value nobody noticed.
func roundupSuffix(v LiveVersions) string {
	if v.Roundup == "" {
		return ""
	}
	return ", roadmap roundup " + v.Roundup
}
