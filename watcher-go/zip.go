package main

import (
	"archive/zip"
	"fmt"
	"io"
	"os"
	"path/filepath"
)

var zipArchiveDir string

// handleZip extracts a dropped zip, runs every file that comes out of it
// back through classifyAndRoute (nested zips included, since a .zip found
// inside the extraction is itself routed straight back into this function),
// then archives the original zip untouched in _zip_archive/. Nothing inside
// is ever silently discarded -- files that can't be classified still land
// in _needs_review/, just one level down from where they'd land if dropped
// loose. Mirrors inbox_watcher.py's handle_zip() exactly.
func handleZip(path string) (string, string, error) {
	extractDir, err := os.MkdirTemp(inboxDir, filepath.Base(path)+"_")
	if err != nil {
		return "", "", err
	}

	r, err := zip.OpenReader(path)
	if err != nil {
		os.RemoveAll(extractDir)
		return routeSimple(path, needsReviewDir, fmt.Sprintf("invalid zip (%s)", err))
	}

	var extractedFiles []string
	for _, f := range r.File {
		destPath := filepath.Join(extractDir, filepath.FromSlash(f.Name))
		if f.FileInfo().IsDir() {
			os.MkdirAll(destPath, 0755)
			continue
		}
		if err := os.MkdirAll(filepath.Dir(destPath), 0755); err != nil {
			continue
		}
		if err := extractZipEntry(f, destPath); err != nil {
			logMsg("could not extract %s from %s: %v", f.Name, filepath.Base(path), err)
			continue
		}
		extractedFiles = append(extractedFiles, destPath)
	}
	r.Close()

	if len(extractedFiles) == 0 {
		os.RemoveAll(extractDir)
		return routeSimple(path, needsReviewDir, "zip was empty")
	}

	sortedCount := 0
	failedCount := 0
	for _, f := range extractedFiles {
		note, dest, err := classifyAndRoute(f)
		if err != nil {
			logMsg("    ✗ (from %s) FAILED processing %s: %v", filepath.Base(path), filepath.Base(f), err)
			failedCount++
			continue
		}
		logMsg("    ✓ (from %s) %s -> %s (%s)", filepath.Base(path), filepath.Base(f), dest, note)
		sortedCount++
	}

	os.RemoveAll(extractDir)

	summary := fmt.Sprintf("zip extracted — %d file(s) sorted", sortedCount)
	if failedCount > 0 {
		summary += fmt.Sprintf(", %d failed", failedCount)
	}
	summary += "; original archived here"

	return routeSimple(path, zipArchiveDir, summary)
}

func extractZipEntry(f *zip.File, destPath string) error {
	rc, err := f.Open()
	if err != nil {
		return err
	}
	defer rc.Close()

	out, err := os.OpenFile(destPath, os.O_WRONLY|os.O_CREATE|os.O_TRUNC, 0644)
	if err != nil {
		return err
	}
	defer out.Close()

	_, err = io.Copy(out, rc)
	return err
}
