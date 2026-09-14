# AP1-WEB-Console Branch Forensics

**Status:** VERIFIED / CLEANUP DECISION LOCKED
**Canonical branch:** `Amrhz`

## Purpose

This document records the final branch-cleanup decision so branch history is not confused with the canonical AP1-WEB-Console source.

## Canonical source

- `Amrhz` — **KEEP / CANONICAL**
- `Amrhz` is the current source of truth for AP1-WEB-Console.

## Cleanup decision

The following branches were reviewed through branch comparison and unique-asset extraction. No verified unique runtime component was found that must be migrated into `Amrhz`.

### Cleanup candidates

- `Ap1-projects-Console-workflows`
- `My-crypto`
- `alert-autofix-9`
- `alert-autofix-10`
- `alert-fix-10`
- `amirulhafiz1132002-code-patch-1` through `amirulhafiz1132002-code-patch-19`
- `codespace-orange-engine-r4jx5pj666v9hg7r`
- `feat/sofa-integration`
- `feature/file-management-integration`
- `file-ingest-skeleton`

## Extraction findings

### `feat/sofa-integration`

Its reusable Python testing utilities overlap the canonical `tests/` structure and are already present on `Amrhz`. The remaining SOFA guide/workflow/template material is process or integration-specific and is not required by the current AP1 runtime architecture.

Mock AI helpers remain test fixtures only and are not evidence of live AI execution.

### `file-ingest-skeleton`

Review did not establish a verified file-ingestion runtime implementation that needs migration. Its notable prompt/configuration material is documentation/configuration, not proof of a live AI or ingestion runtime.

### `feature/file-management-integration`

Its work is already represented in the canonical `Amrhz` history through the merge into the current lineage.

### Other cleanup candidates

Old patch, alert, and disconnected experimental branches were classified as obsolete, superseded, or outside the current AP1-WEB-Console lineage during the forensic review.

## Execution boundary

**Verified:** forensic review and cleanup decision are complete.

**Not executed:** remote branch deletion, because the connected GitHub capability available to this workspace does not expose a branch-delete operation.

This is intentional: no ref is moved or force-updated merely to simulate deletion.

## Source-file cleanup

No source file on `Amrhz` was deleted during this cleanup because no individual runtime file was independently proven obsolete by the branch-forensics task. Deleting source files without that evidence would violate the project truth protocol.

## Rules

1. Do not treat branch names or README claims as implementation proof.
2. Do not copy mock AI code into runtime paths and call it live AI.
3. Do not delete source files without evidence that they are obsolete.
4. `Amrhz` remains the canonical source unless a later architecture decision explicitly changes it.
5. REAL STATE > UI SIMULATION.
6. EVIDENCE > CLAIM.
7. HUMAN INTENTION > AI ASSUMPTION.
8. VERIFICATION > BLIND TRUST.
