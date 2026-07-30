package main

import (
	"fmt"
	"image"
	"image/color"
	"image/jpeg"
	"image/png"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"strings"
	"syscall"
	"time"

	"golang.org/x/image/bmp"
	"golang.org/x/image/tiff"
	"golang.org/x/image/webp"
)

// Mirrors image_handling.py: dual-pass OCR (raw vs. contrast-enhanced),
// cross-checked against each other rather than trusting a single pass.
// Uses the same underlying Tesseract engine binary the Python version
// shelled out to via pytesseract -- this is not "using Python", it's the
// same OCR engine, just invoked directly instead of through a wrapper.

const (
	tesseractPath              = `C:\Program Files\Tesseract-OCR\tesseract.exe`
	textWordThreshold          = 8
	agreementSimilarityThresh  = 0.92
	screenshotRetentionDays    = 14
	ocrDiscrepancyDirName      = "ocr_discrepancies"
)

var imageExtensions = map[string]bool{
	".png": true, ".jpg": true, ".jpeg": true, ".bmp": true, ".webp": true, ".tiff": true,
}

func isImageFile(path string) bool {
	return imageExtensions[extLower(path)]
}

func decodeImage(path string) (image.Image, error) {
	f, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer f.Close()

	switch extLower(path) {
	case ".png":
		return png.Decode(f)
	case ".jpg", ".jpeg":
		return jpeg.Decode(f)
	case ".bmp":
		return bmp.Decode(f)
	case ".tiff":
		return tiff.Decode(f)
	case ".webp":
		return webp.Decode(f)
	default:
		return nil, fmt.Errorf("unsupported image extension")
	}
}

// preprocessEnhanced mirrors image_handling.py's _preprocess_enhanced:
// grayscale + autocontrast (linear histogram stretch) + a light sharpen.
// Deliberately different from the raw pass, so the two OCR runs can
// actually catch each other's mistakes instead of repeating the same read.
func preprocessEnhanced(img image.Image) image.Image {
	bounds := img.Bounds()
	gray := image.NewGray(bounds)
	minV, maxV := uint8(255), uint8(0)
	for y := bounds.Min.Y; y < bounds.Max.Y; y++ {
		for x := bounds.Min.X; x < bounds.Max.X; x++ {
			g := color.GrayModel.Convert(img.At(x, y)).(color.Gray).Y
			gray.SetGray(x, y, color.Gray{Y: g})
			if g < minV {
				minV = g
			}
			if g > maxV {
				maxV = g
			}
		}
	}

	// Autocontrast: linearly stretch [minV, maxV] to [0, 255].
	stretched := image.NewGray(bounds)
	spread := int(maxV) - int(minV)
	for y := bounds.Min.Y; y < bounds.Max.Y; y++ {
		for x := bounds.Min.X; x < bounds.Max.X; x++ {
			v := int(gray.GrayAt(x, y).Y)
			var out uint8
			if spread <= 0 {
				out = uint8(v)
			} else {
				out = uint8((v - int(minV)) * 255 / spread)
			}
			stretched.SetGray(x, y, color.Gray{Y: out})
		}
	}

	// Light sharpen via a simple unsharp-mask-style 3x3 convolution.
	return sharpenGray(stretched)
}

func sharpenGray(img *image.Gray) *image.Gray {
	bounds := img.Bounds()
	out := image.NewGray(bounds)
	kernel := [3][3]int{{0, -1, 0}, {-1, 5, -1}, {0, -1, 0}}
	for y := bounds.Min.Y; y < bounds.Max.Y; y++ {
		for x := bounds.Min.X; x < bounds.Max.X; x++ {
			sum := 0
			for ky := -1; ky <= 1; ky++ {
				for kx := -1; kx <= 1; kx++ {
					px, py := x+kx, y+ky
					if px < bounds.Min.X {
						px = bounds.Min.X
					}
					if px >= bounds.Max.X {
						px = bounds.Max.X - 1
					}
					if py < bounds.Min.Y {
						py = bounds.Min.Y
					}
					if py >= bounds.Max.Y {
						py = bounds.Max.Y - 1
					}
					sum += int(img.GrayAt(px, py).Y) * kernel[ky+1][kx+1]
				}
			}
			if sum < 0 {
				sum = 0
			}
			if sum > 255 {
				sum = 255
			}
			out.SetGray(x, y, color.Gray{Y: uint8(sum)})
		}
	}
	return out
}

func writeTempPNG(img image.Image, dir string) (string, error) {
	f, err := os.CreateTemp(dir, "ocr_pass_*.png")
	if err != nil {
		return "", err
	}
	defer f.Close()
	if err := png.Encode(f, img); err != nil {
		os.Remove(f.Name())
		return "", err
	}
	return f.Name(), nil
}

func runTesseract(imagePath string) (string, error) {
	cmd := exec.Command(tesseractPath, imagePath, "stdout")
	// tesseract.exe is a console-subsystem executable. Since this watcher
	// itself has no console (windowsgui build), Windows would otherwise
	// allocate a new, briefly-visible console window for it -- HideWindow
	// suppresses that so OCR never flashes a window on screen.
	cmd.SysProcAttr = &syscall.SysProcAttr{HideWindow: true}
	out, err := cmd.Output()
	if err != nil {
		return "", err
	}
	return strings.TrimSpace(string(out)), nil
}

func normalizeForComparison(s string) string {
	return strings.ToLower(strings.Join(strings.Fields(s), " "))
}

// similarityRatio approximates Python's difflib.SequenceMatcher.ratio()
// (2*matches / total length) using LCS length as the match count -- a
// close conceptual equivalent for a threshold-based agreement check.
func similarityRatio(a, b string) float64 {
	if a == "" && b == "" {
		return 1.0
	}
	lcs := lcsLength(a, b)
	total := len(a) + len(b)
	if total == 0 {
		return 1.0
	}
	return 2.0 * float64(lcs) / float64(total)
}

func lcsLength(a, b string) int {
	ra, rb := []rune(a), []rune(b)
	n, m := len(ra), len(rb)
	if n == 0 || m == 0 {
		return 0
	}
	prev := make([]int, m+1)
	curr := make([]int, m+1)
	for i := 1; i <= n; i++ {
		for j := 1; j <= m; j++ {
			if ra[i-1] == rb[j-1] {
				curr[j] = prev[j-1] + 1
			} else if prev[j] >= curr[j-1] {
				curr[j] = prev[j]
			} else {
				curr[j] = curr[j-1]
			}
		}
		prev, curr = curr, prev
	}
	return prev[m]
}

type ocrCrossCheckResult struct {
	agreed        bool
	text          string
	rawText       string
	enhancedText  string
	similarity    float64
	bothFailed    bool
}

func ocrCrossChecked(path string) ocrCrossCheckResult {
	img, err := decodeImage(path)
	if err != nil {
		return ocrCrossCheckResult{bothFailed: true}
	}

	tmpDir := filepath.Dir(path)

	rawPath, err := writeTempPNG(img, tmpDir)
	if err != nil {
		return ocrCrossCheckResult{bothFailed: true}
	}
	defer os.Remove(rawPath)
	rawText, rawErr := runTesseract(rawPath)

	enhancedImg := preprocessEnhanced(img)
	enhancedPath, err := writeTempPNG(enhancedImg, tmpDir)
	if err != nil {
		return ocrCrossCheckResult{bothFailed: true}
	}
	defer os.Remove(enhancedPath)
	enhancedText, enhancedErr := runTesseract(enhancedPath)

	if rawErr != nil && enhancedErr != nil {
		return ocrCrossCheckResult{bothFailed: true}
	}

	sim := similarityRatio(normalizeForComparison(rawText), normalizeForComparison(enhancedText))
	agreed := sim >= agreementSimilarityThresh

	result := ocrCrossCheckResult{
		agreed:       agreed,
		rawText:      rawText,
		enhancedText: enhancedText,
		similarity:   sim,
	}
	if agreed {
		result.text = enhancedText
	}
	return result
}

// classifyImage mirrors image_handling.py's handle_image_file(): archives
// the original first (never deleted), OCRs it twice with different
// preprocessing, and routes based on whether the two passes agree.
func classifyImage(path string) (string, string, error) {
	if err := os.MkdirAll(imageArchiveDir, 0755); err != nil {
		return "", "", err
	}
	if err := os.MkdirAll(needsReviewDir, 0755); err != nil {
		return "", "", err
	}

	timestamp := time.Now().Format("20060102_150405")
	archivedPath := filepath.Join(imageArchiveDir, fmt.Sprintf("%s_%s", timestamp, filepath.Base(path)))
	if err := os.MkdirAll(filepath.Dir(archivedPath), 0755); err != nil {
		return "", "", err
	}
	if err := os.Rename(path, archivedPath); err != nil {
		return "", "", err
	}

	if _, err := os.Stat(tesseractPath); err != nil {
		fallback := filepath.Join(needsReviewDir, filepath.Base(archivedPath))
		os.Rename(archivedPath, fallback)
		return fmt.Sprintf("OCR unavailable (tesseract.exe not found) — filed to %s without transcription", needsReviewDir), fallback, nil
	}

	result := ocrCrossChecked(archivedPath)
	if result.bothFailed {
		fallback := filepath.Join(needsReviewDir, filepath.Base(archivedPath))
		os.Rename(archivedPath, fallback)
		return "OCR failed (both passes) — filed for manual review", fallback, nil
	}

	rawWords := len(strings.Fields(result.rawText))
	enhancedWords := len(strings.Fields(result.enhancedText))
	bestWords := rawWords
	if enhancedWords > bestWords {
		bestWords = enhancedWords
	}

	if bestWords < textWordThreshold {
		contentDir := filepath.Join(needsReviewDir, "images")
		os.MkdirAll(contentDir, 0755)
		finalPath := filepath.Join(contentDir, filepath.Base(archivedPath))
		os.Rename(archivedPath, finalPath)
		return fmt.Sprintf("image with little/no OCR text (%d words, best of 2 passes) — filed for future vision analysis (not yet implemented)", bestWords), finalPath, nil
	}

	if !result.agreed {
		discrepancyDir := filepath.Join(needsReviewDir, ocrDiscrepancyDirName)
		os.MkdirAll(discrepancyDir, 0755)
		finalImagePath := filepath.Join(discrepancyDir, filepath.Base(archivedPath))
		os.Rename(archivedPath, finalImagePath)

		reportPath := filepath.Join(discrepancyDir, fmt.Sprintf("%s_%s_DISCREPANCY.md",
			timestamp, strings.TrimSuffix(filepath.Base(path), filepath.Ext(path))))
		reportContent := fmt.Sprintf(
			"<!-- OCR cross-check disagreement for %s, %s. Similarity score: %.4f (agreement threshold: %.2f). Original image kept at: %s in this same folder. -->\n\n"+
				"# OCR cross-check disagreement — needs manual review\n\n## Raw-pass transcription\n\n%s\n\n## Enhanced-pass transcription\n\n%s\n\n"+
				"Neither version was auto-filed. Compare against the original image (%s) and manually drop a corrected .md into inbox/ if you want this processed further.\n",
			filepath.Base(path), time.Now().Format("2006-01-02 15:04:05"), result.similarity, agreementSimilarityThresh,
			filepath.Base(finalImagePath), orNoText(result.rawText), orNoText(result.enhancedText), filepath.Base(finalImagePath),
		)
		os.WriteFile(reportPath, []byte(reportContent), 0644)

		note := fmt.Sprintf("image screenshot — OCR cross-check DISAGREED (similarity %.2f) — both transcriptions filed to _needs_review/%s/ for manual review, nothing auto-filed", result.similarity, ocrDiscrepancyDirName)
		return note, finalImagePath, nil
	}

	mdName := fmt.Sprintf("screenshot_%s_ocr.md", timestamp)
	mdPath := filepath.Join(inboxDir, mdName)
	mdContent := fmt.Sprintf(
		"<!-- OCR transcription of %s, %s. Cross-checked: raw vs. contrast-enhanced passes agreed (similarity %.2f). Original image kept at: %s (see image archive folder). -->\n\n%s\n",
		filepath.Base(archivedPath), time.Now().Format("2006-01-02 15:04:05"), result.similarity, filepath.Base(archivedPath), result.text,
	)
	if err := os.WriteFile(mdPath, []byte(mdContent), 0644); err != nil {
		return "", "", err
	}

	note := fmt.Sprintf("image screenshot — OCR cross-check agreed (similarity %.2f), .md dropped back into inbox/ for normal processing", result.similarity)
	return note, mdPath, nil
}

func orNoText(s string) string {
	if s == "" {
		return "(no text)"
	}
	return s
}

var timestampPrefixRE = regexp.MustCompile(`^(\d{8}_\d{6})_`)

func confirmedAtFromFilename(name string) (time.Time, bool) {
	m := timestampPrefixRE.FindStringSubmatch(name)
	if m == nil {
		return time.Time{}, false
	}
	t, err := time.ParseInLocation("20060102_150405", m[1], time.Local)
	if err != nil {
		return time.Time{}, false
	}
	return t, true
}

// cleanupAgedConfirmedScreenshots recycles (never permanently deletes)
// confirmed screenshot images once they're older than screenshotRetentionDays
// past their confirmed-transcribed date. Only ever touches imageArchiveDir,
// which under this pipeline's routing holds ONLY cross-check-agreed images.
func cleanupAgedConfirmedScreenshots() {
	entries, err := os.ReadDir(imageArchiveDir)
	if err != nil {
		return
	}
	cutoff := time.Now().AddDate(0, 0, -screenshotRetentionDays)
	for _, e := range entries {
		if e.IsDir() {
			continue
		}
		confirmedAt, ok := confirmedAtFromFilename(e.Name())
		if !ok {
			info, err := e.Info()
			if err != nil {
				continue
			}
			confirmedAt = info.ModTime()
		}
		if confirmedAt.After(cutoff) {
			continue
		}
		fullPath := filepath.Join(imageArchiveDir, e.Name())
		if err := recycleFile(fullPath); err != nil {
			logMsg("could not recycle %s: %v", e.Name(), err)
			continue
		}
		logMsg("Recycled aged confirmed screenshot: %s (confirmed %s)", e.Name(), confirmedAt.Format("2006-01-02"))
	}
}
