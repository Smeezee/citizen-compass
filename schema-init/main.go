// Schema Init — Citizen Compass Phase 1 tool
//
// Ensures pipeline_check_results exists in the citizen_compass Postgres
// database: the single shared table any future checker/watcher/auditor
// writes its results to. Idempotent -- safe to re-run.
//
// Usage:
//   schema-init
package main

import (
	"os"

	"citizencompass/pkg/pgconn"
	"citizencompass/pkg/pipelinelog"
)

func main() {
	db, projectRoot, err := pgconn.Connect()
	logger := pipelinelog.New(projectRoot, "schema_init")
	if err != nil {
		logger.Logf("FATAL: could not connect to Postgres: %v", err)
		os.Exit(1)
	}
	defer db.Close()
	logger.Logf("Connected to Postgres")

	_, err = db.Exec(`
		CREATE TABLE IF NOT EXISTS pipeline_check_results (
			id SERIAL PRIMARY KEY,
			check_name VARCHAR(150) NOT NULL,
			subject VARCHAR(255),
			result VARCHAR(20) NOT NULL,
			details TEXT,
			source_process VARCHAR(100) NOT NULL,
			checked_at TIMESTAMP NOT NULL DEFAULT NOW()
		)
	`)
	if err != nil {
		logger.Logf("FATAL: could not create pipeline_check_results: %v", err)
		os.Exit(1)
	}
	logger.Logf("pipeline_check_results table ready")

	_, err = db.Exec(`
		CREATE INDEX IF NOT EXISTS ix_pipeline_check_results_check_name
		ON pipeline_check_results (check_name)
	`)
	if err != nil {
		logger.Logf("FATAL: could not create index: %v", err)
		os.Exit(1)
	}
	_, err = db.Exec(`
		CREATE INDEX IF NOT EXISTS ix_pipeline_check_results_checked_at
		ON pipeline_check_results (checked_at)
	`)
	if err != nil {
		logger.Logf("FATAL: could not create index: %v", err)
		os.Exit(1)
	}
	logger.Logf("Indexes ready (check_name, checked_at)")
}
