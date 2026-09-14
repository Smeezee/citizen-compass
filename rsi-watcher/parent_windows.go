package main

import (
	"path/filepath"
	"strings"
	"unsafe"

	"golang.org/x/sys/windows"
)

func parentProcessName() string {
	self := windows.GetCurrentProcessId()
	snap, err := windows.CreateToolhelp32Snapshot(windows.TH32CS_SNAPPROCESS, 0)
	if err != nil {
		return ""
	}
	defer windows.CloseHandle(snap)
	var pe windows.ProcessEntry32
	pe.Size = uint32(unsafe.Sizeof(pe))
	if err := windows.Process32First(snap, &pe); err != nil {
		return ""
	}
	var parentPID uint32
	for {
		if pe.ProcessID == self {
			parentPID = pe.ParentProcessID
			break
		}
		if err := windows.Process32Next(snap, &pe); err != nil {
			return ""
		}
	}
	if err := windows.Process32First(snap, &pe); err != nil {
		return ""
	}
	for {
		if pe.ProcessID == parentPID {
			return windows.UTF16ToString(pe.ExeFile[:])
		}
		if err := windows.Process32Next(snap, &pe); err != nil {
			return ""
		}
	}
}

func fromTaskScheduler() bool {
	base := strings.ToLower(filepath.Base(parentProcessName()))
	switch base {
	case "taskeng.exe", "svchost.exe", "taskhostw.exe", "taskhost.exe":
		return true
	default:
		return false
	}
}