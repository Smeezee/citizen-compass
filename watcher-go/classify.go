package main

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"time"
)

// classifyAndRoute decides what a dropped file is and where it belongs,
// mirroring inbox_watcher.py's classify_and_route() for the file types this
// first migration step covers. Returns (note, destination, error).
func classifyAndRoute(path string) (string, string, error) {
	ext := extLower(path)

	switch ext {
	case ".py":
		return routeSimple(path, projectRoot, "script")

	case ".md":
		return classifyMarkdown(path)

	case ".glb", ".blend":
		return classifyModel(path, ext)

	case ".json":
		return classifyJSON(path)

	case ".zip":
		return handleZip(path)
	}

	if isImageFile(path) {
		return classifyImage(path)
	}

	// Unknown type -- never silently discard.
	return routeSimple(path, needsReviewDir, fmt.Sprintf("unrecognized extension '%s'", ext))
}

func classifyMarkdown(path string) (string, string, error) {
	raw, err := os.ReadFile(path)
	if err != nil {
		return "", "", err
	}
	text := string(raw)

	if isHandoffDoc(path, text) {
		stamp := time.Now().Format("20060102_150405")
		dest := filepath.Join(handoffArchiveDir, fmt.Sprintf("%s_%s", stamp, filepath.Base(path)))
		note, finalDest, err := routeTo(path, dest, "handoff doc — archived")
		if err != nil {
			return "", "", err
		}
		if werr := os.WriteFile(latestRawPath(), []byte(text), 0644); werr != nil {
			logMsg("could not update _latest_raw.md: %v", werr)
		}
		note += "; will fully replace PROJECT NOTES in LATEST_HANDOFF.md"
		return note, finalDest, nil
	}

	if isUpdateDoc(path, text) {
		stamp := time.Now().Format("20060102_150405")
		dest := filepath.Join(handoffArchiveDir, fmt.Sprintf("%s_%s", stamp, filepath.Base(path)))
		note, finalDest, err := routeTo(path, dest, "update doc — archived")
		if err != nil {
			return "", "", err
		}
		if aerr := appendUpdate(text, filepath.Base(path)); aerr != nil {
			logMsg("could not append to updates log: %v", aerr)
		}
		note += "; appended to running updates log (nothing overwritten)"
		return note, finalDest, nil
	}

	return routeSimple(path, docsDir, "doc")
}

func classifyModel(path string, ext string) (string, string, error) {
	stem := strings.TrimSuffix(filepath.Base(path), filepath.Ext(path))
	slug := guessShipSlug(stem, knownShipSlugs())
	if slug != "" {
		destDir := filepath.Join(shipsDir, slug)
		destName := filepath.Base(path)
		if ext == ".glb" {
			destName = "model.glb"
		}
		return routeTo(path, filepath.Join(destDir, destName), fmt.Sprintf("3D model matched to ship '%s'", slug))
	}
	return routeSimple(path, modelsUnsortedDir, "3D model, no ship slug match")
}

func classifyJSON(path string) (string, string, error) {
	raw, err := os.ReadFile(path)
	if err != nil {
		return "", "", err
	}

	var data map[string]interface{}
	if uerr := json.Unmarshal(raw, &data); uerr != nil {
		return routeSimple(path, needsReviewDir, fmt.Sprintf("invalid JSON (%s)", uerr))
	}

	stemLower := strings.ToLower(strings.TrimSuffix(filepath.Base(path), filepath.Ext(path)))

	if looksLikeViewerHardpoints(data) {
		slug, _ := data["ship_slug"].(string)
		if slug == "" {
			slug = guessShipSlug(stemLower, knownShipSlugs())
		}
		if slug != "" {
			destDir := filepath.Join(shipsDir, slug)
			return routeTo(path, filepath.Join(destDir, "hardpoints.json"), fmt.Sprintf("viewer hardpoint placements for '%s'", slug))
		}
		return routeSimple(path, needsReviewDir, "viewer hardpoint placements, no ship slug match")
	}

	_, hasWbc := data["weapons_by_category"]
	if hasWbc || strings.Contains(stemLower, "hardpoint") || strings.Contains(stemLower, "weapon") {
		note, dest, err := routeSimple(path, pickRawHardpointsDir(), "raw hardpoint/weapon data")
		if err != nil {
			return "", "", err
		}
		organizedPath, oerr := autoOrganizeHardpointFile(dest, data)
		if oerr != nil {
			logMsg("could not auto-categorize %s: %v", filepath.Base(dest), oerr)
		} else if organizedPath != "" {
			note += fmt.Sprintf("; auto-categorized -> %s", organizedPath)
		}
		return note, dest, nil
	}

	_, hasSlug := data["ship_slug"]
	_, hasName := data["ship_name"]
	if hasSlug && hasName {
		return routeSimple(path, pickRawShipsDir(), "ship spec data")
	}

	return routeSimple(path, pickRawMiscDir(), "unclassified JSON, filed as misc — check if a new category is needed")
}

func looksLikeViewerHardpoints(data map[string]interface{}) bool {
	hpList, ok := data["hardpoints"].([]interface{})
	if !ok || len(hpList) == 0 {
		return false
	}
	first, ok := hpList[0].(map[string]interface{})
	if !ok {
		return false
	}
	_, hasPos := first["position"]
	_, hasX := first["x"]
	return hasPos || hasX
}

// categorizeWeaponEntry mirrors inbox_watcher.py's _categorize_weapon_entry
// exactly (note: this differs slightly from hardpoint_organizer.py's own
// categorize_hardpoint(), which doesn't check "ballistic"/"energy" -- this
// port matches inbox_watcher.py specifically, since that's what's being
// replaced).
func categorizeWeaponEntry(entryType string) string {
	t := strings.ToLower(entryType)
	if strings.Contains(t, "turret") {
		return "turrets"
	}
	if strings.Contains(t, "missile") || strings.Contains(t, "launcher") {
		return "missiles"
	}
	if strings.Contains(t, "gun") || strings.Contains(t, "ballistic") || strings.Contains(t, "energy") {
		return "weapons"
	}
	return "components"
}

// autoOrganizeHardpointFile categorizes a raw weapon/hardpoint file into
// turrets/missiles/weapons/components, matching inbox_watcher.py's
// auto_organize_hardpoint_file(). Returns "" (no error) if the file didn't
// have a recognizable weapons_by_category / hardpoints shape.
func autoOrganizeHardpointFile(rawPath string, data map[string]interface{}) (string, error) {
	stem := strings.TrimSuffix(filepath.Base(rawPath), filepath.Ext(rawPath))
	shipName, _ := data["ship_name"].(string)
	if shipName == "" {
		shipName = stem
	}
	shipSlug, _ := data["ship_slug"].(string)
	if shipSlug == "" {
		shipSlug = stem
	}

	categories := map[string][]interface{}{
		"weapons": {}, "turrets": {}, "missiles": {}, "components": {},
	}
	foundAny := false

	if wbc, ok := data["weapons_by_category"].(map[string]interface{}); ok {
		for groupName, itemsRaw := range wbc {
			items, ok := itemsRaw.([]interface{})
			if !ok {
				continue
			}
			for _, itemRaw := range items {
				item, ok := itemRaw.(map[string]interface{})
				if !ok {
					continue
				}
				foundAny = true
				typeVal, _ := item["type"].(string)
				if typeVal == "" {
					typeVal = groupName
				}
				cat := categorizeWeaponEntry(typeVal)
				categories[cat] = append(categories[cat], item)
			}
		}
	}

	if hpList, ok := data["hardpoints"].([]interface{}); ok {
		for _, hpRaw := range hpList {
			hp, ok := hpRaw.(map[string]interface{})
			if !ok {
				continue
			}
			foundAny = true
			typeVal, _ := hp["type"].(string)
			cat := categorizeWeaponEntry(typeVal)
			categories[cat] = append(categories[cat], hp)
		}
	}

	if !foundAny {
		return "", nil
	}

	total := 0
	for _, v := range categories {
		total += len(v)
	}

	organized := map[string]interface{}{
		"ship_name":        shipName,
		"ship_slug":        shipSlug,
		"categories":       categories,
		"total_hardpoints": total,
	}

	outDir := pickProcessedHardpointsDir()
	if err := os.MkdirAll(outDir, 0755); err != nil {
		return "", err
	}
	outPath := filepath.Join(outDir, fmt.Sprintf("%s_organized.json", shipSlug))
	encoded, err := json.MarshalIndent(organized, "", "  ")
	if err != nil {
		return "", err
	}
	if err := os.WriteFile(outPath, encoded, 0644); err != nil {
		return "", err
	}
	return outPath, nil
}

func knownShipSlugs() []string {
	entries, err := os.ReadDir(shipsDir)
	if err != nil {
		return nil
	}
	var slugs []string
	for _, e := range entries {
		if e.IsDir() {
			slugs = append(slugs, e.Name())
		}
	}
	return slugs
}

func guessShipSlug(filenameStem string, knownSlugs []string) string {
	stem := strings.ReplaceAll(strings.ToLower(filenameStem), "_", "-")
	for _, slug := range knownSlugs {
		if strings.Contains(stem, slug) {
			return slug
		}
	}
	return ""
}

// --- data-layer path picking, matching inbox_watcher.py's flat/nested
// fallback quirk exactly, for behavior parity with the existing pipeline. ---

func pickRawHardpointsDir() string {
	flat := filepath.Join(projectRoot, "data-layerrawhardpoints")
	if dirExists(flat) {
		return flat
	}
	return filepath.Join(projectRoot, "data-layer", "raw", "hardpoints")
}

func pickRawShipsDir() string {
	flat := filepath.Join(projectRoot, "data-layerrawships")
	if dirExists(flat) {
		return flat
	}
	return filepath.Join(projectRoot, "data-layer", "raw", "ships")
}

func pickRawMiscDir() string {
	return filepath.Join(projectRoot, "data-layer", "raw", "misc")
}

func pickProcessedHardpointsDir() string {
	flat := filepath.Join(projectRoot, "data-layerprocessedhardpoints_by_type")
	if dirExists(flat) {
		return flat
	}
	return filepath.Join(projectRoot, "data-layer", "processed", "hardpoints_by_type")
}

func dirExists(path string) bool {
	info, err := os.Stat(path)
	return err == nil && info.IsDir()
}

// --- routing primitives ---

func routeSimple(path string, destDir string, note string) (string, string, error) {
	if err := os.MkdirAll(destDir, 0755); err != nil {
		return "", "", err
	}
	return routeTo(path, filepath.Join(destDir, filepath.Base(path)), note)
}

// routeTo moves path to dest, never destroying anything -- and THE PLAIN NAME
// ALWAYS ENDS UP HOLDING THE NEWEST ARRIVAL.
//
// # WHY THIS CHANGED, 2026-08-14
//
// It used to rename the NEWCOMER on a collision, which meant a corrected
// document landed under a timestamped filename while the plain one kept the
// superseded text. Observed live the same day:
//
//	AMENDS_tripwire-release-view-only-2026-08-14.md                  rev 1, WRONG
//	AMENDS_tripwire-release-view-only-2026-08-14__20260814180543.md  rev 2, right
//
// Rev 1 attributed a decision to Sleven that he never made. The correction
// existed, was filed, and went to a name nobody would open -- so anyone reading
// the obvious file got a stale instruction stated confidently. C3 hit it, and
// it was caught only because he happened to list the directory.
//
// Now the INCUMBENT is the one that moves aside. Both versions still survive
// (rule 1 is untouched -- nothing is deleted or overwritten), but the plain
// name resolves to the latest arrival, which is what every reader already
// assumes it does.
//
// The archived copy carries ITS OWN modification time, not "now", so the stamp
// says when that version was current rather than when it was pushed aside.
func routeTo(path string, dest string, note string) (string, string, error) {
	if err := os.MkdirAll(filepath.Dir(dest), 0755); err != nil {
		return "", "", err
	}
	if fi, err := os.Stat(dest); err == nil {
		archived, aerr := archiveName(dest, fi.ModTime())
		if aerr != nil {
			return "", "", aerr
		}
		if err := os.Rename(dest, archived); err != nil {
			return "", "", fmt.Errorf("could not move the previous %s aside, so the "+
				"new one was NOT filed (nothing was lost): %w", filepath.Base(dest), err)
		}
		note += fmt.Sprintf(" (SUPERSEDES an earlier file of this name — the older "+
			"one is kept as %s; this name now holds the newest)", filepath.Base(archived))
	}
	if err := os.Rename(path, dest); err != nil {
		return "", "", err
	}
	return note, dest, nil
}

// archiveName picks a free name for a superseded file, stamped with when that
// version was last written.
//
// The loop matters: two corrections to the same document inside one second used
// to be possible to lose, because a second-resolution stamp collides and
// os.Rename would then overwrite the first archive silently. It counts up
// rather than overwriting, because "we kept both" has to be true every time or
// it is not a property, it is a probability.
func archiveName(dest string, when time.Time) (string, error) {
	ext := filepath.Ext(dest)
	stem := strings.TrimSuffix(filepath.Base(dest), ext)
	dir := filepath.Dir(dest)
	stamp := when.Format("20060102150405")
	for i := 0; i < 100; i++ {
		name := fmt.Sprintf("%s__%s%s", stem, stamp, ext)
		if i > 0 {
			name = fmt.Sprintf("%s__%s-%d%s", stem, stamp, i, ext)
		}
		candidate := filepath.Join(dir, name)
		if _, err := os.Stat(candidate); os.IsNotExist(err) {
			return candidate, nil
		}
	}
	return "", fmt.Errorf("could not find a free archive name for %s after 100 "+
		"attempts; refusing to overwrite an existing archive", filepath.Base(dest))
}
