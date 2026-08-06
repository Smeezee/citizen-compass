package main

// capture.go - the backend-agnostic frame type and the fallback chain.

import (
	"fmt"
	"image"
	"strings"
)

// Frame is a captured image plus how it was obtained. The method is carried all
// the way into the sidecar JSON: when the question being answered is "is the
// font legible", knowing WHICH capture path produced the pixels is part of the
// answer, because the three paths do not produce identical images.
type Frame struct {
	Img    *image.RGBA
	Method string // "wgc" | "dxgi" | "gdi"
	Note   string // anything the backend wants on record (e.g. cropped-to-client)
	SrcW   int
	SrcH   int
}

// captureBackend is one way of getting pixels.
type captureBackend struct {
	name string
	fn   func(h HWND) (*Frame, error)
}

// backendChain is the order the work order specifies: Windows.Graphics.Capture
// first, DXGI second. GDI is a third rung that the order does not mention; it
// is here because it is the only path that still works when the other two are
// blocked by a driver or a policy, and a capture tool that returns nothing is
// worth less than one that returns a flawed image plus a note saying so.
func backendChain() []captureBackend {
	return []captureBackend{
		{"wgc", captureWGC},
		{"dxgi", captureDXGI},
		{"gdi", captureGDI},
	}
}

// CaptureWindow walks the chain and returns the first frame that is both
// produced without error AND passes the blank-frame check.
//
// THE BLANK-FRAME CHECK IS THE POINT OF THIS FUNCTION.
// Every one of these APIs can "succeed" against a hardware-accelerated game and
// hand back a fully black or fully transparent buffer. A backend that returns
// (frame, nil) has not proven it captured anything. Treating hr==S_OK as proof
// would be exactly the silent success this project keeps finding: a check that
// reports PASS because it never actually looked at the result.
//
// So a backend only counts as having worked if the pixels say so, and if none
// of them produce a non-blank frame the error explains what each one did rather
// than reporting a generic failure.
func CaptureWindow(h HWND, forced string) (*Frame, error) {
	var attempts []string

	for _, b := range backendChain() {
		if forced != "" && forced != b.name {
			continue
		}
		f, err := b.fn(h)
		if err != nil {
			attempts = append(attempts, fmt.Sprintf("%s: %v", b.name, err))
			continue
		}
		if f == nil || f.Img == nil {
			attempts = append(attempts, b.name+": returned no image")
			continue
		}
		if blank, why := looksBlank(f.Img); blank {
			attempts = append(attempts,
				fmt.Sprintf("%s: produced a blank frame (%s)", b.name, why))
			continue
		}
		return f, nil
	}

	if forced != "" && len(attempts) == 0 {
		return nil, fmt.Errorf("no such backend %q (want wgc, dxgi or gdi)", forced)
	}
	return nil, fmt.Errorf("every capture backend failed:\n    %s",
		strings.Join(attempts, "\n    "))
}

// looksBlank reports whether an image carries no usable content.
//
// Two distinct failure shapes, because they have different causes:
//   - fully uniform colour  -> the capture path handed back an untouched buffer
//     (classic black frame from GDI against a DX11 swapchain)
//   - fully zero alpha      -> WGC/DXGI surface copied without the alpha channel
//     being meaningful; the image will look empty in most viewers even though
//     the RGB data may be present
//
// Sampling rather than scanning every pixel: a 1920x1080 frame is 2M pixels and
// this runs on a hotkey press in front of a game. A stride that is coprime with
// the row width walks across rows rather than down a single column, so a frame
// that is black on the left third and correct elsewhere is not misjudged.
func looksBlank(img *image.RGBA) (bool, string) {
	b := img.Bounds()
	w, h := b.Dx(), b.Dy()
	if w == 0 || h == 0 {
		return true, "zero-sized"
	}

	total := w * h
	step := 7919 // prime, so successive samples land on different rows
	if total < step*4 {
		step = 1
	}

	var first [3]uint8
	haveFirst := false
	uniform := true
	anyAlpha := false
	samples := 0

	for i := 0; i < total; i += step {
		x := b.Min.X + (i % w)
		y := b.Min.Y + (i / w)
		if y >= b.Max.Y {
			break
		}
		o := img.PixOffset(x, y)
		r, g, bl, a := img.Pix[o], img.Pix[o+1], img.Pix[o+2], img.Pix[o+3]
		samples++
		if a != 0 {
			anyAlpha = true
		}
		if !haveFirst {
			first = [3]uint8{r, g, bl}
			haveFirst = true
			continue
		}
		if r != first[0] || g != first[1] || bl != first[2] {
			uniform = false
		}
	}

	if samples == 0 {
		return true, "no pixels sampled"
	}
	if uniform {
		return true, fmt.Sprintf("every one of %d sampled pixels is rgb(%d,%d,%d)",
			samples, first[0], first[1], first[2])
	}
	if !anyAlpha {
		return true, fmt.Sprintf("all %d sampled pixels have alpha=0", samples)
	}
	return false, ""
}

// forceOpaque sets alpha to 255 across the image.
//
// WGC and DXGI both hand back BGRA surfaces whose alpha channel is frequently
// meaningless - a game's backbuffer has no reason to keep a sensible alpha. PNG
// honours alpha, so writing those bytes through produces a file that looks
// blank or ghostly in a viewer while containing perfectly good colour data.
// Since these captures are opaque screen content by definition, the alpha is
// discarded rather than trusted.
func forceOpaque(img *image.RGBA) {
	p := img.Pix
	for i := 3; i < len(p); i += 4 {
		p[i] = 0xFF
	}
}

// cropToWindow cuts the window's rectangle out of a full-output image.
//
// originX/originY are the output's top-left in virtual-desktop coordinates, so
// a window on a secondary monitor is offset correctly instead of being cropped
// from the wrong place. The rect is clamped to the image: a window hanging off
// the edge of the screen yields the visible part rather than an error, and a
// rect with no overlap at all falls back to the full frame with a note, because
// a whole-screen capture still answers the legibility question.
func cropToWindow(full *image.RGBA, win RECT, originX, originY int) (*image.RGBA, string) {
	b := full.Bounds()

	x0 := int(win.Left) - originX
	y0 := int(win.Top) - originY
	x1 := int(win.Right) - originX
	y1 := int(win.Bottom) - originY

	if x0 < b.Min.X {
		x0 = b.Min.X
	}
	if y0 < b.Min.Y {
		y0 = b.Min.Y
	}
	if x1 > b.Max.X {
		x1 = b.Max.X
	}
	if y1 > b.Max.Y {
		y1 = b.Max.Y
	}

	if x1-x0 < 8 || y1-y0 < 8 {
		return full, "window rect did not overlap this output - kept the full screen instead"
	}

	sub := image.NewRGBA(image.Rect(0, 0, x1-x0, y1-y0))
	for y := y0; y < y1; y++ {
		copy(sub.Pix[(y-y0)*sub.Stride:(y-y0)*sub.Stride+(x1-x0)*4],
			full.Pix[full.PixOffset(x0, y):full.PixOffset(x1, y)])
	}
	if x1-x0 == b.Dx() && y1-y0 == b.Dy() {
		return sub, "window fills the output"
	}
	return sub, fmt.Sprintf("cropped to window rect %d,%d %dx%d", x0, y0, x1-x0, y1-y0)
}

// bgraToRGBA converts a tightly-packed or padded BGRA buffer into an RGBA
// image. rowPitch is the source stride in bytes, which is NOT always width*4 -
// D3D staging textures are padded to hardware alignment, and assuming
// width*4 produces the classic diagonally-skewed image.
func bgraToRGBA(src []byte, w, h, rowPitch int) *image.RGBA {
	img := image.NewRGBA(image.Rect(0, 0, w, h))
	for y := 0; y < h; y++ {
		s := y * rowPitch
		d := y * img.Stride
		for x := 0; x < w; x++ {
			si := s + x*4
			di := d + x*4
			if si+3 >= len(src) {
				break
			}
			img.Pix[di+0] = src[si+2] // R <- B
			img.Pix[di+1] = src[si+1] // G
			img.Pix[di+2] = src[si+0] // B <- R
			img.Pix[di+3] = src[si+3] // A
		}
	}
	return img
}
