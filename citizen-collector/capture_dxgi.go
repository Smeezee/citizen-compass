package main

// capture_dxgi.go - DXGI Desktop Duplication.
//
// Captures the whole output the window sits on, then crops to the window rect.
// This is the path that works against a game running fullscreen, where the
// window-targeted APIs are least reliable.
//
// VTABLE LAYOUTS
//   Every interface below is written out in full, in declaration order,
//   including the inherited methods and the ones this file never calls. That is
//   not padding. A COM vtable is positional: ID3D11DeviceContext inherits seven
//   slots from ID3D11DeviceChild before its own methods begin, so Map is slot
//   14, not slot 7. Getting that wrong compiles cleanly and then calls a
//   different function with misinterpreted arguments. Spelling the layouts out
//   is what makes the offsets checkable against the SDK headers by eye.

import (
	"fmt"
	"syscall"
	"unsafe"
)

// --- constants -------------------------------------------------------------

const (
	d3d11SDKVersion       = 7
	driverTypeHardware    = 1
	driverTypeWARP        = 5
	usageStaging          = 3
	cpuAccessRead         = 0x20000
	mapRead               = 1
	formatB8G8R8A8Unorm   = 87

	// BGRA support is required for Direct2D/WGC interop and costs nothing here.
	createDeviceBGRASupport = 0x20

	hrWaitTimeout           = 0x887A0027
	hrAccessLost            = 0x887A0026
	hrNotCurrentlyAvailable = 0x887A0022
	hrUnsupported           = 0x887A0004
	hrAccessDenied          = 0x80070005
	hrNotFound              = 0x887A0002
)

var (
	iidIDXGIDevice     = GUID{0x54ec77fa, 0x1377, 0x44e6, [8]byte{0x8c, 0x32, 0x88, 0xfd, 0x5f, 0x44, 0xc8, 0x4c}}
	iidIDXGIAdapter    = GUID{0x2411e7e1, 0x12ac, 0x4ccf, [8]byte{0xbd, 0x14, 0x97, 0x98, 0xe8, 0x53, 0x4d, 0xc0}}
	iidIDXGIOutput1    = GUID{0x00cddea8, 0x939b, 0x4b83, [8]byte{0xa3, 0x40, 0xa6, 0x85, 0x22, 0x66, 0x66, 0xcc}}
	iidID3D11Texture2D = GUID{0x6f15aaf2, 0xd208, 0x4e89, [8]byte{0x9a, 0xb4, 0x48, 0x95, 0x35, 0xd3, 0x4f, 0x9c}}
)

// --- structs ---------------------------------------------------------------

type d3d11Texture2DDesc struct {
	Width          uint32
	Height         uint32
	MipLevels      uint32
	ArraySize      uint32
	Format         uint32
	SampleCount    uint32
	SampleQuality  uint32
	Usage          uint32
	BindFlags      uint32
	CPUAccessFlags uint32
	MiscFlags      uint32
}

// PData is typed as unsafe.Pointer rather than uintptr on purpose. D3D declares
// it void*, and holding it as a uintptr means every read has to convert
// uintptr->unsafe.Pointer, which `go vet` correctly flags as unsafe: the
// address would be untracked across any statement boundary. Declaring it as a
// pointer to begin with removes the conversion entirely. The memory it refers
// to is GPU-mapped, not Go heap, and is only valid between Map and Unmap.
type d3d11MappedSubresource struct {
	PData      unsafe.Pointer
	RowPitch   uint32
	DepthPitch uint32
}

type dxgiOutduplPointerPosition struct {
	Position POINT
	Visible  int32
}

type dxgiOutduplFrameInfo struct {
	LastPresentTime           int64
	LastMouseUpdateTime       int64
	AccumulatedFrames         uint32
	RectsCoalesced            int32
	ProtectedContentMaskedOut int32
	PointerPosition           dxgiOutduplPointerPosition
	TotalMetadataBufferSize   uint32
	PointerShapeBufferSize    uint32
}

type dxgiOutputDesc struct {
	DeviceName         [32]uint16
	DesktopCoordinates RECT
	AttachedToDesktop  int32
	Rotation           uint32
	Monitor            uintptr
}

// --- vtables ---------------------------------------------------------------

type id3d11DeviceVtbl struct {
	IUnknownVtbl
	CreateBuffer                    uintptr
	CreateTexture1D                 uintptr
	CreateTexture2D                 uintptr
	CreateTexture3D                 uintptr
	CreateShaderResourceView        uintptr
	CreateUnorderedAccessView       uintptr
	CreateRenderTargetView          uintptr
	CreateDepthStencilView          uintptr
	CreateInputLayout               uintptr
	CreateVertexShader              uintptr
	CreateGeometryShader            uintptr
	CreateGeometryShaderWithSO      uintptr
	CreatePixelShader               uintptr
	CreateHullShader                uintptr
	CreateDomainShader              uintptr
	CreateComputeShader             uintptr
	CreateClassLinkage              uintptr
	CreateBlendState                uintptr
	CreateDepthStencilState         uintptr
	CreateRasterizerState           uintptr
	CreateSamplerState              uintptr
	CreateQuery                     uintptr
	CreatePredicate                 uintptr
	CreateCounter                   uintptr
	CreateDeferredContext           uintptr
	OpenSharedResource              uintptr
	CheckFormatSupport              uintptr
	CheckMultisampleQualityLevels   uintptr
	CheckCounterInfo                uintptr
	CheckCounter                    uintptr
	GetPrivateData                  uintptr
	SetPrivateData                  uintptr
	SetPrivateDataInterface         uintptr
	GetFeatureLevel                 uintptr
	GetCreationFlags                uintptr
	GetDeviceRemovedReason          uintptr
	GetImmediateContext             uintptr
	SetExceptionMode                uintptr
	GetExceptionMode                uintptr
}

type id3d11Device struct{ Vtbl *id3d11DeviceVtbl }

// ID3D11DeviceChild contributes 4 slots (GetDevice + 3 private-data methods)
// before ID3D11DeviceContext's own methods start. This is the offset that makes
// Map land on slot 14.
type id3d11DeviceContextVtbl struct {
	IUnknownVtbl
	GetDevice               uintptr
	GetPrivateData          uintptr
	SetPrivateData          uintptr
	SetPrivateDataInterface uintptr

	VSSetConstantBuffers uintptr
	PSSetShaderResources uintptr
	PSSetShader          uintptr
	PSSetSamplers        uintptr
	VSSetShader          uintptr
	DrawIndexed          uintptr
	Draw                 uintptr
	Map                  uintptr // slot 14
	Unmap                uintptr // slot 15
	PSSetConstantBuffers uintptr
	IASetInputLayout     uintptr
	IASetVertexBuffers   uintptr
	IASetIndexBuffer     uintptr
	DrawIndexedInstanced uintptr
	DrawInstanced        uintptr
	GSSetConstantBuffers uintptr
	GSSetShader          uintptr
	IASetPrimitiveTopology uintptr
	VSSetShaderResources uintptr
	VSSetSamplers        uintptr
	Begin                uintptr
	End                  uintptr
	GetData              uintptr
	SetPredication       uintptr
	GSSetShaderResources uintptr
	GSSetSamplers        uintptr
	OMSetRenderTargets   uintptr
	OMSetRenderTargetsAndUAV uintptr
	OMSetBlendState      uintptr
	OMSetDepthStencilState uintptr
	SOSetTargets         uintptr
	DrawAuto             uintptr
	DrawIndexedInstancedIndirect uintptr
	DrawInstancedIndirect uintptr
	Dispatch             uintptr
	DispatchIndirect     uintptr
	RSSetState           uintptr
	RSSetViewports       uintptr
	RSSetScissorRects    uintptr
	CopySubresourceRegion uintptr
	CopyResource         uintptr // slot 47
	UpdateSubresource    uintptr
}

type id3d11DeviceContext struct{ Vtbl *id3d11DeviceContextVtbl }

type idxgiObjectVtbl struct {
	IUnknownVtbl
	SetPrivateData          uintptr
	SetPrivateDataInterface uintptr
	GetPrivateData          uintptr
	GetParent               uintptr
}

type idxgiDeviceVtbl struct {
	idxgiObjectVtbl
	GetAdapter             uintptr
	CreateSurface          uintptr
	QueryResourceResidency uintptr
	SetGPUThreadPriority   uintptr
	GetGPUThreadPriority   uintptr
}

type idxgiDevice struct{ Vtbl *idxgiDeviceVtbl }

type idxgiAdapterVtbl struct {
	idxgiObjectVtbl
	EnumOutputs           uintptr
	GetDesc               uintptr
	CheckInterfaceSupport uintptr
}

type idxgiAdapter struct{ Vtbl *idxgiAdapterVtbl }

type idxgiOutput1Vtbl struct {
	idxgiObjectVtbl
	// IDXGIOutput
	GetDesc                     uintptr
	GetDisplayModeList          uintptr
	FindClosestMatchingMode     uintptr
	WaitForVBlank               uintptr
	TakeOwnership               uintptr
	ReleaseOwnership            uintptr
	GetGammaControlCapabilities uintptr
	SetGammaControl             uintptr
	GetGammaControl             uintptr
	SetDisplaySurface           uintptr
	GetDisplaySurfaceData       uintptr
	GetFrameStatistics          uintptr
	// IDXGIOutput1
	GetDisplayModeList1      uintptr
	FindClosestMatchingMode1 uintptr
	GetDisplaySurfaceData1   uintptr
	DuplicateOutput          uintptr
}

type idxgiOutput1 struct{ Vtbl *idxgiOutput1Vtbl }

type idxgiOutputDuplicationVtbl struct {
	idxgiObjectVtbl
	GetDesc               uintptr
	AcquireNextFrame      uintptr
	GetFrameDirtyRects    uintptr
	GetFrameMoveRects     uintptr
	GetFramePointerShape  uintptr
	MapDesktopSurface     uintptr
	UnMapDesktopSurface   uintptr
	ReleaseFrame          uintptr
}

type idxgiOutputDuplication struct{ Vtbl *idxgiOutputDuplicationVtbl }

// --- device creation -------------------------------------------------------

// createD3D11Device builds a device, preferring the hardware driver and falling
// back to WARP. WARP is a software rasteriser: it still lets Desktop
// Duplication run when the hardware path is refused, which is the difference
// between a capture and no capture on a locked-down GPU driver.
func createD3D11Device() (*id3d11Device, *id3d11DeviceContext, string, error) {
	for _, dt := range []struct {
		kind uintptr
		name string
	}{{driverTypeHardware, "hardware"}, {driverTypeWARP, "warp"}} {
		var dev *id3d11Device
		var ctx *id3d11DeviceContext
		var featureLevel uint32

		hr, _, _ := syscall.SyscallN(procD3D11CreateDevice.Addr(),
			0,                        // pAdapter (NULL = default for driver type)
			dt.kind,                  // DriverType
			0,                        // Software
			uintptr(createDeviceBGRASupport),
			0,                        // pFeatureLevels (NULL = default chain)
			0,                        // FeatureLevels
			uintptr(d3d11SDKVersion),
			uintptr(unsafe.Pointer(&dev)),
			uintptr(unsafe.Pointer(&featureLevel)),
			uintptr(unsafe.Pointer(&ctx)))

		if succeeded(hr) && dev != nil && ctx != nil {
			return dev, ctx, dt.name, nil
		}
	}
	return nil, nil, "", fmt.Errorf("D3D11CreateDevice failed for both hardware and warp driver types")
}

// --- capture ---------------------------------------------------------------

func captureDXGI(h HWND) (*Frame, error) {
	if h == 0 {
		return nil, fmt.Errorf("no window handle")
	}
	winRect, err := GetWindowRectOf(h)
	if err != nil {
		return nil, err
	}

	dev, ctx, driver, err := createD3D11Device()
	if err != nil {
		return nil, err
	}
	defer dev.Release2()
	defer ctx.Release2()

	// device -> IDXGIDevice -> adapter
	dxgiDevP, err := (*IUnknown)(unsafe.Pointer(dev)).QueryInterface(&iidIDXGIDevice)
	if err != nil {
		return nil, fmt.Errorf("device is not an IDXGIDevice: %w", err)
	}
	defer releaseAny(dxgiDevP)
	dxgiDev := (*idxgiDevice)(dxgiDevP)

	var adapterP unsafe.Pointer
	hr, _, _ := syscall.SyscallN(dxgiDev.Vtbl.GetAdapter,
		uintptr(dxgiDevP), uintptr(unsafe.Pointer(&adapterP)))
	if !succeeded(hr) {
		return nil, hrErr("IDXGIDevice::GetAdapter", hr)
	}
	defer releaseAny(adapterP)
	adapter := (*idxgiAdapter)(adapterP)

	// Pick the output the window's centre sits on, so a multi-monitor setup
	// duplicates the screen the game is actually on rather than always output 0.
	cx := winRect.Left + winRect.Width()/2
	cy := winRect.Top + winRect.Height()/2

	var chosen *idxgiOutput1
	var chosenP unsafe.Pointer
	var chosenDesc dxgiOutputDesc
	var outputsSeen int

	for i := uint32(0); ; i++ {
		var outP unsafe.Pointer
		hr, _, _ := syscall.SyscallN(adapter.Vtbl.EnumOutputs,
			uintptr(adapterP), uintptr(i), uintptr(unsafe.Pointer(&outP)))
		if !succeeded(hr) || outP == nil {
			break
		}
		outputsSeen++

		o1P, qerr := (*IUnknown)(outP).QueryInterface(&iidIDXGIOutput1)
		releaseAny(outP)
		if qerr != nil {
			continue
		}
		o1 := (*idxgiOutput1)(o1P)

		var desc dxgiOutputDesc
		syscall.SyscallN(o1.Vtbl.GetDesc, uintptr(o1P), uintptr(unsafe.Pointer(&desc)))

		inside := cx >= desc.DesktopCoordinates.Left && cx < desc.DesktopCoordinates.Right &&
			cy >= desc.DesktopCoordinates.Top && cy < desc.DesktopCoordinates.Bottom

		if inside || chosen == nil {
			if chosen != nil {
				releaseAny(chosenP)
			}
			chosen, chosenP, chosenDesc = o1, o1P, desc
			if inside {
				break
			}
		} else {
			releaseAny(o1P)
		}
	}

	if chosen == nil {
		return nil, fmt.Errorf("no DXGI output found (%d enumerated)", outputsSeen)
	}
	defer releaseAny(chosenP)

	// duplicate
	var dupP unsafe.Pointer
	hr, _, _ = syscall.SyscallN(chosen.Vtbl.DuplicateOutput,
		uintptr(chosenP), uintptr(unsafe.Pointer(dev)), uintptr(unsafe.Pointer(&dupP)))
	if !succeeded(hr) {
		return nil, fmt.Errorf("IDXGIOutput1::DuplicateOutput failed: %s",
			explainDXGI(uint32(hr)))
	}
	defer releaseAny(dupP)
	dup := (*idxgiOutputDuplication)(dupP)

	// AcquireNextFrame: the first call after DuplicateOutput routinely returns a
	// frame with AccumulatedFrames == 0, which carries no new desktop image.
	// Accepting it yields a black capture that "succeeded". Retry until the
	// compositor actually presents something.
	var texP unsafe.Pointer
	var info dxgiOutduplFrameInfo
	got := false

	for attempt := 0; attempt < 30; attempt++ {
		var resP unsafe.Pointer
		hr, _, _ = syscall.SyscallN(dup.Vtbl.AcquireNextFrame,
			uintptr(dupP), 500, // 500ms timeout
			uintptr(unsafe.Pointer(&info)), uintptr(unsafe.Pointer(&resP)))

		if uint32(hr) == hrWaitTimeout {
			continue // nothing presented yet; a static screen does this
		}
		if !succeeded(hr) {
			return nil, fmt.Errorf("AcquireNextFrame failed: %s", explainDXGI(uint32(hr)))
		}

		if info.AccumulatedFrames == 0 && resP != nil {
			// stale frame - release and ask again
			releaseAny(resP)
			syscall.SyscallN(dup.Vtbl.ReleaseFrame, uintptr(dupP))
			continue
		}

		if resP == nil {
			syscall.SyscallN(dup.Vtbl.ReleaseFrame, uintptr(dupP))
			continue
		}

		t, qerr := (*IUnknown)(resP).QueryInterface(&iidID3D11Texture2D)
		releaseAny(resP)
		if qerr != nil {
			syscall.SyscallN(dup.Vtbl.ReleaseFrame, uintptr(dupP))
			return nil, fmt.Errorf("frame is not an ID3D11Texture2D: %w", qerr)
		}
		texP = t
		got = true
		break
	}

	if !got {
		return nil, fmt.Errorf("no desktop frame was presented within 30 attempts " +
			"(a completely static screen can do this; move the mouse and retry)")
	}
	defer releaseAny(texP)
	defer syscall.SyscallN(dup.Vtbl.ReleaseFrame, uintptr(dupP))

	// describe the acquired texture
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

	// staging copy - the acquired texture is not CPU-readable
	staging := desc
	staging.Usage = usageStaging
	staging.BindFlags = 0
	staging.CPUAccessFlags = cpuAccessRead
	staging.MiscFlags = 0

	var stageP unsafe.Pointer
	hr, _, _ = syscall.SyscallN(dev.Vtbl.CreateTexture2D,
		uintptr(unsafe.Pointer(dev)),
		uintptr(unsafe.Pointer(&staging)),
		0,
		uintptr(unsafe.Pointer(&stageP)))
	if !succeeded(hr) {
		return nil, hrErr("CreateTexture2D(staging)", hr)
	}
	defer releaseAny(stageP)

	syscall.SyscallN(ctx.Vtbl.CopyResource,
		uintptr(unsafe.Pointer(ctx)), uintptr(stageP), uintptr(texP))

	var mapped d3d11MappedSubresource
	hr, _, _ = syscall.SyscallN(ctx.Vtbl.Map,
		uintptr(unsafe.Pointer(ctx)), uintptr(stageP), 0,
		uintptr(mapRead), 0, uintptr(unsafe.Pointer(&mapped)))
	if !succeeded(hr) {
		return nil, hrErr("ID3D11DeviceContext::Map", hr)
	}

	fullW, fullH := int(desc.Width), int(desc.Height)
	pitch := int(mapped.RowPitch)

	// Copy out of the mapped GPU memory before unmapping. unsafe.Slice over
	// mapped.PData is only valid between Map and Unmap.
	raw := make([]byte, pitch*fullH)
	copy(raw, unsafe.Slice((*byte)(mapped.PData), pitch*fullH))

	syscall.SyscallN(ctx.Vtbl.Unmap, uintptr(unsafe.Pointer(ctx)), uintptr(stageP), 0)

	full := bgraToRGBA(raw, fullW, fullH, pitch)
	forceOpaque(full)

	// crop to the window, in output-local coordinates
	ox, oy := int(chosenDesc.DesktopCoordinates.Left), int(chosenDesc.DesktopCoordinates.Top)
	cropped, note := cropToWindow(full, winRect, ox, oy)

	return &Frame{
		Img:    cropped,
		Method: "dxgi",
		Note: fmt.Sprintf("desktop duplication on %s (%s driver), output %dx%d; %s",
			syscall.UTF16ToString(chosenDesc.DeviceName[:]), driver, fullW, fullH, note),
		SrcW: fullW,
		SrcH: fullH,
	}, nil
}

func (d *id3d11Device) Release2()        { (*IUnknown)(unsafe.Pointer(d)).Release() }
func (c *id3d11DeviceContext) Release2() { (*IUnknown)(unsafe.Pointer(c)).Release() }

func explainDXGI(hr uint32) string {
	switch hr {
	case hrAccessLost:
		return "DXGI_ERROR_ACCESS_LOST - the desktop switched (UAC prompt, lock screen, or a mode change)"
	case hrNotCurrentlyAvailable:
		return "DXGI_ERROR_NOT_CURRENTLY_AVAILABLE - the maximum number of duplications is already in use by another capture app"
	case hrUnsupported:
		return "DXGI_ERROR_UNSUPPORTED - this output does not support desktop duplication"
	case hrAccessDenied:
		return "E_ACCESSDENIED - blocked, commonly by a protected-content or secure-desktop policy"
	case hrNotFound:
		return "DXGI_ERROR_NOT_FOUND"
	}
	return fmt.Sprintf("hr=0x%08X", hr)
}
