//go:build windows

package main

import (
	"fmt"
	"syscall"
	"unsafe"
)

const (
	foDelete          = 0x0003
	fofAllowUndo      = 0x0040
	fofNoConfirmation = 0x0010
	fofSilent         = 0x0004
)

type shFileOpStruct struct {
	hwnd                  uintptr
	wFunc                 uint32
	pFrom                 *uint16
	pTo                   *uint16
	fFlags                uint16
	fAnyOperationsAborted int32
	hNameMappings         uintptr
	lpszProgressTitle     *uint16
}

// recycleFile moves path to the Windows Recycle Bin via SHFileOperationW --
// never a permanent delete. Used only for confirmed-transcribed screenshot
// images once they've aged past the retention window.
func recycleFile(path string) error {
	utf16Path, err := syscall.UTF16FromString(path)
	if err != nil {
		return err
	}
	// SHFileOperationW requires the pFrom list to be double-null-terminated;
	// UTF16FromString already null-terminates the single path, so append one
	// more null to mark the end of the (one-item) list.
	utf16Path = append(utf16Path, 0)

	op := shFileOpStruct{
		wFunc:  foDelete,
		pFrom:  &utf16Path[0],
		fFlags: fofAllowUndo | fofNoConfirmation | fofSilent,
	}

	shell32 := syscall.NewLazyDLL("shell32.dll")
	proc := shell32.NewProc("SHFileOperationW")
	ret, _, _ := proc.Call(uintptr(unsafe.Pointer(&op)))
	if ret != 0 {
		return fmt.Errorf("SHFileOperationW failed with code %d", ret)
	}
	if op.fAnyOperationsAborted != 0 {
		return fmt.Errorf("recycle operation was aborted")
	}
	return nil
}
