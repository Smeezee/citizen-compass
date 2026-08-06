package main

// capture_wgc.go - Windows.Graphics.Capture, the work order's primary path.
//
// WHY THIS ONE IS FIRST
//   WGC targets a window rather than a screen. It keeps working when the game
//   is fullscreen, when it is occluded, and when it moves, and it captures the
//   window's own composited output rather than whatever pixels happen to be on
//   the monitor. For "is the game's font legible in a captured frame" that is
//   the closest thing to ground truth available.
//
// WHY IT IS THE MOST CODE
//   WinRT is COM plus an activation model plus HSTRING, and with CGO_ENABLED=0
//   every bit of it is hand-dispatched. A WinRT interface derives from
//   IInspectable, which adds THREE methods (GetIids, GetRuntimeClassName,
//   GetTrustLevel) after IUnknown's three - so a WinRT interface's own methods
//   start at vtable slot 6, not slot 3. That offset is the single easiest thing
//   to get wrong here and it fails silently rather than loudly.
//
// FREE-THREADED ON PURPose
//   IDirect3D11CaptureFramePool::Create requires a DispatcherQueue on the
//   calling thread - i.e. a UI message pump owned by WinRT. This program's
//   message pump belongs to the hotkey. CreateFreeThreaded exists exactly for
//   this case and needs no dispatcher, so it is what we call.

import (
	"fmt"
	"image"
	"syscall"
	"time"
	"unsafe"
)

func sleepMS(n int) { time.Sleep(time.Duration(n) * time.Millisecond) }

// --- GUIDs -----------------------------------------------------------------

var (
	iidIGraphicsCaptureItemInterop = GUID{0x3628E81B, 0x3CAC, 0x4C60, [8]byte{0xB7, 0xF4, 0x23, 0xCE, 0x0E, 0x0C, 0x33, 0x56}}
	iidIGraphicsCaptureItem        = GUID{0x79C3F95B, 0x31F7, 0x4EC2, [8]byte{0xA4, 0x64, 0x63, 0x2E, 0xF5, 0xD3, 0x07, 0x60}}
	iidIFramePoolStatics2          = GUID{0x589b103f, 0x6bbc, 0x5df5, [8]byte{0xa9, 0x91, 0x02, 0xe2, 0x8b, 0x3b, 0x66, 0xd5}}
	iidIFramePoolStatics           = GUID{0x7784056a, 0x67aa, 0x4d53, [8]byte{0xae, 0x54, 0x10, 0x88, 0xd5, 0xa8, 0xca, 0x21}}
	iidIDirect3DDevice             = GUID{0xa37624ab, 0x8d5f, 0x4650, [8]byte{0x9d, 0x3e, 0x9e, 0xae, 0x3d, 0x9b, 0xc6, 0x70}}
	iidIDirect3DDxgiInterfaceAccess = GUID{0xA9B3D012, 0x3DF2, 0x4EE3, [8]byte{0xB8, 0xD1, 0x86, 0x95, 0xF4, 0x57, 0xD3, 0xC1}}
	iidICaptureSessionStatics      = GUID{0x2224a540, 0x5974, 0x49aa, [8]byte{0xb2, 0x32, 0x08, 0x82, 0x96, 0x8a, 0x59, 0x80}}
	iidICaptureSession3            = GUID{0xf2cdd966, 0x22ae, 0x5ea1, [8]byte{0x95, 0x96, 0x3a, 0x28, 0x93, 0x44, 0xc3, 0xbe}}
	iidIClosable                   = GUID{0x30D5A829, 0x7FA4, 0x4026, [8]byte{0x83, 0xBB, 0xD7, 0x5B, 0xAE, 0x4E, 0xA9, 0x9E}}
)

const (
	classGraphicsCaptureItem = "Windows.Graphics.Capture.GraphicsCaptureItem"
	classFramePool           = "Windows.Graphics.Capture.Direct3D11CaptureFramePool"
	classCaptureSession      = "Windows.Graphics.Capture.GraphicsCaptureSession"

	// DirectXPixelFormat.B8G8R8A8UIntNormalized
	pixelFormatB8G8R8A8 = 87
)

type sizeInt32 struct{ Width, Height int32 }

// --- vtables ---------------------------------------------------------------

// IInspectable adds three slots on top of IUnknown. Every WinRT vtable below
// embeds this, which is what puts their first real method at slot 6.
type IInspectableVtbl struct {
	IUnknownVtbl
	GetIids             uintptr
	GetRuntimeClassName uintptr
	GetTrustLevel       uintptr
}

type igcItemInteropVtbl struct {
	IUnknownVtbl
	CreateForWindow  uintptr
	CreateForMonitor uintptr
}

type igcItemInterop struct{ Vtbl *igcItemInteropVtbl }

type igcItemVtbl struct {
	IInspectableVtbl
	GetDisplayName uintptr
	GetSize        uintptr
	AddClosed      uintptr
	RemoveClosed   uintptr
}

type igcItem struct{ Vtbl *igcItemVtbl }

type iFramePoolStatics2Vtbl struct {
	IInspectableVtbl
	CreateFreeThreaded uintptr
}

type iFramePoolStatics2 struct{ Vtbl *iFramePoolStatics2Vtbl }

type iFramePoolVtbl struct {
	IInspectableVtbl
	Recreate             uintptr
	TryGetNextFrame      uintptr
	AddFrameArrived      uintptr
	RemoveFrameArrived   uintptr
	CreateCaptureSession uintptr
	GetDispatcherQueue   uintptr
}

type iFramePool struct{ Vtbl *iFramePoolVtbl }

type iCaptureSessionVtbl struct {
	IInspectableVtbl
	StartCapture uintptr
}

type iCaptureSession struct{ Vtbl *iCaptureSessionVtbl }

type iCaptureSession3Vtbl struct {
	IInspectableVtbl
	GetIsBorderRequired uintptr
	PutIsBorderRequired uintptr
}

type iCaptureSession3 struct{ Vtbl *iCaptureSession3Vtbl }

type iCaptureFrameVtbl struct {
	IInspectableVtbl
	GetSurface            uintptr
	GetSystemRelativeTime uintptr
	GetContentSize        uintptr
}

type iCaptureFrame struct{ Vtbl *iCaptureFrameVtbl }

type iDxgiInterfaceAccessVtbl struct {
	IUnknownVtbl
	GetInterface uintptr
}

type iDxgiInterfaceAccess struct{ Vtbl *iDxgiInterfaceAccessVtbl }

type iClosableVtbl struct {
	IInspectableVtbl
	Close uintptr
}

type iCaptureSessionStaticsVtbl struct {
	IInspectableVtbl
	IsSupported uintptr
}

type iCaptureSessionStatics struct{ Vtbl *iCaptureSessionStaticsVtbl }

// closeIt calls IClosable::Close if the object supports it. WinRT capture
// objects hold a GPU frame pool; leaving them to the finaliser leaks a
// duplication slot, and the slot count is finite per session.
func closeIt(p unsafe.Pointer) {
	if p == nil {
		return
	}
	cp, err := (*IUnknown)(p).QueryInterface(&iidIClosable)
	if err != nil {
		return
	}
	defer releaseAny(cp)
	v := *(**iClosableVtbl)(cp)
	syscall.SyscallN(v.Close, uintptr(cp))
}

// --- capture ---------------------------------------------------------------

func captureWGC(h HWND) (*Frame, error) {
	if h == 0 {
		return nil, fmt.Errorf("no window handle")
	}

	if err := RoInitialize(RO_INIT_MULTITHREADED); err != nil {
		return nil, err
	}

	// Ask the OS whether capture is available at all before building anything.
	// On an unsupported build this is a clean, explanatory failure instead of a
	// confusing one four calls deeper.
	if statP, err := RoGetActivationFactory(classCaptureSession, &iidICaptureSessionStatics); err == nil {
		defer releaseAny(statP)
		st := (*iCaptureSessionStatics)(statP)
		var supported int32
		hr, _, _ := syscall.SyscallN(st.Vtbl.IsSupported, uintptr(statP), uintptr(unsafe.Pointer(&supported)))
		if succeeded(hr) && supported == 0 {
			return nil, fmt.Errorf("GraphicsCaptureSession.IsSupported returned false on this system")
		}
	}

	// GraphicsCaptureItem for the window, via the interop factory.
	interopP, err := RoGetActivationFactory(classGraphicsCaptureItem, &iidIGraphicsCaptureItemInterop)
	if err != nil {
		return nil, fmt.Errorf("no IGraphicsCaptureItemInterop: %w", err)
	}
	defer releaseAny(interopP)
	interop := (*igcItemInterop)(interopP)

	var itemP unsafe.Pointer
	hr, _, _ := syscall.SyscallN(interop.Vtbl.CreateForWindow,
		uintptr(interopP), uintptr(h),
		uintptr(unsafe.Pointer(&iidIGraphicsCaptureItem)),
		uintptr(unsafe.Pointer(&itemP)))
	if !succeeded(hr) || itemP == nil {
		return nil, fmt.Errorf("CreateForWindow failed: hr=0x%08X (the window may be "+
			"a console, a UWP host, or otherwise not capturable)", uint32(hr))
	}
	defer releaseAny(itemP)
	item := (*igcItem)(itemP)

	var size sizeInt32
	hr, _, _ = syscall.SyscallN(item.Vtbl.GetSize, uintptr(itemP), uintptr(unsafe.Pointer(&size)))
	if !succeeded(hr) || size.Width <= 0 || size.Height <= 0 {
		return nil, fmt.Errorf("capture item reported size %dx%d", size.Width, size.Height)
	}

	// D3D device, wrapped as a WinRT IDirect3DDevice.
	dev, ctx, driver, err := createD3D11Device()
	if err != nil {
		return nil, err
	}
	defer dev.Release2()
	defer ctx.Release2()

	dxgiDevP, err := (*IUnknown)(unsafe.Pointer(dev)).QueryInterface(&iidIDXGIDevice)
	if err != nil {
		return nil, err
	}
	defer releaseAny(dxgiDevP)

	var inspectableDevP unsafe.Pointer
	hr, _, _ = syscall.SyscallN(procCreateDirect3D11DeviceFromDXGIDevice.Addr(),
		uintptr(dxgiDevP), uintptr(unsafe.Pointer(&inspectableDevP)))
	if !succeeded(hr) || inspectableDevP == nil {
		return nil, hrErr("CreateDirect3D11DeviceFromDXGIDevice", hr)
	}
	defer releaseAny(inspectableDevP)

	rtDevP, err := (*IUnknown)(inspectableDevP).QueryInterface(&iidIDirect3DDevice)
	if err != nil {
		return nil, fmt.Errorf("wrapped device is not an IDirect3DDevice: %w", err)
	}
	defer releaseAny(rtDevP)

	// Free-threaded frame pool - no DispatcherQueue needed. See header.
	poolStaticsP, err := RoGetActivationFactory(classFramePool, &iidIFramePoolStatics2)
	if err != nil {
		return nil, fmt.Errorf("no IDirect3D11CaptureFramePoolStatics2 "+
			"(CreateFreeThreaded unavailable, needs Windows 10 1809+): %w", err)
	}
	defer releaseAny(poolStaticsP)
	poolStatics := (*iFramePoolStatics2)(poolStaticsP)

	// SizeInt32 is an 8-byte struct passed BY VALUE. On the x64 ABI that means
	// it travels in a single register, so it is packed into one uintptr here
	// rather than passed as a pointer.
	packedSize := uintptr(uint32(size.Width)) | uintptr(uint32(size.Height))<<32

	var poolP unsafe.Pointer
	hr, _, _ = syscall.SyscallN(poolStatics.Vtbl.CreateFreeThreaded,
		uintptr(poolStaticsP),
		uintptr(rtDevP),
		uintptr(pixelFormatB8G8R8A8),
		2, // buffers
		packedSize,
		uintptr(unsafe.Pointer(&poolP)))
	if !succeeded(hr) || poolP == nil {
		return nil, hrErr("CreateFreeThreaded", hr)
	}
	defer releaseAny(poolP)
	defer closeIt(poolP)
	pool := (*iFramePool)(poolP)

	var sessP unsafe.Pointer
	hr, _, _ = syscall.SyscallN(pool.Vtbl.CreateCaptureSession,
		uintptr(poolP), uintptr(itemP), uintptr(unsafe.Pointer(&sessP)))
	if !succeeded(hr) || sessP == nil {
		return nil, hrErr("CreateCaptureSession", hr)
	}
	defer releaseAny(sessP)
	defer closeIt(sessP)
	sess := (*iCaptureSession)(sessP)

	// Win11 draws a yellow "this window is being captured" border by default.
	// It lands inside the captured pixels, which is noise in a legibility test.
	// Not available on older builds - failure here is ignored on purpose.
	if s3P, err := (*IUnknown)(sessP).QueryInterface(&iidICaptureSession3); err == nil {
		s3 := (*iCaptureSession3)(s3P)
		syscall.SyscallN(s3.Vtbl.PutIsBorderRequired, uintptr(s3P), 0)
		releaseAny(s3P)
	}

	hr, _, _ = syscall.SyscallN(sess.Vtbl.StartCapture, uintptr(sessP))
	if !succeeded(hr) {
		return nil, hrErr("StartCapture", hr)
	}

	// Poll for the first real frame. TryGetNextFrame legitimately returns S_OK
	// with a NULL frame until the pool has one, so a null is "not yet", not an
	// error - but a null forever is a failure and must be reported as one
	// rather than turning into an empty image.
	var framePtr unsafe.Pointer
	for attempt := 0; attempt < 200; attempt++ {
		hr, _, _ = syscall.SyscallN(pool.Vtbl.TryGetNextFrame,
			uintptr(poolP), uintptr(unsafe.Pointer(&framePtr)))
		if !succeeded(hr) {
			return nil, hrErr("TryGetNextFrame", hr)
		}
		if framePtr != nil {
			break
		}
		sleepMS(10)
	}
	if framePtr == nil {
		return nil, fmt.Errorf("no frame arrived within ~2s of StartCapture")
	}
	defer releaseAny(framePtr)
	defer closeIt(framePtr)
	frame := (*iCaptureFrame)(framePtr)

	var surfP unsafe.Pointer
	hr, _, _ = syscall.SyscallN(frame.Vtbl.GetSurface, uintptr(framePtr), uintptr(unsafe.Pointer(&surfP)))
	if !succeeded(hr) || surfP == nil {
		return nil, hrErr("IDirect3D11CaptureFrame::get_Surface", hr)
	}
	defer releaseAny(surfP)

	accP, err := (*IUnknown)(surfP).QueryInterface(&iidIDirect3DDxgiInterfaceAccess)
	if err != nil {
		return nil, fmt.Errorf("surface has no IDirect3DDxgiInterfaceAccess: %w", err)
	}
	defer releaseAny(accP)
	acc := (*iDxgiInterfaceAccess)(accP)

	var texP unsafe.Pointer
	hr, _, _ = syscall.SyscallN(acc.Vtbl.GetInterface,
		uintptr(accP),
		uintptr(unsafe.Pointer(&iidID3D11Texture2D)),
		uintptr(unsafe.Pointer(&texP)))
	if !succeeded(hr) || texP == nil {
		return nil, hrErr("IDirect3DDxgiInterfaceAccess::GetInterface(ID3D11Texture2D)", hr)
	}
	defer releaseAny(texP)

	img, w, ht, err := readbackTexture(dev, ctx, texP)
	if err != nil {
		return nil, err
	}
	forceOpaque(img)

	return &Frame{
		Img:    img,
		Method: "wgc",
		Note: fmt.Sprintf("Windows.Graphics.Capture on window, item size %dx%d, %s driver",
			size.Width, size.Height, driver),
		SrcW: w,
		SrcH: ht,
	}, nil
}

// readbackTexture copies a GPU texture into a CPU-readable staging texture and
// converts it to RGBA. Shared by WGC; DXGI does the same inline because it also
// needs the un-cropped dimensions.
func readbackTexture(dev *id3d11Device, ctx *id3d11DeviceContext, texP unsafe.Pointer) (*image.RGBA, int, int, error) {
	texVtbl := *(**struct {
		IUnknownVtbl
		GetDevice               uintptr
		GetPrivateData          uintptr
		SetPrivateData          uintptr
		SetPrivateDataInterface uintptr
		GetType                 uintptr
		SetEvictionPriority     uintptr
		GetEvictionPriority     uintptr
		GetDesc                 uintptr
	})(texP)

	var desc d3d11Texture2DDesc
	syscall.SyscallN(texVtbl.GetDesc, uintptr(texP), uintptr(unsafe.Pointer(&desc)))
	if desc.Width == 0 || desc.Height == 0 {
		return nil, 0, 0, fmt.Errorf("texture describes itself as %dx%d", desc.Width, desc.Height)
	}

	staging := desc
	staging.Usage = usageStaging
	staging.BindFlags = 0
	staging.CPUAccessFlags = cpuAccessRead
	staging.MiscFlags = 0

	var stageP unsafe.Pointer
	hr, _, _ := syscall.SyscallN(dev.Vtbl.CreateTexture2D,
		uintptr(unsafe.Pointer(dev)),
		uintptr(unsafe.Pointer(&staging)), 0,
		uintptr(unsafe.Pointer(&stageP)))
	if !succeeded(hr) {
		return nil, 0, 0, hrErr("CreateTexture2D(staging)", hr)
	}
	defer releaseAny(stageP)

	syscall.SyscallN(ctx.Vtbl.CopyResource,
		uintptr(unsafe.Pointer(ctx)), uintptr(stageP), uintptr(texP))

	var mapped d3d11MappedSubresource
	hr, _, _ = syscall.SyscallN(ctx.Vtbl.Map,
		uintptr(unsafe.Pointer(ctx)), uintptr(stageP), 0,
		uintptr(mapRead), 0, uintptr(unsafe.Pointer(&mapped)))
	if !succeeded(hr) {
		return nil, 0, 0, hrErr("Map(staging)", hr)
	}

	w, ht := int(desc.Width), int(desc.Height)
	pitch := int(mapped.RowPitch)
	raw := make([]byte, pitch*ht)
	copy(raw, unsafe.Slice((*byte)(mapped.PData), pitch*ht))

	syscall.SyscallN(ctx.Vtbl.Unmap, uintptr(unsafe.Pointer(ctx)), uintptr(stageP), 0)

	return bgraToRGBA(raw, w, ht, pitch), w, ht, nil
}
