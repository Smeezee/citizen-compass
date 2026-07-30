"""Pluggable checker system - see checks/framework.py for the shared
plumbing (Finding, write_findings, summarize) and checks/file_checks.py
for the filesystem/git-only checkers. Each checks/*.py module exports a
CHECKERS list of (name, function) pairs; run_checks.py (repo root) ties
them together.
"""
