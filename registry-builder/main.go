// Registry Builder — Citizen Compass Phase 1 tool
//
// Builds and maintains the master ship ID registry: a permanent mapping of
// ship code (manufacturer initials + a sequential number, e.g. AEG-01) to
// ship name, manufacturer, and folder path. Postgres (the same
// citizen_compass DB the production app uses, in its own ship_registry
// table) is canonical; a JSON file is regenerated from it on every run for
// fast offline lookups (e.g. by the Blender launcher).
//
// Safe to re-run: existing ships (matched by their ship_specs.json slug)
// are never renumbered or touched. Only ships not yet in the registry get
// a new, permanently-assigned code.
//
// Usage:
//   registry-builder                 # build/update the registry for real
//   registry-builder --dry-run       # show what WOULD be added, no writes
package main

import (
	"bufio"
	"database/sql"
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strconv"
	"strings"

	_ "github.com/jackc/pgx/v5/stdlib"

	"citizencompass/pkg/pipelinelog"
)

// manufacturerCodes maps each known manufacturer name (as it appears in
// ship_specs.json) to its permanent 3-letter registry code. Coded by actual
// current manufacturer, not legacy class-name prefixes -- this is why Mirai
// gets MIR (distinct from Musashi's MSC) even though some Mirai ships'
// underlying class names still say "misc" from before the manufacturers
// split, and why the 3 Argo ATLS variants mis-tagged as "Banu Souli" in the
// source data still get coded ARG, matching their real manufacturer.
var manufacturerCodes = map[string]string{
	"Aegis Dynamics":                             "AEG",
	"Anvil Aerospace":                             "ANV",
	"Aopoa":                                       "XIA",
	"Argo Astronautics":                           "ARG",
	"Banu Souli":                                  "BAN",
	"Consolidated Outland":                        "CNO",
	"Crusader Industries":                         "CRU",
	"Drake Interplanetary":                        "DRA",
	"Esperia":                                      "ESP",
	"Gatac Manufacture":                           "GAT",
	"Grey's Market":                               "GRY",
	"Greycat Industrial":                          "GRC",
	"Kruger Intergalactic":                        "KRU",
	"Mirai":                                        "MIR",
	"Musashi Industrial and Starflight Concern":   "MSC",
	"Origin Jumpworks":                            "ORI",
	"Roberts Space Industries":                    "RSI",
	"Tumbril Land Systems":                        "TUM",
	"Vanduul Clans":                               "VAN",
}

// manufacturerOverrides corrects known data-entry errors in ship_specs.json
// where a ship's stated manufacturer doesn't match its actual maker. Keyed
// by the ship's source_slug. The 3 Argo ATLS variants below are tagged
// "Banu Souli" in the source data but are genuinely Argo-made vehicles.
var manufacturerOverrides = map[string]string{
	"argo-atls-geo-ikti":       "Argo Astronautics",
	"argo-atls-ikti":           "Argo Astronautics",
	"argo-atls-ikti-argos":     "Argo Astronautics",
}

type shipEntry struct {
	SourceSlug   string `json:"source_slug"`
	ShipName     string `json:"ship_name"`
	Manufacturer string `json:"manufacturer_name"`
}

// newRow is one not-yet-registered ship about to be assigned a permanent
// code and inserted.
type newRow struct {
	code, mfrCode, mfrName, shipName, sourceSlug, folderSlug string
}

func main() {
	dryRun := flag.Bool("dry-run", false, "Show what would be added without writing to the database or export file")
	flag.Parse()

	projectRoot := findProjectRoot()
	logger := pipelinelog.New(projectRoot, "registry_builder")

	shipSpecsPath := filepath.Join(projectRoot, "data-layerrawhardpoints", "ship_specs.json")
	ships, err := loadShipSpecs(shipSpecsPath)
	if err != nil {
		logger.Logf("FATAL: could not read %s: %v", shipSpecsPath, err)
		os.Exit(1)
	}
	logger.Logf("Loaded %d ships from %s", len(ships), shipSpecsPath)

	shipsDir := filepath.Join(projectRoot, "tests", "testing-site", "ships")
	knownFolders := listShipFolders(shipsDir)

	dbURL, err := readDatabaseURL(filepath.Join(projectRoot, ".env"))
	if err != nil {
		logger.Logf("FATAL: could not read DATABASE_URL from .env: %v", err)
		os.Exit(1)
	}

	db, err := sql.Open("pgx", dbURL)
	if err != nil {
		logger.Logf("FATAL: could not open database connection: %v", err)
		os.Exit(1)
	}
	defer db.Close()

	if err := db.Ping(); err != nil {
		logger.Logf("FATAL: could not reach Postgres: %v", err)
		os.Exit(1)
	}
	logger.Logf("Connected to Postgres")

	if !*dryRun {
		if err := ensureSchema(db); err != nil {
			logger.Logf("FATAL: could not ensure ship_registry table exists: %v", err)
			os.Exit(1)
		}
	}

	existingSlugs, maxByCode, err := loadExistingRegistry(db, *dryRun)
	if err != nil {
		logger.Logf("FATAL: could not read existing registry: %v", err)
		os.Exit(1)
	}
	logger.Logf("%d ship(s) already registered", len(existingSlugs))

	// Deterministic order: sort by manufacturer code, then ship name, so
	// numbering is reproducible run-to-run for any given input snapshot.
	sort.Slice(ships, func(i, j int) bool {
		ci := manufacturerCodeFor(ships[i])
		cj := manufacturerCodeFor(ships[j])
		if ci != cj {
			return ci < cj
		}
		return ships[i].ShipName < ships[j].ShipName
	})

	var toInsert []newRow
	var unrecognizedMfr []string

	for _, s := range ships {
		if existingSlugs[s.SourceSlug] {
			continue // already registered, permanent code stays untouched
		}
		mfrName := effectiveManufacturer(s)
		code, ok := manufacturerCodes[mfrName]
		if !ok {
			unrecognizedMfr = append(unrecognizedMfr, fmt.Sprintf("%s (manufacturer: %s)", s.SourceSlug, mfrName))
			continue
		}
		maxByCode[code]++
		shipCode := fmt.Sprintf("%s-%02d", code, maxByCode[code])
		folderSlug := matchFolderSlug(s, knownFolders)
		toInsert = append(toInsert, newRow{
			code: shipCode, mfrCode: code, mfrName: mfrName,
			shipName: s.ShipName, sourceSlug: s.SourceSlug, folderSlug: folderSlug,
		})
	}

	if len(unrecognizedMfr) > 0 {
		logger.Logf("⚠ %d ship(s) skipped -- unrecognized manufacturer, not in manufacturerCodes map:", len(unrecognizedMfr))
		for _, u := range unrecognizedMfr {
			logger.Logf("    %s", u)
		}
	}

	if *dryRun {
		logger.Logf("[dry run] %d new ship(s) would be added:", len(toInsert))
		for _, r := range toInsert {
			logger.Logf("  %-8s %-30s mfr=%-45s folder=%s", r.code, r.shipName, r.mfrName, orNone(r.folderSlug))
		}
		logger.Logf("[dry run] no database writes, no export file written")
		return
	}

	if len(toInsert) > 0 {
		if err := insertNewShips(db, toInsert); err != nil {
			logger.Logf("FATAL: could not insert new ships: %v", err)
			os.Exit(1)
		}
	}
	logger.Logf("Added %d new ship(s) to the registry", len(toInsert))

	exportPath := filepath.Join(projectRoot, "data-layer", "ship_registry.json")
	count, err := exportRegistry(db, exportPath)
	if err != nil {
		logger.Logf("FATAL: could not export registry to %s: %v", exportPath, err)
		os.Exit(1)
	}
	logger.Logf("Exported %d total registry entries to %s", count, exportPath)
}

func orNone(s string) string {
	if s == "" {
		return "(none)"
	}
	return s
}

func effectiveManufacturer(s shipEntry) string {
	if override, ok := manufacturerOverrides[s.SourceSlug]; ok {
		return override
	}
	return s.Manufacturer
}

func manufacturerCodeFor(s shipEntry) string {
	return manufacturerCodes[effectiveManufacturer(s)]
}

func findProjectRoot() string {
	dir, err := os.Getwd()
	if err != nil {
		return "."
	}
	for {
		if _, err := os.Stat(filepath.Join(dir, "go.work")); err == nil {
			return dir
		}
		parent := filepath.Dir(dir)
		if parent == dir {
			break
		}
		dir = parent
	}
	cwd, _ := os.Getwd()
	return cwd
}

func loadShipSpecs(path string) ([]shipEntry, error) {
	raw, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}
	var records []struct {
		Data map[string]interface{} `json:"data"`
	}
	if err := json.Unmarshal(raw, &records); err != nil {
		return nil, err
	}

	var out []shipEntry
	for _, r := range records {
		slug, _ := r.Data["slug"].(string)
		name, _ := r.Data["name"].(string)
		if slug == "" || name == "" {
			continue
		}
		mfrName := ""
		switch m := r.Data["manufacturer"].(type) {
		case map[string]interface{}:
			mfrName, _ = m["name"].(string)
		case string:
			mfrName = m
		}
		out = append(out, shipEntry{SourceSlug: slug, ShipName: name, Manufacturer: mfrName})
	}
	return out, nil
}

func listShipFolders(shipsDir string) []string {
	entries, err := os.ReadDir(shipsDir)
	if err != nil {
		return nil
	}
	var out []string
	for _, e := range entries {
		if e.IsDir() {
			out = append(out, e.Name())
		}
	}
	return out
}

// matchFolderSlug finds an existing tests/testing-site/ships/<slug>/ folder
// for this ship, if one exists, using the same substring-match convention
// the watcher uses elsewhere.
func matchFolderSlug(s shipEntry, knownFolders []string) string {
	stem := strings.ToLower(strings.ReplaceAll(s.ShipName, " ", "-"))
	for _, folder := range knownFolders {
		if strings.Contains(stem, folder) || strings.Contains(s.SourceSlug, folder) {
			return folder
		}
	}
	return ""
}

func readDatabaseURL(envPath string) (string, error) {
	f, err := os.Open(envPath)
	if err != nil {
		return "", err
	}
	defer f.Close()

	scanner := bufio.NewScanner(f)
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if line == "" || strings.HasPrefix(line, "#") {
			continue
		}
		parts := strings.SplitN(line, "=", 2)
		if len(parts) != 2 {
			continue
		}
		key := strings.TrimSpace(parts[0])
		if key == "DATABASE_URL" || key == "RAILWAY_DATABASE_URL" {
			val := strings.Trim(strings.TrimSpace(parts[1]), `"'`)
			// Go's pgx stdlib driver expects a plain postgres:// URL, not
			// SQLAlchemy's "postgresql+psycopg2://" dialect+driver form.
			val = strings.Replace(val, "postgresql+psycopg2://", "postgres://", 1)
			val = strings.Replace(val, "postgresql://", "postgres://", 1)
			return val, nil
		}
	}
	return "", fmt.Errorf("no DATABASE_URL or RAILWAY_DATABASE_URL found in %s", envPath)
}

func ensureSchema(db *sql.DB) error {
	_, err := db.Exec(`
		CREATE TABLE IF NOT EXISTS ship_registry (
			id SERIAL PRIMARY KEY,
			ship_code VARCHAR(20) UNIQUE NOT NULL,
			manufacturer_code VARCHAR(10) NOT NULL,
			manufacturer_name VARCHAR(150) NOT NULL,
			ship_name VARCHAR(150) NOT NULL,
			source_slug VARCHAR(150) UNIQUE NOT NULL,
			folder_slug VARCHAR(150),
			created_at TIMESTAMP NOT NULL DEFAULT NOW()
		)
	`)
	return err
}

// loadExistingRegistry returns the set of already-registered source slugs
// and the highest assigned sequence number per manufacturer code, so new
// ships get the next number without ever renumbering existing ones. In
// dry-run mode, gracefully handles the table not existing yet.
func loadExistingRegistry(db *sql.DB, dryRun bool) (map[string]bool, map[string]int, error) {
	existing := map[string]bool{}
	maxByCode := map[string]int{}

	rows, err := db.Query(`SELECT source_slug, ship_code FROM ship_registry`)
	if err != nil {
		if dryRun {
			return existing, maxByCode, nil // table likely doesn't exist yet in dry-run
		}
		return nil, nil, err
	}
	defer rows.Close()

	for rows.Next() {
		var slug, code string
		if err := rows.Scan(&slug, &code); err != nil {
			return nil, nil, err
		}
		existing[slug] = true
		parts := strings.SplitN(code, "-", 2)
		if len(parts) == 2 {
			if n, err := strconv.Atoi(parts[1]); err == nil {
				if n > maxByCode[parts[0]] {
					maxByCode[parts[0]] = n
				}
			}
		}
	}
	return existing, maxByCode, rows.Err()
}

func insertNewShips(db *sql.DB, rows []newRow) error {
	tx, err := db.Begin()
	if err != nil {
		return err
	}
	defer tx.Rollback()

	stmt, err := tx.Prepare(`
		INSERT INTO ship_registry (ship_code, manufacturer_code, manufacturer_name, ship_name, source_slug, folder_slug)
		VALUES ($1, $2, $3, $4, $5, NULLIF($6, ''))
	`)
	if err != nil {
		return err
	}
	defer stmt.Close()

	for _, r := range rows {
		if _, err := stmt.Exec(r.code, r.mfrCode, r.mfrName, r.shipName, r.sourceSlug, r.folderSlug); err != nil {
			return fmt.Errorf("inserting %s (%s): %w", r.shipName, r.code, err)
		}
	}
	return tx.Commit()
}

type registryEntry struct {
	ShipCode         string `json:"ship_code"`
	ManufacturerCode string `json:"manufacturer_code"`
	ManufacturerName string `json:"manufacturer_name"`
	ShipName         string `json:"ship_name"`
	SourceSlug       string `json:"source_slug"`
	FolderSlug       string `json:"folder_slug,omitempty"`
}

func exportRegistry(db *sql.DB, exportPath string) (int, error) {
	rows, err := db.Query(`
		SELECT ship_code, manufacturer_code, manufacturer_name, ship_name, source_slug, COALESCE(folder_slug, '')
		FROM ship_registry ORDER BY ship_code
	`)
	if err != nil {
		return 0, err
	}
	defer rows.Close()

	var entries []registryEntry
	for rows.Next() {
		var e registryEntry
		if err := rows.Scan(&e.ShipCode, &e.ManufacturerCode, &e.ManufacturerName, &e.ShipName, &e.SourceSlug, &e.FolderSlug); err != nil {
			return 0, err
		}
		entries = append(entries, e)
	}
	if err := rows.Err(); err != nil {
		return 0, err
	}

	if err := os.MkdirAll(filepath.Dir(exportPath), 0755); err != nil {
		return 0, err
	}
	encoded, err := json.MarshalIndent(entries, "", "  ")
	if err != nil {
		return 0, err
	}
	if err := os.WriteFile(exportPath, encoded, 0644); err != nil {
		return 0, err
	}
	return len(entries), nil
}
