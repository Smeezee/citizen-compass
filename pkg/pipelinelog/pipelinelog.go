// Package pipelinelog is the shared logging convention for every Citizen
// Compass tool: each tool writes to its own logs/<tool-name>.log file
// (created under the given project root), all using the identical
// "[YYYY-MM-DD HH:MM:SS] message" line format. This is the single
// standardized logging mechanism new tools (the Auditor's checkers, the
// dashboard, the Blender launcher, etc.) should use going forward.
package pipelinelog

import (
	"fmt"
	"os"
	"path/filepath"
	"sync"
	"time"
)

type Logger struct {
	mu      sync.Mutex
	logPath string
}

// New creates a logger that writes to <projectRoot>/logs/<toolName>.log,
// creating the logs/ directory if it doesn't exist yet.
func New(projectRoot string, toolName string) *Logger {
	logsDir := filepath.Join(projectRoot, "logs")
	os.MkdirAll(logsDir, 0755)
	return &Logger{logPath: filepath.Join(logsDir, toolName+".log")}
}

// Logf writes one formatted, timestamped line to this tool's log file and
// (best-effort) to stdout. A console-write failure (e.g. no console
// attached, as with a windowsgui-linked binary) never blocks or fails the
// call -- only the file write matters for correctness.
func (l *Logger) Logf(format string, args ...interface{}) {
	msg := fmt.Sprintf(format, args...)
	line := fmt.Sprintf("[%s] %s", time.Now().Format("2006-01-02 15:04:05"), msg)

	l.mu.Lock()
	defer l.mu.Unlock()

	fmt.Fprintln(os.Stdout, line)

	f, err := os.OpenFile(l.logPath, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		return
	}
	defer f.Close()
	f.WriteString(line + "\n")
}

// Path returns the log file path this logger writes to.
func (l *Logger) Path() string {
	return l.logPath
}
