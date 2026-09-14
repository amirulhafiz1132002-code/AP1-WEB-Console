# AP1-WEB-Console Branch Forensics

**Status:** VERIFIED / READ-ONLY AUDIT RECORD
**Canonical branch:** `Amrhz`
**Canonical HEAD at audit:** `ca5cdb0aa503c4b772f45ee837d7aa07bc26caa6`

## Purpose

This document records the branch-cleanup decision so branch history is not confused with the canonical AP1-WEB-Console source.

## Canonical source

- `Amrhz` — KEEP
- `Amrhz` is the current source of truth for AP1-WEB-Console.

## Preserve temporarily for extraction

### `feat/sofa-integration`

KEEP temporarily while its unique assets are evaluated. Its useful testing assets overlap with the current `tests/` structure, so no duplicate copy is required at this point.

Observed unique assets include:

- `tests/conftest.py`
- `tests/fixtures.py`
- `tests/utils.py`
- `SOFA_CONTRIBUTION_GUIDE.md`
- `PULL_REQUEST_TEMPLATE.md`
- `.github/workflows/sofa-auto-contribute.yml`
- `.github/workflows/sofa-knowledge-check.yml`

The reusable Python testing utilities are already present on `Amrhz`; the mock AI helpers are test fixtures and must not be treated as proof of live AI execution.

### `file-ingest-skeleton`

KEEP temporarily for historical extraction review. The branch diverges from `Amrhz` and contains documentation/configuration artifacts that require separate verification before any migration.

## Cleanup candidates

The following categories are candidates for deletion after final human confirmation:

- obsolete `patch-*` branches
- obsolete `alert-*` branches
- branches already fully merged or superseded by `Amrhz`
- disconnected experiments that are not part of the current AP1-WEB-Console lineage

No branch deletion is recorded as completed by this document.

## Rules

1. Do not treat branch names or README claims as implementation proof.
2. Do not copy mock AI code into runtime paths and call it live AI.
3. Do not delete a branch until unique commits/files have been checked.
4. `Amrhz` remains the canonical source unless a later architecture decision explicitly changes it.
5. REAL STATE > UI SIMULATION.
