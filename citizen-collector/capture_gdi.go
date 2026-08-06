package main

// capture_gdi.go - GDI PrintWindow / BitBlt.
//
// The last rung of the chain. Cheap, dependency-free, and works when the other
// two are blocked. Against a hardware-accelerated game it usually returns a
// black frame - which is precisely why CaptureWindow checks the pixels instead
// of the return code before accepting a backend's output.

import (
	"fmt"
	"image"
	"syscall"
	"unsafe"
)

const (
	srcCopy       = 0x00CC0020
	captureBlt    = 0x40000000
	dibRGBColors  = 0
	biRGB         = 0
	pwClientOnly  = 0x00000001
	// PW_RENDERFULLCONTENT. Undocumented until Win8.1, this is what makes
	// PrintWindow work against composited/DirectComposition windows at all.
	pwRenderFullContent = 0x00000002
)

type bitmapInfoHeader struct {
	Size          uint32
	Width         int32
	Height        int32
	Planes        uint16
	BitCount      uint16
	Compression   uint32
	SizeImage     uint32
	XPelsPerMeter int32
	YPelsPerMeter int32
	ClrUsed       uint32
	ClrImportant  uint32
}

type bitmapInfo struct {
	Header bitmapInfoHeader
	Colors [3]uint32
}

func captureGDI(h HWND) (*Frame, error) {
	if h == 0 {
		return nil, fmt.Errorf("no window handle")
	}
	r, err := GetWindowRectOf(h)
	if err != nil {
		return nil, err
	}
	w, ht := int(r.Width()), int(r.Height())
	if w <= 0 || ht <= 0 {
		return nil, fmt.Errorf("window rect is %dx%d", w, ht)
	}

	srcDC, _, _ := syscall.SyscallN(procGetWindowDC.Addr(), uintptr(h))
	if srcDC == 0 {
		return nil, fmt.Errorf("GetWindowDC returned NULL")
	}
	defer syscall.SyscallN(procReleaseDC.Addr(), uintptr(h), srcDC)

	memDC, _, _ := syscall.SyscallN(procCreateCompatibleDC.Addr(), srcDC)
	if memDC == 0 {
		return nil, fmt.Errorf("CreateCompatibleDC returned NULL")
	}
	defer syscall.SyscallN(procDeleteDC.Addr(), memDC)

	bmp, _, _ := syscall.SyscallN(procCreateCompatibleBitmap.Addr(), srcDC, uintptr(w), uintptr(ht))
	if bmp == 0 {
		return nil, fmt.Errorf("CreateCompatibleBitmap returned NULL")
	}
	defer syscall.SyscallN(procDeleteObject.Addr(), bmp)

	old, _, _ := syscall.SyscallN(procSelectObject.Addr(), memDC, bmp)
	defer syscall.SyscallN(procSelectObject.Addr(), memDC, old)

	// PrintWindow first: it asks the window to render itself, which reaches
	// content that BitBlt from the screen DC cannot. Fall back to BitBlt if it
	// refuses. Both are attempted before giving up because they fail on
	// different window types.
	note := "PrintWindow(PW_RENDERFULLCONTENT)"
	ok, _, _ := syscall.SyscallN(procPrintWindow.Addr(), uintptr(h), memDC, uintptr(pwRenderFullContent))
	if ok == 0 {
		note = "BitBlt(SRCCOPY|CAPTUREBLT)"
		ok2, _, err2 := syscall.SyscallN(procBitBlt.Addr(),
			memDC, 0, 0, uintptr(w), uintptr(ht),
			srcDC, 0, 0, uintptr(srcCopy|captureBlt))
		if ok2 == 0 {
			return nil, fmt.Errorf("PrintWindow and BitBlt both failed: %v", err2)
		}
	}

	// Negative Height requests a top-down DIB. Without it the rows come back
	// bottom-up and the image is vertically mirrored.
	bi := bitmapInfo{Header: bitmapInfoHeader{
		Size:        uint32(unsafe.Sizeof(bitmapInfoHeader{})),
		Width:       int32(w),
		Height:      -int32(ht),
		Planes:      1,
		BitCount:    32,
		Compression: biRGB,
	}}

	buf := make([]byte, w*ht*4)
	got, _, err3 := syscall.SyscallN(procGetDIBits.Addr(),
		memDC, bmp, 0, uintptr(ht),
		uintptr(unsafe.Pointer(&buf[0])),
		uintptr(unsafe.Pointer(&bi)),
		uintptr(dibRGBColors))
	if got == 0 {
		return nil, fmt.Errorf("GetDIBits copied 0 scanlines: %v", err3)
	}

	img := bgraToRGBA(buf, w, ht, w*4)
	// GDI 32bpp DIBs leave the top byte undefined rather than a real alpha.
	forceOpaque(img)

	return &Frame{
		Img:    img,
		Method: "gdi",
		Note:   note + "; whole window rect including border/titlebar",
		SrcW:   w,
		SrcH:   ht,
	}, nil
}

var _ = image.NewRGBA
