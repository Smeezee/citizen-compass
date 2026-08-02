// Schema Init — Citizen Compass Phase 1 tool
//
// Ensures the auditor layer's three tables exist in the citizen_compass
// Postgres database. Idempotent -- safe to re-run.
//
//	pipeline_check_results  the OBSERVATION log. Append-only, one row per
//	                        thing-a-run-saw. Never updated in place.
//	pipeline_findings       lifecycle STATE. One row per distinct condition,
//	                        keyed by finding_key, describing what is true now.
//	pipeline_check_runs     one row per run, written even when a run finds
//	                        nothing -- a dead scheduler and a clean bill of
//	                        health must never look the same.
//
// Why findings are a separate table from results, rather than extra columns:
// the observation log is not redundant. Comparing a finding's timestamp
// against commit times is exactly what proved several 2026-07-30 findings
// stale. Collapsing the two would destroy that history to gain a status
// column. One row per thing-a-run-saw and one row per condition are
// different things, so they are different tables.
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

	// ------------------------------------------------------------------
	// pipeline_findings -- lifecycle state, one row per distinct condition.
	//
	// status is OPEN / CLOSED / UNKNOWN / ACKNOWLEDGED, constrained here so
	// a typo in any writer fails loudly at the database rather than
	// silently creating a fifth status nothing knows how to read.
	//
	// closed_by_run records WHICH run closed a finding, because "a run
	// looked and did not find it" is the only way anything closes, and that
	// claim has to be auditable after the fact.
	// ------------------------------------------------------------------
	_, err = db.Exec(`
		CREATE TABLE IF NOT EXISTS pipeline_findings (
			finding_key         VARCHAR(32) PRIMARY KEY,
			check_name          VARCHAR(150) NOT NULL,
			subject             VARCHAR(255),
			result              VARCHAR(20) NOT NULL,
			details             TEXT,
			status              VARCHAR(20) NOT NULL
			                    CHECK (status IN ('OPEN','CLOSED','UNKNOWN','ACKNOWLEDGED')),
			first_seen          TIMESTAMP NOT NULL,
			last_seen           TIMESTAMP NOT NULL,
			status_changed_at   TIMESTAMP NOT NULL DEFAULT NOW(),
			closed_at           TIMESTAMP,
			closed_by_run       VARCHAR(64),
			run_id              VARCHAR(64),
			occurrences         INTEGER NOT NULL DEFAULT 1,
			acknowledged        BOOLEAN NOT NULL DEFAULT FALSE,
			acknowledged_by     VARCHAR(100),
			acknowledged_reason TEXT,
			acknowledged_at     TIMESTAMP
		)
	`)
	if err != nil {
		logger.Logf("FATAL: could not create pipeline_findings: %v", err)
		os.Exit(1)
	}
	logger.Logf("pipeline_findings table ready")

	for _, idx := range []string{
		`CREATE INDEX IF NOT EXISTS ix_pipeline_findings_status ON pipeline_findings (status)`,
		`CREATE INDEX IF NOT EXISTS ix_pipeline_findings_check_name ON pipeline_findings (check_name)`,
		`CREATE INDEX IF NOT EXISTS ix_pipeline_findings_last_seen ON pipeline_findings (last_seen)`,
	} {
		if _, err = db.Exec(idx); err != nil {
			logger.Logf("FATAL: could not create pipeline_findings index: %v", err)
			os.Exit(1)
		}
	}
	logger.Logf("pipeline_findings indexes ready (status, check_name, last_seen)")

	// ------------------------------------------------------------------
	// pipeline_check_runs -- one row per run, ALWAYS written.
	//
	// checkers_errored and errored_names are what let a later run decide
	// UNKNOWN instead of CLOSED. Without a durable record of which checkers
	// actually completed, a finding's absence is ambiguous, and the
	// ambiguity always resolves the dangerous way.
	// ------------------------------------------------------------------
	_, err = db.Exec(`
		CREATE TABLE IF NOT EXISTS pipeline_check_runs (
			run_id             VARCHAR(64) PRIMARY KEY,
			started_at         TIMESTAMP NOT NULL,
			ended_at           TIMESTAMP,
			groups             VARCHAR(100),
			source_process     VARCHAR(100),
			checkers_attempted INTEGER NOT NULL DEFAULT 0,
			checkers_ok        INTEGER NOT NULL DEFAULT 0,
			checkers_errored   INTEGER NOT NULL DEFAULT 0,
			errored_names      TEXT,
			findings_opened    INTEGER NOT NULL DEFAULT 0,
			findings_closed    INTEGER NOT NULL DEFAULT 0,
			findings_unknown   INTEGER NOT NULL DEFAULT 0,
			findings_unchanged INTEGER NOT NULL DEFAULT 0,
			notes              TEXT
		)
	`)
	if err != nil {
		logger.Logf("FATAL: could not create pipeline_check_runs: %v", err)
		os.Exit(1)
	}
	_, err = db.Exec(`
		CREATE INDEX IF NOT EXISTS ix_pipeline_check_runs_started_at
		ON pipeline_check_runs (started_at)
	`)
	if err != nil {
		logger.Logf("FATAL: could not create pipeline_check_runs index: %v", err)
		os.Exit(1)
	}
	logger.Logf("pipeline_check_runs table ready")
}
