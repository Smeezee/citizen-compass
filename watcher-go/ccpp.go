package main

import (
	"crypto/sha256"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"time"
)

// Ports ccpp.py's CitizenCompassPacket: scans the project, cross-references
// ships/data/docs, and computes the same health-score weighting.

type shipInfo struct {
	Slug             string `json:"slug"`
	Path             string `json:"path"`
	Files            []string `json:"files"`
	HardpointsCount  int    `json:"hardpoints_count"`
	ViewerComplete   bool   `json:"viewer_complete"`
	ModelSize        int64  `json:"model_size,omitempty"`
}

type dataLayerInfo struct {
	Path         string         `json:"path"`
	FileCount    int            `json:"file_count"`
	TotalSizeMB  float64        `json:"total_size_mb"`
	FileTypes    map[string]int `json:"file_types"`
	SampleFiles  []string       `json:"sample_files"`
}

type ccppInventory struct {
	Ships      map[string]*shipInfo     `json:"ships"`
	DataLayers map[string]*dataLayerInfo `json:"data_layers"`
	Scripts    []map[string]interface{} `json:"scripts"`
	Models     []map[string]interface{} `json:"models"`
	Docs       []map[string]interface{} `json:"docs"`
}

type ccppCrossref struct {
	ShipsWithViewers    int            `json:"ships_with_viewers"`
	ShipsTotal          int            `json:"ships_total"`
	ViewersProgressPct  float64        `json:"viewers_progress_pct"`
	DataFilesByCategory map[string]int `json:"data_files_by_category"`
}

type ccppScores struct {
	DataCompleteness float64 `json:"data_completeness"`
	ViewerProgress   float64 `json:"viewer_progress"`
	Documentation    float64 `json:"documentation"`
	OverallHealth    float64 `json:"overall_health"`
}

type ccppPacket struct {
	Metadata  map[string]interface{} `json:"metadata"`
	Inventory ccppInventory          `json:"inventory"`
	Crossref  ccppCrossref           `json:"crossref"`
	Scores    ccppScores             `json:"scores"`
}

func scanProject() *ccppPacket {
	p := &ccppPacket{
		Metadata: map[string]interface{}{
			"format":  "CCPP-1.0",
			"project": "Citizen Compass",
			"created": time.Now().Format(time.RFC3339),
			"updated": time.Now().Format(time.RFC3339),
		},
		Inventory: ccppInventory{
			Ships:      map[string]*shipInfo{},
			DataLayers: map[string]*dataLayerInfo{},
		},
	}

	scanShips(p)
	scanDataLayer(p)
	scanScripts(p)
	scanModels(p)
	scanDocs(p)
	buildCrossref(p)
	calculateScores(p)

	p.Metadata["updated"] = time.Now().Format(time.RFC3339)
	p.Metadata["project_path"] = projectRoot
	p.Metadata["scan_complete"] = true

	return p
}

func scanShips(p *ccppPacket) {
	entries, err := os.ReadDir(shipsDir)
	if err != nil {
		return
	}
	for _, e := range entries {
		if !e.IsDir() {
			continue
		}
		slug := e.Name()
		shipDir := filepath.Join(shipsDir, slug)
		info := &shipInfo{Slug: slug, Path: shipDir, Files: []string{}}

		modelPath := filepath.Join(shipDir, "model.glb")
		indexPath := filepath.Join(shipDir, "index.html")
		hpPath := filepath.Join(shipDir, "hardpoints.json")

		if st, err := os.Stat(modelPath); err == nil {
			info.Files = append(info.Files, "model.glb")
			info.ModelSize = st.Size()
		}
		if _, err := os.Stat(indexPath); err == nil {
			info.Files = append(info.Files, "index.html")
		}
		if _, err := os.Stat(hpPath); err == nil {
			info.Files = append(info.Files, "hardpoints.json")
			if raw, err := os.ReadFile(hpPath); err == nil {
				var data map[string]interface{}
				if json.Unmarshal(raw, &data) == nil {
					if hp, ok := data["hardpoints"].([]interface{}); ok {
						info.HardpointsCount = len(hp)
					}
					info.ViewerComplete = len(info.Files) == 3
				}
			}
		}

		if len(info.Files) > 0 {
			p.Inventory.Ships[slug] = info
		}
	}
}

func scanDataLayer(p *ccppPacket) {
	nested := filepath.Join(projectRoot, "data-layer")
	flat := filepath.Join(projectRoot, "data-layerrawhardpoints")

	var dataDir string
	if dirExists(nested) {
		dataDir = nested
	} else if dirExists(flat) {
		dataDir = flat
	}

	if dataDir == "" {
		matches, _ := filepath.Glob(filepath.Join(projectRoot, "data-layer*"))
		for _, m := range matches {
			if dirExists(m) {
				catalogDataFolder(p, m, filepath.Base(m))
			}
		}
		return
	}

	catalogDataFolder(p, dataDir, "data-layer")
}

func catalogDataFolder(p *ccppPacket, folder string, name string) {
	if !dirExists(folder) {
		return
	}
	fileCount := 0
	var totalSize int64
	fileTypes := map[string]int{}
	var sampleFiles []string

	filepath.Walk(folder, func(path string, info os.FileInfo, err error) error {
		if err != nil || info.IsDir() {
			return nil
		}
		fileCount++
		totalSize += info.Size()
		ext := strings.ToLower(filepath.Ext(path))
		fileTypes[ext]++
		if len(sampleFiles) < 3 {
			sampleFiles = append(sampleFiles, filepath.Base(path))
		}
		return nil
	})

	p.Inventory.DataLayers[name] = &dataLayerInfo{
		Path:        folder,
		FileCount:   fileCount,
		TotalSizeMB: round2(float64(totalSize) / (1024 * 1024)),
		FileTypes:   fileTypes,
		SampleFiles: sampleFiles,
	}
}

func scanScripts(p *ccppPacket) {
	matches, _ := filepath.Glob(filepath.Join(projectRoot, "*.py"))
	for _, m := range matches {
		st, err := os.Stat(m)
		if err != nil {
			continue
		}
		p.Inventory.Scripts = append(p.Inventory.Scripts, map[string]interface{}{
			"name": filepath.Base(m), "path": m, "size": st.Size(),
		})
	}
}

func scanModels(p *ccppPacket) {
	filepath.Walk(projectRoot, func(path string, info os.FileInfo, err error) error {
		if err != nil || info.IsDir() {
			return nil
		}
		ext := strings.ToLower(filepath.Ext(path))
		if ext == ".blend" || ext == ".glb" {
			p.Inventory.Models = append(p.Inventory.Models, map[string]interface{}{
				"name": filepath.Base(path), "path": path, "size_mb": round2(float64(info.Size()) / (1024 * 1024)),
			})
		}
		return nil
	})
}

func scanDocs(p *ccppPacket) {
	filepath.Walk(projectRoot, func(path string, info os.FileInfo, err error) error {
		if err != nil || info.IsDir() {
			return nil
		}
		if strings.ToLower(filepath.Ext(path)) == ".md" {
			p.Inventory.Docs = append(p.Inventory.Docs, map[string]interface{}{
				"name": filepath.Base(path), "path": path,
			})
		}
		return nil
	})
}

func buildCrossref(p *ccppPacket) {
	withViewers := 0
	for _, s := range p.Inventory.Ships {
		if s.ViewerComplete {
			withViewers++
		}
	}
	total := len(p.Inventory.Ships)
	p.Crossref = ccppCrossref{
		ShipsWithViewers:    withViewers,
		ShipsTotal:          total,
		DataFilesByCategory: map[string]int{},
	}
	if total > 0 {
		p.Crossref.ViewersProgressPct = round1(float64(withViewers) / float64(total) * 100)
	}
	for name, data := range p.Inventory.DataLayers {
		lower := strings.ToLower(name)
		switch {
		case strings.Contains(lower, "raw"):
			p.Crossref.DataFilesByCategory["raw"] = data.FileCount
		case strings.Contains(lower, "processed"):
			p.Crossref.DataFilesByCategory["processed"] = data.FileCount
		case strings.Contains(lower, "export"):
			p.Crossref.DataFilesByCategory["exports"] = data.FileCount
		}
	}
}

func calculateScores(p *ccppPacket) {
	dataFiles := 0
	for name, data := range p.Inventory.DataLayers {
		if strings.Contains(strings.ToLower(name), "raw") {
			dataFiles = data.FileCount
			break
		}
	}
	p.Scores.DataCompleteness = minF(100, round1(float64(dataFiles)/232*100))
	p.Scores.ViewerProgress = p.Crossref.ViewersProgressPct
	p.Scores.Documentation = minF(100, float64(len(p.Inventory.Docs)*20))
	p.Scores.OverallHealth = round1(
		p.Scores.DataCompleteness*0.40 + p.Scores.ViewerProgress*0.50 + p.Scores.Documentation*0.10,
	)
}

func saveCcpp(p *ccppPacket, path string) error {
	encoded, err := json.MarshalIndent(p, "", "  ")
	if err != nil {
		return err
	}
	checksum := fmt.Sprintf("%x", sha256.Sum256(encoded))[:16]
	p.Metadata["checksum"] = checksum
	encoded, err = json.MarshalIndent(p, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(path, encoded, 0644)
}

func loadCcpp(path string) (*ccppPacket, error) {
	raw, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}
	var p ccppPacket
	if err := json.Unmarshal(raw, &p); err != nil {
		return nil, err
	}
	return &p, nil
}

// rescanAndScore mirrors inbox_watcher.py's rescan_and_score(): re-scan the
// whole project, save citizen-compass.ccpp, log the refreshed health score.
func rescanAndScore() {
	p := scanProject()
	if err := saveCcpp(p, ccppFile); err != nil {
		logMsg("could not save %s: %v", ccppFile, err)
		return
	}
	logMsg("Health score refreshed: %.1f/100 (data %.1f%%, viewers %.1f%%, docs %.1f%%)",
		p.Scores.OverallHealth, p.Scores.DataCompleteness, p.Scores.ViewerProgress, p.Scores.Documentation)
}

func round1(v float64) float64 {
	return float64(int(v*10+0.5)) / 10
}
func round2(v float64) float64 {
	return float64(int(v*100+0.5)) / 100
}
func minF(a, b float64) float64 {
	if a < b {
		return a
	}
	return b
}
