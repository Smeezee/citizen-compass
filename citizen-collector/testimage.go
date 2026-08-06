package main

// testimage.go - synthetic images used by --selftest to prove the blank-frame
// detector works in BOTH directions.
//
// Hard rule 12: "feed it something that must fail, and confirm it fails". The
// blank-frame check is the one thing standing between a black capture and a
// written PNG that looks like a successful result, so it is the check most
// worth proving. newTestImage(.., false) must be rejected and
// newTestImage(.., true) must be accepted; a detector that cannot do both is
// not a detector.

import "image"

func newTestImage(w, h int, withContent bool) *image.RGBA {
	img := image.NewRGBA(image.Rect(0, 0, w, h))
	for y := 0; y < h; y++ {
		for x := 0; x < w; x++ {
			o := img.PixOffset(x, y)
			if withContent {
				// A deterministic pattern, not random: a selftest that passes
				// or fails depending on the draw is not a test. The multipliers
				// are coprime with the sampling stride in looksBlank so the
				// sampled pixels genuinely differ from one another.
				img.Pix[o+0] = uint8((x*7 + y*13) & 0xFF)
				img.Pix[o+1] = uint8((x*3 + y*29) & 0xFF)
				img.Pix[o+2] = uint8((x*11 + y*5) & 0xFF)
			} else {
				img.Pix[o+0] = 0
				img.Pix[o+1] = 0
				img.Pix[o+2] = 0
			}
			img.Pix[o+3] = 0xFF
		}
	}
	return img
}
