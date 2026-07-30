// Package pgconn is the shared Postgres-connection boilerplate every
// Citizen Compass Go tool that talks to the citizen_compass database needs:
// finding the project root, reading DATABASE_URL out of .env, and opening
// a ready-to-use *sql.DB. Centralized here since Phase 3's Auditor is
// expected to be many small single-purpose checkers, all needing exactly
// this same setup.
package pgconn

import (
	"bufio"
	"database/sql"
	"fmt"
	"os"
	"path/filepath"
	"strings"

	_ "github.com/jackc/pgx/v5/stdlib"
)

// FindProjectRoot walks up from the current working directory looking for
// go.work, which sits at the real project root. Falls back to the cwd if
// no go.work is found (e.g. running outside the workspace).
func FindProjectRoot() string {
	dir, err := os.Getwd()
	if err != nil {
		return "."
	}
	for {
		if _, err := os.Stat(filepath.Join(dir, "go.work")); err == nil {
			return dir
		}
		parent := filepath.Dir(dir)
		if parent == dir {
			break
		}
		dir = parent
	}
	cwd, _ := os.Getwd()
	return cwd
}

// ReadDatabaseURL reads DATABASE_URL (or RAILWAY_DATABASE_URL) out of the
// given .env file and rewrites it from SQLAlchemy's "postgresql+psycopg2://"
// dialect+driver form into the plain "postgres://" scheme pgx expects.
func ReadDatabaseURL(envPath string) (string, error) {
	f, err := os.Open(envPath)
	if err != nil {
		return "", err
	}
	defer f.Close()

	scanner := bufio.NewScanner(f)
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if line == "" || strings.HasPrefix(line, "#") {
			continue
		}
		parts := strings.SplitN(line, "=", 2)
		if len(parts) != 2 {
			continue
		}
		key := strings.TrimSpace(parts[0])
		if key == "DATABASE_URL" || key == "RAILWAY_DATABASE_URL" {
			val := strings.Trim(strings.TrimSpace(parts[1]), `"'`)
			val = strings.Replace(val, "postgresql+psycopg2://", "postgres://", 1)
			val = strings.Replace(val, "postgresql://", "postgres://", 1)
			return val, nil
		}
	}
	return "", fmt.Errorf("no DATABASE_URL or RAILWAY_DATABASE_URL found in %s", envPath)
}

// Connect finds the project root, reads .env, opens a connection to
// citizen_compass, and pings it to confirm it's actually reachable before
// returning. Returns the resolved project root alongside the *sql.DB since
// callers invariably need both.
func Connect() (db *sql.DB, projectRoot string, err error) {
	projectRoot = FindProjectRoot()
	dbURL, err := ReadDatabaseURL(filepath.Join(projectRoot, ".env"))
	if err != nil {
		return nil, projectRoot, err
	}
	db, err = sql.Open("pgx", dbURL)
	if err != nil {
		return nil, projectRoot, err
	}
	if err := db.Ping(); err != nil {
		db.Close()
		return nil, projectRoot, fmt.Errorf("could not reach Postgres: %w", err)
	}
	return db, projectRoot, nil
}
